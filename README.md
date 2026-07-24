# B-Dental

B-Dental is a custom Blender Extension for building a structured digital dental workflow inside Blender.

The project is developed through small, verifiable releases. Each release defines requirements, architectural decisions, an implementation plan, a task checklist, and a local verification record before the next workflow stage begins.

## Current Version: v0.0.5

Version `v0.0.5` implements and verifies:

**Step 4 — Preparation Analysis & Insertion Axis**

The extension now supports:

- Independent Step 4 state and approval for every restoration created in Step 3.
- One authoritative finite normalized insertion axis stored in preparation-scan local coordinates.
- Axis candidates captured from the current 3D View.
- A non-authoritative margin-normal axis suggestion.
- One managed, target-parented axis object per restoration for interaction and display.
- Reversible axis-edit sessions with Start, Reset, Cancel, Capture, and Apply behavior.
- A margin-derived preparation-analysis neighborhood with an adjustable `2 mm` to `15 mm` radius.
- Deterministic, bounded, non-destructive evaluated-mesh sampling.
- World-space undercut ray analysis using the removal direction opposite the stored seating axis.
- Per-restoration sample count, undercut count, ratio, mean depth, maximum depth, and runtime metrics.
- A viewport overlay that distinguishes clear and undercut samples without modifying imported mesh data.
- Independent validation, engineering warnings, visual review, warning acknowledgment, and explicit approval.
- Aggregate Step 4 completion only when every restoration is independently approved.
- Safe invalidation after target, margin, antagonist, axis, radius, analysis, or upstream changes.
- Safe migration from v0.0.4 with empty Step 4 defaults and no automatically created Step 4 artifacts.

## Project Status

Version `v0.0.5` is implemented and locally verified on branch:

`feat/v0.0.5-preparation-analysis-insertion-axis`

The extension manifest is versioned as `0.0.5`. Manifest validation, ZIP build and inspection, install-from-disk, enablement, lifecycle checks, v0.0.4 migration, Step 1–3 regressions, the complete Step 4 scenario matrix, persistence, invalidation, cleanup, UI, performance, and scan-safety checks were completed before preparing the release pull request.

Two defects found during local verification were corrected before acceptance:

- The extension tagline exceeded Blender's 64-character manifest limit.
- Preparation samples were initially compared in target-local coordinates against a world-unit radius; sampling and BVH analysis now run in world space and stored overlay samples remain target-local.

See:

- [`docs/v0.0.5/PRD.md`](docs/v0.0.5/PRD.md)
- [`docs/v0.0.5/plans/0001-preparation-analysis-insertion-axis.md`](docs/v0.0.5/plans/0001-preparation-analysis-insertion-axis.md)
- [`docs/v0.0.5/TASKS.md`](docs/v0.0.5/TASKS.md)
- [`docs/v0.0.5/VERIFICATION.md`](docs/v0.0.5/VERIFICATION.md)
- [`docs/v0.0.5/decisions/`](docs/v0.0.5/decisions/)

## Previous Versions

- `v0.0.4` — Step 3: Multiple Restorations, Manual Margins & Antagonist Regions.
- `v0.0.3` — Step 2: Occlusion Registration & Verification.
- `v0.0.2` — Step 1: Import Intra-Oral Scans.
- `v0.0.1` — Blender Extension foundation.

## Planned Next Workflow Stage

The next production stage has not been accepted yet. Crown-bottom, cement-gap, anatomy, contact-adjustment, and export behavior remain outside v0.0.5 and require a separately approved PRD, decisions, plan, tasks, and verification matrix before implementation.

## Repository Structure

```text
b-dental/
├── docs/
│   ├── v0.0.1/
│   ├── v0.0.2/
│   ├── v0.0.3/
│   ├── v0.0.4/
│   └── v0.0.5/
│       ├── decisions/
│       ├── plans/
│       ├── PRD.md
│       ├── TASKS.md
│       └── VERIFICATION.md
└── extension/
    ├── __init__.py
    ├── alignment.py
    ├── antagonist_region.py
    ├── axis_geometry.py
    ├── axis_overlay.py
    ├── blender_manifest.toml
    ├── margin_geometry.py
    ├── margin_overlay.py
    ├── margin_validation.py
    ├── occlusion_validation.py
    ├── operators.py
    ├── preparation_analysis.py
    ├── properties.py
    ├── restoration_utils.py
    ├── scene_utils.py
    ├── step_four_operators.py
    ├── step_four_session.py
    ├── step_four_validation.py
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
