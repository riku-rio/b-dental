"""Continuous margin-correspondent seal-band construction for Step 5."""

from __future__ import annotations

import math
from dataclasses import dataclass

from mathutils import Vector

from .crown_bottom_geometry import (
    MeshGeometry,
    normalized,
    polygon_signed_area,
    projected_coordinates,
    resample_closed_polyline,
)
from .preparation_die import BlockoutResult
from .relief_field import ReliefResult

SEAL_POLICY_VERSION = 2
MINIMUM_SEAL_WIDTH_FACTOR = 0.35
ALIGNMENT_CANDIDATE_LIMIT = 16


@dataclass(frozen=True)
class SealBandResult:
    geometry: MeshGeometry
    outer_loop: tuple[int, ...]
    inner_loop: tuple[int, ...]
    correspondence_count: int
    continuity: bool
    minimum_width: float
    mean_width: float
    maximum_width: float


def _loop_area(
    vertices: tuple[Vector, ...],
    loop: tuple[int, ...],
    basis,
) -> float:
    points = tuple(
        projected_coordinates(vertices[index], basis)[:2]
        for index in loop
    )
    return polygon_signed_area(points)


def _rotate_samples(
    samples: tuple[Vector, ...],
    offset: int,
) -> tuple[Vector, ...]:
    count = len(samples)
    return tuple(samples[(index + offset) % count] for index in range(count))


def _match_margin_correspondence(
    margin: tuple[Vector, ...],
    boundary_vertices: tuple[Vector, ...],
    boundary_loop: tuple[int, ...],
    basis,
) -> tuple[Vector, ...]:
    samples = resample_closed_polyline(margin, len(boundary_loop))
    boundary_area = _loop_area(boundary_vertices, boundary_loop, basis)
    margin_area = polygon_signed_area(
        tuple(
            projected_coordinates(point, basis)[:2]
            for point in samples
        )
    )
    if boundary_area * margin_area < 0.0:
        samples = tuple(reversed(samples))

    boundary_points = tuple(
        boundary_vertices[index] for index in boundary_loop
    )
    nearest_offsets = sorted(
        range(len(samples)),
        key=lambda offset: (
            boundary_points[0] - samples[offset]
        ).length_squared,
    )[: min(ALIGNMENT_CANDIDATE_LIMIT, len(samples))]

    def alignment_cost(offset: int) -> float:
        return sum(
            (
                boundary_points[index]
                - samples[(index + offset) % len(samples)]
            ).length_squared
            for index in range(len(samples))
        )

    best_offset = min(nearest_offsets, key=alignment_cost)
    return _rotate_samples(samples, best_offset)


def _inward_directions(
    vertices: tuple[Vector, ...],
    boundary: tuple[int, ...],
    basis,
) -> tuple[Vector, ...]:
    first, second, _axis = basis
    points_2d = tuple(
        projected_coordinates(vertices[index], basis)[:2]
        for index in boundary
    )
    signed_area = polygon_signed_area(points_2d)
    if abs(signed_area) <= 1.0e-15:
        raise ValueError(
            "The preparation boundary collapses in the insertion-axis projection."
        )
    orientation = 1.0 if signed_area > 0.0 else -1.0

    directions: list[Vector] = []
    count = len(boundary)
    for index in range(count):
        previous = points_2d[(index - 1) % count]
        following = points_2d[(index + 1) % count]
        tangent_x = following[0] - previous[0]
        tangent_y = following[1] - previous[1]
        tangent_length = math.hypot(tangent_x, tangent_y)
        if tangent_length <= 1.0e-15:
            raise ValueError(
                "The preparation boundary contains a collapsed local tangent."
            )
        tangent_x /= tangent_length
        tangent_y /= tangent_length
        inward_x = -tangent_y * orientation
        inward_y = tangent_x * orientation
        direction = normalized(first * inward_x + second * inward_y)
        if direction is None:
            raise ValueError(
                "The seal-band inward direction is undefined at the preparation boundary."
            )
        directions.append(direction)
    return tuple(directions)


def build_seal_band(
    blockout: BlockoutResult,
    relief: ReliefResult,
    *,
    marginal_gap: float,
    seal_band_width: float,
) -> SealBandResult:
    patch = blockout.patch
    boundary = patch.geometry.boundary_loop
    if len(boundary) < 3:
        raise ValueError(
            "The preparation patch has no ordered boundary for seal-band construction."
        )
    if not math.isfinite(marginal_gap) or marginal_gap < 0.0:
        raise ValueError(
            "Marginal gap must be finite and non-negative."
        )
    if not math.isfinite(seal_band_width) or seal_band_width <= 0.0:
        raise ValueError(
            "Seal-band width must be finite and positive."
        )

    source_vertices = tuple(point.copy() for point in relief.vertices)
    margin_samples = _match_margin_correspondence(
        patch.margin_world,
        source_vertices,
        boundary,
        patch.basis,
    )
    inward_directions = _inward_directions(
        source_vertices,
        boundary,
        patch.basis,
    )

    vertices = [point.copy() for point in source_vertices]
    inner_positions: list[Vector] = []
    for vertex_index, direction in zip(boundary, inward_directions):
        point = source_vertices[vertex_index]
        inner = point + direction * seal_band_width
        vertices[vertex_index] = inner
        inner_positions.append(inner)

    outer_indices: list[int] = []
    widths: list[float] = []
    for offset, margin_point in enumerate(margin_samples):
        boundary_index = boundary[offset]
        normal = relief.oriented_normals[boundary_index]
        outer = margin_point + normal * marginal_gap
        outer_indices.append(len(vertices))
        vertices.append(outer)
        widths.append((inner_positions[offset] - outer).length)

    faces = list(patch.geometry.faces)
    count = len(boundary)
    for offset in range(count):
        outer_left = outer_indices[offset]
        outer_right = outer_indices[(offset + 1) % count]
        inner_left = boundary[offset]
        inner_right = boundary[(offset + 1) % count]
        faces.append((outer_left, outer_right, inner_right, inner_left))

    minimum_width = min(widths, default=0.0)
    continuity = (
        len(outer_indices) == len(boundary)
        and len(set(outer_indices)) == len(outer_indices)
        and minimum_width
        >= seal_band_width * MINIMUM_SEAL_WIDTH_FACTOR
    )
    geometry = MeshGeometry(
        vertices=tuple(vertices),
        faces=tuple(tuple(face) for face in faces),
        boundary_loop=tuple(outer_indices),
        surface_vertex_count=len(relief.vertices),
        metadata=(
            ("seal_policy", str(SEAL_POLICY_VERSION)),
            ("inner_loop", ",".join(str(index) for index in boundary)),
            (
                "outer_loop",
                ",".join(str(index) for index in outer_indices),
            ),
        ),
    )
    return SealBandResult(
        geometry=geometry,
        outer_loop=tuple(outer_indices),
        inner_loop=tuple(boundary),
        correspondence_count=count,
        continuity=continuity,
        minimum_width=float(minimum_width),
        mean_width=(sum(widths) / len(widths)) if widths else 0.0,
        maximum_width=max(widths, default=0.0),
    )
