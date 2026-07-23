# B-Dental

B-Dental is a custom Blender Extension for building a structured digital dental workflow inside Blender.

The project is developed through small, verifiable versions. Each version defines its requirements, architectural decisions, implementation plan, task checklist, and local verification procedure before the next workflow stage begins.

## Current Version: v0.0.2

Version `v0.0.2` implements the first functional workflow stage:

**Step 1 — Import Intra-Oral Scans**

The extension now supports:

- Explicit dental-case initialization.
- Conservative removal of the untouched Blender startup cube.
- A scene-persistent workflow state.
- Single Arch, Dual Arch, and Full Scan Set configurations.
- Fixed roles for Upper Jaw, Lower Jaw, Right Bite, and Left Bite.
- STL import through Blender's built-in importer.
- Source-unit selection with millimeters as the default.
- Managed scan collections, deterministic names, and object metadata.
- Import, replace, remove, focus, and visibility controls.
- Blocking scan validation and non-blocking geometry warnings.
- Transition to Step 2 only after Step 1 validation succeeds.
- A Step 2 placeholder displaying `Not Implemented Yet.`
- Returning to Step 1 without clearing imported scans.

## Current Status

The `v0.0.2` implementation is complete on:

`feat/v0.0.2-scan-import-workflow`

Local Blender acceptance verification is still required before the version can be accepted and merged into `main`.

The following remain intentionally open until they are executed locally:

- Extension validation and package build.
- Installation and enablement in the project Blender version.
- Clean-scene and existing-scene safety tests.
- STL import and replacement scenarios.
- Validation scenarios for every supported scan configuration.
- Save, close, and reopen persistence.
- Repeated enable, disable, and reload lifecycle tests.

See [`docs/v0.0.2/VERIFICATION.md`](docs/v0.0.2/VERIFICATION.md) for the required procedure and [`docs/v0.0.2/TASKS.md`](docs/v0.0.2/TASKS.md) for the current checklist.

## Previous Version: v0.0.1

Version `v0.0.1` established and locally verified the extension foundation:

- Modern Blender Extension packaging.
- Deterministic registration and unregistration.
- A `B-Dental` panel in the 3D Viewport sidebar.
- Local validation, build, installation, and lifecycle documentation.

It was verified with Blender 5.0.1 on Windows before being merged into `main`.

## Planned Next Workflow Stage

The next version is expected to replace the Step 2 placeholder with:

**Occlusion Registration & Verification**

That stage should distinguish between:

- A jaw relationship already preserved by the scanner export.
- A case that requires registration using right and left bite scans.
- A case that requires manual correction.

Imported alignment must be treated as a candidate until it is inspected and explicitly verified. Planning for that version begins only after `v0.0.2` passes local acceptance and is merged.

## Repository Structure

```text
b-dental/
├── docs/
│   ├── v0.0.1/
│   └── v0.0.2/
└── extension/
    ├── __init__.py
    ├── blender_manifest.toml
    ├── operators.py
    ├── properties.py
    ├── scene_utils.py
    ├── ui.py
    └── validation.py
```

## Development Rules

- Every version must have an explicit scope.
- Registration must not modify the user's scene.
- Destructive actions must be explicit and narrowly scoped.
- Dental workflow state and Blender operator results must remain separate.
- Implemented behavior must not be marked accepted before local verification.
- Each version must leave the repository in a reviewable and reproducible state.
