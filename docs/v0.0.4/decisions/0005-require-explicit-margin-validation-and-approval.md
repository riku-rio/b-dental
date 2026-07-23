# Decision 0005: Require Explicit Margin Validation and Approval

## Metadata

- **Version:** v0.0.4
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

A closed curve can still be incomplete, detached from the preparation surface, structurally invalid, associated with the wrong restoration, or clinically inappropriate. Operator success and geometric diagnostics cannot prove that a margin is clinically correct.

## Decision

- Candidate creation never sets `step_3_valid = true`.
- Applying a candidate never sets `step_3_valid = true`.
- Validation reports separate blocking errors and non-blocking warnings.
- Approval is blocked for invalid ownership, metadata, curve structure, point coordinates, closure, minimum point count, target association, or excessive surface distance.
- Engineering warnings include sparse points, moderate surface distance, abnormal spacing, possible folded geometry, and unusual path dimensions.
- Warnings require explicit acknowledgment.
- Approval requires explicit visual-review confirmation.
- Only an explicit Approve Margin action sets `step_3_status = VERIFIED` and `step_3_valid = true`.
- Approval stores an ordered point snapshot, target signature, diagnostics, and summary.
- Diagnostics are presented as engineering aids and never as clinical certification.

## Rationale

Separating candidate state, validation, and approval prevents false confidence and mirrors the explicit approval model already established for occlusion. It also gives later stages a clear contract: Step 3 is complete only when the user has reviewed and approved a technically valid managed margin.

## Rejected Alternatives

- **Approve automatically when the curve closes:** rejected because closure proves only path structure.
- **Approve automatically when all numerical thresholds pass:** rejected because numerical checks cannot establish clinical correctness.
- **Treat every diagnostic as blocking:** rejected because some geometry concerns require review rather than forced rejection.
- **Display warnings without acknowledgment:** rejected because significant warnings could be overlooked.
- **Store only the current curve as proof of approval:** rejected because later edits would make it difficult to detect material changes.

## Consequences

- Step 3 requires explicit candidate, validation, and approval states.
- Review and warning acknowledgment must be persistent enough for the active candidate but cleared after material changes.
- Approved point and target signatures are required for invalidation monitoring.
- The UI must explain that successful checks do not certify the margin.
- Later crown-design stages may depend on `step_3_valid`, not merely on the presence of a curve.

## Acceptance Confirmation

This decision becomes accepted when the v0.0.4 documentation set is approved. Any automatic approval behavior is outside the accepted scope.
