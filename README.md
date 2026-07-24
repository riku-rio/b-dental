# B-Dental

B-Dental is a custom Blender Extension for building a structured digital dental workflow inside Blender.

The project is developed through small, verifiable releases. Each release defines requirements, architectural decisions, an implementation plan, a task checklist, and a local verification record before the next workflow stage begins.

## Current Version: v0.0.4

Version `v0.0.4` implements and verifies:

**Step 3 — Multiple Restorations, Manual Margins & Antagonist Regions**

The extension now supports:

- Multiple independent single-unit anatomical crown restorations in one case.
- Upper- and lower-arch restorations when the required scans are available.
- Permanent FDI tooth identifiers with duplicate-target rejection.
- One managed, target-local, closed manual-margin Curve per restoration.
- Clearly visible margin display and an always-visible viewport overlay.
- Reversible drawing and editing sessions with reset, cancel, capture, and apply behavior.
- Per-restoration validation, diagnostics, warnings, review confirmation, and approval.
- Per-restoration antagonist-region definition using automatic detection or manual picking.
- Antagonist-region review, persistence, ownership, invalidation, visibility, and cleanup.
- Aggregate Step 3 completion only when every configured restoration is approved.
- Safe migration from v0.0.3 and earlier in-branch v0.0.4 state.
- Safe invalidation when upstream scans, transforms, margins, or antagonist regions materially change.

## Project Status

Version `v0.0.4` is implemented and locally verified on branch:

`feat/v0.0.4-restoration-setup-manual-margin-definition`

The extension manifest is versioned as `0.0.4`. Package validation, ZIP build and inspection, installation, lifecycle checks, migration checks, Step 1 and Step 2 regressions, and the Step 3 scenario matrix were completed before preparing the release pull request.

See:

- [`docs/v0.0.4/PRD.md`](docs/v0.0.4/PRD.md)
- [`docs/v0.0.4/plans/0001-restoration-setup-manual-margin-definition.md`](docs/v0.0.4/plans/0001-restoration-setup-manual-margin-definition.md)
- [`docs/v0.0.4/TASKS.md`](docs/v0.0.4/TASKS.md)
- [`docs/v0.0.4/VERIFICATION.md`](docs/v0.0.4/VERIFICATION.md)
- [`docs/v0.0.4/decisions/`](docs/v0.0.4/decisions/)

## Previous Versions

- `v0.0.3` — Step 2: Occlusion Registration & Verification.
- `v0.0.2` — Step 1: Import Intra-Oral Scans.
- `v0.0.1` — Blender Extension foundation.

## Planned Next Workflow Stage

The next release is planned as `v0.0.5` and will define **Step 4**. Its exact production scope must be approved in a new PRD, decisions, plan, tasks, and verification matrix before implementation begins.

## Repository Structure

```text
b-dental/
├── docs/
│   ├── v0.0.1/
│   ├── v0.0.2/
│   ├── v0.0.3/
│   └── v0.0.4/
│       ├── decisions/
│       ├── plans/
│       ├── PRD.md
│       ├── TASKS.md
│       └── VERIFICATION.md
└── extension/
    ├── __init__.py
    ├── alignment.py
    ├── antagonist_region.py
    ├── blender_manifest.toml
    ├── margin_geometry.py
    ├── margin_overlay.py
    ├── margin_validation.py
    ├── occlusion_validation.py
    ├── operators.py
    ├── properties.py
    ├── restoration_utils.py
    ├── scene_utils.py
    ├── step_three_operators.py
    ├── step_three_session.py
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
- Imported occlusion remains a candidate until explicitly approved.
- Engineering metrics and validation do not certify clinical correctness.
- Implemented behavior must be locally verified before acceptance.
- Each version must leave the repository reviewable and reproducible.
- Completed release branches are merged using **Squash and merge**.
