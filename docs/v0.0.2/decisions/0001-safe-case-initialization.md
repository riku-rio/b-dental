# Decision 0001: Use Explicit and Safe Case Initialization

## Metadata

- **Version:** v0.0.2
- **Status:** Accepted and Implemented
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-scan-import-workflow.md`](../plans/0001-scan-import-workflow.md)

## Context

A normal Blender startup scene contains a default cube, camera, and light. The cube is irrelevant to the dental workflow, but deleting objects automatically during extension registration would be unsafe in existing projects.

## Decision

B-Dental uses an explicit `Start New Dental Case` action. Registration and enablement do not modify the scene.

Starting a case:

1. Initializes workflow state.
2. Creates or reuses `B-Dental Scans`.
3. Detects an untouched startup cube conservatively.
4. Removes only that accepted cube.
5. Preserves cameras, lights, modified cubes, and unrelated objects.
6. Activates Step 1.

Detection uses multiple properties rather than name alone, including object type, default transform, and primitive cube mesh characteristics.

Removal uses direct Blender data operations instead of selection-dependent global deletion.

Resetting a case requires confirmation when managed scans or assignments would be destroyed.

## Rejected Alternatives

- Delete `Cube` during `register()`.
- Delete any object named `Cube`.
- Delete all scene objects.
- Never remove the default cube.
- Introduce a Blender Application Template in this version.

## Implementation Result

The decision was implemented in `scene_utils.py` and `operators.py`.

Local verification confirmed:

- Registration has no destructive side effects.
- An untouched startup cube is removed after explicit case start.
- Modified cubes remain untouched.
- Cameras, lights, and unrelated objects remain untouched.
- Destructive reset requires confirmation.

## Consequences

- Existing work is protected.
- Case initialization remains explicit and testable.
- Future initialization behavior can extend the same operator.
- Customized startup scenes without the expected cube remain valid and simply skip removal.

## Completion Record

This decision is accepted, implemented, and locally verified for `v0.0.2`.
