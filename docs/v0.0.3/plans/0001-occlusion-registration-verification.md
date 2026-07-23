# Plan 0001: Occlusion Registration & Verification

## Metadata

- **Version:** v0.0.3
- **Status:** Completed
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

The completed workflow preserves imported transforms until the user acts, supports imported candidates, manual correction, and bite-guided refinement, keeps the upper jaw fixed, and requires explicit approval before Step 2 is complete.

## Implemented Source Structure

```text
extension/
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

## Completed Architecture

### State Layer

`properties.py` contains:

- Step 2 status and validity.
- Alignment mode and bite source.
- Active-session state.
- Warning acknowledgment and review confirmation.
- Persistent verification method and summary.
- Registration metrics.
- Session and approved matrix snapshots.
- Step 1-to-Step 2 invalidation behavior.

### Registration Layer

`alignment.py` provides:

- World-space evaluated-mesh sampling.
- Deterministic bounded point selection.
- KDTree correspondence search.
- Maximum-distance rejection.
- Robust trimming and inlier thresholds.
- Rigid rotation-and-translation estimation.
- Bounded point-to-point ICP.
- Structured registration results and metrics.

### Validation Layer

`occlusion_validation.py` provides:

- Step 2 precondition checks.
- Imported-relationship analysis.
- Finite and rigid-matrix checks.
- Gross-separation and overlap diagnostics.
- Bilateral bite consistency checks.
- Approval-readiness results.

### Session Layer

`step_two_session.py` provides:

- Exact copied world-matrix snapshots.
- Matrix serialization and restoration.
- Upper-jaw reference preservation.
- Reset, cancel, apply, and failure rollback support.

### Operator Layer

`step_two_operators.py` provides:

- Imported analysis.
- Single Arch not-applicable completion.
- Session start, reset, cancel, and apply.
- Manual candidate capture.
- Right, Left, and Both Bites registration.
- Candidate verification.
- Explicit approval.
- Safe Step 1 navigation.

### UI Layer

`ui.py` provides context-sensitive controls based on:

- Scan configuration.
- Current Step 2 status.
- Alignment mode.
- Bite availability.
- Active session.
- Candidate, warning, verification, and completion state.

## Completed Registration Strategy

### Imported Candidate

- Entering Step 2 does not move objects.
- Analysis is explicit.
- Plausible relationships become `IMPORTED_CANDIDATE`.
- Implausible relationships become `NEEDS_ALIGNMENT`.
- Analysis never approves the case automatically.

### Manual Alignment

- The lower jaw is the moving object.
- Blender move and rotate tools are used for positioning.
- Manual capture validates finite and rigid transforms.
- Manual positioning can provide coarse initialization before bite refinement.

### Bite-Guided Alignment

- The upper jaw is fixed.
- Each selected bite is registered to the upper jaw.
- The lower jaw is registered through the aligned bite reference.
- Both Bites mode uses a combined target and reports right-versus-left disagreement.
- Direct upper-to-lower ICP is not used.

## Completed Implementation Phases

1. **Documentation approval** — requirements, terminology, decisions, and scope approved.
2. **State and migration** — Step 2 properties, defaults, persistence, and invalidation implemented.
3. **Session safety** — copied matrices, reset, cancel, apply, and rollback implemented.
4. **Applicability and imported analysis** — Single Arch and imported-candidate paths implemented.
5. **Registration core** — deterministic sampling, KDTree, trimming, rigid estimation, ICP, and metrics implemented.
6. **Manual alignment** — manual session and candidate capture implemented.
7. **Bite-guided registration** — Right, Left, and Both Bites paths implemented.
8. **Verification and approval** — checks, warnings, confirmations, approval, and bite hiding implemented.
9. **Invalidation and monitoring** — Step 1 and material-transform invalidation implemented.
10. **UI and packaging** — Step 2 UI, manifest `0.0.3`, module packaging, and registration implemented.
11. **Verification and completion** — full scenario matrix completed and documentation finalized.

## Implementation Deviations

The implementation introduced two focused modules that were not separated in the earliest proposed source layout:

- `step_two_session.py` for matrix and reversible-session helpers.
- `step_two_operators.py` for Step 2-specific Blender operators.

This separation improved responsibility boundaries and kept the existing Step 1 modules stable. No accepted product behavior was removed by this deviation.

## Safety Results

- Imported transforms remain unchanged until the user acts.
- The upper jaw remains fixed during registration.
- Reset and cancel restore exact session-start matrices.
- Failed registration restores safe matrices.
- Candidate application does not imply approval.
- Mesh data and topology remain unchanged.
- Insufficient overlap produces corrective guidance.
- Explicit approval is required for `step_2_valid = true`.

## Verification Result

The documented PowerShell validation, package build, installation, migration, Step 1 regression, Step 2 scenario, persistence, invalidation, and lifecycle checks passed locally.

See [`../VERIFICATION.md`](../VERIFICATION.md) for the final acceptance record.

## Completion Record

Plan 0001 is complete:

- Documentation is accepted.
- Every required task is complete.
- Every acceptance criterion passed locally.
- Step 1 remains regression-free.
- Registration is reversible and scale-preserving.
- Direct upper-to-lower ICP is absent.
- User approval is required for Step 2 completion.
- The package is ready for review and **Squash and merge**.
