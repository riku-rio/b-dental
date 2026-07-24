"""Managed Step 5 artifact display configuration."""

from __future__ import annotations

import bpy

PREPARATION_DIE_COLOR = (0.20, 0.55, 1.00, 1.0)
BLOCKED_DIE_COLOR = (1.00, 0.55, 0.10, 1.0)
CANDIDATE_COLOR = (0.15, 0.85, 0.45, 1.0)
REJECTED_COLOR = (1.00, 0.15, 0.10, 1.0)
APPROVED_COLOR = (0.25, 1.00, 0.25, 1.0)


def color_for(artifact_type: str, status: str = "") -> tuple[float, float, float, float]:
    if status == "APPROVED":
        return APPROVED_COLOR
    if status == "REJECTED":
        return REJECTED_COLOR
    if artifact_type == "PREPARATION_DIE":
        return PREPARATION_DIE_COLOR
    if artifact_type == "BLOCKED_DIE":
        return BLOCKED_DIE_COLOR
    return CANDIDATE_COLOR


def configure_object(obj: bpy.types.Object, artifact_type: str, *, status: str = "") -> None:
    obj.color = color_for(artifact_type, status)
    obj.display_type = "SOLID"
    obj.show_in_front = artifact_type in {"PREPARATION_DIE", "BLOCKED_DIE"}
    obj.hide_render = True
    obj.hide_viewport = False
    if obj.type == "MESH" and obj.data is not None:
        for polygon in obj.data.polygons:
            polygon.use_smooth = artifact_type == "CROWN_BOTTOM"


def set_candidate_status(obj: bpy.types.Object, status: str) -> None:
    configure_object(obj, "CROWN_BOTTOM", status=status)
