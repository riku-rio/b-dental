"""B-Dental Blender extension registration entry point."""

import bpy
from bpy.props import PointerProperty

from . import operators, properties, step_two_operators, ui

CLASSES = properties.CLASSES + operators.CLASSES + step_two_operators.CLASSES + ui.CLASSES


def register() -> None:
    """Register B-Dental classes and scene-persistent workflow state."""

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bdental_workflow = PointerProperty(
        type=properties.BDENTAL_PG_WorkflowState
    )


def unregister() -> None:
    """Remove scene state and unregister B-Dental classes in reverse order."""

    if hasattr(bpy.types.Scene, "bdental_workflow"):
        del bpy.types.Scene.bdental_workflow

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
