# Product Requirements Document: v0.0.5

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.5
- **Status:** Complete
- **Target branch:** `feat/v0.0.5-preparation-analysis-insertion-axis`
- **Target merge branch:** `main`
- **Workflow stage:** Step 4 — Preparation Analysis & Insertion Axis
- **Merge strategy:** Squash and merge

## Product Overview

B-Dental v0.0.5 adds restoration-specific insertion-axis definition and non-destructive preparation undercut analysis after Step 3 has produced approved restorations, margins, and any required antagonist regions.

Each restoration owns one persistent insertion-axis contract and one current analysis result. Automatic calculations provide engineering candidates, metrics, and visual aids; they do not determine clinical correctness.

## Product Goal

Produce a persistent Step 4 contract that later crown-bottom and cement-gap stages can consume safely. Each restoration provides:

1. One finite normalized insertion axis stored in preparation-scan local coordinates.
2. One managed axis interaction and display artifact owned by the restoration.
3. One margin-derived preparation-analysis neighborhood.
4. One current undercut-analysis result tied to the approved margin, target scan, axis, settings, and upstream state.
5. Independent diagnostics, warnings, review confirmation, warning acknowledgment, and explicit approval.

Step 4 is complete only when at least one restoration exists and every Step 3 restoration has an independently approved Step 4 result.

## Direction Convention

`insertion_axis_local` is a unit vector in the preparation scan's local coordinate system.

- It points in the seating direction from the occlusal/source side toward the preparation.
- Current-view capture follows the 3D View forward direction toward the preparation.
- The removal direction used by undercut analysis is `-insertion_axis_local`.
- The managed axis object's local positive Z direction represents the stored insertion axis.

## Accepted Scope

Version v0.0.5 includes:

- Step 4 entry only after aggregate Step 3 approval.
- Independent Step 4 state and approval for every restoration.
- One authoritative target-local insertion axis per restoration.
- **Set From Current View** as the primary candidate method.
- A non-authoritative **Suggest From Margin** candidate.
- Reversible manual axis sessions with Start, Reset, Cancel, Capture, and Apply.
- One owned, target-parented, non-renderable managed axis object per restoration.
- A margin-derived analysis center and user-adjustable radius from `2 mm` to `15 mm`.
- Deterministic, bounded evaluated-mesh sampling.
- World-space BVH undercut testing using the removal direction opposite the seating axis.
- Per-restoration analyzed count, undercut count, ratio, mean blocking depth, maximum blocking depth, and duration.
- A non-destructive viewport overlay for clear and undercut samples.
- Independent validation, engineering warnings, visual review, warning acknowledgment, and approval.
- Aggregate Step 4 completion derived from every restoration.
- Dependency signatures and safe invalidation after material changes.
- Safe v0.0.4 migration with empty Step 4 defaults and no automatically created Step 4 artifacts.
- Packaging as extension version `0.0.5`.

## Out of Scope

Version v0.0.5 does not include:

- Automatic clinical insertion-axis optimization.
- Automatic tooth identification, segmentation, or preparation die extraction.
- A clinically certified path-of-draw decision.
- Automatic correction or block-out of undercuts.
- Survey lines, wax-up, scan modification, or destructive mesh editing.
- Crown bottom, cement gap, spacer, minimum thickness, or internal relief.
- Crown anatomy, tooth libraries, contact adjustment, or export.
- Bridges, implants, dentures, orthodontic appliances, or new restoration types.
- Third-party Python dependencies.
- Production Step 5 behavior.

## Workflow Preconditions

Entering Step 4 requires:

- An initialized case.
- Valid Step 1.
- Completed and approved Step 2.
- Aggregate Step 3 status `VERIFIED` with `step_3_valid = true`.
- At least one restoration.
- Every restoration approved with a valid managed margin.

Entering Step 4 does not modify scans, margins, antagonist regions, transforms, topology, materials, or ownership, and does not create or approve an axis automatically.

## Persistent State

Each restoration stores:

- `step_4_status` and `step_4_valid`.
- `insertion_axis_local` and `axis_source`.
- Managed-axis pointer and session snapshots.
- Analysis radius, samples, metrics, duration, and current-result state.
- Errors, warnings, summary, review, and warning acknowledgment.
- Approved axis, settings, metrics, and dependency signatures.

Aggregate Step 4 status and validity are derived from the restoration collection.

## Axis Candidate Methods

### Set From Current View

The user looks toward the preparation along the intended seating direction. The viewport forward direction is transformed into preparation-scan local coordinates, normalized, stored as a candidate, and displayed through the managed axis artifact and overlay.

### Suggest From Margin

The approved ordered margin provides a polygon-normal engineering suggestion. Because the sign is ambiguous, the sign closest to the current viewport forward direction is selected. The result remains a candidate requiring review and analysis.

### Manual Axis Editing

A reversible session allows rotation of the managed object using Blender transform controls. Capture converts the object's local positive Z direction to the candidate target-local vector. Apply closes the session, preserves the candidate, clears stale analysis and approval, and never approves Step 4 automatically.

## Managed Axis Artifact

Each restoration owns one managed axis object with:

- Preparation scan as parent.
- Target-local coordinates.
- Margin-derived origin.
- Local positive Z aligned to the stored axis.
- Visible arrow-style display.
- Rendering disabled.
- Restoration ID, target arch, FDI tooth, artifact type, and schema metadata.

The stored normalized vector is authoritative; the object is an interaction and display artifact.

## Preparation Analysis

The analysis neighborhood is derived from the approved margin rather than automatic tooth segmentation.

- Center: arithmetic mean of approved margin points, projected to the target surface when required.
- Default radius: margin extent multiplied by the engineering expansion factor and clamped to `2 mm`–`15 mm`.
- Sampling: deterministic evaluated triangles inside the world-space radius.
- Maximum sample count: bounded by implementation policy.
- Acceleration: evaluated target mesh represented by a world-space BVH.
- Removal direction: opposite the stored seating axis.
- Self-hit handling: scale-aware epsilon offset.
- Output: clear/undercut classification and blocking depth per sample.

The implementation does not modify imported mesh coordinates, topology, materials, color attributes, or transforms.

## Validation and Warnings

Blocking errors include invalid upstream state, missing or changed target or margin, invalid axis ownership, missing or non-finite axis, active session, invalid radius, missing samples, stale analysis, and signature mismatches.

Engineering warnings include low sample count, substantial axis tilt from the margin suggestion, high undercut ratio, large blocking depth, boundary radius, and possible inclusion of adjacent anatomy because segmentation is outside scope.

Engineering thresholds are implementation aids, not clinical rules.

## Approval

Approval is independent for each restoration and requires:

- No blocking errors.
- A fresh analysis matching current dependencies.
- Explicit visual review of the axis and undercut overlay.
- Warning acknowledgment when warnings exist.
- A fresh validation pass.

Approval stores the current axis, source, settings, metrics, and dependency signatures, then sets the restoration to `VERIFIED`. Aggregate `step_4_valid` becomes true only after every restoration is independently verified.

## Invalidation and Cleanup

- Step 1–3 invalidation clears aggregate Step 4 validity.
- Margin changes invalidate only the owning restoration where possible.
- Target replacement invalidates dependent Step 4 state and unsafe artifacts.
- Antagonist-region changes invalidate Step 3 and therefore Step 4 upstream state.
- Axis or radius changes clear current analysis and approval.
- Missing or corrupted managed artifacts invalidate safely.
- Removing a restoration removes only its Step 4 artifacts.
- Case reset removes all B-Dental-managed Step 4 artifacts while preserving unrelated content.

## Migration

Existing v0.0.4 files open with safe empty Step 4 defaults, no candidate, no analysis result, and no automatically created Step 4 artifact. Existing scans, transforms, restorations, margins, antagonist regions, and approvals remain preserved.

## Implementation Corrections

Two defects found during local verification were corrected before acceptance:

1. The manifest tagline exceeded Blender's 64-character limit and was shortened.
2. The initial analysis compared a world-unit radius with target-local mesh coordinates. Evaluated vertices, sample centers, axis direction, and BVH ray casting now use world space; overlay sample locations are converted back to target-local coordinates for persistent display.

The sampling policy version was advanced after this correction so stale development-build results cannot be treated as current.

## Acceptance Criteria

Version v0.0.5 is accepted because:

1. v0.0.4 files migrate safely with empty Step 4 defaults.
2. Step 4 remains inaccessible until Step 3 is fully approved.
3. Every restoration has independent Step 4 state and approval.
4. Current-view capture is deterministic and target-local.
5. Margin suggestion is finite, signed using the view, and non-authoritative.
6. Manual editing is independently reversible.
7. Axis artifacts are owned, persistent, recoverable, and safely removable.
8. Analysis uses the current target, margin, axis, settings, and upstream state.
9. Sampling and undercut analysis are deterministic, bounded, scale-correct, and non-destructive.
10. Overlay visualization does not modify imported scan data.
11. Validation rejects missing, stale, corrupted, or incomplete state.
12. Explicit review and warning acknowledgment are required before approval.
13. Aggregate completion requires every restoration.
14. Step 1, Step 2, and Step 3 remain regression-free.
15. Imported scan geometry, transforms, materials, and unrelated content remain safe.
16. Manifest validation, package build, installation, lifecycle, migration, regression, and the complete Step 4 scenario matrix passed locally.

## Completion Record

The implementation, documentation, packaging, and local verification are complete. Version v0.0.5 is ready for a non-draft pull request and **Squash and merge** into `main`.
