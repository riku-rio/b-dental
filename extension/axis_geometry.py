"""Insertion-axis geometry and managed-artifact helpers for B-Dental Step 4."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Sequence

import bpy
from mathutils import Matrix, Vector

from . import margin_geometry, restoration_utils, scene_utils

AXIS_ARTIFACT_TYPE = "INSERTION_AXIS"
AXIS_SCHEMA_VERSION = 1
AXIS_VECTOR_EPSILON = 1.0e-9
AXIS_ORIENTATION_TOLERANCE_DEGREES = 0.5
MIN_AXIS_DISPLAY_SIZE = 0.004
MAX_AXIS_DISPLAY_SIZE = 0.012
CANDIDATE_COLOR = (0.0, 0.8, 1.0, 1.0)
VERIFIED_COLOR = (0.15, 1.0, 0.25, 1.0)
ERROR_COLOR = (1.0, 0.15, 0.1, 1.0)


def finite_vector(value: Vector | Sequence[float] | None) -> bool:
    if value is None:
        return False
    try:
        return len(value) >= 3 and all(math.isfinite(float(component)) for component in value[:3])
    except (TypeError, ValueError, IndexError):
        return False


def normalized_vector(value: Vector | Sequence[float] | None) -> Vector | None:
    if not finite_vector(value):
        return None
    vector = Vector((float(value[0]), float(value[1]), float(value[2])))
    if vector.length <= AXIS_VECTOR_EPSILON:
        return None
    vector.normalize()
    return vector if finite_vector(vector) else None


def serialize_vector(value: Vector | Sequence[float] | None) -> str:
    vector = normalized_vector(value)
    if vector is None:
        return ""
    return json.dumps([float(component) for component in vector], separators=(",", ":"))


def deserialize_vector(value: str) -> Vector | None:
    if not value:
        return None
    try:
        payload = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return normalized_vector(payload)


def serialize_matrix(matrix: Matrix | None) -> str:
    if matrix is None:
        return ""
    payload = [float(matrix[row][column]) for row in range(4) for column in range(4)]
    if not all(math.isfinite(value) for value in payload):
        return ""
    return json.dumps(payload, separators=(",", ":"))


def deserialize_matrix(value: str) -> Matrix | None:
    if not value:
        return None
    try:
        payload = [float(item) for item in json.loads(value)]
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if len(payload) != 16 or not all(math.isfinite(item) for item in payload):
        return None
    return Matrix((payload[0:4], payload[4:8], payload[8:12], payload[12:16]))


def target_local_to_world_direction(target: bpy.types.Object, value) -> Vector | None:
    vector = normalized_vector(value)
    if vector is None or not scene_utils.object_is_alive(target):
        return None
    return normalized_vector(target.matrix_world.to_quaternion() @ vector)


def world_to_target_local_direction(target: bpy.types.Object, value) -> Vector | None:
    vector = normalized_vector(value)
    if vector is None or not scene_utils.object_is_alive(target):
        return None
    return normalized_vector(target.matrix_world.to_quaternion().inverted() @ vector)


def current_view_forward_world(context: bpy.types.Context) -> Vector | None:
    region_data = getattr(context, "region_data", None)
    if region_data is None:
        return None
    return normalized_vector(region_data.view_rotation @ Vector((0.0, 0.0, -1.0)))


def margin_points_local(restoration) -> tuple[Vector, ...]:
    margin = restoration_utils.resolve_margin(restoration)
    if margin is None or not margin_geometry.curve_is_cyclic(margin):
        return ()
    return margin_geometry.curve_points(margin)


def margin_center_local(state, restoration, depsgraph=None) -> Vector | None:
    points = margin_points_local(restoration)
    if not points:
        return None
    center = sum(points, Vector()) / len(points)
    target = restoration_utils.target_scan(state, restoration)
    if target is None:
        return normalized_vector(center) if center.length > AXIS_VECTOR_EPSILON else center
    try:
        result, location, _normal, _index = target.closest_point_on_mesh(
            center,
            distance=1000.0,
            depsgraph=depsgraph,
        )
    except (AttributeError, RuntimeError, TypeError):
        result = False
        location = center
    return location.copy() if result else center


def margin_normal_local(restoration) -> Vector | None:
    points = margin_points_local(restoration)
    if len(points) < 3:
        return None

    normal = Vector((0.0, 0.0, 0.0))
    for current, following in zip(points, (*points[1:], points[0])):
        normal.x += (current.y - following.y) * (current.z + following.z)
        normal.y += (current.z - following.z) * (current.x + following.x)
        normal.z += (current.x - following.x) * (current.y + following.y)
    return normalized_vector(normal)


def margin_axis_suggestion(state, restoration, view_forward_world: Vector) -> Vector | None:
    target = restoration_utils.target_scan(state, restoration)
    normal_local = margin_normal_local(restoration)
    forward_world = normalized_vector(view_forward_world)
    if target is None or normal_local is None or forward_world is None:
        return None
    normal_world = target_local_to_world_direction(target, normal_local)
    if normal_world is None:
        return None
    return -normal_local if normal_world.dot(forward_world) < 0.0 else normal_local


def axis_object_name(restoration) -> str:
    return f"BDENTAL_Insertion_Axis_{restoration.target_tooth_fdi}_{restoration.restoration_id[:8]}"


def tag_axis(obj: bpy.types.Object, restoration) -> None:
    obj[scene_utils.META_MANAGED] = True
    obj[restoration_utils.META_ARTIFACT_TYPE] = AXIS_ARTIFACT_TYPE
    obj[restoration_utils.META_RESTORATION_ID] = restoration.restoration_id
    obj[restoration_utils.META_TARGET_ROLE] = restoration.target_arch
    obj[restoration_utils.META_TARGET_TOOTH] = restoration.target_tooth_fdi
    obj[restoration_utils.META_SCHEMA_VERSION] = restoration_utils.RESTORATION_SCHEMA_VERSION
    obj["bdental_axis_schema_version"] = AXIS_SCHEMA_VERSION


def is_managed_axis(obj: bpy.types.Object | None, restoration=None) -> bool:
    if not scene_utils.object_is_alive(obj):
        return False
    try:
        if obj.type != "EMPTY" or not bool(obj.get(scene_utils.META_MANAGED, False)):
            return False
        if obj.get(restoration_utils.META_ARTIFACT_TYPE) != AXIS_ARTIFACT_TYPE:
            return False
        if restoration is None:
            return True
        return (
            obj.get(restoration_utils.META_RESTORATION_ID) == restoration.restoration_id
            and obj.get(restoration_utils.META_TARGET_ROLE) == restoration.target_arch
            and obj.get(restoration_utils.META_TARGET_TOOTH) == restoration.target_tooth_fdi
        )
    except (AttributeError, ReferenceError, RuntimeError):
        return False


def find_axis_by_restoration_id(restoration_id: str):
    if not restoration_id:
        return None
    collection = bpy.data.collections.get(restoration_utils.RESTORATION_COLLECTION_NAME)
    if collection is None:
        return None
    for obj in collection.objects:
        if is_managed_axis(obj) and obj.get(restoration_utils.META_RESTORATION_ID) == restoration_id:
            return obj
    return None


def resolve_axis(restoration):
    if restoration is None:
        return None
    try:
        obj = restoration.axis_object
    except (AttributeError, ReferenceError, RuntimeError):
        obj = None
    if is_managed_axis(obj, restoration):
        return obj
    recovered = find_axis_by_restoration_id(restoration.restoration_id)
    if is_managed_axis(recovered, restoration):
        restoration.axis_object = recovered
        return recovered
    return None


def remove_axis_object(obj: bpy.types.Object | None) -> bool:
    if not scene_utils.object_is_alive(obj):
        return False
    bpy.data.objects.remove(obj, do_unlink=True)
    return True


def remove_restoration_axis(restoration) -> bool:
    obj = resolve_axis(restoration)
    removed = remove_axis_object(obj) if is_managed_axis(obj, restoration) else False
    restoration.axis_object = None
    return removed


def iter_managed_axes(scene: bpy.types.Scene) -> Iterable[bpy.types.Object]:
    collection = bpy.data.collections.get(restoration_utils.RESTORATION_COLLECTION_NAME)
    if collection is None:
        return
    for obj in list(collection.objects):
        if scene.objects.get(obj.name) is obj and is_managed_axis(obj):
            yield obj


def _axis_color(restoration) -> tuple[float, float, float, float]:
    if restoration.step_4_valid and restoration.step_4_status == "VERIFIED":
        return VERIFIED_COLOR
    if restoration.step_4_status in {"ERROR", "UPSTREAM_INVALID"}:
        return ERROR_COLOR
    return CANDIDATE_COLOR


def _axis_display_size(restoration) -> float:
    radius = float(getattr(restoration, "analysis_radius", 0.006))
    return max(MIN_AXIS_DISPLAY_SIZE, min(MAX_AXIS_DISPLAY_SIZE, radius * 0.8))


def orient_axis_object(obj: bpy.types.Object, axis_local) -> None:
    axis = normalized_vector(axis_local)
    if axis is None:
        raise ValueError("The insertion axis must be a finite non-zero vector.")
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = axis.to_track_quat("Z", "Y")


def ensure_axis_object(scene, state, restoration, depsgraph=None):
    target = restoration_utils.target_scan(state, restoration)
    axis = deserialize_vector(restoration.insertion_axis_local)
    center = margin_center_local(state, restoration, depsgraph)
    if target is None:
        raise ValueError("The preparation scan is unavailable.")
    if axis is None:
        raise ValueError("Define an insertion-axis candidate first.")
    if center is None:
        raise ValueError("The approved margin cannot provide an axis origin.")

    obj = resolve_axis(restoration)
    if obj is None:
        obj = bpy.data.objects.new(axis_object_name(restoration), None)
        restoration_utils.move_to_restoration_collection(obj, scene)
        restoration.axis_object = obj

    obj.name = axis_object_name(restoration)
    obj.parent = target
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = center
    obj.scale = (1.0, 1.0, 1.0)
    obj.empty_display_type = "SINGLE_ARROW"
    obj.empty_display_size = _axis_display_size(restoration)
    obj.color = _axis_color(restoration)
    obj.show_in_front = True
    obj.hide_render = True
    orient_axis_object(obj, axis)
    tag_axis(obj, restoration)
    return obj


def capture_axis_from_object(restoration) -> Vector | None:
    obj = resolve_axis(restoration)
    if obj is None:
        return None
    return normalized_vector(obj.matrix_basis.to_quaternion() @ Vector((0.0, 0.0, 1.0)))


def axis_object_matches(restoration, tolerance_degrees: float = AXIS_ORIENTATION_TOLERANCE_DEGREES) -> bool:
    stored = deserialize_vector(restoration.insertion_axis_local)
    captured = capture_axis_from_object(restoration)
    if stored is None or captured is None:
        return False
    dot = max(-1.0, min(1.0, stored.dot(captured)))
    return math.degrees(math.acos(dot)) <= tolerance_degrees


def axis_world_origin_and_direction(state, restoration):
    target = restoration_utils.target_scan(state, restoration)
    axis = deserialize_vector(restoration.insertion_axis_local)
    center = margin_center_local(state, restoration)
    if target is None or axis is None or center is None:
        return None, None
    return target.matrix_world @ center, target_local_to_world_direction(target, axis)
