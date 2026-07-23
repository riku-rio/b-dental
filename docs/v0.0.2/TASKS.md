# Tasks: v0.0.2

## Documentation

- [x] V002-001 Define the v0.0.2 product requirements.
- [x] V002-002 Record the scan-import workflow implementation plan.
- [x] V002-003 Record the safe case-initialization decision.
- [x] V002-004 Record the fixed scan-slot and configuration decision.
- [x] V002-005 Record the workflow-state and step-navigation decision.
- [x] V002-006 Record the local verification plan.
- [ ] V002-007 Review and approve the v0.0.2 documentation set.

## Project Structure

- [ ] V002-008 Create `extension/properties.py`.
- [ ] V002-009 Create `extension/operators.py`.
- [ ] V002-010 Create `extension/scene_utils.py`.
- [ ] V002-011 Create `extension/validation.py`.
- [ ] V002-012 Create `extension/ui.py`.
- [ ] V002-013 Refactor `extension/__init__.py` into registration orchestration.
- [ ] V002-014 Update `extension/blender_manifest.toml` to version `0.0.2`.
- [ ] V002-015 Add all required Python modules to manifest build paths.

## Workflow State

- [ ] V002-016 Define the workflow-step enum.
- [ ] V002-017 Define the Step 1 status enum.
- [ ] V002-018 Define the scan-configuration enum.
- [ ] V002-019 Define the single-arch role enum.
- [ ] V002-020 Define the source-unit enum.
- [ ] V002-021 Define object pointer properties for upper jaw, lower jaw, right bite, and left bite.
- [ ] V002-022 Define Step 1 validity and validation-message properties.
- [ ] V002-023 Attach the workflow `PropertyGroup` to `bpy.types.Scene`.
- [ ] V002-024 Remove the scene pointer property during unregistration.
- [ ] V002-025 Verify workflow state persists after saving and reopening a `.blend` file.

## Case Initialization

- [ ] V002-026 Implement safe untouched-default-cube detection.
- [ ] V002-027 Ensure default-cube detection checks object type, transform, and primitive mesh characteristics.
- [ ] V002-028 Implement narrow removal of only the accepted untouched default cube.
- [ ] V002-029 Implement creation or reuse of the `B-Dental Scans` collection.
- [ ] V002-030 Implement `bdental.start_case`.
- [ ] V002-031 Initialize workflow state to Step 1.
- [ ] V002-032 Ensure extension registration has no scene-modification side effects.
- [ ] V002-033 Add confirmation before destructive reset of an initialized case.
- [ ] V002-034 Verify modified cubes and unrelated scene objects remain untouched.

## Scan Configuration

- [ ] V002-035 Implement `Single Arch`, `Dual Arch`, and `Full Scan Set` options.
- [ ] V002-036 Implement upper/lower selection for Single Arch.
- [ ] V002-037 Implement required-role derivation for every configuration.
- [ ] V002-038 Invalidate Step 1 validation when configuration changes.
- [ ] V002-039 Invalidate Step 1 validation when single-arch role changes.

## STL Import

- [ ] V002-040 Implement the STL file-selection operator.
- [ ] V002-041 Filter the file browser to `.stl` files.
- [ ] V002-042 Call Blender's built-in `bpy.ops.wm.stl_import` operator.
- [ ] V002-043 Enable Blender mesh validation during import.
- [ ] V002-044 Implement millimeters as the default source unit.
- [ ] V002-045 Implement source-unit to import-scale conversion.
- [ ] V002-046 Detect newly imported objects through before/after object-set comparison.
- [ ] V002-047 Reject imports that do not produce exactly one assignable mesh object.
- [ ] V002-048 Move imported scan objects into `B-Dental Scans`.
- [ ] V002-049 Apply deterministic B-Dental object names by role.
- [ ] V002-050 Tag managed objects with B-Dental metadata, role, and source path.
- [ ] V002-051 Preserve scene and state when the file browser is cancelled.
- [ ] V002-052 Preserve the previous slot object when replacement import fails.
- [ ] V002-053 Restore prior selection state where appropriate after import failures.

## Scan Slot Actions

- [ ] V002-054 Implement `bdental.focus_scan`.
- [ ] V002-055 Implement `bdental.replace_scan` or replacement mode in the import operator.
- [ ] V002-056 Implement `bdental.remove_scan`.
- [ ] V002-057 Implement slot visibility control.
- [ ] V002-058 Prevent one object from being assigned to more than one role.
- [ ] V002-059 Clear stale pointers safely when a managed object is deleted outside the panel.
- [ ] V002-060 Invalidate Step 1 status after import, replacement, removal, or reassignment.

## Validation

- [ ] V002-061 Define an immutable structured validation-result model.
- [ ] V002-062 Implement required-role presence validation.
- [ ] V002-063 Validate that assigned objects still exist.
- [ ] V002-064 Validate that assigned objects are meshes.
- [ ] V002-065 Validate non-empty vertex and polygon counts.
- [ ] V002-066 Validate non-zero object dimensions.
- [ ] V002-067 Validate finite coordinate and dimension values.
- [ ] V002-068 Validate unique object assignment across roles.
- [ ] V002-069 Validate B-Dental management and role metadata.
- [ ] V002-070 Add non-blocking scale warnings.
- [ ] V002-071 Add non-blocking topology warnings where practical.
- [ ] V002-072 Implement `bdental.validate_step_one`.
- [ ] V002-073 Keep Blender operator completion separate from B-Dental validation success.
- [ ] V002-074 Set Step 1 status and errors correctly on validation failure.
- [ ] V002-075 Set `step_1_valid = true` and advance to Step 2 on validation success.

## User Interface

- [ ] V002-076 Replace the foundation placeholder draw function with workflow-aware UI.
- [ ] V002-077 Add a workflow header and Step 1 indicator.
- [ ] V002-078 Add `Start New Dental Case`.
- [ ] V002-079 Add scan-configuration controls.
- [ ] V002-080 Add source-unit control.
- [ ] V002-081 Draw only the scan slots relevant to the selected configuration.
- [ ] V002-082 Show empty-slot import actions.
- [ ] V002-083 Show populated-slot filename or object summary.
- [ ] V002-084 Show `Focus`, `Replace`, `Remove`, and visibility actions.
- [ ] V002-085 Show validation readiness, errors, and warnings.
- [ ] V002-086 Add the primary `Validate & Continue` action.
- [ ] V002-087 Draw Step 2 when `current_step` is `STEP_2`.
- [ ] V002-088 Display `Not Implemented Yet.` exactly in Step 2.
- [ ] V002-089 Add `Back to Step 1` while preserving scans and assignments.
- [ ] V002-090 Verify the UI remains usable at normal sidebar width.

## Registration Lifecycle

- [ ] V002-091 Define deterministic module and class registration order.
- [ ] V002-092 Unregister classes in reverse order.
- [ ] V002-093 Verify repeated enable and disable cycles.
- [ ] V002-094 Verify script reload during development does not create duplicate registrations.
- [ ] V002-095 Verify no B-Dental scene property remains after disabling the extension.

## Validation and Local Verification

- [ ] V002-096 Validate the extension manifest.
- [ ] V002-097 Build the `0.0.2` extension package.
- [ ] V002-098 Inspect the ZIP contents for required modules and no development-only files.
- [ ] V002-099 Install the package locally in Blender.
- [ ] V002-100 Verify the extension enables without errors.
- [ ] V002-101 Run the clean-startup-scene acceptance scenario.
- [ ] V002-102 Run the existing-user-scene safety scenario.
- [ ] V002-103 Run Single Arch upper-jaw validation.
- [ ] V002-104 Run Single Arch lower-jaw validation.
- [ ] V002-105 Run Dual Arch validation.
- [ ] V002-106 Run Full Scan Set validation.
- [ ] V002-107 Verify missing-role validation errors.
- [ ] V002-108 Verify invalid or empty mesh validation errors.
- [ ] V002-109 Verify import cancellation has no side effects.
- [ ] V002-110 Verify failed replacement preserves the existing scan.
- [ ] V002-111 Verify successful validation advances to Step 2.
- [ ] V002-112 Verify Step 2 displays the exact placeholder text.
- [ ] V002-113 Verify returning to Step 1 preserves scans.
- [ ] V002-114 Verify scan changes invalidate the previous valid state.
- [ ] V002-115 Verify save, close, and reopen persistence.
- [ ] V002-116 Review the Blender console for B-Dental errors.

## Documentation and Completion

- [ ] V002-117 Record final PowerShell validation and build commands.
- [ ] V002-118 Record package installation steps.
- [ ] V002-119 Record executed manual acceptance results.
- [ ] V002-120 Update the PRD status after acceptance.
- [ ] V002-121 Update the implementation plan with actual results and deviations.
- [ ] V002-122 Check every completed task only after local verification.
- [ ] V002-123 Confirm every PRD acceptance criterion.
- [ ] V002-124 Prepare v0.0.2 for review and squash merge.

## Completion Rule

Version `v0.0.2` is complete only when:

- The documentation set is approved.
- All implementation tasks are checked.
- All acceptance criteria in `PRD.md` pass locally.
- The extension validates, builds, installs, enables, and completes its registration lifecycle.
- Step 1 imports and validates the supported scan configurations.
- Successful validation advances to Step 2.
- Step 2 displays `Not Implemented Yet.` exactly.
- `VERIFICATION.md` contains the actual completed verification record.
