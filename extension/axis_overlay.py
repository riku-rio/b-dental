"""Lifecycle-safe viewport overlay for B-Dental Step 4."""

from __future__ import annotations

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from . import axis_geometry, preparation_analysis, restoration_utils

_DRAW_HANDLER_KEY = "BDENTAL_STEP_FOUR_OVERLAY_DRAW_HANDLER"
_CLEAR_COLOR = (0.15, 0.85, 1.0, 0.9)
_UNDERCUT_COLOR = (1.0, 0.15, 0.05, 0.95)
_AXIS_CANDIDATE_COLOR = (0.0, 0.9, 1.0, 1.0)
_AXIS_VERIFIED_COLOR = (0.15, 1.0, 0.25, 1.0)
_POINT_SIZE = 5.0
_AXIS_WIDTH = 4.0


def _world_samples(state, restoration):
    target = restoration_utils.target_scan(state, restoration)
    if target is None:
        return (), ()
    clear_points = []
    undercut_points = []
    for sample in preparation_analysis.deserialize_samples(restoration.analysis_samples):
        point = target.matrix_world @ Vector(sample.location)
        if sample.blocked:
            undercut_points.append(tuple(point))
        else:
            clear_points.append(tuple(point))
    return tuple(clear_points), tuple(undercut_points)


def _draw_points(vertices, color) -> None:
    if not vertices:
        return
    shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    batch = batch_for_shader(shader, "POINTS", {"pos": vertices})
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)


def _draw_axis(state, restoration, viewport_size) -> None:
    origin, direction = axis_geometry.axis_world_origin_and_direction(state, restoration)
    if origin is None or direction is None:
        return
    length = max(
        axis_geometry.MIN_AXIS_DISPLAY_SIZE,
        min(axis_geometry.MAX_AXIS_DISPLAY_SIZE, float(restoration.analysis_radius)),
    )
    vertices = (tuple(origin), tuple(origin + direction * length))
    shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": vertices})
    shader.bind()
    shader.uniform_float("viewportSize", viewport_size)
    shader.uniform_float("lineWidth", _AXIS_WIDTH)
    shader.uniform_float(
        "color",
        _AXIS_VERIFIED_COLOR if restoration.step_4_valid else _AXIS_CANDIDATE_COLOR,
    )
    batch.draw(shader)


def _draw_overlay() -> None:
    context = bpy.context
    scene = context.scene
    region = context.region
    if scene is None or region is None or not hasattr(scene, "bdental_workflow"):
        return
    state = scene.bdental_workflow
    if state.current_step != "STEP_4":
        return
    restoration = restoration_utils.active_restoration(state)
    if restoration is None:
        return

    viewport_size = (float(region.width), float(region.height))
    clear_points, undercut_points = _world_samples(state, restoration)
    try:
        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.point_size_set(_POINT_SIZE)
        _draw_axis(state, restoration, viewport_size)
        if restoration.analysis_overlay_visible and restoration.analysis_current:
            _draw_points(clear_points, _CLEAR_COLOR)
            _draw_points(undercut_points, _UNDERCUT_COLOR)
    finally:
        gpu.state.point_size_set(1.0)
        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.blend_set("NONE")


def tag_redraw() -> None:
    manager = bpy.context.window_manager
    if manager is None:
        return
    for window in manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def register() -> None:
    unregister()
    handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_overlay,
        (),
        "WINDOW",
        "POST_VIEW",
    )
    bpy.app.driver_namespace[_DRAW_HANDLER_KEY] = handle
    tag_redraw()


def unregister() -> None:
    handle = bpy.app.driver_namespace.pop(_DRAW_HANDLER_KEY, None)
    if handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(handle, "WINDOW")
        except (ReferenceError, RuntimeError, ValueError):
            pass
    tag_redraw()
