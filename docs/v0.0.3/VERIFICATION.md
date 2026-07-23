# Local Verification: v0.0.3

## Document Status

- **Version:** v0.0.3
- **Status:** Passed
- **Target branch:** `feat/v0.0.3-occlusion-registration-verification`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Minimum Blender version:** 4.2
- **Result:** Accepted for review and squash merge

This document records the completed validation, build, installation, regression, registration, safety, persistence, and acceptance result for Step 2 — Occlusion Registration & Verification.

All fixtures used for local verification were de-identified.

## PowerShell Validation and Build Commands

```powershell
$ErrorActionPreference = "Stop"

$RepoPath = "C:\b-addon\b-dental"
$Blender = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
$Branch = "feat/v0.0.3-occlusion-registration-verification"

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

$Package = Get-ChildItem $OutputDirectory -Filter "b_dental-0.0.3.zip" |
    Select-Object -First 1

if (-not $Package) {
    throw "The expected v0.0.3 package was not created."
}

$InspectDirectory = Join-Path $OutputDirectory "inspect-v0.0.3"
if (Test-Path $InspectDirectory) {
    Remove-Item $InspectDirectory -Recurse -Force
}

Expand-Archive $Package.FullName $InspectDirectory
Get-ChildItem $InspectDirectory -Recurse | Select-Object FullName
```

## Package Result

- Manifest validation: **Passed**
- Extension build: **Passed**
- Expected package: `b_dental-0.0.3.zip`
- Package inspection: **Passed**
- Installation from disk: **Passed**
- Extension enablement: **Passed**
- B-Dental registration errors: **None observed**

Required packaged modules were present:

```text
__init__.py
alignment.py
blender_manifest.toml
occlusion_validation.py
operators.py
properties.py
scene_utils.py
step_two_operators.py
step_two_session.py
ui.py
validation.py
```

No source-control, cache, fixture, or development-only files were required by the installed extension package.

## Scenario Results

### 1. v0.0.2 Migration

**Passed**

- Existing v0.0.2 case data opened safely.
- Step 1 pointers and validity remained available.
- New Step 2 properties used safe defaults.
- No object moved during load or registration.

### 2. Step 1 Regression

**Passed**

Verified:

- Start New Dental Case.
- Single Arch upper and lower workflows.
- Dual Arch workflow.
- Full Scan Set workflow.
- Import cancellation.
- Failed replacement safety.
- Missing-role validation.
- Back to Step 1.
- Save and reopen.

### 3. Step 2 Entry Safety

**Passed**

- Step 2 UI appeared after valid Step 1 completion.
- Upper and lower matrices remained unchanged.
- Step 2 did not become valid automatically.

### 4. Single Arch Not Applicable

**Passed**

- Registration controls were unavailable.
- Explicit completion was required.
- Status became `NOT_APPLICABLE`.
- `step_2_valid` became true only after confirmation.

### 5. Plausible Imported Relationship

**Passed**

- Analysis preserved object transforms.
- Status became `IMPORTED_CANDIDATE`.
- Engineering metrics and warnings were displayed.
- Step 2 remained unverified until approval.

### 6. Grossly Separated Imported Relationship

**Passed**

- Status became `NEEDS_ALIGNMENT`.
- Corrective alignment guidance was shown.
- No object moved during analysis.

### 7. Manual Session Reset and Cancel

**Passed**

- Reset restored exact session-start matrices.
- Cancel restored exact session-start matrices and closed the session.
- The upper jaw remained unchanged.

### 8. Manual Candidate

**Passed**

- A valid manual candidate was captured and applied.
- Candidate application did not approve Step 2.
- Invalid non-rigid scale changes were rejected.

### 9. Right Bite Registration

**Passed**

- Right Bite registered to the fixed upper jaw.
- The lower jaw registered through the aligned right bite.
- The upper jaw remained fixed.
- Mesh vertex and polygon counts remained unchanged.
- Metrics were produced.

### 10. Left Bite Registration

**Passed**

- Left Bite registered to the fixed upper jaw.
- The lower jaw registered through the aligned left bite.
- The upper jaw remained fixed.
- Mesh data remained unchanged.
- Metrics were produced.

### 11. Both Bites Registration

**Passed**

- Both bite scans aligned to the upper jaw.
- Lower refinement used the combined bite target.
- Right-only and left-only diagnostic transforms were calculated.
- Bilateral disagreement was reported.

### 12. Bilateral Disagreement

**Passed**

- Translation and rotation disagreement were displayed.
- Severity followed the implemented thresholds.
- Significant disagreement prevented silent approval.

### 13. Noisy Bite Robustness

**Passed**

- Robust trimming reduced unmatched geometry influence.
- Unusable overlap failed safely.
- No exception left partial movement.

### 14. Insufficient Overlap

**Passed**

- Registration failed safely.
- Starting matrices were restored.
- The user was instructed to perform manual coarse positioning.

### 15. Candidate Verification

**Passed**

Verified for imported, manual, and bite-guided candidates:

- Required objects and metadata.
- Finite transforms.
- Rigid-transform tolerances.
- Fixed upper-jaw reference.
- Gross separation and geometry warnings.
- Engineering metrics and bilateral diagnostics.

### 16. Explicit Approval

**Passed**

- Approval without review confirmation was blocked.
- Approval with unacknowledged warnings was blocked.
- Explicit review and warning acknowledgment enabled approval.
- Approval set `step_2_status = VERIFIED`.
- Approval set `step_2_valid = true`.
- Method, metrics, warnings, and summary persisted.
- Bite objects were preserved and hidden.

### 17. Invalidation

**Passed**

Step 2 approval was invalidated after:

- Upper scan replacement.
- Lower scan replacement.
- Scan removal.
- Scan-configuration change.
- Material lower-jaw movement.
- Material bite movement after bite-guided approval.

Objects were preserved unless separately removed by the user.

### 18. Save and Reopen

**Passed**

- Step 1 validity persisted.
- Step 2 verification persisted.
- Applied matrices persisted.
- Method, metrics, warnings, and summary persisted.
- Bite visibility persisted.

### 19. Registration Lifecycle

**Passed**

- Repeated disable and enable cycles completed cleanly.
- Script reload did not duplicate registration state.
- No transform changes occurred during registration lifecycle operations.
- No B-Dental console errors were observed.

## Implementation Deviations Verified

The final implementation uses two focused modules beyond the earliest proposed structure:

- `step_two_session.py`
- `step_two_operators.py`

Both modules are included in the manifest build paths and passed packaging, installation, and lifecycle checks.

## Final Acceptance Record

```text
Version: v0.0.3
Branch: feat/v0.0.3-occlusion-registration-verification
Manifest validation: Passed
Package build: Passed
Package inspection: Passed
Installation: Passed
Enablement: Passed
v0.0.2 migration: Passed
Step 1 regression: Passed
Step 2 entry safety: Passed
Single Arch not applicable: Passed
Imported analysis: Passed
Manual alignment: Passed
Right Bite registration: Passed
Left Bite registration: Passed
Both Bites registration: Passed
Failure safety: Passed
Explicit approval: Passed
Invalidation: Passed
Persistence: Passed
Lifecycle: Passed
Overall result: Passed
```

## Completion Record

Version `v0.0.3` is accepted:

- All required scenarios passed locally.
- The actual implementation structure is documented.
- PRD acceptance criteria are confirmed.
- `TASKS.md` is complete.
- README is updated.
- The extension is ready for a non-draft pull request and **Squash and merge**.
