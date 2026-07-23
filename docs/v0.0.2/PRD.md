# Product Requirements Document: v0.0.2

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.2
- **Status:** Proposed
- **Target implementation branch:** `feat/v0.0.2-scan-import-workflow`

## Product Overview

B-Dental is a custom Blender extension developed through small, verifiable milestones. Version `v0.0.2` introduces the first functional dental workflow stage: initialize a new dental case, import one or more intra-oral STL scans, validate the required scan set, and advance to a placeholder second step.

The existing B-Dental panel in the 3D Viewport sidebar remains the workflow entry point. The panel changes its displayed content according to the current workflow step instead of opening a separate operating-system window or replacing the Blender workspace.

## Problem Statement

The extension foundation from `v0.0.1` proves that B-Dental can be installed, enabled, displayed, and cleanly unregistered. The project now needs a first domain-specific workflow that safely modifies the scene only after explicit user action, imports dental scan geometry, records the role of every scan, validates the result, and provides a deterministic transition to the next workflow stage.

A generic STL import is not sufficient because B-Dental must know whether each imported object represents an upper jaw, lower jaw, right bite, or left bite. It must also distinguish a successful Blender operator execution from a successful dental workflow validation.

## Version Goal

Create Step 1 of the B-Dental workflow with the following behavior:

1. The user explicitly starts a new dental case.
2. B-Dental safely removes the untouched default cube when present.
3. The user selects a supported scan configuration.
4. The user imports the required intra-oral STL scans into named role slots.
5. B-Dental validates the required scan assignments and imported mesh objects.
6. Successful validation sets the Step 1 application status to true and changes the active workflow step to Step 2.
7. Step 2 displays the exact placeholder text `Not Implemented Yet.`

## User Stories

- As a dental Blender user, I want to start a new B-Dental case so that the scene is prepared without deleting unrelated work.
- As a dental Blender user, I want to import an STL scan into a specific dental role so that the workflow understands what the object represents.
- As a dental Blender user, I want to import either one arch, two arches, or a complete scan set so that the workflow supports common intra-oral scan exports.
- As a dental Blender user, I want clear validation errors when scans are missing or invalid so that I can correct the case before continuing.
- As a dental Blender user, I want successful validation to advance the interface to Step 2 while preserving the imported scans.

## In Scope

- A two-step workflow displayed inside the existing B-Dental 3D Viewport sidebar panel.
- Scene-persistent B-Dental workflow state.
- An explicit `Start New Dental Case` action.
- Safe detection and removal of the untouched Blender default cube.
- Creation and reuse of a `B-Dental Scans` collection.
- Scan configurations:
  - Single Arch.
  - Dual Arch.
  - Full Scan Set.
- Single-arch role selection:
  - Upper Jaw.
  - Lower Jaw.
- Fixed scan roles:
  - Upper Jaw.
  - Lower Jaw.
  - Right Bite.
  - Left Bite.
- STL file selection and import through Blender's built-in STL importer.
- Source-unit selection with millimeters as the default.
- Deterministic object naming and B-Dental metadata tags.
- Import, replace, remove, focus, and visibility actions for scan slots.
- Required scan-set validation.
- Basic imported mesh validation.
- Validation errors and non-blocking warnings.
- Step 1 application status independent from Blender operator return values.
- Transition to Step 2 after successful validation.
- Step 2 placeholder content reading `Not Implemented Yet.`
- A `Back to Step 1` action that preserves imported scans.
- Extension validation, package build, installation, lifecycle, and manual acceptance documentation.

## Out of Scope

- Automatic jaw alignment or occlusion registration.
- Bite alignment calculations.
- Scan cleanup, smoothing, hole filling, remeshing, decimation, or sculpting.
- Automatic scan-role assignment based on geometry.
- Guaranteed role assignment based only on filenames.
- Bulk multi-file role-assignment UI.
- DICOM, PLY, OBJ, glTF, or proprietary scanner formats.
- Patient demographics or protected health information.
- Database, cloud, network, or external service integration.
- Case export or report generation.
- Step 2 production functionality.
- Dedicated Blender workspace or custom editor.
- Third-party Python dependencies.
- Public extension repository distribution.

## Workflow Model

### Step 1: Import Intra-Oral Scans

Step 1 is active when `current_step` is `STEP_1`.

The interface must allow the user to:

- Start or reset a B-Dental case.
- Select a scan configuration.
- Select source units.
- Import scans into the displayed role slots.
- Inspect the imported scan summary.
- Replace, remove, focus, or hide a scan.
- Run `Validate & Continue`.

### Step 2: Placeholder

Step 2 is active when `current_step` is `STEP_2`.

The interface must:

- Confirm that Step 1 is complete.
- Display the exact text `Not Implemented Yet.`
- Provide `Back to Step 1`.
- Preserve all imported scan objects and slot assignments.

## Supported Scan Configurations

### Single Arch

The user selects one required role:

- Upper Jaw, or
- Lower Jaw.

Only the selected role is required for validation.

### Dual Arch

Required roles:

- Upper Jaw.
- Lower Jaw.

Right and left bite scans are not required.

### Full Scan Set

Required roles:

- Upper Jaw.
- Lower Jaw.
- Right Bite.
- Left Bite.

## Functional Requirements

### Workflow State

- **FR-001:** The extension must register scene-persistent workflow state through a Blender `PropertyGroup` attached to `bpy.types.Scene`.
- **FR-002:** The workflow state must include `current_step`, `step_1_status`, and `step_1_valid`.
- **FR-003:** `current_step` must support at least `STEP_1` and `STEP_2`.
- **FR-004:** `step_1_status` must support at least `NOT_STARTED`, `INCOMPLETE`, `VALID`, and `ERROR`.
- **FR-005:** The workflow state must persist when the `.blend` file is saved and reopened.
- **FR-006:** Importing, replacing, removing, or reassigning a scan must invalidate the previous Step 1 validation result.

### Case Initialization

- **FR-007:** Enabling or registering the extension must not delete or modify scene objects.
- **FR-008:** The panel must provide an explicit `Start New Dental Case` action.
- **FR-009:** Starting a new case must initialize B-Dental workflow state and set `current_step` to `STEP_1`.
- **FR-010:** Starting a new case must create or reuse a collection named `B-Dental Scans`.
- **FR-011:** Starting a new case may delete the Blender default cube only when it matches the accepted untouched-default-cube checks.
- **FR-012:** Starting a new case must not delete cameras, lights, unrelated meshes, user-created objects, or a modified cube.
- **FR-013:** Resetting a previously initialized B-Dental case must require user confirmation when managed scan objects or assignments would be removed.

### Scan Configuration

- **FR-014:** The user must be able to select `Single Arch`, `Dual Arch`, or `Full Scan Set`.
- **FR-015:** In `Single Arch`, the user must select `Upper Jaw` or `Lower Jaw` as the required role.
- **FR-016:** The UI must derive required roles from the selected configuration.
- **FR-017:** Changing the configuration must invalidate the prior validation result.

### STL Import

- **FR-018:** Each displayed scan role must provide an `Import STL` action when empty.
- **FR-019:** The file browser must filter for `.stl` files.
- **FR-020:** The implementation must use Blender's built-in STL import operator.
- **FR-021:** The import must enable Blender mesh validation.
- **FR-022:** Millimeters must be the default source unit.
- **FR-023:** Imported objects must be detected by comparing the object set before and after the STL import operation.
- **FR-024:** A successful role import must produce exactly one assigned mesh object for that slot.
- **FR-025:** An imported scan must be moved into the `B-Dental Scans` collection.
- **FR-026:** An imported scan must receive a deterministic B-Dental name for its role.
- **FR-027:** An imported scan must be tagged with B-Dental-managed metadata, its dental role, and its source path when available.
- **FR-028:** Cancelling file selection must leave the scene and workflow state unchanged.
- **FR-029:** A failed import must not remove or replace an existing valid slot assignment.

### Scan Slot Actions

- **FR-030:** A populated scan slot must display its role and imported object or source filename.
- **FR-031:** A populated slot must provide `Focus`, `Replace`, and `Remove` actions.
- **FR-032:** A populated slot must provide a visibility control.
- **FR-033:** `Focus` must select the assigned object, make it active, and frame it in an available 3D Viewport when context permits.
- **FR-034:** `Replace` must retain the existing scan until the replacement import succeeds.
- **FR-035:** `Remove` must clear the role assignment and remove the managed scan object after confirmation when destructive removal is required.
- **FR-036:** The same object must not be assigned to more than one dental role.

### Validation

- **FR-037:** The panel must provide a `Validate & Continue` action.
- **FR-038:** Validation must check that every required role has an assigned object.
- **FR-039:** Every assigned required object must still exist in Blender data.
- **FR-040:** Every assigned required object must be a mesh.
- **FR-041:** Every assigned required mesh must contain at least one vertex and one polygon.
- **FR-042:** Every assigned required object must have non-zero dimensions.
- **FR-043:** Validation must reject non-finite coordinate or dimension values.
- **FR-044:** Validation must reject duplicate role assignments.
- **FR-045:** Validation must reject a role whose assigned object is not tagged as B-Dental-managed for that role.
- **FR-046:** Validation must return a structured result containing success, errors, and warnings.
- **FR-047:** Missing required scans and invalid mesh data must be blocking errors.
- **FR-048:** Scale anomalies, non-manifold geometry, open boundaries, disconnected islands, and unusually high polygon counts may be warnings and must not block this milestone by default.
- **FR-049:** Validation failure must set `step_1_valid` to false, set `step_1_status` to `ERROR`, keep `current_step` at `STEP_1`, and display actionable errors.
- **FR-050:** Validation success must set `step_1_valid` to true, set `step_1_status` to `VALID`, and change `current_step` to `STEP_2`.
- **FR-051:** The validation operator must return a normal Blender operator result independently of the B-Dental validation boolean.

### Step Navigation

- **FR-052:** The panel content must be selected from workflow state rather than by opening a new window.
- **FR-053:** Step 2 must display `Not Implemented Yet.` exactly.
- **FR-054:** Step 2 must provide `Back to Step 1`.
- **FR-055:** Returning to Step 1 must preserve imported scans and their assignments.
- **FR-056:** Step 2 must not be reachable through the normal UI unless Step 1 validation succeeds.

### Registration and Packaging

- **FR-057:** All new classes and scene properties must register and unregister deterministically.
- **FR-058:** Unregistration must remove the custom scene pointer property.
- **FR-059:** Repeated enable, disable, and script-reload cycles must not create duplicate registrations.
- **FR-060:** The extension manifest must be updated to version `0.0.2` and package all required Python modules.

## Non-Functional Requirements

- **NFR-001:** The implementation must continue using Blender's modern Extensions packaging model.
- **NFR-002:** The milestone must support Blender 4.2 or newer and be verified with the project's current Blender test version.
- **NFR-003:** The implementation must not require third-party dependencies.
- **NFR-004:** Extension registration must have no destructive scene side effects.
- **NFR-005:** Destructive actions must be explicit and narrowly scoped.
- **NFR-006:** Operators should support Blender undo where practical.
- **NFR-007:** Object operations must not depend on the user's previous selection state unless selection is the purpose of the action.
- **NFR-008:** Managed objects must be identified by metadata rather than object names alone.
- **NFR-009:** Validation logic should be separable from UI drawing and operator orchestration.
- **NFR-010:** Registration, state, operators, validation, scene utilities, and UI should be split into focused modules.
- **NFR-011:** User-facing errors must explain the role and corrective action.
- **NFR-012:** The panel must remain usable within normal 3D Viewport sidebar width.
- **NFR-013:** The implementation must not store patient-identifying data.
- **NFR-014:** Source paths stored in the `.blend` file must not be treated as portable or guaranteed to remain valid.
- **NFR-015:** The implementation must not assume that the extension installation directory is writable.

## Proposed Source Structure

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

Responsibilities:

- `__init__.py`: registration orchestration only.
- `properties.py`: workflow state, role enums, and configuration enums.
- `operators.py`: case initialization, scan import, slot actions, validation, and navigation.
- `scene_utils.py`: safe default-cube detection, collection management, object tagging, and object lookup helpers.
- `validation.py`: structured Step 1 validation rules and result model.
- `ui.py`: conditional Step 1 and Step 2 panel drawing.

## Acceptance Criteria

Version `v0.0.2` is accepted when all of the following are verified locally:

1. The manifest validates and the extension package builds.
2. The extension installs and enables without B-Dental-related errors.
3. The B-Dental sidebar initially displays Step 1.
4. Enabling the extension does not modify the scene.
5. `Start New Dental Case` removes an untouched default cube when present.
6. `Start New Dental Case` does not remove a modified cube or unrelated objects.
7. The `B-Dental Scans` collection is created or reused correctly.
8. Single Arch supports either an upper-jaw or lower-jaw required scan.
9. Dual Arch requires upper and lower scans.
10. Full Scan Set requires upper, lower, right-bite, and left-bite scans.
11. A user can import an STL into each relevant scan slot.
12. Imported scans are moved, renamed, tagged, and assigned correctly.
13. File-browser cancellation has no side effects.
14. Replacement is transactional and preserves the old scan when the new import fails.
15. Missing required roles fail validation with clear errors.
16. Empty or invalid meshes fail validation.
17. Non-blocking geometry concerns are reported as warnings.
18. Failed validation keeps the workflow on Step 1 with `step_1_valid = false`.
19. Successful validation sets `step_1_valid = true` and switches to Step 2.
20. Step 2 displays `Not Implemented Yet.` exactly.
21. `Back to Step 1` preserves the imported scans and assignments.
22. Changing or removing scans after returning to Step 1 invalidates the previous success state.
23. Saving and reopening the `.blend` file preserves workflow state and valid object pointers.
24. Disabling and re-enabling the extension completes without duplicate registrations or leftover scene properties.
25. Validation, build, installation, and manual acceptance steps are documented and reproducible.

## Assumptions and Constraints

- Development and verification are performed locally on Windows using PowerShell commands.
- Blender's built-in STL importer is available in supported Blender builds.
- Most intra-oral scan STL files are expressed in millimeters, but the user remains responsible for selecting the correct source unit.
- Dental scan meshes may intentionally contain open boundaries; watertight geometry is not required in this milestone.
- Filename parsing may be added later as a convenience but cannot be authoritative for dental role assignment.
- The 3D Viewport sidebar remains suitable for this milestone; the dedicated-workspace decision will be revisited only when workflow size justifies it.

## Completion Rule

This document remains `Proposed` until its requirements are reviewed and approved. Implementation begins only after the PRD, plan, tasks, decisions, and verification plan are aligned.
