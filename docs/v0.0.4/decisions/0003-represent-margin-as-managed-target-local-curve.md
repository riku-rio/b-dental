# Decision 0003: Represent the Margin as a Managed Target-Local Curve

## Metadata

- **Version:** v0.0.4
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

The manual margin must remain visible and editable while staying associated with the correct preparation scan. Storing only world-space coordinates would make the margin fragile when the target scan transform changes. Editing the imported scan mesh directly would violate the existing non-destructive workflow and complicate rollback.

## Decision

- The margin is one B-Dental-managed Blender Curve object.
- It contains one 3D `POLY` spline.
- Candidate and approved margins are cyclic closed paths.
- Ordered margin coordinates are stored in the target preparation scan's local coordinate system.
- The margin object is associated with the target scan so its displayed position follows that scan.
- The object carries explicit B-Dental ownership, artifact type, restoration ID, target role, target tooth, and schema metadata.
- The margin is placed in `B-Dental Restorations`.
- Imported scan mesh coordinates and topology are never modified to create or store the margin.
- Additional splines or unsupported spline types are rejected during validation.

## Rationale

A managed Curve object provides native viewport visibility and editability. Target-local coordinates preserve the geometric relationship to the preparation scan and simplify serialization, rollback, reprojection, diagnostics, and future downstream design stages.

## Rejected Alternatives

- **Write the margin into the scan mesh:** rejected because it is destructive and mixes imported source geometry with workflow artifacts.
- **Store only world-space points:** rejected because later target transforms could detach the margin from the preparation.
- **Use Grease Pencil as the authoritative artifact:** rejected because the required geometry and persistence model is less direct for downstream curve-based operations.
- **Use a mesh edge loop as the authoritative artifact:** rejected because point editing, cyclic-path validation, and curve display are simpler with a Curve object.
- **Allow arbitrary user-created curves:** rejected because ownership, target association, and safe cleanup would be ambiguous.

## Consequences

- Coordinate conversion between world and target-local space is required during drawing and display.
- The implementation must safely handle target parenting or equivalent transform association without changing scan transforms.
- Curve structure and metadata become approval preconditions.
- A later downstream stage can consume a stable ordered closed path.
- Replacing or removing the target scan invalidates and removes its dependent managed margin.

## Acceptance Confirmation

This decision becomes accepted when the v0.0.4 documentation set is approved. Any alternative authoritative geometry representation requires a revised decision record and migration plan.
