"""B-Dental Blender extension registration entry point."""

import bpy
from bpy.props import PointerProperty

from . import operators, properties, scene_utils, step_two_operators, step_two_session, ui

CLASSES = properties.CLASSES + operators.CLASSES + step_two_operators.CLASSES + ui.CLASSES

_ORIGINAL_RESET_WORKFLOW_STATE = scene_utils.reset_workflow_state


def _reset_workflow_state_with_step_two(state) -> None:
    """Reset the existing Step 1 state and all dependent Step 2 state."""

    _ORIGINAL_RESET_WORKFLOW_STATE(state)
    state.internal_update_lock = True
    try:
        properties.clear_step_two_state(state)
    finally:
        state.internal_update_lock = False


scene_utils.reset_workflow_state = _reset_workflow_state_with_step_two
scene_utils.matrix_from_string = step_two_session.matrix_from_string


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
