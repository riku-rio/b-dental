# Decision 0004: Use Reversible Manual Margin Sessions

## Metadata

- **Version:** v0.0.4
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

Manual margin drawing and editing are interactive operations that may be cancelled, restarted, or fail because of invalid clicks, stale objects, context changes, or unexpected Blender errors. Directly overwriting an existing approved margin during interaction would risk losing the last accepted result.

## Decision

- Margin creation and modification occur inside an explicit session.
- Session start records whether a margin existed, its exact ordered local-space points, its curve structure, and the prior Step 3 state.
- A new session may begin from no margin, an applied candidate, or an approved margin.
- Reset restores the exact session-start margin and keeps the session active.
- Cancel restores the exact session-start margin and prior Step 3 state, then closes the session.
- If no margin existed at session start, Cancel removes the draft managed margin.
- Apply Candidate keeps the current closed candidate, closes the session, invalidates prior approval, and does not approve Step 3.
- Exceptions and invalid context restore a safe snapshot whenever possible.
- Navigation away from Step 3 is blocked while a session remains unresolved.

## Rationale

This follows the safety model established by Step 2 while adapting it to ordered curve points instead of object matrices. It protects prior work, keeps user intent explicit, and makes destructive outcomes predictable and testable.

## Rejected Alternatives

- **Edit the approved margin in place without snapshots:** rejected because cancellation cannot restore the accepted result reliably.
- **Depend only on Blender Undo:** rejected because operator context, modal actions, save/reopen behavior, and workflow state require explicit deterministic restoration.
- **Auto-apply on leaving Step 3:** rejected because navigation must not silently accept geometry.
- **Auto-approve after closing the curve:** rejected because curve closure is not validation or professional review.
- **Create a permanent duplicate for every preview:** rejected because duplicate ownership and cleanup would become error-prone.

## Consequences

- Point serialization and exact ordered restoration are required.
- Session state must include prior status, validity, diagnostics, review, and approval data.
- Modal drawing and later editing must share the same session contract.
- Reset, Cancel, Apply, exception rollback, and navigation blocking require dedicated verification scenarios.
- Applied candidates remain separate from approved results.

## Acceptance Confirmation

This decision becomes accepted when the v0.0.4 documentation set is approved. Implementation must not rely on Blender Undo as the only restoration mechanism.
