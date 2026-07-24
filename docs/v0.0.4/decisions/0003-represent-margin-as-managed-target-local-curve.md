# Decision 0003: Represent the Margin as a Managed Target-Local Curve

## Metadata

- **Version:** v0.0.4
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

The manual margin must remain visible and editable while staying associated with the correct preparation scan. Editing imported scan meshes directly would violate the non-destructive workflow.

## Decision

- Each restoration owns one B-Dental-managed Blender Curve.
- The Curve contains one ordered 3D `POLY` spline.
- Candidate and approved margins are cyclic.
- Coordinates are stored in the target preparation scan's local space.
- Ownership metadata includes restoration ID, target role, tooth, artifact type, and schema version.
- The margin remains visible through Curve display settings and the viewport overlay.
- Imported scan topology and coordinates are not modified.

## Rationale

A target-local managed Curve provides native editability, deterministic ownership, reversible sessions, persistence, reprojection, validation, and a stable downstream contract.

## Rejected Alternatives

- Writing margin edges into the scan mesh.
- Storing only world-space points.
- Using Grease Pencil as the authoritative artifact.
- Using arbitrary user-created curves.
- Combining multiple restorations in one multi-spline object.

## Consequences

Coordinate conversion, metadata validation, safe recovery, overlay registration, and dependent invalidation are required.

## Acceptance Confirmation

Accepted after successful v0.0.4 implementation and local verification.
