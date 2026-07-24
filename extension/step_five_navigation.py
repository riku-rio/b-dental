"""Step 5 multi-restoration navigation and scoped cleanup integration."""

from __future__ import annotations

import bpy
from bpy.props import IntProperty

from . import (
    crown_bottom_candidates,
    restoration_utils,
    step_five_operators,
    step_five_session,
    step_four_operators,
    step_three_operators,
)


class BDENTAL_OT_select_step_five_restoration(bpy.types.Operator):
    bl_idname = "bdental.select_step_five_restoration"
    bl_label = "Select Step 5 Restoration"

    index: IntProperty(default=0, min=0)

    def execute(self, context):
        state = context.scene.bdental_workflow
        active = restoration_utils.active_restoration(state)
        if active is not None and active.step_5_correction_active:
            self.report({"ERROR"}, "Apply or cancel the active Step 5 correction session before switching.")
            return {"CANCELLED"}
        if self.index >= len(state.restorations):
            return {"CANCELLED"}
        state.active_restoration_index = self.index
        step_five_session.sync_step_five_state(state)
        return {"FINISHED"}


def _patch_step_five_draw() -> None:
    if hasattr(step_five_operators, "_bdental_step_five_navigation_original_draw"):
        return
    original = step_five_operators._draw_step_five
    step_five_operators._bdental_step_five_navigation_original_draw = original

    def draw(layout, state, context):
        box = layout.box()
        approved = sum(1 for restoration in state.restorations if restoration.step_5_valid)
        box.label(
            text=f"Restorations | Approved {approved} of {len(state.restorations)}",
            icon="OUTLINER_COLLECTION",
        )
        for index, restoration in enumerate(state.restorations):
            row = box.row(align=True)
            operator = row.operator(
                "bdental.select_step_five_restoration",
                text=f"FDI {restoration.target_tooth_fdi}",
                icon="CHECKMARK" if restoration.step_5_valid else "MESH_DATA",
                depress=index == state.active_restoration_index,
            )
            operator.index = index
            row.label(text=restoration.step_5_status.replace("_", " ").title())
        original(layout, state, context)

    step_five_operators._draw_step_five = draw


def _patch_upstream_selection() -> None:
    for operator in (
        step_three_operators.BDENTAL_OT_select_restoration,
        step_four_operators.BDENTAL_OT_select_step_four_restoration,
    ):
        if hasattr(operator, "_bdental_step_five_original_execute"):
            continue
        original = operator.execute
        operator._bdental_step_five_original_execute = original

        def execute(self, context, _original=original):
            active = restoration_utils.active_restoration(context.scene.bdental_workflow)
            if active is not None and getattr(active, "step_5_correction_active", False):
                self.report({"ERROR"}, "Apply or cancel the active Step 5 correction session before switching.")
                return {"CANCELLED"}
            return _original(self, context)

        operator.execute = execute


def _patch_restoration_removal() -> None:
    operator = step_three_operators.BDENTAL_OT_remove_restoration
    if hasattr(operator, "_bdental_step_five_cleanup_original_execute"):
        return
    original = operator.execute
    operator._bdental_step_five_cleanup_original_execute = original

    def execute(self, context):
        state = context.scene.bdental_workflow
        restoration = restoration_utils.active_restoration(state)
        if restoration is not None and restoration.step_5_correction_active:
            self.report({"ERROR"}, "Cancel the active Step 5 correction session before removing this restoration.")
            return {"CANCELLED"}
        artifacts = (
            list(crown_bottom_candidates.iter_managed_artifacts(context.scene, restoration))
            if restoration is not None
            else []
        )
        result = original(self, context)
        if result == {"FINISHED"}:
            for artifact in artifacts:
                crown_bottom_candidates.remove_artifact(artifact)
            step_five_session.sync_step_five_state(state)
        return result

    operator.execute = execute


CLASSES = (BDENTAL_OT_select_step_five_restoration,)

_patch_step_five_draw()
_patch_upstream_selection()
_patch_restoration_removal()
