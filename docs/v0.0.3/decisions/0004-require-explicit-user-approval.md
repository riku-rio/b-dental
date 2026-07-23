# Decision 0004: Require Explicit User Approval and Treat Metrics as Engineering Aids

## Metadata

- **Version:** v0.0.3
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-occlusion-registration-verification.md`](../plans/0001-occlusion-registration-verification.md)

## Context

Low registration error, visual fit, or successful operator execution does not prove that a maxillomandibular relationship is clinically correct. Scanner acquisition, bite capture, noise, and local registration minima can produce plausible but incorrect results.

## Decision

Step 2 completion requires explicit user approval.

The following are not sufficient by themselves:

- Blender operator success.
- ICP convergence.
- Low RMSE.
- High inlier ratio.
- Visual plausibility.
- Candidate application.

Before approval, B-Dental must:

- Run required engineering checks.
- Display blocking errors and non-blocking warnings.
- Require acknowledgment of warnings when present.
- Require confirmation that the result was visually reviewed.

Only explicit occlusion approval or confirmed Single Arch not-applicable completion may set `step_2_valid = true`.

Metrics are engineering aids and are not clinical validation.

## Rationale

This avoids false clinical claims, keeps final review responsibility explicit, separates computation from workflow approval, and creates a persistent audit state in the `.blend` file.

## Rejected Alternatives

- **Auto-approve below an RMSE threshold:** rejected because low error can still describe a wrong local registration.
- **Treat candidate application as approval:** rejected because applying a transform does not confirm review.
- **Block every warning:** rejected because common scan artifacts may be non-blocking.
- **Provide no metrics:** rejected because users need objective engineering feedback.

## Consequences

- Completion semantics are explicit.
- Warnings remain visible and actionable.
- Approval depends on human review.
- The extension does not guarantee clinical correctness.

## Implementation Confirmation

The accepted v0.0.3 implementation keeps operator state, candidate state, and verified state separate; requires review confirmation and warning acknowledgment; records method and summary; and invalidates approval after material input or transform changes.
