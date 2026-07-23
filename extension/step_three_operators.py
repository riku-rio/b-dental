"""Step 3 multiple-restoration and manual-margin operators for B-Dental."""

from __future__ import annotations

import bpy
from bpy.props import IntProperty

from . import (
    margin_geometry,
    margin_validation,
    properties,
    restoration_utils,
    scene_utils,
    step_three_session,
)


def _state(context):
    return context.scene.bdental_workflow


def _active(state):
    return restoration_utils.active_restoration(state)


def _messages(restoration, summary="", errors=(), warnings=()):
    restoration.summary = summary
    restoration.errors = "\n".join(errors)
    restoration.warnings = "\n".join(warnings)
    restoration.warning_acknowledged = False
    restoration.review_confirmed = False


def _store_diagnostics(restoration, result):
    restoration.margin_point_count = result.point_count
    restoration.margin_path_length = result.path_length
    restoration.margin_mean_surface_distance = result.mean_surface_distance
    restoration.margin_max_surface_distance = result.max_surface_distance


def _ready(context):
    return bool(
        context.scene
        and hasattr(context.scene, "bdental_workflow")
        and context.scene.bdental_workflow.step_1_valid
        and context.scene.bdental_workflow.step_2_valid
    )


def _select_only(context, target):
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
    window_manager = context.window_manager
    if window_manager is None:
        return False
    for window in window_manager.windows:
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
                with context.temp_override(
                    window=window,
                    screen=screen,
                    area=area,
                    region=region,
                    space_data=area.spaces.active,
                ):
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                return True
            except (RuntimeError, TypeError):
                continue
    return False


def _clear_modal_status(context):
    try:
        context.workspace.status_text_set(None)
    except (AttributeError, RuntimeError):
        pass
    try:
        context.area.header_text_set(None)
    except (AttributeError, RuntimeError):
        pass


class BDENTAL_OT_enter_step_three(bpy.types.Operator):
    bl_idname = "bdental.enter_step_three"
    bl_label = "Continue to Step 3"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return _ready(context) and not context.scene.bdental_workflow.alignment_session_active

    def execute(self, context):
        state = _state(context)
        result = margin_validation.validate_step_three_preconditions(state)
        if not result.ok:
            state.step_3_summary = result.summary
            state.step_3_errors = "\n".join(result.errors)
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}
        restoration_utils.migrate_legacy_restoration(state)
        restoration_utils.initialize_new_restoration_defaults(state)
        state.current_step = "STEP_3"
        properties.sync_step_three_state(state)
        state.step_3_summary = (
            f"{len(state.restorations)} restoration(s) configured."
            if state.restorations
            else "Add the first restoration."
        )
        return {"FINISHED"}


class BDENTAL_OT_add_restoration(bpy.types.Operator):
    bl_idname = "bdental.add_restoration"
    bl_label = "Add Restoration"
    bl_description = "Add an independent anatomical crown restoration"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(state and state.current_step == "STEP_3" and state.step_2_valid)

    def execute(self, context):
        state = _state(context)
        restoration_utils.initialize_new_restoration_defaults(state)
        arch = state.new_target_arch
        tooth = state.new_target_tooth_fdi
        if arch not in restoration_utils.available_target_arches(state):
            self.report({"ERROR"}, "The selected preparation arch is unavailable.")
            return {"CANCELLED"}
        if not restoration_utils.tooth_belongs_to_arch(tooth, arch):
            self.report({"ERROR"}, "The selected FDI tooth does not belong to the preparation arch.")
            return {"CANCELLED"}
        if restoration_utils.duplicate_tooth_exists(state, arch, tooth):
            self.report({"ERROR"}, f"FDI {tooth} already has a restoration.")
            return {"CANCELLED"}

        restoration = state.restorations.add()
        restoration.restoration_id = restoration_utils.new_restoration_id()
        restoration.restoration_type = restoration_utils.RESTORATION_TYPE
        restoration.target_arch = arch
        restoration.target_tooth_fdi = tooth
        restoration.target_scan_signature = restoration_utils.target_scan_signature(
            restoration_utils.target_scan(state, restoration)
        )
        restoration.status = "READY_FOR_MARGIN"
        restoration.summary = f"Anatomical crown configured for FDI {tooth}."
        state.active_restoration_index = len(state.restorations) - 1
        properties.sync_step_three_state(state)
        self.report({"INFO"}, restoration.summary)
        return {"FINISHED"}


class BDENTAL_OT_select_restoration(bpy.types.Operator):
    bl_idname = "bdental.select_restoration"
    bl_label = "Select Restoration"
    bl_options = {"REGISTER"}

    index: IntProperty(default=0, min=0)

    def execute(self, context):
        state = _state(context)
        active = _active(state)
        if active is not None and active.margin_session_active:
            self.report({"ERROR"}, "Apply or cancel the active margin session before switching.")
            return {"CANCELLED"}
        if self.index >= len(state.restorations):
            return {"CANCELLED"}
        state.active_restoration_index = self.index
        properties.sync_step_three_state(state)
        return {"FINISHED"}


class BDENTAL_OT_remove_restoration(bpy.types.Operator):
    bl_idname = "bdental.remove_restoration"
    bl_label = "Remove Restoration"
    bl_description = "Remove only the active restoration and its managed margin"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        if restoration is None:
            return {"CANCELLED"}
        if restoration.margin_session_active:
            self.report({"ERROR"}, "Cancel the active margin session before removing this restoration.")
            return {"CANCELLED"}
        index = state.active_restoration_index
        restoration_utils.remove_restoration_margin(restoration)
        state.restorations.remove(index)
        state.active_restoration_index = min(index, max(0, len(state.restorations) - 1))
        properties.sync_step_three_state(state)
        return {"FINISHED"}


class BDENTAL_OT_draw_margin(bpy.types.Operator):
    bl_idname = "bdental.draw_margin"
    bl_label = "Draw Manual Margin"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        restoration = _active(state) if state else None
        return bool(
            state
            and restoration
            and state.current_step == "STEP_3"
            and state.step_2_valid
            and not restoration.margin_session_active
        )

    def invoke(self, context, event):
        del event
        if context.area is None or context.area.type != "VIEW_3D" or context.region_data is None:
            self.report({"ERROR"}, "Manual margin drawing must start in a 3D Viewport.")
            return {"CANCELLED"}
        state = _state(context)
        restoration = _active(state)
        result = margin_validation.validate_restoration_setup(state, restoration)
        if not result.ok:
            _messages(restoration, result.summary, result.errors, result.warnings)
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}
        try:
            margin = step_three_session.start_session(context.scene, state, restoration)
            _select_only(context, margin)
        except Exception as exc:
            restoration.status = "ERROR"
            _messages(restoration, "Could not start the manual margin session.", (str(exc),))
            properties.sync_step_three_state(state)
            return {"CANCELLED"}
        context.window_manager.modal_handler_add(self)
        instructions = "LMB: add point | Backspace/Ctrl+Z: remove last | Enter/RMB: close | Esc: cancel"
        try:
            context.workspace.status_text_set(instructions)
            context.area.header_text_set(instructions)
        except (AttributeError, RuntimeError):
            pass
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        state = _state(context)
        restoration = _active(state)
        margin = restoration_utils.resolve_margin(restoration)
        target = restoration_utils.target_scan(state, restoration)
        if restoration is None or margin is None or target is None:
            _clear_modal_status(context)
            if restoration is not None and restoration.margin_session_active:
                step_three_session.cancel_session(state, restoration)
            self.report({"ERROR"}, "The active restoration became unavailable.")
            return {"CANCELLED"}

        if event.type == "ESC" and event.value == "PRESS":
            step_three_session.cancel_session(state, restoration)
            _clear_modal_status(context)
            return {"CANCELLED"}
        if event.type in {"BACK_SPACE", "DEL"} and event.value == "PRESS":
            margin_geometry.remove_last_curve_point(margin)
            restoration.margin_candidate_closed = False
            return {"RUNNING_MODAL"}
        if event.type == "Z" and event.value == "PRESS" and event.ctrl:
            margin_geometry.remove_last_curve_point(margin)
            restoration.margin_candidate_closed = False
            return {"RUNNING_MODAL"}
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            hit = margin_geometry.raycast_target(context, event, target)
            if hit is None:
                self.report({"WARNING"}, "Click directly on the active preparation scan.")
            else:
                margin_geometry.append_curve_point(margin, hit)
                restoration.margin_point_count = len(margin_geometry.curve_points(margin))
                restoration.summary = f"Placed {restoration.margin_point_count} margin point(s)."
            return {"RUNNING_MODAL"}
        if event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"} and event.value == "PRESS":
            ok, message = step_three_session.capture_candidate(state, restoration)
            if not ok:
                self.report({"WARNING"}, message)
                return {"RUNNING_MODAL"}
            _clear_modal_status(context)
            return {"FINISHED"}
        if event.type in {
            "MIDDLEMOUSE",
            "WHEELUPMOUSE",
            "WHEELDOWNMOUSE",
            "TRACKPADPAN",
            "TRACKPADZOOM",
        }:
            return {"PASS_THROUGH"}
        return {"RUNNING_MODAL"}


class BDENTAL_OT_reset_margin_session(bpy.types.Operator):
    bl_idname = "bdental.reset_margin_session"
    bl_label = "Reset Margin Session"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        restoration = _active(context.scene.bdental_workflow) if context.scene else None
        return bool(restoration and restoration.margin_session_active)

    def execute(self, context):
        state = _state(context)
        step_three_session.reset_session(state, _active(state))
        return {"FINISHED"}


class BDENTAL_OT_cancel_margin_session(bpy.types.Operator):
    bl_idname = "bdental.cancel_margin_session"
    bl_label = "Cancel Margin Session"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        restoration = _active(context.scene.bdental_workflow) if context.scene else None
        return bool(restoration and restoration.margin_session_active)

    def execute(self, context):
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
        state = _state(context)
        step_three_session.cancel_session(state, _active(state))
        return {"FINISHED"}


class BDENTAL_OT_apply_margin_candidate(bpy.types.Operator):
    bl_idname = "bdental.apply_margin_candidate"
    bl_label = "Apply Margin Candidate"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        restoration = _active(context.scene.bdental_workflow) if context.scene else None
        return bool(
            restoration
            and restoration.margin_session_active
            and restoration.margin_candidate_closed
            and restoration_utils.resolve_margin(restoration) is not None
        )

    def execute(self, context):
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
        state = _state(context)
        restoration = _active(state)
        ok, message = step_three_session.capture_candidate(state, restoration)
        if not ok:
            self.report({"ERROR"}, message)
            return {"CANCELLED"}
        step_three_session.apply_candidate(state, restoration)
        return {"FINISHED"}


class BDENTAL_OT_prepare_margin_edit(bpy.types.Operator):
    bl_idname = "bdental.prepare_margin_edit"
    bl_label = "Edit Margin Points"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        restoration = _active(context.scene.bdental_workflow) if context.scene else None
        return bool(
            restoration
            and not restoration.margin_session_active
            and restoration_utils.resolve_margin(restoration) is not None
        )

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        margin = step_three_session.start_session(context.scene, state, restoration)
        margin_geometry.replace_curve_points(
            margin,
            margin_geometry.curve_points(margin),
            cyclic=True,
        )
        restoration.margin_candidate_closed = True
        _select_only(context, margin)
        try:
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.curve.select_all(action="SELECT")
        except RuntimeError as exc:
            step_three_session.cancel_session(state, restoration)
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        restoration.summary = "Edit points, then reproject and capture the candidate."
        return {"FINISHED"}


class BDENTAL_OT_reproject_margin(bpy.types.Operator):
    bl_idname = "bdental.reproject_margin"
    bl_label = "Reproject Margin Points"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        restoration = _active(context.scene.bdental_workflow) if context.scene else None
        return bool(restoration and restoration_utils.resolve_margin(restoration) is not None)

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        margin = restoration_utils.resolve_margin(restoration)
        target = restoration_utils.target_scan(state, restoration)
        if margin is None or target is None:
            return {"CANCELLED"}
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError as exc:
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}
        try:
            projected = margin_geometry.reproject_points(
                target,
                margin_geometry.curve_points(margin),
                context.evaluated_depsgraph_get(),
            )
            margin_geometry.replace_curve_points(margin, projected, cyclic=True)
        except (RuntimeError, ValueError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        properties.clear_restoration_approval(restoration)
        restoration.margin_candidate_closed = True
        restoration.status = "DRAWING" if restoration.margin_session_active else "CANDIDATE"
        restoration.summary = "Margin points reprojected to this restoration's preparation surface."
        properties.sync_step_three_state(state)
        return {"FINISHED"}


class BDENTAL_OT_capture_edited_margin(bpy.types.Operator):
    bl_idname = "bdental.capture_edited_margin"
    bl_label = "Capture Edited Candidate"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError as exc:
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}
        state = _state(context)
        restoration = _active(state)
        ok, message = step_three_session.capture_candidate(state, restoration)
        if not ok:
            self.report({"ERROR"}, message)
            return {"CANCELLED"}
        return {"FINISHED"}


class BDENTAL_OT_validate_margin(bpy.types.Operator):
    bl_idname = "bdental.validate_margin"
    bl_label = "Run Margin Validation"
    bl_options = {"REGISTER"}

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        result = margin_validation.validate_margin(
            state,
            restoration,
            context.evaluated_depsgraph_get(),
        )
        restoration.status = result.status
        restoration.valid = False
        _store_diagnostics(restoration, result)
        _messages(restoration, result.summary, result.errors, result.warnings)
        properties.sync_step_three_state(state)
        if result.ok:
            return {"FINISHED"}
        self.report({"ERROR"}, result.errors[0])
        return {"CANCELLED"}


class BDENTAL_OT_approve_margin(bpy.types.Operator):
    bl_idname = "bdental.approve_margin"
    bl_label = "Approve Manual Margin"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        restoration = _active(context.scene.bdental_workflow) if context.scene else None
        return bool(
            restoration
            and restoration.status == "CANDIDATE"
            and not restoration.margin_session_active
            and restoration.review_confirmed
            and not restoration.errors
            and (not restoration.warnings or restoration.warning_acknowledged)
        )

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        result = margin_validation.validate_margin(
            state,
            restoration,
            context.evaluated_depsgraph_get(),
        )
        _store_diagnostics(restoration, result)
        if not result.ok:
            _messages(restoration, result.summary, result.errors, result.warnings)
            properties.sync_step_three_state(state)
            return {"CANCELLED"}
        if result.warnings and not restoration.warning_acknowledged:
            _messages(restoration, result.summary, result.errors, result.warnings)
            self.report({"ERROR"}, "Acknowledge warnings before approval.")
            return {"CANCELLED"}
        if not restoration.review_confirmed:
            self.report({"ERROR"}, "Confirm visual review before approval.")
            return {"CANCELLED"}

        step_three_session.snapshot_approved(state, restoration)
        restoration.status = "VERIFIED"
        restoration.valid = True
        restoration.errors = ""
        restoration.warnings = "\n".join(result.warnings)
        restoration.summary = (
            f"Manual margin approved for FDI {restoration.target_tooth_fdi}. "
            "Engineering checks do not certify clinical correctness."
        )
        properties.sync_step_three_state(state)
        return {"FINISHED"}


class BDENTAL_OT_focus_step_three_target(bpy.types.Operator):
    bl_idname = "bdental.focus_step_three_target"
    bl_label = "Focus Preparation Scan"

    def execute(self, context):
        state = _state(context)
        target = restoration_utils.target_scan(state, _active(state))
        if target is None:
            return {"CANCELLED"}
        _select_only(context, target)
        _frame_selected(context)
        return {"FINISHED"}


class BDENTAL_OT_focus_margin(bpy.types.Operator):
    bl_idname = "bdental.focus_margin"
    bl_label = "Focus Margin"

    def execute(self, context):
        margin = restoration_utils.resolve_margin(_active(_state(context)))
        if margin is None:
            return {"CANCELLED"}
        _select_only(context, margin)
        _frame_selected(context)
        return {"FINISHED"}


class BDENTAL_OT_toggle_margin_visibility(bpy.types.Operator):
    bl_idname = "bdental.toggle_margin_visibility"
    bl_label = "Toggle Margin Visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        margin = restoration_utils.resolve_margin(_active(_state(context)))
        if margin is None:
            return {"CANCELLED"}
        margin.hide_viewport = not margin.hide_viewport
        return {"FINISHED"}


class BDENTAL_OT_back_to_step_two(bpy.types.Operator):
    bl_idname = "bdental.back_to_step_two"
    bl_label = "Back to Step 2"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        restoration = _active(_state(context))
        if restoration is not None and restoration.margin_session_active:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        state = _state(context)
        restoration = _active(state)
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
        if restoration is not None and restoration.margin_session_active:
            step_three_session.cancel_session(state, restoration)
        state.current_step = "STEP_2"
        return {"FINISHED"}


CLASSES = (
    BDENTAL_OT_enter_step_three,
    BDENTAL_OT_add_restoration,
    BDENTAL_OT_select_restoration,
    BDENTAL_OT_remove_restoration,
    BDENTAL_OT_draw_margin,
    BDENTAL_OT_reset_margin_session,
    BDENTAL_OT_cancel_margin_session,
    BDENTAL_OT_apply_margin_candidate,
    BDENTAL_OT_prepare_margin_edit,
    BDENTAL_OT_reproject_margin,
    BDENTAL_OT_capture_edited_margin,
    BDENTAL_OT_validate_margin,
    BDENTAL_OT_approve_margin,
    BDENTAL_OT_focus_step_three_target,
    BDENTAL_OT_focus_margin,
    BDENTAL_OT_toggle_margin_visibility,
    BDENTAL_OT_back_to_step_two,
)
