# Plan 0001: Occlusion Registration & Verification

## Metadata

- **Version:** v0.0.3
- **Status:** Proposed
- **Target branch:** `feat/v0.0.3-occlusion-registration-verification`
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related tasks:** [`../TASKS.md`](../TASKS.md)
- **Related decisions:**
  - [`../decisions/0001-imported-relationship-is-a-candidate.md`](../decisions/0001-imported-relationship-is-a-candidate.md)
  - [`../decisions/0002-use-bite-mediated-registration.md`](../decisions/0002-use-bite-mediated-registration.md)
  - [`../decisions/0003-fix-upper-and-use-reversible-sessions.md`](../decisions/0003-fix-upper-and-use-reversible-sessions.md)
  - [`../decisions/0004-require-explicit-user-approval.md`](../decisions/0004-require-explicit-user-approval.md)

## Objective

Replace the Step 2 placeholder from `v0.0.2` with a safe, measurable, reversible workflow for occlusion registration and verification.

The workflow must preserve an imported jaw relationship until the user chooses an action. It must support imported candidates, manual correction, and bite-guided refinement while keeping the upper jaw fixed and requiring explicit approval before Step 2 is complete.

## Current State

The repository currently provides:

- Valid Step 1 case initialization and scan import.
- Persistent pointers for upper jaw, lower jaw, right bite, and left bite.
- Single Arch, Dual Arch, and Full Scan Set configurations.
- Step 1 validation.
- A Step 2 placeholder reading `Not Implemented Yet.`
- No occlusion state, transform snapshots, registration engine, or approval workflow.

## Planned Source Structure

```text
extension/
├── __init__.py
├── blender_manifest.toml
├── alignment.py
├── occlusion_validation.py
├── operators.py
├── properties.py
├── scene_utils.py
├── ui.py
└── validation.py
```

## Architecture

### State Layer

`properties.py` will extend the existing scene property group with:

- Step 2 status and validity.
- Alignment mode and bite source.
- Active-session state.
- Warning acknowledgment and review confirmation.
- Persistent method and summary.
- Registration metrics.
- Matrix snapshots and approved matrices.

Step 1 invalidation must also invalidate Step 2.

### Registration Layer

`alignment.py` will contain no panel drawing. It will provide:

- World-space evaluated-mesh sampling.
- Deterministic point limiting.
- KDTree correspondence search.
- Maximum-distance rejection.
- Robust trimming.
- Rigid transform estimation.
- Point-to-point ICP.
- Structured registration results.

The implementation must use only Blender's bundled Python APIs and standard library.

### Occlusion Validation Layer

`occlusion_validation.py` will provide:

- Step 2 precondition checks.
- Imported-relationship analysis.
- Rigid-matrix validation.
- Gross-separation checks.
- Optional BVH overlap diagnostics.
- Bilateral bite consistency checks.
- Approval-readiness results.

### Session Layer

Alignment actions will run inside a reversible session:

1. Copy relevant world matrices.
2. Keep the upper jaw fixed.
3. Preview lower-jaw and bite transforms.
4. Allow reset, cancel, or apply.
5. Keep approval separate from apply.

### UI Layer

`ui.py` will draw Step 2 according to:

- Scan configuration.
- Current Step 2 status.
- Active session.
- Available bite scans.
- Candidate and verification results.

## Registration Strategy

### Imported Candidate

Entering Step 2 does not move objects. The user runs analysis explicitly.

Analysis classifies the current relationship as:

- Plausible imported candidate.
- Alignment required.
- Blocking input error.

It never marks the relationship verified.

### Manual Alignment

The user may position the lower jaw with Blender transform tools. B-Dental captures the resulting matrix as a candidate after checking finite values, rigid scale, and upper-jaw stability.

### Bite-Guided Alignment

The upper jaw is the world-space reference.

For each selected bite:

1. Register the bite to the upper jaw.
2. Use the aligned bite as an intermediate target for the lower jaw.
3. Refine the lower jaw using robust trimmed correspondences.

For Both Bites:

1. Align each bite to the upper jaw independently.
2. Build a combined target from both aligned bite scans.
3. Refine the lower jaw against the combined target.
4. Calculate right-only and left-only diagnostic transforms.
5. Report disagreement.

Direct upper-to-lower ICP is prohibited.

## Implementation Phases

### Phase 1: Documentation Approval

- Review requirements and terminology.
- Confirm that imported relationships are candidates only.
- Confirm upper fixed / lower moving behavior.
- Confirm explicit approval semantics.
- Confirm no clinical-certification claims.

Exit condition: documentation approved.

### Phase 2: State and Migration

- Add Step 2 enums and properties.
- Add safe defaults for v0.0.2 scenes.
- Add Step 2 invalidation.
- Add persistent matrix and metric storage.

Exit condition: old cases open safely and Step 2 state persists.

### Phase 3: Session Safety

- Implement matrix copy, serialization, and restoration helpers.
- Add start, reset, cancel, and apply actions.
- Guarantee upper-jaw immobility.
- Restore safe matrices on errors.

Exit condition: preview transforms are fully reversible.

### Phase 4: Imported Analysis and Applicability

- Add Single Arch not-applicable path.
- Add imported relationship analysis.
- Add coarse plausibility and separation diagnostics.
- Add candidate and needs-alignment states.

Exit condition: Step 2 classifies input without moving objects.

### Phase 5: Registration Core

- Add deterministic evaluated-mesh sampling.
- Add KDTree correspondence search.
- Add trimming and inlier thresholds.
- Add rigid transform estimation.
- Add bounded ICP and metrics.
- Add progress reporting.

Exit condition: the engine returns reproducible structured results and fails safely.

### Phase 6: Manual Alignment

- Add manual mode.
- Select lower jaw for transform tools.
- Capture and validate manual candidates.
- Permit manual coarse initialization before ICP.

Exit condition: manual candidates can be created and reversed.

### Phase 7: Bite-Guided Registration

- Add Right, Left, and Both Bites paths.
- Align bite scans to the fixed upper jaw.
- Align lower jaw through bite references.
- Calculate bilateral diagnostics.
- Add disagreement thresholds and messages.

Exit condition: suitable fixtures produce stable candidates and unsuitable fixtures fail safely.

### Phase 8: Verification and Approval

- Add engineering verification checks.
- Separate blocking errors and warnings.
- Add warning acknowledgment.
- Add explicit review confirmation.
- Add approval, persistence, and bite hiding.

Exit condition: Step 2 becomes valid only after explicit approval.

### Phase 9: Invalidation and Monitoring

- Invalidate after Step 1 changes.
- Detect material approved-transform changes.
- Avoid duplicate handlers.
- Preserve objects during invalidation.

Exit condition: stale approvals cannot survive material input changes.

### Phase 10: UI and Packaging

- Replace the Step 2 placeholder.
- Add context-sensitive controls and metrics.
- Update manifest and registration.
- Validate and build package.

Exit condition: complete workflow is accessible at normal sidebar width.

### Phase 11: Verification and Completion

- Execute the full scenario matrix.
- Record actual results and deviations.
- Update README, PRD, plan, tasks, and verification status.
- Prepare for squash merge.

Exit condition: every acceptance criterion passes.

## Default Registration Parameters

Initial implementation defaults should be conservative and configurable in code:

- Deterministic point cap per object.
- Maximum correspondence distance based on scene units and dental-scale assumptions.
- Robust retained-distance percentile.
- Minimum correspondence count.
- Minimum inlier ratio.
- Maximum iteration count.
- Translation convergence tolerance.
- Rotation convergence tolerance.
- RMSE-change tolerance.

Exact values must be verified with multiple de-identified fixtures before acceptance and documented as implementation constants rather than clinical thresholds.

## Error Handling

- Missing or stale objects produce blocking errors.
- Non-finite matrices abort before movement.
- Insufficient overlap requests manual coarse positioning.
- Non-convergence restores the last safe matrices.
- Registration exceptions restore session-start matrices.
- Active sessions cannot be abandoned silently.
- Applying a candidate never implies approval.
- Approval is blocked until required checks pass.

## Performance Strategy

- Use deterministic vertex subsampling.
- Reuse KDTree targets within an iteration stage.
- Bound point counts and iterations.
- Avoid Python threads.
- Use Blender progress reporting.
- Do not duplicate meshes solely for computation.

## Testing Strategy

Testing is primarily scenario-driven inside Blender.

Required fixtures include:

- Single Arch case.
- Dual Arch case with a plausible imported relationship.
- Dual Arch case with gross separation.
- Full set with good right and left bites.
- Full set with only right bite usable.
- Full set with only left bite usable.
- Full set with noisy bite fragments.
- Full set with bilateral disagreement.
- Insufficient-overlap fixture.
- Previously saved v0.0.2 case.

All fixtures must be de-identified.

## Risks and Mitigations

### Imported Alignment Trust

Mitigation: treat it as a candidate and require explicit approval.

### ICP Local Minima

Mitigation: require reasonable initial overlap, robust trimming, bounded transforms, and manual coarse positioning when needed.

### Noisy Bite Geometry

Mitigation: distance rejection, trimming, minimum inlier requirements, and bilateral diagnostics.

### Destructive Transform Changes

Mitigation: exact matrix snapshots and reversible sessions.

### False Clinical Confidence

Mitigation: label metrics as engineering aids and require professional visual review.

### Performance

Mitigation: deterministic bounded sampling and iteration limits.

### State Migration

Mitigation: additive properties with safe defaults and no destructive migration.

## Completion Rule

Plan 0001 is complete only when:

- Documentation is approved.
- Every required task is implemented.
- Every acceptance criterion passes locally.
- Step 1 remains regression-free.
- Registration is reversible and scale-preserving.
- Direct upper-to-lower ICP is absent.
- User approval is required for `step_2_valid = true`.
- Actual verification results are recorded.
- The package is ready for review and squash merge.
