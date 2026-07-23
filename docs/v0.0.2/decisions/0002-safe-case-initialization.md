# Decision 0002: Use Explicit and Safe Case Initialization

## Metadata

- **Version:** v0.0.2
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0002-scan-import-workflow.md`](../plans/0002-scan-import-workflow.md)

## Context

The first workflow step should begin with a scene prepared for dental scan import. A normal Blender startup scene contains a default cube, camera, and light. The cube is not useful to the dental workflow, but deleting objects automatically when the extension is enabled would be unsafe in existing user projects.

The implementation therefore needs a narrow rule for removing only the untouched startup cube while preserving modified cubes and all unrelated scene content.

## Decision

B-Dental will provide an explicit `Start New Dental Case` operator. Extension registration and enablement will not modify the scene.

When the user starts a new case, B-Dental will:

1. Initialize the scene workflow state.
2. Create or reuse the `B-Dental Scans` collection.
3. Detect whether an untouched Blender startup cube is present.
4. Remove only that accepted startup cube.
5. Preserve the camera, light, modified cubes, and unrelated objects.
6. Set the active workflow step to Step 1.

Startup-cube detection will use multiple properties, not object name alone. The accepted object must be a mesh named `Cube`, have the expected default transform within a small tolerance, and retain primitive cube mesh characteristics such as eight vertices and six polygons.

Removal will use a direct Blender data operation rather than selection-dependent global deletion.

Resetting an initialized B-Dental case will require confirmation when managed objects or assignments would be destroyed.

## Rationale

This approach:

- Keeps extension enablement non-destructive.
- Makes the user's intent explicit.
- Supports both clean startup scenes and existing projects.
- Avoids deleting a user-created object merely because it is named `Cube`.
- Avoids dependence on the user's current selection and active object.
- Provides a clear future location for additional case initialization behavior.

## Alternatives Considered

### Delete `Cube` During `register()`

This is simple but unsafe. Registration may occur in an existing project, during script reload, or after re-enabling the extension.

**Decision:** Rejected.

### Delete Any Object Named `Cube`

Names are user-editable and not reliable evidence that an object is the untouched startup primitive.

**Decision:** Rejected.

### Delete All Scene Objects

This creates a clean scene but is destructive and incompatible with adding B-Dental to an existing file.

**Decision:** Rejected.

### Never Remove the Default Cube

This is safe but leaves irrelevant geometry in every new case and does not satisfy the requested first action.

**Decision:** Rejected.

### Use a Blender Application Template Immediately

A dedicated application template could start with a prepared scene and no cube. It is a valid future option but introduces a separate distribution and startup workflow beyond this milestone.

**Decision:** Deferred.

## Consequences

### Positive

- Existing user work remains protected.
- New-case initialization is easy to test and undo where supported.
- Future scene defaults can be added behind the same explicit action.

### Limitations

- A cube modified only in ways not covered by the checks could be misclassified unless the detection remains conservative.
- A startup scene customized by the user may not contain the expected cube and therefore nothing will be removed.
- Direct data removal is not a substitute for a complete case reset policy.

## Implementation Constraints

- Use conservative tolerances.
- Return false when detection is uncertain.
- Never infer startup-cube identity from the name alone.
- Do not delete the camera or light.
- Do not delete unrelated objects.
- Do not run this logic during registration.
- Add a confirmation dialog before destructive case reset.

## Revisit Conditions

Revisit this decision when:

- B-Dental adopts an Application Template.
- Case initialization requires a dedicated workspace or startup file.
- The workflow gains a formal case lifecycle with open, close, duplicate, and archive operations.
