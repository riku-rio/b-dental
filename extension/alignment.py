"""Rigid point registration utilities for B-Dental Step 2."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from statistics import median
from typing import Iterable, Sequence

import bpy
from mathutils import Matrix, Quaternion, Vector
from mathutils.kdtree import KDTree


@dataclass(frozen=True)
class RegistrationSettings:
    """Conservative, bounded registration settings in Blender world units."""

    max_points: int = 4000
    max_correspondence_distance: float = 0.015
    retained_fraction: float = 0.60
    minimum_correspondences: int = 32
    minimum_inlier_ratio: float = 0.02
    maximum_iterations: int = 30
    translation_tolerance: float = 1.0e-5
    rotation_tolerance: float = 1.0e-3
    rmse_change_tolerance: float = 1.0e-6


DEFAULT_SETTINGS = RegistrationSettings()


@dataclass(frozen=True)
class RegistrationResult:
    """Structured result returned by rigid registration."""

    ok: bool
    transform: Matrix
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    iterations: int = 0
    inlier_count: int = 0
    inlier_ratio: float = 0.0
    rmse: float = 0.0
    median_distance: float = 0.0
    translation_delta: float = 0.0
    rotation_delta: float = 0.0


@dataclass(frozen=True)
class TransformDisagreement:
    """Difference between two rigid transform candidates."""

    translation: float
    rotation: float


def _finite_vector(vector: Vector) -> bool:
    return all(isfinite(float(value)) for value in vector)


def matrix_is_finite(matrix: Matrix) -> bool:
    """Return whether all matrix values are finite."""

    return all(isfinite(float(value)) for row in matrix for value in row)


def sample_object_points(
    obj: bpy.types.Object,
    depsgraph: bpy.types.Depsgraph,
    *,
    max_points: int = DEFAULT_SETTINGS.max_points,
) -> tuple[Vector, ...]:
    """Deterministically sample evaluated mesh vertices in world space."""

    if obj.type != "MESH" or obj.data is None:
        raise ValueError(f"{obj.name} is not a mesh object.")
    if max_points < 3:
        raise ValueError("Point cap must be at least three.")

    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        vertex_count = len(mesh.vertices)
        if vertex_count < 3:
            raise ValueError(f"{obj.name} does not contain enough mesh vertices.")

        step = max(1, (vertex_count + max_points - 1) // max_points)
        matrix = evaluated.matrix_world.copy()
        points = tuple(
            matrix @ mesh.vertices[index].co
            for index in range(0, vertex_count, step)
        )[:max_points]
    finally:
        evaluated.to_mesh_clear()

    if len(points) < 3 or any(not _finite_vector(point) for point in points):
        raise ValueError(f"{obj.name} produced invalid sampled coordinates.")
    return points


def transform_points(points: Iterable[Vector], matrix: Matrix) -> tuple[Vector, ...]:
    """Apply a matrix to a point sequence."""

    return tuple(matrix @ point for point in points)


def combine_points(*groups: Iterable[Vector]) -> tuple[Vector, ...]:
    """Combine point groups without modifying their vectors."""

    return tuple(Vector(point) for group in groups for point in group)


def _build_tree(points: Sequence[Vector]) -> KDTree:
    tree = KDTree(len(points))
    for index, point in enumerate(points):
        tree.insert(point, index)
    tree.balance()
    return tree


def _trimmed_correspondences(
    source_points: Sequence[Vector],
    target_points: Sequence[Vector],
    settings: RegistrationSettings,
) -> tuple[tuple[Vector, Vector, float], ...]:
    if len(source_points) < 3 or len(target_points) < 3:
        return ()

    tree = _build_tree(target_points)
    candidates: list[tuple[Vector, Vector, float]] = []
    for source in source_points:
        target, _index, distance = tree.find(source)
        if target is None or distance > settings.max_correspondence_distance:
            continue
        candidates.append((source, Vector(target), float(distance)))

    candidates.sort(key=lambda item: item[2])
    if not candidates:
        return ()

    retained_count = int(len(candidates) * settings.retained_fraction)
    retained_count = max(settings.minimum_correspondences, retained_count)
    retained_count = min(len(candidates), retained_count)
    return tuple(candidates[:retained_count])


def _centroid(points: Sequence[Vector]) -> Vector:
    total = Vector((0.0, 0.0, 0.0))
    for point in points:
        total += point
    return total / float(len(points))


def _dominant_eigenvector(matrix: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    vector = (1.0, 0.0, 0.0, 0.0)
    for _iteration in range(64):
        product = tuple(
            sum(matrix[row][column] * vector[column] for column in range(4))
            for row in range(4)
        )
        norm = sqrt(sum(value * value for value in product))
        if norm <= 1.0e-15:
            return (1.0, 0.0, 0.0, 0.0)
        updated = tuple(value / norm for value in product)
        if sum(abs(updated[index] - vector[index]) for index in range(4)) <= 1.0e-12:
            return updated
        vector = updated
    return vector


def estimate_rigid_transform(
    source_points: Sequence[Vector], target_points: Sequence[Vector]
) -> Matrix:
    """Estimate a scale-preserving rigid transform using Horn's quaternion method."""

    if len(source_points) != len(target_points) or len(source_points) < 3:
        raise ValueError("Rigid transform estimation requires matching point sets.")

    source_centroid = _centroid(source_points)
    target_centroid = _centroid(target_points)

    sxx = sxy = sxz = syx = syy = syz = szx = szy = szz = 0.0
    for source, target in zip(source_points, target_points):
        left = source - source_centroid
        right = target - target_centroid
        sxx += left.x * right.x
        sxy += left.x * right.y
        sxz += left.x * right.z
        syx += left.y * right.x
        syy += left.y * right.y
        syz += left.y * right.z
        szx += left.z * right.x
        szy += left.z * right.y
        szz += left.z * right.z

    trace = sxx + syy + szz
    horn = (
        (trace, syz - szy, szx - sxz, sxy - syx),
        (syz - szy, sxx - syy - szz, sxy + syx, szx + sxz),
        (szx - sxz, sxy + syx, -sxx + syy - szz, syz + szy),
        (sxy - syx, szx + sxz, syz + szy, -sxx - syy + szz),
    )

    quaternion_values = _dominant_eigenvector(horn)
    rotation = Quaternion(quaternion_values).normalized()
    rotation_matrix = rotation.to_matrix().to_4x4()
    translation = target_centroid - (rotation_matrix @ source_centroid)
    rotation_matrix.translation = translation

    if not matrix_is_finite(rotation_matrix):
        raise ValueError("Rigid transform estimation produced non-finite values.")
    return rotation_matrix


def _rotation_angle(matrix: Matrix) -> float:
    try:
        return float(matrix.to_quaternion().angle)
    except (ValueError, ZeroDivisionError):
        return 0.0


def _distance_metrics(correspondences: Sequence[tuple[Vector, Vector, float]]) -> tuple[float, float]:
    if not correspondences:
        return 0.0, 0.0
    distances = [item[2] for item in correspondences]
    rmse = sqrt(sum(distance * distance for distance in distances) / len(distances))
    return rmse, float(median(distances))


def run_icp(
    source_points: Sequence[Vector],
    target_points: Sequence[Vector],
    *,
    settings: RegistrationSettings = DEFAULT_SETTINGS,
    progress: callable | None = None,
) -> RegistrationResult:
    """Run bounded, trimmed point-to-point ICP and return a delta world transform."""

    identity = Matrix.Identity(4)
    if len(source_points) < settings.minimum_correspondences:
        return RegistrationResult(
            ok=False,
            transform=identity,
            errors=("The moving scan does not provide enough sampled points.",),
        )
    if len(target_points) < settings.minimum_correspondences:
        return RegistrationResult(
            ok=False,
            transform=identity,
            errors=("The target scan does not provide enough sampled points.",),
        )

    current = tuple(Vector(point) for point in source_points)
    accumulated = identity.copy()
    previous_rmse: float | None = None
    last_translation = 0.0
    last_rotation = 0.0
    converged = False
    iteration_count = 0

    for iteration in range(1, settings.maximum_iterations + 1):
        iteration_count = iteration
        if progress is not None:
            progress(iteration, settings.maximum_iterations)

        correspondences = _trimmed_correspondences(current, target_points, settings)
        inlier_ratio = len(correspondences) / float(len(current))
        if len(correspondences) < settings.minimum_correspondences:
            return RegistrationResult(
                ok=False,
                transform=identity,
                errors=(
                    "Registration found too few overlapping points. Use manual coarse positioning and retry.",
                ),
                iterations=iteration - 1,
                inlier_count=len(correspondences),
                inlier_ratio=inlier_ratio,
            )
        if inlier_ratio < settings.minimum_inlier_ratio:
            return RegistrationResult(
                ok=False,
                transform=identity,
                errors=(
                    "Registration overlap is too small. Use manual coarse positioning and retry.",
                ),
                iterations=iteration - 1,
                inlier_count=len(correspondences),
                inlier_ratio=inlier_ratio,
            )

        source_matches = tuple(item[0] for item in correspondences)
        target_matches = tuple(item[1] for item in correspondences)
        try:
            delta = estimate_rigid_transform(source_matches, target_matches)
        except ValueError as exc:
            return RegistrationResult(
                ok=False,
                transform=identity,
                errors=(str(exc),),
                iterations=iteration - 1,
                inlier_count=len(correspondences),
                inlier_ratio=inlier_ratio,
            )

        current = transform_points(current, delta)
        accumulated = delta @ accumulated
        last_translation = float(delta.translation.length)
        last_rotation = _rotation_angle(delta)

        updated_correspondences = _trimmed_correspondences(current, target_points, settings)
        rmse, _median_distance = _distance_metrics(updated_correspondences)
        rmse_change = (
            abs(previous_rmse - rmse) if previous_rmse is not None else float("inf")
        )
        previous_rmse = rmse

        if (
            last_translation <= settings.translation_tolerance
            and last_rotation <= settings.rotation_tolerance
        ) or rmse_change <= settings.rmse_change_tolerance:
            converged = True
            break

    final_correspondences = _trimmed_correspondences(current, target_points, settings)
    final_ratio = len(final_correspondences) / float(len(current))
    final_rmse, final_median = _distance_metrics(final_correspondences)

    if not converged:
        return RegistrationResult(
            ok=False,
            transform=identity,
            errors=(
                "Registration did not converge within the bounded iteration limit. Reset or adjust manually and retry.",
            ),
            iterations=iteration_count,
            inlier_count=len(final_correspondences),
            inlier_ratio=final_ratio,
            rmse=final_rmse,
            median_distance=final_median,
            translation_delta=last_translation,
            rotation_delta=last_rotation,
        )

    warnings: list[str] = []
    if final_ratio < 0.10:
        warnings.append("Registration converged with a limited overlap ratio; inspect the result carefully.")

    return RegistrationResult(
        ok=True,
        transform=accumulated,
        warnings=tuple(warnings),
        iterations=iteration_count,
        inlier_count=len(final_correspondences),
        inlier_ratio=final_ratio,
        rmse=final_rmse,
        median_distance=final_median,
        translation_delta=float(accumulated.translation.length),
        rotation_delta=_rotation_angle(accumulated),
    )


def transform_disagreement(first: Matrix, second: Matrix) -> TransformDisagreement:
    """Measure translation and rotation disagreement between two world matrices."""

    translation = float((first.translation - second.translation).length)
    rotation = float(
        first.to_quaternion().rotation_difference(second.to_quaternion()).angle
    )
    return TransformDisagreement(translation=translation, rotation=rotation)
