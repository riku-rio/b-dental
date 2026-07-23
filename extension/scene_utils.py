"""Scene and managed-object helpers for B-Dental."""

from collections.abc import Iterable
from pathlib import Path

import bpy
from mathutils import Vector

from . import properties

SCAN_COLLECTION_NAME = "B-Dental Scans"

META_MANAGED = "bdental_managed"
META_ROLE = "bdental_role"
META_SOURCE_PATH = "bdental_source_path"
META_SOURCE_NAME = "bdental_source_name"

_DEFAULT_LOCATION = Vector((0.0, 0.0, 0.0))
_DEFAULT_ROTATION = Vector((0.0, 0.0, 0.0))
_DEFAULT_SCALE = Vector((1.0, 1.0, 1.0))
_DEFAULT_DIMENSIONS = Vector((2.0, 2.0, 2.0))
_DEFAULT_CUBE_VERTICES = {
    (x, y, z)
    for x in (-1.0, 1.0)
    for y in (-1.0, 1.0)
    for z in (-1.0, 1.0)
}
_TRANSFORM_TOLERANCE = 1.0e-6
_COORDINATE_TOLERANCE = 1.0e-6


def _vector_close(left: Iterable[float], right: Iterable[float], tolerance: float) -> bool:
    return all(abs(float(a) - float(b)) <= tolerance for a, b in zip(left, right))


def object_is_alive(obj: bpy.types.Object | None) -> bool:
    """Return whether an object pointer still resolves to Blender data."""

    if obj is None:
        return False

    try:
        resolved = bpy.data.objects.get(obj.name_full)
    except (ReferenceError, RuntimeError):
        return False

    return resolved is obj


def is_untouched_default_cube(obj: bpy.types.Object | None) -> bool:
    """Conservatively identify Blender's untouched startup cube."""

    if not object_is_alive(obj):
        return False

    try:
        if obj.name != "Cube" or obj.type != "MESH" or obj.data is None:
            return False
        if obj.parent is not None or len(obj.constraints) != 0 or len(obj.modifiers) != 0:
            return False
        if obj.data.shape_keys is not None:
            return False
        if not _vector_close(obj.location, _DEFAULT_LOCATION, _TRANSFORM_TOLERANCE):
            return False
        if not _vector_close(obj.rotation_euler, _DEFAULT_ROTATION, _TRANSFORM_TOLERANCE):
            return False
        if not _vector_close(obj.scale, _DEFAULT_SCALE, _TRANSFORM_TOLERANCE):
            return False
        if not _vector_close(obj.dimensions, _DEFAULT_DIMENSIONS, _TRANSFORM_TOLERANCE):
            return False

        mesh = obj.data
        if len(mesh.vertices) != 8 or len(mesh.edges) != 12 or len(mesh.polygons) != 6:
            return False
        if any(polygon.loop_total != 4 for polygon in mesh.polygons):
            return False

        coordinates = {
            tuple(round(float(component), 6) for component in vertex.co)
            for vertex in mesh.vertices
        }
        if len(coordinates) != 8:
            return False

        for coordinate in coordinates:
            if not any(
                _vector_close(coordinate, expected, _COORDINATE_TOLERANCE)
                for expected in _DEFAULT_CUBE_VERTICES
            ):
                return False

        return coordinates == _DEFAULT_CUBE_VERTICES
    except (ReferenceError, RuntimeError, AttributeError):
        return False


def remove_untouched_default_cube(scene: bpy.types.Scene) -> bool:
    """Remove only the accepted untouched startup cube from the scene."""

    cube = scene.objects.get("Cube")
    if not is_untouched_default_cube(cube):
        return False

    remove_object(cube)
    return True


def ensure_scan_collection(scene: bpy.types.Scene) -> bpy.types.Collection:
    """Create or reuse the B-Dental scan collection and link it to the scene."""

    collection = bpy.data.collections.get(SCAN_COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(SCAN_COLLECTION_NAME)

    if scene.collection.children.get(collection.name) is None:
        scene.collection.children.link(collection)

    return collection


def move_object_to_scan_collection(
    obj: bpy.types.Object, scene: bpy.types.Scene
) -> bpy.types.Collection:
    """Link a scan exclusively to the managed scan collection."""

    collection = ensure_scan_collection(scene)

    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)

    if collection.objects.get(obj.name) is None:
        collection.objects.link(obj)

    return collection


def tag_managed_scan(obj: bpy.types.Object, role: str, source_path: str) -> None:
    """Apply B-Dental ownership, role, and source metadata."""

    resolved_path = bpy.path.abspath(source_path) if source_path else ""
    obj[META_MANAGED] = True
    obj[META_ROLE] = role
    obj[META_SOURCE_PATH] = resolved_path
    obj[META_SOURCE_NAME] = Path(resolved_path).name if resolved_path else ""


def is_managed_scan(obj: bpy.types.Object | None) -> bool:
    """Return whether an object is tagged as a B-Dental managed scan."""

    if not object_is_alive(obj):
        return False
    try:
        return bool(obj.get(META_MANAGED, False))
    except (ReferenceError, RuntimeError):
        return False


def is_managed_for_role(obj: bpy.types.Object | None, role: str) -> bool:
    """Return whether an object is managed and tagged for the given role."""

    if not is_managed_scan(obj):
        return False
    try:
        return obj.get(META_ROLE) == role
    except (ReferenceError, RuntimeError):
        return False


def scan_source_name(obj: bpy.types.Object | None) -> str:
    """Return a concise source filename for a managed object."""

    if not object_is_alive(obj):
        return ""
    try:
        stored_name = str(obj.get(META_SOURCE_NAME, ""))
        if stored_name:
            return stored_name
        source_path = str(obj.get(META_SOURCE_PATH, ""))
        return Path(source_path).name if source_path else ""
    except (ReferenceError, RuntimeError, TypeError):
        return ""


def get_role_object(state: bpy.types.PropertyGroup, role: str) -> bpy.types.Object | None:
    """Resolve a workflow role pointer without exposing stale references."""

    attribute = properties.role_pointer_attribute(role)
    try:
        obj = getattr(state, attribute)
    except (AttributeError, ReferenceError, RuntimeError):
        return None
    return obj if object_is_alive(obj) else None


def set_role_object(
    state: bpy.types.PropertyGroup, role: str, obj: bpy.types.Object | None
) -> None:
    """Assign or clear a role pointer."""

    setattr(state, properties.role_pointer_attribute(role), obj)


def iter_assigned_objects(
    state: bpy.types.PropertyGroup,
) -> Iterable[tuple[str, bpy.types.Object]]:
    """Yield live objects assigned to fixed scan roles."""

    for role in properties.SCAN_ROLES:
        obj = get_role_object(state, role)
        if obj is not None:
            yield role, obj


def remove_object(obj: bpy.types.Object | None) -> bool:
    """Remove an object and its now-unused mesh data directly."""

    if not object_is_alive(obj):
        return False

    mesh = obj.data if obj.type == "MESH" else None
    bpy.data.objects.remove(obj, do_unlink=True)

    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)

    return True


def remove_managed_case_scans(
    scene: bpy.types.Scene, state: bpy.types.PropertyGroup
) -> int:
    """Remove only B-Dental-managed scan objects and clear all role pointers."""

    objects_by_pointer: dict[int, bpy.types.Object] = {}

    for _role, obj in iter_assigned_objects(state):
        if is_managed_scan(obj):
            objects_by_pointer[obj.as_pointer()] = obj

    collection = bpy.data.collections.get(SCAN_COLLECTION_NAME)
    if collection is not None:
        for obj in list(collection.objects):
            if scene.objects.get(obj.name) is obj and is_managed_scan(obj):
                objects_by_pointer[obj.as_pointer()] = obj

    for role in properties.SCAN_ROLES:
        set_role_object(state, role, None)

    removed = 0
    for obj in objects_by_pointer.values():
        if remove_object(obj):
            removed += 1

    ensure_scan_collection(scene)
    return removed


def has_destructive_reset_content(
    scene: bpy.types.Scene, state: bpy.types.PropertyGroup
) -> bool:
    """Return whether resetting would remove managed assignments or objects."""

    if any(True for _item in iter_assigned_objects(state)):
        return True

    collection = bpy.data.collections.get(SCAN_COLLECTION_NAME)
    if collection is None:
        return False

    return any(
        scene.objects.get(obj.name) is obj and is_managed_scan(obj)
        for obj in collection.objects
    )


def reset_workflow_state(state: bpy.types.PropertyGroup) -> None:
    """Reset workflow state to a fresh initialized Step 1."""

    state.internal_update_lock = True
    try:
        state.case_initialized = True
        state.current_step = "STEP_1"
        state.step_1_status = "INCOMPLETE"
        state.step_1_valid = False
        state.scan_configuration = "SINGLE_ARCH"
        state.single_arch_role = "UPPER_JAW"
        state.source_unit = "MILLIMETERS"
        state.validation_summary = ""
        state.validation_errors = ""
        state.validation_warnings = ""
        for role in properties.SCAN_ROLES:
            set_role_object(state, role, None)
    finally:
        state.internal_update_lock = False


def object_set_by_pointer() -> dict[int, bpy.types.Object]:
    """Snapshot all Blender objects keyed by stable runtime pointer."""

    return {obj.as_pointer(): obj for obj in bpy.data.objects}
