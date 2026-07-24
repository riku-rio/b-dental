"""Shared deterministic mesh helpers for B-Dental Step 5."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Iterable, Sequence

from mathutils import Vector

GEOMETRY_POLICY_VERSION = 1
COORDINATE_QUANTIZATION = 1.0e-9
DEGENERATE_AREA_EPSILON = 1.0e-14


@dataclass(frozen=True)
class MeshGeometry:
    """World-space mesh geometry with an optional ordered margin boundary."""

    vertices: tuple[Vector, ...]
    faces: tuple[tuple[int, ...], ...]
    boundary_loop: tuple[int, ...] = ()
    surface_vertex_count: int = 0
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class TopologyMetrics:
    vertex_count: int
    edge_count: int
    face_count: int
    boundary_loop_count: int
    boundary_edge_count: int
    non_manifold_edge_count: int
    degenerate_face_count: int
    minimum_edge_length: float


def finite_vector(value: Vector | Sequence[float] | None) -> bool:
    if value is None:
        return False
    try:
        return len(value) >= 3 and all(math.isfinite(float(component)) for component in value[:3])
    except (TypeError, ValueError, IndexError):
        return False


def normalized(value: Vector | Sequence[float] | None) -> Vector | None:
    if not finite_vector(value):
        return None
    vector = Vector((float(value[0]), float(value[1]), float(value[2])))
    if vector.length <= 1.0e-12:
        return None
    vector.normalize()
    return vector


def orthonormal_basis(axis: Vector) -> tuple[Vector, Vector, Vector]:
    normal = normalized(axis)
    if normal is None:
        raise ValueError("A finite non-zero axis is required.")
    reference = Vector((1.0, 0.0, 0.0)) if abs(normal.x) < 0.8 else Vector((0.0, 1.0, 0.0))
    first = normal.cross(reference)
    if first.length <= 1.0e-12:
        reference = Vector((0.0, 0.0, 1.0))
        first = normal.cross(reference)
    first.normalize()
    second = normal.cross(first)
    second.normalize()
    return first, second, normal


def projected_coordinates(point: Vector, basis: tuple[Vector, Vector, Vector]) -> tuple[float, float, float]:
    first, second, axis = basis
    return float(point.dot(first)), float(point.dot(second)), float(point.dot(axis))


def polygon_signed_area(points: Sequence[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    return 0.5 * sum(
        left[0] * right[1] - right[0] * left[1]
        for left, right in zip(points, (*points[1:], points[0]))
    )


def point_in_polygon(point: tuple[float, float], polygon: Sequence[tuple[float, float]]) -> bool:
    if len(polygon) < 3:
        return False
    x_value, y_value = point
    inside = False
    previous = polygon[-1]
    for current in polygon:
        x_left, y_left = previous
        x_right, y_right = current
        intersects = (y_left > y_value) != (y_right > y_value)
        if intersects:
            denominator = y_right - y_left
            if abs(denominator) > 1.0e-15:
                x_crossing = (x_right - x_left) * (y_value - y_left) / denominator + x_left
                if x_value < x_crossing:
                    inside = not inside
        previous = current
    return inside


def nearest_point_on_polyline(point: Vector, polyline: Sequence[Vector]) -> tuple[Vector, float, int, float]:
    if len(polyline) < 2:
        raise ValueError("A closed polyline requires at least two points.")
    best_point = polyline[0].copy()
    best_distance = float("inf")
    best_index = 0
    best_factor = 0.0
    for index, start in enumerate(polyline):
        end = polyline[(index + 1) % len(polyline)]
        direction = end - start
        denominator = direction.length_squared
        factor = 0.0 if denominator <= 1.0e-20 else max(0.0, min(1.0, (point - start).dot(direction) / denominator))
        candidate = start + factor * direction
        distance = (point - candidate).length
        if distance < best_distance:
            best_point = candidate
            best_distance = distance
            best_index = index
            best_factor = factor
    return best_point, float(best_distance), best_index, float(best_factor)


def resample_closed_polyline(points: Sequence[Vector], count: int) -> tuple[Vector, ...]:
    if count < 3 or len(points) < 3:
        raise ValueError("A closed margin requires at least three samples.")
    lengths = []
    total = 0.0
    for start, end in zip(points, (*points[1:], points[0])):
        segment = (end - start).length
        lengths.append(segment)
        total += segment
    if total <= 1.0e-12:
        raise ValueError("The approved margin has no usable length.")

    result: list[Vector] = []
    segment_index = 0
    segment_start_distance = 0.0
    for sample_index in range(count):
        target_distance = total * sample_index / count
        while segment_index < len(lengths) - 1 and segment_start_distance + lengths[segment_index] < target_distance:
            segment_start_distance += lengths[segment_index]
            segment_index += 1
        start = points[segment_index]
        end = points[(segment_index + 1) % len(points)]
        segment_length = max(lengths[segment_index], 1.0e-12)
        factor = (target_distance - segment_start_distance) / segment_length
        result.append(start.lerp(end, max(0.0, min(1.0, factor))))
    return tuple(result)


def edge_use_counts(faces: Sequence[Sequence[int]]) -> dict[tuple[int, int], int]:
    counts: dict[tuple[int, int], int] = {}
    for face in faces:
        if len(face) < 3:
            continue
        for left, right in zip(face, (*face[1:], face[0])):
            edge = (left, right) if left < right else (right, left)
            counts[edge] = counts.get(edge, 0) + 1
    return counts


def ordered_boundary_loops(faces: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    counts = edge_use_counts(faces)
    boundary_edges = [edge for edge, use_count in counts.items() if use_count == 1]
    if not boundary_edges:
        return ()
    adjacency: dict[int, list[int]] = {}
    for left, right in boundary_edges:
        adjacency.setdefault(left, []).append(right)
        adjacency.setdefault(right, []).append(left)
    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        return ()

    remaining = {tuple(sorted(edge)) for edge in boundary_edges}
    loops: list[tuple[int, ...]] = []
    while remaining:
        start_edge = min(remaining)
        start, current = start_edge
        loop = [start]
        previous = start
        while True:
            loop.append(current)
            remaining.discard(tuple(sorted((previous, current))))
            neighbors = adjacency[current]
            next_vertex = neighbors[0] if neighbors[0] != previous else neighbors[1]
            previous, current = current, next_vertex
            if current == start:
                remaining.discard(tuple(sorted((previous, current))))
                break
            if len(loop) > len(boundary_edges) + 1:
                return ()
        loops.append(tuple(loop))
    loops.sort(key=lambda loop: (len(loop), loop), reverse=True)
    return tuple(loops)


def triangle_area(left: Vector, middle: Vector, right: Vector) -> float:
    return 0.5 * (middle - left).cross(right - left).length


def topology_metrics(geometry: MeshGeometry) -> TopologyMetrics:
    counts = edge_use_counts(geometry.faces)
    boundary_edges = [edge for edge, count in counts.items() if count == 1]
    non_manifold = [edge for edge, count in counts.items() if count > 2]
    degenerate = 0
    for face in geometry.faces:
        if len(face) < 3 or len(set(face)) < 3:
            degenerate += 1
            continue
        anchor = geometry.vertices[face[0]]
        area = 0.0
        for index in range(1, len(face) - 1):
            area += triangle_area(anchor, geometry.vertices[face[index]], geometry.vertices[face[index + 1]])
        if area <= DEGENERATE_AREA_EPSILON:
            degenerate += 1
    minimum_edge = min(
        ((geometry.vertices[right] - geometry.vertices[left]).length for left, right in counts),
        default=0.0,
    )
    loops = ordered_boundary_loops(geometry.faces)
    return TopologyMetrics(
        vertex_count=len(geometry.vertices),
        edge_count=len(counts),
        face_count=len(geometry.faces),
        boundary_loop_count=len(loops),
        boundary_edge_count=len(boundary_edges),
        non_manifold_edge_count=len(non_manifold),
        degenerate_face_count=degenerate,
        minimum_edge_length=float(minimum_edge),
    )


def geometry_signature(vertices: Sequence[Vector], faces: Sequence[Sequence[int]]) -> str:
    payload = {
        "policy": GEOMETRY_POLICY_VERSION,
        "vertices": [
            [round(float(component) / COORDINATE_QUANTIZATION) for component in vertex]
            for vertex in vertices
        ],
        "faces": [list(map(int, face)) for face in faces],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def vector_payload(values: Iterable[Vector]) -> list[list[float]]:
    return [[float(component) for component in value] for value in values]
