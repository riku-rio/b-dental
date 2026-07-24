"""Restoration identity and managed-artifact helpers for B-Dental Step 3."""

from __future__ import annotations

import json
import uuid

import bpy
from mathutils import Matrix

from . import properties, scene_utils

RESTORATION_COLLECTION_NAME = "B-Dental Restorations"
RESTORATION_SCHEMA_VERSION = 2
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
    return tuple(
        role
        for role in ("UPPER_JAW", "LOWER_JAW")
        if scene_utils.get_role_object(state, role) is not None
    )


def active_restoration(state):
    return properties.active_restoration_state(state)


def target_scan(state, restoration=None):
    restoration = restoration or active_restoration(state)
    if restoration is None or restoration.target_arch not in {"UPPER_JAW", "LOWER_JAW"}:
        return None
    return scene_utils.get_role_object(state, restoration.target_arch)


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


def tag_margin(obj: bpy.types.Object, restoration) -> None:
    obj[scene_utils.META_MANAGED] = True
    obj[META_ARTIFACT_TYPE] = MARGIN_ARTIFACT_TYPE
    obj[META_RESTORATION_ID] = restoration.restoration_id
    obj[META_TARGET_ROLE] = restoration.target_arch
    obj[META_TARGET_TOOTH] = restoration.target_tooth_fdi
    obj[META_SCHEMA_VERSION] = RESTORATION_SCHEMA_VERSION


def is_managed_margin(obj: bpy.types.Object | None, restoration=None) -> bool:
    if not scene_utils.object_is_alive(obj):
        return False
    try:
        if obj.type != "CURVE" or not bool(obj.get(scene_utils.META_MANAGED, False)):
            return False
        if obj.get(META_ARTIFACT_TYPE) != MARGIN_ARTIFACT_TYPE:
            return False
        if restoration is None:
            return True
        return (
            obj.get(META_RESTORATION_ID) == restoration.restoration_id
            and obj.get(META_TARGET_ROLE) == restoration.target_arch
            and obj.get(META_TARGET_TOOTH) == restoration.target_tooth_fdi
        )
    except (ReferenceError, RuntimeError, AttributeError):
        return False


def find_margin_by_restoration_id(restoration_id: str):
    if not restoration_id:
        return None
    collection = bpy.data.collections.get(RESTORATION_COLLECTION_NAME)
    if collection is None:
        return None
    for obj in collection.objects:
        if is_managed_margin(obj) and obj.get(META_RESTORATION_ID) == restoration_id:
            return obj
    return None


def resolve_margin(restoration):
    if restoration is None:
        return None
    try:
        obj = restoration.margin_object
    except (AttributeError, ReferenceError, RuntimeError):
        obj = None
    if is_managed_margin(obj, restoration):
        return obj
    recovered = find_margin_by_restoration_id(restoration.restoration_id)
    if is_managed_margin(recovered, restoration):
        restoration.margin_object = recovered
        return recovered
    return None


def remove_margin_object(obj: bpy.types.Object | None) -> bool:
    if not scene_utils.object_is_alive(obj):
        return False
    curve = obj.data if obj.type == "CURVE" else None
    bpy.data.objects.remove(obj, do_unlink=True)
    if curve is not None and curve.users == 0:
        bpy.data.curves.remove(curve)
    return True


def remove_restoration_margin(restoration) -> bool:
    obj = resolve_margin(restoration)
    removed = remove_margin_object(obj) if is_managed_margin(obj, restoration) else False
    restoration.margin_object = None
    restoration.margin_candidate_closed = False
    restoration.margin_session_active = False
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
    for restoration in state.restorations:
        obj = resolve_margin(restoration)
        if is_managed_margin(obj):
            objects[obj.as_pointer()] = obj
        restoration.margin_object = None
    removed = sum(1 for obj in objects.values() if remove_margin_object(obj))
    ensure_restoration_collection(scene)
    return removed


def has_managed_restoration_artifacts(scene: bpy.types.Scene, state) -> bool:
    if any(resolve_margin(restoration) is not None for restoration in state.restorations):
        return True
    return any(True for _obj in iter_managed_restoration_artifacts(scene))


def restoration_for_id(state, restoration_id: str):
    for restoration in state.restorations:
        if restoration.restoration_id == restoration_id:
            return restoration
    return None


def duplicate_tooth_exists(state, arch: str, tooth: str, *, exclude_id: str = "") -> bool:
    return any(
        restoration.restoration_id != exclude_id
        and restoration.target_arch == arch
        and restoration.target_tooth_fdi == tooth
        for restoration in state.restorations
    )


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


def initialize_new_restoration_defaults(state) -> None:
    arches = available_target_arches(state)
    if not arches:
        return
    preferred = state.single_arch_role if state.scan_configuration == "SINGLE_ARCH" else state.new_target_arch
    arch = preferred if preferred in arches else arches[0]
    state.internal_update_lock = True
    try:
        state.new_target_arch = arch
        valid_teeth = teeth_for_arch(arch)
        if state.new_target_tooth_fdi not in valid_teeth:
            state.new_target_tooth_fdi = valid_teeth[0]
    finally:
        state.internal_update_lock = False


def migrate_legacy_restoration(state) -> bool:
    """Migrate the earlier in-branch single-restoration state once."""

    if state.legacy_restoration_migrated:
        return False
    state.legacy_restoration_migrated = True
    if not state.restoration_id:
        return False

    restoration = state.restorations.add()
    restoration.restoration_id = state.restoration_id
    restoration.restoration_type = state.restoration_type
    restoration.target_arch = state.target_arch
    restoration.target_tooth_fdi = state.target_tooth_fdi
    restoration.margin_object = state.margin_object
    restoration.margin_session_active = state.margin_session_active
    restoration.margin_candidate_closed = state.margin_candidate_closed
    restoration.warning_acknowledged = state.margin_warning_acknowledged
    restoration.review_confirmed = state.margin_review_confirmed
    restoration.status = "VERIFIED" if state.step_3_valid else (
        "CANDIDATE" if state.margin_object else "READY_FOR_MARGIN"
    )
    restoration.valid = bool(state.step_3_valid)
    restoration.summary = state.step_3_summary
    restoration.errors = state.step_3_errors
    restoration.warnings = state.step_3_warnings
    restoration.margin_point_count = state.margin_point_count
    restoration.margin_path_length = state.margin_path_length
    restoration.margin_mean_surface_distance = state.margin_mean_surface_distance
    restoration.margin_max_surface_distance = state.margin_max_surface_distance
    restoration.margin_session_points = state.margin_session_points
    restoration.margin_session_cyclic = state.margin_session_cyclic
    restoration.margin_session_had_margin = state.margin_session_had_margin
    restoration.margin_session_status = state.margin_session_status
    restoration.margin_session_valid = state.margin_session_valid
    restoration.margin_session_review_confirmed = state.margin_session_review_confirmed
    restoration.margin_session_warning_acknowledged = state.margin_session_warning_acknowledged
    restoration.margin_session_summary = state.margin_session_summary
    restoration.margin_session_errors = state.margin_session_errors
    restoration.margin_session_warnings = state.margin_session_warnings
    restoration.approved_margin_points = state.approved_margin_points
    restoration.approved_target_signature = state.approved_target_signature
    restoration.approved_target_matrix = state.approved_target_matrix
    restoration.approved_upstream_signature = state.approved_upstream_signature
    restoration.target_scan_signature = state.target_scan_signature
    state.active_restoration_index = len(state.restorations) - 1
    properties.sync_step_three_state(state)
    return True
