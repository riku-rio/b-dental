"""Workflow-aware 3D Viewport sidebar interface for B-Dental."""

import textwrap

import bpy

from . import properties, scene_utils

_WRAP_WIDTH = 38


def _draw_wrapped_label(
    layout: bpy.types.UILayout,
    text: str,
    *,
    icon: str = "NONE",
) -> None:
    first = True
    for line in textwrap.wrap(text, width=_WRAP_WIDTH) or [""]:
        layout.label(text=line, icon=icon if first else "NONE")
        first = False


def _draw_messages(
    layout: bpy.types.UILayout,
    messages: str,
    *,
    title: str,
    icon: str,
) -> None:
    items = [message.strip() for message in messages.splitlines() if message.strip()]
    if not items:
        return

    box = layout.box()
    box.label(text=title, icon=icon)
    for message in items:
        _draw_wrapped_label(box, message)


def _object_summary(obj: bpy.types.Object) -> str:
    source_name = scene_utils.scan_source_name(obj)
    return source_name or obj.name


def _draw_scan_slot(
    layout: bpy.types.UILayout,
    state: bpy.types.PropertyGroup,
    role: str,
) -> None:
    box = layout.box()
    header = box.row(align=True)
    header.label(text=properties.role_label(role), icon="MESH_DATA")
    header.label(text="Required")

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

    visibility_icon = "HIDE_ON" if obj.hide_viewport else "HIDE_OFF"
    visibility_text = "Show" if obj.hide_viewport else "Hide"
    visibility = box.operator(
        "bdental.toggle_scan_visibility",
        text=visibility_text,
        icon=visibility_icon,
    )
    visibility.role = role


def _draw_step_one(layout: bpy.types.UILayout, state: bpy.types.PropertyGroup) -> None:
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

    ready = all(scene_utils.get_role_object(state, role) is not None for role in required)
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


def _draw_step_two(layout: bpy.types.UILayout, state: bpy.types.PropertyGroup) -> None:
    del state
    box = layout.box()
    box.label(text="Step 1 Complete", icon="CHECKMARK")
    box.label(text="Step 2 of 2")
    box.separator()
    box.label(text="Not Implemented Yet.", icon="INFO")
    layout.operator("bdental.back_to_step_one", text="Back to Step 1", icon="BACK")


class BDENTAL_PT_workflow(bpy.types.Panel):
    """Display the current B-Dental workflow step."""

    bl_idname = "BDENTAL_PT_workflow"
    bl_label = "B-Dental"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "B-Dental"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        state = context.scene.bdental_workflow

        if state.current_step == "STEP_2" and state.step_1_valid:
            _draw_step_two(layout, state)
        else:
            _draw_step_one(layout, state)


CLASSES = (BDENTAL_PT_workflow,)
