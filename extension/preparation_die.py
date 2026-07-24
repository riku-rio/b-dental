"""Preparation-die and insertion-axis-aware blockout geometry for Step 5."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

from mathutils import Vector

from .crown_bottom_geometry import MeshGeometry, projected_coordinates
from .preparation_region import PreparationPatch, vertex_normals

DIE_POLICY_VERSION = 2
DEFAULT_BASE_EXTENSION = 0.0025
MIN_BASE_EXTENSION = 0.001
MAX_BASE_EXTENSION = 0.006
RESIDUAL_OBSTRUCTION_TOLERANCE = 0.00002


@dataclass(frozen=True)
class BlockoutResult:
    patch: PreparationPatch
    blocked_vertices: tuple[Vector, ...]
    residual_collision_count: int
    maximum_residual_depth: float
    moved_vertex_count: int
    maximum_blockout_depth: float
    mean_blockout_depth: float
    iterations: int


def _patch_edges(
    faces: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, int], ...]:
    edges = set()
    for face in faces:
        for left, right in zip(face, (*face[1:], face[0])):
            edges.add((left, right) if left < right else (right, left))
    return tuple(sorted(edges))


def _vertex_neighbors(
    vertex_count: int,
    faces: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    neighbors = [set() for _ in range(vertex_count)]
    for left, right in _patch_edges(faces):
        neighbors[left].add(right)
        neighbors[right].add(left)
    return tuple(tuple(sorted(items)) for items in neighbors)


def _grid_key(
    point: Vector,
    basis,
    cell_size: float,
) -> tuple[int, int]:
    first, second, _axis = projected_coordinates(point, basis)
    return math.floor(first / cell_size), math.floor(second / cell_size)


def _accessible_heights(
    vertices: tuple[Vector, ...],
    basis,
    cell_size: float,
) -> tuple[float, ...]:
    cells: dict[tuple[int, int], list[int]] = defaultdict(list)
    coordinates = [projected_coordinates(vertex, basis) for vertex in vertices]
    for index, vertex in enumerate(vertices):
        cells[_grid_key(vertex, basis, cell_size)].append(index)

    accessible: list[float] = []
    for index, vertex in enumerate(vertices):
        key = _grid_key(vertex, basis, cell_size)
        nearby: list[int] = []
        for horizontal in (-1, 0, 1):
            for vertical in (-1, 0, 1):
                nearby.extend(
                    cells.get((key[0] + horizontal, key[1] + vertical), ())
                )
        if not nearby:
            accessible.append(coordinates[index][2])
            continue
        u_value, v_value, _height = coordinates[index]
        radius_squared = (cell_size * 1.75) ** 2
        heights = [
            coordinates[item][2]
            for item in nearby
            if (
                (coordinates[item][0] - u_value) ** 2
                + (coordinates[item][1] - v_value) ** 2
                <= radius_squared
            )
        ]
        accessible.append(
            min(heights) if heights else coordinates[index][2]
        )
    return tuple(float(value) for value in accessible)


def build_blockout(
    patch: PreparationPatch,
    *,
    clearance: float,
    resolution: float,
    smoothing_strength: float,
    maximum_iterations: int,
) -> BlockoutResult:
    if not math.isfinite(clearance) or clearance < 0.0:
        raise ValueError(
            "Blockout clearance must be finite and non-negative."
        )
    cell_size = max(0.00005, float(resolution))
    iterations = max(1, min(int(maximum_iterations), 20))
    smoothing = max(0.0, min(1.0, float(smoothing_strength)))

    source = patch.geometry.vertices
    axis = patch.axis_world
    basis = patch.basis
    boundary = set(patch.geometry.boundary_loop)
    neighbors = _vertex_neighbors(len(source), patch.geometry.faces)
    source_heights = tuple(
        projected_coordinates(vertex, basis)[2] for vertex in source
    )
    accessible = _accessible_heights(source, basis, cell_size)

    envelope_heights = tuple(
        source_heights[index]
        if index in boundary
        else min(source_heights[index], accessible[index] - clearance)
        for index in range(len(source))
    )
    target_heights = list(envelope_heights)

    for _iteration in range(iterations):
        if smoothing <= 0.0:
            break
        updated = list(target_heights)
        for index, adjacent in enumerate(neighbors):
            if index in boundary or not adjacent:
                continue
            average = sum(target_heights[item] for item in adjacent) / len(
                adjacent
            )
            proposed = (
                target_heights[index] * (1.0 - smoothing * 0.25)
                + average * (smoothing * 0.25)
            )
            updated[index] = min(envelope_heights[index], proposed)
        target_heights = updated

    blocked = tuple(
        source[index]
        + axis * (target_heights[index] - source_heights[index])
        for index in range(len(source))
    )
    blocked_heights = tuple(
        projected_coordinates(vertex, basis)[2] for vertex in blocked
    )
    depths = [
        max(0.0, source_heights[index] - blocked_heights[index])
        for index in range(len(source))
    ]
    moved = [value for value in depths if value > 1.0e-9]

    residual_depths = [
        max(0.0, blocked_heights[index] - envelope_heights[index])
        for index in range(len(blocked))
        if index not in boundary
    ]
    residual = [
        value
        for value in residual_depths
        if value > RESIDUAL_OBSTRUCTION_TOLERANCE
    ]

    return BlockoutResult(
        patch=patch,
        blocked_vertices=blocked,
        residual_collision_count=len(residual),
        maximum_residual_depth=max(residual, default=0.0),
        moved_vertex_count=len(moved),
        maximum_blockout_depth=max(moved, default=0.0),
        mean_blockout_depth=(sum(moved) / len(moved)) if moved else 0.0,
        iterations=iterations,
    )


def _oriented_faces(
    faces: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(face) for face in faces)


def build_closed_die(
    patch: PreparationPatch,
    *,
    surface_vertices: tuple[Vector, ...] | None = None,
    base_extension: float = DEFAULT_BASE_EXTENSION,
) -> MeshGeometry:
    vertices = list(surface_vertices or patch.geometry.vertices)
    faces = list(_oriented_faces(patch.geometry.faces))
    boundary = patch.geometry.boundary_loop
    if len(boundary) < 3:
        raise ValueError(
            "The preparation patch has no usable boundary loop."
        )
    extension = max(
        MIN_BASE_EXTENSION,
        min(MAX_BASE_EXTENSION, float(base_extension)),
    )
    axis = patch.axis_world
    heights = [vertex.dot(axis) for vertex in vertices]
    base_height = max(heights) + extension

    ring_indices: list[int] = []
    for source_index in boundary:
        source = vertices[source_index]
        projected_height = source.dot(axis)
        ring_indices.append(len(vertices))
        vertices.append(source + axis * (base_height - projected_height))

    count = len(boundary)
    for offset in range(count):
        source_left = boundary[offset]
        source_right = boundary[(offset + 1) % count]
        base_left = ring_indices[offset]
        base_right = ring_indices[(offset + 1) % count]
        faces.append((source_left, source_right, base_right, base_left))

    center_index = len(vertices)
    center = sum((vertices[index] for index in ring_indices), Vector()) / count
    vertices.append(center)
    for offset in range(count):
        left = ring_indices[offset]
        right = ring_indices[(offset + 1) % count]
        faces.append((center_index, right, left))

    return MeshGeometry(
        vertices=tuple(vertices),
        faces=tuple(faces),
        boundary_loop=(),
        surface_vertex_count=len(surface_vertices or patch.geometry.vertices),
        metadata=(("die_policy", str(DIE_POLICY_VERSION)),),
    )


def blocked_patch_normals(
    blockout: BlockoutResult,
) -> tuple[Vector, ...]:
    normals = vertex_normals(blockout.patch)
    return tuple(normal.copy() for normal in normals)
