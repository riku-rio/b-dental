# Decision 0004: Use Reversible Manual Margin Sessions

## Metadata

- **Version:** v0.0.4
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

Manual margin creation and editing are interactive and may be cancelled, reset, or interrupted. Directly overwriting approved geometry would risk losing the last accepted state.

## Decision

- Margin creation and editing occur inside explicit per-restoration sessions.
- Session start snapshots the exact ordered points, structure, diagnostics, review state, and approval state.
- Reset restores the session-start margin and keeps the session active.
- Cancel restores the exact prior state and closes the session.
- A new draft is removed on Cancel when no margin existed at session start.
- Apply Candidate retains the closed candidate, closes the session, invalidates prior approval, and does not approve the restoration.
- Switching restorations is blocked while a margin session is unresolved.
- Blender Undo is not the sole rollback mechanism.

## Rationale

Explicit snapshots make rollback deterministic, isolate changes to the active restoration, and protect approved work.

## Rejected Alternatives

- Editing approved geometry without snapshots.
- Depending only on Blender Undo.
- Auto-applying when leaving Step 3.
- Auto-approving when the curve closes.
- Keeping permanent preview duplicates.

## Consequences

Point serialization, exact state restoration, modal lifecycle handling, and dedicated Reset, Cancel, Apply, and navigation verification are required.

## Acceptance Confirmation

Accepted after successful v0.0.4 implementation and local verification.
