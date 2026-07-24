# Decision 0002: Use Permanent FDI Tooth Identifiers

## Metadata

- **Version:** v0.0.4
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

The restoration requires a durable tooth identity. Human-readable labels alone are ambiguous across notation systems, and Blender object names are not a suitable clinical-domain identifier. Supporting multiple notation systems in the first implementation would add conversion and validation complexity without improving the core manual-margin workflow.

## Decision

- B-Dental uses canonical FDI two-digit identifiers for v0.0.4.
- Only permanent dentition is supported.
- Upper arch values are `11` through `18` and `21` through `28`.
- Lower arch values are `31` through `38` and `41` through `48`.
- The UI filters tooth options by the selected target arch.
- Invalid arch-to-tooth combinations are rejected even if introduced through stale or scripted state.
- The canonical FDI identifier is stored in workflow state and managed artifact metadata.

## Rationale

FDI identifiers are concise, deterministic, serializable, and naturally encode arch and quadrant. A single canonical representation simplifies persistence, artifact ownership, validation, and future migration.

## Rejected Alternatives

- Store only a free-text tooth label.
- Use Blender object names as tooth identity.
- Support FDI, Universal, and Palmer simultaneously.
- Infer the tooth number from click location.
- Include primary dentition in v0.0.4.

## Consequences

Users working in another notation system must select the equivalent FDI tooth. The MVP trusts the user to choose the correct FDI tooth; automatic tooth-number verification remains outside scope.

## Acceptance Confirmation

Accepted after successful v0.0.4 implementation and local verification.
