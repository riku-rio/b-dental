"""B-Dental Blender extension registration entry point."""

import bpy
from bpy.app.handlers import persistent
from bpy.props import PointerProperty

from . import (
    margin_geometry,
    margin_validation,
    operators,
    properties,
    restoration_utils,
    scene_utils,
    step_three_operators,
    step_three_session,
    step_two_operators,
    step_two_session,
    ui,
)

CLASSES = (
    properties.CLASSES
    + operators.CLASSES
    + step_two_operators.CLASSES
    + step_three_operators.CLASSES
    + ui.CLASSES
)

if not hasattr(scene_utils, "_bdental_original_reset_workflow_state"):
    scene_utils._bdental_original_reset_workflow_state = scene_utils.reset_workflow_state
if not hasattr(scene_utils, "_bdental_original_remove_managed_case_scans"):
    scene_utils._bdental_original_remove_managed_case_scans = scene_utils.remove_managed_case_scans
if not hasattr(scene_utils, "_bdental_original_has_destructive_reset_content"):
    scene_utils._bdental_original_has_destructive_reset_content = scene_utils.has_destructive_reset_content


def _reset_workflow_state_with_dependencies(state) -> None:
    """Reset Step 1 and explicitly clear all dependent workflow state."""

    scene_utils._bdental_original_reset_workflow_state(state)
    state.internal_update_lock = True
    try:
        properties.clear_step_two_state(state)
        properties.clear_step_three_state(state)
    finally:
        state.internal_update_lock = False


def _remove_managed_case_content(scene, state) -> int:
    removed_scans = scene_utils._bdental_original_remove_managed_case_scans(scene, state)
    restoration_utils.remove_all_managed_restoration_artifacts(scene, state)
    return removed_scans


def _has_destructive_case_content(scene, state) -> bool:
    return bool(
        scene_utils._bdental_original_has_destructive_reset_content(scene, state)
        or restoration_utils.has_managed_restoration_artifacts(scene, state)
    )


scene_utils.reset_workflow_state = _reset_workflow_state_with_dependencies
scene_utils.remove_managed_case_scans = _remove_managed_case_content
scene_utils.has_destructive_reset_content = _has_destructive_case_content
scene_utils.matrix_from_string = step_two_session.matrix_from_string


@persistent
def _monitor_step_three_dependencies(scene, _depsgraph) -> None:
    step_three_session.monitor_scene(scene)


def register() -> None:
    """Register B-Dental classes and scene-persistent workflow state."""

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bdental_workflow = PointerProperty(
        type=properties.BDENTAL_PG_WorkflowState
    )
    if _monitor_step_three_dependencies not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_monitor_step_three_dependencies)


def unregister() -> None:
    """Remove scene state and unregister B-Dental classes in reverse order."""

    if _monitor_step_three_dependencies in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_monitor_step_three_dependencies)

    if hasattr(bpy.types.Scene, "bdental_workflow"):
        del bpy.types.Scene.bdental_workflow

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
