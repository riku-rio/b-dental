"""User actions for the B-Dental scan-import workflow."""

from collections.abc import Iterable

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy_extras.io_utils import ImportHelper

from . import properties, scene_utils, validation


def _workflow_state(context: bpy.types.Context) -> bpy.types.PropertyGroup:
    return context.scene.bdental_workflow


def _capture_selection(
    context: bpy.types.Context,
) -> tuple[tuple[bpy.types.Object, ...], bpy.types.Object | None]:
    selected = tuple(obj for obj in context.view_layer.objects if obj.select_get())
    return selected, context.view_layer.objects.active


def _restore_selection(
    context: bpy.types.Context,
    selected: Iterable[bpy.types.Object],
    active: bpy.types.Object | None,
) -> None:
    for obj in context.view_layer.objects:
        try:
            obj.select_set(False)
        except (ReferenceError, RuntimeError):
            continue

    for obj in selected:
        if scene_utils.object_is_alive(obj):
            try:
                obj.select_set(True)
            except (ReferenceError, RuntimeError):
                continue

    if scene_utils.object_is_alive(active):
        try:
            context.view_layer.objects.active = active
        except (ReferenceError, RuntimeError):
            pass


def _cleanup_objects(objects: Iterable[bpy.types.Object]) -> None:
    for obj in list(objects):
        scene_utils.remove_object(obj)


def _select_only(context: bpy.types.Context, target: bpy.types.Object) -> None:
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


def _frame_selected_in_viewport(context: bpy.types.Context) -> bool:
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


class BDENTAL_OT_start_case(bpy.types.Operator):
    """Initialize or reset the current scene as a B-Dental case."""

    bl_idname = "bdental.start_case"
    bl_label = "Start New Dental Case"
    bl_description = "Initialize Step 1 and safely remove only an untouched startup cube"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        state = _workflow_state(context)
        if scene_utils.has_destructive_reset_content(context.scene, state):
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context: bpy.types.Context):
        state = _workflow_state(context)
        removed_scans = scene_utils.remove_managed_case_scans(context.scene, state)
        removed_cube = scene_utils.remove_untouched_default_cube(context.scene)
        scene_utils.ensure_scan_collection(context.scene)
        scene_utils.reset_workflow_state(state)

        details: list[str] = []
        if removed_cube:
            details.append("removed untouched startup cube")
        if removed_scans:
            details.append(f"removed {removed_scans} managed scan(s)")
        suffix = f" ({'; '.join(details)})" if details else ""
        self.report({"INFO"}, f"B-Dental case initialized{suffix}.")
        return {"FINISHED"}


class BDENTAL_OT_import_scan(bpy.types.Operator, ImportHelper):
    """Import one STL and assign it transactionally to a dental role."""

    bl_idname = "bdental.import_scan"
    bl_label = "Import Scan STL"
    bl_description = "Import one STL file into the selected dental role"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".stl"
    filter_glob: StringProperty(default="*.stl", options={"HIDDEN"})
    role: EnumProperty(name="Dental Role", items=properties.SCAN_ROLE_ITEMS)
    replace_existing: BoolProperty(
        name="Replace Existing",
        default=False,
        options={"HIDDEN"},
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return (
            context.scene is not None
            and hasattr(context.scene, "bdental_workflow")
            and context.scene.bdental_workflow.case_initialized
        )

    def execute(self, context: bpy.types.Context):
        state = _workflow_state(context)
        if self.role not in properties.SCAN_ROLES:
            self.report({"ERROR"}, "Unsupported dental scan role.")
            return {"CANCELLED"}
        if not self.filepath:
            self.report({"ERROR"}, "No STL file was selected.")
            return {"CANCELLED"}

        previous_object = scene_utils.get_role_object(state, self.role)
        if previous_object is not None and not self.replace_existing:
            self.report({"ERROR"}, "This role already has a scan. Use Replace instead.")
            return {"CANCELLED"}

        selected_before, active_before = _capture_selection(context)
        objects_before = scene_utils.object_set_by_pointer()

        try:
            result = bpy.ops.wm.stl_import(
                filepath=self.filepath,
                global_scale=properties.source_unit_scale(state.source_unit),
                use_scene_unit=False,
                use_facet_normal=False,
                use_mesh_validate=True,
                forward_axis="Y",
                up_axis="Z",
            )
        except Exception as exc:
            _restore_selection(context, selected_before, active_before)
            self.report({"ERROR"}, f"STL import failed: {exc}")
            return {"CANCELLED"}

        objects_after = scene_utils.object_set_by_pointer()
        imported_objects = [
            obj for pointer, obj in objects_after.items() if pointer not in objects_before
        ]

        if "FINISHED" not in result:
            _cleanup_objects(imported_objects)
            _restore_selection(context, selected_before, active_before)
            self.report({"ERROR"}, "Blender cancelled the STL import.")
            return {"CANCELLED"}

        if len(imported_objects) != 1 or imported_objects[0].type != "MESH":
            _cleanup_objects(imported_objects)
            _restore_selection(context, selected_before, active_before)
            self.report(
                {"ERROR"},
                "The STL import must create exactly one mesh object for this role.",
            )
            return {"CANCELLED"}

        imported_object = imported_objects[0]
        basic_result = validation.validate_scan_object(
            imported_object,
            self.role,
            require_metadata=False,
            include_warnings=False,
        )
        if not basic_result.ok:
            _cleanup_objects(imported_objects)
            _restore_selection(context, selected_before, active_before)
            self.report({"ERROR"}, basic_result.errors[0])
            return {"CANCELLED"}

        try:
            imported_object.name = f"{properties.role_object_name(self.role)}_Incoming"
            scene_utils.move_object_to_scan_collection(imported_object, context.scene)
            scene_utils.tag_managed_scan(imported_object, self.role, self.filepath)
            scene_utils.set_role_object(state, self.role, imported_object)
        except Exception as exc:
            if scene_utils.object_is_alive(previous_object):
                scene_utils.set_role_object(state, self.role, previous_object)
            else:
                scene_utils.set_role_object(state, self.role, None)
            scene_utils.remove_object(imported_object)
            _restore_selection(context, selected_before, active_before)
            self.report({"ERROR"}, f"Could not assign the imported scan: {exc}")
            return {"CANCELLED"}

        old_scan_removed = True
        if (
            previous_object is not None
            and previous_object is not imported_object
            and scene_utils.is_managed_for_role(previous_object, self.role)
        ):
            old_scan_removed = scene_utils.remove_object(previous_object)

        imported_object.name = properties.role_object_name(self.role)
        properties.invalidate_step_one(state)

        try:
            _select_only(context, imported_object)
        except (ReferenceError, RuntimeError):
            _restore_selection(context, selected_before, active_before)

        action = "Replaced" if previous_object is not None else "Imported"
        if previous_object is not None and not old_scan_removed:
            self.report(
                {"WARNING"},
                "Replacement succeeded, but the previous managed object could not be removed.",
            )
        self.report(
            {"INFO"},
            f"{action} {properties.role_label(self.role)} scan successfully.",
        )
        return {"FINISHED"}


class BDENTAL_OT_focus_scan(bpy.types.Operator):
    """Select, activate, and frame a scan when a 3D Viewport is available."""

    bl_idname = "bdental.focus_scan"
    bl_label = "Focus Scan"
    bl_options = {"REGISTER"}

    role: EnumProperty(name="Dental Role", items=properties.SCAN_ROLE_ITEMS)

    def execute(self, context: bpy.types.Context):
        obj = scene_utils.get_role_object(_workflow_state(context), self.role)
        if obj is None:
            self.report({"ERROR"}, f"{properties.role_label(self.role)} scan is missing.")
            return {"CANCELLED"}

        try:
            _select_only(context, obj)
        except (ReferenceError, RuntimeError) as exc:
            self.report({"ERROR"}, f"Could not select the scan: {exc}")
            return {"CANCELLED"}

        if not _frame_selected_in_viewport(context):
            self.report({"WARNING"}, "Scan selected, but no 3D Viewport could be framed.")
        return {"FINISHED"}


class BDENTAL_OT_toggle_scan_visibility(bpy.types.Operator):
    """Toggle persistent viewport visibility for a scan slot."""

    bl_idname = "bdental.toggle_scan_visibility"
    bl_label = "Toggle Scan Visibility"
    bl_options = {"REGISTER", "UNDO"}

    role: EnumProperty(name="Dental Role", items=properties.SCAN_ROLE_ITEMS)

    def execute(self, context: bpy.types.Context):
        obj = scene_utils.get_role_object(_workflow_state(context), self.role)
        if obj is None:
            self.report({"ERROR"}, f"{properties.role_label(self.role)} scan is missing.")
            return {"CANCELLED"}

        obj.hide_viewport = not obj.hide_viewport
        return {"FINISHED"}


class BDENTAL_OT_remove_scan(bpy.types.Operator):
    """Clear a role assignment and remove its managed object."""

    bl_idname = "bdental.remove_scan"
    bl_label = "Remove Scan"
    bl_description = "Remove the managed scan from this role"
    bl_options = {"REGISTER", "UNDO"}

    role: EnumProperty(name="Dental Role", items=properties.SCAN_ROLE_ITEMS)

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        state = _workflow_state(context)
        if scene_utils.get_role_object(state, self.role) is None:
            self.report({"ERROR"}, f"{properties.role_label(self.role)} scan is missing.")
            return {"CANCELLED"}
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: bpy.types.Context):
        state = _workflow_state(context)
        obj = scene_utils.get_role_object(state, self.role)
        if obj is None:
            scene_utils.set_role_object(state, self.role, None)
            properties.invalidate_step_one(state)
            self.report({"WARNING"}, "The stale scan assignment was cleared.")
            return {"FINISHED"}

        scene_utils.set_role_object(state, self.role, None)
        removed = False
        if scene_utils.is_managed_for_role(obj, self.role):
            removed = scene_utils.remove_object(obj)

        properties.invalidate_step_one(state)
        message = "Scan removed." if removed else "Assignment cleared; unrelated object preserved."
        self.report({"INFO"}, message)
        return {"FINISHED"}


class BDENTAL_OT_validate_step_one(bpy.types.Operator):
    """Validate Step 1 and advance only when the dental result is valid."""

    bl_idname = "bdental.validate_step_one"
    bl_label = "Validate & Continue"
    bl_description = "Validate required scan roles and continue to Step 2 on success"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context):
        state = _workflow_state(context)
        result = validation.validate_step_one(state)

        state.internal_update_lock = True
        try:
            state.validation_errors = "\n".join(result.errors)
            state.validation_warnings = "\n".join(result.warnings)
            if result.ok:
                state.step_1_valid = True
                state.step_1_status = "VALID"
                state.current_step = "STEP_2"
                if result.warnings:
                    state.validation_summary = (
                        f"Step 1 is valid with {len(result.warnings)} warning(s)."
                    )
                else:
                    state.validation_summary = "Step 1 is valid."
            else:
                state.step_1_valid = False
                state.step_1_status = "ERROR"
                state.current_step = "STEP_1"
                state.validation_summary = f"{len(result.errors)} blocking error(s)."
        finally:
            state.internal_update_lock = False

        if result.ok:
            self.report({"INFO"}, state.validation_summary)
        else:
            self.report({"ERROR"}, result.errors[0])

        return {"FINISHED"}


class BDENTAL_OT_back_to_step_one(bpy.types.Operator):
    """Return to Step 1 without clearing scans or validation state."""

    bl_idname = "bdental.back_to_step_one"
    bl_label = "Back to Step 1"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context):
        state = _workflow_state(context)
        state.current_step = "STEP_1"
        return {"FINISHED"}


CLASSES = (
    BDENTAL_OT_start_case,
    BDENTAL_OT_import_scan,
    BDENTAL_OT_focus_scan,
    BDENTAL_OT_toggle_scan_visibility,
    BDENTAL_OT_remove_scan,
    BDENTAL_OT_validate_step_one,
    BDENTAL_OT_back_to_step_one,
)
