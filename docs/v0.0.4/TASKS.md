# Tasks: v0.0.4

## Status

- **Version:** v0.0.4
- **Release status:** Complete
- **Workflow:** Step 3 — Multiple Restorations, Manual Margins & Antagonist Regions
- **Verification:** Passed locally
- **Merge strategy:** Squash and merge

## Documentation Revision

- [x] V004-001 Supersede the single-restoration decision.
- [x] V004-002 Record the multiple-independent-restorations decision.
- [x] V004-003 Revise the PRD for multiple restorations.
- [x] V004-004 Revise the implementation plan.
- [x] V004-005 Revise the task checklist.
- [x] V004-006 Revise the verification matrix.
- [x] V004-007 Accept documentation after implementation verification.

## Collection State

- [x] V004-008 Add `BDENTAL_PG_RestorationState`.
- [x] V004-009 Add persistent restoration collection.
- [x] V004-010 Add persistent active restoration index.
- [x] V004-011 Add new-restoration arch selection.
- [x] V004-012 Add new-restoration FDI selection.
- [x] V004-013 Store per-restoration status and validity.
- [x] V004-014 Store per-restoration margin pointer.
- [x] V004-015 Store per-restoration session state.
- [x] V004-016 Store per-restoration diagnostics.
- [x] V004-017 Store per-restoration approval snapshots.
- [x] V004-018 Implement aggregate Step 3 synchronization.
- [x] V004-019 Require at least one restoration for Step 3 completion.
- [x] V004-020 Require every restoration to be approved for Step 3 completion.

## Migration

- [x] V004-021 Preserve safe empty defaults for v0.0.3 scenes.
- [x] V004-022 Retain legacy in-branch single-restoration fields.
- [x] V004-023 Implement one-time legacy restoration migration.
- [x] V004-024 Preserve legacy margin pointer during migration.
- [x] V004-025 Preserve legacy diagnostics and approval snapshots.
- [x] V004-026 Verify v0.0.3 migration in Blender.
- [x] V004-027 Verify single-restoration v0.0.4 migration in Blender.

## Restoration Ownership

- [x] V004-028 Generate stable restoration IDs.
- [x] V004-029 Support anatomical crowns only.
- [x] V004-030 Support permanent FDI teeth.
- [x] V004-031 Constrain FDI teeth by arch.
- [x] V004-032 Resolve available target arches.
- [x] V004-033 Reject duplicate arch and FDI targets.
- [x] V004-034 Resolve active restoration safely.
- [x] V004-035 Tag each margin with restoration ID, arch, and tooth.
- [x] V004-036 Recover stale pointers by restoration ID.
- [x] V004-037 Remove only the owning restoration margin.
- [x] V004-038 Preserve unrelated restoration artifacts.

## Multiple Restoration Operators

- [x] V004-039 Add restoration creation operator.
- [x] V004-040 Add restoration selection operator.
- [x] V004-041 Block switching during an active margin session.
- [x] V004-042 Add confirmed active-restoration removal.
- [x] V004-043 Preserve other restorations during removal.
- [x] V004-044 Scope target focus to active restoration.
- [x] V004-045 Scope margin focus and visibility to active restoration.

## Margin Geometry

- [x] V004-046 Create one Curve per restoration.
- [x] V004-047 Use one 3D `POLY` spline.
- [x] V004-048 Store points in target-local coordinates.
- [x] V004-049 Support cyclic closure.
- [x] V004-050 Preserve visible bevel settings.
- [x] V004-051 Implement ordered point serialization.
- [x] V004-052 Implement target-only ray casting.
- [x] V004-053 Implement nearest-surface reprojection.
- [x] V004-054 Preserve imported scan mesh data.

## Reversible Sessions

- [x] V004-055 Snapshot only the active restoration.
- [x] V004-056 Restore exact active-restoration points on reset.
- [x] V004-057 Restore prior active-restoration state on cancel.
- [x] V004-058 Remove only a new active draft on cancel.
- [x] V004-059 Apply only the active candidate.
- [x] V004-060 Ensure candidate application does not approve.
- [x] V004-061 Preserve all inactive restorations during sessions.

## Validation and Approval

- [x] V004-062 Validate each restoration setup independently.
- [x] V004-063 Validate target ownership and signature.
- [x] V004-064 Validate margin ownership metadata.
- [x] V004-065 Validate curve structure and closure.
- [x] V004-066 Validate minimum unique points.
- [x] V004-067 Validate path length.
- [x] V004-068 Validate surface distance.
- [x] V004-069 Report spacing and proximity warnings.
- [x] V004-070 Store diagnostics per restoration.
- [x] V004-071 Require warning acknowledgment per restoration.
- [x] V004-072 Require visual review per restoration.
- [x] V004-073 Approve each restoration independently.
- [x] V004-074 Recalculate aggregate Step 3 completion after approval.

## Invalidation

- [x] V004-075 Monitor every restoration.
- [x] V004-076 Invalidate edited restoration approval independently.
- [x] V004-077 Invalidate all approvals after upstream invalidation.
- [x] V004-078 Preserve usable geometry when safe.
- [x] V004-079 Detect target scan identity changes.
- [x] V004-080 Detect approved target transform changes.
- [x] V004-081 Detect upstream approval changes.

## User Interface

- [x] V004-082 Display restoration count.
- [x] V004-083 Display aggregate approved count.
- [x] V004-084 Display selectable restoration rows.
- [x] V004-085 Display active restoration status.
- [x] V004-086 Display add-restoration controls.
- [x] V004-087 Allow upper and lower additions when available.
- [x] V004-088 Display per-restoration margin controls.
- [x] V004-089 Display per-restoration diagnostics and approval.
- [x] V004-090 Invoke drawing in the 3D Viewport window region.

## Packaging and Regression Verification

- [x] V004-091 Validate the extension manifest.
- [x] V004-092 Build `b_dental-0.0.4.zip`.
- [x] V004-093 Inspect package contents.
- [x] V004-094 Install and enable the package.
- [x] V004-095 Verify repeated enable, disable, and reload.
- [x] V004-096 Re-run Step 1 regression scenarios.
- [x] V004-097 Re-run Step 2 regression scenarios.
- [x] V004-098 Execute the complete revised Step 3 scenario matrix.
- [x] V004-099 Record actual implementation results and deviations.
- [x] V004-100 Update README after acceptance.
- [x] V004-101 Mark PRD and plan completed after verification.
- [x] V004-102 Prepare a non-draft PR for squash merge.

## Antagonist Region MVP

- [x] V004-103 Resolve the opposing arch per restoration.
- [x] V004-104 Add automatic antagonist-region detection from the approved margin location.
- [x] V004-105 Add manual antagonist-region picking on the opposing scan.
- [x] V004-106 Store per-restoration region ownership, source, radius, and scan signatures.
- [x] V004-107 Display, focus, hide, resize, and clear the managed region.
- [x] V004-108 Require antagonist-region review when an opposing arch exists.
- [x] V004-109 Treat antagonist regions as not applicable for single-arch cases.
- [x] V004-110 Invalidate approval after region or opposing-scan changes.
- [x] V004-111 Remove only the owning region during restoration deletion or case reset.
- [x] V004-112 Verify automatic, manual, persistence, invalidation, and cleanup behavior locally.

## Completion Record

All v0.0.4 tasks are complete. The implementation and documentation were accepted after local Blender validation, package verification, installation, lifecycle testing, migration checks, regression testing, and the complete Step 3 verification matrix. The release pull request is ready for review and **Squash and merge**.
