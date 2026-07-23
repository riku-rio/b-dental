# Product Requirements Document: v0.0.2

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.2
- **Status:** Implementation Complete; Local Acceptance Pending
- **Target branch:** `feat/v0.0.2-scan-import-workflow`
- **Target merge branch:** `main`

## Product Overview

Version `v0.0.2` introduces the first functional B-Dental workflow stage: initialize a dental case, import intra-oral STL scans into explicit dental roles, validate the scan set, and advance to a placeholder second step.

The workflow remains inside the existing B-Dental panel in the 3D Viewport sidebar. No separate operating-system window or replacement workspace is introduced.

## Version Goal

Step 1 must allow the user to:

1. Explicitly start a new dental case.
2. Safely remove only an untouched Blender startup cube when present.
3. Select Single Arch, Dual Arch, or Full Scan Set.
4. Import scans into Upper Jaw, Lower Jaw, Right Bite, and Left Bite slots as required.
5. Validate role assignments and imported mesh data.
6. Set `step_1_valid = true` only after successful B-Dental validation.
7. Change the panel to Step 2 after validation succeeds.
8. Display `Not Implemented Yet.` in Step 2.

## In Scope

- Scene-persistent workflow state through a Blender `PropertyGroup`.
- Explicit case initialization with no registration-time scene changes.
- Conservative startup-cube detection and removal.
- Creation and reuse of `B-Dental Scans`.
- Single Arch, Dual Arch, and Full Scan Set configurations.
- Upper Jaw, Lower Jaw, Right Bite, and Left Bite role slots.
- Millimeter, centimeter, and meter source-unit options.
- STL import through Blender's built-in importer with mesh validation enabled.
- Deterministic managed-object names and B-Dental metadata.
- Import, replace, remove, focus, show, and hide actions.
- Blocking validation errors and non-blocking geometry warnings.
- Step 1 and Step 2 conditional panel navigation.
- Returning to Step 1 without clearing imported scans.
- Modern Blender Extension packaging without third-party dependencies.

## Out of Scope

- Automatic jaw alignment or occlusion registration.
- Bite-based registration calculations.
- Clinical occlusion approval.
- Scan cleanup, smoothing, hole filling, remeshing, or sculpting.
- Automatic scan-role classification.
- Bulk multi-file assignment.
- Formats other than STL.
- Patient demographics or protected health information.
- Network, database, or cloud integration.
- Production Step 2 behavior.

## Supported Configurations

### Single Arch

The user selects one required role:

- Upper Jaw, or
- Lower Jaw.

### Dual Arch

Required roles:

- Upper Jaw.
- Lower Jaw.

### Full Scan Set

Required roles:

- Upper Jaw.
- Lower Jaw.
- Right Bite.
- Left Bite.

## Functional Requirements

### Workflow State

- **FR-001:** Register scene-persistent B-Dental workflow state.
- **FR-002:** Include `current_step`, `step_1_status`, and `step_1_valid`.
- **FR-003:** Support `STEP_1` and `STEP_2`.
- **FR-004:** Support `NOT_STARTED`, `INCOMPLETE`, `VALID`, and `ERROR` Step 1 states.
- **FR-005:** Persist state and object pointers in saved `.blend` files.
- **FR-006:** Invalidate Step 1 after material scan or configuration changes.

### Case Initialization

- **FR-007:** Registration must not modify the scene.
- **FR-008:** Provide `Start New Dental Case`.
- **FR-009:** Initialize the workflow at Step 1.
- **FR-010:** Create or reuse `B-Dental Scans`.
- **FR-011:** Remove the default cube only when conservative untouched-cube checks pass.
- **FR-012:** Preserve modified cubes and unrelated scene objects.
- **FR-013:** Require confirmation before destructive case reset.

### Configuration and Import

- **FR-014:** Support all three scan configurations.
- **FR-015:** Support upper/lower selection for Single Arch.
- **FR-016:** Derive required roles from configuration.
- **FR-017:** Invalidate prior validation after configuration changes.
- **FR-018:** Provide role-specific STL import actions.
- **FR-019:** Filter the file browser to `.stl`.
- **FR-020:** Use `bpy.ops.wm.stl_import`.
- **FR-021:** Enable Blender mesh validation during import.
- **FR-022:** Default source units to millimeters.
- **FR-023:** Detect imported objects by comparing object sets before and after import.
- **FR-024:** Accept exactly one assignable mesh per role import.
- **FR-025:** Move managed scans into `B-Dental Scans`.
- **FR-026:** Apply deterministic names and role metadata.
- **FR-027:** Store source-path metadata when available.
- **FR-028:** File-browser cancellation must have no workflow side effects.
- **FR-029:** Failed replacement must preserve the previous valid assignment.

### Slot Actions

- **FR-030:** Display role and object or source-file summary.
- **FR-031:** Provide Focus, Replace, and Remove.
- **FR-032:** Provide visibility control.
- **FR-033:** Focus must select, activate, and frame the scan when context permits.
- **FR-034:** Replacement must be transactional.
- **FR-035:** Remove must clear the slot and delete only the managed object after confirmation.
- **FR-036:** Prevent the same object from occupying multiple roles.

### Validation

- **FR-037:** Provide `Validate & Continue`.
- **FR-038:** Require every role needed by the selected configuration.
- **FR-039:** Reject missing or stale object assignments.
- **FR-040:** Require mesh objects.
- **FR-041:** Require vertices and polygons.
- **FR-042:** Require non-zero dimensions.
- **FR-043:** Reject non-finite transforms or dimensions.
- **FR-044:** Reject duplicate object assignments.
- **FR-045:** Require matching B-Dental management and role metadata.
- **FR-046:** Return a structured result with success, errors, and warnings.
- **FR-047:** Treat missing and invalid required meshes as blocking errors.
- **FR-048:** Treat scale and topology concerns as non-blocking warnings in this version.
- **FR-049:** Failed validation must remain on Step 1 and set an error state.
- **FR-050:** Successful validation must set `step_1_valid = true`, set status to `VALID`, and advance to Step 2.
- **FR-051:** Blender operator completion must remain separate from B-Dental validation success.

### Navigation and Packaging

- **FR-052:** Draw panel content from workflow state.
- **FR-053:** Display `Not Implemented Yet.` exactly in Step 2.
- **FR-054:** Provide `Back to Step 1`.
- **FR-055:** Preserve imported scans when returning.
- **FR-056:** Do not expose Step 2 through normal UI before successful validation.
- **FR-057:** Register and unregister classes deterministically.
- **FR-058:** Remove the Scene pointer property during unregistration.
- **FR-059:** Support repeated lifecycle operations without duplicate registrations.
- **FR-060:** Package version `0.0.2` with all required modules.

## Non-Functional Requirements

- Use Blender's modern Extensions model.
- Support Blender 4.2 or newer.
- Require no third-party Python dependencies.
- Keep destructive actions explicit and narrow.
- Prefer direct data operations over selection-dependent deletion.
- Identify managed objects through metadata, not names alone.
- Keep state, operators, validation, scene utilities, and UI in focused modules.
- Keep the panel usable at normal sidebar width.
- Store no patient-identifying data.
- Do not assume source paths remain valid or portable.
- Do not assume the extension installation directory is writable.

## Implementation Record

The implementation now contains:

```text
extension/
├── __init__.py
├── blender_manifest.toml
├── operators.py
├── properties.py
├── scene_utils.py
├── ui.py
└── validation.py
```

All planned implementation layers are present. The manifest is set to version `0.0.2` and includes every required Python module.

## Acceptance Criteria

The version is accepted only after local verification confirms:

1. Manifest validation and package build pass.
2. Installation and enablement complete without B-Dental errors.
3. Registration does not modify the scene.
4. Safe case initialization behaves correctly in clean and existing scenes.
5. Every supported scan configuration imports and validates correctly.
6. Cancellation and failed replacement preserve state.
7. Validation failure remains on Step 1.
8. Validation success advances to Step 2.
9. Step 2 displays `Not Implemented Yet.` exactly.
10. Returning to Step 1 preserves scans.
11. Save, close, and reopen preserve workflow state.
12. Repeated lifecycle operations leave no duplicate classes or stale Scene properties.

## Completion Status

Implementation is complete. Acceptance is pending execution and recording of the local Blender scenarios in [`VERIFICATION.md`](VERIFICATION.md).

The next version must not begin until this version is accepted and merged into `main`.
