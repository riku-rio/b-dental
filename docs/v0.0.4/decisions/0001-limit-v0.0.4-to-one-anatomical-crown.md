# Decision 0001: Limit v0.0.4 to One Anatomical Crown

## Metadata

- **Version:** v0.0.4
- **Status:** Superseded
- **Superseded by:** [`0006-support-multiple-independent-restorations.md`](0006-support-multiple-independent-restorations.md)
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-restoration-setup-manual-margin-definition.md`](../plans/0001-restoration-setup-manual-margin-definition.md)

## Original Context

The earliest v0.0.4 design limited a case to one anatomical crown so the first manual-margin implementation could avoid collection ownership, selection, and independent approval concerns.

## Original Decision

The initial implementation exposed one active restoration and one managed margin per case.

## Supersession

Hands-on verification showed that replacing the active restoration prevents a normal case from retaining margins for multiple prepared teeth and prevents a dual-arch case from keeping both upper and lower restorations.

The product requirement has therefore changed. Version v0.0.4 now supports multiple independent single-unit anatomical crown restorations in one B-Dental case. Each restoration owns its own target arch, FDI tooth, margin, diagnostics, session state, and approval.

This record remains in the repository to preserve the design history. It is no longer authoritative for implementation.
