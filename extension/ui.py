"""Workflow-aware 3D Viewport sidebar interface for B-Dental."""

import textwrap

import bpy

from . import properties, scene_utils

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
        box.label(
            text=f"{len(obj.data.vertices):,} vertices | {len(obj.data.polygons):,} faces"
        )
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
    header.label(text="Step 1 of 2", icon="IMPORT")
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
    ready = all(
        scene_utils.get_role_object(state, role) is not None for role in required
    )
    if state.step_1_status == "VALID" and state.step_1_valid:
        validation_box.label(text="Step 1 passed validation", icon="CHECKMARK")
    elif ready:
        validation_box.label(text="Ready to validate", icon="INFO")
    else:
        validation_box.label(text="Import all required scans", icon="ERROR")
    if state.validation_summary:
        _draw_wrapped_label(validation_box, state.validation_summary)
    _draw_messages(
        layout,
        state.validation_errors,
        title="Blocking Errors",
        icon="ERROR",
    )
    _draw_messages(
        layout,
        state.validation_warnings,
        title="Warnings",
        icon="INFO",
    )
    layout.operator(
        "bdental.validate_step_one",
        text="Validate & Continue",
        icon="FILE_TICK",
    )


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
    box.label(
        text=f"Median: {state.registration_median_distance * 1000.0:.3f} mm"
    )
    box.label(
        text=f"Translation: {state.registration_translation_delta * 1000.0:.3f} mm"
    )
    box.label(text=f"Rotation: {state.registration_rotation_delta:.4f} rad")
    if (
        state.bilateral_translation_disagreement > 0.0
        or state.bilateral_rotation_disagreement > 0.0
    ):
        box.label(
            text=(
                f"Bilateral delta: "
                f"{state.bilateral_translation_disagreement * 1000.0:.3f} mm"
            )
        )
        box.label(
            text=f"Bilateral rotation: {state.bilateral_rotation_disagreement:.4f} rad"
        )
    _draw_wrapped_label(
        box,
        "Metrics are engineering aids and do not prove clinical correctness.",
        icon="INFO",
    )


def _draw_step_two(layout, state) -> None:
    header = layout.box()
    header.label(text="Step 1 Complete", icon="CHECKMARK")
    header.label(text="Step 2 of 2")
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
        else:
            layout.operator(
                "bdental.complete_step_two_na",
                text="Complete as Not Applicable",
                icon="CHECKMARK",
            )
        layout.operator(
            "bdental.back_to_step_one_safe",
            text="Back to Step 1",
            icon="BACK",
        )
        return

    if state.step_2_status == "VERIFIED" and state.step_2_valid:
        complete = layout.box()
        complete.label(text="Step 2 Verified", icon="CHECKMARK")
        _draw_wrapped_label(
            complete,
            state.step_2_summary or "Occlusal relationship approved.",
        )
        if state.verification_method:
            complete.label(
                text=f"Method: {state.verification_method.replace('_', ' ').title()}"
            )
        _draw_metrics(layout, state)
        _draw_step_two_objects(layout, state)
        layout.operator(
            "bdental.back_to_step_one_safe",
            text="Back to Step 1",
            icon="BACK",
        )
        return

    analysis = layout.box()
    analysis.label(text="Imported Relationship")
    _draw_wrapped_label(
        analysis,
        "Entering Step 2 does not move scans. Analyze the imported relationship before deciding whether alignment is needed.",
    )
    analysis.operator(
        "bdental.analyze_step_two",
        text="Analyze Imported Relationship",
        icon="VIEWZOOM",
    )

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
            layout.operator(
                "bdental.start_step_two_session",
                text="Start Alignment Session",
                icon="PLAY",
            )
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
        controls.operator(
            "bdental.reset_step_two_preview",
            text="Reset",
            icon="LOOP_BACK",
        )
        controls.operator(
            "bdental.cancel_step_two_session",
            text="Cancel",
            icon="CANCEL",
        )
        if state.step_2_status == "CANDIDATE":
            session.operator(
                "bdental.apply_step_two_candidate",
                text="Apply Candidate",
                icon="CHECKMARK",
            )

    if (
        state.step_2_status in {"CANDIDATE", "IMPORTED_CANDIDATE"}
        or state.candidate_applied
    ):
        layout.operator(
            "bdental.verify_step_two",
            text="Run Verification Checks",
            icon="FILE_TICK",
        )

    _draw_messages(
        layout,
        state.step_2_errors,
        title="Blocking Errors",
        icon="ERROR",
    )
    _draw_messages(
        layout,
        state.step_2_warnings,
        title="Warnings",
        icon="INFO",
    )
    if state.step_2_summary:
        summary = layout.box()
        _draw_wrapped_label(summary, state.step_2_summary)
    _draw_metrics(layout, state)

    if (
        state.step_2_status in {"CANDIDATE", "IMPORTED_CANDIDATE"}
        and not state.alignment_session_active
    ):
        approval = layout.box()
        approval.label(text="Approval")
        approval.prop(state, "review_confirmed")
        if state.step_2_warnings:
            approval.prop(state, "warning_acknowledged")
        approval.operator(
            "bdental.approve_step_two",
            text="Approve Occlusion",
            icon="CHECKMARK",
        )

    _draw_step_two_objects(layout, state)
    layout.operator(
        "bdental.back_to_step_one_safe",
        text="Back to Step 1",
        icon="BACK",
    )


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
        if state.current_step == "STEP_2" and state.step_1_valid:
            _draw_step_two(layout, state)
        else:
            _draw_step_one(layout, state)


CLASSES = (BDENTAL_PT_workflow,)
