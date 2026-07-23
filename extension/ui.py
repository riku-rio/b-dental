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


def _draw_scan_slot(layout, state, role: str, required: bool = True) -> None:
    box = layout.box()
    header = box.row(align=True)
    header.label(text=properties.role_label(role), icon="MESH_DATA")
    header.label(text="Required" if required else "Reference")
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
        box.label(
            text=(
                f"{dimensions_mm[0]:.1f} x {dimensions_mm[1]:.1f} x "
                f"{dimensions_mm[2]:.1f} mm"
            )
        )

    actions = box.row(align=True)
    focus = actions.operator("bdental.focus_scan", text="Focus", icon="VIEWZOOM")
    focus.role = role
    replace = actions.operator("bdental.import_scan", text="Replace", icon="FILE_REFRESH")
    replace.role = role
    replace.replace_existing = True
    remove = actions.operator("bdental.remove_scan", text="Remove", icon="TRASH")
    remove.role = role
    visibility = box.operator(
        "bdental.toggle_scan_visibility",
        text="Show" if obj.hide_viewport else "Hide",
        icon="HIDE_ON" if obj.hide_viewport else "HIDE_OFF",
    )
    visibility.role = role


def _draw_step_one(layout, state) -> None:
    header = layout.box()
    header.label(text="Step 1 of 3", icon="IMPORT")
    header.label(text="Import Intra-Oral Scans")

    if state.case_initialized:
        layout.operator("bdental.start_case", text="Reset Dental Case", icon="FILE_REFRESH")
    else:
        layout.operator("bdental.start_case", text="Start New Dental Case", icon="FILE_NEW")
        info = layout.box()
        _draw_wrapped_label(
            info,
            "Start a new dental case before importing scans. Enabling B-Dental does not modify the scene.",
            icon="INFO",
        )
        return

    settings = layout.box()
    settings.label(text="Scan Configuration")
    settings.prop(state, "scan_configuration", text="")
    if state.scan_configuration == "SINGLE_ARCH":
        settings.prop(state, "single_arch_role")
    settings.prop(state, "source_unit")

    layout.label(text="Required Scans")
    required = properties.required_roles(state)
    for role in required:
        _draw_scan_slot(layout, state, role)

    validation_box = layout.box()
    validation_box.label(text="Validation")
    ready = all(scene_utils.get_role_object(state, role) is not None for role in required)
    if state.step_1_status == "VALID" and state.step_1_valid:
        validation_box.label(text="Step 1 passed validation", icon="CHECKMARK")
    elif ready:
        validation_box.label(text="Ready to validate", icon="INFO")
    else:
        validation_box.label(text="Import all required scans", icon="ERROR")
    if state.validation_summary:
        _draw_wrapped_label(validation_box, state.validation_summary)
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
    box.label(text=f"Translation: {state.registration_translation_delta * 1000.0:.3f} mm")
    box.label(text=f"Rotation: {state.registration_rotation_delta:.4f} rad")
    if state.bilateral_translation_disagreement > 0.0 or state.bilateral_rotation_disagreement > 0.0:
        box.label(
            text=f"Bilateral delta: {state.bilateral_translation_disagreement * 1000.0:.3f} mm"
        )
        box.label(text=f"Bilateral rotation: {state.bilateral_rotation_disagreement:.4f} rad")
    _draw_wrapped_label(
        box,
        "Metrics are engineering aids and do not prove clinical correctness.",
        icon="INFO",
    )


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
        _draw_wrapped_label(
            info,
            "Occlusion registration is not applicable because this case contains only one arch.",
            icon="INFO",
        )
        if state.step_2_valid:
            info.label(text="Step 2 Complete", icon="CHECKMARK")
            _draw_step_two_completion(layout, state)
        else:
            layout.operator(
                "bdental.complete_step_two_na",
                text="Complete as Not Applicable",
                icon="CHECKMARK",
            )
            layout.operator("bdental.back_to_step_one_safe", text="Back to Step 1", icon="BACK")
        return

    if state.step_2_status == "VERIFIED" and state.step_2_valid:
        complete = layout.box()
        complete.label(text="Step 2 Verified", icon="CHECKMARK")
        _draw_wrapped_label(complete, state.step_2_summary or "Occlusal relationship approved.")
        if state.verification_method:
            complete.label(text=f"Method: {state.verification_method.replace('_', ' ').title()}")
        _draw_metrics(layout, state)
        _draw_step_two_completion(layout, state)
        return

    analysis = layout.box()
    analysis.label(text="Imported Relationship")
    _draw_wrapped_label(
        analysis,
        "Entering Step 2 does not move scans. Analyze the imported relationship before deciding whether alignment is needed.",
    )
    analysis.operator("bdental.analyze_step_two", text="Analyze Imported Relationship", icon="VIEWZOOM")

    settings = layout.box()
    settings.label(text="Alignment Path")
    settings.prop(state, "alignment_mode", text="")
    if state.alignment_mode == "IMPORTED":
        _draw_wrapped_label(
            settings,
            "Imported mode preserves the scanner-exported relationship. Analyze it, run verification checks, and approve it without starting an alignment session.",
            icon="INFO",
        )
    elif state.alignment_mode == "BITE_GUIDED":
        settings.prop(state, "bite_source", text="")
        if state.scan_configuration != "FULL_SCAN_SET":
            _draw_wrapped_label(
                settings,
                "Bite-guided mode requires imported bite references.",
                icon="INFO",
            )

    if not state.alignment_session_active:
        if state.alignment_mode in {"MANUAL", "BITE_GUIDED"}:
            layout.operator("bdental.start_step_two_session", text="Start Alignment Session", icon="PLAY")
    else:
        session = layout.box()
        session.label(text="Alignment Session Active", icon="REC")
        _draw_wrapped_label(
            session,
            "Upper Jaw is fixed. Preview changes remain reversible until Apply Candidate.",
        )
        if state.alignment_mode == "MANUAL":
            _draw_wrapped_label(
                session,
                "Use Blender Move and Rotate tools on Lower Jaw, then capture the candidate.",
            )
            session.operator(
                "bdental.capture_manual_step_two",
                text="Capture Manual Candidate",
                icon="CHECKMARK",
            )
        elif state.alignment_mode == "BITE_GUIDED":
            session.operator(
                "bdental.run_bite_step_two",
                text="Run Bite-Guided Registration",
                icon="MODIFIER",
            )
        controls = session.row(align=True)
        controls.operator("bdental.reset_step_two_preview", text="Reset", icon="LOOP_BACK")
        controls.operator("bdental.cancel_step_two_session", text="Cancel", icon="CANCEL")
        if state.step_2_status == "CANDIDATE":
            session.operator("bdental.apply_step_two_candidate", text="Apply Candidate", icon="CHECKMARK")

    if state.step_2_status in {"CANDIDATE", "IMPORTED_CANDIDATE"} or state.candidate_applied:
        layout.operator("bdental.verify_step_two", text="Run Verification Checks", icon="FILE_TICK")

    _draw_messages(layout, state.step_2_errors, title="Blocking Errors", icon="ERROR")
    _draw_messages(layout, state.step_2_warnings, title="Warnings", icon="INFO")
    if state.step_2_summary:
        summary = layout.box()
        _draw_wrapped_label(summary, state.step_2_summary)
    _draw_metrics(layout, state)

    if state.step_2_status in {"CANDIDATE", "IMPORTED_CANDIDATE"} and not state.alignment_session_active:
        approval = layout.box()
        approval.label(text="Approval")
        approval.prop(state, "review_confirmed")
        if state.step_2_warnings:
            approval.prop(state, "warning_acknowledged")
        approval.operator("bdental.approve_step_two", text="Approve Occlusion", icon="CHECKMARK")

    _draw_step_two_objects(layout, state)
    layout.operator("bdental.back_to_step_one_safe", text="Back to Step 1", icon="BACK")


def _draw_margin_diagnostics(layout, state) -> None:
    if state.margin_point_count <= 0:
        return
    box = layout.box()
    box.label(text="Margin Diagnostics", icon="DRIVER_DISTANCE")
    box.label(text=f"Points: {state.margin_point_count}")
    box.label(text=f"Path length: {state.margin_path_length * 1000.0:.3f} mm")
    box.label(text=f"Mean surface distance: {state.margin_mean_surface_distance * 1000.0:.3f} mm")
    box.label(text=f"Max surface distance: {state.margin_max_surface_distance * 1000.0:.3f} mm")
    _draw_wrapped_label(
        box,
        "Diagnostics are engineering aids and do not identify a clinically correct margin.",
        icon="INFO",
    )


def _draw_step_three(layout, state, context) -> None:
    header = layout.box()
    header.label(text="Steps 1 and 2 Complete", icon="CHECKMARK")
    header.label(text="Step 3 of 3")
    header.label(text="Restoration Setup & Manual Margin")
    header.label(text=f"Status: {state.step_3_status.replace('_', ' ').title()}")

    setup = layout.box()
    setup.label(text="Restoration Setup", icon="MESH_DATA")
    setup.label(text="Type: Anatomical Crown")
    margin = restoration_utils.resolve_margin(state)
    controls = setup.column()
    controls.enabled = margin is None and not state.margin_session_active
    if state.scan_configuration == "SINGLE_ARCH":
        controls.label(text=f"Preparation Arch: {properties.role_label(state.target_arch)}")
    else:
        controls.prop(state, "target_arch")
    controls.prop(state, "target_tooth_fdi")
    if not state.restoration_id:
        setup.operator("bdental.create_restoration", text="Confirm Restoration Setup", icon="CHECKMARK")
    else:
        setup.label(text=f"Target: FDI {state.target_tooth_fdi}", icon="CHECKMARK")
        setup.operator("bdental.reset_restoration_setup", text="Reset Restoration Setup", icon="FILE_REFRESH")

    target = restoration_utils.target_scan(state)
    target_box = layout.box()
    target_box.label(text="Target Preparation Scan", icon="MESH_DATA")
    if target is None:
        target_box.label(text="Target scan unavailable", icon="ERROR")
    else:
        target_box.label(text=properties.role_label(state.target_arch))
        _draw_wrapped_label(target_box, _object_summary(target))
        target_box.operator("bdental.focus_step_three_target", text="Focus Preparation Scan", icon="VIEWZOOM")

    if not state.restoration_id:
        if state.step_3_summary:
            summary = layout.box()
            _draw_wrapped_label(summary, state.step_3_summary)
        layout.operator("bdental.back_to_step_two", text="Back to Step 2", icon="BACK")
        return

    margin_box = layout.box()
    margin_box.label(text="Manual Margin", icon="CURVE_DATA")
    if state.margin_session_active:
        margin_box.label(text="Reversible session active", icon="REC")
        if context.object is not None and context.object.mode == "EDIT":
            _draw_wrapped_label(
                margin_box,
                "Move, add, or delete curve points. Return to Object Mode by capturing or reprojecting the candidate.",
            )
            margin_box.operator("bdental.reproject_margin", text="Reproject Edited Points", icon="MOD_SHRINKWRAP")
            margin_box.operator("bdental.capture_edited_margin", text="Capture Edited Candidate", icon="CHECKMARK")
        elif state.margin_candidate_closed:
            _draw_wrapped_label(
                margin_box,
                "The closed candidate is still reversible until Apply Margin Candidate.",
            )
            margin_box.operator("bdental.apply_margin_candidate", text="Apply Margin Candidate", icon="CHECKMARK")
        else:
            _draw_wrapped_label(
                margin_box,
                "Drawing is active in the 3D Viewport. LMB adds points, Backspace removes the last point, Enter closes, and Esc cancels.",
            )
        row = margin_box.row(align=True)
        row.operator("bdental.reset_margin_session", text="Reset", icon="LOOP_BACK")
        row.operator("bdental.cancel_margin_session", text="Cancel", icon="CANCEL")
    else:
        if margin is None:
            draw_row = margin_box.row()
            draw_row.operator_context = "INVOKE_REGION_WIN"
            draw_row.operator("bdental.draw_margin", text="Draw Manual Margin", icon="GREASEPENCIL")
        else:
            margin_box.label(text=f"{len(margin.data.splines[0].points) if len(margin.data.splines) == 1 else 0} curve points")
            row = margin_box.row(align=True)
            row.operator("bdental.focus_margin", text="Focus", icon="VIEWZOOM")
            row.operator(
                "bdental.toggle_margin_visibility",
                text="Show" if margin.hide_viewport else "Hide",
                icon="HIDE_ON" if margin.hide_viewport else "HIDE_OFF",
            )
            redraw_row = margin_box.row()
            redraw_row.operator_context = "INVOKE_REGION_WIN"
            redraw_row.operator("bdental.draw_margin", text="Redraw Margin", icon="GREASEPENCIL")
            margin_box.operator("bdental.prepare_margin_edit", text="Edit Margin Points", icon="EDITMODE_HLT")
            margin_box.operator("bdental.reproject_margin", text="Reproject Margin Points", icon="MOD_SHRINKWRAP")
            margin_box.operator("bdental.validate_margin", text="Run Margin Validation", icon="FILE_TICK")

    _draw_messages(layout, state.step_3_errors, title="Blocking Errors", icon="ERROR")
    _draw_messages(layout, state.step_3_warnings, title="Warnings", icon="INFO")
    if state.step_3_summary:
        summary = layout.box()
        _draw_wrapped_label(summary, state.step_3_summary)
    _draw_margin_diagnostics(layout, state)

    if state.step_3_status == "CANDIDATE" and not state.margin_session_active and margin is not None:
        approval = layout.box()
        approval.label(text="Margin Approval")
        approval.prop(state, "margin_review_confirmed")
        if state.step_3_warnings:
            approval.prop(state, "margin_warning_acknowledged")
        approval.operator("bdental.approve_margin", text="Approve Manual Margin", icon="CHECKMARK")

    if state.step_3_status == "VERIFIED" and state.step_3_valid:
        complete = layout.box()
        complete.label(text="Step 3 Verified", icon="CHECKMARK")
        _draw_wrapped_label(complete, state.step_3_summary)

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
