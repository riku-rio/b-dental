# Decision 0005: Require Explicit Margin Validation and Approval

## Metadata

- **Version:** v0.0.4
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Context

A closed curve or defined antagonist marker can still be incomplete, detached, structurally invalid, associated with the wrong restoration, or clinically inappropriate. Operator success and engineering diagnostics cannot establish clinical correctness.

## Decision

- Candidate creation and application never approve a restoration.
- Validation reports separate blocking errors and non-blocking warnings.
- Margin ownership, structure, coordinates, closure, point count, target association, and surface distance are approval preconditions.
- When an opposing arch exists, a valid reviewed antagonist region is also an approval precondition.
- Warnings require explicit acknowledgment.
- Approval requires explicit visual review.
- Only the explicit approval action sets a restoration to `VERIFIED`.
- Approval stores margin, target, upstream, and antagonist-region signatures.
- Aggregate `step_3_valid` becomes true only when every restoration is verified.
- Diagnostics remain engineering aids and do not certify clinical correctness.

## Rationale

Separating candidate, validation, review, and approval prevents false confidence and gives later workflow stages a stable verified contract.

## Rejected Alternatives

- Automatic approval after curve closure.
- Automatic approval after numerical checks.
- Treating every diagnostic as blocking.
- Displaying warnings without acknowledgment.
- Storing only current mutable geometry as proof of approval.

## Consequences

Review state and signatures must be persistent, material changes must clear approval, and downstream stages may depend on `step_3_valid` rather than artifact presence alone.

## Acceptance Confirmation

Accepted after successful v0.0.4 implementation and local verification.
