# Decision 0003: Use Scene-Persistent Workflow State and Conditional Panel Navigation

## Metadata

- **Version:** v0.0.2
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0002-scan-import-workflow.md`](../plans/0001-scan-import-workflow.md)
- **Supersedes:** Nothing
- **Extends:** [`../../v0.0.1/decisions/0001-use-3d-viewport-sidebar-panel.md`](../../v0.0.1/decisions/0001-use-3d-viewport-sidebar-panel.md)

## Context

Version `v0.0.2` introduces multiple workflow stages, scan assignments, validation results, and navigation. This state must remain available while the user works, survive saving and reopening the `.blend` file, and drive what the B-Dental panel displays.

Operator-local variables are temporary. Module globals are not reliable across file loading, extension reloads, or multiple Blender scenes. Opening a new operating-system window or replacing the user's workspace is unnecessary for a two-step milestone.

## Decision

B-Dental will define a custom Blender `PropertyGroup` and attach one pointer property to `bpy.types.Scene`.

The scene state will include at least:

- Current workflow step.
- Step 1 status.
- Step 1 validation boolean.
- Scan configuration.
- Single-arch role selection.
- Source units.
- Object pointers for upper jaw, lower jaw, right bite, and left bite.
- User-facing validation summary or messages.

The existing 3D Viewport sidebar panel will draw different content according to `current_step`:

- `STEP_1`: case initialization, scan configuration, scan slots, and validation.
- `STEP_2`: Step 1 completion state, `Not Implemented Yet.`, and `Back to Step 1`.

Successful B-Dental validation will set `step_1_valid = true` and change `current_step` to `STEP_2`. Blender operator return values remain separate and use Blender's expected result sets such as `{'FINISHED'}` or `{'CANCELLED'}`.

## Rationale

Scene-persistent state:

- Is saved naturally with the `.blend` case.
- Supports future case-specific workflow stages.
- Allows object pointers to remain associated with the scene.
- Avoids fragile module-global state.
- Lets the existing panel evolve without premature workspace architecture.
- Separates application success from operator execution success.

## Alternatives Considered

### Module-Level Global Variables

Globals are easy to implement but are not reliably saved, can become stale after reload, and do not model multiple scenes correctly.

**Decision:** Rejected.

### Window Manager Properties

Window-manager state is useful for temporary session UI but is not the correct primary home for saved case data.

**Decision:** Rejected for persistent workflow state.

### Object-Only Custom Properties

Managed objects will carry role metadata, but object properties alone do not represent workflow step, configuration, or missing slots.

**Decision:** Used only as complementary metadata.

### Separate Blender Workspace

A dedicated workspace offers more room but introduces layout and lifecycle complexity before the workflow requires it.

**Decision:** Deferred.

### Popup or Separate Window per Step

Temporary windows make navigation and persistence harder and separate the controls from the scene context.

**Decision:** Rejected.

## Consequences

### Positive

- Workflow state survives save and reopen.
- UI navigation is deterministic.
- Later steps can extend the same property group.
- Imported object assignments remain explicit.

### Limitations

- Scene-level state means each Blender scene may hold a separate B-Dental workflow.
- Pointer properties can become empty when users delete objects externally.
- Schema changes in future versions may require migration logic.

## Implementation Constraints

- Registration must attach the pointer property only after registering its type.
- Unregistration must delete the pointer property before unregistering its type.
- UI drawing must tolerate missing and stale object pointers.
- Any material Step 1 change must invalidate previous validation.
- Step 2 must not be reachable through normal controls unless validation succeeds.
- Returning to Step 1 must not clear valid scan assignments.
- Application status and Blender operator status must never be conflated.

## Revisit Conditions

Revisit this decision when:

- B-Dental supports multiple cases inside one `.blend` file.
- Case data requires a dedicated Blender data-block or external project format.
- Workflow schema migration becomes necessary.
- The sidebar no longer provides sufficient space for the number of workflow stages.
