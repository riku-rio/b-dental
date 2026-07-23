# Plan 0001: Multiple Restoration Setup & Manual Margin Definition

## Metadata

- **Version:** v0.0.4
- **Status:** In Progress
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related tasks:** [`../TASKS.md`](../TASKS.md)
- **Related decisions:**
  - [`../decisions/0001-limit-v0.0.4-to-one-anatomical-crown.md`](../decisions/0001-limit-v0.0.4-to-one-anatomical-crown.md) — superseded
  - [`../decisions/0002-use-permanent-fdi-tooth-identifiers.md`](../decisions/0002-use-permanent-fdi-tooth-identifiers.md)
  - [`../decisions/0003-represent-margin-as-managed-target-local-curve.md`](../decisions/0003-represent-margin-as-managed-target-local-curve.md)
  - [`../decisions/0004-use-reversible-manual-margin-sessions.md`](../decisions/0004-use-reversible-manual-margin-sessions.md)
  - [`../decisions/0005-require-explicit-margin-validation-and-approval.md`](../decisions/0005-require-explicit-margin-validation-and-approval.md)
  - [`../decisions/0006-support-multiple-independent-restorations.md`](../decisions/0006-support-multiple-independent-restorations.md)

## Objective

Implement Step 3 as a collection-based workflow supporting multiple independent anatomical crown restorations and manual margins in one B-Dental case.

The workflow must preserve upper and lower restorations simultaneously, isolate every margin operation to the active restoration, and derive aggregate Step 3 completion only when every configured restoration is approved.

## Delivery Principles

- Multiple restorations, but one active editing target at a time.
- One unique restoration per arch and FDI tooth.
- One managed margin object per restoration.
- Independent session, diagnostics, validation, and approval state.
- Switching blocked during active sessions.
- No imported scan mesh edits.
- No automatic margin detection, insertion axis, or crown generation.
- Preserve safe geometry during upstream invalidation.
- Use Blender and the Python standard library only.

## Source Structure

```text
extension/
├── __init__.py
├── alignment.py
├── blender_manifest.toml
├── margin_geometry.py
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

## Architecture

### Collection State

`properties.py` provides:

- `BDENTAL_PG_RestorationState` for one restoration.
- `CollectionProperty` named `restorations`.
- Persistent `active_restoration_index`.
- New-restoration arch and FDI controls.
- Per-restoration status, validity, margin pointer, sessions, diagnostics, and approval snapshots.
- Aggregate `step_3_status` and `step_3_valid` synchronization.
- Legacy single-restoration properties retained only for one-time migration.

### Restoration Ownership

`restoration_utils.py` provides:

- Stable IDs.
- Permanent FDI constraints.
- Duplicate-tooth detection.
- Active-restoration resolution.
- Per-restoration target-scan resolution.
- Managed margin metadata and recovery.
- Safe per-restoration and whole-case cleanup.
- Legacy single-restoration migration.

### Margin Geometry

`margin_geometry.py` provides:

- One target-local 3D `POLY` Curve per restoration.
- Target-only viewport ray casting.
- Ordered point replacement and serialization.
- Reprojection and diagnostics.

### Validation

`margin_validation.py` accepts both workflow state and a restoration item. It validates:

- Upstream state.
- Unique restoration target.
- Target scan and signature.
- Margin ownership metadata.
- Curve structure, closure, and points.
- Surface distance and path diagnostics.

### Sessions and Monitoring

`step_three_session.py` snapshots and restores only the active restoration. Dependency monitoring iterates all restorations and invalidates each independently.

### Operators

`step_three_operators.py` provides:

- Step 3 entry.
- Add, select, and remove restoration.
- Active restoration drawing and editing.
- Reset, cancel, apply, validate, and approve.
- Focus and visibility actions.
- Safe return to Step 2.

### UI

`ui.py` displays:

- Restoration count and aggregate approval count.
- Selectable restoration rows.
- Add-restoration controls.
- Active restoration details and actions.
- Per-restoration messages and diagnostics.
- Aggregate Step 3 completion.

## Implementation Phases

### Phase 1 — Documentation Revision

1. Supersede the single-restoration decision.
2. Accept the multiple-restoration decision.
3. Revise PRD, plan, tasks, and verification.

### Phase 2 — Collection State

1. Add restoration PropertyGroup.
2. Add collection and active index.
3. Add aggregate synchronization.
4. Retain legacy fields for migration.

### Phase 3 — Ownership and Migration

1. Scope metadata to restoration items.
2. Recover margins by restoration ID.
3. Add duplicate target rejection.
4. Migrate earlier single-restoration branch state.

### Phase 4 — Geometry, Validation, and Sessions

1. Pass restoration explicitly to geometry helpers.
2. Validate each restoration independently.
3. Snapshot and restore independent sessions.
4. Monitor every restoration dependency.

### Phase 5 — Operators and UI

1. Add restoration creation.
2. Add selection with session gating.
3. Add confirmed removal.
4. Scope all margin operators to active restoration.
5. Add list and aggregate status UI.

### Phase 6 — Verification

1. Validate and build package.
2. Verify v0.0.3 and single-restoration branch migration.
3. Re-run Step 1 and Step 2 regressions.
4. Verify multiple upper restorations.
5. Verify mixed upper and lower restorations.
6. Verify duplicate rejection.
7. Verify independent drawing, edit, validation, approval, removal, persistence, and invalidation.
8. Record actual results.

## Safety Requirements

- Adding or switching restorations never changes scans.
- Margin operations affect only the active restoration.
- Removing one restoration preserves all others.
- Case reset removes only B-Dental-managed content.
- Imported topology and coordinates remain unchanged.
- Failed operators leave no false approval.
- Aggregate completion is never inferred from only the active restoration.

## Completion Definition

This plan is complete only when:

- Multiple restorations coexist and persist.
- Upper and lower restorations coexist in one case.
- Every margin workflow is independently reversible.
- Duplicate target teeth are rejected.
- Aggregate Step 3 validity requires all restorations to be approved.
- Step 1 and Step 2 remain regression-free.
- The revised verification matrix passes locally.
- Actual implementation results and deviations are documented.

## Current Implementation Status

The collection state, ownership, migration, geometry, validation, session, operator, and UI changes have been implemented on the target branch. Blender package validation and the complete manual verification matrix remain pending.
