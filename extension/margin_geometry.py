"""Manual-margin geometry helpers for B-Dental Step 3."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Sequence

import bpy
from bpy_extras import view3d_utils
from mathutils import Matrix, Vector

from . import restoration_utils, scene_utils

MIN_MARGIN_POINTS = 6
RECOMMENDED_MARGIN_POINTS = 12
POINT_EPSILON = 1.0e-7
SURFACE_WARNING_DISTANCE = 0.00025
SURFACE_BLOCKING_DISTANCE = 0.001
MIN_PATH_LENGTH = 0.002
SELF_PROXIMITY_DISTANCE = 0.0002


def serialize_points(points: Iterable[Vector | Sequence[float]]) -> str:
    payload = [[float(value) for value in point[:3]] for point in points]
    return json.dumps(payload, separators=(",", ":"))


def deserialize_points(value: str) -> tuple[Vector, ...]:
    if not value:
        return ()
    try:
        payload = json.loads(value)
        return tuple(
            Vector((float(item[0]), float(item[1]), float(item[2])))
            for item in payload
        )
    except (TypeError, ValueError, IndexError, json.JSONDecodeError):
        return ()


def curve_points(obj: bpy.types.Object | None) -> tuple[Vector, ...]:
    if not scene_utils.object_is_alive(obj) or obj.type != "CURVE" or obj.data is None:
        return ()
    if len(obj.data.splines) != 1 or obj.data.splines[0].type != "POLY":
        return ()
    return tuple(Vector(point.co[:3]) for point in obj.data.splines[0].points)


def curve_is_cyclic(obj: bpy.types.Object | None) -> bool:
    return bool(
        scene_utils.object_is_alive(obj)
        and obj.type == "CURVE"
        and obj.data is not None
        and len(obj.data.splines) == 1
        and obj.data.splines[0].type == "POLY"
        and obj.data.splines[0].use_cyclic_u
    )


def replace_curve_points(
    obj: bpy.types.Object,
    points: Iterable[Vector | Sequence[float]],
    *,
    cyclic: bool,
) -> None:
    if obj.type != "CURVE" or obj.data is None:
        raise ValueError("Margin object must be a Curve.")
    values = tuple(Vector(point[:3]) for point in points)
    obj.data.dimensions = "3D"
    obj.data.resolution_u = 1
    obj.data.splines.clear()
    if not values:
        return
    spline = obj.data.splines.new("POLY")
    spline.points.add(len(values) - 1)
    for spline_point, value in zip(spline.points, values):
        spline_point.co = (*value, 1.0)
    spline.use_cyclic_u = bool(cyclic)


def ensure_margin_object(scene: bpy.types.Scene, state, restoration) -> bpy.types.Object:
    target = restoration_utils.target_scan(state, restoration)
    if target is None:
        raise ValueError("The target preparation scan is unavailable.")

    obj = restoration_utils.resolve_margin(restoration)
    if obj is None:
        curve = bpy.data.curves.new(
            f"BDENTAL_Margin_{restoration.target_tooth_fdi}_{restoration.restoration_id[:8]}_Curve",
            type="CURVE",
        )
        curve.dimensions = "3D"
        curve.resolution_u = 1
        curve.bevel_depth = 0.00015
        curve.bevel_resolution = 2
        obj = bpy.data.objects.new(
            f"BDENTAL_Margin_{restoration.target_tooth_fdi}_{restoration.restoration_id[:8]}",
            curve,
        )
        restoration_utils.move_to_restoration_collection(obj, scene)
        restoration.margin_object = obj

    obj.parent = target
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = Matrix.Identity(4)
    obj.hide_viewport = False
    restoration_utils.tag_margin(obj, restoration)
    return obj


def append_curve_point(obj: bpy.types.Object, point: Vector) -> None:
    replace_curve_points(obj, (*curve_points(obj), point.copy()), cyclic=False)


def remove_last_curve_point(obj: bpy.types.Object) -> bool:
    points = curve_points(obj)
    if not points:
        return False
    replace_curve_points(obj, points[:-1], cyclic=False)
    return True


def finite_point(point: Vector) -> bool:
    return all(math.isfinite(float(value)) for value in point)


def unique_point_count(points: Sequence[Vector], tolerance: float = POINT_EPSILON) -> int:
    unique: list[Vector] = []
    for point in points:
        if not any((point - existing).length <= tolerance for existing in unique):
            unique.append(point)
    return len(unique)


def path_length(points: Sequence[Vector], *, cyclic: bool = True) -> float:
    if len(points) < 2:
        return 0.0
    total = sum((right - left).length for left, right in zip(points, points[1:]))
    if cyclic and len(points) > 2:
        total += (points[0] - points[-1]).length
    return float(total)


def segment_lengths(points: Sequence[Vector], *, cyclic: bool = True) -> tuple[float, ...]:
    if len(points) < 2:
        return ()
    lengths = [(right - left).length for left, right in zip(points, points[1:])]
    if cyclic and len(points) > 2:
        lengths.append((points[0] - points[-1]).length)
    return tuple(float(value) for value in lengths)


def spacing_ratio(points: Sequence[Vector]) -> float:
    lengths = tuple(value for value in segment_lengths(points) if value > POINT_EPSILON)
    if len(lengths) < 2:
        return 1.0
    return max(lengths) / max(min(lengths), POINT_EPSILON)


def _point_segment_distance(point: Vector, start: Vector, end: Vector) -> float:
    direction = end - start
    denominator = direction.length_squared
    if denominator <= POINT_EPSILON:
        return (point - start).length
    factor = max(0.0, min(1.0, (point - start).dot(direction) / denominator))
    return (point - (start + factor * direction)).length


def approximate_non_adjacent_proximity(points: Sequence[Vector]) -> float | None:
    if len(points) < 4:
        return None
    segments = [(points[index], points[(index + 1) % len(points)]) for index in range(len(points))]
    best: float | None = None
    for left_index, (left_start, left_end) in enumerate(segments):
        for right_index, (right_start, right_end) in enumerate(segments):
            if right_index <= left_index:
                continue
            if right_index in {left_index - 1, left_index, left_index + 1}:
                continue
            if {left_index, right_index} == {0, len(segments) - 1}:
                continue
            distance = min(
                _point_segment_distance(left_start, right_start, right_end),
                _point_segment_distance(left_end, right_start, right_end),
                _point_segment_distance(right_start, left_start, left_end),
                _point_segment_distance(right_end, left_start, left_end),
            )
            best = distance if best is None else min(best, distance)
    return best


def point_surface_distances(
    target: bpy.types.Object,
    points: Sequence[Vector],
    depsgraph: bpy.types.Depsgraph,
) -> tuple[float, ...]:
    distances = []
    for point in points:
        result, location, _normal, _index = target.closest_point_on_mesh(
            point,
            distance=1000.0,
            depsgraph=depsgraph,
        )
        distances.append((point - location).length if result else float("inf"))
    return tuple(float(value) for value in distances)


def reproject_points(
    target: bpy.types.Object,
    points: Sequence[Vector],
    depsgraph: bpy.types.Depsgraph,
) -> tuple[Vector, ...]:
    projected = []
    for point in points:
        result, location, _normal, _index = target.closest_point_on_mesh(
            point,
            distance=1000.0,
            depsgraph=depsgraph,
        )
        if not result:
            raise ValueError("At least one margin point could not be projected to the target scan.")
        projected.append(location.copy())
    return tuple(projected)


def raycast_target(context, event, target: bpy.types.Object) -> Vector | None:
    region = context.region
    region_data = context.region_data
    if region is None or region_data is None or context.area is None or context.area.type != "VIEW_3D":
        return None

    coordinate = (event.mouse_region_x, event.mouse_region_y)
    origin_world = view3d_utils.region_2d_to_origin_3d(region, region_data, coordinate)
    direction_world = view3d_utils.region_2d_to_vector_3d(region, region_data, coordinate).normalized()
    inverse = target.matrix_world.inverted_safe()
    origin_local = inverse @ origin_world
    direction_local = (inverse.to_3x3() @ direction_world).normalized()
    result, location, _normal, _index = target.ray_cast(
        origin_local,
        direction_local,
        distance=1000.0,
        depsgraph=context.evaluated_depsgraph_get(),
    )
    return location.copy() if result else None
