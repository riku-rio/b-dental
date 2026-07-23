# Decision 0002: Use Bite Scans as Intermediate Registration References

## Metadata

- **Version:** v0.0.3
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-occlusion-registration-verification.md`](../plans/0001-occlusion-registration-verification.md)

## Context

Upper and lower arches are opposing anatomical surfaces. They should contact or maintain small clearances; they should not be superimposed. Direct nearest-neighbor registration between them can therefore pull complementary surfaces into an anatomically incorrect overlap.

Buccal bite scans contain partial surfaces from both arches in the recorded closed relationship. They can act as intermediate references because each bite overlaps with portions of the upper and lower scans.

## Decision

B-Dental will not run direct ICP between upper and lower jaw meshes.

Bite-guided registration will use this sequence:

1. Keep the upper jaw fixed.
2. Register the selected bite scan to the upper jaw.
3. Use the aligned bite as an intermediate target for the lower jaw.
4. Move only the lower jaw during final arch registration.

Supported sources:

- Right Bite.
- Left Bite.
- Both Bites.

Both Bites mode will align both bite scans to the upper jaw, refine the lower jaw against a combined bite target, and calculate independent right-only and left-only diagnostics.

## Rationale

This approach:

- Matches the role of buccal bite records.
- Avoids collapsing opposing arches onto each other.
- Supports unilateral and bilateral workflows.
- Provides consistency diagnostics when two bites are available.
- Works with noisy partial scans through robust correspondence filtering.

## Alternatives Considered

### Direct Upper-to-Lower ICP

Rejected because the surfaces are complementary rather than duplicate observations of the same surface.

### Treat Bite Scans as Final Anatomy

Rejected because bite scans are partial registration references and may contain noise, soft tissue, or floating fragments.

### Require Both Bite Scans

Rejected because some cases provide only one usable bite.

### Automatically Average Right and Left Transforms

Rejected as the only strategy because large disagreement should be visible rather than silently averaged.

## Consequences

### Positive

- Registration uses geometrically meaningful overlap.
- Bilateral disagreement can be measured.
- Bite objects remain available for inspection.

### Limitations

- Reasonable initial overlap is still required.
- Noisy bite scans may fail.
- Automatic registration cannot determine clinical correctness.

## Implementation Constraints

- Never invoke direct upper-to-lower ICP.
- Validate bite pointers and metadata.
- Use robust trimming and minimum inlier thresholds.
- Preserve bite meshes and original matrices through session snapshots.
- Fail safely when overlap is insufficient.
- Report right-versus-left disagreement.

## Revisit Conditions

Revisit when the project adds global feature registration, scanner-provided transform metadata, or a validated articulator workflow.
