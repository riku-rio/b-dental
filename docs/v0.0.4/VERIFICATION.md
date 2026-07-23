# Local Verification: v0.0.4

## Document Status

- **Version:** v0.0.4
- **Status:** Planned
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Minimum Blender version:** 4.2
- **Result:** Not executed

This document defines the required package, migration, regression, multiple-restoration, margin-session, safety, persistence, and acceptance checks for Step 3.

Use only de-identified dental fixtures.

## PowerShell Validation and Build

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

$Package = Get-ChildItem $OutputDirectory -Filter "b_dental-0.0.4.zip" |
    Select-Object -First 1

if (-not $Package) {
    throw "The expected b_dental-0.0.4.zip package was not created."
}

$InspectDirectory = Join-Path $OutputDirectory "inspect-v0.0.4"
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

Expected Step 3 modules:

```text
margin_geometry.py
margin_validation.py
restoration_utils.py
step_three_operators.py
step_three_session.py
```

## Safety Baseline

Before scenarios involving restoration operations, record:

- Every scan world matrix.
- Mesh data-block identity.
- Vertex, edge, and polygon counts.
- Deterministic coordinate sample or checksum.
- Existing unrelated objects and collections.
- Existing restoration IDs, margin object names, and point snapshots.

Only intended workflow state and B-Dental-managed restoration artifacts may change.

## Scenario Matrix

### 1. v0.0.3 Migration

**Status: Pending**

Verify:

- Existing Step 1 and Step 2 state opens safely.
- Restoration collection is empty.
- Active index is safe.
- No collection or margin is created automatically.
- No scan changes.

### 2. Earlier Single-Restoration v0.0.4 Migration

**Status: Pending**

Using a file saved with the earlier branch implementation, verify:

- One legacy restoration becomes one collection item.
- Stable ID, arch, FDI tooth, margin pointer, diagnostics, and approval snapshots are preserved.
- Migration occurs once.
- The migrated restoration can be selected, edited, validated, and approved.

### 3. Registration and Lifecycle

**Status: Pending**

Verify:

- Enablement creates no case or restoration.
- Repeated enable/disable produces no errors.
- Script reload does not duplicate properties or handlers.
- Registration does not modify scene objects.

### 4. Step 1 Regression

**Status: Pending**

Re-run Single Arch upper/lower, Dual Arch, Full Scan Set, import cancellation, replacement failure, scan removal, validation, persistence, and reset scenarios.

### 5. Step 2 Regression

**Status: Pending**

Re-run imported, manual, Right Bite, Left Bite, Both Bites, reset, cancel, verification, approval, persistence, and invalidation scenarios.

### 6. Step 3 Entry

**Status: Pending**

Verify Step 3 gating, unchanged scans, empty restoration list for a fresh case, and no automatic restoration creation.

### 7. Add First Restoration

**Status: Pending**

Verify:

- Single Arch constrains the arch automatically.
- Dual/Full cases expose available upper and lower arches.
- FDI choices match the selected arch.
- Add creates one stable ID.
- Status becomes `READY_FOR_MARGIN`.

### 8. Add Multiple Upper Restorations

**Status: Pending**

Add at least FDI 11 and FDI 14. Verify independent IDs, independent rows, independent state, and no scan changes.

### 9. Mixed Upper and Lower Restorations

**Status: Pending**

In a Dual Arch or Full Scan Set case:

- Add an upper restoration.
- Add a lower restoration.
- Confirm both remain listed simultaneously.
- Confirm each resolves its correct preparation scan.
- Confirm switching preserves both.

### 10. Duplicate Target Rejection

**Status: Pending**

Attempt to add the same arch and FDI tooth twice. Verify rejection without modifying the existing restoration.

### 11. Active Restoration Switching

**Status: Pending**

Verify selection changes only the active index and displays the correct target, status, margin, diagnostics, and approval state.

### 12. Switch Gating During Session

**Status: Pending**

Start drawing or editing one margin. Attempt to select another restoration. Verify switching is blocked until Apply or Cancel.

### 13. Independent Margin Creation

**Status: Pending**

Draw margins for two restorations. Verify:

- Separate Curve objects.
- Separate restoration metadata.
- Correct target parents.
- Correct local points.
- No shared spline or pointer.

### 14. Target-Only Picking

**Status: Pending**

For upper and lower active restorations separately, verify only the active preparation scan accepts clicks. Antagonist, other margins, bite scans, unrelated meshes, and empty space must not add points.

### 15. Modal Controls

**Status: Pending**

Verify LMB add, Backspace/Ctrl+Z remove, Enter/RMB close, Esc cancel, minimum-point enforcement, status instructions, and drawing from the Sidebar button through the viewport window region.

### 16. Independent Reset and Cancel

**Status: Pending**

With two restorations present, reset and cancel one active session. Verify exact restoration of its state and zero changes to the other restoration.

### 17. Independent Apply

**Status: Pending**

Apply one candidate. Verify its session closes and approval remains false while the other restoration is unchanged.

### 18. Independent Editing and Reprojection

**Status: Pending**

Edit and reproject each arch separately. Verify reprojection uses only the owning target scan and does not change the other margin.

### 19. Per-Restoration Validation

**Status: Pending**

Verify structure, unique points, finite coordinates, closure, path, surface distance, spacing, and proximity diagnostics are stored only on the active restoration.

### 20. Independent Approval

**Status: Pending**

Approve one restoration and leave another as Candidate. Verify:

- First restoration remains verified.
- Second remains unverified.
- Aggregate `step_3_valid` remains false.
- Approved count is correct.

### 21. Aggregate Completion

**Status: Pending**

Approve every configured restoration. Verify aggregate status becomes `VERIFIED` and `step_3_valid = true` only after the final approval.

### 22. Add After Aggregate Completion

**Status: Pending**

After Step 3 is verified, add another restoration. Verify aggregate validity becomes false while existing approvals remain intact.

### 23. Remove One Restoration

**Status: Pending**

With multiple restorations:

- Remove one after confirmation.
- Confirm only its managed margin is deleted.
- Confirm all other items, margins, diagnostics, and approvals remain intact.
- Confirm active index remains valid.

### 24. Removal and Aggregate Recalculation

**Status: Pending**

Remove an unapproved restoration while all remaining restorations are approved. Verify aggregate Step 3 becomes verified. Remove the last restoration and verify Step 3 becomes setup-required and invalid.

### 25. Persistence

**Status: Pending**

Save and reopen a case containing multiple upper/lower restorations at mixed statuses. Verify collection order, active index, IDs, target data, margins, diagnostics, and approvals persist.

### 26. Independent Margin-Edit Invalidation

**Status: Pending**

Edit one approved margin. Verify only its approval is invalidated and aggregate validity recalculates while other approvals remain.

### 27. Upstream Invalidation

**Status: Pending**

Invalidate Step 1 or Step 2. Verify every restoration approval becomes invalid, statuses become upstream-invalid as appropriate, and usable geometry remains preserved when target scans remain.

### 28. Target Scan Replacement

**Status: Pending**

Replace Upper Jaw in a case with upper and lower restorations. Verify upper-dependent restorations invalidate or lose dependent margins safely while lower restorations remain preserved.

### 29. Metadata Corruption

**Status: Pending**

Corrupt one margin restoration ID, arch, or tooth metadata. Verify only the owning restoration errors and unrelated restoration objects remain untouched.

### 30. Case Reset

**Status: Pending**

Verify confirmed reset removes all B-Dental-managed restoration margins and state while preserving unrelated curves, meshes, and collections.

### 31. Scan Safety

**Status: Pending**

Across all scenarios confirm world matrices, mesh identity, topology, and vertex coordinates remain unchanged except for explicitly permitted Step 2 transforms.

### 32. UI Readability

**Status: Pending**

At normal Sidebar width verify restoration rows, active status, add controls, margin actions, diagnostics, approval controls, approved count, and aggregate completion remain readable.

## Acceptance Record

Do not mark this document Passed until every scenario is executed and actual results are recorded. Any failure requires implementation or documentation correction before v0.0.4 acceptance.
