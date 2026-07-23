# Plan 0001: Restoration Setup & Manual Margin Definition

## Metadata

- **Version:** v0.0.4
- **Status:** Proposed
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related tasks:** [`../TASKS.md`](../TASKS.md)
- **Related decisions:**
  - [`../decisions/0001-limit-v0.0.4-to-one-anatomical-crown.md`](../decisions/0001-limit-v0.0.4-to-one-anatomical-crown.md)
  - [`../decisions/0002-use-permanent-fdi-tooth-identifiers.md`](../decisions/0002-use-permanent-fdi-tooth-identifiers.md)
  - [`../decisions/0003-represent-margin-as-managed-target-local-curve.md`](../decisions/0003-represent-margin-as-managed-target-local-curve.md)
  - [`../decisions/0004-use-reversible-manual-margin-sessions.md`](../decisions/0004-use-reversible-manual-margin-sessions.md)
  - [`../decisions/0005-require-explicit-margin-validation-and-approval.md`](../decisions/0005-require-explicit-margin-validation-and-approval.md)

## Objective

Replace the post-Step-2 endpoint with a safe, persistent, and verifiable Step 3 workflow that defines one anatomical-crown restoration and one manually drawn margin on its preparation scan.

The completed workflow must establish a stable restoration identity, constrain target selection, preserve imported scan geometry, provide reversible margin drawing and editing, report engineering diagnostics, and require explicit approval before Step 3 is complete.

## Delivery Principles

- Keep v0.0.4 limited to one active single-unit anatomical crown.
- Do not implement automatic margin detection.
- Do not implement insertion axis or crown generation.
- Keep imported scans read-only at the mesh-data level.
- Make all destructive cleanup explicit and narrowly scoped.
- Store margin points in the preparation scan's local coordinate system.
- Separate operator success, candidate state, validation, and approval.
- Preserve applied geometry when upstream state becomes temporarily invalid whenever safe.
- Use only Blender and Python standard-library capabilities.

## Expected Source Structure

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

The implementation may refine the structure, but Step 3 responsibilities must remain separated from Step 1 and Step 2 code.

## Architecture Plan

### State Layer

Extend `properties.py` with:

- `STEP_3` workflow navigation.
- Step 3 status and validity.
- Stable restoration identity.
- Fixed anatomical-crown restoration type.
- Target arch and permanent FDI tooth.
- Margin object pointer.
- Active-session and candidate state.
- Review confirmation and warning acknowledgment.
- Diagnostics and summaries.
- Session and approved point snapshots.
- Target-scan and upstream approval signatures.
- Step 1-to-Step 3 and Step 2-to-Step 3 invalidation behavior.

Add explicit helpers:

- `clear_step_three_state()`
- `invalidate_step_three()`
- dependency-aware reset behavior

Case reset must also clear Step 2 state completely before Step 3 is added.

### Restoration Layer

Create `restoration_utils.py` for:

- Restoration ID generation.
- Supported restoration constants.
- Permanent FDI tooth sets.
- Arch-to-tooth constraints.
- Target scan resolution.
- Managed restoration collection creation.
- Margin ownership metadata.
- Safe managed-artifact lookup and cleanup.
- Target-scan signatures.

### Margin Geometry Layer

Create `margin_geometry.py` for:

- Evaluated target-only ray casting.
- World-to-target-local coordinate conversion.
- Target-local-to-world display conversion.
- Curve and spline creation.
- Ordered point replacement.
- Point serialization and deserialization.
- Path-length calculation.
- Point-to-surface distance calculation.
- Edited-point reprojection.
- Approximate spacing and non-adjacent proximity diagnostics.

### Validation Layer

Create `margin_validation.py` for:

- Step 3 precondition checks.
- Restoration setup checks.
- Managed margin metadata checks.
- Curve structure checks.
- Point-count and finite-coordinate checks.
- Cyclic-closure checks.
- Surface-distance checks.
- Path diagnostics.
- Approval-readiness results.
- Separate blocking errors and warnings.

### Session Layer

Create `step_three_session.py` for:

- Exact ordered point snapshots.
- Existing-margin and no-margin session starts.
- Draft-object cleanup.
- Reset behavior.
- Cancel behavior.
- Candidate application.
- Failure rollback.
- Prior status and approval restoration.

### Operator Layer

Create `step_three_operators.py` for:

- Enter Step 3.
- Create or reset restoration setup.
- Confirm target-arch changes.
- Confirm target-tooth changes.
- Start margin session.
- Modal target-only margin drawing.
- Remove last point.
- Finish and close candidate.
- Reset session.
- Cancel session.
- Apply candidate.
- Prepare margin for editing.
- Reproject edited points.
- Recapture edited candidate.
- Validate margin.
- Approve margin.
- Focus and visibility actions.
- Safe return to Step 2.

### UI Layer

Update `ui.py` to:

- Display three workflow steps.
- Replace `Step 1 of 2` and `Step 2 of 2` with three-step progress text.
- Add an explicit Step 2-to-Step 3 transition after Step 2 completion.
- Display restoration setup before drawing controls.
- Display target scan and tooth selection.
- Display context-sensitive session controls.
- Display modal drawing instructions.
- Display editing and reprojection actions.
- Display validation errors, warnings, and diagnostics.
- Display review confirmation and approval controls.
- Prevent silent navigation during an active session.

## Implementation Phases

### Phase 1 — Documentation Approval

1. Review and approve the PRD.
2. Review and approve all decision records.
3. Review and approve this plan.
4. Review and approve the task checklist.
5. Review and approve the verification procedure.

No production Step 3 implementation begins before the documentation set is accepted.

### Phase 2 — Existing Lifecycle Correction

1. Ensure a case reset explicitly clears all Step 2 state.
2. Add dependency-aware clearing for future Step 3 state.
3. Verify reset removes only confirmed B-Dental-managed content.
4. Re-run current Step 1 and Step 2 lifecycle scenarios.

### Phase 3 — Step 3 State and Migration

1. Add Step 3 navigation and status values.
2. Add restoration properties.
3. Add target arch and FDI tooth properties.
4. Add margin pointer, session, candidate, review, and diagnostic properties.
5. Add serialized session and approved point snapshots.
6. Add safe defaults for v0.0.3 scenes.
7. Add clear and invalidation helpers.

### Phase 4 — Restoration Identity and Managed Artifacts

1. Implement permanent FDI arch constraints.
2. Implement stable restoration identity.
3. Implement `B-Dental Restorations` collection management.
4. Implement managed margin metadata.
5. Implement safe margin lookup and removal.
6. Implement target-scan signatures.
7. Verify unrelated objects remain untouched.

### Phase 5 — Restoration Setup Workflow

1. Implement Step 3 preconditions.
2. Implement Single Arch automatic target selection.
3. Implement Dual Arch and Full Scan Set target selection.
4. Implement target-tooth filtering.
5. Implement explicit restoration creation.
6. Implement confirmed setup changes when a margin exists.
7. Implement setup persistence.

### Phase 6 — Margin Curve Core

1. Implement managed 3D `POLY` curve creation.
2. Implement target-local point storage.
3. Implement ordered spline updates.
4. Implement cyclic closure.
5. Implement visible bevel settings.
6. Implement point serialization.
7. Verify scan mesh data remains unchanged.

### Phase 7 — Modal Manual Drawing

1. Implement a Viewport modal operator.
2. Implement target-only ray casting.
3. Implement accepted-hit conversion to target-local points.
4. Implement live open-path display.
5. Implement remove-last-point behavior.
6. Implement explicit finish and cancel behavior.
7. Enforce minimum point requirements.
8. Handle missing viewport, stale target, and operator exceptions safely.

### Phase 8 — Reversible Session Safety

1. Snapshot existing margin and state.
2. Implement new-draft and existing-margin session paths.
3. Implement exact reset.
4. Implement exact cancel.
5. Implement candidate application.
6. Ensure candidate application does not approve Step 3.
7. Add failure rollback.
8. Prevent silent navigation during an active session.

### Phase 9 — Editing and Reprojection

1. Provide a supported edit path for the managed margin.
2. Validate that the active artifact remains the expected curve.
3. Reproject edited points to the target preparation surface.
4. Reject unsupported additional splines or changed spline types.
5. Recapture edited points as a candidate.
6. Invalidate previous approval after material edits.

### Phase 10 — Validation and Diagnostics

1. Define structured validation results.
2. Implement managed-object and metadata validation.
3. Implement curve-structure validation.
4. Implement unique-point and finite-coordinate validation.
5. Implement closure and path-length validation.
6. Implement target-surface distance diagnostics.
7. Implement spacing warnings.
8. Implement approximate self-proximity warnings.
9. Separate blocking errors and warnings.
10. Display point count, path length, and surface-distance metrics.

### Phase 11 — Explicit Approval

1. Add warning acknowledgment.
2. Add visual-review confirmation.
3. Implement explicit approval.
4. Store approved point and target signatures.
5. Store diagnostics and summary.
6. Set `step_3_valid = true` only after approval.
7. Preserve the approved margin visibly.

### Phase 12 — Invalidation and Monitoring

1. Invalidate Step 3 after Step 1 invalidation.
2. Invalidate Step 3 after Step 2 invalidation.
3. Remove a margin only when its target scan is removed or replaced.
4. Preserve usable geometry during temporary upstream invalidation.
5. Detect material approved-margin edits.
6. Detect target metadata mismatch.
7. Detect target-scan signature changes.
8. Verify persistence after save and reopen.

### Phase 13 — Packaging and UI Completion

1. Register new modules and classes deterministically.
2. Unregister in reverse order.
3. Update manifest version to `0.0.4`.
4. Add required modules to build paths.
5. Complete Step 3 sidebar UI.
6. Verify normal-width readability.
7. Verify repeated enable, disable, and reload behavior.

### Phase 14 — Verification and Completion

1. Validate the manifest.
2. Build and inspect the `0.0.4` package.
3. Install and enable from disk.
4. Verify v0.0.3 migration.
5. Re-run Step 1 and Step 2 regressions.
6. Execute every Step 3 scenario in `VERIFICATION.md`.
7. Record actual results and deviations.
8. Update PRD and plan status only after acceptance.
9. Mark tasks complete only after implementation or verification.
10. Update README and prepare a non-draft pull request for squash merge.

## Safety Requirements

- Registration and enablement must not modify the scene.
- Entering Step 3 must not modify scans.
- Imported mesh coordinates and topology remain unchanged.
- Surface picking must target only the selected preparation scan.
- Reset and cancel restore exact session-start margin points.
- Failed operators must not leave partial approved state.
- Changing restoration setup must not remove unrelated objects.
- Upstream invalidation must not silently claim Step 3 completion.
- Metrics and warnings must not be presented as clinical proof.
- Approval must remain explicit.

## Planned Deviations Process

If implementation reveals a necessary architectural deviation:

1. Stop expansion beyond the accepted behavior.
2. Update the relevant decision record.
3. Update the PRD when user-visible behavior changes.
4. Update this plan and task checklist.
5. Add or update verification scenarios.
6. Resume implementation only after the revised documentation is accepted.

## Completion Definition

This plan is complete only when:

- Every accepted requirement is implemented.
- Every required task is complete.
- All verification scenarios pass locally.
- Step 1 and Step 2 remain regression-free.
- The margin workflow is reversible and scan-safe.
- Approval is explicit and persistent.
- Actual implementation deviations are documented.
- The package is ready for a non-draft pull request and **Squash and merge**.
