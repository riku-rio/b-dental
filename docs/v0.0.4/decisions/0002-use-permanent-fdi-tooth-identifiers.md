# Decision 0002: Use Permanent FDI Tooth Identifiers

## Metadata

- **Version:** v0.0.4
- **Status:** Proposed
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
- The canonical FDI identifier is stored in workflow state and margin metadata.

## Rationale

FDI identifiers are concise, deterministic, serializable, and naturally encode arch and quadrant. A single canonical representation simplifies persistence, artifact ownership, validation, and future migration.

## Rejected Alternatives

- **Store only a free-text tooth label:** rejected because it is not reliably validated or comparable.
- **Use Blender object names as tooth identity:** rejected because names are editable and scene-specific.
- **Support FDI, Universal, and Palmer simultaneously:** rejected because notation conversion is outside the first margin milestone.
- **Infer the tooth from click location:** rejected because automatic tooth identification is outside scope and can be wrong.
- **Include primary dentition now:** rejected to keep the first restoration model narrowly testable.

## Consequences

- Users working in another notation system must select the equivalent FDI tooth.
- Arch filtering is a required UI and validation behavior.
- Future notation preferences may display alternative labels while preserving FDI as the stored canonical identifier.
- Primary dentition requires a future explicit scope and migration decision.

## Acceptance Confirmation

This decision becomes accepted when the v0.0.4 documentation set is approved. The implementation must store the canonical identifier independently of translated or formatted UI labels.
