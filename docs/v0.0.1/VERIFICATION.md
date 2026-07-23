# Local Verification: v0.0.1

This document records the validation, build, installation, and manual acceptance steps for the B-Dental `v0.0.1` extension foundation.

## Prerequisites

- Windows with PowerShell.
- Blender 4.2 or newer. The current development environment uses Blender 5.0.
- The repository checked out on `feat/v0.0.1-foundation`.
- Commands run from the repository root.

Set the Blender executable path for the installed Blender version:

```powershell
$Blender = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"

if (-not (Test-Path $Blender)) {
    throw "Blender executable was not found at: $Blender"
}
```

Change the path if Blender is installed elsewhere.

## Validate the Extension

Run Blender's extension validator against the source package:

```powershell
& $Blender --command extension validate ".\extension"

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed."
}
```

Expected result:

```text
Success parsing TOML in ".\extension"
```

## Build the Extension Package

Create a clean output directory and build the distributable ZIP archive:

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

& $Blender --command extension build --source-dir $SourceDirectory --output-dir $OutputDirectory

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension build failed with exit code $LASTEXITCODE."
}

$Package = Get-ChildItem $OutputDirectory -Filter "*.zip" |
    Select-Object -First 1

if (-not $Package) {
    throw "Build completed, but no ZIP package was found."
}

Write-Host "Extension package created successfully:"
Write-Host $Package.FullName
```

Expected output package:

```text
b_dental-0.0.1.zip
```

The package must contain only:

```text
__init__.py
blender_manifest.toml
```

The manifest is included automatically by Blender's extension builder. It must not be listed inside `[build].paths`.

Inspect the archive contents with PowerShell:

```powershell
$InspectionDirectory = Join-Path $OutputDirectory "inspection"

if (Test-Path $InspectionDirectory) {
    Remove-Item $InspectionDirectory -Recurse -Force
}

Expand-Archive -Path $Package.FullName -DestinationPath $InspectionDirectory

Get-ChildItem $InspectionDirectory -Recurse -File |
    ForEach-Object {
        $_.FullName.Substring($InspectionDirectory.Length + 1)
    }
```

## Install Locally Through Blender

1. Open Blender 5.0.
2. Open **Edit > Preferences**.
3. Select **Get Extensions**.
4. Open the menu in the upper-right corner.
5. Select **Install from Disk**.
6. Select `dist\b_dental-0.0.1.zip`.
7. Enable B-Dental if Blender does not enable it automatically.

## Manual Acceptance Test

1. Open a 3D Viewport.
2. Press `N` to open the sidebar.
3. Select the `B-Dental` tab.
4. Confirm that the panel label is `B-Dental`.
5. Confirm that the panel displays exactly:

```text
Not Implemented Yet.
```

6. Open **Edit > Preferences > Get Extensions**.
7. Disable B-Dental.
8. Confirm that the `B-Dental` sidebar tab disappears.
9. Enable B-Dental again.
10. Confirm that the tab and placeholder return without duplicate-registration errors.

## Console Review

During enable, disable, and re-enable testing, review Blender's console for:

- Manifest errors.
- Python import errors.
- Class registration errors.
- Duplicate registration errors.
- Class unregistration errors.

The acceptance test passes only when no B-Dental-related error is reported.

## Verification Record

Record the local result before marking the remaining tasks complete:

```text
Blender version:
Validation result:
Build result:
Built package:
Installation result:
Enable result:
Panel result:
Disable result:
Re-enable result:
Console errors:
Tester:
Date:
```
