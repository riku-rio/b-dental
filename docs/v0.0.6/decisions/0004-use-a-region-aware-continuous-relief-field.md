# Decision 0004: Use a Region-Aware Continuous Relief Field

## Metadata

- **Version:** v0.0.6
- **Status:** Accepted for implementation
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-automated-preparation-die-crown-bottom.md`](../plans/0001-automated-preparation-die-crown-bottom.md)

## Context

A crown bottom requires different internal spacing near the margin, on axial walls, and on the occlusal surface. One uniform offset cannot represent marginal seal, spacer start, cement space, axial relief, and occlusal relief correctly.

## Decision

- Compute a deterministic distance-from-margin field on the blocked preparation surface.
- Classify seal, transition, axial, and occlusal regions using stored geometric rules.
- Build one continuous scalar relief field from marginal gap, spacer start, cement gap, axial relief, and occlusal relief settings.
- Use bounded interpolation across transition regions.
- Apply the field along stable generated-surface directions.
- Detect offset inversion, folding, self-intersection, and local collapse.
- Store achieved regional gap metrics rather than assuming requested values were achieved.

## Rationale

A continuous field gives explicit control of all required zones while avoiding abrupt internal steps and hidden modifier behavior.

## Rejected Alternatives

- **Single uniform offset:** rejected because it cannot preserve a seal region and separate axial/occlusal targets.
- **Independent disconnected offsets:** rejected because they create discontinuities.
- **Modifier stack as the authoritative definition:** rejected because evaluated results and settings must remain measurable and reproducible.
- **Manual painting as the default:** rejected because routine spacing should be generated automatically.

## Consequences

- Surface-distance and surface-classification helpers are required.
- Requested and achieved spacing must both be recorded.
- Transition width and smoothing policy become signed dependencies.
- Extreme or contradictory settings must fail validation instead of producing collapsed geometry.