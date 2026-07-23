# Tasks: v0.0.3

## Documentation

- [x] V003-001 Define the v0.0.3 product requirements.
- [x] V003-002 Record the occlusion workflow implementation plan.
- [x] V003-003 Record the imported-relationship candidate decision.
- [x] V003-004 Record the bite-mediated registration decision.
- [x] V003-005 Record the fixed-upper and reversible-session decision.
- [x] V003-006 Record the explicit approval and non-clinical-metrics decision.
- [x] V003-007 Record the local verification procedure.
- [x] V003-008 Review and approve the complete v0.0.3 documentation set.

## Project Structure

- [ ] V003-009 Create `extension/alignment.py`.
- [ ] V003-010 Create `extension/occlusion_validation.py`.
- [ ] V003-011 Extend `extension/properties.py` for Step 2 state.
- [ ] V003-012 Extend `extension/operators.py` for Step 2 actions.
- [ ] V003-013 Extend `extension/scene_utils.py` for matrix snapshots and transform helpers.
- [ ] V003-014 Replace the Step 2 placeholder in `extension/ui.py`.
- [ ] V003-015 Update `extension/__init__.py` registration orchestration.
- [ ] V003-016 Update `blender_manifest.toml` to version `0.0.3`.
- [ ] V003-017 Add all required modules to manifest build paths.

## Step 2 State and Migration

- [ ] V003-018 Define Step 2 status values.
- [ ] V003-019 Define alignment mode values.
- [ ] V003-020 Define bite-source values.
- [ ] V003-021 Define `step_2_valid`.
- [ ] V003-022 Define active-session state.
- [ ] V003-023 Define user-review confirmation state.
- [ ] V003-024 Define persistent verification method and summary.
- [ ] V003-025 Define persistent registration metrics.
- [ ] V003-026 Define persistent matrix snapshots.
- [ ] V003-027 Add safe defaults for scenes saved with v0.0.2.
- [ ] V003-028 Invalidate Step 2 when Step 1 becomes invalid.
- [ ] V003-029 Clear active-session state safely during case reset.

## Applicability and Entry

- [ ] V003-030 Revalidate Step 1 objects on Step 2 entry.
- [ ] V003-031 Ensure Step 2 entry does not change object transforms.
- [ ] V003-032 Implement Single Arch not-applicable UI.
- [ ] V003-033 Implement confirmed Single Arch completion.
- [ ] V003-034 Implement Dual Arch applicability checks.
- [ ] V003-035 Implement Full Scan Set applicability checks.
- [ ] V003-036 Handle stale object pointers without UI errors.

## Imported Relationship Analysis

- [ ] V003-037 Define a structured imported-analysis result.
- [ ] V003-038 Implement finite-matrix checks.
- [ ] V003-039 Implement rigid-transform checks.
- [ ] V003-040 Implement coarse arch-distance metrics.
- [ ] V003-041 Implement gross-separation detection.
- [ ] V003-042 Implement optional triangle-overlap diagnostics.
- [ ] V003-043 Implement `bdental.analyze_imported_occlusion`.
- [ ] V003-044 Set plausible imported cases to `IMPORTED_CANDIDATE`.
- [ ] V003-045 Set implausible imported cases to `NEEDS_ALIGNMENT`.
- [ ] V003-046 Preserve transforms during all imported analysis.

## Alignment Session Safety

- [ ] V003-047 Implement exact world-matrix snapshot copying.
- [ ] V003-048 Snapshot upper, lower, and relevant bite objects.
- [ ] V003-049 Implement `bdental.start_alignment_session`.
- [ ] V003-050 Keep the upper jaw fixed during a session.
- [ ] V003-051 Implement `bdental.reset_alignment_preview`.
- [ ] V003-052 Implement `bdental.cancel_alignment`.
- [ ] V003-053 Implement `bdental.apply_alignment_candidate`.
- [ ] V003-054 Ensure apply does not set Step 2 valid.
- [ ] V003-055 Restore safe matrices after registration exceptions.
- [ ] V003-056 Add undo support where practical.
- [ ] V003-057 Prevent leaving Step 2 silently during an active preview.

## Manual Alignment

- [ ] V003-058 Implement manual alignment mode.
- [ ] V003-059 Select and activate the lower jaw for manual movement.
- [ ] V003-060 Display move and rotate instructions.
- [ ] V003-061 Implement `bdental.capture_manual_candidate`.
- [ ] V003-062 Reject non-finite manual transforms.
- [ ] V003-063 Reject scale and shear outside tolerance.
- [ ] V003-064 Preserve the upper-jaw transform.
- [ ] V003-065 Allow manual positioning before bite refinement.

## Registration Core

- [ ] V003-066 Define an immutable registration-result model.
- [ ] V003-067 Sample evaluated mesh vertices in world space.
- [ ] V003-068 Make point sampling deterministic.
- [ ] V003-069 Bound maximum sampled points.
- [ ] V003-070 Build KDTree nearest-neighbor targets.
- [ ] V003-071 Reject correspondences beyond maximum distance.
- [ ] V003-072 Implement robust distance trimming.
- [ ] V003-073 Enforce minimum inlier count.
- [ ] V003-074 Enforce minimum inlier ratio.
- [ ] V003-075 Implement rigid rotation-and-translation estimation.
- [ ] V003-076 Preserve object scale.
- [ ] V003-077 Implement point-to-point ICP iterations.
- [ ] V003-078 Bound iteration count.
- [ ] V003-079 Implement transform convergence tolerance.
- [ ] V003-080 Implement RMSE convergence tolerance.
- [ ] V003-081 Calculate median correspondence distance.
- [ ] V003-082 Calculate translation and rotation deltas.
- [ ] V003-083 Fail safely on insufficient overlap.
- [ ] V003-084 Fail safely on non-convergence.
- [ ] V003-085 Ensure failures do not leave partial transforms.
- [ ] V003-086 Add Blender progress reporting where practical.

## Bite-Guided Registration

- [ ] V003-087 Validate selected bite object and metadata.
- [ ] V003-088 Register Right Bite to the fixed upper jaw.
- [ ] V003-089 Register Left Bite to the fixed upper jaw.
- [ ] V003-090 Register the lower jaw through the aligned Right Bite.
- [ ] V003-091 Register the lower jaw through the aligned Left Bite.
- [ ] V003-092 Implement Both Bites combined-target refinement.
- [ ] V003-093 Calculate right-only lower-jaw diagnostic transform.
- [ ] V003-094 Calculate left-only lower-jaw diagnostic transform.
- [ ] V003-095 Calculate bilateral transform disagreement.
- [ ] V003-096 Define warning and failure thresholds for disagreement.
- [ ] V003-097 Confirm direct upper-to-lower ICP is never used.
- [ ] V003-098 Preserve bite objects for later review.
- [ ] V003-099 Fail with manual-coarse-position guidance when overlap is insufficient.

## Candidate Verification

- [ ] V003-100 Define a structured occlusion-verification result.
- [ ] V003-101 Validate required object references and metadata.
- [ ] V003-102 Validate finite transforms.
- [ ] V003-103 Validate upper-jaw fixed-reference tolerance.
- [ ] V003-104 Validate lower-jaw rigid-transform tolerance.
- [ ] V003-105 Report registration metrics.
- [ ] V003-106 Report gross separation.
- [ ] V003-107 Report possible interpenetration as a warning.
- [ ] V003-108 Report bilateral bite disagreement.
- [ ] V003-109 Separate blocking errors from non-blocking warnings.
- [ ] V003-110 Implement `bdental.run_occlusion_checks`.
- [ ] V003-111 Add explicit warning acknowledgment.
- [ ] V003-112 Add explicit user-review confirmation.
- [ ] V003-113 Implement `bdental.approve_occlusion`.
- [ ] V003-114 Record verification method and summary.
- [ ] V003-115 Set `step_2_status = VERIFIED` on approval.
- [ ] V003-116 Set `step_2_valid = true` only on approval or confirmed not-applicable completion.
- [ ] V003-117 Hide bite objects after approval while preserving them.

## Invalidation and Persistence

- [ ] V003-118 Invalidate Step 2 after scan replacement.
- [ ] V003-119 Invalidate Step 2 after scan removal.
- [ ] V003-120 Invalidate Step 2 after scan-configuration changes.
- [ ] V003-121 Detect material lower-jaw transform changes after approval.
- [ ] V003-122 Detect material bite transform changes after bite-guided approval.
- [ ] V003-123 Preserve objects during invalidation.
- [ ] V003-124 Verify save and reopen persistence of Step 2 state.
- [ ] V003-125 Verify save and reopen persistence of matrices and metrics.

## User Interface

- [ ] V003-126 Replace `Not Implemented Yet.` with Step 2 UI.
- [ ] V003-127 Display Step 1 completion state.
- [ ] V003-128 Display Step 2 status and applicability.
- [ ] V003-129 Display imported-analysis actions.
- [ ] V003-130 Display alignment-mode controls.
- [ ] V003-131 Display bite-source controls conditionally.
- [ ] V003-132 Display active-session controls contextually.
- [ ] V003-133 Display manual-alignment guidance.
- [ ] V003-134 Display progress and registration result summaries.
- [ ] V003-135 Display errors and warnings.
- [ ] V003-136 Display metrics at normal sidebar width.
- [ ] V003-137 Add upper, lower, right-bite, and left-bite focus controls.
- [ ] V003-138 Add upper, lower, right-bite, and left-bite visibility controls.
- [ ] V003-139 Add candidate verification controls.
- [ ] V003-140 Add user-review confirmation.
- [ ] V003-141 Add approval action.
- [ ] V003-142 Display completed verification summary.
- [ ] V003-143 Preserve safe Back-to-Step-1 behavior.

## Registration Lifecycle

- [ ] V003-144 Register new classes in deterministic order.
- [ ] V003-145 Register any transform-monitoring handler only once.
- [ ] V003-146 Remove handlers during unregistration.
- [ ] V003-147 Unregister classes and properties in reverse order.
- [ ] V003-148 Verify repeated enable and disable cycles.
- [ ] V003-149 Verify script reload does not duplicate handlers.
- [ ] V003-150 Verify registration does not change transforms.

## Validation and Local Verification

- [ ] V003-151 Validate the extension manifest.
- [ ] V003-152 Build the `0.0.3` extension package.
- [ ] V003-153 Inspect package contents.
- [ ] V003-154 Install and enable the package.
- [ ] V003-155 Open a v0.0.2 case file safely.
- [ ] V003-156 Re-run Step 1 regression scenarios.
- [ ] V003-157 Verify Step 2 entry preserves transforms.
- [ ] V003-158 Verify Single Arch not-applicable completion.
- [ ] V003-159 Verify imported plausible-candidate analysis.
- [ ] V003-160 Verify imported gross-separation analysis.
- [ ] V003-161 Verify manual reset and cancel restore exact matrices.
- [ ] V003-162 Verify manual candidate capture.
- [ ] V003-163 Verify Right Bite registration.
- [ ] V003-164 Verify Left Bite registration.
- [ ] V003-165 Verify Both Bites registration.
- [ ] V003-166 Verify insufficient-overlap failure safety.
- [ ] V003-167 Verify upper jaw remains fixed.
- [ ] V003-168 Verify mesh data remains unchanged.
- [ ] V003-169 Verify metrics are displayed.
- [ ] V003-170 Verify bilateral disagreement warning.
- [ ] V003-171 Verify apply does not approve automatically.
- [ ] V003-172 Verify explicit approval is required.
- [ ] V003-173 Verify approval persists after reopen.
- [ ] V003-174 Verify transform changes invalidate approval.
- [ ] V003-175 Verify registration lifecycle and console cleanliness.

## Documentation and Completion

- [ ] V003-176 Record actual implementation results and deviations.
- [ ] V003-177 Record final PowerShell validation and build commands.
- [ ] V003-178 Record executed manual verification results.
- [ ] V003-179 Update PRD status after acceptance.
- [ ] V003-180 Update plan status after acceptance.
- [ ] V003-181 Mark tasks only after implementation or verification is complete.
- [ ] V003-182 Confirm every PRD acceptance criterion.
- [ ] V003-183 Update README for v0.0.3.
- [ ] V003-184 Prepare v0.0.3 for review and squash merge.

## Completion Rule

Version `v0.0.3` is complete only when:

- The documentation set is approved.
- All required implementation tasks are complete.
- All acceptance criteria pass locally.
- Step 1 remains regression-free.
- Step 2 preserves imported transforms until the user acts.
- Automatic registration is reversible and fails safely.
- Explicit approval is required for completion.
- `VERIFICATION.md` contains actual results.
- The extension is ready for review and squash merge.
