# Local Verification: v0.0.3

## Document Status

- **Version:** v0.0.3
- **Status:** Planned
- **Target branch:** `feat/v0.0.3-occlusion-registration-verification`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Minimum Blender version:** 4.2
- **Project verification version:** Record the exact installed Blender version during implementation testing.

This document defines the required validation, build, installation, regression, registration, safety, persistence, and acceptance procedure for Step 2 — Occlusion Registration & Verification.

Actual results must replace planned entries only after each scenario is executed locally.

## Test Data Safety

All test fixtures must be de-identified and must not contain patient-identifying information.

Required fixtures:

- One Single Arch case.
- One Dual Arch case with plausible imported articulation.
- One Dual Arch case with gross jaw separation.
- One Full Scan Set with usable right and left bites.
- One Full Scan Set with only the right bite usable.
- One Full Scan Set with only the left bite usable.
- One Full Scan Set with noisy bite fragments.
- One Full Scan Set with meaningful right-versus-left disagreement.
- One insufficient-overlap case.
- One saved v0.0.2 `.blend` case.

Record fixture identifiers without patient information:

```text
Single Arch fixture:
Dual imported fixture:
Dual separated fixture:
Full bilateral fixture:
Right-only fixture:
Left-only fixture:
Noisy-bite fixture:
Bilateral-disagreement fixture:
Insufficient-overlap fixture:
v0.0.2 migration fixture:
```

## Prerequisites

```powershell
$ErrorActionPreference = "Stop"

$RepoPath = "C:\b-addon\b-dental"
$Blender = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
$Branch = "feat/v0.0.3-occlusion-registration-verification"

if (-not (Test-Path $RepoPath)) {
    throw "Repository directory was not found: $RepoPath"
}

if (-not (Test-Path $Blender)) {
    throw "Blender executable was not found: $Blender"
}

Set-Location $RepoPath

if ((git branch --show-current) -ne $Branch) {
    throw "Wrong Git branch. Expected: $Branch"
}

if (git status --porcelain) {
    throw "The working tree is not clean."
}
```

## Validate the Extension

```powershell
& $Blender --command extension validate ".\extension"

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed."
}
```

Expected:

```text
Success parsing TOML in ".\extension"
```

Actual result:

```text
Status: Not Run
Output:
```

## Build the Extension

```powershell
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
    throw "The expected package was not created."
}

Write-Host $Package.FullName
```

Actual result:

```text
Status: Not Run
Package:
```

## Inspect Package Contents

```powershell
$InspectDirectory = Join-Path $OutputDirectory "inspect-v0.0.3"

if (Test-Path $InspectDirectory) {
    Remove-Item $InspectDirectory -Recurse -Force
}

Expand-Archive $Package.FullName $InspectDirectory
Get-ChildItem $InspectDirectory -Recurse | Select-Object FullName
```

Required package files:

```text
__init__.py
alignment.py
blender_manifest.toml
occlusion_validation.py
operators.py
properties.py
scene_utils.py
ui.py
validation.py
```

Confirm no source-control, cache, fixture, or development-only files are included.

Actual result:

```text
Status: Not Run
Notes:
```

## Install and Enable

1. Open Blender.
2. Open **Edit > Preferences > Get Extensions**.
3. Select **Install from Disk**.
4. Select `dist\b_dental-0.0.3.zip`.
5. Enable B-Dental.
6. Open a 3D Viewport and the `B-Dental` sidebar.
7. Review the Blender console for registration errors.

Actual result:

```text
Status: Not Run
Blender version:
Enable result:
Console errors:
```

## Scenario 1: v0.0.2 Migration

1. Open a `.blend` file saved with B-Dental v0.0.2.
2. Confirm the file opens without exceptions.
3. Confirm Step 1 pointers and validity remain available.
4. Confirm new Step 2 properties have safe defaults.
5. Confirm no object moves during load or registration.

Expected:

- No migration error.
- Step 1 data preserved.
- Step 2 starts unverified.
- Object matrices unchanged.

```text
Status: Not Run
Notes:
```

## Scenario 2: Step 1 Regression

Repeat v0.0.2 acceptance scenarios:

- Start New Dental Case.
- Single Arch upper.
- Single Arch lower.
- Dual Arch.
- Full Scan Set.
- Import cancellation.
- Failed replacement.
- Missing-role validation.
- Back to Step 1.
- Save and reopen.

```text
Status: Not Run
Notes:
```

## Scenario 3: Step 2 Entry Safety

1. Complete Step 1 for a Dual Arch case.
2. Record world matrices for upper and lower objects.
3. Enter Step 2.
4. Compare matrices.

Expected:

- Step 2 UI appears.
- No transform changes occur.
- Step 2 is not valid automatically.

```text
Status: Not Run
Upper unchanged:
Lower unchanged:
```

## Scenario 4: Single Arch Not Applicable

1. Complete Step 1 for Single Arch.
2. Enter Step 2.
3. Confirm registration controls are unavailable.
4. Select `Complete as Not Applicable`.
5. Confirm the action requires explicit confirmation.

Expected:

- `step_2_status = NOT_APPLICABLE`.
- `step_2_valid = true` only after confirmation.

```text
Status: Not Run
Notes:
```

## Scenario 5: Plausible Imported Relationship

1. Open the plausible Dual Arch fixture.
2. Record matrices.
3. Run `Analyze Imported Relationship`.
4. Confirm matrices remain unchanged.

Expected:

- Status becomes `IMPORTED_CANDIDATE`.
- Metrics and warnings display.
- Step 2 remains unverified.

```text
Status: Not Run
Transform preservation:
Analysis status:
Metrics:
```

## Scenario 6: Grossly Separated Imported Relationship

1. Open the separated fixture.
2. Run imported analysis.

Expected:

- Status becomes `NEEDS_ALIGNMENT`.
- Feedback requests alignment.
- No objects move.

```text
Status: Not Run
Notes:
```

## Scenario 7: Manual Session Reset and Cancel

1. Start a manual alignment session.
2. Record session-start matrices.
3. Move and rotate the lower jaw.
4. Use `Reset Preview`.
5. Confirm exact restoration.
6. Move the lower jaw again.
7. Use `Cancel Alignment`.
8. Confirm exact restoration and session closure.

```text
Status: Not Run
Reset exact:
Cancel exact:
Upper unchanged:
```

## Scenario 8: Manual Candidate

1. Start a manual session.
2. Move and rotate the lower jaw.
3. Capture the manual candidate.
4. Confirm scale remains valid.
5. Apply the candidate.

Expected:

- Candidate created.
- Apply preserves the candidate transform.
- Step 2 remains unverified.

Repeat with an invalid scale change and confirm rejection.

```text
Status: Not Run
Valid candidate:
Invalid-scale rejection:
```

## Scenario 9: Right Bite Registration

1. Load a suitable full-set fixture.
2. Start a bite-guided session with `RIGHT`.
3. Record all matrices and mesh counts.
4. Run registration.
5. Review metrics.
6. Apply or cancel.

Expected:

- Right bite registers to upper.
- Lower registers through right bite.
- Upper remains fixed.
- Mesh vertex and polygon counts remain unchanged.
- Failure paths restore safe matrices.

```text
Status: Not Run
Iterations:
Inliers:
Inlier ratio:
RMSE:
Median distance:
Upper unchanged:
Mesh data unchanged:
```

## Scenario 10: Left Bite Registration

Repeat Scenario 9 with `LEFT`.

```text
Status: Not Run
Iterations:
Inliers:
Inlier ratio:
RMSE:
Median distance:
```

## Scenario 11: Both Bites Registration

1. Load the bilateral fixture.
2. Select `BOTH`.
3. Run registration.
4. Confirm both bites align to upper.
5. Confirm lower refinement uses the combined target.
6. Review right-only and left-only diagnostics.

```text
Status: Not Run
Combined result:
Right diagnostic:
Left diagnostic:
Disagreement:
```

## Scenario 12: Bilateral Disagreement

1. Load the disagreement fixture.
2. Run Both Bites registration.

Expected:

- Disagreement is displayed.
- Severity follows documented thresholds.
- Severe disagreement blocks approval or requires corrective action.

```text
Status: Not Run
Translation disagreement:
Rotation disagreement:
Severity:
```

## Scenario 13: Noisy Bite Robustness

1. Load the noisy-bite fixture.
2. Run the relevant bite-guided mode.
3. Confirm robust trimming excludes enough outliers to avoid instability, or fails safely.

Expected:

- No uncontrolled transform.
- No exception leaves partial movement.
- Metrics explain success or failure.

```text
Status: Not Run
Notes:
```

## Scenario 14: Insufficient Overlap

1. Load the insufficient-overlap fixture.
2. Run automatic registration.

Expected:

- Registration fails safely.
- Starting matrices are restored.
- User is instructed to perform manual coarse positioning.

```text
Status: Not Run
Matrices restored:
Message:
```

## Scenario 15: Candidate Verification

For imported, manual, and bite-guided candidates:

1. Run verification checks.
2. Confirm required objects and metadata are checked.
3. Confirm finite and rigid transforms are checked.
4. Confirm separation and overlap warnings appear where applicable.
5. Confirm metrics are labeled as engineering aids.

```text
Status: Not Run
Imported candidate:
Manual candidate:
Bite candidate:
```

## Scenario 16: Explicit Approval

1. Apply a valid candidate.
2. Attempt approval without review confirmation.
3. Confirm approval is blocked.
4. Add a non-blocking warning.
5. Attempt approval without warning acknowledgment.
6. Confirm approval is blocked.
7. Confirm review and warning acknowledgment.
8. Approve.

Expected:

- `step_2_status = VERIFIED`.
- `step_2_valid = true`.
- Method and metrics persist.
- Bite objects are hidden but not deleted.

```text
Status: Not Run
Review requirement:
Warning acknowledgment:
Verified state:
Bites preserved:
```

## Scenario 17: Invalidation

After approval, test each independently:

- Replace upper scan.
- Replace lower scan.
- Remove a scan.
- Change configuration.
- Move lower jaw materially.
- Move a bite materially after bite-guided approval.

Expected:

- Step 2 becomes invalid.
- Objects are preserved unless separately removed.
- User-facing reason is available.

```text
Status: Not Run
Scan replacement:
Scan removal:
Configuration change:
Lower movement:
Bite movement:
```

## Scenario 18: Save and Reopen

1. Approve a candidate.
2. Save the `.blend` file.
3. Close Blender.
4. Reopen the file.

Expected:

- Step 1 validity preserved.
- Step 2 verification preserved.
- Matrices preserved.
- Method, metrics, warnings, and summary preserved.
- Bite visibility preserved.

```text
Status: Not Run
Notes:
```

## Scenario 19: Lifecycle

1. Disable the extension.
2. Confirm UI, properties, and handlers are removed cleanly.
3. Re-enable the extension.
4. Repeat multiple times.
5. Reload scripts during development.

Expected:

- No duplicate registrations.
- No duplicate handlers.
- No transform changes.
- No B-Dental console errors.

```text
Status: Not Run
Cycles:
Console result:
```

## Final Acceptance Record

```text
Version: v0.0.3
Branch: feat/v0.0.3-occlusion-registration-verification
Commit:
Blender version:
Manifest validation: Not Run
Package build: Not Run
Installation: Not Run
v0.0.2 migration: Not Run
Step 1 regression: Not Run
Step 2 entry safety: Not Run
Single Arch not applicable: Not Run
Imported analysis: Not Run
Manual alignment: Not Run
Right Bite registration: Not Run
Left Bite registration: Not Run
Both Bites registration: Not Run
Failure safety: Not Run
Explicit approval: Not Run
Invalidation: Not Run
Persistence: Not Run
Lifecycle: Not Run
Tester:
Date:
Overall result: Not Run
```

## Completion Rule

Do not mark v0.0.3 complete until:

- Every required scenario has passed.
- Actual values and observations are recorded.
- Any deviations from the plan are documented.
- PRD acceptance criteria are confirmed.
- TASKS.md reflects actual completion.
- README is updated.
- The extension is ready for review and squash merge.
