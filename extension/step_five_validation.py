"""Structured validation for B-Dental Step 5."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

from . import crown_bottom_candidates, restoration_utils
from .crown_bottom_scoring import deserialize_metrics

MIN_MARGINAL_GAP = 0.0
MAX_MARGINAL_GAP = 0.00020
MIN_CEMENT_GAP = 0.0
MAX_CEMENT_GAP = 0.00030
MIN_SPACER_START = 0.00020
MAX_SPACER_START = 0.00300
MIN_RELIEF = 0.0
MAX_AXIAL_RELIEF = 0.00030
MAX_OCCLUSAL_RELIEF = 0.00050
MIN_SEAL_BAND_WIDTH = 0.00015
MAX_SEAL_BAND_WIDTH = 0.00200
MIN_BLOCKOUT_CLEARANCE = 0.0
MAX_BLOCKOUT_CLEARANCE = 0.00030
MIN_SAMPLING_RESOLUTION = 0.00005
MAX_SAMPLING_RESOLUTION = 0.00100
MIN_RUNTIME = 1.0
MAX_RUNTIME = 60.0


@dataclass(frozen=True)
class StepFiveValidationResult:
    ok: bool
    status: str
    summary: str
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def validate_settings(restoration) -> tuple[tuple[str, ...], tuple[str, ...]]:
    errors: list[str] = []
    warnings: list[str] = []
    numeric = {
        "Marginal gap": float(restoration.step_5_marginal_gap),
        "Cement gap": float(restoration.step_5_cement_gap),
        "Spacer start": float(restoration.step_5_spacer_start),
        "Axial relief": float(restoration.step_5_axial_relief),
        "Occlusal relief": float(restoration.step_5_occlusal_relief),
        "Seal-band width": float(restoration.step_5_seal_band_width),
        "Blockout clearance": float(restoration.step_5_blockout_clearance),
        "Sampling resolution": float(restoration.step_5_sampling_resolution),
        "Smoothing strength": float(restoration.step_5_smoothing_strength),
        "Maximum runtime": float(restoration.step_5_maximum_runtime),
        "Correction limit": float(restoration.step_5_correction_limit),
    }
    for label, value in numeric.items():
        if not math.isfinite(value):
            errors.append(f"{label} must be finite.")

    ranges = (
        ("Marginal gap", numeric["Marginal gap"], MIN_MARGINAL_GAP, MAX_MARGINAL_GAP),
        ("Cement gap", numeric["Cement gap"], MIN_CEMENT_GAP, MAX_CEMENT_GAP),
        ("Spacer start", numeric["Spacer start"], MIN_SPACER_START, MAX_SPACER_START),
        ("Axial relief", numeric["Axial relief"], MIN_RELIEF, MAX_AXIAL_RELIEF),
        ("Occlusal relief", numeric["Occlusal relief"], MIN_RELIEF, MAX_OCCLUSAL_RELIEF),
        ("Seal-band width", numeric["Seal-band width"], MIN_SEAL_BAND_WIDTH, MAX_SEAL_BAND_WIDTH),
        ("Blockout clearance", numeric["Blockout clearance"], MIN_BLOCKOUT_CLEARANCE, MAX_BLOCKOUT_CLEARANCE),
        ("Sampling resolution", numeric["Sampling resolution"], MIN_SAMPLING_RESOLUTION, MAX_SAMPLING_RESOLUTION),
        ("Smoothing strength", numeric["Smoothing strength"], 0.0, 1.0),
        ("Maximum runtime", numeric["Maximum runtime"], MIN_RUNTIME, MAX_RUNTIME),
        ("Correction limit", numeric["Correction limit"], 0.00002, 0.00050),
    )
    for label, value, minimum, maximum in ranges:
        if math.isfinite(value) and not minimum <= value <= maximum:
            errors.append(
                f"{label} must remain between {minimum * 1000.0:.3f} and {maximum * 1000.0:.3f} mm."
                if maximum < 1.0
                else f"{label} must remain between {minimum:.1f} and {maximum:.1f}."
            )
        elif math.isfinite(value) and (value <= minimum * 1.05 or value >= maximum * 0.95):
            warnings.append(f"{label} is near the supported engineering boundary.")

    if numeric["Spacer start"] < numeric["Seal-band width"]:
        errors.append("Spacer start must not be smaller than the seal-band width.")
    if int(restoration.step_5_maximum_candidates) not in {1, 2, 3}:
        errors.append("Maximum candidate count must be between 1 and 3.")
    if not 1 <= int(restoration.step_5_maximum_iterations) <= 20:
        errors.append("Maximum iteration count must be between 1 and 20.")
    return tuple(dict.fromkeys(errors)), tuple(dict.fromkeys(warnings))


def validate_preconditions(state) -> StepFiveValidationResult:
    errors: list[str] = []
    if not state.case_initialized:
        errors.append("Start a dental case before entering Step 5.")
    if not state.step_1_valid or not state.step_2_valid:
        errors.append("Complete Steps 1 and 2 before entering Step 5.")
    if not state.step_3_valid or state.step_3_status != "VERIFIED":
        errors.append("Approve every Step 3 restoration before entering Step 5.")
    if not state.step_4_valid or state.step_4_status != "VERIFIED":
        errors.append("Approve every Step 4 preparation analysis before entering Step 5.")
    if not state.restorations:
        errors.append("Configure at least one restoration before entering Step 5.")
    for restoration in state.restorations:
        label = f"FDI {restoration.target_tooth_fdi}"
        if not restoration.valid or restoration.status != "VERIFIED":
            errors.append(f"{label} is not approved in Step 3.")
        if not restoration.step_4_valid or restoration.step_4_status != "VERIFIED":
            errors.append(f"{label} is not approved in Step 4.")
        if restoration.margin_session_active or restoration.axis_session_active:
            errors.append(f"{label} has an active upstream edit session.")
        if restoration_utils.resolve_margin(restoration) is None or not restoration.approved_margin_points:
            errors.append(f"{label} has no current approved margin.")
        if not restoration.approved_axis_local or not restoration.approved_analysis_signature:
            errors.append(f"{label} has no current approved insertion-axis analysis.")
    errors = list(dict.fromkeys(errors))
    return StepFiveValidationResult(
        ok=not errors,
        status="READY_TO_GENERATE" if not errors else "UPSTREAM_INVALID",
        summary="Step 5 prerequisites are satisfied." if not errors else "Step 5 prerequisites are incomplete.",
        errors=tuple(errors),
        warnings=(),
    )


def _record_metrics(restoration):
    record = crown_bottom_candidates.record_for_id(restoration, restoration.selected_candidate_id)
    if record is None:
        return None, None
    obj = crown_bottom_candidates.resolve_selected_candidate(restoration)
    metrics = deserialize_metrics(str(obj.get(crown_bottom_candidates.META_METRICS, ""))) if obj is not None else None
    return record, metrics


def validate_restoration(state, restoration) -> StepFiveValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if restoration is None:
        return StepFiveValidationResult(False, "ERROR", "No restoration is active.", ("Select a restoration.",), ())
    label = f"FDI {restoration.target_tooth_fdi}"
    if not state.step_4_valid or not restoration.step_4_valid or restoration.step_4_status != "VERIFIED":
        errors.append("The owning restoration is no longer approved in Step 4.")
    if restoration.margin_session_active or restoration.axis_session_active:
        errors.append("Apply or cancel the active upstream edit session.")
    if restoration.step_5_correction_active:
        errors.append("Apply or cancel the active Step 5 correction session.")
    setting_errors, setting_warnings = validate_settings(restoration)
    errors.extend(setting_errors)
    warnings.extend(setting_warnings)

    if not restoration.step_5_generation_current:
        errors.append("Generate a current crown-bottom candidate.")
    current_dependency = crown_bottom_candidates.dependency_signature(state, restoration)
    if restoration.step_5_generation_signature != current_dependency:
        errors.append("Step 5 generation is stale because an upstream dependency or setting changed.")

    die = crown_bottom_candidates.resolve_preparation_die(restoration)
    blocked = crown_bottom_candidates.resolve_blocked_die(restoration)
    candidate = crown_bottom_candidates.resolve_selected_candidate(restoration)
    artifacts = (
        (die, crown_bottom_candidates.ARTIFACT_PREPARATION_DIE, "preparation die"),
        (blocked, crown_bottom_candidates.ARTIFACT_BLOCKED_DIE, "blocked die"),
        (candidate, crown_bottom_candidates.ARTIFACT_CROWN_BOTTOM, "selected crown bottom"),
    )
    for obj, artifact_type, label_text in artifacts:
        if obj is None:
            errors.append(f"The managed {label_text} artifact is missing.")
            continue
        if not crown_bottom_candidates.is_managed_artifact(obj, restoration, artifact_type):
            errors.append(f"The managed {label_text} artifact has invalid ownership metadata.")
            continue
        if str(obj.get(crown_bottom_candidates.META_DEPENDENCY_SIGNATURE, "")) != current_dependency:
            errors.append(f"The managed {label_text} artifact is stale for the current dependencies.")
        stored_mesh = str(obj.get(crown_bottom_candidates.META_MESH_SIGNATURE, ""))
        current_mesh = crown_bottom_candidates.object_mesh_signature(obj)
        if not stored_mesh or stored_mesh != current_mesh:
            errors.append(f"The managed {label_text} artifact changed outside its accepted workflow.")

    if candidate is not None:
        if str(candidate.get(crown_bottom_candidates.META_CANDIDATE_ID, "")) != restoration.selected_candidate_id:
            errors.append("The selected candidate identifier does not match the managed artifact.")

    record, metrics = _record_metrics(restoration)
    if record is None:
        errors.append("The selected candidate metadata is missing or corrupt.")
    elif not record.accepted:
        errors.append("Rejected candidates cannot be approved.")
    if candidate is not None:
        topology_errors, topology_warnings = crown_bottom_candidates.current_candidate_constraints(restoration)
        errors.extend(topology_errors)
        warnings.extend(topology_warnings)
        if record is not None and record.mesh_signature and record.mesh_signature != crown_bottom_candidates.object_mesh_signature(candidate):
            if restoration.step_5_override_used:
                warnings.append("The candidate mesh differs from its generated baseline because a constrained override was applied.")
            else:
                errors.append("The selected candidate no longer matches its generated metadata record.")

    if metrics is None:
        errors.append("The selected candidate metrics are unavailable.")
    else:
        if metrics.rejection_reasons:
            errors.extend(metrics.rejection_reasons)
        if metrics.maximum_margin_deviation > 0.00025:
            warnings.append(f"Maximum margin deviation is {metrics.maximum_margin_deviation * 1000.0:.3f} mm.")
        if metrics.minimum_local_feature_size < 0.00005:
            warnings.append("The candidate contains small local features that require expert review.")
        if metrics.generation_duration >= float(restoration.step_5_maximum_runtime) * 0.8:
            warnings.append("Generation runtime was near the configured limit.")
        if metrics.final_score < 75.0:
            warnings.append("The selected accepted candidate has a relatively low engineering score.")

    records = [item for item in crown_bottom_candidates.candidate_records(restoration) if item.accepted]
    if len(records) > 1:
        ordered = sorted(records, key=lambda item: (-item.score, item.candidate_id))
        if ordered[0].score - ordered[1].score < 2.0:
            warnings.append("The two highest-ranked accepted candidates have similar scores.")
    if restoration.step_5_override_used:
        warnings.append(restoration.step_5_override_note or "A constrained expert correction was applied and requires explicit review.")
    warnings.append("Step 5 checks are engineering constraints and do not certify clinical fit or manufacturability.")

    errors = tuple(dict.fromkeys(errors))
    warnings = tuple(dict.fromkeys(warnings))
    return StepFiveValidationResult(
        ok=not errors,
        status="VALIDATED" if not errors else "ERROR",
        summary=(
            f"{label} crown-bottom candidate passed Step 5 engineering validation."
            if not errors
            else f"Step 5 validation found {len(errors)} blocking error(s) for {label}."
        ),
        errors=errors,
        warnings=warnings,
    )


def approved_signature(state, restoration) -> str:
    candidate = crown_bottom_candidates.resolve_selected_candidate(restoration)
    payload = {
        "dependencies": crown_bottom_candidates.dependency_signature(state, restoration),
        "candidate": restoration.selected_candidate_id,
        "mesh": crown_bottom_candidates.object_mesh_signature(candidate),
        "metrics": str(candidate.get(crown_bottom_candidates.META_METRICS, "")) if candidate is not None else "",
        "settings": crown_bottom_candidates.settings_payload(restoration),
        "override": bool(restoration.step_5_override_used),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
