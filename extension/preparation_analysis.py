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
SAMPLING_POLICY_VERSION = 1
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
    center = sum(points, Vector()) / len(points)
    extent = max((point - center).length for point in points)
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


def _evaluated_geometry(target, depsgraph):
    evaluated = target.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=False, depsgraph=depsgraph)
    if mesh is None:
        raise ValueError("The evaluated preparation mesh is unavailable.")
    vertices = tuple(vertex.co.copy() for vertex in mesh.vertices)
    polygons = tuple(tuple(polygon.vertices) for polygon in mesh.polygons if len(polygon.vertices) >= 3)
    centers = tuple(
        (index, mesh.polygons[index].center.copy())
        for index in range(len(mesh.polygons))
        if len(mesh.polygons[index].vertices) >= 3
    )
    evaluated.to_mesh_clear()
    return vertices, polygons, centers


def _deterministic_indices(count: int, limit: int) -> tuple[int, ...]:
    if count <= limit:
        return tuple(range(count))
    step = count / float(limit)
    return tuple(min(count - 1, int(index * step)) for index in range(limit))


def _candidate_centers(centers, center: Vector, radius: float):
    candidates = [(polygon_index, point) for polygon_index, point in centers if (point - center).length <= radius]
    candidates.sort(key=lambda item: item[0])
    return tuple(candidates[index] for index in _deterministic_indices(len(candidates), MAX_ANALYSIS_SAMPLES))


def run_analysis(state, restoration, depsgraph) -> AnalysisResult:
    started = time.perf_counter()
    target = restoration_utils.target_scan(state, restoration)
    axis = axis_geometry.deserialize_vector(restoration.insertion_axis_local)
    center = axis_geometry.margin_center_local(state, restoration, depsgraph)
    radius = clamp_radius(restoration.analysis_radius)
    if target is None:
        raise ValueError("The preparation scan is unavailable.")
    if axis is None:
        raise ValueError("Define a valid insertion axis before analysis.")
    if center is None:
        raise ValueError("The approved margin cannot define an analysis neighborhood.")

    vertices, polygons, centers = _evaluated_geometry(target, depsgraph)
    if not vertices or not polygons:
        raise ValueError("The preparation scan has no usable evaluated surface.")
    candidates = _candidate_centers(centers, center, radius)
    if not candidates:
        raise ValueError("No usable surface samples were found inside the analysis radius.")

    tree = BVHTree.FromPolygons(vertices, polygons, all_triangles=False, epsilon=0.0)
    removal = -axis
    epsilon = max(MIN_SELF_HIT_EPSILON, radius * SELF_HIT_EPSILON_FACTOR)
    ray_distance = max(radius * MAX_RAY_DISTANCE_FACTOR, epsilon * 10.0)
    results: list[AnalysisSample] = []
    blocked_depths: list[float] = []

    for _polygon_index, point in candidates:
        origin = point + removal * epsilon
        hit, _normal, _face_index, distance = tree.ray_cast(origin, removal, ray_distance)
        blocked = hit is not None and distance is not None and float(distance) > epsilon
        depth = float(distance) if blocked else 0.0
        if blocked:
            blocked_depths.append(depth)
        results.append(AnalysisSample(tuple(float(component) for component in point), blocked, depth))

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
