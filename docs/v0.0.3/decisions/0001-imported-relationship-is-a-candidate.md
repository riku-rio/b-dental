# Decision 0001: Treat Imported Jaw Relationships as Unverified Candidates

## Metadata

- **Version:** v0.0.3
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-occlusion-registration-verification.md`](../plans/0001-occlusion-registration-verification.md)

## Context

Upper and lower STL files may already share a scanner-generated coordinate system. The relationship may be useful, but visual plausibility does not prove that the occlusion is correct.

Automatically moving every imported case could degrade a good scanner-exported relationship. Automatically approving the imported relationship would create false confidence.

## Decision

- Entering Step 2 does not modify object transforms.
- The imported relationship begins as an unverified candidate.
- Analysis is initiated explicitly by the user.
- Analysis may classify the relationship as `IMPORTED_CANDIDATE`, `NEEDS_ALIGNMENT`, or `ERROR`.
- Analysis alone never sets `step_2_valid = true`.
- A plausible imported candidate may proceed to verification and explicit approval without automatic realignment.

## Rationale

This approach preserves scanner-exported relationships, avoids unnecessary transforms, separates plausibility from approval, supports cases with or without bite scans, and keeps user intent explicit.

## Rejected Alternatives

- **Automatically accept imported alignment:** rejected because imported relationships can be wrong.
- **Automatically re-register every case:** rejected because local registration can degrade a good relationship.
- **Require bite scans for every dual-arch case:** rejected because useful imported articulation may exist without bite STL files.

## Consequences

- Step 2 is non-destructive on entry.
- Good imported relationships can be retained.
- Poor relationships can be corrected.
- The user must still inspect and approve the result.
- Metrics remain engineering aids rather than clinical proof.

## Implementation Confirmation

The accepted v0.0.3 implementation follows this decision. Imported analysis preserves matrices, produces candidate or needs-alignment states, and keeps approval as a separate explicit action.
