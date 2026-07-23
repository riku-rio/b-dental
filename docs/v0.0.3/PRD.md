# Product Requirements Document: v0.0.3

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.3
- **Status:** Proposed
- **Target branch:** `feat/v0.0.3-occlusion-registration-verification`
- **Target merge branch:** `main`
- **Workflow stage:** Step 2 — Occlusion Registration & Verification

## Product Overview

B-Dental `v0.0.3` replaces the Step 2 placeholder introduced in `v0.0.2` with a controlled workflow for evaluating, adjusting, registering, and explicitly approving the maxillomandibular relationship.

Many scanner exports already preserve an upper-to-lower relationship. B-Dental must not assume that this relationship is correct, but it must also avoid moving a case that is already well registered. The imported relationship therefore begins as an unverified candidate.

When adjustment is required, the user may preserve the imported relationship, perform a manual correction, or use right and left buccal bite scans as registration references. The upper jaw remains the fixed reference and the lower jaw is the moving arch.

This version provides engineering checks and reproducible registration assistance. It does not certify clinical correctness and does not replace professional review.

## Problem Statement

Version `v0.0.2` imports and validates upper-jaw, lower-jaw, right-bite, and left-bite STL objects, but Step 1 validates only file roles and basic mesh integrity. It does not determine whether the jaws are in a reliable occlusal relationship.

A correct Step 2 must handle several real input conditions:

- Upper and lower scans exported in a shared, already articulated coordinate system.
- Upper and lower scans that are approximately positioned but require refinement.
- Full scan sets where right and left bite scans are available.
- Cases that require manual coarse positioning before automatic refinement can succeed.
- Single-arch cases where occlusion registration is not applicable.

The workflow must preserve existing transforms, avoid destructive mesh changes, fail safely when overlap is insufficient, and require explicit user verification before Step 2 is considered complete.

## Version Goal

Implement Step 2 with the following behavior:

1. Enter Step 2 only after Step 1 is valid.
2. Preserve the imported jaw relationship without moving objects automatically.
3. Analyze the imported relationship as an unverified candidate.
4. Support imported, bite-guided, and manual alignment paths where applicable.
5. Keep the upper jaw fixed and move only the lower jaw during arch alignment.
6. Use right, left, or both bite scans as intermediate registration references.
7. Provide reversible alignment sessions with preview, reset, apply, and cancel actions.
8. Provide measurable registration and geometry feedback.
9. Require explicit user review and approval.
10. Set `step_2_valid = true` only after approval.
11. Preserve the verified result when the `.blend` file is saved and reopened.

## User Stories

- As a dental Blender user, I want B-Dental to preserve an imported jaw relationship so that a correctly exported case is not moved unnecessarily.
- As a dental Blender user, I want to know whether the imported relationship is plausible before I accept it.
- As a dental Blender user, I want to use right and left bite scans to refine jaw registration when the imported relationship is unreliable.
- As a dental Blender user, I want to position the lower jaw manually before refinement when the scans do not begin with sufficient overlap.
- As a dental Blender user, I want every automatic transform to be reversible until I explicitly apply it.
- As a dental Blender user, I want measurable warnings and errors so that I can understand why registration succeeded or failed.
- As a dental Blender user, I want to approve the final relationship explicitly rather than having the software claim clinical correctness automatically.
- As a single-arch user, I want Step 2 to explain that occlusion registration is not applicable instead of presenting irrelevant controls.

## In Scope

- Replacement of the Step 2 placeholder with an occlusion workflow.
- Scene-persistent Step 2 state.
- Safe migration of scenes created with `v0.0.2`.
- Step 2 applicability handling for Single Arch, Dual Arch, and Full Scan Set cases.
- Imported-relationship analysis without automatic movement.
- Imported relationship acceptance path.
- Manual lower-jaw positioning path.
- Bite-guided rigid registration path.
- Right Bite, Left Bite, and Both Bites registration sources.
- Upper jaw as the fixed world-space reference.
- Lower jaw as the moving arch.
- Temporary movement of bite objects when required for registration.
- Transform-only alignment; no mesh-coordinate editing.
- Reversible alignment sessions.
- Snapshot, reset, cancel, apply, and approve actions.
- Deterministic world-space point sampling.
- Nearest-neighbor matching with Blender `mathutils.kdtree.KDTree`.
- Robust correspondence filtering and trimmed point-to-point ICP.
- Rigid-transform estimation without third-party dependencies.
- Bounded iteration and convergence checks.
- Registration metrics including inlier count, inlier ratio, RMSE, median distance, iteration count, translation delta, and rotation delta.
- Right-versus-left bite consistency diagnostics when both bites are available.
- Gross separation and triangle-overlap warnings where practical.
- Explicit user review confirmation.
- Persistent verification method and summary.
- Automatic invalidation when Step 1 inputs or approved transforms materially change.
- Extension validation, build, installation, lifecycle, and manual verification documentation.

## Out of Scope

- Dynamic occlusion or mandibular motion simulation.
- Virtual articulator parameters.
- Condylar-axis or facebow registration.
- Centric-relation acquisition.
- Automatic global registration from arbitrarily separated scans.
- Feature-based global registration.
- Machine-learning scan classification.
- Direct upper-jaw-to-lower-jaw ICP.
- Non-rigid registration.
- Mesh cleanup, smoothing, decimation, remeshing, or hole filling.
- Automatic removal of soft tissue or floating fragments.
- Clinical contact certification.
- Collision correction that changes the captured jaw relationship automatically.
- Patient diagnosis or treatment decisions.
- CBCT, DICOM, PLY, OBJ, or proprietary scanner formats.
- Third-party Python dependencies such as NumPy, SciPy, Open3D, or VTK.
- Production Step 3 behavior.

## Workflow Model

### Preconditions

Step 2 may be entered only when:

- A B-Dental case is initialized.
- Step 1 is valid.
- Required scan objects still exist.
- Required scan metadata remains valid.

If Step 1 becomes invalid, Step 2 must also become invalid.

### Single Arch

Occlusion registration is not applicable when only one arch is required.

The Step 2 UI must:

- Explain why occlusion registration is unavailable.
- Offer `Complete as Not Applicable`.
- Set `step_2_status = NOT_APPLICABLE` and `step_2_valid = true` only after explicit confirmation.

### Dual Arch

Dual Arch supports:

- Analyze Imported Relationship.
- Keep Imported Relationship.
- Manual Alignment.
- Geometry Verification.
- Explicit Approval.

Bite-guided registration is unavailable unless valid bite objects are present.

### Full Scan Set

Full Scan Set supports:

- Analyze Imported Relationship.
- Keep Imported Relationship.
- Manual Alignment.
- Right Bite registration.
- Left Bite registration.
- Both Bites registration.
- Geometry Verification.
- Explicit Approval.

### Step 2 Completion

There is no production Step 3 in this version. After approval, the panel remains on Step 2 and displays a completed verification summary.

## Step 2 State Model

### Status Values

The state must support at least:

- `NOT_STARTED`
- `NOT_APPLICABLE`
- `IMPORTED_CANDIDATE`
- `NEEDS_ALIGNMENT`
- `ALIGNING`
- `CANDIDATE`
- `VERIFIED`
- `ERROR`

### Alignment Modes

The state must support:

- `IMPORTED`
- `BITE_GUIDED`
- `MANUAL`

### Bite Sources

The state must support:

- `RIGHT`
- `LEFT`
- `BOTH`

### Application Boolean

`step_2_valid` represents B-Dental workflow completion only.

It must not be inferred from:

- A Blender operator returning `{'FINISHED'}`.
- ICP convergence by itself.
- Low RMSE by itself.
- The imported objects looking visually aligned.

`step_2_valid` becomes true only when:

- Step 2 is explicitly completed as not applicable, or
- A candidate passes required engineering checks and the user explicitly approves it.

## Functional Requirements

### State and Migration

- **FR-001:** Add scene-persistent Step 2 state to the existing workflow `PropertyGroup`.
- **FR-002:** Add `step_2_status` and `step_2_valid`.
- **FR-003:** Add alignment mode and bite-source properties.
- **FR-004:** Add alignment-session state.
- **FR-005:** Add persistent matrix snapshots for the upper jaw, lower jaw, right bite, and left bite where required.
- **FR-006:** Add persistent verification summary and method.
- **FR-007:** Add persistent registration metrics.
- **FR-008:** Existing `v0.0.2` scenes must open without migration errors.
- **FR-009:** Missing new properties must use safe defaults.
- **FR-010:** Step 1 invalidation must reset Step 2 validity and active-session state.

### Entry and Applicability

- **FR-011:** Step 2 controls must require `step_1_valid = true`.
- **FR-012:** Step 2 must re-check that required objects remain alive and correctly tagged.
- **FR-013:** Single Arch must display an explicit not-applicable state.
- **FR-014:** Single Arch completion must require confirmation.
- **FR-015:** Dual Arch must require upper and lower scans.
- **FR-016:** Full Scan Set must require upper, lower, right bite, and left bite scans.
- **FR-017:** Step 2 entry must not move any object automatically.

### Imported Relationship Analysis

- **FR-018:** Provide `Analyze Imported Relationship`.
- **FR-019:** Analysis must preserve all object transforms.
- **FR-020:** Analysis must confirm finite matrices and valid rigid-transform components.
- **FR-021:** Analysis must calculate coarse spatial plausibility metrics.
- **FR-022:** Analysis must detect gross separation between arches.
- **FR-023:** Analysis may report triangle overlap as a warning but must not treat all overlap as failure.
- **FR-024:** A plausible imported relationship must become `IMPORTED_CANDIDATE`, not `VERIFIED`.
- **FR-025:** An implausible imported relationship must become `NEEDS_ALIGNMENT` with actionable feedback.

### Alignment Session Safety

- **FR-026:** Starting an alignment session must snapshot relevant world matrices.
- **FR-027:** The upper-jaw matrix must be treated as fixed during the session.
- **FR-028:** Automatic arch registration must modify only the lower-jaw world matrix.
- **FR-029:** Bite-guided registration may preview transformed bite matrices.
- **FR-030:** Registration must not edit mesh vertex coordinates or topology.
- **FR-031:** `Reset Preview` must restore the session-start matrices without ending the session.
- **FR-032:** `Cancel Alignment` must restore the session-start matrices and clear the candidate.
- **FR-033:** `Apply Candidate` must keep the candidate transforms and end the preview session.
- **FR-034:** Applying a candidate must not mark Step 2 verified.
- **FR-035:** Alignment operators must support Blender undo where practical.
- **FR-036:** Registration exceptions must restore the last safe matrices.

### Manual Alignment

- **FR-037:** Provide a manual alignment mode.
- **FR-038:** Manual mode must select and expose the lower jaw as the moving object.
- **FR-039:** Manual instructions must direct the user to Blender move and rotate tools.
- **FR-040:** Provide `Capture Manual Candidate`.
- **FR-041:** Manual capture must reject non-finite matrices.
- **FR-042:** Manual capture must reject non-rigid scale or shear changes outside tolerance.
- **FR-043:** Manual capture must create a candidate without automatically verifying it.
- **FR-044:** Manual positioning may be used as coarse initialization before bite refinement.

### Registration Core

- **FR-045:** Add a focused registration module independent from UI drawing.
- **FR-046:** Sample evaluated mesh vertices in world space.
- **FR-047:** Sampling must be deterministic and bounded by a documented maximum.
- **FR-048:** Use Blender `KDTree` for nearest-neighbor queries.
- **FR-049:** Reject correspondences beyond a maximum distance.
- **FR-050:** Apply robust distance trimming to reduce the effect of soft tissue, unmatched jaw surfaces, and floating fragments.
- **FR-051:** Require a minimum inlier count and inlier ratio.
- **FR-052:** Estimate rotation and translation only.
- **FR-053:** Preserve object scale.
- **FR-054:** Implement rigid-transform estimation without third-party dependencies.
- **FR-055:** Bound the iteration count.
- **FR-056:** Stop when transform change and RMSE change satisfy convergence tolerances.
- **FR-057:** Return a structured registration result.
- **FR-058:** The result must include success, errors, warnings, transform, iteration count, inlier count, inlier ratio, RMSE, and median distance.
- **FR-059:** Failure to converge must not leave partial transforms applied.
- **FR-060:** Insufficient initial overlap must fail with a request for manual coarse positioning.
- **FR-061:** Display progress through Blender's progress API where practical.

### Bite-Guided Registration

- **FR-062:** Bite-guided registration must never run direct ICP between upper and lower jaws.
- **FR-063:** The selected bite scan must first register to the fixed upper jaw.
- **FR-064:** Lower-jaw registration must use the aligned bite scan as the intermediate target.
- **FR-065:** Right Bite mode must use the right bite only.
- **FR-066:** Left Bite mode must use the left bite only.
- **FR-067:** Both Bites mode must align each bite to the upper jaw.
- **FR-068:** Both Bites mode must refine the lower jaw against a combined target derived from both aligned bites.
- **FR-069:** Both Bites mode must calculate right-only and left-only diagnostics.
- **FR-070:** Large right-versus-left transform disagreement must produce a warning or blocking error according to severity.
- **FR-071:** Bite registration must reject missing, stale, or incorrectly tagged bite objects.
- **FR-072:** Bite registration must tolerate unmatched portions through robust trimming.
- **FR-073:** Bite registration must fail safely when usable overlap cannot be established.

### Candidate Verification

- **FR-074:** Provide `Run Verification Checks`.
- **FR-075:** Verification must confirm required objects and metadata.
- **FR-076:** Verification must confirm finite transforms.
- **FR-077:** Verification must confirm that the upper jaw has not moved beyond tolerance during the session.
- **FR-078:** Verification must confirm that the lower transform is rigid within tolerance.
- **FR-079:** Verification must expose available registration metrics.
- **FR-080:** Verification must report gross separation.
- **FR-081:** Verification may report mesh overlap and possible interpenetration as warnings.
- **FR-082:** Verification must not claim that geometric metrics prove clinical correctness.
- **FR-083:** Blocking registration errors must prevent approval.
- **FR-084:** Non-blocking warnings may be accepted only after explicit acknowledgment.
- **FR-085:** Provide a user-review confirmation control.
- **FR-086:** Provide `Approve Occlusion`.
- **FR-087:** Approval must set `step_2_status = VERIFIED` and `step_2_valid = true`.
- **FR-088:** Approval must record the selected method and summary metrics.
- **FR-089:** Approval must hide bite objects by default while preserving them for review.
- **FR-090:** Approval must not alter mesh data.

### Invalidation and Persistence

- **FR-091:** Replacing or removing any Step 1 scan must invalidate Step 2.
- **FR-092:** Changing scan configuration must invalidate Step 2.
- **FR-093:** A material lower-jaw transform change after approval must invalidate Step 2.
- **FR-094:** A material bite transform change after bite-guided approval must invalidate Step 2.
- **FR-095:** Invalidation must preserve objects unless a separate destructive action is confirmed.
- **FR-096:** Saving and reopening must preserve Step 2 state, applied matrices, metrics, and verification status.
- **FR-097:** Stale pointers after external deletion must be handled without UI exceptions.

### User Interface

- **FR-098:** Replace the Step 2 placeholder with workflow-aware UI.
- **FR-099:** Display Step 1 completion at the top of Step 2.
- **FR-100:** Display applicability and current Step 2 status.
- **FR-101:** Display imported-relationship analysis actions.
- **FR-102:** Display alignment mode controls appropriate to the scan configuration.
- **FR-103:** Display bite-source controls only when valid bite scans exist.
- **FR-104:** Display Start, Reset, Apply, and Cancel session actions contextually.
- **FR-105:** Display registration progress and results.
- **FR-106:** Display errors and warnings in actionable language.
- **FR-107:** Display registration metrics in normal sidebar width.
- **FR-108:** Provide visibility and focus controls for upper, lower, right bite, and left bite objects.
- **FR-109:** Provide `Back to Step 1` without silently discarding an active session.
- **FR-110:** Leaving Step 2 with an active preview must require confirmation or cancellation.
- **FR-111:** Display a completed summary after approval.

### Registration and Packaging

- **FR-112:** Update the manifest to version `0.0.3` during implementation.
- **FR-113:** Package every required new Python module.
- **FR-114:** Register new classes and handlers deterministically.
- **FR-115:** Unregister classes, properties, and handlers in reverse order.
- **FR-116:** Repeated enable, disable, and reload cycles must not duplicate handlers or properties.
- **FR-117:** Extension registration must not modify object transforms.

## Non-Functional Requirements

- **NFR-001:** Continue using Blender's modern Extensions model.
- **NFR-002:** Support Blender 4.2 or newer and verify with the project Blender version.
- **NFR-003:** Use no third-party Python dependencies.
- **NFR-004:** Preserve imported data unless the user explicitly applies a transform or confirms a destructive action.
- **NFR-005:** Automatic alignment must be deterministic for identical inputs and settings.
- **NFR-006:** Expensive operations must use bounded point counts and iterations.
- **NFR-007:** Registration code must remain separable from Blender panel drawing.
- **NFR-008:** Matrix snapshots must be copied rather than retained as mutable references.
- **NFR-009:** Registration must operate in world space.
- **NFR-010:** Automatic transforms must be rigid and scale-preserving.
- **NFR-011:** Errors must identify the failed stage and corrective action.
- **NFR-012:** Metrics are engineering aids and must not be labeled as clinical validation.
- **NFR-013:** The UI must remain usable at normal sidebar width.
- **NFR-014:** No patient-identifying information may be introduced.
- **NFR-015:** The implementation must not assume the extension directory is writable.
- **NFR-016:** Long operations must leave the scene in a safe state when they fail.
- **NFR-017:** The implementation must avoid Python threads because Blender data access is not thread-safe.

## Proposed Source Structure

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

Responsibilities:

- `alignment.py`: point sampling, correspondence search, robust trimming, rigid-transform estimation, ICP, and registration result models.
- `occlusion_validation.py`: imported-relationship analysis, candidate checks, transform checks, bite-consistency diagnostics, and approval readiness.
- Existing modules: extended for state, operators, scene helpers, registration lifecycle, and Step 2 UI.

## Acceptance Criteria

Version `v0.0.3` is accepted when all of the following are verified locally:

1. The manifest validates and the extension package builds as `0.0.3`.
2. The extension installs and enables without B-Dental errors.
3. Existing `v0.0.2` case files open safely.
4. Step 1 behavior remains unchanged.
5. Step 2 no longer displays the placeholder for valid dual-arch and full-set cases.
6. Entering Step 2 does not move any scan.
7. Single Arch can be completed explicitly as not applicable.
8. Imported relationship analysis does not modify transforms.
9. A plausible imported relationship becomes an imported candidate, not automatically verified.
10. A grossly separated relationship requests alignment.
11. Manual session reset and cancel restore exact starting matrices.
12. Manual candidate capture preserves scale and rejects invalid transforms.
13. Right-bite registration succeeds on a suitable fixture.
14. Left-bite registration succeeds on a suitable fixture.
15. Both-bite registration succeeds on a suitable fixture.
16. Insufficient overlap fails safely without leaving partial transforms.
17. Direct upper-to-lower ICP is not used.
18. The upper jaw remains fixed throughout automatic registration.
19. Automatic registration changes transforms only, not mesh topology or vertex coordinates.
20. Registration metrics and warnings are displayed.
21. Right-versus-left inconsistency is reported.
22. Candidate application does not automatically verify Step 2.
23. Explicit review and approval are required.
24. Approval sets `step_2_valid = true` and status to `VERIFIED`.
25. Bite objects are preserved and hidden after approval.
26. Scan replacement or material transform changes invalidate approval.
27. Save, close, and reopen preserve the verified result.
28. Repeated enable, disable, and reload cycles leave no duplicate classes, properties, or handlers.
29. Verification results are recorded in `VERIFICATION.md`.

## Assumptions and Constraints

- Scanner exports may already contain a useful jaw relationship.
- Automatic refinement requires reasonable initial overlap.
- Arbitrarily separated scans require manual coarse positioning before refinement.
- Dental bite scans may contain noise, soft tissue, unmatched geometry, and floating fragments.
- Right and left bite scans may disagree.
- Open boundaries are expected and are not automatically invalid.
- Low geometric error does not prove clinical correctness.
- Bilateral bite information is preferred when available, but the workflow must support unilateral registration.

## References

- Blender KDTree API: <https://docs.blender.org/api/5.0/mathutils.kdtree.html>
- Blender BVHTree API: <https://docs.blender.org/api/5.0/mathutils.bvhtree.html>
- Blender object world matrices: <https://docs.blender.org/api/5.0/bpy.types.Object.html>
- In vivo precision of digital static interocclusal registration: <https://pubmed.ncbi.nlm.nih.gov/36456986/>
- Clinical accuracy and reproducibility of virtual interocclusal records: <https://pubmed.ncbi.nlm.nih.gov/32014284/>
- Bilateral versus complete-arch interocclusal registration scans: <https://pubmed.ncbi.nlm.nih.gov/36813588/>

## Completion Rule

This document remains `Proposed` until the PRD, plan, tasks, decisions, and verification procedure are reviewed and approved. Implementation must not begin before those documents agree on scope and terminology.
