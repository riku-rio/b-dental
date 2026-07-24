# Plan 0001: Preparation Analysis & Insertion Axis

## Metadata

- **Version:** v0.0.5
- **Status:** Approved for Implementation
- **Target branch:** `feat/v0.0.5-preparation-analysis-insertion-axis`
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

Implement Step 4 as an independent per-restoration workflow for insertion-axis definition and non-destructive preparation undercut analysis.

The implementation must consume approved Step 3 restorations without altering scans, margins, antagonist regions, or unrelated scene content. Every restoration receives an independently editable and approvable axis and analysis result.

## Delivery Principles

- One active restoration at a time.
- One authoritative normalized target-local axis per restoration.
- Current View is the primary MVP axis-input method.
- Margin-normal calculation is only a suggestion.
- Manual editing is reversible and snapshot-based.
- Analysis is margin-derived, deterministic, bounded, and non-destructive.
- The imported preparation mesh remains authoritative and unchanged.
- Analysis results are engineering aids, not clinical certification.
- Step 4 approval is independent per restoration.
- Aggregate Step 4 completion requires every restoration to be approved.
- Blender and the Python standard library only.

## Planned Source Structure

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

Names may change during implementation only when the resulting separation of responsibilities remains clear and the documentation is updated before acceptance.

## Architecture

### Persistent State

`properties.py` will extend each restoration with:

- Step 4 status and validity.
- Stored insertion-axis vector.
- Axis source.
- Managed-axis pointer.
- Reversible session snapshots.
- Analysis radius.
- Analysis metrics and result state.
- Errors, warnings, review, and acknowledgment.
- Approval and dependency signatures.

Workflow state will gain aggregate Step 4 status and validity while preserving the Step 1–3 contract.

### Axis Geometry

`axis_geometry.py` will provide:

- Vector serialization and deserialization.
- Finiteness and normalization helpers.
- Target-local/world-space conversion.
- Current-view axis capture.
- Margin center and margin-normal suggestion.
- Axis-object orientation conversion.
- Managed-axis creation, ownership, recovery, and cleanup.

The authoritative value is the stored target-local unit vector. The managed object is an interaction and display artifact.

### Axis Overlay

`axis_overlay.py` will provide lifecycle-safe viewport drawing for:

- The active restoration's axis.
- Direction convention labels or arrow cues when practical.
- Clear visual distinction between candidate and approved axis state.

The overlay must not modify target meshes or create renderable clinical output.

### Preparation Analysis

`preparation_analysis.py` will provide:

- Margin-derived center and default radius.
- Deterministic local surface sampling.
- Bounded evaluated-mesh acceleration data.
- Removal-direction obstruction testing.
- Blocking-depth measurement.
- Analysis metrics and result serialization.
- Overlay sample preparation.

The first implementation will analyze a neighborhood rather than segmenting the tooth.

### Validation

`step_four_validation.py` will validate:

- Upstream Step 3 state.
- Restoration and target ownership.
- Approved margin dependencies.
- Axis vector and managed-axis structure.
- Session state.
- Analysis settings, samples, metrics, and signatures.
- Warning thresholds.

Validation returns structured status, summary, errors, warnings, and metrics. It does not mutate approval state directly.

### Sessions

`step_four_session.py` will snapshot and restore only the active restoration.

It will support:

- Start.
- Reset.
- Cancel.
- Capture.
- Apply.
- Approval snapshots.
- Dependency monitoring.

Applying an axis candidate clears stale analysis and approval but does not approve Step 4.

### Operators

`step_four_operators.py` will provide:

- Step 4 entry and safe return.
- Restoration selection with session gating.
- Set From Current View.
- Suggest From Margin.
- Start, Reset, Cancel, Capture, and Apply axis actions.
- Axis focus, visibility, and clear actions.
- Analysis-radius updates.
- Run Undercut Analysis.
- Analysis overlay controls.
- Validate and Approve Step 4.

### UI

`ui.py` will gain a Step 4 panel state containing:

- Aggregate progress.
- Restoration list.
- Active restoration identity.
- Axis candidate and session controls.
- Analysis settings and actions.
- Metrics and overlay controls.
- Diagnostics and disclaimer.
- Explicit approval.

## Implementation Phases

### Phase 1 — State and Workflow Contract

1. Add Step 4 workflow and restoration properties.
2. Add statuses and aggregate synchronization.
3. Add safe v0.0.4 defaults.
4. Add Step 4 entry and return gating.

### Phase 2 — Axis Geometry and Managed Artifact

1. Implement vector helpers.
2. Implement margin center and normal suggestion.
3. Implement current-view capture.
4. Implement managed-axis ownership and orientation.
5. Implement focus and visibility.

### Phase 3 — Reversible Axis Sessions

1. Add snapshot model.
2. Add start and manual edit path.
3. Add Reset and Cancel.
4. Add Capture and Apply.
5. Add restoration-switch and navigation gating.

### Phase 4 — Preparation Neighborhood

1. Calculate margin-derived center.
2. Calculate and clamp default radius.
3. Add deterministic sample selection.
4. Bound sample count and runtime.
5. Add empty-neighborhood handling.

### Phase 5 — Undercut Analysis

1. Resolve evaluated target geometry.
2. Implement removal-direction obstruction testing.
3. Add scale-aware epsilon handling.
4. Calculate undercut metrics.
5. Store current dependency signatures.
6. Clear stale results after changes.

### Phase 6 — Overlay, Validation, and Approval

1. Add clear/undercut visualization.
2. Add structured validation.
3. Add warnings and disclaimers.
4. Add explicit review and acknowledgment.
5. Add approval snapshots.
6. Add aggregate completion.

### Phase 7 — Invalidation and Cleanup

1. Monitor target, margin, axis, settings, and upstream changes.
2. Invalidate only the owning restoration when possible.
3. Remove managed Step 4 artifacts during restoration removal and case reset.
4. Preserve safe candidates during temporary upstream invalidation.

### Phase 8 — Packaging and Verification

1. Update manifest version and module paths.
2. Validate and build the package.
3. Verify v0.0.4 migration.
4. Re-run Step 1–3 regression matrices.
5. Execute the complete Step 4 matrix.
6. Record actual thresholds, performance, results, and deviations.
7. Update README and acceptance documents.

## Safety Requirements

- Entering Step 4 never changes imported geometry.
- Setting an axis never transforms a scan or margin.
- Analysis never writes mesh attributes, vertex colors, materials, coordinates, or topology.
- Managed artifacts carry explicit ownership metadata.
- Reset and Cancel restore exact session-start state.
- Removing one restoration preserves every other restoration.
- Failed operators leave no false validity or approval.
- Aggregate approval is never inferred from only the active restoration.
- Any performance shortcut must remain deterministic and documented.

## Performance Strategy

The implementation must remain usable on intra-oral scan meshes without freezing the UI for unbounded periods.

Planned controls:

- Analyze only the margin-derived neighborhood.
- Use deterministic bounded sampling.
- Build acceleration structures only for evaluated target geometry.
- Cache only while dependency signatures remain current.
- Record analysis duration when practical.
- Treat excessive runtime or missing usable samples as implementation defects, not reasons to silently approve.

## Completion Definition

This plan is complete only when:

- Step 4 state persists safely.
- Every restoration can define, edit, analyze, validate, and approve its own insertion axis.
- Current-view capture and margin suggestion behave deterministically.
- Sessions are independently reversible.
- Undercut analysis is non-destructive and bounded.
- Metrics and overlay correspond to the current axis and dependencies.
- Aggregate Step 4 validity requires all restorations.
- v0.0.4 migration is safe.
- Step 1–3 remain regression-free.
- Package and lifecycle verification pass.
- Actual implementation results and deviations are documented.

## Current Implementation Status

The plan is approved for implementation. No production Step 4 modules or workflow behavior have been added yet.