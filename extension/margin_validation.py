"""Step 3 restoration and manual-margin validation for B-Dental."""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import margin_geometry, restoration_utils, scene_utils


@dataclass(frozen=True)
class MarginValidationResult:
    ok: bool
    status: str
    summary: str
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    point_count: int = 0
    path_length: float = 0.0
    mean_surface_distance: float = 0.0
    max_surface_distance: float = 0.0


def validate_step_three_preconditions(state) -> MarginValidationResult:
    errors = []
    if not state.case_initialized:
        errors.append("Initialize a B-Dental case before starting Step 3.")
    if not state.step_1_valid:
        errors.append("Step 1 must be valid before Step 3.")
    if not state.step_2_valid:
        errors.append("Step 2 must be completed before Step 3.")
    if state.scan_configuration == "SINGLE_ARCH" and state.step_2_status != "NOT_APPLICABLE":
        errors.append("Complete Single Arch Step 2 as not applicable before Step 3.")
    if state.scan_configuration != "SINGLE_ARCH" and state.step_2_status != "VERIFIED":
        errors.append("Approve the occlusal relationship before Step 3.")
    return MarginValidationResult(
        ok=not errors,
        status="UPSTREAM_INVALID" if errors else "SETUP_REQUIRED",
        summary=(
            f"Step 3 has {len(errors)} blocking precondition error(s)."
            if errors
            else "Step 3 preconditions are valid."
        ),
        errors=tuple(errors),
    )


def validate_restoration_setup(state, restoration) -> MarginValidationResult:
    preconditions = validate_step_three_preconditions(state)
    if not preconditions.ok:
        return preconditions

    errors = []
    if restoration is None:
        errors.append("Select or add a restoration before drawing a margin.")
    else:
        if restoration.restoration_type != restoration_utils.RESTORATION_TYPE:
            errors.append("v0.0.4 supports anatomical crown restorations only.")
        if restoration.target_arch not in restoration_utils.available_target_arches(state):
            errors.append("The restoration preparation arch is unavailable.")
        if not restoration_utils.tooth_belongs_to_arch(
            restoration.target_tooth_fdi, restoration.target_arch
        ):
            errors.append("The selected FDI tooth does not belong to the preparation arch.")
        if restoration_utils.duplicate_tooth_exists(
            state,
            restoration.target_arch,
            restoration.target_tooth_fdi,
            exclude_id=restoration.restoration_id,
        ):
            errors.append("Another restoration already uses this target tooth.")
        if not restoration.restoration_id:
            errors.append("The restoration has no stable identifier.")

        target = restoration_utils.target_scan(state, restoration)
        if target is None:
            errors.append("The restoration preparation scan is unavailable.")
        elif not scene_utils.is_managed_for_role(target, restoration.target_arch):
            errors.append("The preparation scan has invalid B-Dental role metadata.")
        else:
            current_signature = restoration_utils.target_scan_signature(target)
            if restoration.target_scan_signature and current_signature != restoration.target_scan_signature:
                errors.append("The target preparation scan changed after restoration creation.")

    return MarginValidationResult(
        ok=not errors,
        status="READY_FOR_MARGIN" if not errors else "ERROR",
        summary=(
            "Restoration setup is valid."
            if not errors
            else f"Restoration setup has {len(errors)} blocking error(s)."
        ),
        errors=tuple(errors),
    )


def validate_margin(state, restoration, depsgraph) -> MarginValidationResult:
    setup = validate_restoration_setup(state, restoration)
    if not setup.ok:
        return setup

    errors = []
    warnings = []
    margin = restoration_utils.resolve_margin(restoration)
    target = restoration_utils.target_scan(state, restoration)

    if restoration.margin_session_active:
        errors.append("Apply or cancel the active margin session before validation.")
    if margin is None:
        errors.append("This restoration does not have a managed margin curve.")
        return MarginValidationResult(
            ok=False,
            status="ERROR",
            summary="Margin validation failed.",
            errors=tuple(errors),
        )

    if margin.type != "CURVE" or margin.data is None:
        errors.append("The managed margin must remain a Curve object.")
    else:
        if margin.data.dimensions != "3D":
            errors.append("The managed margin must remain a 3D curve.")
        if len(margin.data.splines) != 1:
            errors.append("The managed margin must contain exactly one spline.")
        elif margin.data.splines[0].type != "POLY":
            errors.append("The managed margin spline must remain a POLY spline.")
        elif not margin.data.splines[0].use_cyclic_u:
            errors.append("The managed margin must be closed before validation.")

    points = margin_geometry.curve_points(margin)
    point_count = len(points)
    if point_count < margin_geometry.MIN_MARGIN_POINTS:
        errors.append("The margin requires at least six points.")
    if margin_geometry.unique_point_count(points) < margin_geometry.MIN_MARGIN_POINTS:
        errors.append("The margin requires at least six unique points.")
    if any(not margin_geometry.finite_point(point) for point in points):
        errors.append("The margin contains non-finite coordinates.")

    world_points = tuple(target.matrix_world @ point for point in points) if target else ()
    lengths = margin_geometry.segment_lengths(world_points)
    if any(value <= margin_geometry.POINT_EPSILON for value in lengths):
        errors.append("Consecutive margin points collapse within the engineering tolerance.")

    length = margin_geometry.path_length(world_points)
    if length < margin_geometry.MIN_PATH_LENGTH:
        errors.append("The margin path is too short for a usable closed candidate.")

    distances: tuple[float, ...] = ()
    if not errors and target is not None:
        distances = margin_geometry.point_surface_distances(target, points, depsgraph)
        if any(not math.isfinite(value) for value in distances):
            errors.append("At least one margin point could not be resolved against the target surface.")
        elif distances and max(distances) > margin_geometry.SURFACE_BLOCKING_DISTANCE:
            errors.append("At least one margin point is more than 1.0 mm from the target surface.")

    if point_count and point_count < margin_geometry.RECOMMENDED_MARGIN_POINTS:
        warnings.append("The margin contains fewer than twelve points; inspect curve detail carefully.")
    if distances and max(distances) > margin_geometry.SURFACE_WARNING_DISTANCE:
        warnings.append("At least one margin point is more than 0.25 mm from the target surface.")
    if world_points and margin_geometry.spacing_ratio(world_points) > 10.0:
        warnings.append("Margin point spacing varies substantially; inspect sparse regions.")

    proximity = margin_geometry.approximate_non_adjacent_proximity(world_points)
    if proximity is not None and proximity < margin_geometry.SELF_PROXIMITY_DISTANCE:
        warnings.append("Non-adjacent margin segments are very close and may cross or fold.")

    if target is not None and length > 0.0:
        target_diagonal = float(target.dimensions.length)
        if target_diagonal > 0.0 and (
            length < target_diagonal * 0.02 or length > target_diagonal * 1.5
        ):
            warnings.append("Margin path length is unusual relative to the preparation scan dimensions.")

    mean_distance = sum(distances) / len(distances) if distances else 0.0
    max_distance = max(distances) if distances else 0.0
    ok = not errors
    return MarginValidationResult(
        ok=ok,
        status="CANDIDATE" if ok else "ERROR",
        summary=(
            "Margin candidate passed engineering validation."
            if ok
            else f"Margin validation found {len(errors)} blocking error(s)."
        ),
        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
        point_count=point_count,
        path_length=length,
        mean_surface_distance=mean_distance,
        max_surface_distance=max_distance,
    )
