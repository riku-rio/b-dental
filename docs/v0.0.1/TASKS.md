# Tasks: v0.0.1

## Documentation

- [x] V001-001 Define the v0.0.1 product requirements.
- [x] V001-002 Record the extension foundation implementation plan.
- [x] V001-003 Record the initial Blender UI entry-point decision.
- [x] V001-004 Review and approve the v0.0.1 documentation set.

## Project Structure

- [x] V001-005 Create the Blender extension source directory.
- [x] V001-006 Create `blender_manifest.toml`.
- [x] V001-007 Create the Python package entry point.
- [x] V001-008 Define which files are included in the distributable extension package.

## Extension Registration

- [x] V001-009 Implement `register()`.
- [x] V001-010 Implement `unregister()`.
- [x] V001-011 Register the B-Dental panel class.
- [ ] V001-012 Verify that repeated enable, disable, and reload cycles do not produce duplicate-registration errors.

## User Interface

- [x] V001-013 Add a `B-Dental` tab to the 3D Viewport sidebar.
- [x] V001-014 Add a B-Dental panel inside the tab.
- [x] V001-015 Display the exact text `Not Implemented Yet.`
- [ ] V001-016 Verify that disabling the extension removes its interface elements.

## Validation and Local Verification

- [ ] V001-017 Validate the extension manifest with Blender's extension validator.
- [ ] V001-018 Build the extension package with Blender's extension tooling.
- [ ] V001-019 Install the built package locally in Blender.
- [ ] V001-020 Enable the extension and verify that no Python errors occur.
- [ ] V001-021 Verify that the B-Dental tab and panel are visible.
- [ ] V001-022 Verify that the placeholder text is correct.
- [ ] V001-023 Disable the extension and verify clean unregistration.
- [ ] V001-024 Review the Blender console for registration, runtime, or cleanup errors.

## Documentation and Completion

- [x] V001-025 Document the local validation and build commands.
- [x] V001-026 Document the local installation and enablement steps.
- [x] V001-027 Document the manual acceptance test.
- [ ] V001-028 Confirm that every PRD acceptance criterion is satisfied.
- [ ] V001-029 Update this checklist after local Blender verification.
- [ ] V001-030 Prepare v0.0.1 for review before merging into `main`.

## Current Verification State

A repository-side static check has confirmed that:

- `extension/blender_manifest.toml` parses as valid TOML.
- The required manifest fields used by this milestone are present.
- `extension/__init__.py` compiles as valid Python syntax.
- The build allowlist contains only `__init__.py` and `blender_manifest.toml`.

These checks do not replace Blender's own extension validation, package build, installation, registration, UI, or cleanup tests. Complete the remaining tasks using [`VERIFICATION.md`](./VERIFICATION.md).

## Completion Rule

Version `v0.0.1` is complete only when all required tasks above are checked and every acceptance criterion in [`PRD.md`](./PRD.md) has been verified.
