# Decision 0001: Treat Imported Jaw Relationships as Unverified Candidates

## Metadata

- **Version:** v0.0.3
- **Status:** Proposed
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-occlusion-registration-verification.md`](../plans/0001-occlusion-registration-verification.md)

## Context

Upper and lower STL files may already share a scanner-generated coordinate system. In many cases they appear nearly articulated immediately after import. That relationship may be useful, but visual plausibility alone does not prove that the occlusion is correct.

Automatically moving every imported case would damage cases that are already positioned well. Automatically approving every imported case would create false confidence.

## Decision

Entering Step 2 will not modify any object transform.

The imported upper-to-lower relationship will begin as an unverified candidate. The user must run analysis explicitly.

Analysis may classify the relationship as:

- `IMPORTED_CANDIDATE`
- `NEEDS_ALIGNMENT`
- `ERROR`

Analysis alone may never set `step_2_valid = true`.

A plausible imported candidate may proceed directly to verification and explicit approval without automatic realignment.

## Rationale

This approach:

- Preserves scanner-exported relationships.
- Avoids unnecessary transforms.
- Separates plausibility from verification.
- Supports cases with and without bite scans.
- Keeps user intent explicit.
- Avoids claiming clinical certainty from appearance alone.

## Alternatives Considered

### Automatically Accept Imported Alignment

Rejected because scanner exports and bite registrations can contain errors.

### Automatically Re-register Every Case

Rejected because local registration can degrade an already correct relationship and may converge to an incorrect local minimum.

### Require Bite Scans for Every Dual-Arch Case

Rejected because some valid scanner exports preserve articulation while some workflows do not provide bite STL files.

## Consequences

### Positive

- Step 2 is non-destructive on entry.
- Good imported relationships can be retained.
- Poor relationships can be corrected.
- Approval remains explicit.

### Limitations

- Imported analysis cannot prove clinical correctness.
- The user must still inspect the result.
- Some cases require manual or bite-guided correction.

## Implementation Constraints

- No transforms during Step 2 entry.
- No automatic approval.
- Analysis results must be structured and persistent.
- Metrics must be labeled as engineering aids.
- Approval requires a separate action.

## Revisit Conditions

Revisit this decision only if a future version introduces validated scanner metadata, trusted registration provenance, or a clinically governed approval workflow.
