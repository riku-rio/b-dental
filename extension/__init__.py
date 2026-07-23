"""B-Dental Blender extension foundation."""

import bpy


class BDENTAL_PT_foundation(bpy.types.Panel):
    """Display the initial B-Dental placeholder interface."""

    bl_idname = "BDENTAL_PT_foundation"
    bl_label = "B-Dental"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "B-Dental"

    def draw(self, context: bpy.types.Context) -> None:
        del context
        self.layout.label(text="Not Implemented Yet.")


CLASSES = (
    BDENTAL_PT_foundation,
)


def register() -> None:
    """Register B-Dental classes with Blender."""

    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister B-Dental classes from Blender."""

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
