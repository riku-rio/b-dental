# Decision 0001: Store the Insertion Axis as a Target-Local Unit Vector

## Metadata

- **Version:** v0.0.5
- **Status:** Accepted and Implemented
- **Verification:** Passed locally
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-preparation-analysis-insertion-axis.md`](../plans/0001-preparation-analysis-insertion-axis.md)

## Context

Step 4 requires a durable insertion direction that remains associated with the preparation scan, survives save and reopen, supports independent restorations, and can be compared reliably for invalidation and downstream design.

World-space vectors would change meaning when the preparation scan is transformed. Relying only on a Blender object's rotation would make workflow state dependent on an editable scene artifact.

## Decision

- Store one authoritative `insertion_axis_local` per restoration.
- Store it in the preparation scan's local coordinate system.
- Require the vector to be finite, non-zero, and normalized.
- Define the vector as the seating direction from the occlusal/source side toward the preparation.
- Define the removal direction as the negative of the stored vector.
- Use a managed axis object only for interaction and display.
- Align the managed object's local positive Z direction with the stored insertion axis.
- Convert between local and world direction using rotation-only transform behavior and renormalize after conversion.
- Store approved vector and dependency signatures for invalidation.

## Rationale

A normalized target-local vector is compact, deterministic, serializable, independent of object naming, stable under target transforms, and suitable for undercut analysis and future crown-bottom construction.

## Rejected Alternatives

- **World-space vector:** rejected because target transforms would detach the direction from the preparation.
- **Managed object rotation as the only source of truth:** rejected because the object may be edited, deleted, or corrupted independently of workflow state.
- **Euler angles as authoritative state:** rejected because rotation order and equivalent angle representations complicate comparison and persistence.
- **Quaternion as the only state:** rejected because Step 4 requires a direction, not a complete roll orientation.
- **Unnormalized vector:** rejected because magnitude has no meaning and would complicate validation and comparison.

## Consequences

- Direction conversion helpers are required.
- Every material change must renormalize and validate the vector.
- Axis-object recovery reconstructs orientation from stored state.
- Approval signatures include the normalized vector.
- Future stages may consume the axis without depending on the viewport artifact.

## Implementation and Verification Record

Implemented in `axis_geometry.py`, `step_four_session.py`, and `step_four_validation.py`.

Local verification confirmed finite normalized storage, current-view conversion, managed-object positive-Z alignment, persistence, pointer recovery, stale-state invalidation, and independent per-restoration approval. World-space undercut analysis consumes a converted copy of the target-local axis without changing the authoritative representation.
