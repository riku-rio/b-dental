# Tasks: v0.0.5

## Documentation Foundation

- [x] V005-001 Define Step 4 product scope.
- [x] V005-002 Define insertion-axis direction convention.
- [x] V005-003 Define per-restoration Step 4 state.
- [x] V005-004 Define reversible axis-session behavior.
- [x] V005-005 Define preparation-analysis neighborhood behavior.
- [x] V005-006 Define non-destructive undercut-analysis behavior.
- [x] V005-007 Define validation, approval, and invalidation rules.
- [x] V005-008 Add the implementation plan.
- [x] V005-009 Add the verification matrix.
- [x] V005-010 Record architectural decisions.
- [ ] V005-011 Review and accept the documentation set before production implementation.

## Version and Workflow State

- [ ] V005-012 Update the extension manifest to `0.0.5` during implementation.
- [ ] V005-013 Add `STEP_4` to the workflow-step enum.
- [ ] V005-014 Add aggregate Step 4 status and validity.
- [ ] V005-015 Add per-restoration Step 4 status and validity.
- [ ] V005-016 Add persistent target-local insertion-axis state.
- [ ] V005-017 Add persistent axis source.
- [ ] V005-018 Add persistent managed-axis pointer.
- [ ] V005-019 Add persistent axis-session snapshots.
- [ ] V005-020 Add persistent analysis settings.
- [ ] V005-021 Add persistent analysis metrics.
- [ ] V005-022 Add persistent Step 4 errors, warnings, and summary.
- [ ] V005-023 Add persistent review and warning confirmation.
- [ ] V005-024 Add persistent approval signatures.
- [ ] V005-025 Implement aggregate Step 4 synchronization.

## Step 4 Entry and Navigation

- [ ] V005-026 Add Step 4 entry operator.
- [ ] V005-027 Require aggregate Step 3 approval before entry.
- [ ] V005-028 Preserve scans, margins, antagonist regions, and restoration state on entry.
- [ ] V005-029 Prevent automatic axis or analysis creation on entry.
- [ ] V005-030 Add safe return to Step 3.
- [ ] V005-031 Block navigation while an axis session is active.

## Insertion-Axis Geometry

- [ ] V005-032 Add finite-vector validation helpers.
- [ ] V005-033 Add safe vector normalization.
- [ ] V005-034 Add target-local and world-space axis conversion.
- [ ] V005-035 Add current-view forward-direction capture.
- [ ] V005-036 Add margin-derived analysis center calculation.
- [ ] V005-037 Add margin-normal suggestion calculation.
- [ ] V005-038 Resolve the margin-normal sign using the current view.
- [ ] V005-039 Store the authoritative axis as a normalized target-local vector.
- [ ] V005-040 Add axis-to-orientation conversion for the managed object.
- [ ] V005-041 Add orientation-to-axis capture from the managed object.

## Managed Axis Artifact

- [ ] V005-042 Define managed Step 4 artifact metadata.
- [ ] V005-043 Create one managed axis object per restoration.
- [ ] V005-044 Parent the axis artifact to the preparation scan.
- [ ] V005-045 Place the axis origin at the margin-derived analysis center.
- [ ] V005-046 Align the object's local positive Z to the insertion axis.
- [ ] V005-047 Make the axis clearly visible in the viewport.
- [ ] V005-048 Disable rendering for the axis artifact.
- [ ] V005-049 Recover stale axis pointers by restoration ID.
- [ ] V005-050 Remove only the owning restoration's axis artifact.
- [ ] V005-051 Preserve unrelated objects and other restorations.

## Reversible Axis Sessions

- [ ] V005-052 Add axis-session start.
- [ ] V005-053 Snapshot existing axis vector and source.
- [ ] V005-054 Snapshot managed-axis transform.
- [ ] V005-055 Snapshot analysis settings and results.
- [ ] V005-056 Snapshot approval and diagnostic state.
- [ ] V005-057 Add exact session Reset.
- [ ] V005-058 Add exact session Cancel.
- [ ] V005-059 Add candidate Capture.
- [ ] V005-060 Add candidate Apply.
- [ ] V005-061 Ensure Apply clears stale analysis.
- [ ] V005-062 Ensure candidate creation never approves Step 4.
- [ ] V005-063 Block restoration switching during an active session.
- [ ] V005-064 Preserve inactive restorations during sessions.

## Axis Candidate Operators

- [ ] V005-065 Add **Set From Current View**.
- [ ] V005-066 Add **Suggest From Margin**.
- [ ] V005-067 Add **Start Axis Edit**.
- [ ] V005-068 Add **Capture Axis Candidate**.
- [ ] V005-069 Add **Apply Axis Candidate**.
- [ ] V005-070 Add **Reset Axis Session**.
- [ ] V005-071 Add **Cancel Axis Session**.
- [ ] V005-072 Add axis focus and visibility controls.
- [ ] V005-073 Add clear-axis behavior.

## Preparation-Analysis Neighborhood

- [ ] V005-074 Calculate the margin-derived neighborhood center.
- [ ] V005-075 Calculate a default radius from margin extent.
- [ ] V005-076 Clamp radius to the supported engineering range.
- [ ] V005-077 Add persistent user-adjustable radius.
- [ ] V005-078 Select deterministic target-surface samples inside the radius.
- [ ] V005-079 Bound sample count and runtime.
- [ ] V005-080 Reject an empty or unusable analysis neighborhood.
- [ ] V005-081 Invalidate stale results after radius changes.

## Undercut Analysis

- [ ] V005-082 Define a deterministic sampling policy.
- [ ] V005-083 Build or resolve an evaluated target-mesh acceleration structure.
- [ ] V005-084 Use the removal direction opposite the stored seating axis.
- [ ] V005-085 Add scale-aware self-intersection epsilon handling.
- [ ] V005-086 Detect blocked samples without modifying the target mesh.
- [ ] V005-087 Measure per-sample blocking depth.
- [ ] V005-088 Store analyzed sample count.
- [ ] V005-089 Store undercut sample count.
- [ ] V005-090 Store undercut ratio.
- [ ] V005-091 Store mean blocking depth.
- [ ] V005-092 Store maximum blocking depth.
- [ ] V005-093 Store analysis signatures and settings.
- [ ] V005-094 Clear stale analysis after material dependency changes.

## Analysis Overlay

- [ ] V005-095 Add a non-destructive Step 4 viewport overlay.
- [ ] V005-096 Distinguish clear and undercut samples visually.
- [ ] V005-097 Scope the overlay to the active restoration.
- [ ] V005-098 Add Show, Hide, and Clear controls.
- [ ] V005-099 Ensure overlay registration is lifecycle-safe.
- [ ] V005-100 Ensure overlay data is not stored in imported mesh attributes.

## Validation and Approval

- [ ] V005-101 Validate Step 4 upstream preconditions.
- [ ] V005-102 Validate target scan identity and transform dependencies.
- [ ] V005-103 Validate approved margin dependencies.
- [ ] V005-104 Validate managed-axis ownership metadata.
- [ ] V005-105 Validate axis finiteness and non-zero length.
- [ ] V005-106 Validate normalized-axis tolerance.
- [ ] V005-107 Reject validation during an active axis session.
- [ ] V005-108 Validate analysis radius.
- [ ] V005-109 Validate analysis sample count.
- [ ] V005-110 Validate current analysis signatures.
- [ ] V005-111 Report axis-tilt warning.
- [ ] V005-112 Report low-sample warning.
- [ ] V005-113 Report high-undercut-ratio warning.
- [ ] V005-114 Report large-blocking-depth warning.
- [ ] V005-115 Report neighborhood-boundary warning.
- [ ] V005-116 Require explicit visual review.
- [ ] V005-117 Require warning acknowledgment when warnings exist.
- [ ] V005-118 Add independent restoration approval.
- [ ] V005-119 Store approved axis, analysis, settings, and dependency signatures.
- [ ] V005-120 Recalculate aggregate Step 4 completion after approval.

## Invalidation and Monitoring

- [ ] V005-121 Monitor every restoration's Step 4 dependencies.
- [ ] V005-122 Invalidate all Step 4 approvals after Step 3 invalidation.
- [ ] V005-123 Invalidate the owning restoration after margin changes.
- [ ] V005-124 Invalidate the owning restoration after target changes.
- [ ] V005-125 Invalidate the owning restoration after axis changes.
- [ ] V005-126 Invalidate the owning restoration after radius changes.
- [ ] V005-127 Detect missing or corrupted managed-axis artifacts.
- [ ] V005-128 Preserve usable candidates when safe.
- [ ] V005-129 Remove Step 4 artifacts during restoration removal.
- [ ] V005-130 Remove Step 4 artifacts during confirmed case reset.

## Migration

- [ ] V005-131 Add safe v0.0.4 Step 4 defaults.
- [ ] V005-132 Verify no Step 4 artifact is created while opening v0.0.4 files.
- [ ] V005-133 Preserve all existing Step 1–3 state during migration.
- [ ] V005-134 Document any in-branch v0.0.5 migration before release.

## User Interface

- [ ] V005-135 Display Step 4 aggregate status.
- [ ] V005-136 Display restoration count and Step 4 approved count.
- [ ] V005-137 Display selectable restoration rows.
- [ ] V005-138 Display active target arch and FDI tooth.
- [ ] V005-139 Display axis candidate controls.
- [ ] V005-140 Display reversible session controls.
- [ ] V005-141 Display normalized axis and source.
- [ ] V005-142 Display analysis-radius control.
- [ ] V005-143 Display **Run Undercut Analysis**.
- [ ] V005-144 Display overlay controls.
- [ ] V005-145 Display analysis metrics.
- [ ] V005-146 Display errors, warnings, and disclaimer.
- [ ] V005-147 Display review, acknowledgment, and approval controls.
- [ ] V005-148 Verify normal Sidebar-width readability.

## Packaging and Verification

- [ ] V005-149 Add Step 4 modules to `blender_manifest.toml`.
- [ ] V005-150 Validate the extension manifest.
- [ ] V005-151 Build `b_dental-0.0.5.zip`.
- [ ] V005-152 Inspect package contents.
- [ ] V005-153 Install and enable the package.
- [ ] V005-154 Verify repeated enable, disable, restart, and reload.
- [ ] V005-155 Verify v0.0.4 migration.
- [ ] V005-156 Re-run Step 1 regression scenarios.
- [ ] V005-157 Re-run Step 2 regression scenarios.
- [ ] V005-158 Re-run Step 3 regression scenarios.
- [ ] V005-159 Execute the complete Step 4 scenario matrix.
- [ ] V005-160 Record actual implementation results and deviations.
- [ ] V005-161 Update README after acceptance.
- [ ] V005-162 Mark PRD, plan, decisions, tasks, and verification complete only after local verification.
- [ ] V005-163 Prepare a non-draft PR for **Squash and merge**.

## Current Status

The v0.0.5 documentation foundation is present. Production implementation, package validation, and local verification remain pending.