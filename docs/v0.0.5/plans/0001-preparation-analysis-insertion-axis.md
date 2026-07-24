# Plan 0001: Preparation Analysis & Insertion Axis

## Metadata

- **Version:** v0.0.5
- **Status:** Complete
- **Target branch:** `feat/v0.0.5-preparation-analysis-insertion-axis`
- **Target merge branch:** `main`
- **Merge strategy:** Squash and merge
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related tasks:** [`../TASKS.md`](../TASKS.md)
- **Related verification:** [`../VERIFICATION.md`](../VERIFICATION.md)
- **Related decisions:**
  - [`../decisions/0001-store-insertion-axis-as-target-local-unit-vector.md`](../decisions/0001-store-insertion-axis-as-target-local-unit-vector.md)
  - [`../decisions/0002-use-current-view-as-primary-axis-input.md`](../decisions/0002-use-current-view-as-primary-axis-input.md)
  - [`../decisions/0003-use-reversible-managed-axis-sessions.md`](../decisions/0003-use-reversible-managed-axis-sessions.md)
  - [`../decisions/0004-use-margin-derived-sample-based-undercut-analysis.md`](../decisions/0004-use-margin-derived-sample-based-undercut-analysis.md)
  - [`../decisions/0005-require-explicit-step-four-validation-and-approval.md`](../decisions/0005-require-explicit-step-four-validation-and-approval.md)

## Objective

Implement Step 4 as an independent per-restoration workflow for insertion-axis definition and non-destructive preparation undercut analysis while preserving all approved Step 1–3 data and unrelated scene content.

## Delivered Source Structure

```text
extension/
├── __init__.py
├── axis_geometry.py
├── axis_overlay.py
├── preparation_analysis.py
├── step_four_operators.py
├── step_four_session.py
├── step_four_validation.py
├── antagonist_region.py
├── blender_manifest.toml
├── margin_geometry.py
├── properties.py
├── restoration_utils.py
├── scene_utils.py
└── ui.py
```

## Delivered Architecture

### Persistent State

The restoration state now includes Step 4 status and validity, target-local axis vector, source, managed-axis pointer, reversible session snapshots, analysis radius, samples, metrics, diagnostics, review state, warning acknowledgment, and approval signatures.

Workflow state includes aggregate Step 4 status and validity while preserving all earlier workflow contracts.

### Axis Geometry

`axis_geometry.py` provides:

- Vector finiteness, normalization, serialization, and deserialization.
- Target-local/world-space direction conversion.
- Current-view forward capture.
- Margin-derived center and normal suggestion.
- Axis-object orientation conversion.
- Managed-axis creation, ownership metadata, pointer recovery, and cleanup.

The stored target-local unit vector is authoritative. The managed object remains an interaction and display artifact.

### Axis and Analysis Overlay

`axis_overlay.py` provides lifecycle-safe viewport drawing for the active restoration's axis and analysis samples. Candidate and approved axis states are visually distinct. Clear and undercut samples are drawn without modifying target mesh data.

### Preparation Analysis

`preparation_analysis.py` provides:

- Margin-derived center and default radius.
- Radius clamping to the supported engineering range.
- Evaluated triangulated target geometry.
- Deterministic bounded world-space sample selection.
- World-space BVH obstruction testing.
- Scale-aware self-hit offset.
- Blocking-depth measurement.
- Analysis metrics and target-local overlay sample serialization.

The analysis operates on a neighborhood rather than segmented tooth anatomy.

### Validation

`step_four_validation.py` validates upstream state, target and margin dependencies, axis ownership and vector state, session state, radius, samples, metrics, and signatures. It reports blocking errors separately from engineering warnings and does not approve automatically.

### Sessions

`step_four_session.py` snapshots and restores only the active restoration. It supports Start, Reset, Cancel, Capture, Apply, approval snapshots, aggregate synchronization, dependency monitoring, invalidation, and safe cleanup.

### Operators and UI

`step_four_operators.py` and the patched workflow panel provide:

- Gated Step 4 entry and safe return.
- Restoration selection with session gating.
- Set From Current View and Suggest From Margin.
- Axis editing, capture, apply, reset, cancel, focus, visibility, and clearing.
- Radius adjustment and undercut analysis.
- Overlay Show, Hide, and Clear.
- Validation and explicit approval.
- Aggregate progress, identity, metrics, diagnostics, warnings, disclaimers, review, and acknowledgment controls.

## Completed Implementation Phases

### Phase 1 — State and Workflow Contract

- [x] Added Step 4 workflow and restoration properties.
- [x] Added aggregate synchronization.
- [x] Added safe v0.0.4 defaults.
- [x] Added entry and return gating.

### Phase 2 — Axis Geometry and Managed Artifact

- [x] Implemented vector helpers and conversions.
- [x] Implemented margin center and normal suggestion.
- [x] Implemented current-view capture.
- [x] Implemented managed-axis ownership, orientation, focus, visibility, recovery, and cleanup.

### Phase 3 — Reversible Axis Sessions

- [x] Added exact snapshot, Start, Reset, Cancel, Capture, and Apply behavior.
- [x] Added restoration-switch and navigation gating.
- [x] Preserved inactive restoration state.

### Phase 4 — Preparation Neighborhood

- [x] Added margin-derived center and radius.
- [x] Added deterministic bounded sample selection.
- [x] Added empty-neighborhood handling.

### Phase 5 — Undercut Analysis

- [x] Added evaluated target geometry and world-space BVH analysis.
- [x] Added removal-direction obstruction testing and self-hit handling.
- [x] Added metrics, signatures, duration, and stale-result clearing.

### Phase 6 — Overlay, Validation, and Approval

- [x] Added clear/undercut visualization.
- [x] Added structured validation and warnings.
- [x] Added explicit review, acknowledgment, approval snapshots, and aggregate completion.

### Phase 7 — Invalidation and Cleanup

- [x] Added target, margin, antagonist, axis, settings, artifact, analysis, and upstream monitoring.
- [x] Added scoped invalidation and artifact cleanup.
- [x] Preserved safe candidates and unrelated content.

### Phase 8 — Packaging and Verification

- [x] Updated manifest version and build paths.
- [x] Validated and built `b_dental-0.0.5.zip`.
- [x] Verified install, lifecycle, migration, regressions, Step 4 matrix, persistence, cleanup, UI, and safety.
- [x] Updated README, PRD, tasks, decisions, plan, and verification record.

## Implementation Corrections and Deviations

### Manifest Tagline

Blender rejected the initial 70-character tagline because extension taglines are limited to 64 characters. The tagline was shortened before the accepted build.

### World-Space Analysis

The initial implementation selected local polygon centers using a radius expressed in Blender world units. Imported scans with non-identity scale could therefore produce an empty or incorrectly sized neighborhood.

The accepted implementation:

- Triangulates evaluated mesh geometry.
- Converts evaluated vertices and triangle centers to world space.
- Converts the stored target-local axis to world space.
- Performs radius selection and BVH ray casting in world space.
- Converts sample points back to target-local coordinates for persistent overlay data.
- Advances the sampling policy version so earlier development results are stale.

This correction preserves the target-local authoritative axis contract while making physical radius and depth measurements scale-correct.

## Safety Result

- Entering Step 4 does not change imported geometry.
- Setting or editing an axis does not transform scans or margins.
- Analysis does not write mesh attributes, colors, materials, coordinates, or topology.
- Managed artifacts carry explicit ownership metadata.
- Reset and Cancel restore session-start state.
- Removing one restoration preserves all others.
- Failed operations do not create false approval.
- Aggregate approval is never inferred from only the active restoration.

## Performance Result

Analysis is bounded to the margin-derived neighborhood and a maximum deterministic sample count. Representative local verification processed 2,000 samples in approximately 0.354 seconds; actual duration depends on fixture geometry and hardware.

## Completion Definition

The plan is complete because:

- Step 4 state persists safely.
- Every restoration can independently define, edit, analyze, validate, and approve an axis.
- Candidate methods and reversible sessions behave as specified.
- Analysis is deterministic, bounded, scale-correct, and non-destructive.
- Metrics and overlay match current dependencies.
- Aggregate validity requires all restorations.
- v0.0.4 migration and Step 1–3 regressions passed.
- Package and lifecycle verification passed.
- Results, corrections, limits, and deviations are documented.

## Completion Record

The implementation plan has been delivered and locally verified. Version v0.0.5 is ready for a non-draft pull request and **Squash and merge** into `main`.
