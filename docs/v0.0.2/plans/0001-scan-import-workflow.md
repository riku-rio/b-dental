# Plan 0002: Scan Import Workflow

## Metadata

- **Version:** v0.0.2
- **Status:** Proposed
- **Target implementation branch:** `feat/v0.0.2-scan-import-workflow`
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related tasks:** [`../TASKS.md`](../TASKS.md)
- **Related decisions:**
  - [`../decisions/0001-safe-case-initialization.md`](../decisions/0001-safe-case-initialization.md)
  - [`../decisions/0002-fixed-scan-role-slots.md`](../decisions/0002-fixed-scan-role-slots.md)
  - [`../decisions/0003-scene-persistent-workflow-state.md`](../decisions/0003-scene-persistent-workflow-state.md)

## Objective

Implement the first usable B-Dental workflow stage while preserving the reliable extension foundation established in `v0.0.1`.

The completed milestone will let a user explicitly initialize a dental case, import required intra-oral STL scans into known dental roles, validate the case, and advance to a placeholder Step 2.

## Current State

The repository currently contains:

- A valid modern Blender Extension package.
- A `B-Dental` panel in the 3D Viewport sidebar.
- A single Python module containing registration and panel drawing.
- Placeholder content reading `Not Implemented Yet.`
- No operators, workflow state, scene processing, imported-object tracking, or validation logic.

## Planned Repository Structure

```text
b-dental/
├── docs/
│   ├── v0.0.1/
│   └── v0.0.2/
│       ├── PRD.md
│       ├── TASKS.md
│       ├── VERIFICATION.md
│       ├── decisions/
│       │   ├── 0002-safe-case-initialization.md
│       │   ├── 0003-fixed-scan-role-slots.md
│       │   └── 0004-scene-persistent-workflow-state.md
│       └── plans/
│           └── 0002-scan-import-workflow.md
└── extension/
    ├── __init__.py
    ├── blender_manifest.toml
    ├── operators.py
    ├── properties.py
    ├── scene_utils.py
    ├── ui.py
    └── validation.py
```

## Architecture

### Registration Layer

`extension/__init__.py` will remain small and deterministic. It will import the focused modules and orchestrate registration and unregistration in a fixed order.

Recommended registration order:

1. Property-group classes.
2. Operator classes.
3. Panel classes.
4. Scene pointer property.

Unregistration must reverse that order and remove the scene pointer property before unregistering its type.

### State Layer

`properties.py` will define:

- Current workflow step.
- Step 1 status.
- Step 1 validity.
- Scan configuration.
- Single-arch selected role.
- Source units.
- Object pointers for the four fixed scan roles.
- User-facing validation summary.

### Scene Utility Layer

`scene_utils.py` will implement narrow, reusable helpers for:

- Detecting an untouched startup cube.
- Removing that cube directly without selection-dependent deletion.
- Creating or finding the `B-Dental Scans` collection.
- Linking and unlinking managed objects safely.
- Applying and reading B-Dental custom metadata.
- Resolving role-to-pointer and role-to-name mappings.

### Operator Layer

`operators.py` will implement explicit user actions:

- Start or reset case.
- Import scan for a role.
- Replace scan.
- Remove scan.
- Focus scan.
- Validate Step 1.
- Return to Step 1.

The import operator will own the Blender file browser interaction and call `bpy.ops.wm.stl_import` with mesh validation enabled.

### Validation Layer

`validation.py` will provide a structured validation result independent from Blender operator return values.

Blocking checks will cover:

- Required roles.
- Existing object references.
- Mesh type.
- Non-empty mesh data.
- Non-zero finite dimensions.
- Unique object assignments.
- Correct B-Dental role metadata.

Warnings may cover scale and topology concerns without blocking this milestone.

### UI Layer

`ui.py` will draw one panel whose content depends on `current_step`.

Step 1 will include:

- Workflow header.
- Start/reset action.
- Scan configuration.
- Source unit.
- Relevant fixed scan slots.
- Slot actions and imported scan summary.
- Validation feedback.
- `Validate & Continue`.

Step 2 will include:

- Step 1 completed state.
- `Not Implemented Yet.`
- `Back to Step 1`.

## Implementation Phases

### Phase 1: Documentation Approval

- Review PRD scope and terminology.
- Confirm supported scan configurations.
- Confirm default unit behavior.
- Confirm the exact definition of `step_1_valid`.
- Approve the three architectural decisions.

Exit condition: documentation status is approved and implementation may begin.

### Phase 2: Module and Registration Foundation

- Create the focused Python modules.
- Move panel code to `ui.py`.
- Define deterministic class registries.
- Update the manifest version and build paths.
- Verify the extension still validates, builds, installs, and displays before adding behavior.

Exit condition: the refactored extension behaves like `v0.0.1` without registration regressions.

### Phase 3: Persistent Workflow State

- Define enums and the scene property group.
- Attach the pointer property to `bpy.types.Scene`.
- Draw Step 1 or Step 2 from state.
- Verify save and reopen persistence.

Exit condition: step navigation and state persistence work without scan imports.

### Phase 4: Safe Case Initialization

- Implement untouched-default-cube detection.
- Implement direct narrow deletion.
- Create or reuse the scan collection.
- Initialize state through `Start New Dental Case`.
- Add destructive reset confirmation.

Exit condition: a clean startup scene is prepared while existing scenes remain safe.

### Phase 5: Scan Configuration UI

- Add the configuration enum.
- Add the single-arch selected role.
- Derive and display required slots.
- Add millimeters as default source unit.
- Invalidate prior validation when controls change.

Exit condition: the panel accurately communicates required scans for every supported configuration.

### Phase 6: STL Import and Assignment

For each scan import:

1. Record the Blender object set before import.
2. Open the STL file browser filtered to `.stl`.
3. Call Blender's built-in STL importer.
4. Record the object set after import.
5. Identify newly created objects.
6. Require exactly one assignable mesh for the selected role.
7. Move the object to `B-Dental Scans`.
8. Apply deterministic name and metadata.
9. Assign the object pointer to the role slot.
10. Invalidate prior Step 1 validation.

Replacement will be transactional: the existing assignment remains until the replacement is imported and accepted.

Exit condition: every role can be imported, replaced, removed, focused, and hidden without stale state.

### Phase 7: Validation and Navigation

- Implement the structured result model.
- Implement all blocking checks.
- Add practical non-blocking warnings.
- Display errors and warnings in the panel.
- On success, set `step_1_valid = true`, set status to `VALID`, and change to Step 2.
- On failure, remain on Step 1 with actionable errors.
- Implement `Back to Step 1` without clearing scans.

Exit condition: all supported configurations transition deterministically based on validation.

### Phase 8: Verification and Hardening

- Run the full manual scenario matrix.
- Verify undo behavior where supported.
- Verify cancellation and failed replacement.
- Verify stale pointers after external object deletion.
- Verify save/reopen persistence.
- Verify repeated enable, disable, and reload cycles.
- Inspect the packaged ZIP.
- Record actual results in `VERIFICATION.md`.

Exit condition: every acceptance criterion is recorded as passed or the milestone remains incomplete.

## UI Behavior Summary

### Initial State

The panel displays Step 1 and an explicit `Start New Dental Case` action. No scene change occurs merely because the extension is enabled.

### Active Step 1

The user selects a configuration and imports scans into role-specific slots. Validation readiness and corrective messages appear near the primary action.

### Valid Step 1

Successful validation changes the same panel to Step 2. No new Blender window is created.

### Return to Step 1

The user can return for review or replacement. Existing scans remain assigned, but any subsequent material change invalidates the previous validation success.

## Error-Handling Strategy

- File-browser cancellation returns without changing state.
- Import exceptions or cancelled Blender operations report an error and preserve existing assignments.
- Unexpected multiple imported objects are not silently assigned.
- Invalid replacement imports are cleaned up when safe and do not delete the old scan.
- Missing or externally deleted objects are reported as validation errors.
- UI drawing must tolerate empty and stale pointers without raising exceptions.

## Testing Strategy

Testing is primarily local and scenario-driven for this milestone.

Where logic is sufficiently independent from Blender context, pure helper functions should be structured to support later automated tests. The first implementation must not introduce a fake test framework that cannot reliably run Blender APIs.

Manual testing will cover:

- Clean startup scene.
- Existing scene safety.
- Each scan configuration.
- Cancellation and failure paths.
- Persistence.
- Registration lifecycle.

## Risks and Mitigations

### Destructive Scene Changes

Mitigation: perform no deletion at registration, require explicit case start, and detect the startup cube using multiple characteristics rather than name alone.

### Unit Ambiguity

Mitigation: expose source units and default to millimeters. Treat suspicious dimensions as warnings rather than silently rescaling after import.

### Blender Context Sensitivity

Mitigation: prefer direct data operations for object removal and collection management. Limit context-dependent actions to file selection, import, and viewport focus.

### Stale Object Pointers

Mitigation: validate pointers before use, tolerate externally deleted objects, and clear or report stale slot assignments.

### Premature Complex UI

Mitigation: retain one conditional sidebar panel and fixed role slots. Defer bulk import and a dedicated workspace.

### Dental Geometry Variability

Mitigation: require only basic mesh validity. Do not require watertight or manifold scans in this milestone.

## Completion Rule

Plan 0002 is complete only when:

- The documentation set is approved.
- Every required implementation task is completed.
- Every PRD acceptance criterion is verified locally.
- Actual implementation results and deviations are recorded.
- The extension package is ready for review and squash merge.
