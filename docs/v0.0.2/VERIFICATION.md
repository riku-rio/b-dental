# Local Verification: v0.0.2

## Document Status

- **Version:** v0.0.2
- **Status:** Planned
- **Target implementation branch:** `feat/v0.0.2-scan-import-workflow`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Minimum Blender version:** 4.2
- **Project verification version:** Record the exact installed Blender version when implementation testing begins.

This document defines the validation, build, installation, and manual acceptance procedure for the B-Dental scan-import workflow. Replace planned results with actual results only after running each step locally.

## Prerequisites

- Windows with PowerShell.
- Blender 4.2 or newer.
- The implementation branch checked out locally.
- Commands run from the repository root.
- At least the following safe test fixtures:
  - One valid upper-jaw STL.
  - One valid lower-jaw STL.
  - One valid right-bite STL.
  - One valid left-bite STL.
  - One empty or deliberately invalid mesh fixture when practical.
  - One STL with suspicious scale for warning verification.
- Test files must not contain patient-identifying information.

Set the Blender executable path:

```powershell
$Blender = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"

if (-not (Test-Path $Blender)) {
    throw "Blender executable was not found at: $Blender"
}
```

Adjust the path to the actual Blender installation used for verification.

## Validate the Extension

```powershell
& $Blender --command extension validate ".\extension"

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed with exit code $LASTEXITCODE."
}
```

Expected result:

```text
Success parsing TOML in ".\extension"
```

Record actual result:

```text
Status: Not Run
Output:
```

## Build the Extension Package

```powershell
$SourceDirectory = Join-Path $PWD "extension"
$OutputDirectory = Join-Path $PWD "dist"

if (-not (Test-Path $SourceDirectory)) {
    throw "Extension directory was not found at: $SourceDirectory"
}

if (Test-Path $OutputDirectory) {
    Remove-Item $OutputDirectory -Recurse -Force
}

New-Item -ItemType Directory -Path $OutputDirectory | Out-Null

& $Blender --command extension build `
    --source-dir $SourceDirectory `
    --output-dir $OutputDirectory

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension build failed with exit code $LASTEXITCODE."
}

$Package = Get-ChildItem $OutputDirectory -Filter "*.zip" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Package) {
    throw "Build completed, but no ZIP package was found."
}

Write-Host "Extension package created successfully:"
Write-Host $Package.FullName
```

Expected package name:

```text
b_dental-0.0.2.zip
```

Record actual result:

```text
Status: Not Run
Package:
```

## Inspect Package Contents

```powershell
$InspectDirectory = Join-Path $OutputDirectory "inspect-v0.0.2"

if (Test-Path $InspectDirectory) {
    Remove-Item $InspectDirectory -Recurse -Force
}

Expand-Archive -Path $Package.FullName -DestinationPath $InspectDirectory
Get-ChildItem $InspectDirectory -Recurse -File |
    ForEach-Object {
        $_.FullName.Substring($InspectDirectory.Length + 1)
    }
```

Expected extension source files include:

```text
__init__.py
blender_manifest.toml
operators.py
properties.py
scene_utils.py
ui.py
validation.py
```

The package must not contain:

- `__pycache__`.
- `.pyc` files.
- `dist`.
- Git metadata.
- Documentation files unless intentionally added to build paths.
- Local test fixtures.

Record actual result:

```text
Status: Not Run
Contents:
```

## Install Locally Through Blender

1. Open the exact Blender version used for verification.
2. Open **Edit > Preferences**.
3. Select **Get Extensions**.
4. Open the upper-right menu.
5. Select **Install from Disk**.
6. Select `dist\b_dental-0.0.2.zip`.
7. Enable B-Dental if Blender does not enable it automatically.
8. Review the Blender console for registration errors.

Record:

```text
Installation: Not Run
Enablement: Not Run
Registration errors: Not Reviewed
```

## Manual Acceptance Matrix

### Scenario 1: Registration Is Non-Destructive

1. Open Blender with a scene containing user-created objects.
2. Record object names and counts.
3. Enable B-Dental.
4. Open the B-Dental sidebar.
5. Confirm that no scene object was deleted, renamed, moved, or relinked.
6. Confirm that Step 1 is visible.

Expected:

- Extension enablement changes only registered UI and properties.
- No default cube or user object is deleted automatically.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 2: Clean Startup Case Initialization

1. Open Blender's normal startup scene.
2. Open the B-Dental sidebar.
3. Click `Start New Dental Case`.
4. Confirm that the untouched default cube is removed.
5. Confirm that the camera and light remain.
6. Confirm that `B-Dental Scans` exists.
7. Confirm that the workflow is on Step 1.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 3: Existing Scene Safety

1. Create or modify a mesh named `Cube`.
2. Add at least one unrelated mesh.
3. Click `Start New Dental Case`.
4. Confirm that the modified cube remains.
5. Confirm that unrelated objects remain.
6. Confirm that B-Dental initializes without deleting uncertain objects.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 4: Single Arch — Upper Jaw

1. Select `Single Arch`.
2. Select `Upper Jaw`.
3. Confirm that only the upper-jaw slot is required.
4. Import a valid upper-jaw STL.
5. Confirm object assignment, deterministic name, collection placement, and metadata.
6. Click `Validate & Continue`.
7. Confirm `step_1_valid = true`.
8. Confirm the panel changes to Step 2.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 5: Single Arch — Lower Jaw

Repeat Scenario 4 using the lower-jaw role and fixture.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 6: Dual Arch

1. Select `Dual Arch`.
2. Import upper and lower scans.
3. Confirm bite scans are not required.
4. Validate and continue.
5. Confirm Step 2 is reached.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 7: Full Scan Set

1. Select `Full Scan Set`.
2. Import upper jaw, lower jaw, right bite, and left bite.
3. Confirm every role has a unique assigned object.
4. Validate and continue.
5. Confirm Step 2 is reached.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 8: Missing Required Scan

1. Select `Dual Arch`.
2. Import only the upper jaw.
3. Click `Validate & Continue`.
4. Confirm validation fails.
5. Confirm the error identifies the missing lower jaw.
6. Confirm `step_1_valid = false`.
7. Confirm the workflow remains on Step 1.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 9: Invalid Mesh

1. Assign or import an empty or deliberately invalid mesh fixture.
2. Run validation.
3. Confirm validation fails with an actionable mesh error.
4. Confirm the workflow remains on Step 1.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 10: Warning Does Not Block

1. Import a scan fixture with suspicious dimensions or another supported warning condition.
2. Run validation.
3. Confirm the warning is visible.
4. Confirm no blocking error exists.
5. Confirm Step 1 may still complete.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 11: File Browser Cancellation

1. Click `Import STL` for an empty role.
2. Cancel the file browser.
3. Confirm no object is created.
4. Confirm no slot is assigned.
5. Confirm validation state and existing scene objects remain unchanged.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 12: Transactional Replacement

1. Import a valid scan into a role.
2. Record the assigned object.
3. Begin replacement.
4. Cancel or force a failed replacement import.
5. Confirm the original scan remains assigned and present.
6. Perform a successful replacement.
7. Confirm the new scan becomes assigned only after success.
8. Confirm the previous managed scan is removed or detached according to implementation policy.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 13: Slot Actions

For every populated role:

1. Click `Focus` and confirm the correct object becomes active and selected.
2. Toggle visibility and confirm the correct object responds.
3. Click `Remove` and confirm the slot clears after any required confirmation.
4. Confirm removal invalidates Step 1 validation.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 14: Duplicate Assignment Protection

1. Attempt to assign the same object to two roles through any available path.
2. Confirm the UI prevents it or validation rejects it.
3. Confirm the error identifies both conflicting roles.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 15: External Object Deletion

1. Import a scan into a role.
2. Delete the object outside the B-Dental panel.
3. Return to the panel.
4. Confirm UI drawing does not raise an exception.
5. Confirm validation reports the missing object or clears the stale assignment safely.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 16: Step 2 Placeholder

1. Complete any supported valid configuration.
2. Confirm Step 2 displays exactly:

```text
Not Implemented Yet.
```

3. Click `Back to Step 1`.
4. Confirm all imported scans and assignments remain.
5. Change or remove a scan.
6. Confirm the previous valid state is invalidated.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 17: Save and Reopen Persistence

1. Create a valid or partially completed B-Dental case.
2. Save the `.blend` file.
3. Close Blender.
4. Reopen the file.
5. Confirm the workflow step, configuration, units, object pointers, and slot assignments persist.
6. Confirm managed object metadata persists.
7. Run validation again.

Result:

```text
Status: Not Run
Notes:
```

### Scenario 18: Registration Lifecycle

1. Disable B-Dental.
2. Confirm the panel is removed.
3. Confirm the custom scene pointer property is removed from the registered RNA type.
4. Re-enable B-Dental.
5. Confirm the panel returns without duplicate-registration errors.
6. Repeat the cycle.
7. Reload scripts during development if applicable.
8. Review the console.

Result:

```text
Status: Not Run
Notes:
```

## Final Verification Record

Complete this section only after all required scenarios pass.

```text
Blender version:
Branch:
Commit:
Validation result:
Build result:
Built package:
Package inspection:
Installation result:
Enable result:
Clean startup initialization:
Existing scene safety:
Single Arch upper:
Single Arch lower:
Dual Arch:
Full Scan Set:
Validation failures:
Warning behavior:
Cancellation behavior:
Replacement behavior:
Step 2 placeholder:
Persistence:
Disable/re-enable:
Console errors:
Tester:
Date:
```

## Final Result

Status: Not Verified

Version `v0.0.2` must not be marked complete until every required PRD acceptance criterion and applicable scenario above has an actual recorded passing result.
