# Product Requirements Document: v0.0.4

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.4
- **Status:** In Progress
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Target merge branch:** `main`
- **Workflow stage:** Step 3 — Multiple Restoration Setup & Manual Margin Definition

## Product Overview

B-Dental v0.0.4 introduces restoration-specific case planning after scan import and occlusion verification.

A case may contain multiple independent single-unit anatomical crown restorations. Each restoration identifies one preparation arch and one permanent FDI tooth, owns one managed manual-margin curve, and has independent session, validation, diagnostics, and approval state.

The implementation does not identify a clinically correct margin automatically. All metrics are engineering workflow aids and every margin requires explicit visual review and approval.

## Product Goal

Produce a persistent restoration collection that later design stages can consume safely. Each restoration must provide:

1. Stable restoration identity.
2. Target preparation arch and permanent FDI tooth.
3. One closed target-local manual margin.
4. Independent validation diagnostics.
5. Independent explicit approval.

Step 3 is complete only when at least one restoration exists and every configured restoration is approved.

## Accepted Scope

Version v0.0.4 includes:

- Step 3 named **Multiple Restorations & Manual Margins**.
- Multiple restorations in one B-Dental case.
- Mixed upper- and lower-arch restorations when both scans exist.
- One supported restoration type: `ANATOMICAL_CROWN`.
- Permanent dentition using canonical two-digit FDI identifiers.
- One restoration per unique arch and FDI tooth combination.
- Stable restoration IDs.
- Active-restoration selection for editing.
- One B-Dental-managed margin Curve per restoration.
- Restoration list, add, select, and remove controls.
- Independent reversible margin sessions.
- Target-only surface picking.
- Ordered target-local points and cyclic closure.
- Editing and target-surface reprojection.
- Independent errors, warnings, diagnostics, review confirmation, and warning acknowledgment.
- Independent explicit margin approval.
- Aggregate Step 3 completion derived from all restorations.
- Safe in-branch migration from the earlier single-restoration v0.0.4 state.
- Safe v0.0.3 defaults with an empty restoration collection.
- Upstream invalidation across all restoration approvals while preserving usable geometry when safe.
- Case reset that removes only B-Dental-managed scans and restoration artifacts.

## Out of Scope

Version v0.0.4 does not include:

- Automatic, assisted, AI, or machine-learning margin detection.
- Bridges or linked multi-unit prostheses.
- Inlays, onlays, veneers, copings, pontics, implants, abutments, splints, dentures, or orthodontic appliances.
- Primary dentition.
- Universal, Palmer, or configurable notation.
- Preparation segmentation or die extraction.
- Scan cleanup, trimming, smoothing, remeshing, decimation, hole filling, or topology repair.
- Insertion-axis selection or undercut analysis.
- Crown bottom, cement gap, tooth library, crown proposal, contact adjustment, or export.
- Clinical certification, diagnosis, or treatment decisions.
- Third-party Python dependencies.
- Production Step 4 behavior.

## Workflow Preconditions

Step 3 requires:

- An initialized case.
- Valid Step 1.
- Completed Step 2.
- Single Arch explicitly completed as not applicable, or Dual/Full Scan Set explicitly verified.

Entering Step 3 must not change scan transforms, mesh coordinates, or topology and must not create a restoration automatically.

## Restoration Collection Model

### Collection Rules

- A case contains zero or more restorations.
- Only one restoration is active in the UI at a time.
- The active index is persistent.
- Switching is blocked while the active restoration has an open margin session.
- Adding a restoration does not modify existing restorations or margins.
- Removing a restoration requires confirmation and removes only that restoration's managed margin.
- The same arch and FDI tooth combination is unique within the case.

### Restoration State

Each restoration stores:

- `restoration_id`
- `restoration_type`
- `target_arch`
- `target_tooth_fdi`
- `status`
- `valid`
- `margin_object`
- session and candidate state
- review and warning confirmation
- summaries, errors, and warnings
- point count, path length, and surface-distance diagnostics
- session snapshots
- approved point, target, transform, and upstream signatures

### Supported Targets

Target arches:

- `UPPER_JAW`
- `LOWER_JAW`

Permanent FDI teeth:

- Upper: `11`–`18`, `21`–`28`
- Lower: `31`–`38`, `41`–`48`

Single Arch cases automatically constrain new restorations to the imported arch. Dual Arch and Full Scan Set cases may contain restorations on both arches.

## Status Model

Per-restoration statuses:

- `READY_FOR_MARGIN`
- `DRAWING`
- `CANDIDATE`
- `VERIFIED`
- `UPSTREAM_INVALID`
- `ERROR`

Aggregate Step 3 statuses:

- `NOT_STARTED`
- `SETUP_REQUIRED`
- `READY_FOR_MARGIN`
- `DRAWING`
- `CANDIDATE`
- `VERIFIED`
- `UPSTREAM_INVALID`
- `ERROR`

Aggregate rules:

- No restorations: `SETUP_REQUIRED`, invalid.
- Any open session: `DRAWING`, invalid.
- Every restoration verified and valid: `VERIFIED`, valid.
- Otherwise the aggregate status follows the active restoration and remains invalid.

## Managed Margin Artifact

Each restoration owns one Curve object:

- One 3D `POLY` spline.
- Ordered points.
- Cyclic after candidate capture.
- Visible bevel.
- Parent and local coordinates tied to the target preparation scan.

Required metadata:

- `bdental_managed = true`
- `bdental_artifact_type = "MARGIN"`
- `bdental_restoration_id`
- `bdental_target_role`
- `bdental_target_tooth_fdi`
- `bdental_schema_version`

Margin lookup and deletion must use restoration ownership metadata. Unrelated objects and other restorations must remain untouched.

## Manual Margin Session

A session applies only to the active restoration.

Starting a session must revalidate upstream state and restoration setup, snapshot the active margin and approval state, and preserve all scans and other restorations.

Drawing controls provide actions equivalent to:

- Add point.
- Remove last point.
- Finish and close.
- Cancel.

Candidate capture requires at least six unique finite points and creates a cyclic curve. Applying a candidate ends the session but does not approve it.

Reset and Cancel restore only the active restoration's exact session-start state. They must not affect any other margin.

## Editing and Reprojection

The active managed margin may be edited using Blender Curve edit mode. The workflow must:

- Reject multiple splines or unsupported spline types.
- Reproject only to the restoration's target scan.
- Preserve ordered points where practical.
- Invalidate only that restoration's prior approval after material edits.

## Validation

Blocking errors include:

- Invalid upstream state.
- Missing or duplicate restoration target.
- Missing or changed target scan.
- Missing or incorrectly owned margin.
- Wrong restoration ID, arch, or tooth metadata.
- Wrong object or spline structure.
- Non-cyclic margin.
- Fewer than six unique finite points.
- Collapsed consecutive points.
- Path below the engineering minimum.
- A point more than `1.0 mm` from the target surface.
- Validation during an active session.

Warnings include:

- Fewer than twelve points.
- A point more than `0.25 mm` from the target surface.
- Large spacing variation.
- Possible non-adjacent segment crossing or folding.
- Unusual path length relative to the target scan.

Diagnostics are stored and displayed per restoration.

## Approval

Approval is independent for each restoration and requires:

- No blocking errors.
- Warning acknowledgment when warnings exist.
- Explicit visual-review confirmation.
- A fresh validation pass.

Approval stores the margin points and dependency signatures and sets that restoration to `VERIFIED` and `valid = true`.

Step 3 sets `step_3_valid = true` only when at least one restoration exists and all restorations are verified.

## Invalidation

- Step 1 or Step 2 invalidation clears aggregate Step 3 validity and invalidates every restoration approval.
- Usable restoration setup and margin geometry remain preserved during temporary upstream invalidation when their target scans remain alive.
- Replacing or removing a target scan invalidates or removes only restorations that depend on that scan.
- Material margin edits invalidate only the owning restoration.
- Removing a restoration never removes another restoration's margin.
- Case reset removes all B-Dental-managed restoration artifacts after confirmation.

## Migration

### v0.0.3

Existing files open with an empty restoration collection and safe Step 3 defaults.

### Earlier v0.0.4 Single-Restoration Builds

When legacy single-restoration properties contain a restoration ID, the extension migrates them once into one collection item, preserving the margin pointer, status, diagnostics, session snapshots, and approval snapshots where available.

## Acceptance Criteria

Version v0.0.4 is acceptable only when:

1. v0.0.3 migration is safe.
2. Earlier single-restoration v0.0.4 state migrates to one collection item.
3. Multiple restorations can coexist in one case.
4. Upper and lower restorations can coexist in a dual-arch case.
5. Duplicate target teeth are rejected.
6. Switching restorations preserves each independent state.
7. Switching is blocked during an active session.
8. Every restoration owns a separate managed margin.
9. Drawing, reset, cancel, edit, reprojection, validation, and approval affect only the active restoration.
10. Removing one restoration preserves all others.
11. Aggregate Step 3 validity requires every restoration to be approved.
12. Upstream invalidation invalidates all approvals safely.
13. Imported scan mesh coordinates and topology remain unchanged.
14. Unrelated scene objects remain unchanged.
15. Manifest validation, package build, installation, lifecycle, regression, and the revised verification matrix pass locally.
16. Actual implementation results and deviations are recorded before acceptance.

## Current Status

The multiple-restoration implementation is present on the target branch. Blender package validation and the complete local verification matrix remain pending, so this PRD remains **In Progress**.
