"""Persistent workflow properties for B-Dental."""

from collections.abc import Iterable

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)

WORKFLOW_STEP_ITEMS = (
    ("STEP_1", "Step 1", "Import and validate intra-oral scans"),
    ("STEP_2", "Step 2", "Register and verify the occlusal relationship"),
    ("STEP_3", "Step 3", "Configure a restoration and define its manual margin"),
)

STEP_ONE_STATUS_ITEMS = (
    ("NOT_STARTED", "Not Started", "A dental case has not been initialized"),
    ("INCOMPLETE", "Incomplete", "Step 1 requires input or revalidation"),
    ("VALID", "Valid", "Step 1 passed validation"),
    ("ERROR", "Error", "Step 1 contains blocking validation errors"),
)

STEP_TWO_STATUS_ITEMS = (
    ("NOT_STARTED", "Not Started", "Step 2 has not been analyzed"),
    ("NOT_APPLICABLE", "Not Applicable", "Occlusion is not applicable to this case"),
    ("IMPORTED_CANDIDATE", "Imported Candidate", "Imported relationship requires review"),
    ("NEEDS_ALIGNMENT", "Needs Alignment", "The relationship requires correction"),
    ("ALIGNING", "Aligning", "An alignment preview session is active"),
    ("CANDIDATE", "Candidate", "A candidate is ready for engineering checks"),
    ("VERIFIED", "Verified", "The user approved the occlusal relationship"),
    ("ERROR", "Error", "Step 2 contains blocking errors"),
)

STEP_THREE_STATUS_ITEMS = (
    ("NOT_STARTED", "Not Started", "Step 3 has not started"),
    ("SETUP_REQUIRED", "Setup Required", "Restoration setup must be confirmed"),
    ("READY_FOR_MARGIN", "Ready for Margin", "Restoration setup is complete"),
    ("DRAWING", "Drawing", "A reversible manual-margin session is active"),
    ("CANDIDATE", "Candidate", "A closed margin candidate requires validation"),
    ("VERIFIED", "Verified", "The user approved the manual margin"),
    ("UPSTREAM_INVALID", "Upstream Invalid", "Step 1 or Step 2 must be completed again"),
    ("ERROR", "Error", "Step 3 contains blocking errors"),
)

ALIGNMENT_MODE_ITEMS = (
    ("IMPORTED", "Imported", "Preserve and review the imported relationship"),
    ("BITE_GUIDED", "Bite Guided", "Refine using buccal bite scans"),
    ("MANUAL", "Manual", "Position the lower jaw with Blender transform tools"),
)

BITE_SOURCE_ITEMS = (
    ("RIGHT", "Right Bite", "Use the right bite scan"),
    ("LEFT", "Left Bite", "Use the left bite scan"),
    ("BOTH", "Both Bites", "Use right and left bite scans"),
)

SCAN_CONFIGURATION_ITEMS = (
    ("SINGLE_ARCH", "Single Arch", "Import either an upper or lower jaw scan"),
    ("DUAL_ARCH", "Dual Arch", "Import upper and lower jaw scans"),
    ("FULL_SCAN_SET", "Full Scan Set", "Import upper, lower, right bite, and left bite scans"),
)

SINGLE_ARCH_ROLE_ITEMS = (
    ("UPPER_JAW", "Upper Jaw", "Require an upper-jaw scan"),
    ("LOWER_JAW", "Lower Jaw", "Require a lower-jaw scan"),
)

SOURCE_UNIT_ITEMS = (
    ("MILLIMETERS", "Millimeters", "STL coordinates are expressed in millimeters"),
    ("CENTIMETERS", "Centimeters", "STL coordinates are expressed in centimeters"),
    ("METERS", "Meters", "STL coordinates are expressed in meters"),
)

SCAN_ROLE_ITEMS = (
    ("UPPER_JAW", "Upper Jaw", "Upper or maxillary scan"),
    ("LOWER_JAW", "Lower Jaw", "Lower or mandibular scan"),
    ("RIGHT_BITE", "Right Bite", "Right buccal bite scan"),
    ("LEFT_BITE", "Left Bite", "Left buccal bite scan"),
)

TARGET_ARCH_ITEMS = (
    ("UPPER_JAW", "Upper Jaw", "Use the upper jaw as the preparation scan"),
    ("LOWER_JAW", "Lower Jaw", "Use the lower jaw as the preparation scan"),
)

RESTORATION_TYPE_ITEMS = (
    ("ANATOMICAL_CROWN", "Anatomical Crown", "Single-unit anatomical crown"),
)

UPPER_FDI_TEETH = tuple(str(value) for value in (*range(11, 19), *range(21, 29)))
LOWER_FDI_TEETH = tuple(str(value) for value in (*range(31, 39), *range(41, 49)))
_FDI_ITEMS = {
    "UPPER_JAW": tuple((value, f"FDI {value}", f"Permanent tooth {value}") for value in UPPER_FDI_TEETH),
    "LOWER_JAW": tuple((value, f"FDI {value}", f"Permanent tooth {value}") for value in LOWER_FDI_TEETH),
}

SCAN_ROLES = tuple(item[0] for item in SCAN_ROLE_ITEMS)
_ROLE_LABELS = {identifier: label for identifier, label, _description in SCAN_ROLE_ITEMS}
_ROLE_POINTER_ATTRIBUTES = {
    "UPPER_JAW": "upper_jaw",
    "LOWER_JAW": "lower_jaw",
    "RIGHT_BITE": "right_bite",
    "LEFT_BITE": "left_bite",
}
_ROLE_OBJECT_NAMES = {
    "UPPER_JAW": "BDENTAL_Upper_Jaw",
    "LOWER_JAW": "BDENTAL_Lower_Jaw",
    "RIGHT_BITE": "BDENTAL_Right_Bite",
    "LEFT_BITE": "BDENTAL_Left_Bite",
}
_SOURCE_UNIT_SCALES = {"MILLIMETERS": 0.001, "CENTIMETERS": 0.01, "METERS": 1.0}


def target_tooth_items(state, _context):
    return _FDI_ITEMS.get(getattr(state, "target_arch", "UPPER_JAW"), _FDI_ITEMS["UPPER_JAW"])


def clear_step_three_state(state: "BDENTAL_PG_WorkflowState") -> None:
    state.step_3_status = "NOT_STARTED"
    state.step_3_valid = False
    state.restoration_id = ""
    state.restoration_type = "ANATOMICAL_CROWN"
    state.target_arch = "UPPER_JAW"
    state.target_tooth_fdi = "11"
    state.margin_object = None
    state.margin_session_active = False
    state.margin_candidate_closed = False
    state.margin_warning_acknowledged = False
    state.margin_review_confirmed = False
    state.step_3_summary = ""
    state.step_3_errors = ""
    state.step_3_warnings = ""
    state.margin_point_count = 0
    state.margin_path_length = 0.0
    state.margin_mean_surface_distance = 0.0
    state.margin_max_surface_distance = 0.0
    state.margin_session_points = ""
    state.margin_session_cyclic = False
    state.margin_session_had_margin = False
    state.margin_session_status = "NOT_STARTED"
    state.margin_session_valid = False
    state.margin_session_review_confirmed = False
    state.margin_session_warning_acknowledged = False
    state.margin_session_summary = ""
    state.margin_session_errors = ""
    state.margin_session_warnings = ""
    state.approved_margin_points = ""
    state.approved_target_signature = ""
    state.approved_target_matrix = ""
    state.approved_upstream_signature = ""
    state.target_scan_signature = ""


def invalidate_step_three(state: "BDENTAL_PG_WorkflowState", *, upstream: bool = False) -> None:
    state.step_3_valid = False
    state.margin_session_active = False
    state.margin_warning_acknowledged = False
    state.margin_review_confirmed = False
    state.approved_margin_points = ""
    state.approved_target_signature = ""
    state.approved_target_matrix = ""
    state.approved_upstream_signature = ""
    if upstream:
        state.step_3_status = "UPSTREAM_INVALID"
    elif state.restoration_id and state.target_tooth_fdi:
        state.step_3_status = "CANDIDATE" if state.margin_object else "READY_FOR_MARGIN"
    else:
        state.step_3_status = "SETUP_REQUIRED"


def clear_step_two_state(state: "BDENTAL_PG_WorkflowState") -> None:
    state.step_2_status = "NOT_STARTED"
    state.step_2_valid = False
    state.alignment_mode = "IMPORTED"
    state.bite_source = "BOTH"
    state.alignment_session_active = False
    state.candidate_applied = False
    state.warning_acknowledged = False
    state.review_confirmed = False
    state.step_2_summary = ""
    state.step_2_errors = ""
    state.step_2_warnings = ""
    state.verification_method = ""
    state.session_upper_matrix = ""
    state.session_lower_matrix = ""
    state.session_right_bite_matrix = ""
    state.session_left_bite_matrix = ""
    state.approved_upper_matrix = ""
    state.approved_lower_matrix = ""
    state.approved_right_bite_matrix = ""
    state.approved_left_bite_matrix = ""
    state.registration_iterations = 0
    state.registration_inlier_count = 0
    state.registration_inlier_ratio = 0.0
    state.registration_rmse = 0.0
    state.registration_median_distance = 0.0
    state.registration_translation_delta = 0.0
    state.registration_rotation_delta = 0.0
    state.bilateral_translation_disagreement = 0.0
    state.bilateral_rotation_disagreement = 0.0


def invalidate_step_two(state: "BDENTAL_PG_WorkflowState") -> None:
    if state.internal_update_lock:
        return
    state.internal_update_lock = True
    try:
        clear_step_two_state(state)
        invalidate_step_three(state, upstream=True)
    finally:
        state.internal_update_lock = False


def invalidate_step_one(state: "BDENTAL_PG_WorkflowState") -> None:
    if state.internal_update_lock:
        return
    state.internal_update_lock = True
    try:
        state.step_1_valid = False
        state.step_1_status = "INCOMPLETE" if state.case_initialized else "NOT_STARTED"
        state.current_step = "STEP_1"
        state.validation_summary = ""
        state.validation_errors = ""
        state.validation_warnings = ""
        clear_step_two_state(state)
        invalidate_step_three(state, upstream=True)
    finally:
        state.internal_update_lock = False


def _invalidate_update(state: "BDENTAL_PG_WorkflowState", context: bpy.types.Context) -> None:
    del context
    invalidate_step_one(state)


def _invalidate_step_three_setup(state: "BDENTAL_PG_WorkflowState", context: bpy.types.Context) -> None:
    del context
    if state.internal_update_lock:
        return
    state.internal_update_lock = True
    try:
        valid_teeth = UPPER_FDI_TEETH if state.target_arch == "UPPER_JAW" else LOWER_FDI_TEETH
        if state.target_tooth_fdi not in valid_teeth:
            state.target_tooth_fdi = valid_teeth[0]
        state.restoration_id = ""
        state.target_scan_signature = ""
        invalidate_step_three(state)
        state.step_3_status = "SETUP_REQUIRED"
        state.step_3_summary = "Restoration setup changed. Confirm the setup before drawing."
    finally:
        state.internal_update_lock = False


def role_label(role: str) -> str:
    return _ROLE_LABELS.get(role, role.replace("_", " ").title())


def role_pointer_attribute(role: str) -> str:
    try:
        return _ROLE_POINTER_ATTRIBUTES[role]
    except KeyError as exc:
        raise ValueError(f"Unsupported scan role: {role}") from exc


def role_object_name(role: str) -> str:
    try:
        return _ROLE_OBJECT_NAMES[role]
    except KeyError as exc:
        raise ValueError(f"Unsupported scan role: {role}") from exc


def source_unit_scale(source_unit: str) -> float:
    try:
        return _SOURCE_UNIT_SCALES[source_unit]
    except KeyError as exc:
        raise ValueError(f"Unsupported source unit: {source_unit}") from exc


def required_roles(state: "BDENTAL_PG_WorkflowState") -> tuple[str, ...]:
    if state.scan_configuration == "SINGLE_ARCH":
        return (state.single_arch_role,)
    if state.scan_configuration == "DUAL_ARCH":
        return ("UPPER_JAW", "LOWER_JAW")
    if state.scan_configuration == "FULL_SCAN_SET":
        return SCAN_ROLES
    return ()


def iter_role_attributes(roles: Iterable[str] = SCAN_ROLES) -> Iterable[tuple[str, str]]:
    for role in roles:
        yield role, role_pointer_attribute(role)


class BDENTAL_PG_WorkflowState(bpy.types.PropertyGroup):
    internal_update_lock: BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})
    case_initialized: BoolProperty(name="Case Initialized", default=False)
    current_step: EnumProperty(name="Current Step", items=WORKFLOW_STEP_ITEMS, default="STEP_1")
    step_1_status: EnumProperty(name="Step 1 Status", items=STEP_ONE_STATUS_ITEMS, default="NOT_STARTED")
    step_1_valid: BoolProperty(name="Step 1 Valid", default=False)
    step_2_status: EnumProperty(name="Step 2 Status", items=STEP_TWO_STATUS_ITEMS, default="NOT_STARTED")
    step_2_valid: BoolProperty(name="Step 2 Valid", default=False)
    alignment_mode: EnumProperty(name="Alignment Mode", items=ALIGNMENT_MODE_ITEMS, default="IMPORTED")
    bite_source: EnumProperty(name="Bite Source", items=BITE_SOURCE_ITEMS, default="BOTH")
    alignment_session_active: BoolProperty(name="Alignment Session Active", default=False)
    candidate_applied: BoolProperty(name="Candidate Applied", default=False)
    warning_acknowledged: BoolProperty(name="Acknowledge Warnings", default=False)
    review_confirmed: BoolProperty(name="I Reviewed the Occlusion", default=False)

    step_3_status: EnumProperty(name="Step 3 Status", items=STEP_THREE_STATUS_ITEMS, default="NOT_STARTED")
    step_3_valid: BoolProperty(name="Step 3 Valid", default=False)
    restoration_id: StringProperty(name="Restoration ID", default="")
    restoration_type: EnumProperty(name="Restoration Type", items=RESTORATION_TYPE_ITEMS, default="ANATOMICAL_CROWN")
    target_arch: EnumProperty(name="Preparation Arch", items=TARGET_ARCH_ITEMS, default="UPPER_JAW", update=_invalidate_step_three_setup)
    target_tooth_fdi: EnumProperty(name="Target Tooth", items=target_tooth_items, update=_invalidate_step_three_setup)
    margin_object: PointerProperty(name="Margin Object", type=bpy.types.Object)
    margin_session_active: BoolProperty(name="Margin Session Active", default=False)
    margin_candidate_closed: BoolProperty(name="Margin Candidate Closed", default=False)
    margin_warning_acknowledged: BoolProperty(name="Acknowledge Margin Warnings", default=False)
    margin_review_confirmed: BoolProperty(name="I Reviewed the Margin", default=False)

    scan_configuration: EnumProperty(name="Scan Configuration", items=SCAN_CONFIGURATION_ITEMS, default="SINGLE_ARCH", update=_invalidate_update)
    single_arch_role: EnumProperty(name="Required Arch", items=SINGLE_ARCH_ROLE_ITEMS, default="UPPER_JAW", update=_invalidate_update)
    source_unit: EnumProperty(name="Source Units", items=SOURCE_UNIT_ITEMS, default="MILLIMETERS", update=_invalidate_update)

    upper_jaw: PointerProperty(type=bpy.types.Object)
    lower_jaw: PointerProperty(type=bpy.types.Object)
    right_bite: PointerProperty(type=bpy.types.Object)
    left_bite: PointerProperty(type=bpy.types.Object)

    validation_summary: StringProperty(default="")
    validation_errors: StringProperty(default="")
    validation_warnings: StringProperty(default="")
    step_2_summary: StringProperty(default="")
    step_2_errors: StringProperty(default="")
    step_2_warnings: StringProperty(default="")
    verification_method: StringProperty(default="")
    step_3_summary: StringProperty(default="")
    step_3_errors: StringProperty(default="")
    step_3_warnings: StringProperty(default="")

    session_upper_matrix: StringProperty(default="")
    session_lower_matrix: StringProperty(default="")
    session_right_bite_matrix: StringProperty(default="")
    session_left_bite_matrix: StringProperty(default="")
    approved_upper_matrix: StringProperty(default="")
    approved_lower_matrix: StringProperty(default="")
    approved_right_bite_matrix: StringProperty(default="")
    approved_left_bite_matrix: StringProperty(default="")

    registration_iterations: IntProperty(default=0, min=0)
    registration_inlier_count: IntProperty(default=0, min=0)
    registration_inlier_ratio: FloatProperty(default=0.0, min=0.0, max=1.0)
    registration_rmse: FloatProperty(default=0.0, min=0.0)
    registration_median_distance: FloatProperty(default=0.0, min=0.0)
    registration_translation_delta: FloatProperty(default=0.0, min=0.0)
    registration_rotation_delta: FloatProperty(default=0.0, min=0.0)
    bilateral_translation_disagreement: FloatProperty(default=0.0, min=0.0)
    bilateral_rotation_disagreement: FloatProperty(default=0.0, min=0.0)

    margin_point_count: IntProperty(default=0, min=0)
    margin_path_length: FloatProperty(default=0.0, min=0.0)
    margin_mean_surface_distance: FloatProperty(default=0.0, min=0.0)
    margin_max_surface_distance: FloatProperty(default=0.0, min=0.0)
    margin_session_points: StringProperty(default="")
    margin_session_cyclic: BoolProperty(default=False)
    margin_session_had_margin: BoolProperty(default=False)
    margin_session_status: StringProperty(default="NOT_STARTED")
    margin_session_valid: BoolProperty(default=False)
    margin_session_review_confirmed: BoolProperty(default=False)
    margin_session_warning_acknowledged: BoolProperty(default=False)
    margin_session_summary: StringProperty(default="")
    margin_session_errors: StringProperty(default="")
    margin_session_warnings: StringProperty(default="")
    approved_margin_points: StringProperty(default="")
    approved_target_signature: StringProperty(default="")
    approved_target_matrix: StringProperty(default="")
    approved_upstream_signature: StringProperty(default="")
    target_scan_signature: StringProperty(default="")


CLASSES = (BDENTAL_PG_WorkflowState,)
