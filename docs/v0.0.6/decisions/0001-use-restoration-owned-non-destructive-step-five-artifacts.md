# Decision 0001: Use Restoration-Owned Non-Destructive Step 5 Artifacts

## Metadata

- **Version:** v0.0.6
- **Status:** Accepted for implementation
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-automated-preparation-die-crown-bottom.md`](../plans/0001-automated-preparation-die-crown-bottom.md)

## Context

Step 5 generates multiple meshes from authoritative scans, margins, and insertion-axis state. Directly editing the imported scan or relying on loosely named scene objects would make rollback, invalidation, multiple restorations, and save/reopen recovery unsafe.

## Decision

- Create separate managed preparation-die, blocked-die, and crown-bottom candidate objects.
- Assign every artifact to exactly one restoration through stable restoration ID, artifact type, schema version, and generation signature metadata.
- Keep imported scans and approved upstream artifacts unchanged.
- Store persistent object pointers, but treat ownership metadata and generated signatures as the recovery and integrity contract.
- Keep an existing approved candidate authoritative until a replacement candidate is explicitly approved.
- Remove artifacts only within the owning restoration or confirmed case reset.

## Rationale

Restoration-owned non-destructive artifacts provide safe rollback, scoped invalidation, independent multi-restoration workflows, explicit cleanup, reproducible approval, and protection of source data.

## Rejected Alternatives

- **Modify the scan in place:** rejected because source geometry must remain authoritative and reusable.
- **Use duplicate objects without ownership metadata:** rejected because pointer loss or renaming would make recovery ambiguous.
- **Use one shared Step 5 object for all restorations:** rejected because state, invalidation, visibility, and cleanup must remain independent.
- **Replace approved geometry immediately on regeneration:** rejected because failed or rejected generation must not destroy the current approved result.

## Consequences

- Artifact creation and deletion must be transactional.
- Pointer recovery and duplicate-artifact detection are required.
- Generated geometry must carry stable signatures.
- Direct unmanaged edits must invalidate the owning candidate safely.
- Reset and restoration removal logic must include all Step 5 artifact types.