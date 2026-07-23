# Local Verification: v0.0.4

## Document Status

- **Version:** v0.0.4
- **Status:** Planned
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Minimum Blender version:** 4.2
- **Result:** Not executed

This document defines the required validation, build, migration, regression, margin-session, safety, persistence, and acceptance scenarios for Step 3 — Restoration Setup & Manual Margin Definition.

All dental fixtures used for verification must be de-identified.

## PowerShell Validation and Build Commands

```powershell
$ErrorActionPreference = "Stop"

$RepoPath = "C:\b-addon\b-dental"
$Blender = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
$Branch = "feat/v0.0.4-restoration-setup-manual-margin-definition"

Set-Location $RepoPath

if ((git branch --show-current) -ne $Branch) {
    throw "Wrong Git branch. Expected: $Branch"
}

& $Blender --command extension validate ".\extension"
if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed."
}

$SourceDirectory = Join-Path $PWD "extension"
$OutputDirectory = Join-Path $PWD "dist"

if (Test-Path $OutputDirectory) {
    Remove-Item $OutputDirectory -Recurse -Force
}

New-Item -ItemType Directory -Path $OutputDirectory | Out-Null

& $Blender --command extension build `
    --source-dir $SourceDirectory `
    --output-dir $OutputDirectory

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension build failed."
}

$Package = Get-ChildItem $OutputDirectory -Filter "b_dental-0.0.4.zip" |
    Select-Object -First 1

if (-not $Package) {
    throw "The expected v0.0.4 package was not created."
}

$InspectDirectory = Join-Path $OutputDirectory "inspect-v0.0.4"
if (Test-Path $InspectDirectory) {
    Remove-Item $InspectDirectory -Recurse -Force
}

Expand-Archive $Package.FullName $InspectDirectory
Get-ChildItem $InspectDirectory -Recurse | Select-Object FullName
```

## Package Verification

Record after execution:

- Manifest validation: **Pending**
- Extension build: **Pending**
- Expected package: `b_dental-0.0.4.zip`
- Package inspection: **Pending**
- Installation from disk: **Pending**
- Extension enablement: **Pending**
- B-Dental registration errors: **Pending**

Required packaged modules are expected to include:

```text
__init__.py
alignment.py
blender_manifest.toml
margin_geometry.py
margin_validation.py
occlusion_validation.py
operators.py
properties.py
restoration_utils.py
scene_utils.py
step_three_operators.py
step_three_session.py
step_two_operators.py
step_two_session.py
ui.py
validation.py
```

## Baseline Capture Rules

Before each transform or mesh-safety scenario, record:

- Object world matrices.
- Mesh data-block identity.
- Vertex count.
- Edge count.
- Polygon count.
- A deterministic sample or checksum of vertex coordinates.
- Existing unrelated scene objects and collections.

The result is acceptable only when Step 3 changes are limited to intended B-Dental restoration artifacts and workflow state.

## Scenario Matrix

### 1. v0.0.3 Migration

**Status: Pending**

Verify:

- A saved v0.0.3 case opens without errors.
- Step 1 and Step 2 state remains available.
- New Step 3 properties use safe defaults.
- `current_step` remains valid.
- No restoration collection or margin is created during file load.
- No scan object moves.
- No scan mesh data changes.

### 2. Registration and Enablement Safety

**Status: Pending**

Verify:

- Enabling the extension does not create a case.
- Enabling the extension does not create a restoration.
- Enabling the extension does not create a margin.
- Existing scene objects and transforms remain unchanged.
- Repeated enable and disable cycles produce no B-Dental errors.
- Script reload does not duplicate handlers or properties.

### 3. Step 1 Regression

**Status: Pending**

Re-run:

- Start New Dental Case.
- Single Arch upper workflow.
- Single Arch lower workflow.
- Dual Arch workflow.
- Full Scan Set workflow.
- Import cancellation.
- Failed replacement safety.
- Missing-role validation.
- Scan replacement and removal.
- Save and reopen.

### 4. Step 2 Regression

**Status: Pending**

Re-run:

- Single Arch not-applicable completion.
- Imported relationship analysis.
- Manual alignment reset and cancel.
- Manual candidate application.
- Right Bite registration.
- Left Bite registration.
- Both Bites registration.
- Candidate verification and approval.
- Approval persistence.
- Transform-change invalidation.

### 5. Step 3 Entry Gating

**Status: Pending**

Verify:

- Step 3 is unavailable before Step 2 completion.
- Single Arch requires explicit Step 2 not-applicable completion.
- Dual Arch and Full Scan Set require verified Step 2.
- Entering Step 3 preserves all scan transforms.
- Entering Step 3 preserves all scan mesh data.
- Entering Step 3 does not set `step_3_valid`.

### 6. Existing Case Reset Correction

**Status: Pending**

Verify:

- Reset clears Step 1, Step 2, and Step 3 workflow state.
- Reset clears active sessions.
- Reset removes confirmed B-Dental-managed scans and restoration artifacts.
- Reset preserves unrelated objects, curves, collections, and meshes.
- No old Step 2 metrics or approval state survives the reset.

### 7. Single Arch Restoration Setup

**Status: Pending**

Verify separately for upper and lower Single Arch cases:

- Target arch is selected automatically.
- The unavailable arch cannot be selected.
- Only FDI teeth belonging to the imported arch are available.
- A target tooth is required.
- Creating the restoration produces one stable restoration ID.
- Save and reopen preserves setup.

### 8. Dual Arch and Full Scan Set Restoration Setup

**Status: Pending**

Verify:

- Upper Jaw and Lower Jaw are available only when live managed scans exist.
- Selecting Upper Jaw exposes only upper permanent FDI teeth.
- Selecting Lower Jaw exposes only lower permanent FDI teeth.
- Invalid arch-tooth combinations are unavailable or rejected.
- The restoration type remains Anatomical Crown.
- Only one active restoration is exposed.

### 9. Confirmed Setup Changes

**Status: Pending**

Verify:

- Changing arch or tooth without a margin updates setup safely.
- Changing arch or tooth with a margin requires confirmation.
- Cancelling confirmation preserves setup and margin.
- Confirming removes only the active restoration's managed margin.
- Unrelated curves and objects remain unchanged.
- A new stable setup can be created after the change.

### 10. Start New Margin Session

**Status: Pending**

Verify:

- Session start revalidates upstream state and setup.
- Session start creates or reuses only the active restoration margin.
- The margin belongs to `B-Dental Restorations`.
- Required ownership metadata is present.
- Scan transforms remain unchanged.
- Scan mesh identity, topology, and coordinates remain unchanged.
- Status becomes `DRAWING`.
- Step 3 remains invalid.

### 11. Target-Only Surface Picking

**Status: Pending**

Verify using visible overlapping objects:

- Clicking the target preparation scan adds a point.
- Clicking the antagonist does not add a point.
- Clicking a bite scan does not add a point.
- Clicking the margin does not add a point.
- Clicking an unrelated mesh does not add a point.
- Clicking empty space does not add a point.
- Accepted points lie on the target scan and are stored in target-local coordinates.

### 12. Modal Drawing Controls

**Status: Pending**

Verify:

- The UI or status bar displays active controls.
- Accepted clicks add ordered points.
- Remove-last removes only the most recent point.
- Finish is rejected below the minimum point count.
- Cancel exits without an approved result.
- A missing or closed 3D Viewport fails safely.
- A stale target during drawing fails safely.

### 13. Candidate Closure

**Status: Pending**

Verify:

- Six or more unique finite points can be finished.
- Finish creates one 3D `POLY` spline.
- The spline is cyclic.
- The point order matches drawing order.
- Status becomes `CANDIDATE`.
- `step_3_valid` remains false.
- The curve has a visible viewport bevel.

### 14. New-Draft Reset and Cancel

**Status: Pending**

Verify:

- Reset restores the exact session-start empty draft state and keeps the session active.
- Cancel removes the new draft margin.
- Cancel restores the prior Step 3 status and validity.
- No scan object changes.
- No unrelated object changes.

### 15. Existing-Margin Reset and Cancel

**Status: Pending**

Verify:

- Starting from an applied margin snapshots exact ordered points.
- Starting from an approved margin snapshots approval state.
- Reset restores exact session-start points.
- Cancel restores exact session-start points.
- Cancel restores prior status, validity, diagnostics, and approval.
- No extra spline or duplicate margin remains.

### 16. Apply Candidate

**Status: Pending**

Verify:

- Apply keeps the current closed candidate.
- Apply closes the session.
- Apply clears previous review confirmation and warning acknowledgment.
- Apply invalidates prior approval.
- Apply sets status to `CANDIDATE`.
- Apply does not set `step_3_valid`.

### 17. Editing and Reprojection

**Status: Pending**

Verify:

- The managed margin can be selected and edited through the supported path.
- Moving points off the surface is detected.
- Reprojection places points back on the target preparation surface.
- Reprojection never uses the antagonist or unrelated geometry.
- Ordered point count is preserved where applicable.
- Recapture produces a valid candidate.
- Material edits invalidate approval.

### 18. Unsupported Curve Structures

**Status: Pending**

Verify blocking behavior for:

- Missing margin object.
- Unmanaged replacement curve.
- Wrong restoration ID.
- Wrong target role.
- Wrong target tooth.
- Multiple splines.
- Bézier or NURBS spline.
- Non-cyclic spline.
- Fewer than six unique points.
- Non-finite point coordinates.
- Collapsed consecutive points.

### 19. Surface-Distance Diagnostics

**Status: Pending**

Verify:

- Points on or near the target surface pass distance checks.
- A point beyond `0.25 mm` produces a warning.
- A point beyond `1.0 mm` produces a blocking error.
- Mean and maximum distances are displayed in millimeters.
- Diagnostics use the evaluated target preparation surface.

### 20. Path and Spacing Diagnostics

**Status: Pending**

Verify:

- Point count is displayed.
- Closed path length is displayed in millimeters.
- Fewer than twelve points produces a warning.
- Abnormal spacing variation produces a warning.
- Approximate non-adjacent proximity can produce a possible-fold warning.
- Diagnostic warnings do not claim clinical incorrectness.

### 21. Explicit Review and Approval

**Status: Pending**

Verify:

- Blocking errors prevent approval.
- Warnings require acknowledgment.
- Visual-review confirmation is required.
- Candidate creation alone does not approve.
- Validation alone does not approve.
- Approval sets `step_3_status = VERIFIED`.
- Approval sets `step_3_valid = true`.
- Approved local-space points and target signature are stored.
- The approved margin remains visible.
- The UI states that diagnostics are not clinical certification.

### 22. Approval Persistence

**Status: Pending**

Verify after save and reopen:

- Restoration ID persists.
- Target arch and tooth persist.
- Margin pointer resolves safely.
- Margin point order and cyclic state persist.
- Approved point snapshot persists.
- Diagnostics and summary persist.
- `step_3_status` and `step_3_valid` persist.

### 23. Margin-Edit Invalidation

**Status: Pending**

Verify:

- Moving an approved point materially invalidates Step 3.
- Adding or deleting a point invalidates Step 3.
- Changing curve metadata invalidates or errors safely.
- Review confirmation and warning acknowledgment are cleared.
- Structurally usable edited geometry becomes `CANDIDATE`.
- Structurally unusable edited geometry becomes `ERROR`.

### 24. Step 2 Invalidation

**Status: Pending**

Verify:

- Invalidating Step 2 invalidates Step 3 approval.
- Step 3 becomes `UPSTREAM_INVALID` when geometry remains usable.
- Restoration setup remains preserved.
- Margin geometry remains preserved when the target scan remains live.
- Re-completing Step 2 does not silently reapprove Step 3.
- Step 3 validation and approval must be rerun.

### 25. Target Scan Removal and Replacement

**Status: Pending**

Verify:

- Removing the target scan invalidates Step 1, Step 2, and Step 3.
- The dependent managed margin is removed safely.
- Replacing the target scan removes the old dependent margin.
- A margin for an unrelated future restoration is not removed by broad cleanup.
- Unrelated scene content remains unchanged.

### 26. Non-Target Scan Changes

**Status: Pending**

Verify:

- Changes to a non-target arch follow upstream invalidation rules.
- Usable target-linked margin geometry is preserved when safe.
- Step 3 approval is invalidated when Step 2 no longer verifies the case.
- No margin is silently reparented or retargeted.

### 27. Scan Transform and Mesh Safety

**Status: Pending**

Compare baseline and final values after all Step 3 actions:

- Target scan world matrix.
- Non-target scan world matrices.
- Mesh data-block identity.
- Vertex count.
- Edge count.
- Polygon count.
- Deterministic vertex-coordinate sample or checksum.

All must remain unchanged unless an explicitly tested upstream Step 1 or Step 2 action is responsible for the change.

### 28. Navigation Safety

**Status: Pending**

Verify:

- Back to Step 2 works when no session is active.
- Active sessions cannot be abandoned silently.
- Reset, Cancel, or Apply resolves the session before navigation.
- Applied or approved margins remain preserved when navigating back.
- Returning to Step 3 restores the correct state.

### 29. UI Readability

**Status: Pending**

Verify at normal Blender sidebar width:

- `Step 1 of 3`, `Step 2 of 3`, and `Step 3 of 3` display correctly.
- Restoration setup is understandable.
- Target arch and tooth constraints are clear.
- Session actions are context-sensitive.
- Drawing instructions are readable.
- Errors and warnings wrap correctly.
- Diagnostics remain readable.
- Approval controls are unambiguous.

### 30. Lifecycle and Console Cleanliness

**Status: Pending**

Verify:

- Repeated enable and disable cycles.
- Repeated session start, reset, cancel, and apply cycles.
- Repeated file save and reopen.
- Repeated target focus and visibility actions.
- No duplicate modal handlers.
- No stale-pointer exceptions.
- No B-Dental-related console errors during accepted workflows.

## Acceptance Record

Complete only after implementation and execution:

1. Manifest validation and package build: **Pending**
2. Installation and enablement: **Pending**
3. v0.0.3 migration: **Pending**
4. Step 1 regression: **Pending**
5. Step 2 regression: **Pending**
6. Restoration setup scenarios: **Pending**
7. Manual drawing scenarios: **Pending**
8. Session rollback scenarios: **Pending**
9. Editing and reprojection scenarios: **Pending**
10. Validation and diagnostics: **Pending**
11. Explicit approval: **Pending**
12. Persistence and invalidation: **Pending**
13. Scan transform and mesh safety: **Pending**
14. Registration lifecycle: **Pending**

## Final Status

Version `v0.0.4` is **not yet verified**. This document must be updated with actual results, deviations, Blender version, package contents, and acceptance evidence before the PRD or plan is marked accepted.
