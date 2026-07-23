"""Engineering checks for B-Dental occlusion candidates."""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, isfinite

import bpy
from mathutils import Matrix, Vector

from . import alignment, properties, scene_utils, validation


@dataclass(frozen=True)
class OcclusionResult:
    """Structured Step 2 analysis or approval result."""

    ok: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    summary: str = ""
    status: str = "ERROR"
    separation: float = 0.0
    overlap_ratio: float = 0.0


def matrix_uniform_scale(matrix: Matrix, tolerance: float = 1.0e-4) -> float | None:
    """Return a positive uniform scale when the matrix is finite and shear-free.

    STL import may preserve a legitimate unit-conversion scale such as 0.001.
    Step 2 accepts that uniform scale while rejecting non-uniform scale, shear,
    degenerate bases, and reflected transforms.
    """

    if not alignment.matrix_is_finite(matrix):
        return None

    basis = [Vector(matrix.col[index][:3]) for index in range(3)]
    if any(not all(isfinite(float(value)) for value in vector) for vector in basis):
        return None

    lengths = [float(vector.length) for vector in basis]
    if any(length <= 1.0e-12 for length in lengths):
        return None

    uniform_scale = sum(lengths) / 3.0
    relative_spread = max(abs(length - uniform_scale) for length in lengths) / uniform_scale
    if relative_spread > tolerance:
        return None

    normalized = [vector / length for vector, length in zip(basis, lengths)]
    if abs(normalized[0].dot(normalized[1])) > tolerance:
        return None
    if abs(normalized[0].dot(normalized[2])) > tolerance:
        return None
    if abs(normalized[1].dot(normalized[2])) > tolerance:
        return None

    handedness = normalized[0].cross(normalized[1]).dot(normalized[2])
    if abs(handedness - 1.0) > tolerance * 10.0:
        return None

    return uniform_scale


def matrix_is_rigid(matrix: Matrix, tolerance: float = 1.0e-4) -> bool:
    """Return whether a matrix is finite, shear-free, and uniformly scaled."""

    return matrix_uniform_scale(matrix, tolerance) is not None


def matrix_distance(first: Matrix, second: Matrix) -> tuple[float, float]:
    """Return translation and rotation difference between matrices."""

    translation = float((first.translation - second.translation).length)
    first_q = first.to_quaternion().normalized()
    second_q = second.to_quaternion().normalized()
    dot = max(-1.0, min(1.0, abs(first_q.dot(second_q))))
    rotation = float(2.0 * acos(dot))
    return translation, rotation


def _append_scale_diagnostics(
    upper: bpy.types.Object,
    lower: bpy.types.Object,
    errors: list[str],
    warnings: list[str],
) -> None:
    """Report incompatible jaw scales without rejecting valid unit conversion."""

    upper_scale = matrix_uniform_scale(upper.matrix_world)
    lower_scale = matrix_uniform_scale(lower.matrix_world)
    if upper_scale is None or lower_scale is None:
        return

    scale_ratio = max(upper_scale, lower_scale) / min(upper_scale, lower_scale)
    if scale_ratio > 1.05:
        errors.append(
            "Upper and Lower Jaw use incompatible uniform scales. Re-import both scans with the same source units."
        )
    elif scale_ratio > 1.01:
        warnings.append(
            "Upper and Lower Jaw uniform scales differ slightly; confirm both scans used the same source units."
        )


def _world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    matrix = obj.matrix_world
    points = tuple(matrix @ Vector(corner) for corner in obj.bound_box)
    minimum = Vector(tuple(min(point[index] for point in points) for index in range(3)))
    maximum = Vector(tuple(max(point[index] for point in points) for index in range(3)))
    return minimum, maximum


def _axis_gap(first_min: float, first_max: float, second_min: float, second_max: float) -> float:
    if first_max < second_min:
        return second_min - first_max
    if second_max < first_min:
        return first_min - second_max
    return 0.0


def bounding_box_separation(first: bpy.types.Object, second: bpy.types.Object) -> float:
    """Return Euclidean separation between world-space bounding boxes."""

    first_min, first_max = _world_bounds(first)
    second_min, second_max = _world_bounds(second)
    gaps = Vector(
        tuple(
            _axis_gap(first_min[index], first_max[index], second_min[index], second_max[index])
            for index in range(3)
        )
    )
    return float(gaps.length)


def bounding_box_overlap_ratio(first: bpy.types.Object, second: bpy.types.Object) -> float:
    """Return overlap volume divided by the smaller bounding-box volume."""

    first_min, first_max = _world_bounds(first)
    second_min, second_max = _world_bounds(second)
    overlap = Vector(
        tuple(
            max(
                0.0,
                min(first_max[index], second_max[index])
                - max(first_min[index], second_min[index]),
            )
            for index in range(3)
        )
    )
    overlap_volume = float(overlap.x * overlap.y * overlap.z)
    first_size = first_max - first_min
    second_size = second_max - second_min
    first_volume = max(0.0, float(first_size.x * first_size.y * first_size.z))
    second_volume = max(0.0, float(second_size.x * second_size.y * second_size.z))
    denominator = min(first_volume, second_volume)
    return overlap_volume / denominator if denominator > 0.0 else 0.0


def validate_step_two_preconditions(state: bpy.types.PropertyGroup) -> OcclusionResult:
    """Validate Step 2 input pointers and Step 1 state."""

    errors: list[str] = []
    if not state.step_1_valid or state.step_1_status != "VALID":
        errors.append("Step 1 must be valid before occlusion registration can continue.")

    if state.scan_configuration == "SINGLE_ARCH":
        return OcclusionResult(
            ok=not errors,
            errors=tuple(errors),
            summary="Occlusion registration is not applicable to a single-arch case.",
            status="NOT_APPLICABLE" if not errors else "ERROR",
        )

    for role in ("UPPER_JAW", "LOWER_JAW"):
        obj = scene_utils.get_role_object(state, role)
        if obj is None:
            errors.append(f"{properties.role_label(role)} scan is missing.")
            continue
        scan_result = validation.validate_scan_object(
            obj,
            role,
            require_metadata=True,
            include_warnings=False,
        )
        errors.extend(scan_result.errors)

    if state.scan_configuration == "FULL_SCAN_SET":
        for role in ("RIGHT_BITE", "LEFT_BITE"):
            obj = scene_utils.get_role_object(state, role)
            if obj is None:
                errors.append(f"{properties.role_label(role)} scan is missing.")
            elif not scene_utils.is_managed_for_role(obj, role):
                errors.append(f"{properties.role_label(role)} metadata is invalid.")

    return OcclusionResult(
        ok=not errors,
        errors=tuple(errors),
        summary="Step 2 inputs are ready." if not errors else "Step 2 input validation failed.",
        status="NOT_STARTED" if not errors else "ERROR",
    )


def analyze_imported_relationship(state: bpy.types.PropertyGroup) -> OcclusionResult:
    """Analyze the current imported upper/lower relationship without moving objects."""

    preconditions = validate_step_two_preconditions(state)
    if not preconditions.ok or state.scan_configuration == "SINGLE_ARCH":
        return preconditions

    upper = scene_utils.get_role_object(state, "UPPER_JAW")
    lower = scene_utils.get_role_object(state, "LOWER_JAW")
    if upper is None or lower is None:
        return OcclusionResult(ok=False, errors=("Upper and lower scans are required.",))

    errors: list[str] = []
    warnings: list[str] = []
    for obj, label in ((upper, "Upper Jaw"), (lower, "Lower Jaw")):
        if not alignment.matrix_is_finite(obj.matrix_world):
            errors.append(f"{label} has a non-finite world matrix.")
        elif matrix_uniform_scale(obj.matrix_world) is None:
            errors.append(
                f"{label} world transform contains non-uniform scale, shear, a reflection, or a degenerate basis."
            )

    _append_scale_diagnostics(upper, lower, errors, warnings)

    separation = bounding_box_separation(upper, lower)
    overlap_ratio = bounding_box_overlap_ratio(upper, lower)
    combined_extent = max(float(upper.dimensions.length), float(lower.dimensions.length), 1.0e-9)

    if separation > combined_extent * 0.50:
        errors.append("Upper and lower jaws are grossly separated. Use manual coarse positioning.")
    elif separation > combined_extent * 0.10:
        warnings.append("The arches have a visible gap; inspect or align before approval.")

    if overlap_ratio > 0.65:
        warnings.append("The jaw bounding boxes overlap substantially; inspect for interpenetration.")

    if errors:
        return OcclusionResult(
            ok=False,
            errors=tuple(errors),
            warnings=tuple(dict.fromkeys(warnings)),
            summary="Imported relationship requires alignment or corrected scan units.",
            status="NEEDS_ALIGNMENT",
            separation=separation,
            overlap_ratio=overlap_ratio,
        )

    return OcclusionResult(
        ok=True,
        warnings=tuple(dict.fromkeys(warnings)),
        summary="Imported relationship is a candidate and requires user verification.",
        status="IMPORTED_CANDIDATE",
        separation=separation,
        overlap_ratio=overlap_ratio,
    )


def verify_candidate(state: bpy.types.PropertyGroup) -> OcclusionResult:
    """Run engineering checks before explicit user approval."""

    preconditions = validate_step_two_preconditions(state)
    if not preconditions.ok:
        return preconditions
    if state.scan_configuration == "SINGLE_ARCH":
        return OcclusionResult(
            ok=True,
            summary="Single-arch Step 2 may be completed as not applicable.",
            status="NOT_APPLICABLE",
        )

    upper = scene_utils.get_role_object(state, "UPPER_JAW")
    lower = scene_utils.get_role_object(state, "LOWER_JAW")
    if upper is None or lower is None:
        return OcclusionResult(ok=False, errors=("Upper and lower scans are required.",))

    errors: list[str] = []
    warnings: list[str] = []
    if matrix_uniform_scale(upper.matrix_world) is None:
        errors.append(
            "Upper Jaw transform contains non-uniform scale, shear, a reflection, or invalid values."
        )
    if matrix_uniform_scale(lower.matrix_world) is None:
        errors.append(
            "Lower Jaw transform contains non-uniform scale, shear, a reflection, or invalid values."
        )

    _append_scale_diagnostics(upper, lower, errors, warnings)

    stored_upper = scene_utils.matrix_from_string(state.session_upper_matrix)
    if stored_upper is not None:
        translation, rotation = matrix_distance(stored_upper, upper.matrix_world)
        if translation > 1.0e-5 or rotation > 1.0e-3:
            errors.append("Upper Jaw moved during the alignment session; reset or cancel the session.")

    separation = bounding_box_separation(upper, lower)
    overlap_ratio = bounding_box_overlap_ratio(upper, lower)
    combined_extent = max(float(upper.dimensions.length), float(lower.dimensions.length), 1.0e-9)
    if separation > combined_extent * 0.50:
        errors.append("The jaws remain grossly separated.")
    elif separation > combined_extent * 0.10:
        warnings.append("The arches remain separated; confirm this relationship visually.")
    if overlap_ratio > 0.65:
        warnings.append("Substantial bounding-box overlap may indicate interpenetration.")

    if state.registration_inlier_count > 0:
        if state.registration_inlier_ratio < 0.02:
            errors.append("Registration inlier ratio is too low for approval.")
        elif state.registration_inlier_ratio < 0.10:
            warnings.append("Registration used a limited overlap ratio.")

    return OcclusionResult(
        ok=not errors,
        errors=tuple(errors),
        warnings=tuple(dict.fromkeys(warnings)),
        summary="Candidate passed engineering checks." if not errors else "Candidate verification failed.",
        status="CANDIDATE" if not errors else "ERROR",
        separation=separation,
        overlap_ratio=overlap_ratio,
    )
