# Plan 0001: Extension Foundation

## Metadata

- **Version:** v0.0.1
- **Status:** Planned
- **Target branch:** `feat/v0.0.1-foundation`
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related tasks:** [`../TASKS.md`](../TASKS.md)
- **Related decision:** [`../decisions/0001-use-3d-viewport-sidebar-panel.md`](../decisions/0001-use-3d-viewport-sidebar-panel.md)

## Objective

Build the smallest valid B-Dental Blender Extension that can be installed locally, enabled, accessed through Blender's interface, and used to display `Not Implemented Yet.`

This plan establishes only the technical foundation. It does not implement dental workflows or production features.

## Current State

- The repository contains an initial `README.md`.
- No Blender extension package exists.
- No manifest or Python entry point exists.
- No Blender UI classes are registered.
- No build, installation, or verification workflow is documented.

## Target State

At completion:

- The repository contains a modern Blender Extension package.
- The package has a valid manifest and Python entry point.
- The extension registers a B-Dental panel in the 3D Viewport sidebar.
- The panel displays `Not Implemented Yet.`
- The extension can be built, installed, enabled, disabled, and verified locally.
- The implementation remains deliberately small and ready for later expansion.

## Proposed Repository Structure

```text
b-dental/
├── README.md
├── docs/
│   └── v0.0.1/
│       ├── PRD.md
│       ├── TASKS.md
│       ├── plans/
│       │   └── 0001-extension-foundation.md
│       └── decisions/
│           └── 0001-use-3d-viewport-sidebar-panel.md
└── extension/
    ├── blender_manifest.toml
    └── __init__.py
```

The exact distributable contents will be kept minimal. Documentation remains outside the extension package unless packaging requirements justify including selected files.

## Implementation Phases

### Phase 1: Create the Extension Package

- Create the extension source directory.
- Add a modern `blender_manifest.toml`.
- Declare the extension identity, version, Blender compatibility, license, and required metadata.
- Avoid permissions and external dependencies unless later requirements make them necessary.

### Phase 2: Create the Python Entry Point

- Add the extension's `__init__.py`.
- Define the UI panel class.
- Define explicit `register()` and `unregister()` functions.
- Keep the class registry small and deterministic.

### Phase 3: Add the Initial User Interface

- Target the 3D Viewport sidebar.
- Create a sidebar category labeled `B-Dental`.
- Add a panel labeled `B-Dental`.
- Render the exact placeholder text `Not Implemented Yet.`
- Do not add buttons, properties, operators, or hidden behavior.

### Phase 4: Validate and Build

- Run Blender's extension validation workflow against the package.
- Correct manifest or package-layout errors.
- Build the distributable archive using Blender's supported extension tooling.
- Confirm that the archive contains only the expected extension files.

### Phase 5: Install and Verify Locally

- Install the built extension through Blender's local extension installation workflow.
- Enable B-Dental.
- Open the 3D Viewport sidebar and select the `B-Dental` tab.
- Confirm that the panel and exact placeholder text appear.
- Disable and re-enable the extension.
- Confirm clean unregistration and the absence of duplicate-class errors.

### Phase 6: Document Completion

- Record the validation and build commands.
- Record installation and manual test steps.
- Update [`../TASKS.md`](../TASKS.md).
- Verify every acceptance criterion in [`../PRD.md`](../PRD.md).

## Planned Blender UI

- **Editor:** 3D Viewport
- **Region:** Sidebar (`UI` region)
- **Category:** `B-Dental`
- **Panel label:** `B-Dental`
- **Content:** `Not Implemented Yet.`

This placement follows the decision recorded in [`../decisions/0001-use-3d-viewport-sidebar-panel.md`](../decisions/0001-use-3d-viewport-sidebar-panel.md).

## Validation Strategy

The version will use a small manual acceptance test supported by Blender's extension validation and build commands.

The verification must confirm:

1. The manifest is valid.
2. The extension archive builds successfully.
3. Blender accepts the local installation.
4. Enabling the extension produces no Python errors.
5. The `B-Dental` sidebar category appears.
6. The panel displays the exact placeholder text.
7. Disabling the extension removes the registered interface.
8. Repeated enable and disable cycles remain error-free.

## Risks and Mitigations

### Blender Version Compatibility

**Risk:** Manifest fields or APIs may differ across Blender versions.

**Mitigation:** Declare an explicit minimum Blender version and validate using the selected development version before implementation is considered complete.

### Registration Errors

**Risk:** Reloading the extension may cause duplicate class registration.

**Mitigation:** Keep a single deterministic class registry and ensure `unregister()` reverses registration order cleanly.

### Premature Architecture

**Risk:** The foundation could introduce abstractions that are unnecessary for a one-panel milestone.

**Mitigation:** Implement only the files and classes required by the PRD. Add structure later when concrete features require it.

## Rollback Strategy

If the extension fails during local verification:

- Disable or uninstall the local B-Dental extension.
- Return to the latest known-good commit.
- Rebuild the package after correcting the isolated manifest or Python registration issue.
- Do not modify Blender's internal installation files manually.

## Completion Criteria

This plan is complete when:

- All functional requirements in the PRD are implemented.
- All acceptance criteria pass.
- All required tasks in `TASKS.md` are checked.
- The extension can be installed, enabled, displayed, disabled, and re-enabled locally without errors.
- No functionality outside the v0.0.1 scope has been introduced.
