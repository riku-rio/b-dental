"""Step 3 restoration setup and manual-margin operators for B-Dental."""

from __future__ import annotations

import bpy

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


def _messages(state, summary="", errors=(), warnings=()):
    state.step_3_summary = summary
    state.step_3_errors = "\n".join(errors)
    state.step_3_warnings = "\n".join(warnings)
    state.margin_warning_acknowledged = False
    state.margin_review_confirmed = False


def _store_diagnostics(state, result):
    state.margin_point_count = result.point_count
    state.margin_path_length = result.path_length
    state.margin_mean_surface_distance = result.mean_surface_distance
    state.margin_max_surface_distance = result.max_surface_distance


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
    bl_description = "Open restoration setup after Step 2 completion"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return _ready(context) and not context.scene.bdental_workflow.alignment_session_active

    def execute(self, context):
        state = _state(context)
        restoration_utils.initialize_target_defaults(state)
        result = margin_validation.validate_step_three_preconditions(state)
        if not result.ok:
            _messages(state, result.summary, result.errors, result.warnings)
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}

        state.current_step = "STEP_3"
        if state.step_3_valid:
            state.step_3_status = "VERIFIED"
        elif state.restoration_id and state.target_scan_signature:
            state.step_3_status = "CANDIDATE" if restoration_utils.resolve_margin(state) else "READY_FOR_MARGIN"
        else:
            state.step_3_status = "SETUP_REQUIRED"
            state.step_3_summary = "Confirm the restoration setup before drawing the margin."
        return {"FINISHED"}


class BDENTAL_OT_create_restoration(bpy.types.Operator):
    bl_idname = "bdental.create_restoration"
    bl_label = "Confirm Restoration Setup"
    bl_description = "Create one anatomical-crown restoration for the selected arch and FDI tooth"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(state and state.current_step == "STEP_3" and state.step_2_valid)

    def execute(self, context):
        state = _state(context)
        if restoration_utils.resolve_margin(state) is not None:
            self.report({"ERROR"}, "Reset Restoration Setup before changing a restoration with a margin.")
            return {"CANCELLED"}

        result = margin_validation.validate_step_three_preconditions(state)
        if not result.ok:
            _messages(state, result.summary, result.errors, result.warnings)
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}
        if not restoration_utils.tooth_belongs_to_arch(state.target_tooth_fdi, state.target_arch):
            _messages(
                state,
                "Restoration setup is invalid.",
                ("The selected FDI tooth does not belong to the preparation arch.",),
            )
            return {"CANCELLED"}

        target = restoration_utils.target_scan(state)
        state.internal_update_lock = True
        try:
            state.restoration_id = state.restoration_id or restoration_utils.new_restoration_id()
            state.restoration_type = restoration_utils.RESTORATION_TYPE
            state.target_scan_signature = restoration_utils.target_scan_signature(target)
            state.step_3_status = "READY_FOR_MARGIN"
            state.step_3_valid = False
            state.margin_candidate_closed = False
            state.margin_review_confirmed = False
            state.margin_warning_acknowledged = False
            state.step_3_summary = (
                f"Anatomical crown configured for FDI {state.target_tooth_fdi} on "
                f"{properties.role_label(state.target_arch)}."
            )
            state.step_3_errors = ""
            state.step_3_warnings = ""
        finally:
            state.internal_update_lock = False
        self.report({"INFO"}, state.step_3_summary)
        return {"FINISHED"}


class BDENTAL_OT_reset_restoration_setup(bpy.types.Operator):
    bl_idname = "bdental.reset_restoration_setup"
    bl_label = "Reset Restoration Setup"
    bl_description = "Remove only the active managed margin and configure the restoration again"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        state = _state(context)
        if state.restoration_id or restoration_utils.resolve_margin(state) is not None:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        state = _state(context)
        restoration_utils.remove_active_margin(state)
        state.internal_update_lock = True
        try:
            properties.clear_step_three_state(state)
            state.current_step = "STEP_3"
            restoration_utils.initialize_target_defaults(state)
            state.step_3_status = "SETUP_REQUIRED"
            state.step_3_summary = "Restoration setup reset. Select the target arch and tooth."
        finally:
            state.internal_update_lock = False
        return {"FINISHED"}


class BDENTAL_OT_draw_margin(bpy.types.Operator):
    bl_idname = "bdental.draw_margin"
    bl_label = "Draw Manual Margin"
    bl_description = "Place ordered points on the selected preparation scan"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and state.current_step == "STEP_3"
            and state.step_2_valid
            and state.restoration_id
            and not state.margin_session_active
        )

    def invoke(self, context, event):
        del event
        if context.area is None or context.area.type != "VIEW_3D" or context.region_data is None:
            self.report({"ERROR"}, "Manual margin drawing must start in a 3D Viewport.")
            return {"CANCELLED"}

        state = _state(context)
        result = margin_validation.validate_restoration_setup(state)
        if not result.ok:
            _messages(state, result.summary, result.errors, result.warnings)
            self.report({"ERROR"}, result.errors[0])
            return {"CANCELLED"}

        try:
            margin = step_three_session.start_session(context.scene, state)
            _select_only(context, margin)
        except Exception as exc:
            state.step_3_status = "ERROR"
            _messages(state, "Could not start the manual margin session.", (str(exc),))
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
        margin = restoration_utils.resolve_margin(state)
        target = restoration_utils.target_scan(state)
        if margin is None or target is None:
            _clear_modal_status(context)
            if state.margin_session_active:
                step_three_session.cancel_session(state)
            self.report({"ERROR"}, "The active margin or preparation scan became unavailable.")
            return {"CANCELLED"}

        if event.type == "ESC" and event.value == "PRESS":
            step_three_session.cancel_session(state)
            _clear_modal_status(context)
            self.report({"INFO"}, "Manual margin drawing cancelled.")
            return {"CANCELLED"}

        if event.type in {"BACK_SPACE", "DEL"} and event.value == "PRESS":
            margin_geometry.remove_last_curve_point(margin)
            state.margin_candidate_closed = False
            return {"RUNNING_MODAL"}

        if event.type == "Z" and event.value == "PRESS" and event.ctrl:
            margin_geometry.remove_last_curve_point(margin)
            state.margin_candidate_closed = False
            return {"RUNNING_MODAL"}

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            hit = margin_geometry.raycast_target(context, event, target)
            if hit is None:
                self.report({"WARNING"}, "No point was added; click directly on the preparation scan.")
            else:
                margin_geometry.append_curve_point(margin, hit)
                state.margin_point_count = len(margin_geometry.curve_points(margin))
                state.step_3_summary = f"Placed {state.margin_point_count} margin point(s)."
            return {"RUNNING_MODAL"}

        if event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"} and event.value == "PRESS":
            ok, message = step_three_session.capture_candidate(state)
            if not ok:
                self.report({"WARNING"}, message)
                return {"RUNNING_MODAL"}
            _clear_modal_status(context)
            self.report({"INFO"}, message)
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
        state = context.scene.bdental_workflow if context.scene else None
        return bool(state and state.margin_session_active)

    def execute(self, context):
        step_three_session.reset_session(_state(context))
        return {"FINISHED"}


class BDENTAL_OT_cancel_margin_session(bpy.types.Operator):
    bl_idname = "bdental.cancel_margin_session"
    bl_label = "Cancel Margin Session"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(state and state.margin_session_active)

    def execute(self, context):
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
        step_three_session.cancel_session(_state(context))
        return {"FINISHED"}


class BDENTAL_OT_apply_margin_candidate(bpy.types.Operator):
    bl_idname = "bdental.apply_margin_candidate"
    bl_label = "Apply Margin Candidate"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and state.margin_session_active
            and state.margin_candidate_closed
            and restoration_utils.resolve_margin(state) is not None
        )

    def execute(self, context):
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
        state = _state(context)
        ok, message = step_three_session.capture_candidate(state)
        if not ok:
            self.report({"ERROR"}, message)
            return {"CANCELLED"}
        step_three_session.apply_candidate(state)
        return {"FINISHED"}


class BDENTAL_OT_prepare_margin_edit(bpy.types.Operator):
    bl_idname = "bdental.prepare_margin_edit"
    bl_label = "Edit Margin Points"
    bl_description = "Start a reversible edit session for the managed margin curve"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and not state.margin_session_active
            and restoration_utils.resolve_margin(state) is not None
        )

    def execute(self, context):
        state = _state(context)
        margin = step_three_session.start_session(context.scene, state)
        points = margin_geometry.curve_points(margin)
        margin_geometry.replace_curve_points(margin, points, cyclic=True)
        state.margin_candidate_closed = True
        _select_only(context, margin)
        try:
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.curve.select_all(action="SELECT")
        except RuntimeError as exc:
            step_three_session.cancel_session(state)
            self.report({"ERROR"}, f"Could not enter curve edit mode: {exc}")
            return {"CANCELLED"}
        state.step_3_summary = "Edit the selected curve points, then reproject and capture the candidate."
        return {"FINISHED"}


class BDENTAL_OT_reproject_margin(bpy.types.Operator):
    bl_idname = "bdental.reproject_margin"
    bl_label = "Reproject Margin Points"
    bl_description = "Project edited margin points to the nearest target-scan surface locations"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(state and restoration_utils.resolve_margin(state) is not None)

    def execute(self, context):
        state = _state(context)
        margin = restoration_utils.resolve_margin(state)
        target = restoration_utils.target_scan(state)
        if margin is None or target is None:
            return {"CANCELLED"}
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError as exc:
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}
        points = margin_geometry.curve_points(margin)
        try:
            projected = margin_geometry.reproject_points(
                target,
                points,
                context.evaluated_depsgraph_get(),
            )
            margin_geometry.replace_curve_points(margin, projected, cyclic=True)
        except (RuntimeError, ValueError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        state.margin_candidate_closed = True
        state.step_3_valid = False
        state.step_3_status = "CANDIDATE" if not state.margin_session_active else "DRAWING"
        state.step_3_summary = "Margin points reprojected to the target preparation surface."
        return {"FINISHED"}


class BDENTAL_OT_capture_edited_margin(bpy.types.Operator):
    bl_idname = "bdental.capture_edited_margin"
    bl_label = "Capture Edited Candidate"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(state and state.margin_session_active)

    def execute(self, context):
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError as exc:
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}
        state = _state(context)
        ok, message = step_three_session.capture_candidate(state)
        if not ok:
            self.report({"ERROR"}, message)
            return {"CANCELLED"}
        self.report({"INFO"}, message)
        return {"FINISHED"}


class BDENTAL_OT_validate_margin(bpy.types.Operator):
    bl_idname = "bdental.validate_margin"
    bl_label = "Run Margin Validation"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and not state.margin_session_active
            and restoration_utils.resolve_margin(state) is not None
        )

    def execute(self, context):
        state = _state(context)
        result = margin_validation.validate_margin(state, context.evaluated_depsgraph_get())
        state.step_3_status = result.status
        state.step_3_valid = False
        _store_diagnostics(state, result)
        _messages(state, result.summary, result.errors, result.warnings)
        if result.ok:
            self.report({"INFO"}, result.summary)
            return {"FINISHED"}
        self.report({"ERROR"}, result.errors[0])
        return {"CANCELLED"}


class BDENTAL_OT_approve_margin(bpy.types.Operator):
    bl_idname = "bdental.approve_margin"
    bl_label = "Approve Manual Margin"
    bl_description = "Approve the reviewed margin without claiming clinical correctness"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and state.step_3_status == "CANDIDATE"
            and not state.margin_session_active
            and state.margin_review_confirmed
            and not state.step_3_errors
            and (not state.step_3_warnings or state.margin_warning_acknowledged)
        )

    def execute(self, context):
        state = _state(context)
        result = margin_validation.validate_margin(state, context.evaluated_depsgraph_get())
        _store_diagnostics(state, result)
        if not result.ok:
            _messages(state, result.summary, result.errors, result.warnings)
            return {"CANCELLED"}
        if result.warnings and not state.margin_warning_acknowledged:
            _messages(state, result.summary, result.errors, result.warnings)
            self.report({"ERROR"}, "Acknowledge the margin warnings before approval.")
            return {"CANCELLED"}
        if not state.margin_review_confirmed:
            self.report({"ERROR"}, "Confirm visual review before approval.")
            return {"CANCELLED"}

        step_three_session.snapshot_approved(state)
        state.step_3_status = "VERIFIED"
        state.step_3_valid = True
        state.step_3_errors = ""
        state.step_3_warnings = "\n".join(result.warnings)
        state.step_3_summary = (
            f"Step 3 approved for anatomical crown FDI {state.target_tooth_fdi}. "
            "Engineering checks do not certify clinical correctness."
        )
        self.report({"INFO"}, "Step 3 manual margin approved.")
        return {"FINISHED"}


class BDENTAL_OT_focus_step_three_target(bpy.types.Operator):
    bl_idname = "bdental.focus_step_three_target"
    bl_label = "Focus Preparation Scan"

    def execute(self, context):
        target = restoration_utils.target_scan(_state(context))
        if target is None:
            return {"CANCELLED"}
        _select_only(context, target)
        if not _frame_selected(context):
            self.report({"WARNING"}, "Preparation scan selected, but no 3D Viewport could be framed.")
        return {"FINISHED"}


class BDENTAL_OT_focus_margin(bpy.types.Operator):
    bl_idname = "bdental.focus_margin"
    bl_label = "Focus Margin"

    def execute(self, context):
        margin = restoration_utils.resolve_margin(_state(context))
        if margin is None:
            return {"CANCELLED"}
        _select_only(context, margin)
        if not _frame_selected(context):
            self.report({"WARNING"}, "Margin selected, but no 3D Viewport could be framed.")
        return {"FINISHED"}


class BDENTAL_OT_toggle_margin_visibility(bpy.types.Operator):
    bl_idname = "bdental.toggle_margin_visibility"
    bl_label = "Toggle Margin Visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        margin = restoration_utils.resolve_margin(_state(context))
        if margin is None:
            return {"CANCELLED"}
        margin.hide_viewport = not margin.hide_viewport
        return {"FINISHED"}


class BDENTAL_OT_back_to_step_two(bpy.types.Operator):
    bl_idname = "bdental.back_to_step_two"
    bl_label = "Back to Step 2"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if _state(context).margin_session_active:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        state = _state(context)
        if context.object is not None and context.object.mode == "EDIT":
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
        if state.margin_session_active:
            step_three_session.cancel_session(state)
        state.current_step = "STEP_2"
        return {"FINISHED"}


CLASSES = (
    BDENTAL_OT_enter_step_three,
    BDENTAL_OT_create_restoration,
    BDENTAL_OT_reset_restoration_setup,
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
