# Decision 0003: Keep the Upper Jaw Fixed and Use Reversible Alignment Sessions

## Metadata

- **Version:** v0.0.3
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-occlusion-registration-verification.md`](../plans/0001-occlusion-registration-verification.md)

## Context

Occlusion registration modifies object transforms. Without a fixed reference and reliable rollback, repeated attempts can accumulate drift or leave a case in an unknown state after cancellation or failure.

## Decision

- The upper jaw is the fixed world-space reference for Step 2.
- Automatic arch registration moves only the lower jaw.
- Bite objects may move temporarily as registration references.
- Every alignment attempt runs inside an explicit reversible session.

A session:

1. Copies relevant world matrices at start.
2. Preserves the upper-jaw matrix.
3. Allows preview transforms.
4. Supports `Reset Preview`.
5. Supports `Cancel Alignment` with exact restoration.
6. Supports `Apply Candidate` without approving the occlusion.
7. Restores safe matrices after exceptions or failed registration.

Registration changes object matrices only. It does not modify mesh vertices or topology.

## Rationale

This creates a stable coordinate reference, prevents cumulative drift, makes automatic and manual attempts reversible, separates preview from approval, preserves mesh data, and makes failures recoverable.

## Rejected Alternatives

- **Move both jaws toward a midpoint:** rejected because it changes the reference coordinate system.
- **Apply transforms immediately:** rejected because cancellation and recovery become unreliable.
- **Duplicate every mesh for preview:** rejected because copied matrices provide a lighter transaction model.
- **Edit vertex coordinates:** rejected because it is destructive and unnecessary for rigid registration.

## Consequences

- Behavior is repeatable and reversible.
- The moving transform has clear ownership.
- Persistence and invalidation checks are simpler.
- The lower jaw remains the moving arch throughout v0.0.3.

## Implementation Confirmation

The accepted v0.0.3 implementation copies matrix snapshots, preserves the upper jaw, restores exact session-start matrices on reset or cancel, rolls back failed registration, and keeps candidate application separate from approval.
