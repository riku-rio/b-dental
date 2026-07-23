# Tasks: v0.0.2

## Documentation

- [x] V002-001 Define the v0.0.2 product requirements.
- [x] V002-002 Record the scan-import workflow implementation plan.
- [x] V002-003 Record the safe case-initialization decision.
- [x] V002-004 Record the fixed scan-slot and configuration decision.
- [x] V002-005 Record the workflow-state and step-navigation decision.
- [x] V002-006 Record the local verification plan.
- [x] V002-007 Review and approve the v0.0.2 documentation set.

## Project Structure

- [x] V002-008 Create `extension/properties.py`.
- [x] V002-009 Create `extension/operators.py`.
- [x] V002-010 Create `extension/scene_utils.py`.
- [x] V002-011 Create `extension/validation.py`.
- [x] V002-012 Create `extension/ui.py`.
- [x] V002-013 Refactor `extension/__init__.py` into registration orchestration.
- [x] V002-014 Update `extension/blender_manifest.toml` to version `0.0.2`.
- [x] V002-015 Add all required Python modules to manifest build paths.

## Workflow State

- [x] V002-016 Define the workflow-step enum.
- [x] V002-017 Define the Step 1 status enum.
- [x] V002-018 Define the scan-configuration enum.
- [x] V002-019 Define the single-arch role enum.
- [x] V002-020 Define the source-unit enum.
- [x] V002-021 Define object pointer properties for upper jaw, lower jaw, right bite, and left bite.
- [x] V002-022 Define Step 1 validity and validation-message properties.
- [x] V002-023 Attach the workflow `PropertyGroup` to `bpy.types.Scene`.
- [x] V002-024 Remove the scene pointer property during unregistration.
- [x] V002-025 Verify workflow state persists after saving and reopening a `.blend` file.

## Case Initialization

- [x] V002-026 Implement safe untouched-default-cube detection.
- [x] V002-027 Ensure default-cube detection checks object type, transform, and primitive mesh characteristics.
- [x] V002-028 Implement narrow removal of only the accepted untouched default cube.
- [x] V002-029 Implement creation or reuse of the `B-Dental Scans` collection.
- [x] V002-030 Implement `bdental.start_case`.
- [x] V002-031 Initialize workflow state to Step 1.
- [x] V002-032 Ensure extension registration has no scene-modification side effects.
- [x] V002-033 Add confirmation before destructive reset of an initialized case.
- [x] V002-034 Verify modified cubes and unrelated scene objects remain untouched.

## Scan Configuration

- [x] V002-035 Implement `Single Arch`, `Dual Arch`, and `Full Scan Set` options.
- [x] V002-036 Implement upper/lower selection for Single Arch.
- [x] V002-037 Implement required-role derivation for every configuration.
- [x] V002-038 Invalidate Step 1 validation when configuration changes.
- [x] V002-039 Invalidate Step 1 validation when single-arch role changes.

## STL Import

- [x] V002-040 Implement the STL file-selection operator.
- [x] V002-041 Filter the file browser to `.stl` files.
- [x] V002-042 Call Blender's built-in `bpy.ops.wm.stl_import` operator.
- [x] V002-043 Enable Blender mesh validation during import.
- [x] V002-044 Implement millimeters as the default source unit.
- [x] V002-045 Implement source-unit to import-scale conversion.
- [x] V002-046 Detect newly imported objects through before/after object-set comparison.
- [x] V002-047 Reject imports that do not produce exactly one assignable mesh object.
- [x] V002-048 Move imported scan objects into `B-Dental Scans`.
- [x] V002-049 Apply deterministic B-Dental object names by role.
- [x] V002-050 Tag managed objects with B-Dental metadata, role, and source path.
- [x] V002-051 Preserve scene and state when the file browser is cancelled.
- [x] V002-052 Preserve the previous slot object when replacement import fails.
- [x] V002-053 Restore prior selection state where appropriate after import failures.

## Scan Slot Actions

- [x] V002-054 Implement `bdental.focus_scan`.
- [x] V002-055 Implement replacement mode in the import operator.
- [x] V002-056 Implement `bdental.remove_scan`.
- [x] V002-057 Implement slot visibility control.
- [x] V002-058 Prevent one object from being assigned to more than one role.
- [x] V002-059 Clear stale pointers safely when a managed object is deleted outside the panel.
- [x] V002-060 Invalidate Step 1 status after import, replacement, removal, or reassignment.

## Validation

- [x] V002-061 Define an immutable structured validation-result model.
- [x] V002-062 Implement required-role presence validation.
- [x] V002-063 Validate that assigned objects still exist.
- [x] V002-064 Validate that assigned objects are meshes.
- [x] V002-065 Validate non-empty vertex and polygon counts.
- [x] V002-066 Validate non-zero object dimensions.
- [x] V002-067 Validate finite coordinate and dimension values.
- [x] V002-068 Validate unique object assignment across roles.
- [x] V002-069 Validate B-Dental management and role metadata.
- [x] V002-070 Add non-blocking scale warnings.
- [x] V002-071 Add non-blocking topology warnings where practical.
- [x] V002-072 Implement `bdental.validate_step_one`.
- [x] V002-073 Keep Blender operator completion separate from B-Dental validation success.
- [x] V002-074 Set Step 1 status and errors correctly on validation failure.
- [x] V002-075 Set `step_1_valid = true` and advance to Step 2 on validation success.

## User Interface

- [x] V002-076 Replace the foundation placeholder draw function with workflow-aware UI.
- [x] V002-077 Add a workflow header and Step 1 indicator.
- [x] V002-078 Add `Start New Dental Case`.
- [x] V002-079 Add scan-configuration controls.
- [x] V002-080 Add source-unit control.
- [x] V002-081 Draw only the scan slots relevant to the selected configuration.
- [x] V002-082 Show empty-slot import actions.
- [x] V002-083 Show populated-slot filename or object summary.
- [x] V002-084 Show `Focus`, `Replace`, `Remove`, and visibility actions.
- [x] V002-085 Show validation readiness, errors, and warnings.
- [x] V002-086 Add the primary `Validate & Continue` action.
- [x] V002-087 Draw Step 2 when `current_step` is `STEP_2`.
- [x] V002-088 Display `Not Implemented Yet.` exactly in Step 2.
- [x] V002-089 Add `Back to Step 1` while preserving scans and assignments.
- [x] V002-090 Verify the UI remains usable at normal sidebar width.

## Registration Lifecycle

- [x] V002-091 Define deterministic module and class registration order.
- [x] V002-092 Unregister classes in reverse order.
- [x] V002-093 Verify repeated enable and disable cycles.
- [x] V002-094 Verify script reload during development does not create duplicate registrations.
- [x] V002-095 Verify no B-Dental scene property remains after disabling the extension.

## Validation and Local Verification

- [x] V002-096 Validate the extension manifest.
- [x] V002-097 Build the `0.0.2` extension package.
- [x] V002-098 Inspect the ZIP contents for required modules and no development-only files.
- [x] V002-099 Install the package locally in Blender.
- [x] V002-100 Verify the extension enables without errors.
- [x] V002-101 Run the clean-startup-scene acceptance scenario.
- [x] V002-102 Run the existing-user-scene safety scenario.
- [x] V002-103 Run Single Arch upper-jaw validation.
- [x] V002-104 Run Single Arch lower-jaw validation.
- [x] V002-105 Run Dual Arch validation.
- [x] V002-106 Run Full Scan Set validation.
- [x] V002-107 Verify missing-role validation errors.
- [x] V002-108 Verify invalid or empty mesh validation errors.
- [x] V002-109 Verify import cancellation has no side effects.
- [x] V002-110 Verify failed replacement preserves the existing scan.
- [x] V002-111 Verify successful validation advances to Step 2.
- [x] V002-112 Verify Step 2 displays the exact placeholder text.
- [x] V002-113 Verify returning to Step 1 preserves scans.
- [x] V002-114 Verify scan changes invalidate the previous valid state.
- [x] V002-115 Verify save, close, and reopen persistence.
- [x] V002-116 Review the Blender console for B-Dental errors.

## Documentation and Completion

- [x] V002-117 Record final PowerShell validation and build commands.
- [x] V002-118 Record package installation steps.
- [x] V002-119 Record executed manual acceptance results.
- [x] V002-120 Update the PRD status after acceptance.
- [x] V002-121 Update the implementation plan with actual results and deviations.
- [x] V002-122 Check every completed task only after local verification.
- [x] V002-123 Confirm every PRD acceptance criterion.
- [x] V002-124 Prepare v0.0.2 for review and squash merge.

## Verification Summary

Version `v0.0.2` was implemented and locally verified successfully.

Confirmed results:

- The extension manifest validated.
- The `0.0.2` package built and installed successfully.
- The extension enabled without B-Dental-related errors.
- Safe case initialization preserved unrelated scene objects.
- All supported scan configurations imported and validated.
- Failed and cancelled imports preserved existing workflow state.
- Successful validation advanced to Step 2.
- Step 2 displayed `Not Implemented Yet.` exactly.
- Workflow state persisted after saving and reopening the `.blend` file.
- Registration and unregistration completed cleanly.

## Completion Rule

All implementation tasks and acceptance criteria for `v0.0.2` are complete. The version is ready for review and squash merge into `main`.
