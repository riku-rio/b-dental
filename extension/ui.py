"""Workflow-aware 3D Viewport sidebar interface for B-Dental."""

import textwrap

import bpy

from . import properties, restoration_utils, scene_utils

_WRAP_WIDTH = 38


def _draw_wrapped_label(layout, text: str, *, icon: str = "NONE") -> None:
    first = True
    for line in textwrap.wrap(text, width=_WRAP_WIDTH) or [""]:
        layout.label(text=line, icon=icon if first else "NONE")
        first = False


def _draw_messages(layout, messages: str, *, title: str, icon: str) -> None:
    items = [message.strip() for message in messages.splitlines() if message.strip()]
    if not items:
        return
    box = layout.box()
    box.label(text=title, icon=icon)
    for message in items:
        _draw_wrapped_label(box, message)


def _object_summary(obj) -> str:
    return scene_utils.scan_source_name(obj) or obj.name


def _draw_scan_slot(layout, state, role: str) -> None:
    box = layout.box()
    box.label(text=properties.role_label(role), icon="MESH_DATA")
    obj = scene_utils.get_role_object(state, role)
    if obj is None:
        box.label(text="No scan imported", icon="INFO")
        operator = box.operator("bdental.import_scan", text="Import STL", icon="IMPORT")
        operator.role = role
        operator.replace_existing = False
        return
    _draw_wrapped_label(box, _object_summary(obj), icon="CHECKMARK")
    if obj.type == "MESH" and obj.data is not None:
        dimensions_mm = tuple(float(value) * 1000.0 for value in obj.dimensions)
        box.label(text=f"{len(obj.data.vertices):,} vertices | {len(obj.data.polygons):,} faces")
        box.label(text=f"{dimensions_mm[0]:.1f} x {dimensions_mm[1]:.1f} x {dimensions_mm[2]:.1f} mm")
    row = box.row(align=True)
    focus = row.operator("bdental.focus_scan", text="Focus", icon="VIEWZOOM")
    focus.role = role
    replace = row.operator("bdental.import_scan", text="Replace", icon="FILE_REFRESH")
    replace.role = role
    replace.replace_existing = True
    remove = row.operator("bdental.remove_scan", text="Remove", icon="TRASH")
    remove.role = role


def _draw_step_one(layout, state) -> None:
    header = layout.box()
    header.label(text="Step 1 of 3", icon="IMPORT")
    header.label(text="Import Intra-Oral Scans")
    if state.case_initialized:
        layout.operator("bdental.start_case", text="Reset Dental Case", icon="FILE_REFRESH")
    else:
        layout.operator("bdental.start_case", text="Start New Dental Case", icon="FILE_NEW")
        _draw_wrapped_label(layout.box(), "Start a case before importing scans.", icon="INFO")
        return
    settings = layout.box()
    settings.label(text="Scan Configuration")
    settings.prop(state, "scan_configuration", text="")
    if state.scan_configuration == "SINGLE_ARCH":
        settings.prop(state, "single_arch_role")
    settings.prop(state, "source_unit")
    for role in properties.required_roles(state):
        _draw_scan_slot(layout, state, role)
    validation = layout.box()
    validation.label(text="Validation")
    if state.step_1_valid:
        validation.label(text="Step 1 passed validation", icon="CHECKMARK")
    else:
        validation.label(text="Import all required scans", icon="INFO")
    if state.validation_summary:
        _draw_wrapped_label(validation, state.validation_summary)
    _draw_messages(layout, state.validation_errors, title="Blocking Errors", icon="ERROR")
    _draw_messages(layout, state.validation_warnings, title="Warnings", icon="INFO")
    layout.operator("bdental.validate_step_one", text="Validate & Continue", icon="FILE_TICK")


def _draw_step_two_objects(layout, state) -> None:
    box = layout.box()
    box.label(text="Scan Visibility")
    for role in properties.SCAN_ROLES:
        obj = scene_utils.get_role_object(state, role)
        if obj is None:
            continue
        row = box.row(align=True)
        row.label(text=properties.role_label(role))
        focus = row.operator("bdental.focus_scan", text="", icon="VIEWZOOM")
        focus.role = role
        visibility = row.operator(
            "bdental.toggle_scan_visibility",
            text="",
            icon="HIDE_ON" if obj.hide_viewport else "HIDE_OFF",
        )
        visibility.role = role


def _draw_metrics(layout, state) -> None:
    if state.registration_inlier_count <= 0:
        return
    box = layout.box()
    box.label(text="Registration Metrics", icon="DRIVER_DISTANCE")
    box.label(text=f"Iterations: {state.registration_iterations}")
    box.label(text=f"Inliers: {state.registration_inlier_count:,}")
    box.label(text=f"Inlier ratio: {state.registration_inlier_ratio:.3f}")
    box.label(text=f"RMSE: {state.registration_rmse * 1000.0:.3f} mm")
    box.label(text=f"Median: {state.registration_median_distance * 1000.0:.3f} mm")


def _draw_step_two_completion(layout, state) -> None:
    layout.operator("bdental.enter_step_three", text="Continue to Step 3", icon="FORWARD")
    _draw_step_two_objects(layout, state)
    layout.operator("bdental.back_to_step_one_safe", text="Back to Step 1", icon="BACK")


def _draw_step_two(layout, state) -> None:
    header = layout.box()
    header.label(text="Step 1 Complete", icon="CHECKMARK")
    header.label(text="Step 2 of 3")
    header.label(text="Occlusion Registration & Verification")
    header.label(text=f"Status: {state.step_2_status.replace('_', ' ').title()}")

    if state.scan_configuration == "SINGLE_ARCH":
        info = layout.box()
        _draw_wrapped_label(info, "Occlusion registration is not applicable to a single-arch case.", icon="INFO")
        if state.step_2_valid:
            info.label(text="Step 2 Complete", icon="CHECKMARK")
            _draw_step_two_completion(layout, state)
        else:
            layout.operator("bdental.complete_step_two_na", text="Complete as Not Applicable", icon="CHECKMARK")
            layout.operator("bdental.back_to_step_one_safe", text="Back to Step 1", icon="BACK")
        return

    if state.step_2_status == "VERIFIED" and state.step_2_valid:
        complete = layout.box()
        complete.label(text="Step 2 Verified", icon="CHECKMARK")
        _draw_wrapped_label(complete, state.step_2_summary or "Occlusal relationship approved.")
        _draw_metrics(layout, state)
        _draw_step_two_completion(layout, state)
        return

    analysis = layout.box()
    analysis.label(text="Imported Relationship")
    analysis.operator("bdental.analyze_step_two", text="Analyze Imported Relationship", icon="VIEWZOOM")
    settings = layout.box()
    settings.label(text="Alignment Path")
    settings.prop(state, "alignment_mode", text="")
    if state.alignment_mode == "BITE_GUIDED":
        settings.prop(state, "bite_source", text="")
    if not state.alignment_session_active:
        if state.alignment_mode in {"MANUAL", "BITE_GUIDED"}:
            layout.operator("bdental.start_step_two_session", text="Start Alignment Session", icon="PLAY")
    else:
        session = layout.box()
        session.label(text="Alignment Session Active", icon="REC")
        if state.alignment_mode == "MANUAL":
            session.operator("bdental.capture_manual_step_two", text="Capture Manual Candidate", icon="CHECKMARK")
        else:
            session.operator("bdental.run_bite_step_two", text="Run Bite-Guided Registration", icon="MODIFIER")
        row = session.row(align=True)
        row.operator("bdental.reset_step_two_preview", text="Reset", icon="LOOP_BACK")
        row.operator("bdental.cancel_step_two_session", text="Cancel", icon="CANCEL")
        if state.step_2_status == "CANDIDATE":
            session.operator("bdental.apply_step_two_candidate", text="Apply Candidate", icon="CHECKMARK")
    if state.step_2_status in {"CANDIDATE", "IMPORTED_CANDIDATE"} or state.candidate_applied:
        layout.operator("bdental.verify_step_two", text="Run Verification Checks", icon="FILE_TICK")
    _draw_messages(layout, state.step_2_errors, title="Blocking Errors", icon="ERROR")
    _draw_messages(layout, state.step_2_warnings, title="Warnings", icon="INFO")
    if state.step_2_status in {"CANDIDATE", "IMPORTED_CANDIDATE"} and not state.alignment_session_active:
        approval = layout.box()
        approval.prop(state, "review_confirmed")
        if state.step_2_warnings:
            approval.prop(state, "warning_acknowledged")
        approval.operator("bdental.approve_step_two", text="Approve Occlusion", icon="CHECKMARK")
    _draw_step_two_objects(layout, state)
    layout.operator("bdental.back_to_step_one_safe", text="Back to Step 1", icon="BACK")


def _draw_restoration_list(layout, state) -> None:
    box = layout.box()
    box.label(text=f"Restorations ({len(state.restorations)})", icon="OUTLINER_COLLECTION")
    if not state.restorations:
        box.label(text="No restorations configured", icon="INFO")
        return
    for index, restoration in enumerate(state.restorations):
        row = box.row(align=True)
        icon = "CHECKMARK" if restoration.valid else ("REC" if restoration.margin_session_active else "CURVE_DATA")
        operator = row.operator(
            "bdental.select_restoration",
            text=f"FDI {restoration.target_tooth_fdi} | {properties.role_label(restoration.target_arch)}",
            icon=icon,
            depress=index == state.active_restoration_index,
        )
        operator.index = index
        row.label(text=restoration.status.replace("_", " ").title())


def _draw_add_restoration(layout, state) -> None:
    box = layout.box()
    box.label(text="Add Restoration", icon="ADD")
    controls = box.column()
    if state.scan_configuration == "SINGLE_ARCH":
        controls.label(text=f"Preparation Arch: {properties.role_label(state.new_target_arch)}")
    else:
        controls.prop(state, "new_target_arch")
    controls.prop(state, "new_target_tooth_fdi")
    box.operator("bdental.add_restoration", text="Add Anatomical Crown", icon="ADD")


def _draw_restoration_diagnostics(layout, restoration) -> None:
    if restoration.margin_point_count <= 0:
        return
    box = layout.box()
    box.label(text="Margin Diagnostics", icon="DRIVER_DISTANCE")
    box.label(text=f"Points: {restoration.margin_point_count}")
    box.label(text=f"Path length: {restoration.margin_path_length * 1000.0:.3f} mm")
    box.label(text=f"Mean surface distance: {restoration.margin_mean_surface_distance * 1000.0:.3f} mm")
    box.label(text=f"Max surface distance: {restoration.margin_max_surface_distance * 1000.0:.3f} mm")


def _draw_active_restoration(layout, state, context) -> None:
    restoration = restoration_utils.active_restoration(state)
    if restoration is None:
        return
    margin = restoration_utils.resolve_margin(restoration)
    target = restoration_utils.target_scan(state, restoration)

    box = layout.box()
    box.label(text=f"Active: FDI {restoration.target_tooth_fdi}", icon="TOOTH" if hasattr(bpy.types, "TOOTH") else "MESH_DATA")
    box.label(text=f"Preparation: {properties.role_label(restoration.target_arch)}")
    box.label(text=f"Status: {restoration.status.replace('_', ' ').title()}")
    row = box.row(align=True)
    row.operator("bdental.focus_step_three_target", text="Focus Scan", icon="VIEWZOOM")
    row.operator("bdental.remove_restoration", text="Remove", icon="TRASH")

    margin_box = layout.box()
    margin_box.label(text="Manual Margin", icon="CURVE_DATA")
    if restoration.margin_session_active:
        margin_box.label(text="Reversible session active", icon="REC")
        if context.object is not None and context.object.mode == "EDIT":
            margin_box.operator("bdental.reproject_margin", text="Reproject Edited Points", icon="MOD_SHRINKWRAP")
            margin_box.operator("bdental.capture_edited_margin", text="Capture Edited Candidate", icon="CHECKMARK")
        elif restoration.margin_candidate_closed:
            margin_box.operator("bdental.apply_margin_candidate", text="Apply Margin Candidate", icon="CHECKMARK")
        else:
            _draw_wrapped_label(margin_box, "LMB adds points, Backspace removes, Enter closes, Esc cancels.")
        row = margin_box.row(align=True)
        row.operator("bdental.reset_margin_session", text="Reset", icon="LOOP_BACK")
        row.operator("bdental.cancel_margin_session", text="Cancel", icon="CANCEL")
    elif margin is None:
        draw_row = margin_box.row()
        draw_row.operator_context = "INVOKE_REGION_WIN"
        draw_row.operator("bdental.draw_margin", text="Draw Manual Margin", icon="GREASEPENCIL")
    else:
        point_count = len(margin.data.splines[0].points) if len(margin.data.splines) == 1 else 0
        margin_box.label(text=f"{point_count} curve points")
        row = margin_box.row(align=True)
        row.operator("bdental.focus_margin", text="Focus", icon="VIEWZOOM")
        row.operator(
            "bdental.toggle_margin_visibility",
            text="Show" if margin.hide_viewport else "Hide",
            icon="HIDE_ON" if margin.hide_viewport else "HIDE_OFF",
        )
        redraw = margin_box.row()
        redraw.operator_context = "INVOKE_REGION_WIN"
        redraw.operator("bdental.draw_margin", text="Redraw Margin", icon="GREASEPENCIL")
        margin_box.operator("bdental.prepare_margin_edit", text="Edit Margin Points", icon="EDITMODE_HLT")
        margin_box.operator("bdental.reproject_margin", text="Reproject Margin Points", icon="MOD_SHRINKWRAP")
        margin_box.operator("bdental.validate_margin", text="Run Margin Validation", icon="FILE_TICK")

    _draw_messages(layout, restoration.errors, title="Blocking Errors", icon="ERROR")
    _draw_messages(layout, restoration.warnings, title="Warnings", icon="INFO")
    if restoration.summary:
        _draw_wrapped_label(layout.box(), restoration.summary)
    _draw_restoration_diagnostics(layout, restoration)

    if restoration.status == "CANDIDATE" and not restoration.margin_session_active and margin is not None:
        approval = layout.box()
        approval.label(text=f"Approve FDI {restoration.target_tooth_fdi}")
        approval.prop(restoration, "review_confirmed")
        if restoration.warnings:
            approval.prop(restoration, "warning_acknowledged")
        approval.operator("bdental.approve_margin", text="Approve Manual Margin", icon="CHECKMARK")


def _draw_step_three(layout, state, context) -> None:
    header = layout.box()
    header.label(text="Steps 1 and 2 Complete", icon="CHECKMARK")
    header.label(text="Step 3 of 3")
    header.label(text="Multiple Restorations & Manual Margins")
    header.label(text=f"Status: {state.step_3_status.replace('_', ' ').title()}")
    if state.restorations:
        approved = sum(1 for item in state.restorations if item.valid)
        header.label(text=f"Approved: {approved} of {len(state.restorations)}")

    _draw_restoration_list(layout, state)
    _draw_add_restoration(layout, state)
    _draw_active_restoration(layout, state, context)

    if state.step_3_valid:
        complete = layout.box()
        complete.label(text="All Restorations Approved", icon="CHECKMARK")
        _draw_wrapped_label(complete, "Step 3 is complete because every configured restoration has an approved margin.")
    layout.operator("bdental.back_to_step_two", text="Back to Step 2", icon="BACK")


class BDENTAL_PT_workflow(bpy.types.Panel):
    bl_idname = "BDENTAL_PT_workflow"
    bl_label = "B-Dental"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "B-Dental"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        state = context.scene.bdental_workflow
        if state.current_step == "STEP_3" and state.step_1_valid and state.step_2_valid:
            _draw_step_three(layout, state, context)
        elif state.current_step == "STEP_2" and state.step_1_valid:
            _draw_step_two(layout, state)
        else:
            _draw_step_one(layout, state)


CLASSES = (BDENTAL_PT_workflow,)
