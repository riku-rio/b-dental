# Decision 0006: Rank Only Candidates That Pass Blocking Constraints

## Metadata

- **Version:** v0.0.6
- **Status:** Accepted for implementation
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-automated-preparation-die-crown-bottom.md`](../plans/0001-automated-preparation-die-crown-bottom.md)

## Context

Step 5 may generate multiple geometric candidates. A weighted score alone could allow a candidate with a critical defect to outrank a structurally valid candidate by performing well on softer objectives.

## Decision

- Evaluate blocking constraints before computing final rank.
- Reject candidates with invalid seal-band continuity, unresolved insertion obstruction, self-intersection, stale ownership, invalid topology beyond accepted repair, or other PRD-defined blocking failures.
- Preserve rejection reasons and metrics for diagnostics.
- Compute normalized objective terms only for candidates eligible for acceptance.
- Rank accepted candidates using documented weights and deterministic stable tie-breaking.
- Report ranking ambiguity when accepted scores are materially close.
- Never allow a high aggregate score to cancel a blocking failure.

## Rationale

Hard constraints define whether a candidate is structurally usable. Ranking is meaningful only among candidates that already satisfy those requirements.

## Rejected Alternatives

- **One unconstrained weighted score:** rejected because critical failures could be traded against cosmetic improvements.
- **Always choose the first generated candidate:** rejected because measurable alternatives may differ materially.
- **Hide rejected candidates:** rejected because failure diagnostics are necessary for debugging and constrained correction.
- **Manual visual ranking only:** rejected because the automation-first workflow requires reproducible measurable selection.

## Consequences

- Validation and scoring must be separate phases.
- Every constraint and objective needs a stable identifier and finite metric.
- Weight and threshold versions must participate in dependency signatures.
- The UI must distinguish rejected, accepted, selected, and approved candidates.