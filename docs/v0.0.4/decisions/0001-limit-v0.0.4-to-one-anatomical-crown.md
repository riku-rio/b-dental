# Decision 0001: Limit v0.0.4 to One Anatomical Crown

## Metadata

- **Version:** v0.0.4
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

A manual margin needs a restoration identity, target preparation scan, and target tooth. Supporting multiple restorations or multiple restoration types in the first Step 3 implementation would multiply ownership, selection, invalidation, UI, persistence, and cleanup paths before the core margin workflow has been verified.

## Decision

- Version `v0.0.4` supports zero or one active restoration per case.
- The only supported restoration type is `ANATOMICAL_CROWN`.
- The restoration is single-unit.
- A stable restoration ID associates workflow state and managed artifacts.
- Creating, resetting, or retargeting the restoration is explicit.
- Existing managed margin geometry requires confirmation before destructive setup changes.
- Multi-restoration and additional restoration types remain out of scope.

## Rationale

This creates the smallest useful restoration model while preserving a clear identity boundary for the margin. It allows Step 3 safety, persistence, editing, and invalidation behavior to be tested without prematurely committing to bridge or multi-unit architecture.

## Rejected Alternatives

- **Draw a margin without creating a restoration:** rejected because ownership and future downstream use would be ambiguous.
- **Support an arbitrary list of restorations immediately:** rejected because it greatly increases state and cleanup complexity.
- **Support every restoration type with the same margin UI:** rejected because different indications require different downstream rules and not all use the same design workflow.
- **Infer the restoration from the selected Blender object:** rejected because transient Blender selection is not durable workflow state.

## Consequences

- The Step 3 UI remains focused.
- One margin can be resolved deterministically.
- Setup changes can remove only the active restoration's margin.
- Later multi-restoration support will require a deliberate migration from scalar state to a collection model.
- The stable restoration ID must be persisted and included in artifact metadata.

## Acceptance Confirmation

This decision becomes accepted when the v0.0.4 documentation set is approved. Implementation must not expose unfinished multi-unit or multi-type behavior.
