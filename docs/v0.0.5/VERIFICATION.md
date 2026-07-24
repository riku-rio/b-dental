# Local Verification: v0.0.5

## Document Status

- **Version:** v0.0.5
- **Status:** Passed
- **Target branch:** `feat/v0.0.5-preparation-analysis-insertion-axis`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Blender:** 5.0.1
- **Minimum supported Blender:** 4.2
- **Result:** Accepted
- **Merge strategy:** Squash and merge

This record reflects the completed local verification reported for the v0.0.5 release candidate. Only de-identified dental fixtures were used.

## Package Result

- Manifest version `0.0.5`: **Passed**
- Manifest validation: **Passed**
- Python syntax validation through Blender Python: **Passed**
- `b_dental-0.0.5.zip` creation: **Passed**
- Package-content inspection: **Passed**
- Installation from disk: **Passed**
- Enablement and registration: **Passed**
- Repeated enable, disable, restart, and reload: **Passed**
- Duplicate handlers or draw callbacks: **None observed**
- Registration errors after accepted fixes: **None observed**

Verified Step 4 package modules include:

```text
axis_geometry.py
axis_overlay.py
preparation_analysis.py
step_four_operators.py
step_four_session.py
step_four_validation.py
```

## Defects Found and Corrected During Verification

### 1. Manifest Tagline Length

The initial v0.0.5 tagline was 70 characters. Blender extension validation requires no more than 64 characters, so validation and build correctly failed.

**Correction:** The tagline was shortened to:

`Define insertion axes and analyze preparation undercuts`

**Retest:** Manifest validation and package build passed.

### 2. Analysis Coordinate-Space Mismatch

The initial sample-selection implementation compared target-local polygon centers with an analysis radius expressed in Blender world units. Imported scans with non-identity scale could report:

`No usable surface samples were found inside the analysis radius.`

**Correction:** Evaluated geometry, triangle centers, radius selection, axis direction, BVH construction, ray origin, ray direction, and blocking depth now operate in world space. Sample points are converted back to target-local coordinates only for persistent overlay storage.

**Retest:** Representative analysis found and displayed bounded samples correctly and validation passed.

## Migration and Regression Results

- v0.0.4 scene migration with safe empty Step 4 defaults: **Passed**
- No automatic axis or analysis artifacts when opening v0.0.4 files: **Passed**
- Existing Step 1–3 state preservation: **Passed**
- Step 1 regression scenarios: **Passed**
- Step 2 regression scenarios: **Passed**
- Step 3 regression scenarios: **Passed**
- Existing restorations, margins, and antagonist regions preserved: **Passed**

## Step 4 Scenario Results

### Workflow and State

- Entry remains blocked until aggregate Step 3 approval: **Passed**
- Fresh Step 4 defaults are safe and unapproved: **Passed**
- Entry preserves scans and Step 3 artifacts: **Passed**
- Entry creates no axis automatically: **Passed**
- Safe return to Step 3: **Passed**
- Navigation and restoration switching are blocked during active axis sessions: **Passed**

### Axis Definition

- Set From Current View: **Passed**
- Finite normalized target-local storage: **Passed**
- Seating-direction convention: **Passed**
- World-space display correspondence: **Passed**
- Repeat capture from unchanged view: **Passed**
- Margin-normal suggestion: **Passed**
- View-based sign resolution: **Passed**
- Suggestion remains non-authoritative: **Passed**
- Degenerate input fails safely: **Passed**

### Managed Axis Ownership

- One managed axis object per restoration: **Passed**
- Parent is the preparation scan: **Passed**
- Origin is margin-derived: **Passed**
- Local positive Z matches stored axis: **Passed**
- Rendering disabled: **Passed**
- Ownership metadata present: **Passed**
- Pointer recovery by restoration ID: **Passed**
- Scoped removal and unrelated-content preservation: **Passed**

### Reversible Axis Sessions

- Start and complete state snapshot: **Passed**
- Exact Reset while session remains active: **Passed**
- Exact Cancel and draft-object cleanup: **Passed**
- Capture from managed-object positive Z: **Passed**
- Apply preserves candidate and closes session: **Passed**
- Apply clears stale analysis and approval: **Passed**
- Candidate creation never approves automatically: **Passed**
- Inactive restorations remain unchanged: **Passed**

### Preparation Neighborhood

- Reproducible margin-derived center: **Passed**
- Default radius from margin extent: **Passed**
- `2 mm` to `15 mm` clamping: **Passed**
- User radius adjustment: **Passed**
- Radius changes clear stale results and approval: **Passed**
- Empty neighborhood creates a blocking error without stale approval: **Passed**
- World-space radius remains correct for imported scan scale: **Passed**

### Undercut Analysis

- Deterministic bounded sample policy: **Passed**
- Evaluated triangulated target geometry: **Passed**
- World-space BVH analysis: **Passed**
- Removal direction opposite seating axis: **Passed**
- Scale-aware self-hit offset: **Passed**
- Originating surface is not treated as immediate obstruction: **Passed**
- Clear case: **Passed**
- Obstructed/undercut case: **Passed**
- Axis sensitivity and reversed-axis behavior: **Passed**
- Metrics remain finite and reproducible: **Passed**
- Imported target mesh remains unchanged: **Passed**

### Representative Performance Record

One representative accepted run reported:

- Analyzed samples: `2000`
- Undercut samples: `17`
- Undercut ratio: `0.9%`
- Mean blocking depth: `0.336 mm`
- Maximum blocking depth: `0.809 mm`
- Runtime: approximately `0.354 s`

These values are fixture-specific engineering outputs, not clinical acceptance thresholds.

### Overlay

- Clear and undercut samples are visually distinct: **Passed**
- Axis and sample overlay are scoped to the active restoration: **Passed**
- Show, Hide, and Clear controls: **Passed**
- Overlay source data persists safely: **Passed**
- Overlay does not modify mesh attributes or materials: **Passed**
- Reload does not duplicate callbacks: **Passed**

### Validation, Warnings, and Approval

- Missing axis blocks approval: **Passed**
- Missing analysis blocks approval: **Passed**
- Stale target, margin, axis, radius, settings, or upstream signatures are rejected: **Passed**
- Low-sample, axis-tilt, high-ratio, large-depth, radius-boundary, and adjacent-anatomy warnings: **Passed**
- Visual review required: **Passed**
- Warning acknowledgment required when warnings exist: **Passed**
- Analysis completion alone does not approve: **Passed**
- Independent restoration approval: **Passed**
- Aggregate completion only after the final restoration: **Passed**

### Invalidation and Cleanup

- Step 3 invalidation propagates safely: **Passed**
- Margin edits invalidate the owning restoration: **Passed**
- Target replacement invalidates dependent Step 4 state: **Passed**
- Antagonist-region changes invalidate upstream state: **Passed**
- Axis and radius changes clear stale analysis: **Passed**
- Missing or corrupted axis metadata fails safely: **Passed**
- Removing one restoration removes only its artifacts: **Passed**
- Confirmed case reset removes managed Step 4 state and artifacts: **Passed**
- Unrelated scene objects remain preserved: **Passed**

### Persistence and UI

- Save/reopen preserves restoration order and active index: **Passed**
- Axis vectors and managed artifacts persist: **Passed**
- Radius, metrics, samples, diagnostics, and approvals persist: **Passed**
- Normal Sidebar-width readability: **Passed**
- Status, controls, metrics, warnings, disclaimer, and approval remain usable: **Passed**

## Safety Record

Across the executed scenarios:

- Imported scan mesh identity, topology, coordinates, materials, and color attributes remained unchanged.
- Step 4 did not modify approved margins or antagonist regions.
- Axis operations affected only the active restoration's managed artifact and state.
- Analysis affected only Step 4 result data and viewport visualization.
- Failed, cancelled, stale, or incomplete operations did not create false validity.
- Removing one restoration preserved every other restoration and unrelated object.
- Engineering validation remained explicitly separate from clinical correctness.

## MVP Limits

- The user remains responsible for choosing and visually reviewing the intended insertion direction.
- Margin-normal suggestion is not an automatic clinical recommendation.
- Analysis uses a margin-derived neighborhood rather than segmented preparation anatomy.
- Adjacent anatomy may be included and is reported as an engineering warning.
- The analysis does not automatically correct undercuts.
- Crown bottom, cement gap, anatomy, contacts, and export remain outside v0.0.5.

## Acceptance Record

Manifest validation, build, package inspection, installation, lifecycle, migration, Step 1–3 regression, the complete Step 4 workflow, persistence, invalidation, cleanup, UI, performance, and scan-safety checks were completed successfully after the recorded corrections.

Version v0.0.5 is accepted and ready for a non-draft pull request using **Squash and merge**.
