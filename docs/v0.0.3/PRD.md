# Product Requirements Document: v0.0.3

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.3
- **Status:** Accepted
- **Target branch:** `feat/v0.0.3-occlusion-registration-verification`
- **Target merge branch:** `main`
- **Workflow stage:** Step 2 — Occlusion Registration & Verification

## Product Overview

B-Dental `v0.0.3` replaces the Step 2 placeholder introduced in `v0.0.2` with a controlled workflow for evaluating, adjusting, registering, and explicitly approving the maxillomandibular relationship.

Imported upper and lower scans are treated as an unverified candidate. Entering Step 2 does not move objects. When correction is required, the user can use manual positioning or right, left, or bilateral bite-guided registration. The upper jaw remains fixed and the lower jaw is the moving arch.

The version provides engineering checks and reproducible registration assistance. It does not certify clinical correctness and does not replace professional review.

## Accepted Scope

Version `v0.0.3` includes:

- Scene-persistent Step 2 state with safe defaults for v0.0.2 scenes.
- Single Arch completion as explicitly not applicable.
- Dual Arch imported analysis and manual alignment.
- Full Scan Set imported, manual, Right Bite, Left Bite, and Both Bites paths.
- Imported-relationship analysis without automatic movement.
- Reversible alignment sessions with exact matrix snapshots.
- Upper jaw as fixed world-space reference.
- Lower jaw as the moving arch.
- Transform-only alignment with no mesh-coordinate or topology edits.
- Deterministic evaluated-mesh sampling.
- Blender KDTree nearest-neighbor correspondence search.
- Robust distance trimming and inlier thresholds.
- Bounded rigid point-to-point ICP.
- Registration metrics and bilateral bite disagreement diagnostics.
- Blocking errors and non-blocking warnings.
- Explicit warning acknowledgment and user review confirmation.
- Explicit approval before `step_2_valid` can become true.
- Persistent verification method, summary, matrices, and metrics.
- Invalidation after Step 1 changes or material approved-transform changes.
- Context-sensitive Step 2 UI and safe navigation back to Step 1.
- Blender Extension validation, package build, installation, lifecycle, and regression verification.

## Out of Scope

Version `v0.0.3` does not include:

- Dynamic occlusion or mandibular-motion simulation.
- Virtual articulator parameters, facebow, condylar-axis, or centric-relation workflows.
- Automatic global registration from arbitrarily separated scans.
- Feature-based, non-rigid, or machine-learning registration.
- Direct upper-to-lower ICP.
- Mesh cleanup, smoothing, remeshing, decimation, or hole filling.
- Automatic collision correction.
- Clinical certification, diagnosis, or treatment decisions.
- Third-party Python dependencies.
- Production Step 3 behavior.

## Workflow Rules

### Preconditions

Step 2 requires:

- An initialized B-Dental case.
- A valid Step 1 result.
- Live required scan objects with valid B-Dental metadata.

If Step 1 becomes invalid, Step 2 is also invalidated.

### Single Arch

- Registration controls are not shown.
- The user explicitly completes Step 2 as not applicable.
- `step_2_status` becomes `NOT_APPLICABLE`.
- `step_2_valid` becomes true only after confirmation.

### Dual Arch

Supported paths:

- Analyze Imported Relationship.
- Keep Imported Relationship.
- Manual Alignment.
- Engineering Verification.
- Explicit Approval.

### Full Scan Set

Supported paths:

- Analyze Imported Relationship.
- Keep Imported Relationship.
- Manual Alignment.
- Right Bite registration.
- Left Bite registration.
- Both Bites registration.
- Engineering Verification.
- Explicit Approval.

## State Model

Step 2 statuses:

- `NOT_STARTED`
- `NOT_APPLICABLE`
- `IMPORTED_CANDIDATE`
- `NEEDS_ALIGNMENT`
- `ALIGNING`
- `CANDIDATE`
- `VERIFIED`
- `ERROR`

Alignment modes:

- `IMPORTED`
- `BITE_GUIDED`
- `MANUAL`

Bite sources:

- `RIGHT`
- `LEFT`
- `BOTH`

`step_2_valid` is workflow completion state. It is not inferred from operator success, ICP convergence, a low RMSE, visual plausibility, or candidate application.

## Safety and Registration Requirements

- Step 2 entry preserves all transforms.
- Imported analysis preserves all transforms.
- Every alignment session copies relevant world matrices.
- Reset restores the session-start matrices without ending the session.
- Cancel restores the session-start matrices and closes the session.
- Apply keeps the candidate transform but does not approve it.
- Exceptions and failed registration restore safe matrices.
- The upper jaw remains fixed.
- Automatic arch registration changes only the lower-jaw transform.
- Bite objects may move temporarily as intermediate references.
- Direct upper-to-lower ICP is prohibited.
- Registration changes transforms only and preserves mesh data.
- Insufficient overlap fails safely with manual coarse-position guidance.

## Verification and Approval Requirements

Before approval, B-Dental must:

- Validate required objects and metadata.
- Validate finite and rigid transforms.
- Confirm the upper jaw remains fixed within tolerance.
- Report available registration metrics.
- Report gross separation and relevant geometry warnings.
- Report bilateral disagreement when applicable.
- Separate blocking errors from warnings.
- Require acknowledgment when warnings exist.
- Require explicit visual-review confirmation.

Approval:

- Sets `step_2_status = VERIFIED`.
- Sets `step_2_valid = true`.
- Records method, metrics, and summary.
- Preserves bite objects and hides them by default.
- Does not claim clinical correctness.

## Implementation Structure

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

Responsibilities:

- `alignment.py`: sampling, KDTree correspondence search, robust trimming, rigid estimation, ICP, and registration results.
- `occlusion_validation.py`: imported analysis, transform checks, separation and overlap diagnostics, bilateral consistency, and approval readiness.
- `step_two_session.py`: copied matrix snapshots, serialization, restoration, and session safety helpers.
- `step_two_operators.py`: Step 2 analysis, session, registration, verification, approval, and navigation operators.
- `properties.py`: persistent workflow state and invalidation.
- `ui.py`: context-sensitive Step 2 presentation.

## Acceptance Record

All acceptance criteria were completed locally before this document was marked accepted:

1. Manifest validation and `0.0.3` package build passed.
2. Installation and enablement passed without B-Dental errors.
3. v0.0.2 case migration passed.
4. Step 1 regression scenarios passed.
5. Step 2 entry preserved transforms.
6. Single Arch not-applicable completion passed.
7. Imported plausible and gross-separation analysis passed.
8. Manual session reset, cancel, capture, and apply behavior passed.
9. Right, Left, and Both Bites registration paths passed on the selected fixtures.
10. Insufficient-overlap failure restored safe matrices.
11. Direct upper-to-lower ICP was not used.
12. The upper jaw remained fixed and mesh data remained unchanged.
13. Metrics, warnings, and bilateral disagreement were displayed.
14. Candidate application did not approve Step 2.
15. Explicit review, warning acknowledgment, and approval were enforced.
16. Approval persistence and invalidation behavior passed.
17. Repeated enable, disable, and reload lifecycle checks passed.
18. Verification results were recorded in `VERIFICATION.md`.

## Final Status

The v0.0.3 requirements are accepted and the implementation is ready for a non-draft pull request and **Squash and merge**.
