# Decision 0005: Require Explicit Step 4 Validation and Approval

## Metadata

- **Version:** v0.0.5
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-preparation-analysis-insertion-axis.md`](../plans/0001-preparation-analysis-insertion-axis.md)

## Context

A finite axis and completed undercut calculation do not prove that the selected insertion direction is clinically appropriate. Analysis may be affected by neighborhood radius, sampling density, adjacent anatomy, scan quality, and the absence of preparation segmentation.

Later crown-bottom stages need a clear contract that distinguishes a candidate, a current engineering analysis, and an explicitly reviewed result.

## Decision

- Axis creation, capture, and Apply never set Step 4 valid.
- Running undercut analysis never approves Step 4 automatically.
- Validation reports blocking errors separately from non-blocking engineering warnings.
- Approval requires a finite normalized axis, current analysis, valid dependency signatures, no blocking errors, explicit visual review, and warning acknowledgment when warnings exist.
- Approval is independent per restoration.
- Approval stores the axis vector, source, analysis settings, metrics, and target, margin, antagonist, upstream, and result signatures.
- Material changes to upstream state, axis, radius, managed artifacts, or analysis invalidate approval.
- Aggregate Step 4 validity becomes true only when every restoration is independently approved.
- UI and stored summaries must state that engineering validation does not certify clinical correctness.

## Rationale

Separating candidate creation, analysis, validation, and approval prevents false confidence and matches the explicit-review safety model established in earlier workflow stages.

## Rejected Alternatives

- **Approve when an axis is captured:** rejected because a direction alone has not been analyzed.
- **Approve automatically when analysis finishes:** rejected because numerical completion does not establish suitability.
- **Treat every warning as blocking:** rejected because some conditions require informed review rather than forced rejection.
- **Use one global Step 4 approval:** rejected because restorations have independent geometry, axes, analysis, and risks.
- **Store only current state without approval snapshots:** rejected because later material changes would be difficult to detect reliably.

## Consequences

- Step 4 requires candidate, analyzed, and verified statuses.
- Validation and approval operators must remain separate.
- Review and warning acknowledgment clear after material changes.
- Per-restoration and aggregate validity synchronization is required.
- Later stages may depend on `step_4_valid`, not merely the presence of an axis or metrics.
- Verification must test stale-result rejection and independent aggregate completion.