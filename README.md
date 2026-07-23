# B-Dental

B-Dental is a custom Blender Extension for building a structured digital dental workflow inside Blender.

The project is developed through small, verifiable versions. Each version defines its requirements, architectural decisions, implementation plan, task checklist, and local verification procedure before the next workflow stage begins.

## Current Version: v0.0.3

Version `v0.0.3` implements and verifies the second workflow stage:

**Step 2 — Occlusion Registration & Verification**

The extension now supports:

- Preserving the scanner-imported upper-to-lower relationship until the user chooses an action.
- Treating imported jaw relationships as unverified candidates rather than automatically accepting or moving them.
- Single Arch completion as explicitly not applicable.
- Dual Arch imported-relationship analysis and manual alignment.
- Full Scan Set registration using Right Bite, Left Bite, or Both Bites.
- Bite-mediated registration without direct upper-to-lower ICP.
- A fixed upper jaw and a moving lower jaw during registration.
- Reversible alignment sessions with start, reset, cancel, capture, and apply actions.
- Deterministic world-space sampling, robust correspondence filtering, and bounded rigid ICP.
- Registration metrics, warnings, gross-separation checks, and bilateral bite disagreement diagnostics.
- Explicit review confirmation and warning acknowledgment before approval.
- `step_2_valid` becoming true only after explicit approval or confirmed Single Arch completion.
- Persistent Step 2 state, matrices, metrics, method, and verification summary.
- Safe Step 2 invalidation when Step 1 inputs or approved transforms materially change.
- Context-sensitive Step 2 UI at normal Blender sidebar width.

## Project Status

Version `v0.0.3` is implemented and locally verified on branch:

`feat/v0.0.3-occlusion-registration-verification`

The extension manifest is versioned as `0.0.3`, the required modules are included in the build, Step 1 remains regression-free, and the Step 2 workflow has passed the documented local scenario matrix.

See:

- [`docs/v0.0.3/PRD.md`](docs/v0.0.3/PRD.md)
- [`docs/v0.0.3/plans/0001-occlusion-registration-verification.md`](docs/v0.0.3/plans/0001-occlusion-registration-verification.md)
- [`docs/v0.0.3/TASKS.md`](docs/v0.0.3/TASKS.md)
- [`docs/v0.0.3/VERIFICATION.md`](docs/v0.0.3/VERIFICATION.md)
- [`docs/v0.0.3/decisions/`](docs/v0.0.3/decisions/)

## Previous Version: v0.0.2

Version `v0.0.2` implemented and verified **Step 1 — Import Intra-Oral Scans**:

- Explicit dental-case initialization.
- Scene-persistent workflow state.
- Single Arch, Dual Arch, and Full Scan Set configurations.
- Fixed Upper Jaw, Lower Jaw, Right Bite, and Left Bite roles.
- STL import through Blender's built-in importer.
- Managed scan objects, validation, focus, visibility, replacement, and removal controls.
- Transition to Step 2 only after Step 1 validation succeeds.

## Planned Next Workflow Stage

The next release is planned as `v0.0.4` and will implement **Step 3**.

Step 3 requirements, architectural decisions, plan, tasks, and verification criteria must be approved before implementation begins. Version `v0.0.3` intentionally contains no production Step 3 behavior.

## Repository Structure

```text
b-dental/
├── docs/
│   ├── v0.0.1/
│   ├── v0.0.2/
│   └── v0.0.3/
│       ├── decisions/
│       ├── plans/
│       ├── PRD.md
│       ├── TASKS.md
│       └── VERIFICATION.md
└── extension/
    ├── __init__.py
    ├── alignment.py
    ├── blender_manifest.toml
    ├── occlusion_validation.py
    ├── operators.py
    ├── properties.py
    ├── scene_utils.py
    ├── step_two_operators.py
    ├── step_two_session.py
    ├── ui.py
    └── validation.py
```

## Development Rules

- Every version must have an explicit scope.
- Registration must not modify the user's scene.
- Destructive actions must be explicit and narrowly scoped.
- Dental workflow state and Blender operator results must remain separate.
- Imported occlusion is a candidate until the user explicitly approves it.
- Registration metrics are engineering aids and are not clinical certification.
- Implemented behavior must be locally verified before a version is accepted.
- Each version must leave the repository in a reviewable and reproducible state.
- Completed release branches are merged with **Squash and merge**.
