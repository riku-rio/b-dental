"""Persistent workflow properties for B-Dental."""

from collections.abc import Iterable

import bpy
from bpy.props import BoolProperty, EnumProperty, PointerProperty, StringProperty

WORKFLOW_STEP_ITEMS = (
    ("STEP_1", "Step 1", "Import and validate intra-oral scans"),
    ("STEP_2", "Step 2", "Placeholder for the next workflow stage"),
)

STEP_ONE_STATUS_ITEMS = (
    ("NOT_STARTED", "Not Started", "A dental case has not been initialized"),
    ("INCOMPLETE", "Incomplete", "Step 1 requires input or revalidation"),
    ("VALID", "Valid", "Step 1 passed validation"),
    ("ERROR", "Error", "Step 1 contains blocking validation errors"),
)

SCAN_CONFIGURATION_ITEMS = (
    ("SINGLE_ARCH", "Single Arch", "Import either an upper or lower jaw scan"),
    ("DUAL_ARCH", "Dual Arch", "Import upper and lower jaw scans"),
    (
        "FULL_SCAN_SET",
        "Full Scan Set",
        "Import upper jaw, lower jaw, right bite, and left bite scans",
    ),
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
_SOURCE_UNIT_SCALES = {
    "MILLIMETERS": 0.001,
    "CENTIMETERS": 0.01,
    "METERS": 1.0,
}


def invalidate_step_one(state: "BDENTAL_PG_WorkflowState") -> None:
    """Invalidate Step 1 after a material workflow change."""

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
    finally:
        state.internal_update_lock = False


def _invalidate_update(
    state: "BDENTAL_PG_WorkflowState", context: bpy.types.Context
) -> None:
    del context
    invalidate_step_one(state)


def role_label(role: str) -> str:
    """Return the user-facing label for a scan role."""

    return _ROLE_LABELS.get(role, role.replace("_", " ").title())


def role_pointer_attribute(role: str) -> str:
    """Return the workflow-state pointer attribute for a scan role."""

    try:
        return _ROLE_POINTER_ATTRIBUTES[role]
    except KeyError as exc:
        raise ValueError(f"Unsupported scan role: {role}") from exc


def role_object_name(role: str) -> str:
    """Return the deterministic managed-object name for a scan role."""

    try:
        return _ROLE_OBJECT_NAMES[role]
    except KeyError as exc:
        raise ValueError(f"Unsupported scan role: {role}") from exc


def source_unit_scale(source_unit: str) -> float:
    """Convert unitless STL coordinates into Blender meter-based units."""

    try:
        return _SOURCE_UNIT_SCALES[source_unit]
    except KeyError as exc:
        raise ValueError(f"Unsupported source unit: {source_unit}") from exc


def required_roles(state: "BDENTAL_PG_WorkflowState") -> tuple[str, ...]:
    """Derive required scan roles from the selected configuration."""

    if state.scan_configuration == "SINGLE_ARCH":
        return (state.single_arch_role,)
    if state.scan_configuration == "DUAL_ARCH":
        return ("UPPER_JAW", "LOWER_JAW")
    if state.scan_configuration == "FULL_SCAN_SET":
        return SCAN_ROLES
    return ()


def iter_role_attributes(roles: Iterable[str] = SCAN_ROLES) -> Iterable[tuple[str, str]]:
    """Yield role identifiers and their pointer attributes."""

    for role in roles:
        yield role, role_pointer_attribute(role)


class BDENTAL_PG_WorkflowState(bpy.types.PropertyGroup):
    """Scene-persistent state for the B-Dental workflow."""

    internal_update_lock: BoolProperty(
        name="Internal Update Lock",
        default=False,
        options={"HIDDEN", "SKIP_SAVE"},
    )
    case_initialized: BoolProperty(
        name="Case Initialized",
        default=False,
        description="Whether this scene has an initialized B-Dental case",
    )
    current_step: EnumProperty(
        name="Current Step",
        items=WORKFLOW_STEP_ITEMS,
        default="STEP_1",
    )
    step_1_status: EnumProperty(
        name="Step 1 Status",
        items=STEP_ONE_STATUS_ITEMS,
        default="NOT_STARTED",
    )
    step_1_valid: BoolProperty(
        name="Step 1 Valid",
        default=False,
    )
    scan_configuration: EnumProperty(
        name="Scan Configuration",
        items=SCAN_CONFIGURATION_ITEMS,
        default="SINGLE_ARCH",
        update=_invalidate_update,
    )
    single_arch_role: EnumProperty(
        name="Required Arch",
        items=SINGLE_ARCH_ROLE_ITEMS,
        default="UPPER_JAW",
        update=_invalidate_update,
    )
    source_unit: EnumProperty(
        name="Source Units",
        items=SOURCE_UNIT_ITEMS,
        default="MILLIMETERS",
        update=_invalidate_update,
    )

    upper_jaw: PointerProperty(type=bpy.types.Object)
    lower_jaw: PointerProperty(type=bpy.types.Object)
    right_bite: PointerProperty(type=bpy.types.Object)
    left_bite: PointerProperty(type=bpy.types.Object)

    validation_summary: StringProperty(
        name="Validation Summary",
        default="",
    )
    validation_errors: StringProperty(
        name="Validation Errors",
        default="",
    )
    validation_warnings: StringProperty(
        name="Validation Warnings",
        default="",
    )


CLASSES = (BDENTAL_PG_WorkflowState,)
