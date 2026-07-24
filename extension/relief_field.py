"""Region-aware continuous crown-bottom relief field for B-Dental Step 5."""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass

from mathutils import Vector

from .crown_bottom_geometry import normalized
from .preparation_die import BlockoutResult, blocked_patch_normals

RELIEF_POLICY_VERSION = 1
OCCLUSAL_ALIGNMENT_THRESHOLD = 0.55


@dataclass(frozen=True)
class ReliefSettings:
    marginal_gap: float
    cement_gap: float
    spacer_start: float
    axial_relief: float
    occlusal_relief: float
    seal_band_width: float
    smoothing_strength: float
    maximum_iterations: int


@dataclass(frozen=True)
class ReliefResult:
    vertices: tuple[Vector, ...]
    oriented_normals: tuple[Vector, ...]
    gaps: tuple[float, ...]
    distances_from_margin: tuple[float, ...]
    regions: tuple[str, ...]
    mean_gap: float
    maximum_gap: float
    mean_axial_gap: float
    maximum_axial_gap: float
    mean_occlusal_gap: float
    maximum_occlusal_gap: float
    iterations: int


def _edges(faces: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, int], ...]:
    result = set()
    for face in faces:
        for left, right in zip(face, (*face[1:], face[0])):
            result.add((left, right) if left < right else (right, left))
    return tuple(sorted(result))


def _neighbors(vertex_count: int, faces: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    values = [set() for _ in range(vertex_count)]
    for left, right in _edges(faces):
        values[left].add(right)
        values[right].add(left)
    return tuple(tuple(sorted(items)) for items in values)


def graph_distances(vertices: tuple[Vector, ...], faces: tuple[tuple[int, ...], ...], seeds: tuple[int, ...]) -> tuple[float, ...]:
    neighbors = _neighbors(len(vertices), faces)
    distances = [float("inf")] * len(vertices)
    queue: list[tuple[float, int]] = []
    for seed in seeds:
        if 0 <= seed < len(vertices):
            distances[seed] = 0.0
            heapq.heappush(queue, (0.0, seed))
    while queue:
        distance, index = heapq.heappop(queue)
        if distance != distances[index]:
            continue
        for neighbor in neighbors[index]:
            candidate = distance + (vertices[neighbor] - vertices[index]).length
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))
    if any(not math.isfinite(value) for value in distances):
        raise ValueError("The preparation patch contains a disconnected surface region.")
    return tuple(float(value) for value in distances)


def _smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def _orient_normal(point: Vector, normal: Vector, center: Vector, axis: Vector) -> Vector:
    candidate = normalized(normal) or (-axis).copy()
    radial = point - center
    radial -= axis * radial.dot(axis)
    reference = radial if radial.length > 1.0e-12 else -axis
    if radial.length > 1.0e-12:
        reference = radial.normalized() + (-axis) * 0.2
    reference = normalized(reference) or (-axis).copy()
    if candidate.dot(reference) < 0.0:
        candidate.negate()
    return candidate


def _region_target(normal: Vector, axis: Vector, settings: ReliefSettings) -> tuple[str, float]:
    alignment = abs(normal.dot(axis))
    if alignment >= OCCLUSAL_ALIGNMENT_THRESHOLD:
        return "OCCLUSAL", settings.cement_gap + settings.occlusal_relief
    return "AXIAL", settings.cement_gap + settings.axial_relief


def _validate_settings(settings: ReliefSettings) -> None:
    values = (
        settings.marginal_gap,
        settings.cement_gap,
        settings.spacer_start,
        settings.axial_relief,
        settings.occlusal_relief,
        settings.seal_band_width,
        settings.smoothing_strength,
    )
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("Relief settings must contain only finite values.")
    if min(values[:6]) < 0.0:
        raise ValueError("Relief distances must be non-negative.")
    if settings.spacer_start < settings.seal_band_width:
        raise ValueError("Spacer start must not be smaller than the seal-band width.")


def build_relief(blockout: BlockoutResult, settings: ReliefSettings) -> ReliefResult:
    _validate_settings(settings)
    patch = blockout.patch
    source = blockout.blocked_vertices
    boundary = patch.geometry.boundary_loop
    distances = graph_distances(source, patch.geometry.faces, boundary)
    center = sum(patch.margin_world, Vector()) / len(patch.margin_world)
    axis = patch.axis_world
    raw_normals = blocked_patch_normals(blockout)
    normals = tuple(_orient_normal(point, normal, center, axis) for point, normal in zip(source, raw_normals))

    targets: list[float] = []
    regions: list[str] = []
    transition_width = max(settings.seal_band_width, 0.00005)
    for distance, normal in zip(distances, normals):
        region, full_target = _region_target(normal, axis, settings)
        if distance <= settings.seal_band_width:
            gap = settings.marginal_gap
            region_name = "SEAL"
        elif distance <= settings.spacer_start:
            gap = settings.marginal_gap
            region_name = "PRE_SPACER"
        elif distance < settings.spacer_start + transition_width:
            factor = _smoothstep((distance - settings.spacer_start) / transition_width)
            gap = settings.marginal_gap * (1.0 - factor) + full_target * factor
            region_name = "TRANSITION"
        else:
            gap = full_target
            region_name = region
        targets.append(float(gap))
        regions.append(region_name)

    neighbors = _neighbors(len(source), patch.geometry.faces)
    gaps = list(targets)
    smoothing = max(0.0, min(1.0, settings.smoothing_strength))
    iterations = max(0, min(int(settings.maximum_iterations), 20))
    fixed = {index for index, distance in enumerate(distances) if distance <= settings.spacer_start}
    minimum = min(targets, default=0.0)
    maximum = max(targets, default=0.0)
    for _iteration in range(iterations):
        if smoothing <= 0.0:
            break
        updated = list(gaps)
        for index, adjacent in enumerate(neighbors):
            if index in fixed or not adjacent:
                continue
            average = sum(gaps[item] for item in adjacent) / len(adjacent)
            value = gaps[index] * (1.0 - smoothing * 0.2) + average * (smoothing * 0.2)
            updated[index] = max(minimum, min(maximum, value))
        gaps = updated

    relieved = tuple(point + normal * gap for point, normal, gap in zip(source, normals, gaps))
    axial = [gap for gap, region in zip(gaps, regions) if region == "AXIAL"]
    occlusal = [gap for gap, region in zip(gaps, regions) if region == "OCCLUSAL"]
    return ReliefResult(
        vertices=relieved,
        oriented_normals=normals,
        gaps=tuple(float(value) for value in gaps),
        distances_from_margin=distances,
        regions=tuple(regions),
        mean_gap=(sum(gaps) / len(gaps)) if gaps else 0.0,
        maximum_gap=max(gaps, default=0.0),
        mean_axial_gap=(sum(axial) / len(axial)) if axial else 0.0,
        maximum_axial_gap=max(axial, default=0.0),
        mean_occlusal_gap=(sum(occlusal) / len(occlusal)) if occlusal else 0.0,
        maximum_occlusal_gap=max(occlusal, default=0.0),
        iterations=iterations,
    )
