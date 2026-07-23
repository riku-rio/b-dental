"""Reversible margin-session and approval-monitoring helpers for Step 3."""

from __future__ import annotations

from . import margin_geometry, properties, restoration_utils


def _snapshot_previous_state(state) -> None:
    state.margin_session_status = state.step_3_status
    state.margin_session_valid = state.step_3_valid
    state.margin_session_review_confirmed = state.margin_review_confirmed
    state.margin_session_warning_acknowledged = state.margin_warning_acknowledged
    state.margin_session_summary = state.step_3_summary
    state.margin_session_errors = state.step_3_errors
    state.margin_session_warnings = state.step_3_warnings


def start_session(scene, state):
    """Start a reversible session and return the managed margin object."""

    existing = restoration_utils.resolve_margin(state)
    state.margin_session_had_margin = existing is not None
    state.margin_session_points = margin_geometry.serialize_points(
        margin_geometry.curve_points(existing)
    )
    state.margin_session_cyclic = margin_geometry.curve_is_cyclic(existing)
    _snapshot_previous_state(state)

    margin = margin_geometry.ensure_margin_object(scene, state)
    state.margin_session_active = True
    state.margin_candidate_closed = False
    state.step_3_status = "DRAWING"
    state.step_3_valid = False
    state.margin_review_confirmed = False
    state.margin_warning_acknowledged = False
    state.step_3_summary = "Manual margin session started."
    state.step_3_errors = ""
    state.step_3_warnings = ""
    return margin


def _restore_points(state, *, keep_draft: bool) -> None:
    points = margin_geometry.deserialize_points(state.margin_session_points)
    if state.margin_session_had_margin:
        margin = margin_geometry.ensure_margin_object(state.id_data, state)
        margin_geometry.replace_curve_points(
            margin,
            points,
            cyclic=state.margin_session_cyclic,
        )
        state.margin_object = margin
        return

    restoration_utils.remove_active_margin(state)
    if keep_draft:
        margin = margin_geometry.ensure_margin_object(state.id_data, state)
        margin_geometry.replace_curve_points(margin, (), cyclic=False)


def reset_session(state) -> None:
    _restore_points(state, keep_draft=True)
    state.margin_session_active = True
    state.margin_candidate_closed = False
    state.step_3_status = "DRAWING"
    state.step_3_valid = False
    state.margin_review_confirmed = False
    state.margin_warning_acknowledged = False
    state.step_3_summary = "Margin restored to the session start."
    state.step_3_errors = ""
    state.step_3_warnings = ""


def cancel_session(state) -> None:
    _restore_points(state, keep_draft=False)
    state.margin_session_active = False
    state.margin_candidate_closed = state.margin_session_cyclic
    state.step_3_status = state.margin_session_status
    state.step_3_valid = state.margin_session_valid
    state.margin_review_confirmed = state.margin_session_review_confirmed
    state.margin_warning_acknowledged = state.margin_session_warning_acknowledged
    state.step_3_summary = state.margin_session_summary
    state.step_3_errors = state.margin_session_errors
    state.step_3_warnings = state.margin_session_warnings


def capture_candidate(state) -> tuple[bool, str]:
    margin = restoration_utils.resolve_margin(state)
    points = margin_geometry.curve_points(margin)
    if len(points) < margin_geometry.MIN_MARGIN_POINTS:
        return False, f"Place at least {margin_geometry.MIN_MARGIN_POINTS} points before closing the margin."
    if margin_geometry.unique_point_count(points) < margin_geometry.MIN_MARGIN_POINTS:
        return False, "The margin requires at least six unique points."
    margin_geometry.replace_curve_points(margin, points, cyclic=True)
    state.margin_candidate_closed = True
    state.step_3_status = "CANDIDATE"
    state.step_3_valid = False
    state.step_3_summary = "Closed margin candidate captured. Apply it before validation."
    state.step_3_errors = ""
    state.step_3_warnings = ""
    return True, state.step_3_summary


def apply_candidate(state) -> None:
    state.margin_session_active = False
    state.margin_candidate_closed = True
    state.step_3_status = "CANDIDATE"
    state.step_3_valid = False
    state.margin_review_confirmed = False
    state.margin_warning_acknowledged = False
    state.approved_margin_points = ""
    state.approved_target_signature = ""
    state.approved_target_matrix = ""
    state.approved_upstream_signature = ""
    state.step_3_summary = "Margin candidate applied. Validation and approval are still required."


def snapshot_approved(state) -> None:
    margin = restoration_utils.resolve_margin(state)
    target = restoration_utils.target_scan(state)
    state.approved_margin_points = margin_geometry.serialize_points(
        margin_geometry.curve_points(margin)
    )
    state.approved_target_signature = restoration_utils.target_scan_signature(target)
    state.approved_target_matrix = restoration_utils.target_matrix_signature(target)
    state.approved_upstream_signature = restoration_utils.upstream_approval_signature(state)


def monitor_scene(scene) -> None:
    """Invalidate approved Step 3 state after material dependency changes."""

    if not hasattr(scene, "bdental_workflow"):
        return
    state = scene.bdental_workflow
    if state.internal_update_lock or not state.case_initialized:
        return

    target = restoration_utils.target_scan(state)
    current_target_signature = restoration_utils.target_scan_signature(target)
    margin_pointer = getattr(state, "margin_object", None)

    if margin_pointer is not None and not restoration_utils.is_managed_margin(margin_pointer, state):
        if restoration_utils.is_managed_margin(margin_pointer):
            restoration_utils.remove_margin_object(margin_pointer)
        state.margin_object = None
        properties.invalidate_step_three(state, upstream=not state.step_2_valid)
        state.step_3_status = "SETUP_REQUIRED" if state.step_2_valid else "UPSTREAM_INVALID"
        state.step_3_summary = "The managed margin no longer matches the active restoration setup."
        return

    if state.target_scan_signature and current_target_signature != state.target_scan_signature:
        restoration_utils.remove_active_margin(state)
        state.restoration_id = ""
        state.target_scan_signature = ""
        properties.invalidate_step_three(state, upstream=not state.step_2_valid)
        state.step_3_status = "SETUP_REQUIRED" if state.step_2_valid else "UPSTREAM_INVALID"
        state.step_3_summary = "The target preparation scan changed. Confirm restoration setup again."
        return

    if not state.step_3_valid or state.margin_session_active:
        return

    margin = restoration_utils.resolve_margin(state)
    if margin is None:
        properties.invalidate_step_three(state)
        state.step_3_status = "ERROR"
        state.step_3_summary = "The approved margin is missing."
        return

    current_points = margin_geometry.serialize_points(margin_geometry.curve_points(margin))
    upstream = restoration_utils.upstream_approval_signature(state)
    target_matrix = restoration_utils.target_matrix_signature(target)
    changed = (
        current_points != state.approved_margin_points
        or current_target_signature != state.approved_target_signature
        or target_matrix != state.approved_target_matrix
        or upstream != state.approved_upstream_signature
        or not state.step_2_valid
    )
    if changed:
        properties.invalidate_step_three(state, upstream=not state.step_2_valid)
        state.step_3_summary = "Step 3 approval was invalidated after a material dependency change."


def depsgraph_update_handler(_scene, _depsgraph) -> None:
    import bpy

    for scene in tuple(bpy.data.scenes):
        monitor_scene(scene)
