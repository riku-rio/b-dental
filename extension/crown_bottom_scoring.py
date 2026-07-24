"""Measurable blocking constraints and deterministic candidate ranking for Step 5."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from typing import Sequence

from mathutils import Vector
from mathutils.bvhtree import BVHTree

from .crown_bottom_geometry import MeshGeometry, topology_metrics
from .preparation_die import BlockoutResult
from .preparation_region import PreparationPatch
from .relief_field import ReliefResult
from .seal_band import SealBandResult

SCORING_POLICY_VERSION = 4
MAX_MARGIN_DEVIATION = 0.00035
MAX_RESIDUAL_BLOCKING_DEPTH = 0.00003
MAX_SELF_INTERSECTIONS = 0
MIN_LOCAL_FEATURE_SIZE = 0.00002
FEATURE_SIZE_EPSILON = 1.0e-9
MAX_OVERLAP_PAIRS = 100000


@dataclass(frozen=True)
class CandidateMetrics:
    source_vertex_count: int
    source_edge_count: int
    source_face_count: int
    generated_vertex_count: int
    generated_edge_count: int
    generated_face_count: int
    margin_sample_count: int
    margin_correspondence_coverage: float
    mean_margin_deviation: float
    maximum_margin_deviation: float
    seal_band_continuous: bool
    minimum_seal_band_width: float
    mean_seal_band_width: float
    mean_gap: float
    maximum_gap: float
    mean_axial_gap: float
    maximum_axial_gap: float
    mean_occlusal_gap: float
    maximum_occlusal_gap: float
    insertion_collision_count: int
    maximum_blocking_depth: float
    self_intersection_count: int
    boundary_loop_count: int
    non_manifold_edge_count: int
    degenerate_face_count: int
    minimum_local_feature_size: float
    optimization_iterations: int
    generation_duration: float
    smoothness_error: float
    relief_target_error: float
    final_score: float
    rejection_reasons: tuple[str, ...]


@dataclass(frozen=True)
class ScoredCandidate:
    candidate_id: str
    accepted: bool
    score: float
    metrics: CandidateMetrics
    rejection_reasons: tuple[str, ...]


def serialize_metrics(metrics: CandidateMetrics) -> str:
    payload = asdict(metrics)
    payload["rejection_reasons"] = list(metrics.rejection_reasons)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def deserialize_metrics(value: str) -> CandidateMetrics | None:
    if not value:
        return None
    try:
        payload = json.loads(value)
        payload["rejection_reasons"] = tuple(
            str(item) for item in payload.get("rejection_reasons", ())
        )
        return CandidateMetrics(**payload)
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        return None


def _triangulate_faces_with_owners(
    faces: Sequence[Sequence[int]],
) -> tuple[tuple[tuple[int, int, int], int], ...]:
    triangles: list[tuple[tuple[int, int, int], int]] = []
    for face_index, face in enumerate(faces):
        if len(face) < 3:
            continue
        for index in range(1, len(face) - 1):
            triangles.append(
                (
                    (
                        int(face[0]),
                        int(face[index]),
                        int(face[index + 1]),
                    ),
                    face_index,
                )
            )
    return tuple(triangles)


def _self_intersection_count(
    geometry: MeshGeometry,
    source_face_count: int,
) -> int:
    owned_triangles = _triangulate_faces_with_owners(geometry.faces)
    if not owned_triangles:
        return 0

    triangles = tuple(item[0] for item in owned_triangles)
    owners = tuple(item[1] for item in owned_triangles)
    tree = BVHTree.FromPolygons(
        geometry.vertices,
        triangles,
        all_triangles=True,
        epsilon=1.0e-9,
    )
    overlaps = tree.overlap(tree)
    count = 0
    for left_index, right_index in overlaps:
        if left_index >= right_index:
            continue

        left_face = owners[left_index]
        right_face = owners[right_index]
        if left_face < source_face_count and right_face < source_face_count:
            continue

        left = set(triangles[left_index])
        right = set(triangles[right_index])
        if left & right:
            continue

        count += 1
        if count >= MAX_OVERLAP_PAIRS:
            break
    return count


def _face_normal(
    vertices: tuple[Vector, ...],
    face: Sequence[int],
) -> Vector | None:
    if len(face) < 3:
        return None
    normal = (vertices[face[1]] - vertices[face[0]]).cross(
        vertices[face[2]] - vertices[face[0]]
    )
    if normal.length <= 1.0e-14:
        return None
    normal.normalize()
    return normal


def _smoothness_error(geometry: MeshGeometry) -> float:
    edge_faces: dict[tuple[int, int], list[int]] = {}
    normals = [
        _face_normal(geometry.vertices, face)
        for face in geometry.faces
    ]
    for face_index, face in enumerate(geometry.faces):
        for left, right in zip(face, (*face[1:], face[0])):
            edge = (left, right) if left < right else (right, left)
            edge_faces.setdefault(edge, []).append(face_index)

    errors: list[float] = []
    for owners in edge_faces.values():
        if len(owners) != 2:
            continue
        left = normals[owners[0]]
        right = normals[owners[1]]
        if left is None or right is None:
            continue
        dot = max(-1.0, min(1.0, left.dot(right)))
        errors.append(1.0 - dot)
    return float(sum(errors) / len(errors)) if errors else 0.0


def _margin_deviations(
    geometry: MeshGeometry,
    seal: SealBandResult,
) -> tuple[float, float, float]:
    if (
        not seal.outer_loop
        or len(seal.outer_loop) != len(seal.margin_samples)
    ):
        return float("inf"), float("inf"), 0.0

    distances = [
        (
            geometry.vertices[vertex_index]
            - seal.margin_samples[index]
        ).length
        for index, vertex_index in enumerate(seal.outer_loop)
    ]
    coverage = (
        sum(1 for distance in distances if math.isfinite(distance))
        / len(distances)
    )
    return (
        float(sum(distances) / len(distances)),
        float(max(distances, default=0.0)),
        float(coverage),
    )


def _generated_minimum_feature_size(
    geometry: MeshGeometry,
    seal: SealBandResult,
) -> float:
    """Measure the generated band span, not source or margin tessellation."""

    widths = [
        (geometry.vertices[outer] - geometry.vertices[inner]).length
        for outer, inner in zip(seal.outer_loop, seal.inner_loop)
    ]
    return float(min(widths, default=0.0))


def _normalized_good(value: float, limit: float) -> float:
    if not math.isfinite(value):
        return 0.0
    if limit <= 0.0:
        return 1.0 if value <= 0.0 else 0.0
    return max(0.0, min(1.0, 1.0 - value / limit))


def evaluate_candidate(
    candidate_id: str,
    patch: PreparationPatch,
    blockout: BlockoutResult,
    relief: ReliefResult,
    seal: SealBandResult,
    *,
    generation_duration: float,
) -> ScoredCandidate:
    geometry = seal.geometry
    topology = topology_metrics(geometry)
    mean_margin, max_margin, coverage = _margin_deviations(
        geometry,
        seal,
    )
    self_intersections = _self_intersection_count(
        geometry,
        len(patch.geometry.faces),
    )
    smoothness = _smoothness_error(geometry)
    generated_minimum_feature = _generated_minimum_feature_size(
        geometry,
        seal,
    )
    reasons: list[str] = []

    if coverage < 1.0:
        reasons.append("Margin correspondence is incomplete.")
    if max_margin > MAX_MARGIN_DEVIATION:
        reasons.append(
            f"Maximum margin deviation is {max_margin * 1000.0:.3f} mm, "
            "above the supported tolerance."
        )
    if not seal.continuity:
        reasons.append(
            "The margin seal band is not continuous at the configured width."
        )
    if (
        blockout.residual_collision_count > 0
        or blockout.maximum_residual_depth > MAX_RESIDUAL_BLOCKING_DEPTH
    ):
        reasons.append(
            f"Insertion-path validation found "
            f"{blockout.residual_collision_count} residual obstruction "
            "sample(s)."
        )
    if self_intersections > MAX_SELF_INTERSECTIONS:
        reasons.append(
            f"The candidate contains {self_intersections} Step 5-created "
            "non-adjacent self-intersection pair(s)."
        )
    if topology.boundary_loop_count != 1:
        reasons.append(
            f"The crown bottom must have one margin boundary loop; found "
            f"{topology.boundary_loop_count}."
        )
    if topology.non_manifold_edge_count:
        reasons.append(
            f"The candidate contains {topology.non_manifold_edge_count} "
            "non-manifold edge(s)."
        )
    if topology.degenerate_face_count:
        reasons.append(
            f"The candidate contains {topology.degenerate_face_count} "
            "degenerate face(s)."
        )
    if (
        generated_minimum_feature
        and generated_minimum_feature + FEATURE_SIZE_EPSILON
        < MIN_LOCAL_FEATURE_SIZE
    ):
        reasons.append(
            f"Minimum generated local feature size is "
            f"{generated_minimum_feature * 1000.0:.3f} mm, below the "
            "supported limit."
        )

    relief_target_error = 0.0
    margin_term = _normalized_good(max_margin, MAX_MARGIN_DEVIATION)
    seal_term = 1.0 if seal.continuity else 0.0
    path_term = 1.0 if not blockout.residual_collision_count else 0.0
    relief_term = _normalized_good(relief_target_error, 0.00005)
    smoothness_term = _normalized_good(smoothness, 0.5)
    topology_term = (
        1.0
        if not topology.non_manifold_edge_count
        and topology.boundary_loop_count == 1
        else 0.0
    )
    self_term = 1.0 if not self_intersections else 0.0
    complexity_penalty = min(0.1, topology.face_count / 1_000_000.0)
    runtime_penalty = min(
        0.1,
        max(0.0, generation_duration) / 300.0,
    )
    score = 100.0 * (
        0.20 * margin_term
        + 0.18 * seal_term
        + 0.20 * path_term
        + 0.12 * relief_term
        + 0.10 * smoothness_term
        + 0.12 * topology_term
        + 0.08 * self_term
        - complexity_penalty
        - runtime_penalty
    )
    score = max(0.0, min(100.0, score))

    metrics = CandidateMetrics(
        source_vertex_count=patch.source_vertex_count,
        source_edge_count=patch.source_edge_count,
        source_face_count=patch.source_face_count,
        generated_vertex_count=topology.vertex_count,
        generated_edge_count=topology.edge_count,
        generated_face_count=topology.face_count,
        margin_sample_count=len(seal.outer_loop),
        margin_correspondence_coverage=coverage,
        mean_margin_deviation=mean_margin,
        maximum_margin_deviation=max_margin,
        seal_band_continuous=seal.continuity,
        minimum_seal_band_width=seal.minimum_width,
        mean_seal_band_width=seal.mean_width,
        mean_gap=relief.mean_gap,
        maximum_gap=relief.maximum_gap,
        mean_axial_gap=relief.mean_axial_gap,
        maximum_axial_gap=relief.maximum_axial_gap,
        mean_occlusal_gap=relief.mean_occlusal_gap,
        maximum_occlusal_gap=relief.maximum_occlusal_gap,
        insertion_collision_count=blockout.residual_collision_count,
        maximum_blocking_depth=blockout.maximum_residual_depth,
        self_intersection_count=self_intersections,
        boundary_loop_count=topology.boundary_loop_count,
        non_manifold_edge_count=topology.non_manifold_edge_count,
        degenerate_face_count=topology.degenerate_face_count,
        minimum_local_feature_size=generated_minimum_feature,
        optimization_iterations=blockout.iterations + relief.iterations,
        generation_duration=max(0.0, generation_duration),
        smoothness_error=smoothness,
        relief_target_error=relief_target_error,
        final_score=score,
        rejection_reasons=tuple(reasons),
    )
    return ScoredCandidate(
        candidate_id=candidate_id,
        accepted=not reasons,
        score=score,
        metrics=metrics,
        rejection_reasons=tuple(reasons),
    )


def rank_candidates(
    candidates: Sequence[ScoredCandidate],
) -> tuple[ScoredCandidate, ...]:
    accepted = [candidate for candidate in candidates if candidate.accepted]
    accepted.sort(
        key=lambda candidate: (
            -round(candidate.score, 9),
            candidate.candidate_id,
        )
    )
    return tuple(accepted)
