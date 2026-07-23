"""Reversible margin-session and approval-monitoring helpers for Step 3."""

from __future__ import annotations

from . import margin_geometry, properties, restoration_utils


def _snapshot_previous_state(restoration) -> None:
    restoration.margin_session_status = restoration.status
    restoration.margin_session_valid = restoration.valid
    restoration.margin_session_review_confirmed = restoration.review_confirmed
    restoration.margin_session_warning_acknowledged = restoration.warning_acknowledged
    restoration.margin_session_summary = restoration.summary
    restoration.margin_session_errors = restoration.errors
    restoration.margin_session_warnings = restoration.warnings


def start_session(scene, state, restoration):
    existing = restoration_utils.resolve_margin(restoration)
    restoration.margin_session_had_margin = existing is not None
    restoration.margin_session_points = margin_geometry.serialize_points(
        margin_geometry.curve_points(existing)
    )
    restoration.margin_session_cyclic = margin_geometry.curve_is_cyclic(existing)
    _snapshot_previous_state(restoration)

    margin = margin_geometry.ensure_margin_object(scene, state, restoration)
    restoration.margin_session_active = True
    restoration.margin_candidate_closed = False
    restoration.status = "DRAWING"
    restoration.valid = False
    restoration.review_confirmed = False
    restoration.warning_acknowledged = False
    restoration.summary = "Manual margin session started."
    restoration.errors = ""
    restoration.warnings = ""
    properties.sync_step_three_state(state)
    return margin


def _restore_points(state, restoration, *, keep_draft: bool) -> None:
    points = margin_geometry.deserialize_points(restoration.margin_session_points)
    if restoration.margin_session_had_margin:
        margin = margin_geometry.ensure_margin_object(state.id_data, state, restoration)
        margin_geometry.replace_curve_points(
            margin,
            points,
            cyclic=restoration.margin_session_cyclic,
        )
        restoration.margin_object = margin
        return

    restoration_utils.remove_restoration_margin(restoration)
    if keep_draft:
        margin = margin_geometry.ensure_margin_object(state.id_data, state, restoration)
        margin_geometry.replace_curve_points(margin, (), cyclic=False)


def reset_session(state, restoration) -> None:
    _restore_points(state, restoration, keep_draft=True)
    restoration.margin_session_active = True
    restoration.margin_candidate_closed = False
    restoration.status = "DRAWING"
    restoration.valid = False
    restoration.review_confirmed = False
    restoration.warning_acknowledged = False
    restoration.summary = "Margin restored to the session start."
    restoration.errors = ""
    restoration.warnings = ""
    properties.sync_step_three_state(state)


def cancel_session(state, restoration) -> None:
    _restore_points(state, restoration, keep_draft=False)
    restoration.margin_session_active = False
    restoration.margin_candidate_closed = restoration.margin_session_cyclic
    restoration.status = restoration.margin_session_status
    restoration.valid = restoration.margin_session_valid
    restoration.review_confirmed = restoration.margin_session_review_confirmed
    restoration.warning_acknowledged = restoration.margin_session_warning_acknowledged
    restoration.summary = restoration.margin_session_summary
    restoration.errors = restoration.margin_session_errors
    restoration.warnings = restoration.margin_session_warnings
    properties.sync_step_three_state(state)


def capture_candidate(state, restoration) -> tuple[bool, str]:
    margin = restoration_utils.resolve_margin(restoration)
    points = margin_geometry.curve_points(margin)
    if len(points) < margin_geometry.MIN_MARGIN_POINTS:
        return False, f"Place at least {margin_geometry.MIN_MARGIN_POINTS} points before closing the margin."
    if margin_geometry.unique_point_count(points) < margin_geometry.MIN_MARGIN_POINTS:
        return False, "The margin requires at least six unique points."
    margin_geometry.replace_curve_points(margin, points, cyclic=True)
    restoration.margin_candidate_closed = True
    restoration.status = "CANDIDATE"
    restoration.valid = False
    restoration.summary = "Closed margin candidate captured. Apply it before validation."
    restoration.errors = ""
    restoration.warnings = ""
    properties.sync_step_three_state(state)
    return True, restoration.summary


def apply_candidate(state, restoration) -> None:
    restoration.margin_session_active = False
    restoration.margin_candidate_closed = True
    restoration.status = "CANDIDATE"
    restoration.valid = False
    restoration.review_confirmed = False
    restoration.warning_acknowledged = False
    restoration.approved_margin_points = ""
    restoration.approved_target_signature = ""
    restoration.approved_target_matrix = ""
    restoration.approved_upstream_signature = ""
    restoration.summary = "Margin candidate applied. Validation and approval are still required."
    properties.sync_step_three_state(state)


def snapshot_approved(state, restoration) -> None:
    margin = restoration_utils.resolve_margin(restoration)
    target = restoration_utils.target_scan(state, restoration)
    restoration.approved_margin_points = margin_geometry.serialize_points(
        margin_geometry.curve_points(margin)
    )
    restoration.approved_target_signature = restoration_utils.target_scan_signature(target)
    restoration.approved_target_matrix = restoration_utils.target_matrix_signature(target)
    restoration.approved_upstream_signature = restoration_utils.upstream_approval_signature(state)


def monitor_scene(scene) -> None:
    if not hasattr(scene, "bdental_workflow"):
        return
    state = scene.bdental_workflow
    if state.internal_update_lock or not state.case_initialized:
        return

    restoration_utils.migrate_legacy_restoration(state)
    upstream_signature = restoration_utils.upstream_approval_signature(state)

    for restoration in state.restorations:
        target = restoration_utils.target_scan(state, restoration)
        target_signature = restoration_utils.target_scan_signature(target)
        margin_pointer = getattr(restoration, "margin_object", None)

        if margin_pointer is not None and not restoration_utils.is_managed_margin(
            margin_pointer, restoration
        ):
            if restoration_utils.is_managed_margin(margin_pointer):
                restoration_utils.remove_margin_object(margin_pointer)
            restoration.margin_object = None
            properties.clear_restoration_approval(restoration)
            restoration.status = "ERROR"
            restoration.summary = "The managed margin no longer matches this restoration."
            continue

        if restoration.target_scan_signature and target_signature != restoration.target_scan_signature:
            restoration_utils.remove_restoration_margin(restoration)
            properties.clear_restoration_approval(restoration)
            restoration.status = "ERROR" if state.step_2_valid else "UPSTREAM_INVALID"
            restoration.summary = "The target preparation scan changed. Recreate this restoration."
            continue

        if not restoration.valid or restoration.margin_session_active:
            continue

        margin = restoration_utils.resolve_margin(restoration)
        if margin is None:
            properties.clear_restoration_approval(restoration)
            restoration.status = "ERROR"
            restoration.summary = "The approved margin is missing."
            continue

        current_points = margin_geometry.serialize_points(margin_geometry.curve_points(margin))
        target_matrix = restoration_utils.target_matrix_signature(target)
        changed = (
            current_points != restoration.approved_margin_points
            or target_signature != restoration.approved_target_signature
            or target_matrix != restoration.approved_target_matrix
            or upstream_signature != restoration.approved_upstream_signature
            or not state.step_2_valid
        )
        if changed:
            properties.clear_restoration_approval(restoration)
            restoration.status = "CANDIDATE" if state.step_2_valid else "UPSTREAM_INVALID"
            restoration.summary = "Approval was invalidated after a material dependency change."

    properties.sync_step_three_state(state)


def depsgraph_update_handler(_scene, _depsgraph) -> None:
    import bpy

    for scene in tuple(bpy.data.scenes):
        monitor_scene(scene)
