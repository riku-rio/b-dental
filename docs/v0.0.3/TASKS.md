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

- [x] V003-009 Create `extension/alignment.py`.
- [x] V003-010 Create `extension/occlusion_validation.py`.
- [x] V003-011 Extend `extension/properties.py` for Step 2 state.
- [x] V003-012 Create `extension/step_two_operators.py` for Step 2 actions.
- [x] V003-013 Create `extension/step_two_session.py` for matrix snapshots and transform helpers.
- [x] V003-014 Replace the Step 2 placeholder in `extension/ui.py`.
- [x] V003-015 Update `extension/__init__.py` registration orchestration.
- [x] V003-016 Update `blender_manifest.toml` to version `0.0.3`.
- [x] V003-017 Add all required modules to manifest build paths.

## Step 2 State and Migration

- [x] V003-018 Define Step 2 status values.
- [x] V003-019 Define alignment mode values.
- [x] V003-020 Define bite-source values.
- [x] V003-021 Define `step_2_valid`.
- [x] V003-022 Define active-session state.
- [x] V003-023 Define user-review confirmation state.
- [x] V003-024 Define persistent verification method and summary.
- [x] V003-025 Define persistent registration metrics.
- [x] V003-026 Define persistent matrix snapshots.
- [x] V003-027 Add safe defaults for scenes saved with v0.0.2.
- [x] V003-028 Invalidate Step 2 when Step 1 becomes invalid.
- [x] V003-029 Clear active-session state safely during case reset.

## Applicability and Entry

- [x] V003-030 Revalidate Step 1 objects on Step 2 entry.
- [x] V003-031 Ensure Step 2 entry does not change object transforms.
- [x] V003-032 Implement Single Arch not-applicable UI.
- [x] V003-033 Implement confirmed Single Arch completion.
- [x] V003-034 Implement Dual Arch applicability checks.
- [x] V003-035 Implement Full Scan Set applicability checks.
- [x] V003-036 Handle stale object pointers without UI errors.

## Imported Relationship Analysis

- [x] V003-037 Define a structured imported-analysis result.
- [x] V003-038 Implement finite-matrix checks.
- [x] V003-039 Implement rigid-transform checks.
- [x] V003-040 Implement coarse arch-distance metrics.
- [x] V003-041 Implement gross-separation detection.
- [x] V003-042 Implement optional triangle-overlap diagnostics.
- [x] V003-043 Implement imported-occlusion analysis.
- [x] V003-044 Set plausible imported cases to `IMPORTED_CANDIDATE`.
- [x] V003-045 Set implausible imported cases to `NEEDS_ALIGNMENT`.
- [x] V003-046 Preserve transforms during all imported analysis.

## Alignment Session Safety

- [x] V003-047 Implement exact world-matrix snapshot copying.
- [x] V003-048 Snapshot upper, lower, and relevant bite objects.
- [x] V003-049 Implement Step 2 alignment-session start.
- [x] V003-050 Keep the upper jaw fixed during a session.
- [x] V003-051 Implement preview reset.
- [x] V003-052 Implement alignment cancellation.
- [x] V003-053 Implement candidate application.
- [x] V003-054 Ensure apply does not set Step 2 valid.
- [x] V003-055 Restore safe matrices after registration exceptions.
- [x] V003-056 Add undo support where practical.
- [x] V003-057 Prevent leaving Step 2 silently during an active preview.

## Manual Alignment

- [x] V003-058 Implement manual alignment mode.
- [x] V003-059 Select and activate the lower jaw for manual movement.
- [x] V003-060 Display move and rotate instructions.
- [x] V003-061 Implement manual candidate capture.
- [x] V003-062 Reject non-finite manual transforms.
- [x] V003-063 Reject scale and shear outside tolerance.
- [x] V003-064 Preserve the upper-jaw transform.
- [x] V003-065 Allow manual positioning before bite refinement.

## Registration Core

- [x] V003-066 Define an immutable registration-result model.
- [x] V003-067 Sample evaluated mesh vertices in world space.
- [x] V003-068 Make point sampling deterministic.
- [x] V003-069 Bound maximum sampled points.
- [x] V003-070 Build KDTree nearest-neighbor targets.
- [x] V003-071 Reject correspondences beyond maximum distance.
- [x] V003-072 Implement robust distance trimming.
- [x] V003-073 Enforce minimum inlier count.
- [x] V003-074 Enforce minimum inlier ratio.
- [x] V003-075 Implement rigid rotation-and-translation estimation.
- [x] V003-076 Preserve object scale.
- [x] V003-077 Implement point-to-point ICP iterations.
- [x] V003-078 Bound iteration count.
- [x] V003-079 Implement transform convergence tolerance.
- [x] V003-080 Implement RMSE convergence tolerance.
- [x] V003-081 Calculate median correspondence distance.
- [x] V003-082 Calculate translation and rotation deltas.
- [x] V003-083 Fail safely on insufficient overlap.
- [x] V003-084 Fail safely on non-convergence.
- [x] V003-085 Ensure failures do not leave partial transforms.
- [x] V003-086 Add Blender progress reporting where practical.

## Bite-Guided Registration

- [x] V003-087 Validate selected bite object and metadata.
- [x] V003-088 Register Right Bite to the fixed upper jaw.
- [x] V003-089 Register Left Bite to the fixed upper jaw.
- [x] V003-090 Register the lower jaw through the aligned Right Bite.
- [x] V003-091 Register the lower jaw through the aligned Left Bite.
- [x] V003-092 Implement Both Bites combined-target refinement.
- [x] V003-093 Calculate right-only lower-jaw diagnostic transform.
- [x] V003-094 Calculate left-only lower-jaw diagnostic transform.
- [x] V003-095 Calculate bilateral transform disagreement.
- [x] V003-096 Define warning and failure thresholds for disagreement.
- [x] V003-097 Confirm direct upper-to-lower ICP is never used.
- [x] V003-098 Preserve bite objects for later review.
- [x] V003-099 Fail with manual-coarse-position guidance when overlap is insufficient.

## Candidate Verification

- [x] V003-100 Define a structured occlusion-verification result.
- [x] V003-101 Validate required object references and metadata.
- [x] V003-102 Validate finite transforms.
- [x] V003-103 Validate upper-jaw fixed-reference tolerance.
- [x] V003-104 Validate lower-jaw rigid-transform tolerance.
- [x] V003-105 Report registration metrics.
- [x] V003-106 Report gross separation.
- [x] V003-107 Report possible interpenetration as a warning.
- [x] V003-108 Report bilateral bite disagreement.
- [x] V003-109 Separate blocking errors from non-blocking warnings.
- [x] V003-110 Implement candidate verification checks.
- [x] V003-111 Add explicit warning acknowledgment.
- [x] V003-112 Add explicit user-review confirmation.
- [x] V003-113 Implement explicit occlusion approval.
- [x] V003-114 Record verification method and summary.
- [x] V003-115 Set `step_2_status = VERIFIED` on approval.
- [x] V003-116 Set `step_2_valid = true` only on approval or confirmed not-applicable completion.
- [x] V003-117 Hide bite objects after approval while preserving them.

## Invalidation and Persistence

- [x] V003-118 Invalidate Step 2 after scan replacement.
- [x] V003-119 Invalidate Step 2 after scan removal.
- [x] V003-120 Invalidate Step 2 after scan-configuration changes.
- [x] V003-121 Detect material lower-jaw transform changes after approval.
- [x] V003-122 Detect material bite transform changes after bite-guided approval.
- [x] V003-123 Preserve objects during invalidation.
- [x] V003-124 Verify save and reopen persistence of Step 2 state.
- [x] V003-125 Verify save and reopen persistence of matrices and metrics.

## User Interface

- [x] V003-126 Replace `Not Implemented Yet.` with Step 2 UI.
- [x] V003-127 Display Step 1 completion state.
- [x] V003-128 Display Step 2 status and applicability.
- [x] V003-129 Display imported-analysis actions.
- [x] V003-130 Display alignment-mode controls.
- [x] V003-131 Display bite-source controls conditionally.
- [x] V003-132 Display active-session controls contextually.
- [x] V003-133 Display manual-alignment guidance.
- [x] V003-134 Display progress and registration result summaries.
- [x] V003-135 Display errors and warnings.
- [x] V003-136 Display metrics at normal sidebar width.
- [x] V003-137 Add upper, lower, right-bite, and left-bite focus controls.
- [x] V003-138 Add upper, lower, right-bite, and left-bite visibility controls.
- [x] V003-139 Add candidate verification controls.
- [x] V003-140 Add user-review confirmation.
- [x] V003-141 Add approval action.
- [x] V003-142 Display completed verification summary.
- [x] V003-143 Preserve safe Back-to-Step-1 behavior.

## Registration Lifecycle

- [x] V003-144 Register new classes in deterministic order.
- [x] V003-145 Avoid duplicate transform-monitoring behavior.
- [x] V003-146 Remove registered state safely during unregistration.
- [x] V003-147 Unregister classes and properties in reverse order.
- [x] V003-148 Verify repeated enable and disable cycles.
- [x] V003-149 Verify script reload does not duplicate registration state.
- [x] V003-150 Verify registration does not change transforms.

## Validation and Local Verification

- [x] V003-151 Validate the extension manifest.
- [x] V003-152 Build the `0.0.3` extension package.
- [x] V003-153 Inspect package contents.
- [x] V003-154 Install and enable the package.
- [x] V003-155 Open a v0.0.2 case file safely.
- [x] V003-156 Re-run Step 1 regression scenarios.
- [x] V003-157 Verify Step 2 entry preserves transforms.
- [x] V003-158 Verify Single Arch not-applicable completion.
- [x] V003-159 Verify imported plausible-candidate analysis.
- [x] V003-160 Verify imported gross-separation analysis.
- [x] V003-161 Verify manual reset and cancel restore exact matrices.
- [x] V003-162 Verify manual candidate capture.
- [x] V003-163 Verify Right Bite registration.
- [x] V003-164 Verify Left Bite registration.
- [x] V003-165 Verify Both Bites registration.
- [x] V003-166 Verify insufficient-overlap failure safety.
- [x] V003-167 Verify upper jaw remains fixed.
- [x] V003-168 Verify mesh data remains unchanged.
- [x] V003-169 Verify metrics are displayed.
- [x] V003-170 Verify bilateral disagreement warning.
- [x] V003-171 Verify apply does not approve automatically.
- [x] V003-172 Verify explicit approval is required.
- [x] V003-173 Verify approval persists after reopen.
- [x] V003-174 Verify transform changes invalidate approval.
- [x] V003-175 Verify registration lifecycle and console cleanliness.

## Documentation and Completion

- [x] V003-176 Record actual implementation results and deviations.
- [x] V003-177 Record final PowerShell validation and build commands.
- [x] V003-178 Record executed manual verification results.
- [x] V003-179 Update PRD status after acceptance.
- [x] V003-180 Update plan status after acceptance.
- [x] V003-181 Mark tasks only after implementation or verification is complete.
- [x] V003-182 Confirm every PRD acceptance criterion.
- [x] V003-183 Update README for v0.0.3.
- [x] V003-184 Prepare v0.0.3 for review and squash merge.

## Completion Record

Version `v0.0.3` is complete:

- The documentation set is approved.
- All required implementation tasks are complete.
- All acceptance criteria passed locally.
- Step 1 remains regression-free.
- Step 2 preserves imported transforms until the user acts.
- Automatic registration is reversible and fails safely.
- Explicit approval is required for completion.
- `VERIFICATION.md` records the completed verification result.
- The branch is ready for a non-draft pull request and squash merge.
