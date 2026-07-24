# Decision 0003: Use an Insertion-Axis-Aligned Accessible Envelope for Blockout

## Metadata

- **Version:** v0.0.6
- **Status:** Accepted for implementation
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-automated-preparation-die-crown-bottom.md`](../plans/0001-automated-preparation-die-crown-bottom.md)

## Context

The crown bottom must seat and withdraw along the approved Step 4 insertion axis. A normal-offset copy of the preparation would reproduce undercuts and may create an internal surface that cannot follow the approved path.

## Decision

- Transform preparation-die geometry into an insertion-axis-aligned working frame.
- Construct an accessible envelope by resolving the first reachable preparation surface along the seating or removal direction.
- Fill inaccessible concavities according to a deterministic bounded sampling and reconstruction policy.
- Apply configurable blockout clearance to the accessible envelope.
- Protect the approved margin and future seal-band boundary from uncontrolled displacement.
- Re-test the generated blocked geometry for residual path obstruction.
- Reject unresolved, folded, inverted, discontinuous, or non-reconstructable results.

## Rationale

An axis-aligned accessible envelope directly models the geometric path-of-insertion requirement and converts undercut correction into a measurable construction rather than a visual heuristic.

## Rejected Alternatives

- **Uniform normal offset:** rejected because it preserves undercuts.
- **Destructive sculpting or voxel filling by the user:** rejected because automation is the primary workflow.
- **Use Step 4 sample classifications alone as final geometry:** rejected because sparse diagnostics are not a continuous surface.
- **Ignore small residual obstructions automatically:** rejected because tolerances must be explicit and validated.

## Consequences

- A bounded axis-aligned sampling or equivalent envelope representation is required.
- Reconstruction resolution and tolerance affect quality and must be stored in settings and signatures.
- Residual collision validation is mandatory.
- Some complex or low-resolution preparations may be rejected and require constrained expert review.