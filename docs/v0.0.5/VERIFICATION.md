# Local Verification: v0.0.5

## Document Status

- **Version:** v0.0.5
- **Status:** Planned
- **Target branch:** `feat/v0.0.5-preparation-analysis-insertion-axis`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Minimum Blender version:** 4.2
- **Result:** Not executed

This document defines the required package, migration, regression, axis-session, preparation-analysis, safety, persistence, performance, and acceptance checks for Step 4.

Use only de-identified dental fixtures.

## PowerShell Validation and Build

```powershell
$ErrorActionPreference = "Stop"

$RepoPath = "C:\b-addon\b-dental"
$Blender = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
$Branch = "feat/v0.0.5-preparation-analysis-insertion-axis"

Set-Location $RepoPath

if ((git branch --show-current) -ne $Branch) {
    throw "Wrong Git branch. Expected: $Branch"
}

& $Blender --command extension validate ".\extension"
if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed."
}

$OutputDirectory = Join-Path $PWD "dist"
if (Test-Path $OutputDirectory) {
    Remove-Item $OutputDirectory -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDirectory | Out-Null

& $Blender --command extension build `
    --source-dir ".\extension" `
    --output-dir $OutputDirectory

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension build failed."
}

$Package = Get-ChildItem $OutputDirectory -Filter "b_dental-0.0.5.zip" |
    Select-Object -First 1

if (-not $Package) {
    throw "The expected b_dental-0.0.5.zip package was not created."
}

$InspectDirectory = Join-Path $OutputDirectory "inspect-v0.0.5"
if (Test-Path $InspectDirectory) {
    Remove-Item $InspectDirectory -Recurse -Force
}
Expand-Archive $Package.FullName $InspectDirectory
Get-ChildItem $InspectDirectory -Recurse | Select-Object FullName
```

## Package Result

Record after execution:

- Manifest validation: **Pending**
- Extension build: **Pending**
- Package inspection: **Pending**
- Installation: **Pending**
- Enablement: **Pending**
- Registration errors: **Pending**

Expected new Step 4 modules will be recorded after implementation. The package must contain every module listed in `blender_manifest.toml`.

## Safety Baseline

Before Step 4 scenarios, record:

- Every scan world matrix.
- Mesh data-block identity.
- Vertex, edge, and polygon counts.
- Deterministic coordinate sample or checksum.
- Scan materials and color attributes.
- Every approved Step 3 margin point snapshot.
- Every antagonist-region transform and radius.
- Existing unrelated objects and collections.
- Existing restoration IDs and statuses.

Only Step 4 workflow state and B-Dental-managed Step 4 artifacts may change unless a scenario explicitly tests upstream invalidation.

## Scenario Matrix

### 1. v0.0.4 Migration

**Status: Pending**

Verify:

- Step 1–3 state opens safely.
- Restorations, margins, and antagonist regions remain unchanged.
- Aggregate Step 4 state is safe and not verified.
- Every restoration begins with no axis and no analysis result.
- No Step 4 artifact is created automatically.
- No scan changes occur.

### 2. Registration and Lifecycle

**Status: Pending**

Verify:

- Enablement creates no case, restoration, axis, or analysis result.
- Repeated enable and disable produces no errors.
- Restart and script reload do not duplicate properties, handlers, draw callbacks, or artifacts.
- Registration does not modify scene objects.

### 3. Step 1 Regression

**Status: Pending**

Re-run the accepted v0.0.4 Step 1 scenarios, including import, replacement, removal, validation, persistence, and reset.

### 4. Step 2 Regression

**Status: Pending**

Re-run imported, manual, bite-guided, reset, cancel, verification, approval, persistence, and invalidation scenarios.

### 5. Step 3 Regression

**Status: Pending**

Re-run multiple-restoration, margin drawing, editing, reprojection, antagonist-region, validation, approval, persistence, removal, and invalidation scenarios.

### 6. Step 4 Entry Gating

**Status: Pending**

Verify:

- Step 4 is unavailable while Step 3 is incomplete.
- Step 4 becomes available only after every restoration is approved.
- Entry preserves all scans and Step 3 artifacts.
- Entry creates no axis automatically.

### 7. Fresh Step 4 Defaults

**Status: Pending**

For every restoration verify:

- Status is `READY_FOR_AXIS`.
- Validity is false.
- Axis vector is empty or explicitly unset.
- No analysis result or approval signature exists.

### 8. Set From Current View

**Status: Pending**

For upper and lower restorations:

- Position the viewport toward the preparation.
- Capture from the current view.
- Confirm a finite normalized target-local vector.
- Confirm world-space display matches the intended viewing direction.
- Repeat from the same view and confirm deterministic results within tolerance.

### 9. Direction Convention

**Status: Pending**

Verify:

- Stored vector points in the documented seating direction.
- Managed arrow local positive Z matches the stored vector.
- Undercut analysis uses the opposite removal direction.
- UI text and visual arrow are unambiguous.

### 10. Margin-Normal Suggestion

**Status: Pending**

Verify:

- Approved margin points produce a finite candidate.
- Sign follows the current view direction.
- Reversing the view may reverse the suggested sign as documented.
- The suggestion is presented as non-authoritative.
- Degenerate margin geometry fails safely without false approval.

### 11. Managed Axis Ownership

**Status: Pending**

Verify:

- Each restoration owns a separate managed axis object.
- Metadata contains restoration ID, target arch, FDI tooth, artifact type, and schema version.
- Axis parent is the preparation scan.
- Axis origin is margin-derived.
- Axis is not renderable.
- Other restorations and unrelated objects remain unchanged.

### 12. Multiple Restorations

**Status: Pending**

Create axes for at least two restorations, including mixed upper and lower targets. Verify independent vectors, objects, statuses, metrics, and approvals.

### 13. Restoration Switching

**Status: Pending**

Verify switching changes only the active restoration and displays the correct Step 4 state and artifacts.

### 14. Switch Gating During Axis Session

**Status: Pending**

Start editing one axis and attempt to switch restorations. Verify switching remains blocked until Apply or Cancel.

### 15. Start Axis Edit

**Status: Pending**

Verify:

- Existing axis and analysis state are snapshotted.
- Managed axis becomes the active editable object.
- Starting the session invalidates active approval without changing inactive restorations.

### 16. Axis Reset

**Status: Pending**

Rotate the axis and change candidate state, then Reset. Verify exact restoration of session-start vector, object transform, analysis state, diagnostics, and approval snapshot while the session stays active.

### 17. Axis Cancel

**Status: Pending**

Modify a new and an existing axis, then Cancel. Verify exact restoration of the prior Step 4 state and removal of a new draft artifact when appropriate.

### 18. Axis Capture and Apply

**Status: Pending**

Verify:

- Capture converts object positive Z into a finite target-local candidate.
- Apply closes the session.
- Apply preserves the candidate.
- Apply clears stale analysis and approval.
- Apply never verifies Step 4 automatically.

### 19. Axis Focus, Visibility, and Clear

**Status: Pending**

Verify each action affects only the active restoration's axis and does not alter stored scan geometry.

### 20. Analysis Center

**Status: Pending**

Verify the analysis center is reproducibly derived from approved margin points and remains attached to the preparation scan.

### 21. Default Analysis Radius

**Status: Pending**

Verify the default radius derives from margin extent, is finite, and is clamped to the supported range.

### 22. Radius Adjustment

**Status: Pending**

Change the radius and verify:

- Current analysis is cleared.
- Prior approval is invalidated.
- Other restorations remain unchanged.
- Minimum and maximum constraints are enforced.

### 23. Deterministic Sampling

**Status: Pending**

Run analysis repeatedly with unchanged dependencies. Verify identical sample count, undercut count, ratio, mean depth, maximum depth, and sample overlay within documented tolerances.

### 24. Bounded Runtime

**Status: Pending**

Using representative intra-oral scans, record analysis duration and confirm sample and runtime bounds prevent unbounded processing. Record fixture size and actual result.

### 25. No Usable Samples

**Status: Pending**

Force an empty or invalid neighborhood and verify a blocking error with no stale metrics or approval.

### 26. Clear Preparation Case

**Status: Pending**

Use a fixture and axis expected to produce little or no obstruction. Verify metrics remain finite and no false blocking error occurs.

### 27. Undercut Case

**Status: Pending**

Use a fixture and axis with known visible obstruction. Verify undercut samples and positive blocking depths are reported and displayed.

### 28. Axis Sensitivity

**Status: Pending**

Run analysis with materially different axes. Verify metrics and overlay change, old analysis becomes stale, and only the current result is approvable.

### 29. Removal-Direction Convention

**Status: Pending**

Reverse the axis deliberately and verify the undercut result changes consistently with the documented seating/removal convention.

### 30. Self-Intersection Epsilon

**Status: Pending**

Verify surface samples do not classify their originating triangle as an immediate obstruction and that epsilon remains scale-aware.

### 31. Analysis Metrics

**Status: Pending**

Verify storage and UI display for:

- Analyzed sample count.
- Undercut sample count.
- Undercut ratio.
- Mean blocking depth.
- Maximum blocking depth.
- Analysis radius.
- Axis source.
- Duration when implemented.

### 32. Analysis Overlay

**Status: Pending**

Verify:

- Clear and undercut samples are visually distinct.
- Overlay is scoped to the active restoration.
- Show, Hide, and Clear work.
- Overlay does not write mesh attributes or materials.
- Overlay callbacks do not duplicate after reload.

### 33. Validation Without Axis

**Status: Pending**

Verify validation blocks approval when no finite axis candidate exists.

### 34. Validation Without Analysis

**Status: Pending**

Verify a valid axis alone is insufficient and approval remains blocked until current analysis exists.

### 35. Stale Analysis Detection

**Status: Pending**

Change axis, radius, margin, target transform, or target identity and verify old analysis signatures fail validation.

### 36. Engineering Warnings

**Status: Pending**

Exercise low sample count, strong axis tilt, high undercut ratio, large blocking depth, and radius-boundary conditions. Verify warnings are explicit and non-clinical.

### 37. Independent Approval

**Status: Pending**

Approve one restoration while another remains unapproved. Verify aggregate Step 4 validity remains false and the approved restoration stays independently verified.

### 38. Aggregate Completion

**Status: Pending**

Approve every restoration and verify aggregate status becomes `VERIFIED` and `step_4_valid = true` only after final approval.

### 39. Add or Change Restoration Upstream

**Status: Pending**

Return to Step 3 and add, remove, or materially change a restoration. Verify Step 4 becomes upstream invalid and requires current per-restoration work.

### 40. Margin Edit Invalidation

**Status: Pending**

Edit one approved margin. Verify only the owning restoration's Step 4 state is invalidated when the remaining upstream state stays valid.

### 41. Target Scan Replacement

**Status: Pending**

Replace one preparation scan in a mixed-arch case. Verify dependent Step 4 state and artifacts invalidate safely while unrelated restorations remain preserved.

### 42. Antagonist Region Change

**Status: Pending**

Change a required antagonist region in Step 3. Verify Step 3 invalidates and Step 4 reflects upstream invalidation.

### 43. Metadata Corruption

**Status: Pending**

Corrupt one managed-axis restoration ID, arch, tooth, or artifact type. Verify only the owning restoration errors and unrelated content remains untouched.

### 44. Missing Axis Artifact

**Status: Pending**

Delete an axis object externally. Verify the pointer is recovered when a valid owned object exists or the restoration invalidates safely when it does not.

### 45. Persistence

**Status: Pending**

Save and reopen a file containing mixed Step 4 states. Verify collection order, active index, vectors, axis artifacts, radius, metrics, overlays or overlay source data, diagnostics, and approvals persist correctly.

### 46. Remove One Restoration

**Status: Pending**

Verify removing one restoration deletes only its Step 4 managed artifacts and preserves every other restoration.

### 47. Case Reset

**Status: Pending**

Verify confirmed reset removes all B-Dental-managed Step 4 state and artifacts while preserving unrelated scene content.

### 48. Scan Safety

**Status: Pending**

Across all scenarios confirm unchanged scan mesh identity, topology, coordinates, materials, color attributes, and transforms except transforms explicitly permitted by Step 2.

### 49. UI Readability

**Status: Pending**

At normal Sidebar width verify status, restoration list, axis controls, session controls, radius, analysis action, metrics, overlay controls, diagnostics, disclaimer, and approval remain usable.

### 50. Packaging and Release Readiness

**Status: Pending**

Verify manifest version `0.0.5`, package contents, installation, lifecycle, verification record, README update, and non-draft squash-merge PR readiness.

## Acceptance Record

Do not mark this document Passed until every scenario is executed and actual results, thresholds, durations, deviations, and fixture notes are recorded. Any failure requires implementation or documentation correction before v0.0.5 acceptance.