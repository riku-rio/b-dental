# Decision 0003: Keep the Upper Jaw Fixed and Use Reversible Alignment Sessions

## Metadata

- **Version:** v0.0.3
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-occlusion-registration-verification.md`](../plans/0001-occlusion-registration-verification.md)

## Context

Occlusion registration modifies object transforms. Without a fixed reference and reliable rollback, repeated attempts can accumulate drift or leave a case in an unknown state after cancellation or failure.

The workflow needs a deterministic reference convention and transactional behavior.

## Decision

The upper jaw will be the fixed world-space reference for Step 2.

Automatic arch registration will move only the lower jaw. Bite objects may move temporarily as registration references.

Every alignment attempt will run inside an explicit session that:

1. Copies relevant world matrices at session start.
2. Preserves the upper-jaw matrix.
3. Allows preview transforms.
4. Supports `Reset Preview`.
5. Supports `Cancel Alignment` with exact restoration.
6. Supports `Apply Candidate` without approving the occlusion.
7. Restores the last safe matrices after exceptions or failed registration.

Registration will change object matrices only. It will not modify mesh vertices or topology.

## Rationale

This approach:

- Creates a stable coordinate reference.
- Prevents cumulative transform drift.
- Makes automatic and manual attempts reversible.
- Separates preview, application, and approval.
- Preserves imported mesh data.
- Makes failures recoverable.

## Alternatives Considered

### Move Both Jaws Toward a Midpoint

Rejected because it changes the reference coordinate system and complicates downstream workflows.

### Apply Transform Immediately Without a Session

Rejected because failure and cancellation would be difficult to recover from reliably.

### Duplicate Every Mesh for Preview

Rejected for this milestone because matrix snapshots provide a lighter and clearer transaction model.

### Edit Vertex Coordinates

Rejected because it is destructive and unnecessary for rigid registration.

## Consequences

### Positive

- Repeatable and reversible behavior.
- Clear ownership of the moving transform.
- Easier persistence and invalidation checks.
- Mesh data remains unchanged.

### Limitations

- The lower jaw must be considered the moving arch throughout this version.
- Future workflows using another reference convention will need an explicit migration or new mode.
- External user edits during an active session must be handled carefully.

## Implementation Constraints

- Copy matrices, never keep mutable references as snapshots.
- Validate finite matrices before starting.
- Reject non-rigid scale or shear changes outside tolerance.
- Keep the upper jaw fixed within tolerance.
- Restore matrices in exception handlers.
- Do not silently leave an active preview when navigating away.
- Candidate application must not set `step_2_valid`.

## Revisit Conditions

Revisit when the product introduces articulators, facebow coordinates, skull references, or workflows where another object must define the fixed coordinate frame.
