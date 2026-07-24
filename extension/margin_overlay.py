"""Always-visible 3D Viewport overlay for managed B-Dental margins."""

from __future__ import annotations

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from . import margin_geometry, restoration_utils

_DRAW_HANDLER_KEY = "BDENTAL_MARGIN_OVERLAY_DRAW_HANDLER"

_OUTLINE_COLOR = (0.0, 0.0, 0.0, 0.95)
_CANDIDATE_COLOR = (0.0, 0.95, 1.0, 1.0)
_VERIFIED_COLOR = (0.15, 1.0, 0.25, 1.0)
_ERROR_COLOR = (1.0, 0.15, 0.1, 1.0)
_OUTLINE_WIDTH = 7.0
_LINE_WIDTH = 4.0


def _line_color(restoration) -> tuple[float, float, float, float]:
    if restoration.valid and restoration.status == "VERIFIED":
        return _VERIFIED_COLOR
    if restoration.status in {"ERROR", "UPSTREAM_INVALID"}:
        return _ERROR_COLOR
    return _CANDIDATE_COLOR


def _segment_vertices(obj: bpy.types.Object) -> tuple[tuple[float, float, float], ...]:
    points = margin_geometry.curve_points(obj)
    if len(points) < 2:
        return ()

    world_points = tuple(obj.matrix_world @ point for point in points)
    vertices = []
    for start, end in zip(world_points, world_points[1:]):
        vertices.extend((tuple(start), tuple(end)))

    if margin_geometry.curve_is_cyclic(obj) and len(world_points) > 2:
        vertices.extend((tuple(world_points[-1]), tuple(world_points[0])))

    return tuple(vertices)


def _draw_segments(
    vertices: tuple[tuple[float, float, float], ...],
    color: tuple[float, float, float, float],
    width: float,
    viewport_size: tuple[float, float],
) -> None:
    shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
    batch = batch_for_shader(shader, "LINES", {"pos": vertices})
    shader.bind()
    shader.uniform_float("viewportSize", viewport_size)
    shader.uniform_float("lineWidth", width)
    shader.uniform_float("color", color)
    batch.draw(shader)


def _draw_margin_overlay() -> None:
    context = bpy.context
    scene = context.scene
    region = context.region

    if (
        scene is None
        or region is None
        or not hasattr(scene, "bdental_workflow")
    ):
        return

    state = scene.bdental_workflow
    if state.current_step != "STEP_3":
        return

    draw_items = []
    for restoration in state.restorations:
        margin = restoration_utils.resolve_margin(restoration)
        if margin is None or margin.hide_viewport:
            continue
        try:
            if not margin.visible_get(view_layer=context.view_layer, viewport=context.space_data):
                continue
        except (AttributeError, ReferenceError, RuntimeError, TypeError):
            pass

        vertices = _segment_vertices(margin)
        if vertices:
            draw_items.append((vertices, _line_color(restoration)))

    if not draw_items:
        return

    viewport_size = (float(region.width), float(region.height))

    try:
        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("NONE")

        for vertices, _color in draw_items:
            _draw_segments(vertices, _OUTLINE_COLOR, _OUTLINE_WIDTH, viewport_size)
        for vertices, color in draw_items:
            _draw_segments(vertices, color, _LINE_WIDTH, viewport_size)
    finally:
        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.blend_set("NONE")


def tag_redraw() -> None:
    window_manager = bpy.context.window_manager
    if window_manager is None:
        return
    for window in window_manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def register() -> None:
    unregister()
    handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_margin_overlay,
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
