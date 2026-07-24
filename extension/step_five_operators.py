"""Step 5 operators and workflow UI integration."""

from __future__ import annotations

import bpy
from bpy.props import StringProperty

from . import (
    crown_bottom_candidates,
    properties,
    restoration_utils,
    step_five_session,
    step_five_validation,
    ui,
)


def _state(context):
    return context.scene.bdental_workflow


def _active(state):
    return restoration_utils.active_restoration(state)


def _messages(restoration, result) -> None:
    restoration.step_5_summary = result.summary
    restoration.step_5_errors = "\n".join(result.errors)
    restoration.step_5_warnings = "\n".join(result.warnings)
    restoration.step_5_review_confirmed = False
    restoration.step_5_warning_acknowledged = False


def _select(context, obj) -> None:
    for item in context.view_layer.objects:
        try:
            item.select_set(False)
        except (ReferenceError, RuntimeError):
            continue
    obj.hide_viewport = False
    obj.select_set(True)
    context.view_layer.objects.active = obj


def _focus(context, obj) -> None:
    if obj is None:
        return
    _select(context, obj)
    manager = context.window_manager
    if manager is None:
        return
    for window in manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next(
                (candidate for candidate in area.regions if candidate.type == "WINDOW"),
                None,
            )
            if region is None:
                continue
            try:
                with context.temp_override(
                    window=window,
                    screen=screen,
                    area=area,
                    region=region,
                    space_data=area.spaces.active,
                ):
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                return
            except (RuntimeError, TypeError):
                continue


class BDENTAL_OT_enter_step_five(bpy.types.Operator):
    bl_idname = "bdental.enter_step_five"
    bl_label = "Continue to Step 5"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and state.step_4_valid
            and not any(
                restoration.axis_session_active or restoration.margin_session_active
                for restoration in state.restorations
            )
        )

    def execute(self, context):
        state = _state(context)
        result = step_five_validation.validate_preconditions(state)
        state.step_5_summary = result.summary
        state.step_5_errors = "\n".join(result.errors)
        if not result.ok:
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}
        for restoration in state.restorations:
            if restoration.step_5_status == "UPSTREAM_INVALID":
                restoration.step_5_status = (
                    "GENERATED"
                    if restoration.step_5_generation_current
                    else "READY_TO_GENERATE"
                )
        state.current_step = "STEP_5"
        step_five_session.sync_step_five_state(state)
        return {"FINISHED"}


class BDENTAL_OT_generate_step_five(bpy.types.Operator):
    bl_idname = "bdental.generate_step_five"
    bl_label = "Generate Die & Crown Bottom"
    bl_options = {"REGISTER"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        errors, warnings = step_five_validation.validate_settings(restoration)
        if errors:
            restoration.step_5_status = "ERROR"
            restoration.step_5_errors = "\n".join(errors)
            self.report({"ERROR"}, errors[0])
            return {"CANCELLED"}
        if restoration.step_5_correction_active:
            self.report(
                {"ERROR"},
                "Apply or cancel correction before regeneration.",
            )
            return {"CANCELLED"}

        restoration.step_5_status = "GENERATING"
        restoration.step_5_errors = ""
        step_five_session.sync_step_five_state(state)
        try:
            result = crown_bottom_candidates.generate(
                context.scene,
                state,
                restoration,
                context.evaluated_depsgraph_get(),
            )
        except (ValueError, RuntimeError, TimeoutError) as exc:
            restoration.step_5_status = "ERROR"
            restoration.step_5_errors = str(exc)
            restoration.step_5_summary = (
                "Step 5 generation failed without changing upstream geometry."
            )
            step_five_session.sync_step_five_state(state)
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        step_five_session.store_generation(restoration, result)
        restoration.step_5_warnings = "\n".join(
            dict.fromkeys((*warnings, *result.warnings))
        )
        step_five_session.sync_step_five_state(state)
        return {"FINISHED"}


class BDENTAL_OT_select_step_five_candidate(bpy.types.Operator):
    bl_idname = "bdental.select_step_five_candidate"
    bl_label = "Select Crown-Bottom Candidate"

    candidate_id: StringProperty(default="")

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        if restoration.step_5_correction_active:
            self.report(
                {"ERROR"},
                "Apply or cancel correction before switching candidates.",
            )
            return {"CANCELLED"}
        try:
            obj = crown_bottom_candidates.select_candidate(
                restoration,
                self.candidate_id,
            )
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        step_five_session.clear_step_five_approval(restoration)
        restoration.step_5_status = "GENERATED"
        restoration.step_5_summary = (
            "Candidate selection changed. Run validation again."
        )
        _focus(context, obj)
        step_five_session.sync_step_five_state(state)
        return {"FINISHED"}


class BDENTAL_OT_validate_step_five(bpy.types.Operator):
    bl_idname = "bdental.validate_step_five"
    bl_label = "Validate Step 5"
    bl_options = {"REGISTER"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        result = step_five_validation.validate_restoration(state, restoration)
        _messages(restoration, result)
        restoration.step_5_status = result.status
        restoration.step_5_valid = False
        step_five_session.sync_step_five_state(state)
        if not result.ok:
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_approve_step_five(bpy.types.Operator):
    bl_idname = "bdental.approve_step_five"
    bl_label = "Approve Crown Bottom"
    bl_options = {"REGISTER"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        result = step_five_validation.validate_restoration(state, restoration)
        if not result.ok:
            _messages(restoration, result)
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}
        if not restoration.step_5_review_confirmed:
            self.report({"ERROR"}, "Confirm visual review before approval.")
            return {"CANCELLED"}
        if result.warnings and not restoration.step_5_warning_acknowledged:
            restoration.step_5_warnings = "\n".join(result.warnings)
            self.report(
                {"ERROR"},
                "Acknowledge Step 5 warnings before approval.",
            )
            return {"CANCELLED"}
        try:
            crown_bottom_candidates.promote_selected_candidate(restoration)
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        step_five_session.snapshot_approved(state, restoration)
        restoration.step_5_status = "VERIFIED"
        restoration.step_5_valid = True
        restoration.step_5_errors = ""
        restoration.step_5_warnings = "\n".join(result.warnings)
        restoration.step_5_summary = (
            f"Crown-bottom candidate approved for FDI "
            f"{restoration.target_tooth_fdi}. Engineering checks do not "
            "certify clinical fit."
        )
        step_five_session.sync_step_five_state(state)
        return {"FINISHED"}


class BDENTAL_OT_start_step_five_correction(bpy.types.Operator):
    bl_idname = "bdental.start_step_five_correction"
    bl_label = "Start Constrained Correction"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            obj = step_five_session.start_correction(state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        _select(context, obj)
        return {"FINISHED"}


class BDENTAL_OT_capture_step_five_correction(bpy.types.Operator):
    bl_idname = "bdental.capture_step_five_correction"
    bl_label = "Capture Correction"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            step_five_session.capture_correction(state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_apply_step_five_correction(bpy.types.Operator):
    bl_idname = "bdental.apply_step_five_correction"
    bl_label = "Apply Correction"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            step_five_session.apply_correction(state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_reset_step_five_correction(bpy.types.Operator):
    bl_idname = "bdental.reset_step_five_correction"
    bl_label = "Reset Correction"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            step_five_session.reset_correction(state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_cancel_step_five_correction(bpy.types.Operator):
    bl_idname = "bdental.cancel_step_five_correction"
    bl_label = "Cancel Correction"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            step_five_session.cancel_correction(state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


def _artifact_resolver(artifact_type):
    return {
        "PREPARATION_DIE": crown_bottom_candidates.resolve_preparation_die,
        "BLOCKED_DIE": crown_bottom_candidates.resolve_blocked_die,
        "CROWN_BOTTOM": crown_bottom_candidates.resolve_selected_candidate,
    }.get(
        artifact_type,
        crown_bottom_candidates.resolve_selected_candidate,
    )


class BDENTAL_OT_focus_step_five_artifact(bpy.types.Operator):
    bl_idname = "bdental.focus_step_five_artifact"
    bl_label = "Focus Step 5 Artifact"

    artifact_type: StringProperty(default="CROWN_BOTTOM")

    def execute(self, context):
        restoration = _active(_state(context))
        obj = _artifact_resolver(self.artifact_type)(restoration)
        if obj is None:
            return {"CANCELLED"}
        _focus(context, obj)
        return {"FINISHED"}


class BDENTAL_OT_toggle_step_five_artifact(bpy.types.Operator):
    bl_idname = "bdental.toggle_step_five_artifact"
    bl_label = "Toggle Step 5 Artifact"

    artifact_type: StringProperty(default="CROWN_BOTTOM")

    def execute(self, context):
        restoration = _active(_state(context))
        obj = _artifact_resolver(self.artifact_type)(restoration)
        if obj is None:
            return {"CANCELLED"}
        obj.hide_viewport = not obj.hide_viewport
        return {"FINISHED"}


class BDENTAL_OT_back_to_step_four(bpy.types.Operator):
    bl_idname = "bdental.back_to_step_four"
    bl_label = "Back to Step 4"

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        if restoration and restoration.step_5_correction_active:
            self.report(
                {"ERROR"},
                "Apply or cancel correction before leaving Step 5.",
            )
            return {"CANCELLED"}
        state.current_step = "STEP_4"
        return {"FINISHED"}


def _artifact_row(box, restoration, label, artifact_type, resolver) -> None:
    obj = resolver(restoration)
    row = box.row(align=True)
    row.label(text=label, icon="MESH_DATA")
    if obj is None:
        row.label(text="Missing", icon="ERROR")
        return
    focus = row.operator(
        "bdental.focus_step_five_artifact",
        text="",
        icon="VIEWZOOM",
    )
    focus.artifact_type = artifact_type
    toggle = row.operator(
        "bdental.toggle_step_five_artifact",
        text="",
        icon="HIDE_ON" if obj.hide_viewport else "HIDE_OFF",
    )
    toggle.artifact_type = artifact_type


def _draw_step_five(layout, state, context) -> None:
    header = layout.box()
    header.label(text="Steps 1-4 Complete", icon="CHECKMARK")
    header.label(text="Step 5 of 5")
    header.label(text="Automated Preparation Die & Crown Bottom")
    header.label(text=f"Status: {state.step_5_status.replace('_', ' ').title()}")

    restoration = _active(state)
    if restoration is None:
        return

    identity = layout.box()
    identity.label(
        text=f"Active: FDI {restoration.target_tooth_fdi}",
        icon="MESH_DATA",
    )
    identity.label(
        text=f"Preparation: {properties.role_label(restoration.target_arch)}"
    )

    settings = layout.box()
    settings.label(text="Generation Settings", icon="PREFERENCES")
    for name in (
        "step_5_marginal_gap",
        "step_5_cement_gap",
        "step_5_spacer_start",
        "step_5_axial_relief",
        "step_5_occlusal_relief",
        "step_5_seal_band_width",
        "step_5_blockout_clearance",
        "step_5_sampling_resolution",
        "step_5_smoothing_strength",
        "step_5_maximum_candidates",
        "step_5_maximum_iterations",
        "step_5_maximum_runtime",
    ):
        settings.prop(restoration, name)
    settings.operator(
        "bdental.generate_step_five",
        text="Generate Die & Crown Bottom",
        icon="MODIFIER",
    )

    artifacts = layout.box()
    artifacts.label(text="Managed Geometry")
    _artifact_row(
        artifacts,
        restoration,
        "Preparation Die",
        "PREPARATION_DIE",
        crown_bottom_candidates.resolve_preparation_die,
    )
    _artifact_row(
        artifacts,
        restoration,
        "Blocked Die",
        "BLOCKED_DIE",
        crown_bottom_candidates.resolve_blocked_die,
    )
    _artifact_row(
        artifacts,
        restoration,
        "Crown Bottom",
        "CROWN_BOTTOM",
        crown_bottom_candidates.resolve_selected_candidate,
    )

    records = crown_bottom_candidates.candidate_records(restoration)
    if records:
        candidates = layout.box()
        candidates.label(text="Candidates", icon="OUTLINER_COLLECTION")
        for record in records:
            row = candidates.row(align=True)
            operator = row.operator(
                "bdental.select_step_five_candidate",
                text=f"#{record.rank or '-'} {record.score:.1f}",
                icon="CHECKMARK" if record.accepted else "ERROR",
                depress=record.candidate_id == restoration.selected_candidate_id,
            )
            operator.candidate_id = record.candidate_id
            row.enabled = record.accepted
        candidates.label(
            text=(
                f"Runtime: {restoration.step_5_generation_duration:.3f} s | "
                f"Iterations: {restoration.step_5_generation_iterations}"
            )
        )

    if restoration.step_5_correction_active:
        correction = layout.box()
        correction.label(text="Constrained Correction Active", icon="REC")
        correction.prop(restoration, "step_5_correction_limit")
        correction.operator(
            "bdental.capture_step_five_correction",
            text="Capture",
            icon="CHECKMARK",
        )
        correction.operator(
            "bdental.apply_step_five_correction",
            text="Apply",
            icon="FILE_TICK",
        )
        row = correction.row(align=True)
        row.operator(
            "bdental.reset_step_five_correction",
            text="Reset",
            icon="LOOP_BACK",
        )
        row.operator(
            "bdental.cancel_step_five_correction",
            text="Cancel",
            icon="CANCEL",
        )
    elif restoration.step_5_generation_current:
        layout.operator(
            "bdental.start_step_five_correction",
            text="Start Constrained Correction",
            icon="EDITMODE_HLT",
        )

    if restoration.step_5_generation_current:
        layout.operator(
            "bdental.validate_step_five",
            text="Validate Step 5",
            icon="FILE_TICK",
        )

    ui._draw_messages(
        layout,
        restoration.step_5_errors,
        title="Blocking Errors",
        icon="ERROR",
    )
    ui._draw_messages(
        layout,
        restoration.step_5_warnings,
        title="Engineering Warnings",
        icon="INFO",
    )
    if restoration.step_5_summary:
        ui._draw_wrapped_label(layout.box(), restoration.step_5_summary)

    if (
        restoration.step_5_generation_current
        and not restoration.step_5_correction_active
    ):
        approval = layout.box()
        approval.prop(restoration, "step_5_review_confirmed")
        approval.prop(restoration, "step_5_warning_acknowledged")
        approval.operator(
            "bdental.approve_step_five",
            text="Approve Crown Bottom",
            icon="CHECKMARK",
        )

    layout.operator(
        "bdental.back_to_step_four",
        text="Back to Step 4",
        icon="BACK",
    )


def _patch_ui() -> None:
    panel = ui.BDENTAL_PT_workflow
    if not hasattr(panel, "_bdental_step_five_original_draw"):
        previous_panel_draw = panel.draw
        panel._bdental_step_five_original_draw = previous_panel_draw

        def draw(self, context):
            state = context.scene.bdental_workflow
            if state.current_step == "STEP_5":
                layout = self.layout
                layout.operator_context = "INVOKE_DEFAULT"
                _draw_step_five(layout, state, context)
            else:
                previous_panel_draw(self, context)

        panel.draw = draw

    from . import step_four_operators

    if not hasattr(
        step_four_operators,
        "_bdental_step_five_original_draw_step_four",
    ):
        previous_step_four_draw = step_four_operators._draw_step_four
        step_four_operators._bdental_step_five_original_draw_step_four = (
            previous_step_four_draw
        )

        def draw_step_four(layout, state, context):
            previous_step_four_draw(layout, state, context)
            if state.step_4_valid:
                layout.operator(
                    "bdental.enter_step_five",
                    text="Continue to Step 5",
                    icon="FORWARD",
                )

        step_four_operators._draw_step_four = draw_step_four


CLASSES = (
    BDENTAL_OT_enter_step_five,
    BDENTAL_OT_generate_step_five,
    BDENTAL_OT_select_step_five_candidate,
    BDENTAL_OT_validate_step_five,
    BDENTAL_OT_approve_step_five,
    BDENTAL_OT_start_step_five_correction,
    BDENTAL_OT_capture_step_five_correction,
    BDENTAL_OT_apply_step_five_correction,
    BDENTAL_OT_reset_step_five_correction,
    BDENTAL_OT_cancel_step_five_correction,
    BDENTAL_OT_focus_step_five_artifact,
    BDENTAL_OT_toggle_step_five_artifact,
    BDENTAL_OT_back_to_step_four,
)

_patch_ui()
