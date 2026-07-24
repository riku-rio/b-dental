# Product Requirements Document: v0.0.5

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.5
- **Status:** Approved for Implementation
- **Target branch:** `feat/v0.0.5-preparation-analysis-insertion-axis`
- **Target merge branch:** `main`
- **Workflow stage:** Step 4 — Preparation Analysis & Insertion Axis

## Product Overview

B-Dental v0.0.5 introduces restoration-specific preparation analysis after Step 3 has produced approved manual margins and, when available, reviewed antagonist regions.

Each restoration receives one persistent insertion-axis definition and one non-destructive undercut-analysis result. The workflow remains user-controlled: automatic calculations provide engineering candidates and visual aids, but they do not determine clinical correctness.

## Product Goal

Produce a persistent Step 4 contract that later crown-bottom and cement-gap stages can consume safely. Each restoration must provide:

1. One finite normalized insertion axis stored in preparation-scan local coordinates.
2. One managed axis interaction/display artifact owned by the restoration.
3. One margin-derived preparation-analysis neighborhood.
4. One current undercut-analysis result associated with the approved margin, target scan, axis, and analysis settings.
5. Independent diagnostics, warnings, review confirmation, and explicit approval.

Step 4 is complete only when at least one restoration exists and every Step 3 restoration has an approved Step 4 result.

## Direction Convention

`insertion_axis_local` is a unit vector in the preparation scan's local coordinate system.

- It points in the seating direction: from the occlusal/source side toward the preparation.
- When captured from the current 3D View, it follows the viewport forward direction toward the preparation.
- The removal direction used by undercut analysis is `-insertion_axis_local`.
- The managed axis object's local positive Z direction represents the stored insertion axis.

The UI must explain this convention and display an unambiguous arrow.

## Accepted Scope

Version v0.0.5 includes:

- Step 4 named **Preparation Analysis & Insertion Axis**.
- Step 4 entry only after aggregate Step 3 approval.
- The existing multiple-restoration collection as the authoritative restoration list.
- Independent Step 4 state and approval for every restoration.
- One target-local insertion axis per restoration.
- Axis candidate creation from the current 3D View.
- A non-authoritative margin-normal axis suggestion.
- Manual axis adjustment through a reversible managed-axis session.
- Exact Reset and Cancel behavior for axis sessions.
- Capture and Apply actions that do not automatically approve the result.
- One managed axis artifact per restoration for interaction and visibility.
- A margin-derived preparation-analysis neighborhood with an adjustable radius.
- Non-destructive, sample-based undercut analysis against the preparation scan.
- A viewport overlay that distinguishes analyzed and undercut samples without modifying the imported mesh.
- Per-restoration metrics including analyzed sample count, undercut sample count, undercut ratio, mean blocking depth, and maximum blocking depth.
- Independent validation, warnings, visual review, warning acknowledgment, and explicit approval.
- Aggregate Step 4 completion derived from every restoration.
- Safe invalidation after material changes to Step 3, target scans, approved margins, antagonist regions, insertion axes, analysis radius, or analysis results.
- Safe v0.0.4 migration with empty Step 4 defaults and no automatically created artifacts.
- Packaging as extension version `0.0.5` after implementation verification.

## Out of Scope

Version v0.0.5 does not include:

- Automatic clinical insertion-axis selection or optimization.
- Automatic tooth identification, tooth segmentation, or preparation die extraction.
- A clinically certified path-of-draw decision.
- Automatic correction of undercuts.
- Survey lines, block-out geometry, wax-up, or scan modification.
- Crown bottom, cement gap, spacer parameters, minimum thickness, or internal relief.
- Crown anatomy, tooth library selection, proximal contacts, occlusal contacts, or antagonist collision adjustment.
- Bridges, implants, abutments, dentures, orthodontic appliances, or other new restoration types.
- Export or manufacturing output.
- Third-party Python dependencies.
- Destructive changes to imported scan meshes, transforms, coordinates, topology, materials, or color attributes.
- Production Step 5 behavior.

## Workflow Preconditions

Entering Step 4 requires:

- An initialized case.
- Valid Step 1.
- Completed and approved Step 2.
- Aggregate Step 3 status `VERIFIED` and `step_3_valid = true`.
- At least one restoration.
- Every restoration approved with a valid managed margin.

Entering Step 4 must not:

- Change scan transforms, mesh coordinates, topology, materials, or object ownership.
- Change margins or antagonist regions.
- Create an axis candidate automatically.
- Approve any restoration automatically.

## Restoration Step 4 State

Each restoration stores:

- `step_4_status`
- `step_4_valid`
- `insertion_axis_local`
- `axis_source`
- `axis_object`
- axis-session state and snapshots
- `analysis_radius`
- analysis sample and undercut metrics
- analysis summary, errors, and warnings
- review and warning confirmations
- approved axis, analysis, target, margin, antagonist, settings, and upstream signatures

## Status Model

Per-restoration Step 4 statuses:

- `READY_FOR_AXIS`
- `AXIS_EDITING`
- `AXIS_CANDIDATE`
- `ANALYZED`
- `VERIFIED`
- `UPSTREAM_INVALID`
- `ERROR`

Aggregate Step 4 statuses:

- `NOT_STARTED`
- `READY_FOR_AXIS`
- `AXIS_EDITING`
- `AXIS_CANDIDATE`
- `ANALYZED`
- `VERIFIED`
- `UPSTREAM_INVALID`
- `ERROR`

Aggregate rules:

- Any open axis session: `AXIS_EDITING`, invalid.
- Every restoration verified and Step 4 valid: `VERIFIED`, valid.
- Invalid Step 3: `UPSTREAM_INVALID`, invalid.
- Otherwise aggregate status follows the active restoration and remains invalid.

## Insertion Axis Candidate Methods

### Set From Current View

This is the primary MVP workflow.

The user positions the 3D View so they are looking toward the preparation along the intended seating direction, then selects **Set From Current View**. The viewport direction is transformed into preparation-scan local coordinates, normalized, stored as a candidate, and displayed using the managed axis artifact and overlay.

### Suggest From Margin

The workflow may calculate an engineering starting direction from the ordered approved margin points using a polygon-normal or equivalent standard-library calculation.

Because a closed margin normal has two possible signs, the suggestion chooses the sign closest to the current viewport forward direction. This is only a starting candidate and requires visual review.

### Manual Axis Editing

The user may start a reversible axis-edit session and rotate the managed axis object with Blender transform controls. Capture converts the managed object's local positive Z direction into the candidate `insertion_axis_local` vector.

## Managed Axis Artifact

Each restoration owns one B-Dental-managed axis object:

- Parent: preparation scan.
- Coordinates: target-local.
- Origin: margin-derived analysis center.
- Orientation: local positive Z aligned to `insertion_axis_local`.
- Display: clearly visible arrow or equivalent managed viewport representation.
- Rendering: disabled.
- Ownership metadata: restoration ID, target arch, FDI tooth, artifact type, and schema version.

The axis artifact is an interaction and display object. The stored normalized vector is authoritative.

## Reversible Axis Session

Starting an axis session snapshots:

- Whether an axis existed.
- Exact candidate and approved vectors.
- Axis source.
- Managed axis transform.
- Analysis settings and result state.
- Status, validity, review, warnings, summaries, and approval signatures.

Session behavior:

- Reset restores the exact session-start axis while keeping the session active.
- Cancel restores the exact session-start Step 4 state and closes the session.
- Capture stores the current axis orientation as a candidate.
- Apply ends the session, preserves the candidate, clears stale analysis, and does not approve Step 4.
- Switching restorations and leaving Step 4 are blocked while a session is unresolved.

## Preparation Analysis Neighborhood

The MVP does not segment the preparation tooth.

Instead, analysis operates on a margin-derived neighborhood:

- Center: arithmetic mean of approved target-local margin points, projected to the target surface when required.
- Default radius: maximum center-to-margin distance multiplied by an engineering expansion factor.
- Supported radius: clamped to an implementation-defined safe range, initially planned as `2 mm` to `15 mm`.
- User control: radius may be adjusted before analysis.
- Sample source: evaluated target-mesh surface samples whose centers fall inside the neighborhood.

Changing the radius invalidates the current analysis and prior Step 4 approval.

## Undercut Analysis

Undercut analysis is an engineering approximation tied to the active insertion axis.

For each deterministic target-surface sample inside the analysis neighborhood:

1. Resolve its target-local position.
2. Ignore self-intersection using a small scale-aware epsilon.
3. Test whether movement along the removal direction is blocked by another target surface.
4. Record blocking depth when a valid obstruction is found.
5. Classify the sample as clear or undercut.

The implementation must:

- Use deterministic sampling.
- Avoid modifying the imported target mesh.
- Avoid third-party dependencies.
- Bound sample count and computation time.
- Store reproducible metrics.
- Display results through a managed GPU overlay or another non-destructive viewport representation.

## Analysis Metrics

Store per restoration:

- Analyzed sample count.
- Undercut sample count.
- Undercut ratio.
- Mean blocking depth.
- Maximum blocking depth.
- Analysis radius.
- Axis source.
- Analysis duration when practical.

Metrics are engineering aids and do not establish clinical acceptability.

## Validation

Blocking errors include:

- Invalid upstream Step 3 state.
- Missing or changed target scan.
- Missing, changed, or unapproved margin.
- Missing or incorrectly owned managed axis artifact when required.
- Missing insertion-axis candidate.
- Non-finite or zero-length insertion-axis vector.
- Axis vector that cannot be normalized safely.
- Validation during an active axis session.
- Missing or stale undercut analysis.
- Invalid analysis radius.
- No usable samples in the analysis neighborhood.
- Analysis signatures that do not match the current target, margin, axis, settings, or upstream state.

Engineering warnings include:

- Very low analysis sample count.
- Axis substantially tilted from the margin-normal suggestion.
- High undercut sample ratio.
- Large maximum blocking depth.
- Analysis neighborhood near its supported minimum or maximum.
- Results that may include adjacent anatomy because segmentation is outside scope.

Thresholds must be documented in code and verification records and must be presented as engineering thresholds, not clinical rules.

## Approval

Approval is independent for each restoration and requires:

- No blocking errors.
- A fresh analysis matching the current axis and dependencies.
- Explicit visual review of the axis and undercut overlay.
- Warning acknowledgment when warnings exist.
- A fresh validation pass.

Approval stores the axis vector, metrics, settings, and dependency signatures and sets that restoration's Step 4 state to `VERIFIED` and valid.

Aggregate `step_4_valid` becomes true only after every restoration is independently approved.

## Invalidation

- Any Step 1, Step 2, or Step 3 invalidation clears aggregate Step 4 validity and invalidates every Step 4 approval.
- Margin edits invalidate the owning restoration's axis analysis and approval.
- Target-scan replacement invalidates dependent Step 4 state and removes unsafe managed artifacts.
- Antagonist-region changes invalidate Step 3 and therefore Step 4 upstream state.
- Axis changes clear analysis results and approval for the owning restoration.
- Analysis-radius changes clear analysis results and approval for the owning restoration.
- Removing a restoration removes only its Step 4 managed artifacts.
- Case reset removes all B-Dental-managed Step 4 artifacts while preserving unrelated scene content.

## Migration

### v0.0.4

Existing v0.0.4 files open with:

- Safe default Step 4 status.
- No axis candidate.
- No analysis result.
- No managed Step 4 artifacts created automatically.
- Existing Step 1, Step 2, Step 3, margins, and antagonist regions preserved.

### In-Branch v0.0.5 Development Builds

If the Step 4 schema changes during implementation, migration must be explicit, one-time, narrowly scoped, and documented before release acceptance.

## User Interface Requirements

The Step 4 sidebar must provide:

- Step and aggregate status.
- Restoration list and approved count.
- Active restoration, target arch, and FDI tooth.
- Focus preparation and focus axis actions.
- **Set From Current View**.
- **Suggest From Margin**.
- Start, Reset, Cancel, Capture, and Apply axis-session controls.
- Axis source and normalized vector summary.
- Analysis-radius control.
- **Run Undercut Analysis**.
- Show, hide, and clear analysis overlay.
- Stored metrics.
- Errors, warnings, and engineering disclaimers.
- Review confirmation, warning acknowledgment, and explicit approval.
- Safe return to Step 3.

The UI must remain usable at normal Blender Sidebar width.

## Acceptance Criteria

Version v0.0.5 is acceptable only when:

1. v0.0.4 files migrate safely with empty Step 4 defaults.
2. Step 4 is inaccessible until Step 3 is fully approved.
3. Every restoration has independent Step 4 state.
4. Current-view axis capture is deterministic and target-local.
5. Margin-normal suggestion produces a finite candidate and remains explicitly non-authoritative.
6. Manual axis editing is reversible.
7. Axis artifacts are owned, persistent, recoverable, and safely removable.
8. Analysis uses the current approved margin, target, axis, and settings.
9. Undercut analysis is deterministic, bounded, and non-destructive.
10. Overlay visualization does not modify imported scan data.
11. Axis and analysis edits invalidate only the owning restoration when upstream state remains valid.
12. Aggregate Step 4 validity requires every restoration to be approved.
13. Step 1, Step 2, and Step 3 remain regression-free.
14. Imported scan transforms, coordinates, topology, materials, and unrelated objects remain unchanged.
15. Manifest validation, package build, installation, lifecycle, migration, regression, and the complete Step 4 scenario matrix pass locally.
16. Actual implementation results and deviations are recorded before acceptance.

## Current Status

The v0.0.5 requirements are approved for implementation. Production Step 4 code has not started, and all implementation and verification work remains pending.