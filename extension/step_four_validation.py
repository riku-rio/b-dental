"""Structured validation for B-Dental Step 4."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

from mathutils import Vector

from . import axis_geometry, preparation_analysis, restoration_utils

NORMALIZATION_TOLERANCE = 1.0e-5
LOW_SAMPLE_WARNING = 40
HIGH_UNDERCUT_RATIO_WARNING = 0.35
LARGE_BLOCKING_DEPTH_WARNING = 0.0015
AXIS_TILT_WARNING_DEGREES = 35.0


@dataclass(frozen=True)
class StepFourValidationResult:
    ok: bool
    status: str
    summary: str
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def margin_signature(restoration) -> str:
    return restoration.approved_margin_points or ""


def dependency_signature(state, restoration) -> str:
    try:
        from . import antagonist_region

        antagonist = antagonist_region.region_signature(state, restoration)
    except Exception:
        antagonist = ""
    payload = {
        "target": restoration_utils.target_scan_signature(
            restoration_utils.target_scan(state, restoration)
        ),
        "target_matrix": restoration_utils.target_matrix_signature(
            restoration_utils.target_scan(state, restoration)
        ),
        "margin": margin_signature(restoration),
        "axis": axis_geometry.serialize_vector(
            axis_geometry.deserialize_vector(restoration.insertion_axis_local)
        ),
        "radius": round(float(restoration.analysis_radius), 12),
        "sampling": preparation_analysis.SAMPLING_POLICY_VERSION,
        "upstream": restoration_utils.upstream_approval_signature(state),
        "antagonist": antagonist,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def approved_signature(state, restoration) -> str:
    payload = {
        "dependencies": dependency_signature(state, restoration),
        "samples": int(restoration.analysis_sample_count),
        "undercuts": int(restoration.analysis_undercut_count),
        "ratio": round(float(restoration.analysis_undercut_ratio), 12),
        "mean_depth": round(float(restoration.analysis_mean_blocking_depth), 12),
        "max_depth": round(float(restoration.analysis_max_blocking_depth), 12),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def validate_step_four_preconditions(state) -> StepFourValidationResult:
    errors = []
    if not state.case_initialized:
        errors.append("Start a dental case before entering Step 4.")
    if not state.step_1_valid or not state.step_2_valid:
        errors.append("Complete Steps 1 and 2 before entering Step 4.")
    if not state.step_3_valid or state.step_3_status != "VERIFIED":
        errors.append("Approve every Step 3 restoration before entering Step 4.")
    if not state.restorations:
        errors.append("Configure at least one restoration before entering Step 4.")
    for restoration in state.restorations:
        if not restoration.valid or restoration.status != "VERIFIED":
            errors.append(f"FDI {restoration.target_tooth_fdi} is not approved in Step 3.")
        if restoration_utils.resolve_margin(restoration) is None:
            errors.append(f"FDI {restoration.target_tooth_fdi} has no managed approved margin.")
    errors = tuple(dict.fromkeys(errors))
    return StepFourValidationResult(
        ok=not errors,
        status="READY_FOR_AXIS" if not errors else "UPSTREAM_INVALID",
        summary="Step 4 prerequisites are satisfied." if not errors else "Step 4 prerequisites are incomplete.",
        errors=errors,
        warnings=(),
    )


def validate_restoration(state, restoration) -> StepFourValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if restoration is None:
        errors.append("Select a restoration.")
        return StepFourValidationResult(False, "ERROR", "No restoration is active.", tuple(errors), ())
    if not state.step_3_valid or restoration.status != "VERIFIED" or not restoration.valid:
        errors.append("The owning restoration is no longer approved in Step 3.")
    target = restoration_utils.target_scan(state, restoration)
    margin = restoration_utils.resolve_margin(restoration)
    if target is None:
        errors.append("The preparation scan is unavailable.")
    if margin is None or not restoration.approved_margin_points:
        errors.append("The approved margin is missing or stale.")
    if restoration.axis_session_active:
        errors.append("Apply or cancel the active axis session before validation.")

    axis = axis_geometry.deserialize_vector(restoration.insertion_axis_local)
    if axis is None:
        errors.append("Define a finite non-zero insertion axis.")
    elif abs(axis.length - 1.0) > NORMALIZATION_TOLERANCE:
        errors.append("The insertion axis is not normalized.")

    axis_obj = axis_geometry.resolve_axis(restoration)
    if axis_obj is None:
        errors.append("The managed insertion-axis artifact is missing.")
    elif not axis_geometry.is_managed_axis(axis_obj, restoration):
        errors.append("The insertion-axis artifact is owned by another restoration.")
    elif target is not None and axis_obj.parent is not target:
        errors.append("The insertion-axis artifact is not attached to the preparation scan.")
    elif axis is not None and not axis_geometry.axis_object_matches(restoration):
        errors.append("The managed axis orientation does not match the stored candidate.")

    radius = float(restoration.analysis_radius)
    if not math.isfinite(radius) or not preparation_analysis.MIN_ANALYSIS_RADIUS <= radius <= preparation_analysis.MAX_ANALYSIS_RADIUS:
        errors.append("The analysis radius must remain between 2 and 15 mm.")
    elif radius <= preparation_analysis.MIN_ANALYSIS_RADIUS * 1.05 or radius >= preparation_analysis.MAX_ANALYSIS_RADIUS * 0.95:
        warnings.append("The analysis radius is near the supported boundary.")

    if not restoration.analysis_current:
        errors.append("Run undercut analysis for the current axis and settings.")
    elif restoration.analysis_sample_count <= 0:
        errors.append("The current analysis contains no usable samples.")
    elif restoration.analysis_signature != dependency_signature(state, restoration):
        errors.append("The analysis is stale because a material dependency changed.")

    if restoration.analysis_sample_count and restoration.analysis_sample_count < LOW_SAMPLE_WARNING:
        warnings.append("The analysis neighborhood contains a low sample count.")
    if restoration.analysis_undercut_ratio >= HIGH_UNDERCUT_RATIO_WARNING:
        warnings.append("A high proportion of analyzed samples are obstructed.")
    if restoration.analysis_max_blocking_depth >= LARGE_BLOCKING_DEPTH_WARNING:
        warnings.append("The maximum measured blocking depth is large for this engineering check.")

    if axis is not None:
        suggestion = axis_geometry.margin_normal_local(restoration)
        if suggestion is not None:
            dot = max(-1.0, min(1.0, abs(axis.dot(suggestion))))
            angle = math.degrees(math.acos(dot))
            if angle >= AXIS_TILT_WARNING_DEGREES:
                warnings.append("The insertion axis is substantially tilted from the margin-normal suggestion.")

    warnings.append("The neighborhood may include adjacent anatomy because tooth segmentation is outside this release.")
    errors = tuple(dict.fromkeys(errors))
    warnings = tuple(dict.fromkeys(warnings))
    return StepFourValidationResult(
        ok=not errors,
        status="ANALYZED" if not errors else "ERROR",
        summary=(
            "Insertion axis and undercut analysis passed engineering validation."
            if not errors
            else f"Step 4 validation found {len(errors)} blocking error(s)."
        ),
        errors=errors,
        warnings=warnings,
    )
