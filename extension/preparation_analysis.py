"""Deterministic non-destructive preparation analysis for B-Dental Step 4."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass

from mathutils import Vector
from mathutils.bvhtree import BVHTree

from . import axis_geometry, restoration_utils

MIN_ANALYSIS_RADIUS = 0.002
MAX_ANALYSIS_RADIUS = 0.015
DEFAULT_ANALYSIS_RADIUS = 0.006
RADIUS_EXPANSION_FACTOR = 1.35
MAX_ANALYSIS_SAMPLES = 2000
MIN_RECOMMENDED_SAMPLES = 40
SAMPLING_POLICY_VERSION = 2
SELF_HIT_EPSILON_FACTOR = 1.0e-4
MIN_SELF_HIT_EPSILON = 1.0e-7
MAX_RAY_DISTANCE_FACTOR = 4.0


@dataclass(frozen=True)
class AnalysisSample:
    location: tuple[float, float, float]
    blocked: bool
    depth: float


@dataclass(frozen=True)
class AnalysisResult:
    samples: tuple[AnalysisSample, ...]
    analyzed_count: int
    undercut_count: int
    undercut_ratio: float
    mean_blocking_depth: float
    max_blocking_depth: float
    duration_seconds: float


def clamp_radius(value: float) -> float:
    if not math.isfinite(float(value)):
        return DEFAULT_ANALYSIS_RADIUS
    return max(MIN_ANALYSIS_RADIUS, min(MAX_ANALYSIS_RADIUS, float(value)))


def default_radius(restoration) -> float:
    points = axis_geometry.margin_points_local(restoration)
    if not points:
        return DEFAULT_ANALYSIS_RADIUS

    margin = restoration_utils.resolve_margin(restoration)
    if margin is None:
        return DEFAULT_ANALYSIS_RADIUS

    world_points = tuple(margin.matrix_world @ point for point in points)
    center = sum(world_points, Vector()) / len(world_points)
    extent = max((point - center).length for point in world_points)
    return clamp_radius(extent * RADIUS_EXPANSION_FACTOR)


def serialize_samples(samples: tuple[AnalysisSample, ...]) -> str:
    payload = [
        {"p": list(sample.location), "b": sample.blocked, "d": sample.depth}
        for sample in samples
    ]
    return json.dumps(payload, separators=(",", ":"))


def deserialize_samples(value: str) -> tuple[AnalysisSample, ...]:
    if not value:
        return ()
    try:
        payload = json.loads(value)
        samples = []
        for item in payload:
            point = tuple(float(component) for component in item["p"][:3])
            if len(point) != 3 or not all(math.isfinite(component) for component in point):
                return ()
            depth = float(item.get("d", 0.0))
            if not math.isfinite(depth) or depth < 0.0:
                return ()
            samples.append(AnalysisSample(point, bool(item.get("b", False)), depth))
        return tuple(samples)
    except (TypeError, ValueError, KeyError, IndexError, json.JSONDecodeError):
        return ()


def clear_analysis(restoration) -> None:
    restoration.analysis_current = False
    restoration.analysis_samples = ""
    restoration.analysis_sample_count = 0
    restoration.analysis_undercut_count = 0
    restoration.analysis_undercut_ratio = 0.0
    restoration.analysis_mean_blocking_depth = 0.0
    restoration.analysis_max_blocking_depth = 0.0
    restoration.analysis_duration_seconds = 0.0
    restoration.analysis_signature = ""
    restoration.analysis_overlay_visible = False


def _evaluated_world_geometry(target, depsgraph):
    """Return evaluated triangles and sample centers in Blender world units."""

    evaluated = target.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=False, depsgraph=depsgraph)
    if mesh is None:
        raise ValueError("The evaluated preparation mesh is unavailable.")

    try:
        mesh.calc_loop_triangles()
        matrix_world = evaluated.matrix_world.copy()
        vertices = tuple(matrix_world @ vertex.co for vertex in mesh.vertices)
        triangles = tuple(
            tuple(int(vertex_index) for vertex_index in triangle.vertices)
            for triangle in mesh.loop_triangles
        )
        centers = tuple(
            (
                index,
                (
                    vertices[triangle[0]]
                    + vertices[triangle[1]]
                    + vertices[triangle[2]]
                )
                / 3.0,
            )
            for index, triangle in enumerate(triangles)
        )
        return vertices, triangles, centers
    finally:
        evaluated.to_mesh_clear()


def _deterministic_indices(count: int, limit: int) -> tuple[int, ...]:
    if count <= limit:
        return tuple(range(count))
    step = count / float(limit)
    return tuple(min(count - 1, int(index * step)) for index in range(limit))


def _candidate_centers(centers, center_world: Vector, radius_world: float):
    candidates = [
        (triangle_index, point_world)
        for triangle_index, point_world in centers
        if (point_world - center_world).length <= radius_world
    ]
    candidates.sort(key=lambda item: item[0])
    return tuple(
        candidates[index]
        for index in _deterministic_indices(len(candidates), MAX_ANALYSIS_SAMPLES)
    )


def run_analysis(state, restoration, depsgraph) -> AnalysisResult:
    started = time.perf_counter()
    target = restoration_utils.target_scan(state, restoration)
    axis_local = axis_geometry.deserialize_vector(restoration.insertion_axis_local)
    center_local = axis_geometry.margin_center_local(state, restoration, depsgraph)
    radius_world = clamp_radius(restoration.analysis_radius)

    if target is None:
        raise ValueError("The preparation scan is unavailable.")
    if axis_local is None:
        raise ValueError("Define a valid insertion axis before analysis.")
    if center_local is None:
        raise ValueError("The approved margin cannot define an analysis neighborhood.")

    axis_world = axis_geometry.target_local_to_world_direction(target, axis_local)
    if axis_world is None:
        raise ValueError("The insertion axis could not be converted to world space.")

    center_world = target.matrix_world @ center_local
    vertices_world, triangles, centers_world = _evaluated_world_geometry(target, depsgraph)
    if not vertices_world or not triangles:
        raise ValueError("The preparation scan has no usable evaluated surface.")

    candidates = _candidate_centers(centers_world, center_world, radius_world)
    if not candidates:
        raise ValueError(
            "No usable surface samples were found inside the analysis radius. "
            "Verify the approved margin and preparation transform."
        )

    tree = BVHTree.FromPolygons(
        vertices_world,
        triangles,
        all_triangles=True,
        epsilon=0.0,
    )
    removal_world = -axis_world
    epsilon = max(MIN_SELF_HIT_EPSILON, radius_world * SELF_HIT_EPSILON_FACTOR)
    ray_distance = max(radius_world * MAX_RAY_DISTANCE_FACTOR, epsilon * 10.0)
    world_to_target = target.matrix_world.inverted_safe()

    results: list[AnalysisSample] = []
    blocked_depths: list[float] = []

    for _triangle_index, point_world in candidates:
        origin_world = point_world + removal_world * epsilon
        hit, _normal, _face_index, distance = tree.ray_cast(
            origin_world,
            removal_world,
            ray_distance,
        )
        blocked = hit is not None and distance is not None and float(distance) > epsilon
        depth = float(distance) if blocked else 0.0
        if blocked:
            blocked_depths.append(depth)

        point_local = world_to_target @ point_world
        results.append(
            AnalysisSample(
                tuple(float(component) for component in point_local),
                blocked,
                depth,
            )
        )

    analyzed = len(results)
    undercut = len(blocked_depths)
    return AnalysisResult(
        samples=tuple(results),
        analyzed_count=analyzed,
        undercut_count=undercut,
        undercut_ratio=(undercut / analyzed) if analyzed else 0.0,
        mean_blocking_depth=(sum(blocked_depths) / undercut) if undercut else 0.0,
        max_blocking_depth=max(blocked_depths, default=0.0),
        duration_seconds=max(0.0, time.perf_counter() - started),
    )


def store_result(restoration, result: AnalysisResult, signature: str) -> None:
    restoration.analysis_samples = serialize_samples(result.samples)
    restoration.analysis_sample_count = result.analyzed_count
    restoration.analysis_undercut_count = result.undercut_count
    restoration.analysis_undercut_ratio = result.undercut_ratio
    restoration.analysis_mean_blocking_depth = result.mean_blocking_depth
    restoration.analysis_max_blocking_depth = result.max_blocking_depth
    restoration.analysis_duration_seconds = result.duration_seconds
    restoration.analysis_signature = signature
    restoration.analysis_current = True
    restoration.analysis_overlay_visible = True
