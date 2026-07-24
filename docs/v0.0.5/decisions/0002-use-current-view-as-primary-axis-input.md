# Decision 0002: Use the Current 3D View as the Primary Axis Input

## Metadata

- **Version:** v0.0.5
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-preparation-analysis-insertion-axis.md`](../plans/0001-preparation-analysis-insertion-axis.md)

## Context

The MVP needs a practical way for the user to define an insertion direction without automatic tooth segmentation, preparation classification, or clinically authoritative optimization.

The user can already orient the Blender viewport to inspect the preparation from an intended path of insertion. Capturing that direction is simple, explainable, and compatible with later manual adjustment.

## Decision

- **Set From Current View** is the primary v0.0.5 insertion-axis input.
- The user positions the viewport while looking toward the preparation along the intended seating direction.
- The viewport forward direction is converted to preparation-scan local coordinates and normalized.
- The captured direction becomes an axis candidate, not an approved result.
- **Suggest From Margin** may provide a secondary engineering candidate based on the approved margin geometry.
- The margin-normal sign is selected using the current viewport direction.
- Both methods require explicit visual review and subsequent analysis.
- No method is described as clinically automatic or optimal.

## Rationale

Current-view capture gives the user direct control, avoids hidden optimization assumptions, works without segmentation, and can be implemented using Blender's existing 3D View state.

A margin-normal suggestion is useful as a starting point but is geometrically ambiguous and may not represent the intended path of insertion.

## Rejected Alternatives

- **Fully automatic optimal axis:** rejected because clinical optimization criteria and reliable preparation segmentation are outside scope.
- **Margin normal as the only method:** rejected because the normal has two possible signs and may not represent the desired insertion direction.
- **Global jaw Z axis:** rejected because imported scan orientation is not guaranteed to follow a fixed convention.
- **Three-point manual plane definition:** rejected for the MVP because it adds interaction complexity without eliminating the need for review.
- **Numeric XYZ entry as the primary workflow:** rejected because it is less intuitive for routine visual use.

## Consequences

- Step 4 UI must explain the viewing-direction convention clearly.
- View capture requires a valid 3D View context.
- Determinism must be verified from unchanged view state.
- Suggestion and current-view source must be stored separately.
- Later versions may add additional candidate methods without changing the authoritative target-local representation.