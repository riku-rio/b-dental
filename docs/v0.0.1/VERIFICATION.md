# Local Verification: v0.0.1

This document records the validation, build, installation, and manual acceptance steps for the B-Dental `v0.0.1` extension foundation.

## Prerequisites

- Windows with PowerShell.
- Blender 4.2 or newer.
- The repository checked out on `feat/v0.0.1-foundation`.
- Commands run from the repository root.

Set the Blender executable path for the installed Blender version:

```powershell
$Blender = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if (-not (Test-Path $Blender)) {
    throw "Blender executable was not found at: $Blender"
}
```

Change the path if Blender is installed elsewhere or a newer supported version is being used.

## Validate the Extension

Run Blender's extension validator against the source package:

```powershell
& $Blender --command extension validate ".\extension"

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed."
}
```

Expected result: Blender reports that the extension metadata and package are valid.

## Build the Extension Package

Create a clean output directory and build the distributable ZIP archive:

```powershell
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

Get-ChildItem $OutputDirectory -Filter "*.zip"
```

Expected output:

```text
b_dental-0.0.1.zip
```

The package must contain only:

```text
__init__.py
blender_manifest.toml
```

Inspect the archive contents with PowerShell:

```powershell
$Package = Get-ChildItem $OutputDirectory -Filter "b_dental-0.0.1.zip" |
    Select-Object -First 1

if (-not $Package) {
    throw "The expected extension package was not created."
}

$InspectionDirectory = Join-Path $OutputDirectory "inspection"

if (Test-Path $InspectionDirectory) {
    Remove-Item $InspectionDirectory -Recurse -Force
}

Expand-Archive -Path $Package.FullName -DestinationPath $InspectionDirectory
Get-ChildItem $InspectionDirectory -Recurse -File |
    ForEach-Object { $_.FullName.Substring($InspectionDirectory.Length + 1) }
```

## Install Locally Through Blender

1. Open Blender.
2. Open **Edit > Preferences**.
3. Select **Get Extensions** or **Add-ons**, depending on the Blender version and preferences layout.
4. Open the extension menu in the upper-right corner.
5. Choose **Install from Disk**.
6. Select `dist\b_dental-0.0.1.zip`.
7. Confirm installation and enable **B-Dental** if it is not enabled automatically.

## Manual Acceptance Test

### Enable and Display

1. Open a 3D Viewport.
2. Press `N` to open the sidebar.
3. Confirm that a tab labeled `B-Dental` is visible.
4. Select the `B-Dental` tab.
5. Confirm that a panel labeled `B-Dental` appears.
6. Confirm that the panel displays exactly:

```text
Not Implemented Yet.
```

### Disable and Re-enable

1. Return to **Edit > Preferences**.
2. Disable B-Dental.
3. Return to the 3D Viewport and confirm that the `B-Dental` tab is removed.
4. Re-enable B-Dental.
5. Confirm that the tab, panel, and placeholder return.
6. Repeat the disable and enable cycle once more.
7. Confirm that no duplicate-class registration error appears.

### Console Review

On Windows, open Blender's system console through **Window > Toggle System Console**.

Confirm that installation, enablement, disablement, and re-enablement produce no Python traceback, registration error, runtime error, or cleanup error.

## Acceptance Record

Record the local result before merging:

- Blender version:
- Operating system:
- Manifest validation: Pass / Fail
- Package build: Pass / Fail
- Local installation: Pass / Fail
- Initial enablement: Pass / Fail
- B-Dental tab visible: Pass / Fail
- B-Dental panel visible: Pass / Fail
- Placeholder exact: Pass / Fail
- Disable cleanup: Pass / Fail
- Re-enable cycle: Pass / Fail
- Console clean: Pass / Fail
- Tester:
- Date:
- Notes:

All checks must pass before the remaining local-verification tasks and PRD acceptance criteria are marked complete.
