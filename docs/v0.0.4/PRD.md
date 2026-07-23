# Product Requirements Document: v0.0.4

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.4
- **Status:** Proposed
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Target merge branch:** `main`
- **Workflow stage:** Step 3 — Restoration Setup & Manual Margin Definition

## Product Overview

B-Dental `v0.0.4` introduces the first restoration-specific workflow stage after scan import and occlusion verification.

The version allows the user to define one active single-unit anatomical crown restoration, select its preparation arch and permanent target tooth, draw a manual closed margin on the preparation scan, review engineering diagnostics, and explicitly approve the margin.

The margin is a B-Dental-managed curve artifact. Drawing and editing the margin must not modify imported scan mesh coordinates or topology. The workflow provides reproducible technical checks and state management, but it does not identify a clinically correct margin automatically and does not replace professional judgment.

## Product Goal

Provide the smallest safe and verifiable foundation for later crown-design stages by producing:

1. A persistent restoration identity.
2. A persistent target arch and target tooth.
3. A closed manual margin associated with the correct preparation scan.
4. A reviewed and explicitly approved Step 3 result.

## Accepted Scope

Version `v0.0.4` includes:

- A third workflow step named **Restoration Setup & Manual Margin Definition**.
- Migration-safe Step 3 defaults for scenes saved with v0.0.3.
- One active restoration per B-Dental case.
- One supported restoration type: `ANATOMICAL_CROWN`.
- Permanent dentition only.
- Canonical FDI two-digit tooth identifiers.
- Target-arch selection constrained by imported scan availability.
- Target-tooth selection constrained by the selected arch.
- A stable restoration identifier stored with the workflow state and managed artifacts.
- A B-Dental-managed restoration collection.
- A B-Dental-managed manual-margin curve.
- Target-only surface picking on the preparation scan.
- Ordered surface-point placement.
- Closed cyclic margin creation.
- Reversible margin sessions with start, reset, cancel, capture, and apply behavior.
- Editing support for the active margin candidate.
- Reprojection of edited points to the target preparation surface.
- Technical margin validation and diagnostics.
- Explicit warning acknowledgment when warnings exist.
- Explicit visual-review confirmation.
- Explicit approval before `step_3_valid` can become true.
- Persistent restoration setup, margin reference, summaries, diagnostics, and approved point snapshot.
- Safe invalidation after upstream workflow changes, restoration changes, target-scan changes, or material margin edits.
- Updated Step 1, Step 2, and Step 3 navigation and progress text.
- Blender Extension validation, package build, installation, lifecycle, migration, regression, and scenario verification.

## Out of Scope

Version `v0.0.4` does not include:

- Automatic, assisted, AI, or machine-learning margin detection.
- More than one active restoration.
- Bridges or multi-unit restorations.
- Inlays, onlays, veneers, copings, pontics, implants, abutments, splints, dentures, or orthodontic appliances.
- Primary dentition.
- Universal, Palmer, or user-configurable tooth notation.
- Preparation segmentation or die extraction.
- Scan cleanup, trimming, smoothing, remeshing, decimation, hole filling, or topology repair.
- Automatic margin correction.
- Insertion-axis selection.
- Undercut analysis.
- Crown-bottom generation.
- Cement-gap, spacer, offset, or internal-fit parameters.
- Tooth-library placement.
- Crown proposal or freeform crown design.
- Proximal-contact or occlusal-contact adjustment.
- Dynamic occlusion or articulator simulation.
- Manufacturing validation or STL export.
- Clinical certification, diagnosis, treatment decisions, or claims of margin correctness.
- Third-party Python dependencies.
- Production Step 4 behavior.

## Workflow Preconditions

Step 3 requires:

- An initialized B-Dental case.
- A valid Step 1 result.
- A completed Step 2 result.
- For Single Arch cases, Step 2 must be explicitly completed as not applicable.
- For Dual Arch and Full Scan Set cases, Step 2 must be explicitly verified.
- A live preparation scan with valid B-Dental ownership and role metadata.

Entering Step 3 must not:

- Change scan transforms.
- Change scan mesh coordinates.
- Change scan topology.
- Create a margin until the user explicitly configures a restoration and starts a margin session.
- Set `step_3_valid = true`.

## Restoration Model

### Supported Restoration

The only supported restoration type is:

- `ANATOMICAL_CROWN`

The restoration type is displayed in the UI but is not user-switchable in v0.0.4.

### Active Restoration Limit

- A case contains zero or one active restoration.
- Starting a restoration creates a stable restoration identifier.
- Resetting or replacing the active restoration requires explicit confirmation when a managed margin exists.
- Multi-restoration data structures may be introduced later, but v0.0.4 must not expose incomplete multi-unit behavior.

### Target Arch

Supported values:

- `UPPER_JAW`
- `LOWER_JAW`

Rules:

- The selected target arch must exist as a valid managed scan.
- Single Arch cases automatically use their imported arch.
- Dual Arch and Full Scan Set cases allow Upper Jaw or Lower Jaw selection.
- Changing the target arch invalidates and removes only the managed margin belonging to the active restoration after explicit confirmation.

### Target Tooth

B-Dental uses canonical permanent FDI identifiers.

Upper arch:

- `11` through `18`
- `21` through `28`

Lower arch:

- `31` through `38`
- `41` through `48`

Rules:

- The selected tooth must belong to the selected target arch.
- A target tooth is required before a margin session can begin.
- Changing the target tooth invalidates the existing margin approval.
- If a managed margin already exists, changing the target tooth requires explicit confirmation and removes only that restoration's managed margin.

## Step 3 State Model

Step 3 statuses:

- `NOT_STARTED`
- `SETUP_REQUIRED`
- `READY_FOR_MARGIN`
- `DRAWING`
- `CANDIDATE`
- `VERIFIED`
- `UPSTREAM_INVALID`
- `ERROR`

Required state includes:

- `step_3_status`
- `step_3_valid`
- `restoration_id`
- `restoration_type`
- `target_arch`
- `target_tooth_fdi`
- `margin_object`
- `margin_session_active`
- `margin_candidate_closed`
- `margin_warning_acknowledged`
- `margin_review_confirmed`
- `step_3_summary`
- `step_3_errors`
- `step_3_warnings`
- `margin_point_count`
- `margin_path_length`
- `margin_mean_surface_distance`
- `margin_max_surface_distance`
- `margin_session_points`
- `approved_margin_points`
- `approved_target_signature`

`step_3_valid` is workflow completion state. It is not inferred from curve creation, curve closure, operator success, point count, surface distance, or visual plausibility.

## Managed Artifact Model

### Collection

Version `v0.0.4` creates or reuses:

- `B-Dental Restorations`

The collection contains only B-Dental-managed restoration artifacts.

### Margin Object

The manual margin is represented as:

- One Blender Curve object.
- One 3D `POLY` spline.
- Ordered points.
- Cyclic closure after candidate capture.
- A visible bevel suitable for viewport review.
- No fill geometry required for approval.

Required metadata:

- `bdental_managed = true`
- `bdental_artifact_type = "MARGIN"`
- `bdental_restoration_id`
- `bdental_target_role`
- `bdental_target_tooth_fdi`
- `bdental_schema_version`

The margin curve must be associated with the preparation scan so that its local coordinates remain aligned with that scan. The implementation must not modify the scan's mesh data or use the scan as writable geometry.

## Manual Margin Session

### Starting a Session

Starting a session must:

- Revalidate Step 1, Step 2, restoration setup, and the target scan.
- Snapshot any existing candidate or approved margin points.
- Create or reuse only the active restoration's managed margin object.
- Make the target preparation scan available for focused review.
- Set `margin_session_active = true`.
- Set `step_3_status = DRAWING`.
- Preserve all scan transforms and mesh data.

### Drawing Interaction

The drawing operator must:

- Use a modal 3D Viewport interaction.
- Ray-cast only against the selected target preparation scan.
- Ignore hits on the antagonist, bite scans, margin curve, and unrelated objects.
- Add one ordered local-space point for each accepted surface click.
- Display the open candidate path while drawing.
- Allow removal of the most recently placed point.
- Allow explicit completion of the open path.
- Reject completion when the minimum point requirement is not met.
- Allow cancellation without leaving a partial approved result.

The UI and status bar must document the active controls. The final key mapping may follow Blender conventions, but it must include explicit actions equivalent to:

- Add point.
- Remove last point.
- Finish and close.
- Cancel drawing.

### Candidate Closure

Capturing the candidate must:

- Require at least six unique finite points.
- Convert the spline to cyclic closure.
- Preserve ordered target-local coordinates.
- Set `margin_candidate_closed = true`.
- Set `step_3_status = CANDIDATE`.
- Keep `step_3_valid = false`.

### Editing

The user must be able to:

- Select the managed margin candidate.
- Enter a supported editing path.
- Move existing points.
- Delete points while preserving the minimum-count rule before candidate capture.
- Add points to the active spline.
- Reproject edited points to the target preparation surface.
- Return to object mode and recapture the candidate.

Unsupported spline-type changes, additional splines, non-cyclic final geometry, or replacement with unrelated objects must be detected during validation.

### Reset

Reset must:

- Restore the exact session-start point snapshot.
- Preserve the active session.
- Preserve the target scan and all imported objects.
- Restore the previous approval snapshot when the session began from an approved margin.

### Cancel

Cancel must:

- Restore the exact session-start point snapshot.
- Remove the draft margin object if no margin existed at session start.
- Restore the prior managed margin if one existed.
- Restore the prior Step 3 status and validity.
- Close the session.

### Apply Candidate

Apply Candidate must:

- Keep the current closed candidate points.
- Close the active session.
- Set `step_3_status = CANDIDATE`.
- Clear previous review confirmation and warning acknowledgment.
- Invalidate any previous approval.
- Keep `step_3_valid = false`.

Applying a candidate is not approval.

## Margin Validation

Validation produces separate blocking errors and non-blocking warnings.

### Blocking Errors

Approval must be blocked when:

- Upstream workflow preconditions are invalid.
- The restoration setup is incomplete.
- The target scan is missing, stale, or has invalid metadata.
- The margin object is missing or not B-Dental-managed for the active restoration.
- The margin contains zero or multiple splines.
- The spline is not a 3D `POLY` spline.
- The spline is not cyclic.
- Fewer than six unique points exist.
- Any point coordinate is non-finite.
- Consecutive points collapse within the implementation epsilon.
- The total path length is zero or below a documented engineering minimum.
- Any point is more than `1.0 mm` from the evaluated target surface.
- The margin metadata does not match the active restoration, target arch, or target tooth.
- The target scan mesh identity no longer matches the active restoration reference.
- An active margin session remains open.

### Non-Blocking Warnings

Warnings include:

- Fewer than twelve points.
- Any point more than `0.25 mm` from the evaluated target surface.
- Large spacing differences between consecutive points.
- Approximate non-adjacent segment proximity that may indicate a self-crossing or folded path.
- Unusually short or unusually long path length relative to the target scan dimensions.
- The target scan transform changed after the previous approval snapshot.
- The upstream occlusion was re-approved after the margin was created.

Thresholds are engineering workflow safeguards, not clinical standards. They must be defined as named constants and covered by tests or documented manual scenarios.

### Reported Diagnostics

When available, the UI reports:

- Point count.
- Path length in millimeters.
- Mean point-to-surface distance in millimeters.
- Maximum point-to-surface distance in millimeters.
- Warning count.
- Blocking-error count.

## Approval Requirements

Before approval, B-Dental must:

- Revalidate all Step 3 preconditions.
- Validate restoration and margin metadata.
- Validate the managed curve structure.
- Validate finite point coordinates.
- Validate closure and minimum point count.
- Calculate available engineering diagnostics.
- Separate blocking errors from warnings.
- Require warning acknowledgment when warnings exist.
- Require explicit visual-review confirmation.

Approval must:

- Set `step_3_status = VERIFIED`.
- Set `step_3_valid = true`.
- Store an approved local-space point snapshot.
- Store a target-scan signature.
- Store diagnostics and a verification summary.
- Keep the managed margin visible by default.
- Preserve imported scans and scan mesh data.
- Make no claim of clinical correctness.

## Invalidation Rules

### Case Reset

Resetting the B-Dental case must:

- Clear Step 1, Step 2, and Step 3 state.
- Remove only B-Dental-managed scan and restoration artifacts covered by the confirmed reset.
- Leave unrelated scene objects unchanged.

### Step 1 Invalidation

When Step 1 becomes invalid:

- Step 2 and Step 3 become invalid.
- `current_step` returns to Step 1.
- The active margin session is cancelled safely.
- A margin tied to a replaced or removed target preparation scan is removed.
- A margin tied to an unchanged target preparation scan may remain preserved as an unapproved artifact.

### Step 2 Invalidation

When Step 2 becomes invalid:

- Step 3 becomes `UPSTREAM_INVALID`.
- `step_3_valid` becomes false.
- The restoration setup and margin may remain preserved when the target preparation scan still exists.
- The user must re-complete Step 2 and rerun Step 3 validation before approval.

### Restoration Changes

Changing target arch or target tooth:

- Requires explicit confirmation when a managed margin exists.
- Removes only the active restoration's managed margin after confirmation.
- Clears Step 3 diagnostics, snapshots, and approval.
- Returns Step 3 to `READY_FOR_MARGIN` when setup remains complete.

### Margin Changes

A material change to approved margin points:

- Sets `step_3_valid = false`.
- Clears review confirmation and warning acknowledgment.
- Sets `step_3_status = CANDIDATE` when the curve remains structurally usable.
- Sets `step_3_status = ERROR` when the curve becomes structurally invalid.

## Navigation and User Interface

The sidebar must display:

- `Step 1 of 3` during scan import.
- `Step 2 of 3` during occlusion registration.
- `Step 3 of 3` during restoration setup and margin definition.

Step 3 UI sections:

1. Upstream completion summary.
2. Restoration Setup.
3. Target Preparation Scan.
4. Manual Margin Session.
5. Candidate Editing and Reprojection.
6. Validation Results.
7. Diagnostics.
8. Review and Approval.
9. Managed-object visibility and focus controls.
10. Safe navigation back to Step 2.

Navigation rules:

- Entering Step 3 requires completed Step 2.
- Returning to Step 2 must not silently discard an active session.
- An active session must be reset, cancelled, or applied before leaving Step 3.
- Returning to Step 2 preserves an applied or approved margin unless an upstream change invalidates it.

## Implementation Structure

Expected structure:

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

Expected responsibilities:

- `restoration_utils.py`: restoration identity, tooth and arch helpers, managed artifact metadata, collection and object resolution.
- `margin_geometry.py`: target-only ray casting, local-space point conversion, curve creation, point serialization, reprojection, and diagnostics.
- `margin_validation.py`: Step 3 preconditions, managed-curve validation, surface-distance checks, path diagnostics, and approval readiness.
- `step_three_session.py`: exact point snapshots, restoration of existing margins, reset, cancel, apply, and rollback helpers.
- `step_three_operators.py`: restoration setup, drawing, editing support, reprojection, validation, approval, and navigation operators.
- `properties.py`: Step 3 persistent state, migration-safe defaults, dependency invalidation, and change monitoring.
- `scene_utils.py`: generalized managed-artifact cleanup without removing unrelated objects.
- `ui.py`: three-step navigation and context-sensitive Step 3 controls.

The final implementation may adjust module boundaries when the responsibility split remains explicit and documented.

## Acceptance Criteria

Version `v0.0.4` is acceptable only when:

1. Existing v0.0.3 files open with safe Step 3 defaults.
2. Registration and extension enablement do not change scene objects.
3. Step 1 and Step 2 regression scenarios still pass.
4. Step 3 cannot open before Step 2 completion.
5. Single Arch uses its imported arch automatically.
6. Dual Arch and Full Scan Set allow only available target arches.
7. Only permanent FDI teeth belonging to the selected arch can be chosen.
8. Only one active anatomical-crown restoration is exposed.
9. Starting a margin session preserves all scan transforms and mesh data.
10. Surface clicks resolve only against the target preparation scan.
11. Drawing creates ordered target-local points.
12. Candidate capture requires a closed curve with at least six unique points.
13. Reset restores exact session-start points.
14. Cancel restores the previous margin or removes a new draft safely.
15. Apply Candidate does not approve Step 3.
16. Edited points can be reprojected to the target surface.
17. Invalid or unrelated curve structures are rejected.
18. Blocking errors and warnings are separated.
19. Diagnostics are displayed at normal sidebar width.
20. Warnings require acknowledgment.
21. Approval requires explicit visual-review confirmation.
22. `step_3_valid` becomes true only after explicit approval.
23. Approval persists after save and reopen.
24. Material margin edits invalidate approval.
25. Target-scan replacement removes only the dependent managed margin.
26. Upstream Step 2 invalidation preserves usable margin geometry but invalidates Step 3 approval.
27. Case reset removes only confirmed B-Dental-managed artifacts.
28. No imported scan mesh coordinates or topology are changed.
29. Repeated enable, disable, and reload cycles remain clean.
30. Manifest validation, `0.0.4` package build, inspection, installation, and local verification pass.
31. Documentation records actual implementation results and deviations before acceptance.

## Documentation Status Rule

This PRD remains **Proposed** until the complete v0.0.4 documentation set is reviewed and accepted. Implementation must not silently expand the accepted scope. Any material change requires updating this PRD, the related decision record, plan, tasks, and verification scenarios before the version is marked complete.
