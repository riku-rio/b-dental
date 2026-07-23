# Local Verification: v0.0.1

This document records the completed validation, build, installation, and manual acceptance steps for the B-Dental `v0.0.1` extension foundation.

## Prerequisites

- Windows with PowerShell.
- Blender 4.2 or newer.
- The completed verification used Blender 5.0.1.
- The repository checked out on `feat/v0.0.1-foundation`.
- Commands run from the repository root.

Set the Blender executable path:

```powershell
$Blender = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"

if (-not (Test-Path $Blender)) {
    throw "Blender executable was not found at: $Blender"
}
```

## Validate the Extension

```powershell
& $Blender --command extension validate ".\extension"

if ($LASTEXITCODE -ne 0) {
    throw "Blender extension validation failed."
}
```

Verified result:

```text
Success parsing TOML in ".\extension"
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

Verified build output:

```text
building: b_dental-0.0.1.zip
complete
created: "C:\b-addon\b-dental\dist\b_dental-0.0.1.zip"
```

The package contains only:

```text
__init__.py
blender_manifest.toml
```

The manifest is included automatically by Blender's extension builder and is intentionally not listed inside `[build].paths`.

## Install Locally Through Blender

1. Open Blender 5.0.1.
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

6. Disable B-Dental and confirm the registered interface is removed.
7. Enable B-Dental again and confirm the interface returns without duplicate-registration errors.
8. Review the Blender console for B-Dental-related registration, runtime, or cleanup errors.

## Verification Record

```text
Blender version: 5.0.1
Validation result: Passed
Build result: Passed
Built package: C:\b-addon\b-dental\dist\b_dental-0.0.1.zip
Installation result: Passed
Enable result: Passed
Panel result: Passed; B-Dental tab and panel visible
Placeholder result: Passed; displays "Not Implemented Yet." exactly
Disable result: Passed
Re-enable result: Passed
Console errors: None related to B-Dental
Tester: Project owner
Date: 2026-07-23
```

## Final Result

The `v0.0.1` extension foundation passed its acceptance test and is ready for review and squash merge into `main`.
