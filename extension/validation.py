"""Validation rules for B-Dental Step 1."""

from dataclasses import dataclass
import math

import bmesh
import bpy

from . import properties, scene_utils

_DIMENSION_EPSILON = 1.0e-9
_SMALL_SCAN_MM = 5.0
_LARGE_SCAN_MM = 250.0
_HIGH_POLYGON_COUNT = 2_000_000
_TOPOLOGY_ISLAND_LIMIT = 250_000


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Immutable B-Dental workflow-validation outcome."""

    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def _finite_values(values: object) -> bool:
    try:
        return all(math.isfinite(float(value)) for value in values)
    except (TypeError, ValueError, OverflowError):
        return False


def _mesh_coordinates_are_finite(mesh: bpy.types.Mesh) -> bool:
    for vertex in mesh.vertices:
        if not _finite_values(vertex.co):
            return False
    return True


def _topology_warnings(
    mesh: bpy.types.Mesh, role_label: str
) -> tuple[str, ...]:
    warnings: list[str] = []
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        boundary_edges = sum(1 for edge in bm.edges if edge.is_boundary)
        non_manifold_edges = sum(
            1 for edge in bm.edges if not edge.is_manifold and not edge.is_boundary
        )

        if boundary_edges:
            warnings.append(
                f"{role_label}: mesh has {boundary_edges:,} open boundary edges."
            )
        if non_manifold_edges:
            warnings.append(
                f"{role_label}: mesh has {non_manifold_edges:,} non-manifold edges."
            )

        if len(bm.verts) <= _TOPOLOGY_ISLAND_LIMIT and bm.verts:
            remaining = set(bm.verts)
            island_count = 0
            while remaining:
                island_count += 1
                stack = [remaining.pop()]
                while stack:
                    vertex = stack.pop()
                    for edge in vertex.link_edges:
                        neighbor = edge.other_vert(vertex)
                        if neighbor in remaining:
                            remaining.remove(neighbor)
                            stack.append(neighbor)

            if island_count > 1:
                warnings.append(
                    f"{role_label}: mesh contains {island_count:,} disconnected islands."
                )
    except (ReferenceError, RuntimeError, ValueError) as exc:
        warnings.append(f"{role_label}: topology checks could not be completed ({exc}).")
    finally:
        bm.free()

    return tuple(warnings)


def validate_scan_object(
    obj: bpy.types.Object | None,
    role: str,
    *,
    require_metadata: bool = True,
    include_warnings: bool = True,
) -> ValidationResult:
    """Validate one assigned or newly imported scan object."""

    label = properties.role_label(role)
    errors: list[str] = []
    warnings: list[str] = []

    if not scene_utils.object_is_alive(obj):
        return ValidationResult(
            ok=False,
            errors=(f"{label}: assigned object no longer exists. Import the scan again.",),
            warnings=(),
        )

    assert obj is not None

    if obj.type != "MESH" or obj.data is None:
        return ValidationResult(
            ok=False,
            errors=(f"{label}: assigned object must be a mesh.",),
            warnings=(),
        )

    mesh = obj.data
    if len(mesh.vertices) == 0:
        errors.append(f"{label}: mesh has no vertices.")
    if len(mesh.polygons) == 0:
        errors.append(f"{label}: mesh has no polygons.")

    try:
        dimensions = tuple(float(value) for value in obj.dimensions)
    except (ReferenceError, RuntimeError, TypeError, ValueError):
        dimensions = ()

    if len(dimensions) != 3 or not _finite_values(dimensions):
        errors.append(f"{label}: object dimensions contain invalid numeric values.")
    elif any(abs(value) <= _DIMENSION_EPSILON for value in dimensions):
        errors.append(f"{label}: object dimensions must be non-zero on every axis.")

    try:
        matrix_values = [value for row in obj.matrix_world for value in row]
    except (ReferenceError, RuntimeError, TypeError):
        matrix_values = []

    if not matrix_values or not _finite_values(matrix_values):
        errors.append(f"{label}: object transform contains invalid numeric values.")

    if mesh.vertices and not _mesh_coordinates_are_finite(mesh):
        errors.append(f"{label}: mesh coordinates contain non-finite values.")

    if require_metadata and not scene_utils.is_managed_scan(obj):
        errors.append(f"{label}: object is not tagged as a B-Dental managed scan.")
    elif require_metadata and not scene_utils.is_managed_for_role(obj, role):
        errors.append(f"{label}: object metadata does not match this dental role.")

    if include_warnings and not errors:
        maximum_dimension_mm = max(abs(value) for value in dimensions) * 1000.0
        if maximum_dimension_mm < _SMALL_SCAN_MM:
            warnings.append(
                f"{label}: maximum dimension is {maximum_dimension_mm:.2f} mm; verify source units."
            )
        elif maximum_dimension_mm > _LARGE_SCAN_MM:
            warnings.append(
                f"{label}: maximum dimension is {maximum_dimension_mm:.2f} mm; verify source units."
            )

        if len(mesh.polygons) > _HIGH_POLYGON_COUNT:
            warnings.append(
                f"{label}: mesh has {len(mesh.polygons):,} polygons and may be slow to process."
            )

        warnings.extend(_topology_warnings(mesh, label))

    return ValidationResult(ok=not errors, errors=tuple(errors), warnings=tuple(warnings))


def validate_step_one(state: bpy.types.PropertyGroup) -> ValidationResult:
    """Validate required roles, assignments, object data, and metadata."""

    errors: list[str] = []
    warnings: list[str] = []
    required = properties.required_roles(state)

    if not state.case_initialized:
        return ValidationResult(
            ok=False,
            errors=("Start a new dental case before validating Step 1.",),
            warnings=(),
        )

    assigned_pointers: dict[int, str] = {}
    for role in properties.SCAN_ROLES:
        obj = scene_utils.get_role_object(state, role)
        if obj is None:
            continue

        pointer = obj.as_pointer()
        previous_role = assigned_pointers.get(pointer)
        if previous_role is not None:
            errors.append(
                f"{properties.role_label(role)} and {properties.role_label(previous_role)} "
                "cannot use the same object."
            )
        else:
            assigned_pointers[pointer] = role

    for role in required:
        label = properties.role_label(role)
        obj = scene_utils.get_role_object(state, role)
        if obj is None:
            errors.append(f"{label}: required scan is missing. Import an STL for this role.")
            continue

        result = validate_scan_object(obj, role)
        errors.extend(result.errors)
        warnings.extend(result.warnings)

    return ValidationResult(ok=not errors, errors=tuple(errors), warnings=tuple(warnings))
