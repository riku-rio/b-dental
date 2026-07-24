"""MVP antagonist-region workflow integrated into B-Dental Step 3."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable

import bpy
from bpy.props import BoolProperty, FloatProperty, PointerProperty, StringProperty
from mathutils import Matrix, Vector

from . import (
    margin_geometry,
    margin_validation,
    properties,
    restoration_utils,
    scene_utils,
    step_three_operators,
    step_three_session,
    ui,
)

ANTAGONIST_REGION_ARTIFACT_TYPE = "ANTAGONIST_REGION"
MIN_REGION_RADIUS = 0.002
MAX_REGION_RADIUS = 0.015
DEFAULT_REGION_RADIUS = 0.006
SURFACE_WARNING_DISTANCE = 0.00025
SURFACE_BLOCKING_DISTANCE = 0.001
REGION_COLOR = (1.0, 0.15, 0.65, 1.0)


def opposing_arch(target_arch: str) -> str:
    if target_arch == "UPPER_JAW":
        return "LOWER_JAW"
    if target_arch == "LOWER_JAW":
        return "UPPER_JAW"
    return ""


def antagonist_scan(state, restoration=None):
    restoration = restoration or restoration_utils.active_restoration(state)
    if restoration is None:
        return None
    role = opposing_arch(restoration.target_arch)
    return scene_utils.get_role_object(state, role) if role else None


def antagonist_required(state, restoration=None) -> bool:
    return antagonist_scan(state, restoration) is not None


def _is_alive(obj) -> bool:
    return scene_utils.object_is_alive(obj)


def _region_name(restoration) -> str:
    return (
        f"BDENTAL_Antagonist_Region_{restoration.target_tooth_fdi}_"
        f"{restoration.restoration_id[:8]}"
    )


def tag_region(obj: bpy.types.Object, restoration) -> None:
    obj[scene_utils.META_MANAGED] = True
    obj[restoration_utils.META_ARTIFACT_TYPE] = ANTAGONIST_REGION_ARTIFACT_TYPE
    obj[restoration_utils.META_RESTORATION_ID] = restoration.restoration_id
    obj[restoration_utils.META_TARGET_ROLE] = opposing_arch(restoration.target_arch)
    obj[restoration_utils.META_TARGET_TOOTH] = restoration.target_tooth_fdi
    obj[restoration_utils.META_SCHEMA_VERSION] = restoration_utils.RESTORATION_SCHEMA_VERSION


def is_managed_region(obj: bpy.types.Object | None, restoration=None) -> bool:
    if not _is_alive(obj):
        return False
    try:
        if obj.type != "EMPTY" or not bool(obj.get(scene_utils.META_MANAGED, False)):
            return False
        if obj.get(restoration_utils.META_ARTIFACT_TYPE) != ANTAGONIST_REGION_ARTIFACT_TYPE:
            return False
        if restoration is None:
            return True
        return (
            obj.get(restoration_utils.META_RESTORATION_ID) == restoration.restoration_id
            and obj.get(restoration_utils.META_TARGET_ROLE) == opposing_arch(restoration.target_arch)
            and obj.get(restoration_utils.META_TARGET_TOOTH) == restoration.target_tooth_fdi
        )
    except (AttributeError, ReferenceError, RuntimeError):
        return False


def find_region(restoration_id: str):
    if not restoration_id:
        return None
    collection = bpy.data.collections.get(restoration_utils.RESTORATION_COLLECTION_NAME)
    if collection is None:
        return None
    for obj in collection.objects:
        if is_managed_region(obj) and obj.get(restoration_utils.META_RESTORATION_ID) == restoration_id:
            return obj
    return None


def resolve_region(restoration):
    if restoration is None:
        return None
    try:
        obj = restoration.antagonist_region_object
    except (AttributeError, ReferenceError, RuntimeError):
        obj = None
    if is_managed_region(obj, restoration):
        return obj
    recovered = find_region(restoration.restoration_id)
    if is_managed_region(recovered, restoration):
        restoration.antagonist_region_object = recovered
        restoration.antagonist_region_defined = True
        return recovered
    return None


def remove_region_object(obj: bpy.types.Object | None) -> bool:
    if not _is_alive(obj):
        return False
    bpy.data.objects.remove(obj, do_unlink=True)
    return True


def clear_region(restoration, *, remove_object: bool = True) -> bool:
    obj = resolve_region(restoration)
    removed = remove_region_object(obj) if remove_object else False
    restoration.antagonist_region_object = None
    restoration.antagonist_region_defined = False
    restoration.antagonist_region_review_confirmed = False
    restoration.antagonist_region_source = ""
    restoration.antagonist_scan_signature = ""
    restoration.approved_antagonist_signature = ""
    return removed


def ensure_region_object(scene, state, restoration):
    scan = antagonist_scan(state, restoration)
    if scan is None:
        raise ValueError("An opposing arch scan is not available for this restoration.")

    obj = resolve_region(restoration)
    if obj is None:
        obj = bpy.data.objects.new(_region_name(restoration), None)
        restoration_utils.move_to_restoration_collection(obj, scene)
        restoration.antagonist_region_object = obj

    obj.name = _region_name(restoration)
    obj.parent = scan
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = float(restoration.antagonist_region_radius)
    obj.color = REGION_COLOR
    obj.show_in_front = True
    obj.hide_render = True
    obj.hide_viewport = False
    try:
        obj.hide_set(False)
    except (AttributeError, RuntimeError):
        pass
    tag_region(obj, restoration)
    return obj


def margin_world_points(restoration) -> tuple[Vector, ...]:
    margin = restoration_utils.resolve_margin(restoration)
    if margin is None:
        return ()
    return tuple(margin.matrix_world @ point for point in margin_geometry.curve_points(margin))


def suggested_radius(restoration) -> float:
    points = margin_world_points(restoration)
    if not points:
        return DEFAULT_REGION_RADIUS
    center = sum(points, Vector()) / len(points)
    extent = max((point - center).length for point in points)
    return max(MIN_REGION_RADIUS, min(MAX_REGION_RADIUS, extent * 1.35))


def _clear_messages_after_region_change(restoration) -> None:
    restoration.errors = ""
    restoration.warnings = ""
    restoration.review_confirmed = False
    restoration.warning_acknowledged = False


def set_region(
    scene,
    state,
    restoration,
    center_local: Vector,
    *,
    radius: float,
    source: str,
) -> bpy.types.Object:
    scan = antagonist_scan(state, restoration)
    if scan is None:
        raise ValueError("An opposing arch scan is not available for this restoration.")
    if not all(math.isfinite(float(value)) for value in center_local):
        raise ValueError("The antagonist region center is invalid.")

    properties.clear_restoration_approval(restoration)
    obj = ensure_region_object(scene, state, restoration)
    obj.location = center_local

    state.internal_update_lock = True
    try:
        restoration.antagonist_region_radius = max(
            MIN_REGION_RADIUS,
            min(MAX_REGION_RADIUS, float(radius)),
        )
    finally:
        state.internal_update_lock = False

    obj.empty_display_size = float(restoration.antagonist_region_radius)
    restoration.antagonist_region_defined = True
    restoration.antagonist_region_review_confirmed = False
    restoration.antagonist_region_source = source
    restoration.antagonist_scan_signature = restoration_utils.target_scan_signature(scan)
    restoration.status = (
        "CANDIDATE"
        if restoration_utils.resolve_margin(restoration) is not None
        else "READY_FOR_MARGIN"
    )
    restoration.summary = (
        "Antagonist region detected from the margin. Review the region before approval."
        if source == "AUTO"
        else "Antagonist region picked manually. Review the region before approval."
    )
    _clear_messages_after_region_change(restoration)
    properties.sync_step_three_state(state)
    return obj


def auto_detect_region(scene, state, restoration, depsgraph) -> bpy.types.Object:
    points = margin_world_points(restoration)
    if len(points) < margin_geometry.MIN_MARGIN_POINTS:
        raise ValueError("Create a closed margin before detecting the antagonist region.")

    scan = antagonist_scan(state, restoration)
    if scan is None:
        raise ValueError("An opposing arch scan is not available for this restoration.")

    centroid_world = sum(points, Vector()) / len(points)
    centroid_local = scan.matrix_world.inverted_safe() @ centroid_world
    result, location, _normal, _index = scan.closest_point_on_mesh(
        centroid_local,
        distance=1000.0,
        depsgraph=depsgraph,
    )
    if not result:
        raise ValueError("The opposing surface could not be resolved from the margin location.")

    return set_region(
        scene,
        state,
        restoration,
        location.copy(),
        radius=suggested_radius(restoration),
        source="AUTO",
    )


def region_signature(state, restoration) -> str:
    scan = antagonist_scan(state, restoration)
    obj = resolve_region(restoration)
    if scan is None:
        return "NOT_APPLICABLE"
    if obj is None:
        return ""
    payload = {
        "center": [float(value) for value in obj.location],
        "radius": float(restoration.antagonist_region_radius),
        "source": restoration.antagonist_region_source,
        "scan": restoration_utils.target_scan_signature(scan),
        "matrix": restoration_utils.target_matrix_signature(scan),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def validate_region(state, restoration, depsgraph) -> tuple[tuple[str, ...], tuple[str, ...]]:
    scan = antagonist_scan(state, restoration)
    if scan is None:
        return (), ()

    errors: list[str] = []
    warnings: list[str] = []
    obj = resolve_region(restoration)
    if obj is None or not restoration.antagonist_region_defined:
        errors.append("Define an antagonist region on the opposing arch before approval.")
        return tuple(errors), tuple(warnings)

    if not is_managed_region(obj, restoration):
        errors.append("The antagonist region is not owned by the active restoration.")
    if obj.parent is not scan:
        errors.append("The antagonist region is not attached to the expected opposing scan.")
    if restoration.antagonist_scan_signature != restoration_utils.target_scan_signature(scan):
        errors.append("The opposing scan changed after the antagonist region was defined.")

    radius = float(restoration.antagonist_region_radius)
    if not math.isfinite(radius) or not MIN_REGION_RADIUS <= radius <= MAX_REGION_RADIUS:
        errors.append("The antagonist region radius is outside the supported 2 to 15 mm range.")

    center = Vector(obj.location)
    if not all(math.isfinite(float(value)) for value in center):
        errors.append("The antagonist region center contains invalid coordinates.")
    elif not errors:
        result, location, _normal, _index = scan.closest_point_on_mesh(
            center,
            distance=1000.0,
            depsgraph=depsgraph,
        )
        if not result:
            errors.append("The antagonist region center could not be resolved on the opposing scan.")
        else:
            center_world = scan.matrix_world @ center
            location_world = scan.matrix_world @ location
            distance = (center_world - location_world).length
            if distance > SURFACE_BLOCKING_DISTANCE:
                errors.append("The antagonist region center is more than 1.0 mm from the opposing surface.")
            elif distance > SURFACE_WARNING_DISTANCE:
                warnings.append("The antagonist region center is more than 0.25 mm from the opposing surface.")

    return tuple(dict.fromkeys(errors)), tuple(dict.fromkeys(warnings))


def region_ready_for_approval(state, restoration) -> bool:
    if not antagonist_required(state, restoration):
        return True
    return bool(
        restoration.antagonist_region_defined
        and resolve_region(restoration) is not None
        and restoration.antagonist_region_review_confirmed
    )


def _select_only(context, target) -> None:
    for obj in context.view_layer.objects:
        try:
            obj.select_set(False)
        except (ReferenceError, RuntimeError):
            continue
    target.hide_viewport = False
    try:
        target.hide_set(False)
    except (AttributeError, RuntimeError):
        pass
    target.select_set(True)
    context.view_layer.objects.active = target


def _frame_selected(context) -> bool:
    window_manager = context.window_manager
    if window_manager is None:
        return False
    for window in window_manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((item for item in area.regions if item.type == "WINDOW"), None)
            if region is None:
                continue
            try:
                with context.temp_override(
                    window=window,
                    screen=screen,
                    area=area,
                    region=region,
                    space_data=area.spaces.active,
                ):
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                return True
            except (RuntimeError, TypeError):
                continue
    return False


def _clear_modal_status(context) -> None:
    try:
        context.workspace.status_text_set(None)
    except (AttributeError, RuntimeError):
        pass
    try:
        context.area.header_text_set(None)
    except (AttributeError, RuntimeError):
        pass


class BDENTAL_OT_auto_detect_antagonist_region(bpy.types.Operator):
    bl_idname = "bdental.auto_detect_antagonist_region"
    bl_label = "Auto Detect Antagonist Region"
    bl_description = "Locate an opposing surface region from the current margin centroid"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        restoration = restoration_utils.active_restoration(state) if state else None
        margin = restoration_utils.resolve_margin(restoration) if restoration else None
        return bool(
            state
            and restoration
            and state.current_step == "STEP_3"
            and state.step_2_valid
            and not restoration.margin_session_active
            and antagonist_required(state, restoration)
            and margin_geometry.curve_is_cyclic(margin)
        )

    def execute(self, context):
        state = context.scene.bdental_workflow
        restoration = restoration_utils.active_restoration(state)
        try:
            obj = auto_detect_region(
                context.scene,
                state,
                restoration,
                context.evaluated_depsgraph_get(),
            )
            _select_only(context, obj)
        except (RuntimeError, ValueError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        self.report({"INFO"}, "Antagonist region detected. Review and adjust it if needed.")
        return {"FINISHED"}


class BDENTAL_OT_pick_antagonist_region(bpy.types.Operator):
    bl_idname = "bdental.pick_antagonist_region"
    bl_label = "Pick Antagonist Region"
    bl_description = "Click the opposing arch to place the antagonist region center"
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        restoration = restoration_utils.active_restoration(state) if state else None
        margin = restoration_utils.resolve_margin(restoration) if restoration else None
        return bool(
            state
            and restoration
            and state.current_step == "STEP_3"
            and state.step_2_valid
            and not restoration.margin_session_active
            and antagonist_required(state, restoration)
            and margin_geometry.curve_is_cyclic(margin)
        )

    def invoke(self, context, event):
        del event
        if context.area is None or context.area.type != "VIEW_3D" or context.region_data is None:
            self.report({"ERROR"}, "Antagonist picking must start in a 3D Viewport.")
            return {"CANCELLED"}
        state = context.scene.bdental_workflow
        restoration = restoration_utils.active_restoration(state)
        scan = antagonist_scan(state, restoration)
        if scan is None:
            self.report({"ERROR"}, "The opposing arch scan is unavailable.")
            return {"CANCELLED"}
        scan.hide_viewport = False
        try:
            scan.hide_set(False)
        except (AttributeError, RuntimeError):
            pass
        context.window_manager.modal_handler_add(self)
        instructions = "LMB: place antagonist region | MMB/Wheel: navigate | Esc: cancel"
        try:
            context.workspace.status_text_set(instructions)
            context.area.header_text_set(instructions)
        except (AttributeError, RuntimeError):
            pass
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        state = context.scene.bdental_workflow
        restoration = restoration_utils.active_restoration(state)
        scan = antagonist_scan(state, restoration)
        if restoration is None or scan is None:
            _clear_modal_status(context)
            self.report({"ERROR"}, "The active restoration or opposing scan became unavailable.")
            return {"CANCELLED"}

        if event.type == "ESC" and event.value == "PRESS":
            _clear_modal_status(context)
            return {"CANCELLED"}
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            hit = margin_geometry.raycast_target(context, event, scan)
            if hit is None:
                self.report({"WARNING"}, "Click directly on the opposing arch scan.")
                return {"RUNNING_MODAL"}
            try:
                obj = set_region(
                    context.scene,
                    state,
                    restoration,
                    hit,
                    radius=suggested_radius(restoration),
                    source="MANUAL",
                )
                _select_only(context, obj)
            except (RuntimeError, ValueError) as exc:
                _clear_modal_status(context)
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}
            _clear_modal_status(context)
            return {"FINISHED"}
        if event.type in {
            "MIDDLEMOUSE",
            "WHEELUPMOUSE",
            "WHEELDOWNMOUSE",
            "TRACKPADPAN",
            "TRACKPADZOOM",
        }:
            return {"PASS_THROUGH"}
        return {"RUNNING_MODAL"}


class BDENTAL_OT_focus_antagonist_region(bpy.types.Operator):
    bl_idname = "bdental.focus_antagonist_region"
    bl_label = "Focus Antagonist Region"

    def execute(self, context):
        restoration = restoration_utils.active_restoration(context.scene.bdental_workflow)
        obj = resolve_region(restoration)
        if obj is None:
            return {"CANCELLED"}
        _select_only(context, obj)
        _frame_selected(context)
        return {"FINISHED"}


class BDENTAL_OT_toggle_antagonist_region_visibility(bpy.types.Operator):
    bl_idname = "bdental.toggle_antagonist_region_visibility"
    bl_label = "Toggle Antagonist Region Visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        restoration = restoration_utils.active_restoration(context.scene.bdental_workflow)
        obj = resolve_region(restoration)
        if obj is None:
            return {"CANCELLED"}
        obj.hide_viewport = not obj.hide_viewport
        return {"FINISHED"}


class BDENTAL_OT_clear_antagonist_region(bpy.types.Operator):
    bl_idname = "bdental.clear_antagonist_region"
    bl_label = "Clear Antagonist Region"
    bl_description = "Remove only the active restoration's antagonist region"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        state = context.scene.bdental_workflow
        restoration = restoration_utils.active_restoration(state)
        if restoration is None:
            return {"CANCELLED"}
        properties.clear_restoration_approval(restoration)
        clear_region(restoration)
        restoration.status = (
            "CANDIDATE"
            if restoration_utils.resolve_margin(restoration) is not None
            else "READY_FOR_MARGIN"
        )
        restoration.summary = "Antagonist region cleared. Define it again before approval."
        restoration.errors = ""
        restoration.warnings = ""
        properties.sync_step_three_state(state)
        return {"FINISHED"}


CLASSES = (
    BDENTAL_OT_auto_detect_antagonist_region,
    BDENTAL_OT_pick_antagonist_region,
    BDENTAL_OT_focus_antagonist_region,
    BDENTAL_OT_toggle_antagonist_region_visibility,
    BDENTAL_OT_clear_antagonist_region,
)


def _radius_updated(restoration, context) -> None:
    obj = resolve_region(restoration)
    if obj is not None:
        obj.empty_display_size = float(restoration.antagonist_region_radius)

    state = context.scene.bdental_workflow if context and context.scene else None
    if state is None or state.internal_update_lock or not restoration.antagonist_region_defined:
        return

    properties.clear_restoration_approval(restoration)
    restoration.antagonist_region_review_confirmed = False
    if restoration.status == "VERIFIED":
        restoration.status = "CANDIDATE"
    restoration.summary = "Antagonist region radius changed. Review and approve the restoration again."
    properties.sync_step_three_state(state)


def _inject_properties() -> None:
    annotations = properties.BDENTAL_PG_RestorationState.__annotations__
    annotations.setdefault(
        "antagonist_region_object",
        PointerProperty(name="Antagonist Region", type=bpy.types.Object),
    )
    annotations.setdefault(
        "antagonist_region_defined",
        BoolProperty(name="Antagonist Region Defined", default=False),
    )
    annotations.setdefault(
        "antagonist_region_review_confirmed",
        BoolProperty(name="I Reviewed the Antagonist Region", default=False),
    )
    annotations.setdefault(
        "antagonist_region_radius",
        FloatProperty(
            name="Region Radius",
            description="Radius of the opposing surface region reserved for later contact analysis",
            default=DEFAULT_REGION_RADIUS,
            min=MIN_REGION_RADIUS,
            max=MAX_REGION_RADIUS,
            subtype="DISTANCE",
            unit="LENGTH",
            update=_radius_updated,
        ),
    )
    annotations.setdefault(
        "antagonist_region_source",
        StringProperty(name="Antagonist Region Source", default=""),
    )
    annotations.setdefault(
        "antagonist_scan_signature",
        StringProperty(default=""),
    )
    annotations.setdefault(
        "approved_antagonist_signature",
        StringProperty(default=""),
    )
    annotations.setdefault(
        "margin_session_antagonist_review_confirmed",
        BoolProperty(default=False),
    )


def _patch_clear_approval() -> None:
    if hasattr(properties, "_bdental_antagonist_original_clear_restoration_approval"):
        return
    original = properties.clear_restoration_approval
    properties._bdental_antagonist_original_clear_restoration_approval = original

    def wrapped(restoration) -> None:
        original(restoration)
        restoration.antagonist_region_review_confirmed = False
        restoration.approved_antagonist_signature = ""

    properties.clear_restoration_approval = wrapped


def _patch_validation() -> None:
    if hasattr(margin_validation, "_bdental_antagonist_original_validate_margin"):
        return
    original = margin_validation.validate_margin
    margin_validation._bdental_antagonist_original_validate_margin = original

    def wrapped(state, restoration, depsgraph):
        base = original(state, restoration, depsgraph)
        if restoration is None or not antagonist_required(state, restoration):
            return base

        region_errors, region_warnings = validate_region(state, restoration, depsgraph)
        errors = tuple(dict.fromkeys((*base.errors, *region_errors)))
        warnings = tuple(dict.fromkeys((*base.warnings, *region_warnings)))
        ok = not errors
        return margin_validation.MarginValidationResult(
            ok=ok,
            status="CANDIDATE" if ok else "ERROR",
            summary=(
                "Margin and antagonist region passed engineering validation."
                if ok
                else f"Step 3 validation found {len(errors)} blocking error(s)."
            ),
            errors=errors,
            warnings=warnings,
            point_count=base.point_count,
            path_length=base.path_length,
            mean_surface_distance=base.mean_surface_distance,
            max_surface_distance=base.max_surface_distance,
        )

    margin_validation.validate_margin = wrapped


def _patch_session() -> None:
    if not hasattr(step_three_session, "_bdental_antagonist_original_snapshot_previous_state"):
        original_snapshot_state = step_three_session._snapshot_previous_state
        step_three_session._bdental_antagonist_original_snapshot_previous_state = original_snapshot_state

        def snapshot_state(restoration) -> None:
            original_snapshot_state(restoration)
            restoration.margin_session_antagonist_review_confirmed = (
                restoration.antagonist_region_review_confirmed
            )

        step_three_session._snapshot_previous_state = snapshot_state

    if not hasattr(step_three_session, "_bdental_antagonist_original_start_session"):
        original_start = step_three_session.start_session
        step_three_session._bdental_antagonist_original_start_session = original_start

        def start_session(scene, state, restoration):
            margin = original_start(scene, state, restoration)
            restoration.antagonist_region_review_confirmed = False
            return margin

        step_three_session.start_session = start_session

    if not hasattr(step_three_session, "_bdental_antagonist_original_reset_session"):
        original_reset = step_three_session.reset_session
        step_three_session._bdental_antagonist_original_reset_session = original_reset

        def reset_session(state, restoration) -> None:
            original_reset(state, restoration)
            restoration.antagonist_region_review_confirmed = False

        step_three_session.reset_session = reset_session

    if not hasattr(step_three_session, "_bdental_antagonist_original_cancel_session"):
        original_cancel = step_three_session.cancel_session
        step_three_session._bdental_antagonist_original_cancel_session = original_cancel

        def cancel_session(state, restoration) -> None:
            original_cancel(state, restoration)
            restoration.antagonist_region_review_confirmed = (
                restoration.margin_session_antagonist_review_confirmed
            )
            properties.sync_step_three_state(state)

        step_three_session.cancel_session = cancel_session

    if not hasattr(step_three_session, "_bdental_antagonist_original_apply_candidate"):
        original_apply = step_three_session.apply_candidate
        step_three_session._bdental_antagonist_original_apply_candidate = original_apply

        def apply_candidate(state, restoration) -> None:
            original_apply(state, restoration)
            restoration.antagonist_region_review_confirmed = False
            restoration.approved_antagonist_signature = ""

        step_three_session.apply_candidate = apply_candidate

    if not hasattr(step_three_session, "_bdental_antagonist_original_snapshot_approved"):
        original_approved = step_three_session.snapshot_approved
        step_three_session._bdental_antagonist_original_snapshot_approved = original_approved

        def snapshot_approved(state, restoration) -> None:
            original_approved(state, restoration)
            restoration.approved_antagonist_signature = region_signature(state, restoration)

        step_three_session.snapshot_approved = snapshot_approved

    if not hasattr(step_three_session, "_bdental_antagonist_original_monitor_scene"):
        original_monitor = step_three_session.monitor_scene
        step_three_session._bdental_antagonist_original_monitor_scene = original_monitor

        def monitor_scene(scene) -> None:
            original_monitor(scene)
            if not hasattr(scene, "bdental_workflow"):
                return
            state = scene.bdental_workflow
            if state.internal_update_lock or not state.case_initialized:
                return

            for restoration in state.restorations:
                scan = antagonist_scan(state, restoration)
                pointer = getattr(restoration, "antagonist_region_object", None)
                obj = resolve_region(restoration)

                if pointer is not None and not is_managed_region(pointer, restoration):
                    if is_managed_region(pointer):
                        remove_region_object(pointer)
                    restoration.antagonist_region_object = None
                    restoration.antagonist_region_defined = False
                    properties.clear_restoration_approval(restoration)
                    restoration.status = "ERROR"
                    restoration.summary = "The managed antagonist region no longer matches this restoration."
                    continue

                if scan is None:
                    if obj is not None:
                        clear_region(restoration)
                    continue

                current_scan_signature = restoration_utils.target_scan_signature(scan)
                if (
                    restoration.antagonist_scan_signature
                    and current_scan_signature != restoration.antagonist_scan_signature
                ):
                    clear_region(restoration)
                    properties.clear_restoration_approval(restoration)
                    restoration.status = "CANDIDATE" if state.step_2_valid else "UPSTREAM_INVALID"
                    restoration.summary = "The opposing scan changed. Define the antagonist region again."
                    continue

                if restoration.valid:
                    current_signature = region_signature(state, restoration)
                    if not current_signature or current_signature != restoration.approved_antagonist_signature:
                        properties.clear_restoration_approval(restoration)
                        restoration.status = "CANDIDATE" if state.step_2_valid else "UPSTREAM_INVALID"
                        restoration.summary = "Approval was invalidated after the antagonist region changed."

            properties.sync_step_three_state(state)

        step_three_session.monitor_scene = monitor_scene


def _patch_restoration_artifacts() -> None:
    if not hasattr(restoration_utils, "_bdental_antagonist_original_iter_artifacts"):
        original_iter = restoration_utils.iter_managed_restoration_artifacts
        restoration_utils._bdental_antagonist_original_iter_artifacts = original_iter

        def iter_artifacts(scene) -> Iterable[bpy.types.Object]:
            seen: set[int] = set()
            for obj in original_iter(scene):
                pointer = obj.as_pointer()
                if pointer not in seen:
                    seen.add(pointer)
                    yield obj
            collection = bpy.data.collections.get(restoration_utils.RESTORATION_COLLECTION_NAME)
            if collection is None:
                return
            for obj in list(collection.objects):
                if scene.objects.get(obj.name) is obj and is_managed_region(obj):
                    pointer = obj.as_pointer()
                    if pointer not in seen:
                        seen.add(pointer)
                        yield obj

        restoration_utils.iter_managed_restoration_artifacts = iter_artifacts

    if not hasattr(restoration_utils, "_bdental_antagonist_original_remove_all_artifacts"):
        original_remove_all = restoration_utils.remove_all_managed_restoration_artifacts
        restoration_utils._bdental_antagonist_original_remove_all_artifacts = original_remove_all

        def remove_all(scene, state) -> int:
            removed = original_remove_all(scene, state)
            for restoration in state.restorations:
                restoration.antagonist_region_object = None
                restoration.antagonist_region_defined = False
                restoration.antagonist_region_review_confirmed = False
                restoration.antagonist_region_source = ""
                restoration.antagonist_scan_signature = ""
                restoration.approved_antagonist_signature = ""
            return removed

        restoration_utils.remove_all_managed_restoration_artifacts = remove_all


def _patch_remove_restoration_operator() -> None:
    operator = step_three_operators.BDENTAL_OT_remove_restoration
    if hasattr(operator, "_bdental_antagonist_original_execute"):
        return
    original = operator.execute
    operator._bdental_antagonist_original_execute = original

    def execute(self, context):
        restoration = restoration_utils.active_restoration(context.scene.bdental_workflow)
        region = resolve_region(restoration)
        result = original(self, context)
        if result == {"FINISHED"} and region is not None:
            remove_region_object(region)
        return result

    operator.execute = execute


def _patch_approval_operator() -> None:
    operator = step_three_operators.BDENTAL_OT_approve_margin
    if hasattr(operator, "_bdental_antagonist_original_execute"):
        return
    original_execute = operator.execute
    operator._bdental_antagonist_original_execute = original_execute

    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        restoration = restoration_utils.active_restoration(state) if state else None
        return bool(
            restoration
            and restoration.status == "CANDIDATE"
            and not restoration.margin_session_active
            and restoration.review_confirmed
            and not restoration.errors
            and (not restoration.warnings or restoration.warning_acknowledged)
            and region_ready_for_approval(state, restoration)
        )

    def execute(self, context):
        state = context.scene.bdental_workflow
        restoration = restoration_utils.active_restoration(state)
        if antagonist_required(state, restoration) and not restoration.antagonist_region_review_confirmed:
            self.report({"ERROR"}, "Review and confirm the antagonist region before approval.")
            return {"CANCELLED"}
        result = original_execute(self, context)
        if result == {"FINISHED"}:
            restoration.summary = (
                f"Margin and antagonist region approved for FDI {restoration.target_tooth_fdi}. "
                "Engineering checks do not certify clinical correctness."
            )
        return result

    operator.poll = classmethod(poll)
    operator.execute = execute


def _draw_active_restoration(layout, state, context) -> None:
    restoration = restoration_utils.active_restoration(state)
    if restoration is None:
        return
    margin = restoration_utils.resolve_margin(restoration)
    target = restoration_utils.target_scan(state, restoration)

    box = layout.box()
    box.label(
        text=f"Active: FDI {restoration.target_tooth_fdi}",
        icon="TOOTH" if hasattr(bpy.types, "TOOTH") else "MESH_DATA",
    )
    box.label(text=f"Preparation: {properties.role_label(restoration.target_arch)}")
    box.label(text=f"Status: {restoration.status.replace('_', ' ').title()}")
    row = box.row(align=True)
    row.operator("bdental.focus_step_three_target", text="Focus Scan", icon="VIEWZOOM")
    row.operator("bdental.remove_restoration", text="Remove", icon="TRASH")

    margin_box = layout.box()
    margin_box.label(text="Manual Margin", icon="CURVE_DATA")
    if restoration.margin_session_active:
        margin_box.label(text="Reversible session active", icon="REC")
        if context.object is not None and context.object.mode == "EDIT":
            margin_box.operator(
                "bdental.reproject_margin",
                text="Reproject Edited Points",
                icon="MOD_SHRINKWRAP",
            )
            margin_box.operator(
                "bdental.capture_edited_margin",
                text="Capture Edited Candidate",
                icon="CHECKMARK",
            )
        elif restoration.margin_candidate_closed:
            margin_box.operator(
                "bdental.apply_margin_candidate",
                text="Apply Margin Candidate",
                icon="CHECKMARK",
            )
        else:
            ui._draw_wrapped_label(
                margin_box,
                "LMB adds points, Backspace removes, Enter closes, Esc cancels.",
            )
        row = margin_box.row(align=True)
        row.operator("bdental.reset_margin_session", text="Reset", icon="LOOP_BACK")
        row.operator("bdental.cancel_margin_session", text="Cancel", icon="CANCEL")
    elif margin is None:
        draw_row = margin_box.row()
        draw_row.operator_context = "INVOKE_REGION_WIN"
        draw_row.operator("bdental.draw_margin", text="Draw Manual Margin", icon="GREASEPENCIL")
    else:
        point_count = len(margin.data.splines[0].points) if len(margin.data.splines) == 1 else 0
        margin_box.label(text=f"{point_count} curve points")
        row = margin_box.row(align=True)
        row.operator("bdental.focus_margin", text="Focus", icon="VIEWZOOM")
        row.operator(
            "bdental.toggle_margin_visibility",
            text="Show" if margin.hide_viewport else "Hide",
            icon="HIDE_ON" if margin.hide_viewport else "HIDE_OFF",
        )
        redraw = margin_box.row()
        redraw.operator_context = "INVOKE_REGION_WIN"
        redraw.operator("bdental.draw_margin", text="Redraw Margin", icon="GREASEPENCIL")
        margin_box.operator("bdental.prepare_margin_edit", text="Edit Margin Points", icon="EDITMODE_HLT")
        margin_box.operator(
            "bdental.reproject_margin",
            text="Reproject Margin Points",
            icon="MOD_SHRINKWRAP",
        )
        margin_box.operator(
            "bdental.validate_margin",
            text="Run Step 3 Validation",
            icon="FILE_TICK",
        )

    region_box = layout.box()
    region_box.label(text="Antagonist Region", icon="MESH_UVSPHERE")
    scan = antagonist_scan(state, restoration)
    region = resolve_region(restoration)
    if scan is None:
        ui._draw_wrapped_label(
            region_box,
            "No opposing arch is available in this single-arch case.",
            icon="INFO",
        )
    else:
        region_box.label(text=f"Opposing scan: {properties.role_label(opposing_arch(restoration.target_arch))}")
        if margin is None or not margin_geometry.curve_is_cyclic(margin):
            ui._draw_wrapped_label(
                region_box,
                "Create and close the manual margin before defining the antagonist region.",
                icon="INFO",
            )
        else:
            row = region_box.row(align=True)
            row.operator(
                "bdental.auto_detect_antagonist_region",
                text="Auto Detect",
                icon="VIEWZOOM",
            )
            pick = row.operator(
                "bdental.pick_antagonist_region",
                text="Pick on Scan",
                icon="RESTRICT_SELECT_OFF",
            )
            del pick
        if region is not None:
            source = restoration.antagonist_region_source.title() or "Defined"
            region_box.label(text=f"Region source: {source}", icon="CHECKMARK")
            region_box.prop(restoration, "antagonist_region_radius")
            row = region_box.row(align=True)
            row.operator("bdental.focus_antagonist_region", text="Focus", icon="VIEWZOOM")
            row.operator(
                "bdental.toggle_antagonist_region_visibility",
                text="Show" if region.hide_viewport else "Hide",
                icon="HIDE_ON" if region.hide_viewport else "HIDE_OFF",
            )
            row.operator("bdental.clear_antagonist_region", text="Clear", icon="TRASH")
            region_box.prop(restoration, "antagonist_region_review_confirmed")
        else:
            region_box.label(text="Region not defined", icon="INFO")

    ui._draw_messages(layout, restoration.errors, title="Blocking Errors", icon="ERROR")
    ui._draw_messages(layout, restoration.warnings, title="Warnings", icon="INFO")
    if restoration.summary:
        ui._draw_wrapped_label(layout.box(), restoration.summary)
    ui._draw_restoration_diagnostics(layout, restoration)

    if restoration.status == "CANDIDATE" and not restoration.margin_session_active and margin is not None:
        approval = layout.box()
        approval.label(text=f"Approve FDI {restoration.target_tooth_fdi}")
        approval.prop(restoration, "review_confirmed")
        if antagonist_required(state, restoration):
            approval.prop(restoration, "antagonist_region_review_confirmed")
        if restoration.warnings:
            approval.prop(restoration, "warning_acknowledged")
        approval.operator(
            "bdental.approve_margin",
            text=(
                "Approve Margin & Antagonist"
                if antagonist_required(state, restoration)
                else "Approve Manual Margin"
            ),
            icon="CHECKMARK",
        )


def _patch_ui() -> None:
    if hasattr(ui, "_bdental_antagonist_original_draw_active_restoration"):
        return
    ui._bdental_antagonist_original_draw_active_restoration = ui._draw_active_restoration
    ui._draw_active_restoration = _draw_active_restoration


_inject_properties()
_patch_clear_approval()
_patch_validation()
_patch_session()
_patch_restoration_artifacts()
_patch_remove_restoration_operator()
_patch_approval_operator()
_patch_ui()
