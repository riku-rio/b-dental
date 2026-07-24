# Tasks: v0.0.5

## Status

- **Version:** v0.0.5
- **Release status:** Complete
- **Workflow:** Step 4 — Preparation Analysis & Insertion Axis
- **Verification:** Passed locally
- **Merge strategy:** Squash and merge

## Documentation Foundation

- [x] V005-001 through V005-011 — Define and approve the Step 4 scope, direction convention, state model, session behavior, analysis behavior, approval rules, implementation plan, verification matrix, and architectural decisions.

## Version and Workflow State

- [x] V005-012 through V005-025 — Update the manifest to `0.0.5`; add Step 4 workflow and per-restoration state, axis state, session snapshots, analysis settings and metrics, diagnostics, review state, approval signatures, and aggregate synchronization.

## Step 4 Entry and Navigation

- [x] V005-026 through V005-031 — Add gated Step 4 entry, preserve Step 1–3 data, avoid automatic candidate creation, provide safe return, and block navigation while an axis session is active.

## Insertion-Axis Geometry

- [x] V005-032 through V005-041 — Add finite-vector checks, normalization, local/world conversion, current-view capture, margin-derived center and normal suggestion, sign resolution, authoritative target-local storage, and object-orientation conversion.

## Managed Axis Artifact

- [x] V005-042 through V005-051 — Add owned managed-axis objects, preparation-scan parenting, margin-derived origins, positive-Z alignment, viewport display, render disabling, pointer recovery, scoped removal, and unrelated-content preservation.

## Reversible Axis Sessions

- [x] V005-052 through V005-064 — Add session Start, snapshots, exact Reset and Cancel, Capture and Apply, stale-analysis clearing, non-automatic approval, switching gates, and inactive-restoration preservation.

## Axis Candidate Operators

- [x] V005-065 through V005-073 — Add Set From Current View, Suggest From Margin, edit, capture, apply, reset, cancel, focus, visibility, and clear-axis behavior.

## Preparation-Analysis Neighborhood

- [x] V005-074 through V005-081 — Add margin-derived center and default radius, safe radius clamping, user adjustment, deterministic target-surface sampling, sample/runtime bounds, empty-neighborhood rejection, and stale-result invalidation.

## Undercut Analysis

- [x] V005-082 through V005-094 — Add deterministic evaluated-mesh analysis, world-space acceleration geometry, removal-direction obstruction tests, scale-aware self-hit handling, non-destructive classification, depth metrics, signatures, and stale-result clearing.

## Analysis Overlay

- [x] V005-095 through V005-100 — Add active-restoration viewport visualization, distinct clear/undercut samples, Show/Hide/Clear controls, lifecycle-safe registration, and non-destructive overlay storage.

## Validation and Approval

- [x] V005-101 through V005-120 — Add upstream, target, margin, ownership, axis, session, radius, sample, and signature validation; engineering warnings; explicit review; warning acknowledgment; independent approval; approval snapshots; and aggregate completion.

## Invalidation and Monitoring

- [x] V005-121 through V005-130 — Monitor Step 4 dependencies, invalidate after upstream, margin, target, axis, radius, artifact, or analysis changes, preserve safe candidates, and clean up during restoration removal and case reset.

## Migration

- [x] V005-131 through V005-134 — Add safe v0.0.4 defaults, avoid automatic Step 4 artifacts on open, preserve Step 1–3 state, and document the in-branch sampling-policy correction.

## User Interface

- [x] V005-135 through V005-148 — Display aggregate status, restoration progress, active identity, axis controls, reversible-session controls, vector/source summary, radius, analysis action, overlay controls, metrics, diagnostics, disclaimer, review, acknowledgment, approval, and normal-width readability.

## Packaging and Verification

- [x] V005-149 Add Step 4 modules to `blender_manifest.toml`.
- [x] V005-150 Validate the extension manifest.
- [x] V005-151 Build `b_dental-0.0.5.zip`.
- [x] V005-152 Inspect package contents.
- [x] V005-153 Install and enable the package.
- [x] V005-154 Verify repeated enable, disable, restart, and reload.
- [x] V005-155 Verify v0.0.4 migration.
- [x] V005-156 Re-run Step 1 regression scenarios.
- [x] V005-157 Re-run Step 2 regression scenarios.
- [x] V005-158 Re-run Step 3 regression scenarios.
- [x] V005-159 Execute the complete Step 4 scenario matrix.
- [x] V005-160 Record actual implementation results and deviations.
- [x] V005-161 Update README after acceptance.
- [x] V005-162 Mark PRD, plan, decisions, tasks, and verification complete after local verification.
- [x] V005-163 Prepare a non-draft PR for **Squash and merge**.

## Verification Corrections

Two defects found during local verification were fixed before acceptance:

1. The manifest tagline was shortened to satisfy Blender's 64-character limit.
2. Preparation sampling and BVH ray analysis were moved to world space so a world-unit radius behaves correctly for imported scans with non-identity scale; stored overlay points remain target-local.

## Completion Record

The implementation, documentation, packaging, and local verification are complete. Version v0.0.5 is ready for a non-draft pull request and **Squash and merge** into `main`.
