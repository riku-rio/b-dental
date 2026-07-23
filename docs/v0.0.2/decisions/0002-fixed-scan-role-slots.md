# Decision 0002: Use Fixed Dental Scan Role Slots

## Metadata

- **Version:** v0.0.2
- **Status:** Accepted and Implemented
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-scan-import-workflow.md`](../plans/0001-scan-import-workflow.md)

## Decision

B-Dental uses four fixed role slots:

- Upper Jaw.
- Lower Jaw.
- Right Bite.
- Left Bite.

Supported configurations:

- `Single Arch`: upper or lower jaw.
- `Dual Arch`: upper and lower jaw.
- `Full Scan Set`: upper jaw, lower jaw, right bite, and left bite.

Each slot owns its import, replace, remove, focus, and visibility actions. Every populated slot points to one Blender mesh object carrying matching B-Dental role metadata.

## Rationale

Fixed roles make missing scans visible, keep validation deterministic, prevent ambiguous assignments, and provide stable inputs for later dental workflow stages.

## Rejected or Deferred Alternatives

- Generic imported-scan collections.
- Automatic filename assignment without confirmation.
- Geometry-based role classification.
- Requiring all four scans in every case.
- Bulk assignment UI.

## Implementation Result

The decision was implemented in `properties.py`, `scene_utils.py`, `operators.py`, `validation.py`, and `ui.py`.

Local verification confirmed:

- Each configuration displays and requires the correct roles.
- A slot contains at most one object.
- One object cannot occupy multiple roles.
- Managed metadata matches the assigned role.
- Replacement is transactional.
- Configuration changes invalidate prior Step 1 success.

## Completion Record

This decision is accepted, implemented, and locally verified for `v0.0.2`.
