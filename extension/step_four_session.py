"""Persistent state, reversible sessions, invalidation, and monitoring for Step 4."""

from __future__ import annotations

import json
from collections.abc import Iterable

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty

from . import axis_geometry, preparation_analysis, properties, restoration_utils, step_four_validation

STEP_FOUR_STATUS_ITEMS = (
    ("READY_FOR_AXIS", "Ready for Axis", "Define an insertion axis"),
    ("AXIS_EDITING", "Axis Editing", "A reversible axis session is active"),
    ("AXIS_CANDIDATE", "Axis Candidate", "An axis candidate requires analysis"),
    ("ANALYZED", "Analyzed", "Current analysis requires approval"),
    ("VERIFIED", "Verified", "Step 4 is approved for this restoration"),
    ("UPSTREAM_INVALID", "Upstream Invalid", "Step 3 must be approved again"),
    ("ERROR", "Error", "Step 4 contains blocking errors"),
)

AGGREGATE_STEP_FOUR_STATUS_ITEMS = (
    ("NOT_STARTED", "Not Started", "Step 4 has not started"),
    *STEP_FOUR_STATUS_ITEMS,
)

AXIS_SOURCE_ITEMS = (
    ("NONE", "None", "No insertion axis has been defined"),
    ("CURRENT_VIEW", "Current View", "Captured from the current 3D View"),
    ("MARGIN_SUGGESTION", "Margin Suggestion", "Suggested from the approved margin"),
    ("MANUAL_EDIT", "Manual Edit", "Captured from the managed axis object"),
)


def clear_step_four_approval(restoration) -> None:
    restoration.step_4_valid = False
    restoration.step_4_review_confirmed = False
    restoration.step_4_warning_acknowledged = False
    restoration.approved_step_4_signature = ""
    restoration.approved_axis_local = ""
    restoration.approved_analysis_signature = ""


def clear_step_four_analysis(restoration) -> None:
    clear_step_four_approval(restoration)
    preparation_analysis.clear_analysis(restoration)
    if restoration.insertion_axis_local:
        restoration.step_4_status = "AXIS_CANDIDATE"
    else:
        restoration.step_4_status = "READY_FOR_AXIS"


def invalidate_restoration(restoration, *, upstream: bool = False, preserve_axis: bool = True) -> None:
    restoration.axis_session_active = False
    clear_step_four_approval(restoration)
    preparation_analysis.clear_analysis(restoration)
    if upstream:
        restoration.step_4_status = "UPSTREAM_INVALID"
        restoration.step_4_summary = "Step 4 approval was invalidated by an upstream workflow change."
    elif preserve_axis and restoration.insertion_axis_local:
        restoration.step_4_status = "AXIS_CANDIDATE"
        restoration.step_4_summary = "Step 4 analysis was invalidated after a material dependency change."
    else:
        restoration.insertion_axis_local = ""
        restoration.axis_source = "NONE"
        axis_geometry.remove_restoration_axis(restoration)
        restoration.step_4_status = "READY_FOR_AXIS"
        restoration.step_4_summary = "Define an insertion axis."
    restoration.step_4_errors = ""
    restoration.step_4_warnings = ""


def sync_step_four_state(state) -> None:
    restorations = tuple(state.restorations)
    if not restorations:
        state.step_4_status = "NOT_STARTED"
        state.step_4_valid = False
        return
    if not state.step_3_valid:
        state.step_4_status = "UPSTREAM_INVALID"
        state.step_4_valid = False
        return
    if any(restoration.axis_session_active for restoration in restorations):
        state.step_4_status = "AXIS_EDITING"
        state.step_4_valid = False
        return
    if all(restoration.step_4_valid and restoration.step_4_status == "VERIFIED" for restoration in restorations):
        state.step_4_status = "VERIFIED"
        state.step_4_valid = True
        return
    active = restoration_utils.active_restoration(state)
    state.step_4_status = active.step_4_status if active is not None else "NOT_STARTED"
    state.step_4_valid = False


def _snapshot_payload(restoration) -> dict:
    axis_obj = axis_geometry.resolve_axis(restoration)
    return {
        "insertion_axis_local": restoration.insertion_axis_local,
        "axis_source": restoration.axis_source,
        "axis_had_object": axis_obj is not None,
        "axis_matrix": axis_geometry.serialize_matrix(axis_obj.matrix_basis.copy()) if axis_obj else "",
        "analysis_radius": float(restoration.analysis_radius),
        "analysis_current": bool(restoration.analysis_current),
        "analysis_samples": restoration.analysis_samples,
        "analysis_sample_count": int(restoration.analysis_sample_count),
        "analysis_undercut_count": int(restoration.analysis_undercut_count),
        "analysis_undercut_ratio": float(restoration.analysis_undercut_ratio),
        "analysis_mean_blocking_depth": float(restoration.analysis_mean_blocking_depth),
        "analysis_max_blocking_depth": float(restoration.analysis_max_blocking_depth),
        "analysis_duration_seconds": float(restoration.analysis_duration_seconds),
        "analysis_signature": restoration.analysis_signature,
        "analysis_overlay_visible": bool(restoration.analysis_overlay_visible),
        "step_4_status": restoration.step_4_status,
        "step_4_valid": bool(restoration.step_4_valid),
        "step_4_review_confirmed": bool(restoration.step_4_review_confirmed),
        "step_4_warning_acknowledged": bool(restoration.step_4_warning_acknowledged),
        "step_4_summary": restoration.step_4_summary,
        "step_4_errors": restoration.step_4_errors,
        "step_4_warnings": restoration.step_4_warnings,
        "approved_step_4_signature": restoration.approved_step_4_signature,
        "approved_axis_local": restoration.approved_axis_local,
        "approved_analysis_signature": restoration.approved_analysis_signature,
    }


def _restore_payload(scene, state, restoration, payload: dict, *, keep_session: bool) -> None:
    restoration.insertion_axis_local = str(payload.get("insertion_axis_local", ""))
    restoration.axis_source = str(payload.get("axis_source", "NONE"))
    state.internal_update_lock = True
    try:
        restoration.analysis_radius = float(payload.get("analysis_radius", preparation_analysis.DEFAULT_ANALYSIS_RADIUS))
    finally:
        state.internal_update_lock = False
    restoration.analysis_current = bool(payload.get("analysis_current", False))
    restoration.analysis_samples = str(payload.get("analysis_samples", ""))
    restoration.analysis_sample_count = int(payload.get("analysis_sample_count", 0))
    restoration.analysis_undercut_count = int(payload.get("analysis_undercut_count", 0))
    restoration.analysis_undercut_ratio = float(payload.get("analysis_undercut_ratio", 0.0))
    restoration.analysis_mean_blocking_depth = float(payload.get("analysis_mean_blocking_depth", 0.0))
    restoration.analysis_max_blocking_depth = float(payload.get("analysis_max_blocking_depth", 0.0))
    restoration.analysis_duration_seconds = float(payload.get("analysis_duration_seconds", 0.0))
    restoration.analysis_signature = str(payload.get("analysis_signature", ""))
    restoration.analysis_overlay_visible = bool(payload.get("analysis_overlay_visible", False))
    restoration.step_4_status = "AXIS_EDITING" if keep_session else str(payload.get("step_4_status", "READY_FOR_AXIS"))
    restoration.step_4_valid = False if keep_session else bool(payload.get("step_4_valid", False))
    restoration.step_4_review_confirmed = False if keep_session else bool(payload.get("step_4_review_confirmed", False))
    restoration.step_4_warning_acknowledged = False if keep_session else bool(payload.get("step_4_warning_acknowledged", False))
    restoration.step_4_summary = "Axis restored to the session start." if keep_session else str(payload.get("step_4_summary", ""))
    restoration.step_4_errors = "" if keep_session else str(payload.get("step_4_errors", ""))
    restoration.step_4_warnings = "" if keep_session else str(payload.get("step_4_warnings", ""))
    restoration.approved_step_4_signature = "" if keep_session else str(payload.get("approved_step_4_signature", ""))
    restoration.approved_axis_local = "" if keep_session else str(payload.get("approved_axis_local", ""))
    restoration.approved_analysis_signature = "" if keep_session else str(payload.get("approved_analysis_signature", ""))

    if payload.get("axis_had_object") and restoration.insertion_axis_local:
        obj = axis_geometry.ensure_axis_object(scene, state, restoration)
        matrix = axis_geometry.deserialize_matrix(str(payload.get("axis_matrix", "")))
        if matrix is not None:
            obj.matrix_basis = matrix
    else:
        axis_geometry.remove_restoration_axis(restoration)


def start_session(scene, state, restoration) -> bpy.types.Object:
    if restoration.axis_session_active:
        raise ValueError("An axis session is already active.")
    if not restoration.insertion_axis_local:
        raise ValueError("Create an axis candidate before starting manual editing.")
    restoration.axis_session_snapshot = json.dumps(_snapshot_payload(restoration), separators=(",", ":"))
    obj = axis_geometry.ensure_axis_object(scene, state, restoration)
    restoration.axis_session_active = True
    clear_step_four_approval(restoration)
    restoration.step_4_status = "AXIS_EDITING"
    restoration.step_4_summary = "Reversible insertion-axis edit session started."
    restoration.step_4_errors = ""
    restoration.step_4_warnings = ""
    sync_step_four_state(state)
    return obj


def _session_payload(restoration) -> dict:
    if not restoration.axis_session_snapshot:
        raise ValueError("The axis-session snapshot is unavailable.")
    try:
        return json.loads(restoration.axis_session_snapshot)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("The axis-session snapshot is corrupted.") from exc


def reset_session(scene, state, restoration) -> None:
    payload = _session_payload(restoration)
    _restore_payload(scene, state, restoration, payload, keep_session=True)
    restoration.axis_session_active = True
    sync_step_four_state(state)


def cancel_session(scene, state, restoration) -> None:
    payload = _session_payload(restoration)
    _restore_payload(scene, state, restoration, payload, keep_session=False)
    restoration.axis_session_active = False
    restoration.axis_session_snapshot = ""
    sync_step_four_state(state)


def capture_candidate(state, restoration) -> None:
    axis = axis_geometry.capture_axis_from_object(restoration)
    if axis is None:
        raise ValueError("The managed axis orientation could not be captured.")
    restoration.insertion_axis_local = axis_geometry.serialize_vector(axis)
    restoration.axis_source = "MANUAL_EDIT"
    clear_step_four_analysis(restoration)
    restoration.axis_session_active = True
    restoration.step_4_status = "AXIS_EDITING"
    restoration.step_4_summary = "Manual insertion-axis candidate captured. Apply or cancel the session."
    sync_step_four_state(state)


def apply_candidate(state, restoration) -> None:
    if not restoration.axis_session_active:
        raise ValueError("No axis session is active.")
    axis = axis_geometry.capture_axis_from_object(restoration)
    if axis is None:
        raise ValueError("The managed axis orientation could not be applied.")
    restoration.insertion_axis_local = axis_geometry.serialize_vector(axis)
    restoration.axis_source = "MANUAL_EDIT"
    restoration.axis_session_active = False
    restoration.axis_session_snapshot = ""
    clear_step_four_analysis(restoration)
    restoration.step_4_status = "AXIS_CANDIDATE"
    restoration.step_4_summary = "Insertion-axis candidate applied. Run undercut analysis before approval."
    sync_step_four_state(state)


def snapshot_approved(state, restoration) -> None:
    restoration.approved_axis_local = axis_geometry.serialize_vector(
        axis_geometry.deserialize_vector(restoration.insertion_axis_local)
    )
    restoration.approved_analysis_signature = restoration.analysis_signature
    restoration.approved_step_4_signature = step_four_validation.approved_signature(state, restoration)


def _radius_updated(restoration, context) -> None:
    state = context.scene.bdental_workflow if context and context.scene else None
    if state is None or state.internal_update_lock:
        return
    clear_step_four_analysis(restoration)
    restoration.step_4_summary = "Analysis radius changed. Run undercut analysis again."
    sync_step_four_state(state)


def _inject_properties() -> None:
    workflow = properties.BDENTAL_PG_WorkflowState.__annotations__
    workflow["current_step"] = EnumProperty(
        name="Current Step",
        items=(*properties.WORKFLOW_STEP_ITEMS, ("STEP_4", "Step 4", "Define insertion axes and analyze preparations")),
        default="STEP_1",
    )
    workflow.setdefault("step_4_status", EnumProperty(name="Step 4 Status", items=AGGREGATE_STEP_FOUR_STATUS_ITEMS, default="NOT_STARTED"))
    workflow.setdefault("step_4_valid", BoolProperty(name="Step 4 Valid", default=False))
    workflow.setdefault("step_4_summary", StringProperty(default=""))
    workflow.setdefault("step_4_errors", StringProperty(default=""))
    workflow.setdefault("step_4_warnings", StringProperty(default=""))

    annotations = properties.BDENTAL_PG_RestorationState.__annotations__
    annotations.setdefault("step_4_status", EnumProperty(name="Step 4 Status", items=STEP_FOUR_STATUS_ITEMS, default="READY_FOR_AXIS"))
    annotations.setdefault("step_4_valid", BoolProperty(name="Step 4 Approved", default=False))
    annotations.setdefault("insertion_axis_local", StringProperty(default=""))
    annotations.setdefault("axis_source", EnumProperty(name="Axis Source", items=AXIS_SOURCE_ITEMS, default="NONE"))
    annotations.setdefault("axis_object", PointerProperty(name="Insertion Axis", type=bpy.types.Object))
    annotations.setdefault("axis_session_active", BoolProperty(name="Axis Session Active", default=False))
    annotations.setdefault("axis_session_snapshot", StringProperty(default=""))
    annotations.setdefault("analysis_radius", FloatProperty(name="Analysis Radius", default=preparation_analysis.DEFAULT_ANALYSIS_RADIUS, min=preparation_analysis.MIN_ANALYSIS_RADIUS, max=preparation_analysis.MAX_ANALYSIS_RADIUS, subtype="DISTANCE", unit="LENGTH", update=_radius_updated))
    annotations.setdefault("analysis_current", BoolProperty(default=False))
    annotations.setdefault("analysis_samples", StringProperty(default=""))
    annotations.setdefault("analysis_sample_count", IntProperty(default=0, min=0))
    annotations.setdefault("analysis_undercut_count", IntProperty(default=0, min=0))
    annotations.setdefault("analysis_undercut_ratio", FloatProperty(default=0.0, min=0.0, max=1.0))
    annotations.setdefault("analysis_mean_blocking_depth", FloatProperty(default=0.0, min=0.0))
    annotations.setdefault("analysis_max_blocking_depth", FloatProperty(default=0.0, min=0.0))
    annotations.setdefault("analysis_duration_seconds", FloatProperty(default=0.0, min=0.0))
    annotations.setdefault("analysis_signature", StringProperty(default=""))
    annotations.setdefault("analysis_overlay_visible", BoolProperty(name="Show Analysis Overlay", default=False))
    annotations.setdefault("step_4_summary", StringProperty(default=""))
    annotations.setdefault("step_4_errors", StringProperty(default=""))
    annotations.setdefault("step_4_warnings", StringProperty(default=""))
    annotations.setdefault("step_4_review_confirmed", BoolProperty(name="I Reviewed the Axis and Analysis", default=False))
    annotations.setdefault("step_4_warning_acknowledged", BoolProperty(name="Acknowledge Step 4 Warnings", default=False))
    annotations.setdefault("approved_axis_local", StringProperty(default=""))
    annotations.setdefault("approved_analysis_signature", StringProperty(default=""))
    annotations.setdefault("approved_step_4_signature", StringProperty(default=""))


def _patch_step_three_invalidation() -> None:
    if hasattr(properties, "_bdental_step_four_original_clear_restoration_approval"):
        return
    original = properties.clear_restoration_approval
    properties._bdental_step_four_original_clear_restoration_approval = original

    def wrapped(restoration) -> None:
        original(restoration)
        if hasattr(restoration, "step_4_status"):
            invalidate_restoration(restoration, preserve_axis=True)

    properties.clear_restoration_approval = wrapped


def _patch_restoration_artifacts() -> None:
    if not hasattr(restoration_utils, "_bdental_step_four_original_iter_artifacts"):
        original_iter = restoration_utils.iter_managed_restoration_artifacts
        restoration_utils._bdental_step_four_original_iter_artifacts = original_iter

        def iter_artifacts(scene) -> Iterable[bpy.types.Object]:
            seen: set[int] = set()
            for obj in original_iter(scene):
                pointer = obj.as_pointer()
                if pointer not in seen:
                    seen.add(pointer)
                    yield obj
            for obj in axis_geometry.iter_managed_axes(scene):
                pointer = obj.as_pointer()
                if pointer not in seen:
                    seen.add(pointer)
                    yield obj

        restoration_utils.iter_managed_restoration_artifacts = iter_artifacts

    if not hasattr(restoration_utils, "_bdental_step_four_original_remove_all_artifacts"):
        original_remove_all = restoration_utils.remove_all_managed_restoration_artifacts
        restoration_utils._bdental_step_four_original_remove_all_artifacts = original_remove_all

        def remove_all(scene, state) -> int:
            axes = {obj.as_pointer(): obj for obj in axis_geometry.iter_managed_axes(scene)}
            for restoration in state.restorations:
                obj = axis_geometry.resolve_axis(restoration)
                if obj is not None:
                    axes[obj.as_pointer()] = obj
                restoration.axis_object = None
            removed = original_remove_all(scene, state)
            removed += sum(1 for obj in axes.values() if axis_geometry.remove_axis_object(obj))
            return removed

        restoration_utils.remove_all_managed_restoration_artifacts = remove_all


def monitor_scene(scene) -> None:
    if not hasattr(scene, "bdental_workflow"):
        return
    state = scene.bdental_workflow
    if state.internal_update_lock or not state.case_initialized:
        return

    for restoration in state.restorations:
        if not state.step_3_valid or not restoration.valid or restoration.status != "VERIFIED":
            if restoration.step_4_status != "UPSTREAM_INVALID" or restoration.step_4_valid:
                invalidate_restoration(restoration, upstream=True, preserve_axis=True)
            continue

        pointer = getattr(restoration, "axis_object", None)
        obj = axis_geometry.resolve_axis(restoration)
        if pointer is not None and not axis_geometry.is_managed_axis(pointer, restoration):
            if axis_geometry.is_managed_axis(pointer):
                axis_geometry.remove_axis_object(pointer)
            restoration.axis_object = None
            invalidate_restoration(restoration, preserve_axis=False)
            restoration.step_4_status = "ERROR"
            restoration.step_4_summary = "The managed insertion axis no longer matches this restoration."
            continue

        if restoration.analysis_current and restoration.analysis_signature != step_four_validation.dependency_signature(state, restoration):
            invalidate_restoration(restoration, preserve_axis=True)

        if restoration.step_4_valid:
            current = step_four_validation.approved_signature(state, restoration)
            if not restoration.approved_step_4_signature or current != restoration.approved_step_4_signature:
                invalidate_restoration(restoration, preserve_axis=True)

        if obj is not None:
            obj.color = axis_geometry._axis_color(restoration)

    sync_step_four_state(state)


_inject_properties()
_patch_step_three_invalidation()
_patch_restoration_artifacts()
