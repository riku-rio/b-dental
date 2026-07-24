# Decision 0007: Model the Antagonist Region as a Managed Restoration Artifact

## Metadata

- **Version:** v0.0.4
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

Later crown-design stages need a persistent indication of the relevant opposing surface. Requiring manual selection of an opposing FDI tooth would add a second tooth-numbering workflow without providing the actual surface region required for contact analysis.

## Decision

- Each restoration may own one managed antagonist-region marker.
- The opposing arch is resolved from the restoration preparation arch.
- Dual-arch and full-scan cases require a reviewed region before approval.
- Single-arch cases treat the region as not applicable.
- The region may be created by automatic closest-surface detection from the margin location or by manual picking on the opposing scan.
- The marker stores restoration ownership, opposing role, source, radius, scan signature, and approval signature.
- Radius is constrained to the supported MVP range.
- Region, radius, or opposing-scan changes invalidate only the owning restoration approval.
- Restoration removal and case reset remove managed regions without affecting unrelated objects.
- The region is an engineering workflow marker, not an automatically segmented anatomical tooth.

## Rationale

A managed region provides the geometric context required by future contact-analysis stages while keeping the MVP independent of automatic tooth segmentation and opposing-tooth numbering.

## Rejected Alternatives

- Requiring a manually selected opposing FDI tooth.
- Automatically segmenting and numbering opposing teeth in v0.0.4.
- Using the full opposing arch without a localized region.
- Storing only an unowned world-space point.
- Deferring all opposing-surface context until crown generation.

## Consequences

Step 3 approval depends on region review when an opposing scan exists. Persistence, validation, recovery, invalidation, visibility, and cleanup must be scoped per restoration. Future stages may refine the marker into a true surface subset without changing its restoration ownership contract.

## Acceptance Confirmation

Accepted after successful v0.0.4 implementation and local verification.
