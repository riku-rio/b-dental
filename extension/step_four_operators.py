"""Step 4 operators and workflow UI integration."""

from __future__ import annotations

import bpy
from bpy.props import IntProperty

from . import (
    axis_geometry,
    preparation_analysis,
    properties,
    restoration_utils,
    step_four_session,
    step_four_validation,
    step_three_operators,
    ui,
)


def _state(context):
    return context.scene.bdental_workflow


def _active(state):
    return restoration_utils.active_restoration(state)


def _store_messages(restoration, result) -> None:
    restoration.step_4_summary = result.summary
    restoration.step_4_errors = "\n".join(result.errors)
    restoration.step_4_warnings = "\n".join(result.warnings)
    restoration.step_4_review_confirmed = False
    restoration.step_4_warning_acknowledged = False


def _select_only(context, target) -> None:
    for obj in context.view_layer.objects:
        try:
            obj.select_set(False)
        except (ReferenceError, RuntimeError):
            continue
    target.hide_viewport = False
    try:
        target.hide_set(False)
    except (AttributeError, RuntimeError):
        pass
    target.select_set(True)
    context.view_layer.objects.active = target


def _frame_selected(context) -> bool:
    manager = context.window_manager
    if manager is None:
        return False
    for window in manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((item for item in area.regions if item.type == "WINDOW"), None)
            if region is None:
                continue
            try:
                with context.temp_override(window=window, screen=screen, area=area, region=region, space_data=area.spaces.active):
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                return True
            except (RuntimeError, TypeError):
                continue
    return False


def _set_axis_candidate(context, axis_local, source: str) -> None:
    state = _state(context)
    restoration = _active(state)
    serialized = axis_geometry.serialize_vector(axis_local)
    if not serialized:
        raise ValueError("The insertion-axis candidate is invalid.")
    restoration.insertion_axis_local = serialized
    restoration.axis_source = source
    step_four_session.clear_step_four_analysis(restoration)
    restoration.step_4_status = "AXIS_CANDIDATE"
    restoration.step_4_summary = "Insertion-axis candidate created. Review it and run undercut analysis."
    restoration.step_4_errors = ""
    restoration.step_4_warnings = ""
    axis_geometry.ensure_axis_object(context.scene, state, restoration, context.evaluated_depsgraph_get())
    step_four_session.sync_step_four_state(state)


class BDENTAL_OT_enter_step_four(bpy.types.Operator):
    bl_idname = "bdental.enter_step_four"
    bl_label = "Continue to Step 4"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(state and state.step_3_valid and not any(item.margin_session_active for item in state.restorations))

    def execute(self, context):
        state = _state(context)
        result = step_four_validation.validate_step_four_preconditions(state)
        state.step_4_summary = result.summary
        state.step_4_errors = "\n".join(result.errors)
        if not result.ok:
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}
        for restoration in state.restorations:
            if restoration.step_4_status == "UPSTREAM_INVALID":
                restoration.step_4_status = "AXIS_CANDIDATE" if restoration.insertion_axis_local else "READY_FOR_AXIS"
            if not restoration.insertion_axis_local and restoration.analysis_radius == preparation_analysis.DEFAULT_ANALYSIS_RADIUS:
                state.internal_update_lock = True
                try:
                    restoration.analysis_radius = preparation_analysis.default_radius(restoration)
                finally:
                    state.internal_update_lock = False
        state.current_step = "STEP_4"
        step_four_session.sync_step_four_state(state)
        return {"FINISHED"}


class BDENTAL_OT_select_step_four_restoration(bpy.types.Operator):
    bl_idname = "bdental.select_step_four_restoration"
    bl_label = "Select Step 4 Restoration"
    index: IntProperty(default=0, min=0)

    def execute(self, context):
        state = _state(context)
        active = _active(state)
        if active is not None and active.axis_session_active:
            self.report({"ERROR"}, "Apply or cancel the active axis session before switching.")
            return {"CANCELLED"}
        if self.index >= len(state.restorations):
            return {"CANCELLED"}
        state.active_restoration_index = self.index
        step_four_session.sync_step_four_state(state)
        return {"FINISHED"}


class BDENTAL_OT_axis_from_view(bpy.types.Operator):
    bl_idname = "bdental.axis_from_view"
    bl_label = "Set From Current View"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.area is None or context.area.type != "VIEW_3D" or context.region_data is None:
            self.report({"ERROR"}, "Use Set From Current View inside a 3D Viewport.")
            return {"CANCELLED"}
        state = _state(context)
        restoration = _active(state)
        target = restoration_utils.target_scan(state, restoration)
        forward = axis_geometry.current_view_forward_world(context)
        axis = axis_geometry.world_to_target_local_direction(target, forward) if target else None
        try:
            _set_axis_candidate(context, axis, "CURRENT_VIEW")
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_axis_from_margin(bpy.types.Operator):
    bl_idname = "bdental.axis_from_margin"
    bl_label = "Suggest From Margin"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.region_data is None:
            self.report({"ERROR"}, "Use the margin suggestion inside a 3D Viewport.")
            return {"CANCELLED"}
        state = _state(context)
        restoration = _active(state)
        forward = axis_geometry.current_view_forward_world(context)
        axis = axis_geometry.margin_axis_suggestion(state, restoration, forward)
        try:
            _set_axis_candidate(context, axis, "MARGIN_SUGGESTION")
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        restoration.step_4_summary = "Margin-normal suggestion created. It is an engineering starting point, not an automatic clinical decision."
        return {"FINISHED"}


class BDENTAL_OT_start_axis_session(bpy.types.Operator):
    bl_idname = "bdental.start_axis_session"
    bl_label = "Start Axis Edit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        try:
            obj = step_four_session.start_session(context.scene, state, restoration)
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        _select_only(context, obj)
        return {"FINISHED"}


class BDENTAL_OT_capture_axis_candidate(bpy.types.Operator):
    bl_idname = "bdental.capture_axis_candidate"
    bl_label = "Capture Axis Candidate"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            step_four_session.capture_candidate(state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_apply_axis_candidate(bpy.types.Operator):
    bl_idname = "bdental.apply_axis_candidate"
    bl_label = "Apply Axis Candidate"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            step_four_session.apply_candidate(state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_reset_axis_session(bpy.types.Operator):
    bl_idname = "bdental.reset_axis_session"
    bl_label = "Reset Axis Session"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            step_four_session.reset_session(context.scene, state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_cancel_axis_session(bpy.types.Operator):
    bl_idname = "bdental.cancel_axis_session"
    bl_label = "Cancel Axis Session"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        try:
            step_four_session.cancel_session(context.scene, state, _active(state))
        except ValueError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_focus_axis(bpy.types.Operator):
    bl_idname = "bdental.focus_axis"
    bl_label = "Focus Insertion Axis"

    def execute(self, context):
        obj = axis_geometry.resolve_axis(_active(_state(context)))
        if obj is None:
            return {"CANCELLED"}
        _select_only(context, obj)
        _frame_selected(context)
        return {"FINISHED"}


class BDENTAL_OT_toggle_axis_visibility(bpy.types.Operator):
    bl_idname = "bdental.toggle_axis_visibility"
    bl_label = "Toggle Axis Visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = axis_geometry.resolve_axis(_active(_state(context)))
        if obj is None:
            return {"CANCELLED"}
        obj.hide_viewport = not obj.hide_viewport
        return {"FINISHED"}


class BDENTAL_OT_clear_axis(bpy.types.Operator):
    bl_idname = "bdental.clear_axis"
    bl_label = "Clear Insertion Axis"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        if restoration.axis_session_active:
            self.report({"ERROR"}, "Cancel the active axis session before clearing the axis.")
            return {"CANCELLED"}
        axis_geometry.remove_restoration_axis(restoration)
        restoration.insertion_axis_local = ""
        restoration.axis_source = "NONE"
        step_four_session.invalidate_restoration(restoration, preserve_axis=False)
        step_four_session.sync_step_four_state(state)
        return {"FINISHED"}


class BDENTAL_OT_run_undercut_analysis(bpy.types.Operator):
    bl_idname = "bdental.run_undercut_analysis"
    bl_label = "Run Undercut Analysis"
    bl_options = {"REGISTER"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        if restoration.axis_session_active:
            self.report({"ERROR"}, "Apply or cancel the axis session before analysis.")
            return {"CANCELLED"}
        try:
            axis_geometry.ensure_axis_object(context.scene, state, restoration, context.evaluated_depsgraph_get())
            result = preparation_analysis.run_analysis(state, restoration, context.evaluated_depsgraph_get())
            signature = step_four_validation.dependency_signature(state, restoration)
            preparation_analysis.store_result(restoration, result, signature)
        except (RuntimeError, ValueError) as exc:
            step_four_session.clear_step_four_analysis(restoration)
            restoration.step_4_status = "ERROR"
            restoration.step_4_errors = str(exc)
            restoration.step_4_summary = "Undercut analysis failed."
            step_four_session.sync_step_four_state(state)
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        restoration.step_4_status = "ANALYZED"
        restoration.step_4_valid = False
        restoration.step_4_review_confirmed = False
        restoration.step_4_warning_acknowledged = False
        restoration.step_4_errors = ""
        restoration.step_4_warnings = ""
        restoration.step_4_summary = f"Analyzed {result.analyzed_count} deterministic surface samples."
        step_four_session.sync_step_four_state(state)
        return {"FINISHED"}


class BDENTAL_OT_validate_step_four(bpy.types.Operator):
    bl_idname = "bdental.validate_step_four"
    bl_label = "Validate Step 4"
    bl_options = {"REGISTER"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        result = step_four_validation.validate_restoration(state, restoration)
        restoration.step_4_status = result.status
        restoration.step_4_valid = False
        _store_messages(restoration, result)
        step_four_session.sync_step_four_state(state)
        if not result.ok:
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_approve_step_four(bpy.types.Operator):
    bl_idname = "bdental.approve_step_four"
    bl_label = "Approve Preparation Analysis"
    bl_options = {"REGISTER"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        result = step_four_validation.validate_restoration(state, restoration)
        if not result.ok:
            _store_messages(restoration, result)
            step_four_session.sync_step_four_state(state)
            return {"CANCELLED"}
        if not restoration.step_4_review_confirmed:
            self.report({"ERROR"}, "Confirm visual review before approval.")
            return {"CANCELLED"}
        if result.warnings and not restoration.step_4_warning_acknowledged:
            _store_messages(restoration, result)
            self.report({"ERROR"}, "Acknowledge Step 4 warnings before approval.")
            return {"CANCELLED"}
        restoration.step_4_warnings = "\n".join(result.warnings)
        restoration.step_4_errors = ""
        step_four_session.snapshot_approved(state, restoration)
        restoration.step_4_status = "VERIFIED"
        restoration.step_4_valid = True
        restoration.step_4_summary = f"Preparation analysis approved for FDI {restoration.target_tooth_fdi}. Engineering checks do not certify clinical correctness."
        obj = axis_geometry.resolve_axis(restoration)
        if obj is not None:
            obj.color = axis_geometry.VERIFIED_COLOR
        step_four_session.sync_step_four_state(state)
        return {"FINISHED"}


class BDENTAL_OT_toggle_analysis_overlay(bpy.types.Operator):
    bl_idname = "bdental.toggle_analysis_overlay"
    bl_label = "Toggle Analysis Overlay"

    def execute(self, context):
        restoration = _active(_state(context))
        restoration.analysis_overlay_visible = not restoration.analysis_overlay_visible
        return {"FINISHED"}


class BDENTAL_OT_clear_analysis_overlay(bpy.types.Operator):
    bl_idname = "bdental.clear_analysis_overlay"
    bl_label = "Clear Analysis Overlay"

    def execute(self, context):
        _active(_state(context)).analysis_overlay_visible = False
        return {"FINISHED"}


class BDENTAL_OT_back_to_step_three(bpy.types.Operator):
    bl_idname = "bdental.back_to_step_three"
    bl_label = "Back to Step 3"

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        if restoration is not None and restoration.axis_session_active:
            self.report({"ERROR"}, "Apply or cancel the active axis session before leaving Step 4.")
            return {"CANCELLED"}
        state.current_step = "STEP_3"
        return {"FINISHED"}


def _draw_step_four_list(layout, state) -> None:
    box = layout.box()
    approved = sum(1 for item in state.restorations if item.step_4_valid)
    box.label(text=f"Restorations | Approved {approved} of {len(state.restorations)}", icon="OUTLINER_COLLECTION")
    for index, restoration in enumerate(state.restorations):
        row = box.row(align=True)
        operator = row.operator("bdental.select_step_four_restoration", text=f"FDI {restoration.target_tooth_fdi}", icon="CHECKMARK" if restoration.step_4_valid else "EMPTY_AXIS", depress=index == state.active_restoration_index)
        operator.index = index
        row.label(text=restoration.step_4_status.replace("_", " ").title())


def _draw_step_four(layout, state, context) -> None:
    header = layout.box()
    header.label(text="Steps 1-3 Complete", icon="CHECKMARK")
    header.label(text="Step 4 of 4")
    header.label(text="Preparation Analysis & Insertion Axis")
    header.label(text=f"Status: {state.step_4_status.replace('_', ' ').title()}")
    _draw_step_four_list(layout, state)
    restoration = _active(state)
    if restoration is None:
        return

    identity = layout.box()
    identity.label(text=f"Active: FDI {restoration.target_tooth_fdi}", icon="MESH_DATA")
    identity.label(text=f"Preparation: {properties.role_label(restoration.target_arch)}")
    identity.operator("bdental.focus_step_three_target", text="Focus Preparation", icon="VIEWZOOM")

    axis_box = layout.box()
    axis_box.label(text="Insertion Axis", icon="EMPTY_AXIS")
    axis = axis_geometry.deserialize_vector(restoration.insertion_axis_local)
    obj = axis_geometry.resolve_axis(restoration)
    if restoration.axis_session_active:
        axis_box.label(text="Reversible axis session active", icon="REC")
        axis_box.operator("bdental.capture_axis_candidate", text="Capture Axis Candidate", icon="CHECKMARK")
        axis_box.operator("bdental.apply_axis_candidate", text="Apply Axis Candidate", icon="FILE_TICK")
        row = axis_box.row(align=True)
        row.operator("bdental.reset_axis_session", text="Reset", icon="LOOP_BACK")
        row.operator("bdental.cancel_axis_session", text="Cancel", icon="CANCEL")
    else:
        row = axis_box.row(align=True)
        row.operator_context = "INVOKE_REGION_WIN"
        row.operator("bdental.axis_from_view", text="Set From View", icon="VIEW_CAMERA")
        row.operator("bdental.axis_from_margin", text="Suggest From Margin", icon="ORIENTATION_NORMAL")
        if axis is not None:
            axis_box.label(text=f"Source: {restoration.axis_source.replace('_', ' ').title()}")
            axis_box.label(text=f"Local: {axis.x:.4f}, {axis.y:.4f}, {axis.z:.4f}")
            row = axis_box.row(align=True)
            row.operator("bdental.start_axis_session", text="Edit", icon="ORIENTATION_GIMBAL")
            row.operator("bdental.focus_axis", text="Focus", icon="VIEWZOOM")
            if obj is not None:
                row.operator("bdental.toggle_axis_visibility", text="Show" if obj.hide_viewport else "Hide", icon="HIDE_ON" if obj.hide_viewport else "HIDE_OFF")
            axis_box.operator("bdental.clear_axis", text="Clear Axis", icon="TRASH")
        else:
            ui._draw_wrapped_label(axis_box, "Look toward the preparation along the intended seating direction, then capture the current view.", icon="INFO")

    analysis = layout.box()
    analysis.label(text="Preparation Undercut Analysis", icon="VIEWZOOM")
    analysis.prop(restoration, "analysis_radius")
    analysis.operator("bdental.run_undercut_analysis", text="Run Undercut Analysis", icon="MODIFIER")
    if restoration.analysis_sample_count > 0:
        analysis.label(text=f"Samples: {restoration.analysis_sample_count}")
        analysis.label(text=f"Undercut: {restoration.analysis_undercut_count} ({restoration.analysis_undercut_ratio:.1%})")
        analysis.label(text=f"Mean depth: {restoration.analysis_mean_blocking_depth * 1000.0:.3f} mm")
        analysis.label(text=f"Max depth: {restoration.analysis_max_blocking_depth * 1000.0:.3f} mm")
        analysis.label(text=f"Runtime: {restoration.analysis_duration_seconds:.3f} s")
        row = analysis.row(align=True)
        row.operator("bdental.toggle_analysis_overlay", text="Hide Overlay" if restoration.analysis_overlay_visible else "Show Overlay", icon="HIDE_OFF")
        row.operator("bdental.clear_analysis_overlay", text="Clear", icon="X")
        analysis.operator("bdental.validate_step_four", text="Validate Step 4", icon="FILE_TICK")

    ui._draw_messages(layout, restoration.step_4_errors, title="Blocking Errors", icon="ERROR")
    ui._draw_messages(layout, restoration.step_4_warnings, title="Engineering Warnings", icon="INFO")
    if restoration.step_4_summary:
        ui._draw_wrapped_label(layout.box(), restoration.step_4_summary)
    disclaimer = layout.box()
    ui._draw_wrapped_label(disclaimer, "This analysis is a bounded engineering aid. It does not certify a clinically correct path of insertion.", icon="INFO")

    if restoration.analysis_current and not restoration.axis_session_active:
        approval = layout.box()
        approval.label(text=f"Approve FDI {restoration.target_tooth_fdi}")
        approval.prop(restoration, "step_4_review_confirmed")
        if restoration.step_4_warnings:
            approval.prop(restoration, "step_4_warning_acknowledged")
        approval.operator("bdental.approve_step_four", text="Approve Preparation Analysis", icon="CHECKMARK")
    layout.operator("bdental.back_to_step_three", text="Back to Step 3", icon="BACK")


def _patch_ui() -> None:
    if not hasattr(ui, "_bdental_step_four_original_draw_step_three"):
        original_step_three = ui._draw_step_three
        ui._bdental_step_four_original_draw_step_three = original_step_three

        def draw_step_three(layout, state, context):
            original_step_three(layout, state, context)
            if state.step_3_valid:
                layout.operator("bdental.enter_step_four", text="Continue to Step 4", icon="FORWARD")

        ui._draw_step_three = draw_step_three

    panel = ui.BDENTAL_PT_workflow
    if not hasattr(panel, "_bdental_step_four_original_draw"):
        original_draw = panel.draw
        panel._bdental_step_four_original_draw = original_draw

        def draw(self, context):
            state = context.scene.bdental_workflow
            if state.current_step == "STEP_4":
                layout = self.layout
                layout.operator_context = "INVOKE_DEFAULT"
                _draw_step_four(layout, state, context)
            else:
                original_draw(self, context)

        panel.draw = draw


def _patch_step_three_selection() -> None:
    operator = step_three_operators.BDENTAL_OT_select_restoration
    if hasattr(operator, "_bdental_step_four_original_execute"):
        return
    original = operator.execute
    operator._bdental_step_four_original_execute = original

    def execute(self, context):
        active = restoration_utils.active_restoration(context.scene.bdental_workflow)
        if active is not None and getattr(active, "axis_session_active", False):
            self.report({"ERROR"}, "Apply or cancel the active axis session before switching.")
            return {"CANCELLED"}
        return original(self, context)

    operator.execute = execute


def _patch_remove_restoration() -> None:
    operator = step_three_operators.BDENTAL_OT_remove_restoration
    if hasattr(operator, "_bdental_step_four_original_execute"):
        return
    original = operator.execute
    operator._bdental_step_four_original_execute = original

    def execute(self, context):
        restoration = restoration_utils.active_restoration(context.scene.bdental_workflow)
        if restoration is not None and getattr(restoration, "axis_session_active", False):
            self.report({"ERROR"}, "Cancel the active axis session before removing this restoration.")
            return {"CANCELLED"}
        axis = axis_geometry.resolve_axis(restoration)
        result = original(self, context)
        if result == {"FINISHED"} and axis is not None:
            axis_geometry.remove_axis_object(axis)
        step_four_session.sync_step_four_state(context.scene.bdental_workflow)
        return result

    operator.execute = execute


CLASSES = (
    BDENTAL_OT_enter_step_four,
    BDENTAL_OT_select_step_four_restoration,
    BDENTAL_OT_axis_from_view,
    BDENTAL_OT_axis_from_margin,
    BDENTAL_OT_start_axis_session,
    BDENTAL_OT_capture_axis_candidate,
    BDENTAL_OT_apply_axis_candidate,
    BDENTAL_OT_reset_axis_session,
    BDENTAL_OT_cancel_axis_session,
    BDENTAL_OT_focus_axis,
    BDENTAL_OT_toggle_axis_visibility,
    BDENTAL_OT_clear_axis,
    BDENTAL_OT_run_undercut_analysis,
    BDENTAL_OT_validate_step_four,
    BDENTAL_OT_approve_step_four,
    BDENTAL_OT_toggle_analysis_overlay,
    BDENTAL_OT_clear_analysis_overlay,
    BDENTAL_OT_back_to_step_three,
)

_patch_ui()
_patch_step_three_selection()
_patch_remove_restoration()
