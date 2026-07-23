# Decision 0002: Use Bite Scans as Intermediate Registration References

## Metadata

- **Version:** v0.0.3
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-occlusion-registration-verification.md`](../plans/0001-occlusion-registration-verification.md)

## Context

Upper and lower arches are opposing anatomical surfaces. Direct nearest-neighbor registration between them can incorrectly pull complementary surfaces into overlap.

Buccal bite scans contain partial observations of both arches in the captured relationship and therefore provide meaningful intermediate registration references.

## Decision

B-Dental does not run direct ICP between upper and lower jaw meshes.

Bite-guided registration uses this sequence:

1. Keep the upper jaw fixed.
2. Register the selected bite scan to the upper jaw.
3. Use the aligned bite as an intermediate target for the lower jaw.
4. Move only the lower jaw during final arch registration.

Supported sources:

- Right Bite.
- Left Bite.
- Both Bites.

Both Bites mode aligns both bite scans to the upper jaw, refines the lower jaw against a combined target, and calculates right-only and left-only diagnostics.

## Rationale

This approach matches the role of buccal bite records, avoids collapsing opposing arches, supports unilateral and bilateral workflows, and exposes bilateral disagreement rather than silently hiding it.

## Rejected Alternatives

- **Direct upper-to-lower ICP:** rejected because the surfaces are complementary rather than duplicate observations.
- **Treat bite scans as final anatomy:** rejected because bite scans are partial and may contain noise.
- **Require both bites:** rejected because some cases have only one usable bite.
- **Silently average disagreement:** rejected because meaningful disagreement must remain visible.

## Consequences

- Registration uses geometrically meaningful overlap.
- Bilateral consistency can be measured.
- Bite objects remain available for inspection.
- Reasonable initial overlap is still required.
- Automatic registration does not establish clinical correctness.

## Implementation Confirmation

The accepted v0.0.3 implementation provides Right, Left, and Both Bites paths, robust filtering, failure safety, preserved bite objects, and bilateral disagreement reporting without direct upper-to-lower ICP.
