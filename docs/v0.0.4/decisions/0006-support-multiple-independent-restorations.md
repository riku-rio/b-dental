# Decision 0006: Support Multiple Independent Restorations

## Metadata

- **Version:** v0.0.4
- **Status:** Accepted
- **Supersedes:** [`0001-limit-v0.0.4-to-one-anatomical-crown.md`](0001-limit-v0.0.4-to-one-anatomical-crown.md)
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

A dental case may contain more than one prepared tooth, including preparations distributed across both upper and lower arches. Replacing a single active restoration discards valid margin work and does not represent the case accurately.

## Decision

- A B-Dental case may contain multiple restorations.
- v0.0.4 still supports only single-unit `ANATOMICAL_CROWN` restorations.
- Each restoration has a stable ID, target arch, permanent FDI tooth, margin pointer, session state, diagnostics, validation state, and approval state.
- The same arch and FDI tooth combination cannot be added twice.
- Only one restoration is active for editing at a time.
- Switching restorations is blocked while a margin session is active.
- Removing a restoration deletes only its own managed margin.
- Step 3 is complete only when at least one restoration exists and every configured restoration is approved.
- Upstream invalidation invalidates every restoration approval while preserving usable managed margin geometry when safe.

## Rationale

This model supports real multi-preparation cases, preserves upper and lower margin work in one case, keeps ownership explicit, and gives later crown-design stages a stable restoration collection.

## Rejected Alternatives

- **One restoration per Blender file:** rejected because it duplicates scans and case state.
- **Overwrite the active restoration:** rejected because it destroys prior margin work.
- **One margin object containing multiple splines:** rejected because ownership, validation, editing, and approval would become ambiguous.
- **Multiple restorations with one global approval:** rejected because each margin needs independent review and diagnostics.

## Consequences

- Step 3 state is stored in a Blender `CollectionProperty`.
- Margin operations are scoped to the active restoration.
- The UI requires restoration list, add, select, and remove controls.
- Migration is required for the earlier in-branch single-restoration implementation.
- Verification must cover mixed upper/lower restorations and independent approval behavior.
