# Plan 0001: Multiple Restoration Setup, Manual Margin Definition & Antagonist Regions

## Metadata

- **Version:** v0.0.4
- **Status:** Complete
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Target merge branch:** `main`
- **Merge strategy:** Squash and merge
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related tasks:** [`../TASKS.md`](../TASKS.md)
- **Verification:** [`../VERIFICATION.md`](../VERIFICATION.md)

## Objective

Implement Step 3 as a persistent collection-based workflow supporting multiple independent single-unit anatomical crown restorations, one manually defined target-local margin per restoration, and one reviewed antagonist region when an opposing arch exists.

## Delivered Architecture

### Restoration collection

`properties.py` stores independent restoration identity, preparation arch, permanent FDI tooth, status, validity, margin state, antagonist-region state, diagnostics, session snapshots, and approval signatures. Aggregate Step 3 validity is true only when every configured restoration is verified.

### Managed artifacts

- `margin_geometry.py` owns closed target-local 3D `POLY` margin Curves.
- `margin_overlay.py` provides a stable viewport presentation for margins.
- `antagonist_region.py` owns per-restoration opposing-region markers, automatic detection, manual picking, review, validation, invalidation, and cleanup.
- `restoration_utils.py` provides stable ownership, recovery, migration, and safe removal behavior.

### Sessions and validation

- Margin drawing and editing are reversible.
- Candidate capture and application do not approve a restoration.
- Margin and antagonist-region checks produce blocking errors and warnings.
- Visual review and warning acknowledgment are explicit.
- Material changes invalidate only the affected restoration unless an upstream dependency affects all restorations.

### User interface

Step 3 exposes restoration creation, selection, removal, margin drawing/editing, antagonist-region definition, diagnostics, review, approval, and aggregate completion at normal Blender Sidebar width.

## Completed Phases

1. Documentation and architectural decisions.
2. Persistent collection state and migration.
3. Managed restoration ownership.
4. Manual-margin geometry, display, and overlay.
5. Reversible drawing and editing sessions.
6. Per-restoration validation and approval.
7. Antagonist-region MVP for dual/full scan cases.
8. Independent invalidation and safe cleanup.
9. Packaging, installation, migration, regression, lifecycle, and scenario verification.
10. Release documentation and non-draft pull-request preparation.

## Safety Contract

- Imported scan topology and coordinates are not modified by Step 3.
- Margin clicks are restricted to the active preparation scan.
- Antagonist-region picks are restricted to the resolved opposing scan.
- Removing one restoration removes only its managed artifacts.
- Single-arch cases treat antagonist regions as not applicable.
- Engineering validation never certifies clinical correctness.
- Failed or cancelled operations must not create false approval.

## Completion Record

The full implementation was completed and locally verified. Manifest validation, ZIP build and inspection, installation, repeated lifecycle testing, migrations, Step 1 and Step 2 regressions, multiple-restoration workflows, margin workflows, antagonist-region workflows, persistence, invalidation, removal, reset, and scene-safety checks passed before release preparation.
