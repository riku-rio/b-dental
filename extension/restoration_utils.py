"""Restoration identity and managed-artifact helpers for B-Dental Step 3."""

from __future__ import annotations

import json
import uuid

import bpy
from mathutils import Matrix

from . import properties, scene_utils

RESTORATION_COLLECTION_NAME = "B-Dental Restorations"
RESTORATION_SCHEMA_VERSION = 1
RESTORATION_TYPE = "ANATOMICAL_CROWN"
MARGIN_ARTIFACT_TYPE = "MARGIN"

META_ARTIFACT_TYPE = "bdental_artifact_type"
META_RESTORATION_ID = "bdental_restoration_id"
META_TARGET_ROLE = "bdental_target_role"
META_TARGET_TOOTH = "bdental_target_tooth_fdi"
META_SCHEMA_VERSION = "bdental_schema_version"


def new_restoration_id() -> str:
    return uuid.uuid4().hex


def teeth_for_arch(arch: str) -> tuple[str, ...]:
    if arch == "UPPER_JAW":
        return properties.UPPER_FDI_TEETH
    if arch == "LOWER_JAW":
        return properties.LOWER_FDI_TEETH
    return ()


def tooth_belongs_to_arch(tooth: str, arch: str) -> bool:
    return tooth in teeth_for_arch(arch)


def available_target_arches(state) -> tuple[str, ...]:
    arches = []
    for role in ("UPPER_JAW", "LOWER_JAW"):
        if scene_utils.get_role_object(state, role) is not None:
            arches.append(role)
    return tuple(arches)


def target_scan(state):
    if state.target_arch not in {"UPPER_JAW", "LOWER_JAW"}:
        return None
    return scene_utils.get_role_object(state, state.target_arch)


def ensure_restoration_collection(scene: bpy.types.Scene) -> bpy.types.Collection:
    collection = bpy.data.collections.get(RESTORATION_COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(RESTORATION_COLLECTION_NAME)
    if scene.collection.children.get(collection.name) is None:
        scene.collection.children.link(collection)
    return collection


def move_to_restoration_collection(obj: bpy.types.Object, scene: bpy.types.Scene) -> None:
    collection = ensure_restoration_collection(scene)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    if collection.objects.get(obj.name) is None:
        collection.objects.link(obj)


def tag_margin(obj: bpy.types.Object, state) -> None:
    obj[scene_utils.META_MANAGED] = True
    obj[META_ARTIFACT_TYPE] = MARGIN_ARTIFACT_TYPE
    obj[META_RESTORATION_ID] = state.restoration_id
    obj[META_TARGET_ROLE] = state.target_arch
    obj[META_TARGET_TOOTH] = state.target_tooth_fdi
    obj[META_SCHEMA_VERSION] = RESTORATION_SCHEMA_VERSION


def is_managed_margin(obj: bpy.types.Object | None, state=None) -> bool:
    if not scene_utils.object_is_alive(obj):
        return False
    try:
        if obj.type != "CURVE" or not bool(obj.get(scene_utils.META_MANAGED, False)):
            return False
        if obj.get(META_ARTIFACT_TYPE) != MARGIN_ARTIFACT_TYPE:
            return False
        if state is None:
            return True
        return (
            obj.get(META_RESTORATION_ID) == state.restoration_id
            and obj.get(META_TARGET_ROLE) == state.target_arch
            and obj.get(META_TARGET_TOOTH) == state.target_tooth_fdi
        )
    except (ReferenceError, RuntimeError, AttributeError):
        return False


def resolve_margin(state):
    try:
        obj = state.margin_object
    except (AttributeError, ReferenceError, RuntimeError):
        return None
    return obj if is_managed_margin(obj, state) else None


def remove_margin_object(obj: bpy.types.Object | None) -> bool:
    if not scene_utils.object_is_alive(obj):
        return False
    curve = obj.data if obj.type == "CURVE" else None
    bpy.data.objects.remove(obj, do_unlink=True)
    if curve is not None and curve.users == 0:
        bpy.data.curves.remove(curve)
    return True


def remove_active_margin(state) -> bool:
    obj = None
    try:
        obj = state.margin_object
    except (AttributeError, ReferenceError, RuntimeError):
        pass
    removed = remove_margin_object(obj) if is_managed_margin(obj) else False
    state.margin_object = None
    state.margin_candidate_closed = False
    state.margin_session_active = False
    return removed


def iter_managed_restoration_artifacts(scene: bpy.types.Scene):
    collection = bpy.data.collections.get(RESTORATION_COLLECTION_NAME)
    if collection is None:
        return
    for obj in list(collection.objects):
        if scene.objects.get(obj.name) is obj and is_managed_margin(obj):
            yield obj


def remove_all_managed_restoration_artifacts(scene: bpy.types.Scene, state) -> int:
    objects = {obj.as_pointer(): obj for obj in iter_managed_restoration_artifacts(scene)}
    pointer = getattr(state, "margin_object", None)
    if is_managed_margin(pointer):
        objects[pointer.as_pointer()] = pointer
    state.margin_object = None
    removed = sum(1 for obj in objects.values() if remove_margin_object(obj))
    ensure_restoration_collection(scene)
    return removed


def has_managed_restoration_artifacts(scene: bpy.types.Scene, state) -> bool:
    if is_managed_margin(getattr(state, "margin_object", None)):
        return True
    return any(True for _obj in iter_managed_restoration_artifacts(scene))


def matrix_signature(matrix: Matrix) -> str:
    return ";".join(
        ",".join(f"{float(value):.17g}" for value in row) for row in matrix
    )


def target_scan_signature(obj: bpy.types.Object | None) -> str:
    if not scene_utils.object_is_alive(obj) or obj.type != "MESH" or obj.data is None:
        return ""
    payload = {
        "object": obj.name_full,
        "data": obj.data.name_full,
        "vertices": len(obj.data.vertices),
        "edges": len(obj.data.edges),
        "polygons": len(obj.data.polygons),
        "source_path": str(obj.get(scene_utils.META_SOURCE_PATH, "")),
        "source_name": str(obj.get(scene_utils.META_SOURCE_NAME, "")),
        "role": str(obj.get(scene_utils.META_ROLE, "")),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def target_matrix_signature(obj: bpy.types.Object | None) -> str:
    if not scene_utils.object_is_alive(obj):
        return ""
    return matrix_signature(obj.matrix_world.copy())


def upstream_approval_signature(state) -> str:
    payload = {
        "status": state.step_2_status,
        "valid": bool(state.step_2_valid),
        "method": state.verification_method,
        "upper": state.approved_upper_matrix,
        "lower": state.approved_lower_matrix,
        "right": state.approved_right_bite_matrix,
        "left": state.approved_left_bite_matrix,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def initialize_target_defaults(state) -> None:
    arches = available_target_arches(state)
    if not arches:
        return
    preferred = state.single_arch_role if state.scan_configuration == "SINGLE_ARCH" else state.target_arch
    arch = preferred if preferred in arches else arches[0]
    state.internal_update_lock = True
    try:
        state.target_arch = arch
        valid_teeth = teeth_for_arch(arch)
        if state.target_tooth_fdi not in valid_teeth:
            state.target_tooth_fdi = valid_teeth[0]
    finally:
        state.internal_update_lock = False
