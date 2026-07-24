# Decision 0002: Derive the Preparation Region from the Approved Margin

## Metadata

- **Version:** v0.0.6
- **Status:** Accepted for implementation
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-automated-preparation-die-crown-bottom.md`](../plans/0001-automated-preparation-die-crown-bottom.md)

## Context

Step 5 needs a bounded preparation surface, but automatic tooth segmentation is not yet an approved project capability. Step 3 already provides an ordered, reviewed margin attached to the target scan.

## Decision

- Treat the approved margin as the authoritative boundary for preparation-region extraction.
- Map margin samples to stable target-surface anchors.
- Build deterministic triangle adjacency from evaluated target geometry.
- Extract one bounded surface patch using boundary classification and surface traversal.
- Use the approved insertion axis as a secondary filter to reduce leakage into adjacent anatomy.
- Reject open, branching, ambiguous, or multiple-region results instead of selecting one silently.
- Preserve ordered margin correspondence in the extracted boundary.

## Rationale

The approved margin is the strongest restoration-specific boundary already available. It enables a practical non-destructive Step 5 without pretending that reliable automatic segmentation exists.

## Rejected Alternatives

- **Automatic full-tooth segmentation:** deferred because it requires a separate validated capability.
- **Simple Euclidean radius crop:** rejected because it may include adjacent teeth or omit deep preparation surfaces.
- **Viewport selection or active-object state:** rejected because it is transient and non-reproducible.
- **Always choose the largest connected region:** rejected because the largest region may be anatomically wrong.

## Consequences

- Margin anchoring and surface-graph construction are required.
- Extraction ambiguity must be measurable and visible.
- Damaged scans or poor margins may produce explicit generation failure.
- Future automatic segmentation can replace or strengthen this phase while preserving the same downstream die contract.