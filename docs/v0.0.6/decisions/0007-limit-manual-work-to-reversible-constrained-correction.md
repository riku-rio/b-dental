# Decision 0007: Limit Manual Work to Reversible Constrained Correction

## Metadata

- **Version:** v0.0.6
- **Status:** Accepted for implementation
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-automated-preparation-die-crown-bottom.md`](../plans/0001-automated-preparation-die-crown-bottom.md)

## Context

The product roadmap defines B-Dental as automation-first. Unrestricted manual sculpting of the crown bottom would recreate a traditional manual CAD workflow, weaken reproducibility, and make geometric validation difficult.

## Decision

- Automatic generation is the primary Step 5 path.
- Manual changes are available only inside a managed reversible correction session.
- Sessions support Start, Reset, Cancel, Capture, and Apply.
- Allowed corrections are bounded operations such as localized offset adjustment, boundary-preserving smoothing, seal-band reprojection, candidate switching, or local regeneration.
- Protected boundaries, ownership, insertion-path constraints, and accepted displacement limits remain enforced.
- Applying a correction clears previous validation and approval and runs the full validation pipeline again.
- Direct edits outside a managed session invalidate the candidate.
- Expert override is explicit and recorded but cannot suppress structural blocking errors.

## Rationale

Constrained correction preserves expert control for exceptional cases while keeping the normal workflow automated, measurable, reversible, and reviewable.

## Rejected Alternatives

- **Unrestricted Edit Mode or Sculpt Mode as the normal path:** rejected because it is non-reproducible and difficult to validate.
- **No manual correction at all:** rejected because supported automation may still need bounded expert intervention.
- **Apply changes without revalidation:** rejected because geometric constraints may have changed.
- **Override every validation failure:** rejected because structurally invalid candidates must remain ineligible for approval.

## Consequences

- Session snapshots must include geometry and relevant state.
- Correction operators need explicit bounds and protected regions.
- Generated-mesh integrity monitoring is required.
- Validation remains authoritative after every automated or corrected candidate change.