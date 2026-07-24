# Decision 0003: Use Reversible Managed-Axis Sessions

## Metadata

- **Version:** v0.0.5
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-preparation-analysis-insertion-axis.md`](../plans/0001-preparation-analysis-insertion-axis.md)

## Context

Insertion-axis definition may involve repeated viewport capture, manual rotation, reset, cancellation, and comparison against undercut results. Editing an approved axis directly would risk losing the last accepted state and would make restoration switching and save/reopen behavior ambiguous.

Blender Undo alone is not sufficient because workflow status, analysis metrics, approval signatures, and managed-artifact ownership must be restored together.

## Decision

- Axis creation and manual modification occur inside an explicit reversible session.
- Session start snapshots the active restoration's axis vector, source, managed-axis transform, analysis settings, analysis results, diagnostics, review state, warning acknowledgment, approval state, and signatures.
- Reset restores the exact session-start axis and state while keeping the session active.
- Cancel restores the exact session-start Step 4 state and closes the session.
- If no axis artifact existed at session start, Cancel removes the draft artifact.
- Capture converts the managed object's local positive Z direction into a target-local candidate.
- Apply preserves the candidate, closes the session, clears stale analysis and approval, and does not approve Step 4.
- Restoration switching and navigation away from Step 4 are blocked while a session is active.
- Sessions affect only the active restoration.

## Rationale

A snapshot-based session model follows the safety contracts already established in Steps 2 and 3. It protects approved work, keeps user intent explicit, and makes rollback deterministic and testable.

## Rejected Alternatives

- **Edit approved axis directly:** rejected because cancellation cannot reliably restore the accepted state.
- **Depend only on Blender Undo:** rejected because workflow and approval state extend beyond object transforms.
- **Auto-apply when leaving Step 4:** rejected because navigation must not silently accept a candidate.
- **Auto-run analysis after every rotation event:** rejected because it may be expensive and obscures when a result becomes authoritative.
- **Duplicate permanent axis objects for every candidate:** rejected because ownership and cleanup would become error-prone.

## Consequences

- Per-restoration session snapshots are required.
- Axis operators must share one session contract.
- Applying or changing an axis clears stale analysis.
- UI must expose Start, Reset, Cancel, Capture, and Apply actions clearly.
- Verification must cover new-axis and existing-approved-axis rollback independently.