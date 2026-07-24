# Decision 0005: Require a Continuous Margin-Correspondent Seal Band

## Metadata

- **Version:** v0.0.6
- **Status:** Accepted for implementation
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-automated-preparation-die-crown-bottom.md`](../plans/0001-automated-preparation-die-crown-bottom.md)

## Context

The crown-bottom boundary must follow the approved margin continuously. A candidate with a visually close but broken, branching, folded, or weakly corresponding boundary cannot be treated as a valid internal restoration foundation.

## Decision

- Preserve ordered correspondence between the approved margin and the outer seal-band boundary.
- Generate exactly one continuous seal band around the complete restoration margin.
- Construct the inner band boundary from configured width and gap targets.
- Join the band continuously to the relieved internal surface.
- Validate continuity, orientation, correspondence coverage, width, deviation, branch count, duplicate segments, flipped faces, and self-intersection.
- Treat discontinuity or ambiguous correspondence as a blocking failure.

## Rationale

The margin seal is a primary geometric contract, not a cosmetic feature. Explicit correspondence and continuity make it measurable, reproducible, and safe for downstream anatomy and finalization.

## Rejected Alternatives

- **Nearest-point boundary without ordered correspondence:** rejected because points may jump between unrelated surface regions.
- **Patch small gaps silently:** rejected because the cause and resulting topology may be unsafe.
- **Allow multiple seal loops:** rejected for the supported single-unit crown scope.
- **Judge continuity only by viewport appearance:** rejected because rendering can hide small gaps and topology defects.

## Consequences

- Margin resampling and stable loop indexing are required.
- Seal-band metrics are blocking inputs to candidate acceptance.
- Local constrained reprojection may be provided, but it must preserve the approved margin contract and require revalidation.