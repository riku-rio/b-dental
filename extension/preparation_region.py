"""Deterministic preparation-region extraction for B-Dental Step 5."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict, deque
from dataclasses import dataclass

from mathutils import Vector
from mathutils.kdtree import KDTree

from . import axis_geometry, margin_geometry, restoration_utils
from .crown_bottom_geometry import (
    MeshGeometry,
    nearest_point_on_polyline,
    normalized,
    ordered_boundary_loops,
    orthonormal_basis,
    point_in_polygon,
    polygon_signed_area,
    projected_coordinates,
)

REGION_POLICY_VERSION = 1
MAX_REGION_FACES = 60000
MAX_AMBIGUOUS_COMPONENT_RATIO = 0.25
MAX_MARGIN_DEVIATION = 0.0015
WARN_MARGIN_DEVIATION = 0.0005


@dataclass(frozen=True)
class EvaluatedSurface:
    vertices_world: tuple[Vector, ...]
    normals_world: tuple[Vector, ...]
    triangles: tuple[tuple[int, int, int], ...]
    source_vertex_count: int
    source_edge_count: int
    source_face_count: int


@dataclass(frozen=True)
class PreparationPatch:
    geometry: MeshGeometry
    margin_world: tuple[Vector, ...]
    axis_world: Vector
    basis: tuple[Vector, Vector, Vector]
    source_vertex_count: int
    source_edge_count: int
    source_face_count: int
    selected_source_faces: tuple[int, ...]
    mean_margin_deviation: float
    max_margin_deviation: float
    ambiguous_component_ratio: float
    warnings: tuple[str, ...]
    signature: str


def approved_margin_world(state, restoration) -> tuple[Vector, ...]:
    target = restoration_utils.target_scan(state, restoration)
    if target is None:
        return ()
    points = margin_geometry.deserialize_points(restoration.approved_margin_points)
    return tuple(target.matrix_world @ point for point in points)


def evaluated_surface(target, depsgraph) -> EvaluatedSurface:
    evaluated = target.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=False, depsgraph=depsgraph)
    if mesh is None:
        raise ValueError("The evaluated preparation mesh is unavailable.")
    try:
        mesh.calc_loop_triangles()
        matrix_world = evaluated.matrix_world.copy()
        normal_matrix = matrix_world.inverted_safe().transposed().to_3x3()
        vertices = tuple(matrix_world @ vertex.co for vertex in mesh.vertices)
        normals = []
        for vertex in mesh.vertices:
            normal = normal_matrix @ vertex.normal
            if normal.length <= 1.0e-12:
                normal = Vector((0.0, 0.0, 1.0))
            else:
                normal.normalize()
            normals.append(normal)
        triangles = tuple(tuple(int(index) for index in triangle.vertices) for triangle in mesh.loop_triangles)
        if not vertices or not triangles:
            raise ValueError("The preparation scan has no usable evaluated triangles.")
        return EvaluatedSurface(
            vertices_world=vertices,
            normals_world=tuple(normals),
            triangles=triangles,
            source_vertex_count=len(mesh.vertices),
            source_edge_count=len(mesh.edges),
            source_face_count=len(mesh.polygons),
        )
    finally:
        evaluated.to_mesh_clear()


def _face_centroid(surface: EvaluatedSurface, face_index: int) -> Vector:
    face = surface.triangles[face_index]
    return sum((surface.vertices_world[index] for index in face), Vector()) / 3.0


def _face_area(surface: EvaluatedSurface, face_index: int) -> float:
    first, second, third = (surface.vertices_world[index] for index in surface.triangles[face_index])
    return 0.5 * (second - first).cross(third - first).length


def _face_adjacency(triangles: tuple[tuple[int, int, int], ...], selected: set[int]) -> dict[int, set[int]]:
    owners: dict[tuple[int, int], list[int]] = defaultdict(list)
    for face_index in selected:
        face = triangles[face_index]
        for left, right in zip(face, (*face[1:], face[0])):
            edge = (left, right) if left < right else (right, left)
            owners[edge].append(face_index)
    adjacency = {face_index: set() for face_index in selected}
    for face_indices in owners.values():
        if len(face_indices) == 2:
            left, right = face_indices
            adjacency[left].add(right)
            adjacency[right].add(left)
    return adjacency


def _components(adjacency: dict[int, set[int]]) -> tuple[tuple[int, ...], ...]:
    remaining = set(adjacency)
    result: list[tuple[int, ...]] = []
    while remaining:
        start = min(remaining)
        queue = deque([start])
        remaining.remove(start)
        component: list[int] = []
        while queue:
            face = queue.popleft()
            component.append(face)
            for neighbor in sorted(adjacency[face]):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        result.append(tuple(sorted(component)))
    result.sort(key=lambda item: (len(item), item), reverse=True)
    return tuple(result)


def _anchor_vertices(surface: EvaluatedSurface, margin_world: tuple[Vector, ...]) -> tuple[int, ...]:
    tree = KDTree(len(surface.vertices_world))
    for index, point in enumerate(surface.vertices_world):
        tree.insert(point, index)
    tree.balance()
    anchors = []
    for point in margin_world:
        _location, index, _distance = tree.find(point)
        anchors.append(int(index))
    return tuple(anchors)


def _component_score(
    surface: EvaluatedSurface,
    component: tuple[int, ...],
    anchor_vertices: set[int],
    margin_center: Vector,
) -> tuple[int, float, float, int]:
    vertices = {index for face_index in component for index in surface.triangles[face_index]}
    anchor_hits = len(vertices & anchor_vertices)
    area = sum(_face_area(surface, face_index) for face_index in component)
    centroid = sum((_face_centroid(surface, face_index) for face_index in component), Vector()) / max(len(component), 1)
    distance = (centroid - margin_center).length
    return anchor_hits, area, -distance, -min(component)


def _compact_patch(surface: EvaluatedSurface, selected_faces: tuple[int, ...]) -> tuple[MeshGeometry, dict[int, int]]:
    source_indices = sorted({index for face_index in selected_faces for index in surface.triangles[face_index]})
    remap = {source_index: local_index for local_index, source_index in enumerate(source_indices)}
    vertices = tuple(surface.vertices_world[index].copy() for index in source_indices)
    normals = tuple(surface.normals_world[index].copy() for index in source_indices)
    faces = tuple(tuple(remap[index] for index in surface.triangles[face_index]) for face_index in selected_faces)
    loops = ordered_boundary_loops(faces)
    if len(loops) != 1:
        raise ValueError(
            "Preparation extraction did not produce one closed boundary loop. "
            "Adjust the approved margin or use a cleaner scan region."
        )
    geometry = MeshGeometry(
        vertices=vertices,
        faces=faces,
        boundary_loop=loops[0],
        surface_vertex_count=len(vertices),
        metadata=(("normals", json.dumps([[float(value) for value in normal] for normal in normals], separators=(",", ":"))),),
    )
    return geometry, remap


def vertex_normals(patch: PreparationPatch) -> tuple[Vector, ...]:
    for key, value in patch.geometry.metadata:
        if key == "normals":
            try:
                payload = json.loads(value)
                result = tuple(Vector(tuple(float(component) for component in item[:3])) for item in payload)
                if len(result) == len(patch.geometry.vertices):
                    return result
            except (TypeError, ValueError, IndexError, json.JSONDecodeError):
                break
    return tuple(Vector((0.0, 0.0, 1.0)) for _ in patch.geometry.vertices)


def _boundary_deviation(geometry: MeshGeometry, margin_world: tuple[Vector, ...]) -> tuple[float, float]:
    distances = [nearest_point_on_polyline(geometry.vertices[index], margin_world)[1] for index in geometry.boundary_loop]
    if not distances:
        return float("inf"), float("inf")
    return float(sum(distances) / len(distances)), float(max(distances))


def _patch_signature(
    geometry: MeshGeometry,
    selected_faces: tuple[int, ...],
    margin_world: tuple[Vector, ...],
    axis_world: Vector,
) -> str:
    payload = {
        "policy": REGION_POLICY_VERSION,
        "faces": list(selected_faces),
        "boundary": list(geometry.boundary_loop),
        "margin": [[round(float(component), 9) for component in point] for point in margin_world],
        "axis": [round(float(component), 12) for component in axis_world],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def extract_preparation_patch(state, restoration, depsgraph) -> PreparationPatch:
    target = restoration_utils.target_scan(state, restoration)
    if target is None:
        raise ValueError("The preparation scan is unavailable.")
    margin_world = approved_margin_world(state, restoration)
    if len(margin_world) < 6:
        raise ValueError("The approved margin does not contain enough ordered points.")
    axis_local = axis_geometry.deserialize_vector(restoration.approved_axis_local or restoration.insertion_axis_local)
    axis_world = axis_geometry.target_local_to_world_direction(target, axis_local) if axis_local is not None else None
    axis_world = normalized(axis_world)
    if axis_world is None:
        raise ValueError("The approved insertion axis is unavailable.")

    basis = orthonormal_basis(axis_world)
    margin_2d = tuple(projected_coordinates(point, basis)[:2] for point in margin_world)
    signed_area = polygon_signed_area(margin_2d)
    if abs(signed_area) <= 1.0e-12:
        raise ValueError("The approved margin collapses in the insertion-axis projection.")
    if signed_area < 0.0:
        margin_world = tuple(reversed(margin_world))
        margin_2d = tuple(reversed(margin_2d))

    surface = evaluated_surface(target, depsgraph)
    candidate_faces: set[int] = set()
    for face_index, face in enumerate(surface.triangles):
        projected_vertices = tuple(projected_coordinates(surface.vertices_world[index], basis)[:2] for index in face)
        centroid = tuple(sum(values) / 3.0 for values in zip(*projected_vertices))
        if point_in_polygon(centroid, margin_2d) or any(point_in_polygon(point, margin_2d) for point in projected_vertices):
            candidate_faces.add(face_index)
    if not candidate_faces:
        raise ValueError("No target-surface triangles were found inside the approved margin.")
    if len(candidate_faces) > MAX_REGION_FACES:
        raise ValueError(
            f"The bounded preparation region contains {len(candidate_faces):,} triangles, "
            f"above the supported limit of {MAX_REGION_FACES:,}."
        )

    adjacency = _face_adjacency(surface.triangles, candidate_faces)
    components = _components(adjacency)
    if not components:
        raise ValueError("The preparation region could not be separated into a connected surface patch.")
    margin_center = sum(margin_world, Vector()) / len(margin_world)
    anchor_vertices = set(_anchor_vertices(surface, margin_world))
    ranked = sorted(
        components,
        key=lambda component: _component_score(surface, component, anchor_vertices, margin_center),
        reverse=True,
    )
    selected = ranked[0]
    selected_area = max(sum(_face_area(surface, face_index) for face_index in selected), 1.0e-20)
    second_area = sum(_face_area(surface, face_index) for face_index in ranked[1]) if len(ranked) > 1 else 0.0
    ambiguity_ratio = float(second_area / selected_area)
    if ambiguity_ratio > MAX_AMBIGUOUS_COMPONENT_RATIO:
        raise ValueError(
            "The approved margin projection contains multiple similarly sized surface regions. "
            "The generator will not guess which region is the preparation."
        )

    geometry, _remap = _compact_patch(surface, selected)
    mean_deviation, max_deviation = _boundary_deviation(geometry, margin_world)
    if not math.isfinite(max_deviation) or max_deviation > MAX_MARGIN_DEVIATION:
        raise ValueError(
            f"The extracted boundary deviates from the approved margin by up to {max_deviation * 1000.0:.3f} mm, "
            "which exceeds the supported extraction tolerance."
        )
    warnings: list[str] = []
    if max_deviation > WARN_MARGIN_DEVIATION:
        warnings.append(
            f"Preparation-region boundary deviation reached {max_deviation * 1000.0:.3f} mm."
        )
    if ambiguity_ratio > 0.1:
        warnings.append("A secondary surface region was detected near the approved preparation boundary.")

    return PreparationPatch(
        geometry=geometry,
        margin_world=margin_world,
        axis_world=axis_world,
        basis=basis,
        source_vertex_count=surface.source_vertex_count,
        source_edge_count=surface.source_edge_count,
        source_face_count=surface.source_face_count,
        selected_source_faces=tuple(selected),
        mean_margin_deviation=mean_deviation,
        max_margin_deviation=max_deviation,
        ambiguous_component_ratio=ambiguity_ratio,
        warnings=tuple(warnings),
        signature=_patch_signature(geometry, tuple(selected), margin_world, axis_world),
    )
