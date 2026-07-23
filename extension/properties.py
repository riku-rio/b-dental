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


def clear_step_two_state(state: "BDENTAL_PG_WorkflowState") -> None:
    """Clear Step 2 status, session data, metrics, and approval."""

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
    """Invalidate Step 2 while preserving imported objects."""

    if state.internal_update_lock:
        return
    state.internal_update_lock = True
    try:
        clear_step_two_state(state)
    finally:
        state.internal_update_lock = False


def invalidate_step_one(state: "BDENTAL_PG_WorkflowState") -> None:
    """Invalidate Step 1 and all dependent Step 2 results."""

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
    finally:
        state.internal_update_lock = False


def _invalidate_update(state: "BDENTAL_PG_WorkflowState", context: bpy.types.Context) -> None:
    del context
    invalidate_step_one(state)


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
    """Scene-persistent state for the B-Dental workflow."""

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


CLASSES = (BDENTAL_PG_WorkflowState,)
