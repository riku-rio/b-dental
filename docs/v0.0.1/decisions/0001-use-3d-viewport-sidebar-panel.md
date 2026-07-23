# Decision 0001: Use a 3D Viewport Sidebar Panel

## Metadata

- **Version:** v0.0.1
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-extension-foundation.md`](../plans/0001-extension-foundation.md)

## Context

Version `v0.0.1` needs a visible and reliable entry point inside Blender. The interface must be simple to implement, easy to access, suitable for placeholder content, and capable of growing into a larger tool interface in later versions.

The first milestone does not require a complete application workspace, custom editor, multi-screen navigation system, or modal workflow.

## Decision

B-Dental will use a panel in the 3D Viewport sidebar as its initial user-interface entry point.

The first interface will use:

- **Editor:** 3D Viewport
- **Region:** Sidebar (`UI` region)
- **Category:** `B-Dental`
- **Panel label:** `B-Dental`
- **Displayed content:** `Not Implemented Yet.`

## Rationale

The 3D Viewport sidebar is appropriate for the foundation milestone because it:

- Is familiar and easily accessible to Blender users.
- Is a standard location for extension tools and controls.
- Requires a small, straightforward registration surface.
- Provides persistent space for future buttons, properties, sections, and operators.
- Does not require replacing or restructuring the user's workspace.
- Satisfies the v0.0.1 requirements with minimal technical risk.

## Alternatives Considered

### Top Bar or Menu Entry

A menu item would provide a discoverable entry point, but it does not provide a persistent area for content. It would also require an additional destination such as a popup or workspace.

**Decision:** Not selected for the first milestone.

### Popup Dialog

A popup could display the placeholder text with little code, but it is temporary and is not a suitable foundation for a growing tool interface.

**Decision:** Not selected.

### Dedicated Blender Workspace

A dedicated workspace could provide a more application-like experience and more screen area. However, it introduces unnecessary layout, persistence, and lifecycle complexity before the real product interface is defined.

**Decision:** Deferred until future requirements justify it.

### Custom Editor Type

A custom editor could offer maximum control, but it would be significantly more complex and inappropriate for a milestone intended only to validate extension packaging and UI registration.

**Decision:** Not selected.

### Properties Editor Panel

A Properties Editor panel is possible, but the 3D Viewport sidebar is more direct for tools expected to interact with the scene and is easier to discover during early development.

**Decision:** Not selected.

## Consequences

### Positive

- The initial UI can be implemented with very little code.
- The extension gains a clear, dedicated B-Dental category.
- Future controls can be added incrementally within the same area.
- Installation and manual verification remain simple.
- The decision does not force a premature final UI architecture.

### Limitations

- Sidebar width and layout space are limited.
- A complex workflow may eventually outgrow a single panel.
- The panel is not a fully independent screen or workspace.
- Future versions may need navigation beyond the sidebar.

## Revisit Conditions

This decision should be reviewed when one or more of the following becomes true:

- B-Dental requires multiple large screens or workflow stages.
- The interface needs substantially more horizontal or vertical space.
- The product requires a dedicated workspace layout.
- Persistent navigation between several major views becomes necessary.
- The 3D Viewport sidebar negatively constrains usability.

A future decision may replace or supplement this entry point without invalidating the v0.0.1 foundation.
