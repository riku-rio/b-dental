# Product Requirements Document: v0.0.2

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.2
- **Status:** Completed and Accepted
- **Implementation branch:** `feat/v0.0.2-scan-import-workflow`
- **Target branch:** `main`

## Product Overview

Version `v0.0.2` implements the first functional B-Dental workflow stage: initialize a dental case, import intra-oral STL scans into explicit dental roles, validate the required scan set, and advance to a placeholder second step.

The workflow remains inside the existing B-Dental panel in the 3D Viewport sidebar and is driven by scene-persistent state.

## Completed Version Goal

The completed version provides this behavior:

1. The user explicitly starts a new dental case.
2. B-Dental safely removes the untouched default cube when present.
3. The user selects a supported scan configuration.
4. The user imports required STL scans into named role slots.
5. B-Dental validates assignments and imported mesh objects.
6. Successful validation sets `step_1_valid = true` and advances to Step 2.
7. Step 2 displays `Not Implemented Yet.` exactly.

## Supported Configurations

- **Single Arch:** Upper Jaw or Lower Jaw.
- **Dual Arch:** Upper Jaw and Lower Jaw.
- **Full Scan Set:** Upper Jaw, Lower Jaw, Right Bite, and Left Bite.

## Implemented Scope

- Scene-persistent workflow state.
- Explicit case initialization.
- Conservative untouched-startup-cube detection and removal.
- `B-Dental Scans` collection management.
- Fixed scan-role slots.
- STL import using Blender's built-in importer.
- Millimeter, centimeter, and meter source units.
- Deterministic managed-object names and metadata.
- Import, replacement, removal, focus, show, and hide actions.
- Transactional replacement behavior.
- Blocking validation errors and non-blocking geometry warnings.
- Step 1 status independent from Blender operator return values.
- Step 2 transition after successful validation.
- `Back to Step 1` while preserving imported scans.
- Deterministic registration and unregistration.
- Version `0.0.2` extension packaging.

## Out of Scope

- Automatic jaw alignment or occlusion registration.
- Bite-based registration calculations.
- Clinical occlusion approval.
- Scan cleanup, remeshing, smoothing, or sculpting.
- Automatic role classification.
- Bulk multi-file role assignment.
- Non-STL formats.
- Patient-identifying information.
- Network, database, or cloud integration.
- Production Step 2 behavior.

## Requirements Result

All functional requirements `FR-001` through `FR-060` and all non-functional requirements were implemented and locally verified.

This includes:

- Persistent state and navigation.
- Safe case initialization.
- Scan configuration and role assignment.
- STL import and transactional replacement.
- Slot actions.
- Structured validation.
- Step transition behavior.
- Registration and packaging.

## Acceptance Record

Local verification confirmed:

1. Manifest validation and package build passed.
2. Installation and enablement completed without B-Dental-related errors.
3. Registration did not modify the scene.
4. Safe initialization worked in clean and existing scenes.
5. Single Arch, Dual Arch, and Full Scan Set imported and validated correctly.
6. Cancellation and failed replacement preserved state.
7. Missing and invalid scans produced blocking validation errors.
8. Geometry concerns produced non-blocking warnings.
9. Failed validation remained on Step 1.
10. Successful validation set `step_1_valid = true` and advanced to Step 2.
11. Step 2 displayed `Not Implemented Yet.` exactly.
12. Returning to Step 1 preserved imported scans.
13. Save, close, and reopen preserved workflow state.
14. Repeated lifecycle operations produced no duplicate registration or stale Scene property.

## Completion Record

Version `v0.0.2` is complete, accepted, and ready for review and squash merge into `main`.

The next planned version will implement **Step 2 — Occlusion Registration & Verification**.
