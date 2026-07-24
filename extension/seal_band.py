"""Continuous margin-correspondent seal-band construction for Step 5."""

from __future__ import annotations

import math
from dataclasses import dataclass

from mathutils import Vector

from .crown_bottom_geometry import MeshGeometry, polygon_signed_area, projected_coordinates, resample_closed_polyline
from .preparation_die import BlockoutResult
from .relief_field import ReliefResult

SEAL_POLICY_VERSION = 1
MINIMUM_SEAL_WIDTH_FACTOR = 0.35


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


def _loop_area(vertices: tuple[Vector, ...], loop: tuple[int, ...], basis) -> float:
    points = tuple(projected_coordinates(vertices[index], basis)[:2] for index in loop)
    return polygon_signed_area(points)


def _match_margin_orientation(
    margin: tuple[Vector, ...],
    boundary_vertices: tuple[Vector, ...],
    boundary_loop: tuple[int, ...],
    basis,
) -> tuple[Vector, ...]:
    samples = resample_closed_polyline(margin, len(boundary_loop))
    boundary_area = _loop_area(boundary_vertices, boundary_loop, basis)
    margin_area = polygon_signed_area(tuple(projected_coordinates(point, basis)[:2] for point in samples))
    if boundary_area * margin_area < 0.0:
        return tuple(reversed(samples))
    return samples


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
        raise ValueError("The preparation patch has no ordered boundary for seal-band construction.")
    if not math.isfinite(marginal_gap) or marginal_gap < 0.0:
        raise ValueError("Marginal gap must be finite and non-negative.")
    if not math.isfinite(seal_band_width) or seal_band_width <= 0.0:
        raise ValueError("Seal-band width must be finite and positive.")

    vertices = [point.copy() for point in relief.vertices]
    center = sum(patch.margin_world, Vector()) / len(patch.margin_world)
    axis = patch.axis_world

    inner_positions: list[Vector] = []
    for vertex_index in boundary:
        point = vertices[vertex_index]
        radial = center - point
        radial -= axis * radial.dot(axis)
        radial_length = radial.length
        if radial_length <= 1.0e-12:
            raise ValueError("The seal-band inward direction is undefined at the preparation boundary.")
        move_distance = min(seal_band_width, radial_length * 0.35)
        inner = point + radial.normalized() * move_distance
        vertices[vertex_index] = inner
        inner_positions.append(inner)

    margin_samples = _match_margin_orientation(
        patch.margin_world,
        tuple(vertices),
        boundary,
        patch.basis,
    )
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
        and minimum_width >= seal_band_width * MINIMUM_SEAL_WIDTH_FACTOR
    )
    geometry = MeshGeometry(
        vertices=tuple(vertices),
        faces=tuple(tuple(face) for face in faces),
        boundary_loop=tuple(outer_indices),
        surface_vertex_count=len(relief.vertices),
        metadata=(
            ("seal_policy", str(SEAL_POLICY_VERSION)),
            ("inner_loop", ",".join(str(index) for index in boundary)),
            ("outer_loop", ",".join(str(index) for index in outer_indices)),
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
