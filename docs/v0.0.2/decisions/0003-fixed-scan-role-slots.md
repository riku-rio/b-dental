# Decision 0003: Use Fixed Dental Scan Role Slots

## Metadata

- **Version:** v0.0.2
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0002-scan-import-workflow.md`](../plans/0002-scan-import-workflow.md)

## Context

B-Dental must support importing either one scan or a common multi-scan set. Generic STL import provides files and objects but does not identify their dental purpose. The workflow needs deterministic role assignment for upper jaw, lower jaw, right bite, and left bite.

A generic list of imported files would make validation and later dental operations ambiguous. Automatic filename or geometry classification is not reliable enough to be authoritative in this milestone.

## Decision

B-Dental will use four fixed role slots:

- Upper Jaw.
- Lower Jaw.
- Right Bite.
- Left Bite.

The user will choose one of three scan configurations:

- `Single Arch`: upper jaw or lower jaw is required.
- `Dual Arch`: upper jaw and lower jaw are required.
- `Full Scan Set`: upper jaw, lower jaw, right bite, and left bite are required.

Each displayed role slot will own its import, replace, remove, focus, and visibility actions. Every populated slot will point to one Blender mesh object and that object will be tagged with matching B-Dental role metadata.

## Rationale

Fixed slots:

- Match the known workflow requirements.
- Make missing scans immediately visible.
- Make validation rules simple and deterministic.
- Prevent duplicate or ambiguous assignments.
- Create stable inputs for later alignment and dental processing steps.
- Fit the existing sidebar without requiring a complex collection editor.

## Alternatives Considered

### Generic Collection of Imported Scans

A collection supports arbitrary file counts but does not communicate required dental roles clearly and complicates validation.

**Decision:** Rejected for v0.0.2.

### Multi-File Import with Automatic Filename Assignment

This could improve speed, but scanner naming conventions vary and filename inference can be wrong.

**Decision:** Deferred as a convenience feature. Suggestions may be added later but must require user confirmation.

### Geometry-Based Automatic Classification

Classifying arches and bite scans from geometry is outside this milestone and would require substantially more domain logic and testing.

**Decision:** Deferred.

### Require All Four Scans in Every Case

This is simple but excludes legitimate single-arch and dual-arch cases.

**Decision:** Rejected.

## Consequences

### Positive

- The interface and validation are predictable.
- Later steps can refer to stable role names.
- Single and multiple scan workflows use one model.
- Object pointers can remain simple scene properties.

### Limitations

- Arbitrary additional scans are not represented.
- Repeated scans for the same role are not retained as history.
- Batch import is not included in this milestone.

## Implementation Constraints

- A slot may point to at most one object.
- One object may not occupy more than one slot.
- Managed objects must carry role metadata matching their assigned slot.
- Changing configuration or role assignment invalidates Step 1 validation.
- Hidden optional slots must not become required accidentally.
- Replacing a slot must be transactional.

## Revisit Conditions

Revisit this decision when:

- The workflow supports scan history or alternatives.
- Additional dental scan roles are introduced.
- Bulk import and assignment become a priority.
- Geometry classification is implemented and validated.
