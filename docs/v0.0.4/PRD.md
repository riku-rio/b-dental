# Product Requirements Document: v0.0.4

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.4
- **Status:** Complete
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Target merge branch:** `main`
- **Workflow stage:** Step 3 — Multiple Restorations, Manual Margins & Antagonist Regions

## Product Goal

Produce a persistent, non-destructive restoration collection that later design stages can consume safely. Each restoration provides:

1. Stable restoration identity.
2. Preparation arch and permanent FDI tooth.
3. One closed target-local manual margin.
4. One reviewed antagonist region when an opposing arch is available.
5. Independent validation diagnostics.
6. Independent explicit approval.

Step 3 is complete only when at least one restoration exists and every configured restoration is approved.

## Accepted Scope

Version v0.0.4 includes:

- Multiple independent single-unit `ANATOMICAL_CROWN` restorations.
- Mixed upper- and lower-arch restorations when scans are available.
- Permanent FDI identifiers and duplicate-target rejection.
- One managed 3D `POLY` margin Curve per restoration.
- Target-only surface picking, cyclic closure, editing, and reprojection.
- Visible bevel and always-visible viewport margin overlay.
- Reversible per-restoration margin sessions.
- Per-restoration validation, diagnostics, warnings, review, and approval.
- Automatic or manual antagonist-region definition on the opposing arch.
- Per-restoration antagonist-region ownership, radius, visibility, review, persistence, validation, invalidation, and cleanup.
- Antagonist-region not-applicable behavior for single-arch cases.
- Aggregate completion derived from every restoration.
- Safe v0.0.3 defaults and one-time earlier v0.0.4 migration.
- Safe upstream invalidation and narrowly scoped case reset.

## Out of Scope

- Automatic or AI margin detection.
- Automatic tooth identification or verification that the chosen FDI number matches the drawn tooth.
- Tooth segmentation or preparation die extraction.
- Insertion-axis selection or undercut analysis.
- Crown bottom, cement gap, tooth library, anatomy proposal, contact adjustment, or export.
- Bridges, linked multi-unit prostheses, implants, dentures, orthodontic appliances, or primary dentition.
- Scan cleanup, remeshing, topology repair, or destructive scan editing.
- Clinical diagnosis, certification, or treatment decisions.
- Production Step 4 behavior.

## Workflow Contract

Step 3 requires a valid initialized case and completed Step 2. Entering Step 3 must not modify scan mesh coordinates or topology and must not create a restoration automatically.

A restoration owns its margin and antagonist-region artifacts through stable metadata. Switching is blocked while its margin session is open. Removing a restoration removes only its own managed artifacts.

## Manual Margin Contract

- One target-local managed Curve.
- One ordered 3D `POLY` spline.
- At least six unique finite points.
- Cyclic closure before validation.
- Reprojection only to the owning preparation scan.
- Reset and Cancel restore the exact session-start state.
- Applying a candidate does not approve it.

## Antagonist Region Contract

When an opposing arch exists:

- A region is required before restoration approval.
- The region may be detected from the margin location or picked manually.
- The center remains attached to the opposing scan.
- Radius is constrained to the supported engineering range.
- Visual review is required.
- Material region or opposing-scan changes invalidate approval.

When no opposing arch exists, the region is explicitly not applicable and does not block approval.

## Validation and Approval

Blocking errors include invalid upstream state, missing or duplicate restoration targets, changed scans, invalid ownership, invalid Curve structure, insufficient or collapsed points, non-cyclic margins, excessive surface distance, missing required antagonist region, invalid region ownership, or changed opposing scan.

Warnings include sparse points, moderate surface distance, substantial spacing variation, possible folded geometry, unusual path dimensions, and moderate antagonist-center surface distance.

Approval requires a fresh successful validation pass, explicit margin review, antagonist-region review when applicable, and warning acknowledgment when warnings exist. Engineering checks do not certify clinical correctness.

## Invalidation

- Material edits invalidate only the owning restoration.
- Step 1 or Step 2 invalidation clears all restoration approvals.
- Target-scan replacement invalidates dependent restorations.
- Opposing-scan or antagonist-region changes invalidate the owning restoration.
- Usable geometry is preserved when safe.
- Case reset removes only B-Dental-managed content.

## Acceptance Criteria

v0.0.4 is accepted because:

1. Multiple restorations coexist and persist.
2. Upper and lower restorations coexist in dual/full cases.
3. Duplicate targets are rejected.
4. Independent sessions, validation, approval, removal, and invalidation work correctly.
5. Every restoration owns separate managed artifacts.
6. Antagonist regions work automatically and manually when applicable.
7. Single-arch cases remain supported.
8. Aggregate validity requires every restoration to be approved.
9. Imported scan topology and coordinates remain unchanged.
10. Manifest validation, package build and inspection, installation, lifecycle, migration, regressions, and the complete Step 3 verification matrix passed locally.

## Completion Record

The implementation, documentation, packaging, and local verification are complete. Version v0.0.4 is ready for a non-draft pull request and **Squash and merge** into `main`.
