# Local Verification: v0.0.6

## Document Status

- **Version:** v0.0.6
- **Status:** Planned
- **Target branch:** `feat/v0.0.6-automated-preparation-die-crown-bottom`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Blender:** 5.0.1 or current accepted project version
- **Minimum supported Blender:** 4.2
- **Result:** Not executed
- **Merge strategy:** Squash and merge

Only de-identified dental fixtures may be used.

## Package Verification

- [ ] Manifest version is `0.0.6`.
- [ ] Blender Python syntax validation passes.
- [ ] Extension manifest validation passes.
- [ ] `b_dental-0.0.6.zip` is created.
- [ ] Package contents contain every required Step 5 module.
- [ ] Installation from disk passes.
- [ ] Enablement and registration pass.
- [ ] Repeated enable, disable, restart, and reload pass.
- [ ] No duplicate handlers, timers, operators, or draw callbacks remain.

## Migration and Regression

- [ ] v0.0.5 scenes open with safe empty Step 5 defaults.
- [ ] Migration creates no die, blockout, or crown-bottom artifact.
- [ ] Step 1–4 state, approvals, transforms, and artifacts remain unchanged.
- [ ] Step 1 regression matrix passes.
- [ ] Step 2 regression matrix passes.
- [ ] Step 3 regression matrix passes.
- [ ] Step 4 regression matrix passes.

## Step 5 Entry and State

- [ ] Entry is blocked until aggregate Step 4 approval.
- [ ] Entry is blocked during active upstream edit sessions.
- [ ] Entry preserves every upstream artifact and transform.
- [ ] Entry creates no generated geometry automatically.
- [ ] Fresh per-restoration Step 5 state is unapproved.
- [ ] Safe return to Step 4 works.
- [ ] Multiple restorations retain independent settings and state.

## Preparation-Region Extraction

- [ ] Ordered approved margin is reconstructed reproducibly.
- [ ] Margin-to-surface anchors are deterministic.
- [ ] One bounded preparation patch is extracted for a clear fixture.
- [ ] Repeated extraction from unchanged inputs is identical.
- [ ] Extraction handles target objects with non-identity transforms and scale.
- [ ] Adjacent anatomy leakage is bounded and reported.
- [ ] Open, branching, ambiguous, or multiply bounded results fail safely.
- [ ] Low-resolution or damaged source geometry reports warnings or errors correctly.
- [ ] Target scan geometry and data remain unchanged.

## Preparation Die

- [ ] Extracted preparation surface is duplicated non-destructively.
- [ ] Margin boundary correspondence is preserved.
- [ ] Side walls follow the approved insertion axis.
- [ ] Base cap is deterministic and closed.
- [ ] Normals are consistent.
- [ ] Boundary-loop, manifold, degenerate-face, and ownership checks pass.
- [ ] Pointer recovery works after save and reopen.
- [ ] Removing one restoration removes only its die.

## Undercut Blockout

- [ ] Clear preparation produces no unnecessary blockout beyond tolerance.
- [ ] Known undercut fixture is blocked along the approved axis.
- [ ] Reversing or materially changing the axis changes the blockout result.
- [ ] Configured blockout clearance is achieved within tolerance.
- [ ] Margin and seal-band boundary remain protected.
- [ ] Residual path obstruction is detected and blocks approval.
- [ ] Folded, inverted, discontinuous, or failed reconstruction is rejected.
- [ ] Blockout metrics remain finite and reproducible.

## Relief Field

- [ ] Marginal-gap setting affects only the accepted marginal region.
- [ ] Spacer-start distance creates the intended no-spacer band.
- [ ] Cement gap is applied in the internal relieved region.
- [ ] Axial relief is applied to axial-classified surfaces.
- [ ] Occlusal relief is applied to occlusal-classified surfaces.
- [ ] Transition zones are continuous within tolerance.
- [ ] Settings at minimum and maximum accepted bounds behave safely.
- [ ] Invalid, non-finite, or contradictory settings are rejected.
- [ ] Offset inversion, folding, or local collapse is detected.
- [ ] Achieved regional gap metrics match generated geometry.

## Margin Seal Band

- [ ] One continuous band is generated around the complete margin.
- [ ] Ordered correspondence to the approved margin is preserved.
- [ ] Configured width is achieved within tolerance.
- [ ] Marginal gap is achieved within tolerance.
- [ ] Band joins continuously to the relieved internal surface.
- [ ] No missing segments, branches, duplicate segments, flipped faces, or self-intersections exist.
- [ ] Deliberately corrupted bands are rejected.
- [ ] Margin-deviation and band-width metrics remain reproducible.

## Candidate Generation

- [ ] Primary candidate generation succeeds for a supported fixture.
- [ ] Optional bounded variants are generated only under documented policy.
- [ ] Candidate count and iteration limits are enforced.
- [ ] Candidate identifiers and restoration ownership are stable.
- [ ] Previously approved geometry is preserved until replacement approval.
- [ ] Rejected-candidate diagnostics remain available.
- [ ] Temporary evaluated meshes and intermediate objects are removed after success.
- [ ] Temporary data are removed after failure or cancellation.
- [ ] Repeated unchanged generation produces identical geometry signatures and ranking.

## Candidate Validation and Ranking

- [ ] Margin fidelity objective matches measured geometry.
- [ ] Seal-band continuity is a blocking constraint.
- [ ] Insertion-path collision is a blocking constraint above tolerance.
- [ ] Regional gap error is measured and scored.
- [ ] Self-intersection is detected and blocks approval.
- [ ] Non-manifold, invalid-normal, degenerate, or unsupported feature-size cases are handled correctly.
- [ ] Rejected candidates never enter accepted ranking.
- [ ] Accepted candidates are ranked deterministically.
- [ ] Stable tie-breaking works.
- [ ] Ranking ambiguity warning appears for materially close scores.
- [ ] Every score component and rejection reason is visible and finite.

## Constrained Correction

- [ ] Start snapshots the selected candidate and state.
- [ ] Reset restores the exact session-start candidate and keeps the session active.
- [ ] Cancel restores the exact pre-session state and removes drafts.
- [ ] Local offset correction remains within configured bounds.
- [ ] Smoothing preserves the protected boundary and insertion-path constraints.
- [ ] Seal-band reprojection returns to the approved margin contract.
- [ ] Capture and Apply preserve only the managed candidate.
- [ ] Apply clears prior validation and approval.
- [ ] Full validation is required after Apply.
- [ ] Direct out-of-session edits invalidate safely.
- [ ] Expert override is explicit and recorded.
- [ ] Expert override cannot bypass structural blocking errors.

## Validation and Approval

- [ ] Missing target, margin, axis, analysis, settings, or artifacts block approval.
- [ ] Stale dependency or settings signatures block approval.
- [ ] Candidate belonging to another restoration is rejected.
- [ ] Generation completion alone does not approve Step 5.
- [ ] Visual review is required.
- [ ] Warning acknowledgment is required when warnings exist.
- [ ] Active correction sessions block approval.
- [ ] Approval snapshots candidate, settings, metrics, versions, and signatures.
- [ ] Independent restoration approval works.
- [ ] Aggregate Step 5 completes only after the final restoration is approved.

## Invalidation and Cleanup

- [ ] Step 1 invalidation propagates to Step 5.
- [ ] Step 2 invalidation propagates to Step 5.
- [ ] Step 3 margin or target change invalidates the owning Step 5 state.
- [ ] Step 4 axis or analysis change invalidates blockout and candidates.
- [ ] Any Step 5 setting change marks existing results stale.
- [ ] Missing or ownership-corrupted objects fail safely.
- [ ] Valid pointers recover from managed metadata.
- [ ] Removing one restoration preserves all others.
- [ ] Confirmed case reset removes all Step 5 managed artifacts.
- [ ] Unrelated scene objects, collections, materials, and transforms remain unchanged.

## Persistence and UI

- [ ] Save and reopen preserve restoration order and active index.
- [ ] Settings, metrics, candidates, selected candidate, and approval persist.
- [ ] Managed pointers recover after reopen.
- [ ] Visibility and focus controls are scoped to the active restoration.
- [ ] Normal Sidebar-width layout remains readable.
- [ ] Progress, rank, score, errors, warnings, metrics, and disclaimer remain usable.

## Performance and Cancellation

Record representative fixture results for:

- source triangle count;
- extracted patch size;
- generated candidate size;
- candidate count;
- iterations;
- preparation extraction duration;
- blockout duration;
- relief and seal-band duration;
- validation duration;
- total generation duration;
- peak managed temporary object count.

- [ ] Runtime remains within the accepted bounded policy.
- [ ] Candidate and iteration limits are enforced.
- [ ] Cancellation leaves no partial authoritative replacement.
- [ ] UI remains responsive to the accepted extent of the implementation.
- [ ] Failure and cancellation clean temporary data.

## Safety Record

Across all accepted scenarios verify that:

- [ ] Imported scan mesh identity, topology, coordinates, materials, and color attributes remain unchanged.
- [ ] Approved margins, antagonist regions, axes, and Step 4 analysis remain unchanged.
- [ ] Step 5 operations affect only restoration-owned managed artifacts and state.
- [ ] Failed, cancelled, stale, or incomplete operations never create false approval.
- [ ] No candidate is silently represented as clinically certified.

## Defects and Deviations

Record every defect found during implementation or local verification, including:

- observed behavior;
- root cause;
- correction;
- policy or schema version changes;
- retest result;
- any accepted deviation from the PRD.

## Acceptance Record

This section must remain incomplete until all required package, migration, regression, geometry, validation, performance, persistence, cleanup, UI, and safety checks pass locally.