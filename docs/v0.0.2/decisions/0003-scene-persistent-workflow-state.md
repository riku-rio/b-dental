# Decision 0003: Use Scene-Persistent Workflow State and Conditional Panel Navigation

## Metadata

- **Version:** v0.0.2
- **Status:** Accepted and Implemented
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-scan-import-workflow.md`](../plans/0001-scan-import-workflow.md)
- **Extends:** [`../../v0.0.1/decisions/0001-use-3d-viewport-sidebar-panel.md`](../../v0.0.1/decisions/0001-use-3d-viewport-sidebar-panel.md)

## Decision

B-Dental stores workflow state in a custom Blender `PropertyGroup` attached to `bpy.types.Scene`.

The state includes:

- Current workflow step.
- Step 1 status.
- Step 1 validation boolean.
- Scan configuration.
- Single-arch role selection.
- Source units.
- Upper, lower, right-bite, and left-bite object pointers.
- Validation summaries, errors, and warnings.

The existing 3D Viewport sidebar panel draws content conditionally:

- `STEP_1`: case initialization, scan configuration, scan slots, and validation.
- `STEP_2`: Step 1 completion state, `Not Implemented Yet.`, and `Back to Step 1`.

Successful dental validation sets `step_1_valid = true` and changes `current_step` to `STEP_2`. Blender operator return values remain independent.

## Rationale

Scene-level state persists naturally in `.blend` files, keeps assignments associated with the scene, avoids module-global state, and supports deterministic navigation.

## Rejected or Deferred Alternatives

- Module-level globals.
- Window Manager properties as the primary store.
- Object-only custom properties.
- Separate Blender workspace.
- Popup or separate window per step.

## Implementation Result

The decision was implemented in `properties.py`, `__init__.py`, `operators.py`, and `ui.py`.

Local verification confirmed:

- State survives save, close, and reopen.
- Object pointers remain associated with the case.
- Step navigation is deterministic.
- Returning to Step 1 preserves imported scans.
- Material Step 1 changes invalidate prior validation.
- Unregistration removes the custom Scene pointer property.
- Repeated lifecycle operations do not create duplicate registrations.

## Completion Record

This decision is accepted, implemented, and locally verified for `v0.0.2`.
