# Decision 0004: Require Explicit User Approval and Treat Metrics as Engineering Aids

## Metadata

- **Version:** v0.0.3
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-occlusion-registration-verification.md`](../plans/0001-occlusion-registration-verification.md)

## Context

Low registration error, apparent visual fit, or successful operator execution does not prove that a maxillomandibular relationship is clinically correct. Scanner acquisition, bite capture, surface noise, and local registration minima can all produce plausible but incorrect results.

The workflow must provide useful geometric feedback without presenting it as diagnosis or clinical certification.

## Decision

Step 2 completion will require explicit user approval.

The following are not sufficient by themselves:

- A Blender operator returning `{'FINISHED'}`.
- ICP convergence.
- Low RMSE.
- High inlier ratio.
- Visual plausibility.
- Successful candidate application.

Before approval, B-Dental must:

- Run required engineering checks.
- Display blocking errors and non-blocking warnings.
- Require acknowledgment of warnings when present.
- Require the user to confirm that the result was visually reviewed.

Only `Approve Occlusion` or confirmed Single Arch not-applicable completion may set `step_2_valid = true`.

Metrics must be described as engineering aids, not clinical validation.

## Rationale

This approach:

- Avoids false clinical claims.
- Keeps responsibility for final review explicit.
- Separates computation from workflow approval.
- Supports warnings without silently ignoring them.
- Produces a clear audit state in the `.blend` file.

## Alternatives Considered

### Auto-approve Below an RMSE Threshold

Rejected because a low error can still describe an incorrect local registration.

### Treat Candidate Application as Approval

Rejected because application only commits a transform; it does not confirm review.

### Block Every Warning

Rejected because dental scans commonly contain open boundaries and noisy peripheral geometry that may not invalidate registration.

### Provide No Metrics

Rejected because users need objective feedback to diagnose registration quality and failure modes.

## Consequences

### Positive

- Clear completion semantics.
- Safer user expectations.
- Persistent record of method and metrics.
- Warnings remain visible and actionable.

### Limitations

- Approval depends on human review.
- The extension cannot guarantee clinical correctness.
- Thresholds require testing and may evolve.

## Implementation Constraints

- Keep Blender operator status separate from `step_2_valid`.
- Keep candidate state separate from verified state.
- Record approval method and summary.
- Do not label metrics as clinical accuracy.
- Invalidate approval after material input or transform changes.
- Preserve warnings with the verified summary where practical.

## Revisit Conditions

Revisit only if the project later operates under a validated clinical quality system with formally established acceptance criteria and traceability.
