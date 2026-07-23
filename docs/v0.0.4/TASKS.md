# Tasks: v0.0.4

## Documentation

- [x] V004-001 Define the v0.0.4 product requirements.
- [x] V004-002 Record the restoration and manual-margin implementation plan.
- [x] V004-003 Record the single-restoration scope decision.
- [x] V004-004 Record the permanent FDI tooth-identifier decision.
- [x] V004-005 Record the managed target-local curve decision.
- [x] V004-006 Record the reversible manual-margin-session decision.
- [x] V004-007 Record the explicit validation and approval decision.
- [x] V004-008 Record the local verification procedure.
- [ ] V004-009 Review and approve the complete v0.0.4 documentation set.

## Existing Lifecycle Correction

- [ ] V004-010 Ensure case reset explicitly clears Step 2 state.
- [ ] V004-011 Add Step 3 clearing to case reset.
- [ ] V004-012 Preserve unrelated scene objects during reset.
- [ ] V004-013 Re-run Step 1 and Step 2 reset scenarios.

## Project Structure

- [ ] V004-014 Create `extension/restoration_utils.py`.
- [ ] V004-015 Create `extension/margin_geometry.py`.
- [ ] V004-016 Create `extension/margin_validation.py`.
- [ ] V004-017 Create `extension/step_three_session.py`.
- [ ] V004-018 Create `extension/step_three_operators.py`.
- [ ] V004-019 Extend `extension/properties.py` for Step 3 state.
- [ ] V004-020 Extend `extension/scene_utils.py` for restoration artifacts.
- [ ] V004-021 Extend `extension/ui.py` for a three-step workflow.
- [ ] V004-022 Update `extension/__init__.py` registration orchestration.
- [ ] V004-023 Update `blender_manifest.toml` to version `0.0.4`.
- [ ] V004-024 Add all required Step 3 modules to manifest build paths.

## Step 3 State and Migration

- [ ] V004-025 Add `STEP_3` to workflow navigation.
- [ ] V004-026 Define Step 3 status values.
- [ ] V004-027 Define `step_3_valid`.
- [ ] V004-028 Define stable restoration identity state.
- [ ] V004-029 Define fixed anatomical-crown restoration type.
- [ ] V004-030 Define target-arch state.
- [ ] V004-031 Define permanent FDI target-tooth state.
- [ ] V004-032 Define margin object pointer state.
- [ ] V004-033 Define active margin-session state.
- [ ] V004-034 Define margin candidate and closure state.
- [ ] V004-035 Define warning acknowledgment and review confirmation.
- [ ] V004-036 Define Step 3 summaries, errors, and warnings.
- [ ] V004-037 Define persistent diagnostics.
- [ ] V004-038 Define session point snapshots.
- [ ] V004-039 Define approved point snapshots.
- [ ] V004-040 Define target and upstream signatures.
- [ ] V004-041 Add safe defaults for v0.0.3 scenes.
- [ ] V004-042 Implement `clear_step_three_state()`.
- [ ] V004-043 Implement `invalidate_step_three()`.

## Restoration Identity and Tooth Constraints

- [ ] V004-044 Define canonical supported restoration types.
- [ ] V004-045 Expose only `ANATOMICAL_CROWN` in v0.0.4.
- [ ] V004-046 Define upper permanent FDI tooth identifiers.
- [ ] V004-047 Define lower permanent FDI tooth identifiers.
- [ ] V004-048 Implement target-arch-to-tooth filtering.
- [ ] V004-049 Implement restoration ID generation.
- [ ] V004-050 Preserve restoration ID across save and reopen.
- [ ] V004-051 Reject unsupported target tooth and arch combinations.
- [ ] V004-052 Reject missing target preparation scans.

## Managed Restoration Artifacts

- [ ] V004-053 Create or reuse `B-Dental Restorations` collection.
- [ ] V004-054 Define managed restoration metadata keys.
- [ ] V004-055 Define `MARGIN` artifact type.
- [ ] V004-056 Tag margins with restoration ID.
- [ ] V004-057 Tag margins with target role and tooth.
- [ ] V004-058 Implement safe managed-margin lookup.
- [ ] V004-059 Implement safe managed-margin removal.
- [ ] V004-060 Ensure margin cleanup never removes unrelated curves.
- [ ] V004-061 Implement target-scan signature generation.
- [ ] V004-062 Handle stale margin pointers safely.

## Step 3 Entry and Restoration Setup

- [ ] V004-063 Revalidate Step 1 on Step 3 entry.
- [ ] V004-064 Revalidate Step 2 on Step 3 entry.
- [ ] V004-065 Prevent Step 3 entry before Step 2 completion.
- [ ] V004-066 Ensure Step 3 entry changes no scan transform.
- [ ] V004-067 Ensure Step 3 entry changes no scan mesh data.
- [ ] V004-068 Automatically select the imported arch for Single Arch cases.
- [ ] V004-069 Allow Upper or Lower target selection only when available.
- [ ] V004-070 Require a valid FDI target tooth.
- [ ] V004-071 Implement active restoration creation.
- [ ] V004-072 Implement explicit restoration reset.
- [ ] V004-073 Require confirmation before setup changes when a margin exists.
- [ ] V004-074 Remove only the active restoration margin after confirmed setup changes.
- [ ] V004-075 Set `READY_FOR_MARGIN` only when setup is complete.

## Margin Curve Core

- [ ] V004-076 Create one managed Curve object per active restoration.
- [ ] V004-077 Create one 3D `POLY` spline.
- [ ] V004-078 Store ordered target-local coordinates.
- [ ] V004-079 Implement target-local to world display conversion.
- [ ] V004-080 Implement cyclic closure.
- [ ] V004-081 Implement visible viewport bevel settings.
- [ ] V004-082 Implement ordered point replacement.
- [ ] V004-083 Implement point serialization.
- [ ] V004-084 Implement point deserialization.
- [ ] V004-085 Reject unsupported spline types.
- [ ] V004-086 Reject multiple splines.
- [ ] V004-087 Preserve imported mesh coordinates and topology.

## Target-Only Ray Casting

- [ ] V004-088 Resolve the evaluated target preparation mesh.
- [ ] V004-089 Build viewport rays from user input.
- [ ] V004-090 Transform rays into target-local space safely.
- [ ] V004-091 Ray-cast only against the target preparation scan.
- [ ] V004-092 Ignore antagonist, bite scans, margin, and unrelated objects.
- [ ] V004-093 Convert accepted hits to target-local coordinates.
- [ ] V004-094 Reject missed or invalid hits without adding points.
- [ ] V004-095 Handle stale target objects during drawing safely.

## Modal Manual Drawing

- [ ] V004-096 Implement Step 3 margin-session start.
- [ ] V004-097 Implement the modal drawing operator.
- [ ] V004-098 Display active drawing instructions.
- [ ] V004-099 Add ordered points from accepted clicks.
- [ ] V004-100 Display a live open path.
- [ ] V004-101 Implement remove-last-point behavior.
- [ ] V004-102 Implement explicit finish-and-close behavior.
- [ ] V004-103 Enforce at least six unique finite points.
- [ ] V004-104 Reject collapsed consecutive points.
- [ ] V004-105 Implement modal cancellation.
- [ ] V004-106 Handle missing 3D Viewport safely.
- [ ] V004-107 Roll back safely after drawing exceptions.

## Reversible Margin Sessions

- [ ] V004-108 Snapshot whether a margin existed at session start.
- [ ] V004-109 Snapshot exact ordered session-start points.
- [ ] V004-110 Snapshot prior Step 3 status and validity.
- [ ] V004-111 Snapshot prior approval data.
- [ ] V004-112 Implement exact session reset.
- [ ] V004-113 Keep reset inside the active session.
- [ ] V004-114 Implement exact session cancel.
- [ ] V004-115 Remove a new draft on cancel when no margin existed.
- [ ] V004-116 Restore a prior margin on cancel.
- [ ] V004-117 Restore prior approval on cancel.
- [ ] V004-118 Implement candidate application.
- [ ] V004-119 Ensure candidate application clears previous approval.
- [ ] V004-120 Ensure candidate application does not set Step 3 valid.
- [ ] V004-121 Prevent silent navigation during an active session.

## Candidate Editing and Reprojection

- [ ] V004-122 Implement focus and selection of the managed margin.
- [ ] V004-123 Provide a documented supported editing path.
- [ ] V004-124 Detect added unsupported splines.
- [ ] V004-125 Detect changed spline type.
- [ ] V004-126 Detect non-cyclic edited candidates.
- [ ] V004-127 Implement nearest-surface reprojection.
- [ ] V004-128 Reproject edited points only to the target scan.
- [ ] V004-129 Preserve ordered point identity during reprojection.
- [ ] V004-130 Implement edited-candidate recapture.
- [ ] V004-131 Invalidate approval after material edits.

## Margin Geometry Diagnostics

- [ ] V004-132 Calculate unique point count.
- [ ] V004-133 Calculate closed path length.
- [ ] V004-134 Calculate point-to-surface distances.
- [ ] V004-135 Calculate mean surface distance.
- [ ] V004-136 Calculate maximum surface distance.
- [ ] V004-137 Detect consecutive point collapse.
- [ ] V004-138 Detect large spacing variation.
- [ ] V004-139 Implement approximate non-adjacent segment proximity checks.
- [ ] V004-140 Define named diagnostic thresholds.
- [ ] V004-141 Keep thresholds documented as engineering safeguards.

## Margin Validation

- [ ] V004-142 Define a structured Step 3 validation result.
- [ ] V004-143 Validate upstream workflow state.
- [ ] V004-144 Validate restoration setup.
- [ ] V004-145 Validate target scan ownership and metadata.
- [ ] V004-146 Validate margin ownership and metadata.
- [ ] V004-147 Validate restoration ID match.
- [ ] V004-148 Validate target role and tooth match.
- [ ] V004-149 Validate one 3D `POLY` spline.
- [ ] V004-150 Validate cyclic closure.
- [ ] V004-151 Validate finite coordinates.
- [ ] V004-152 Validate minimum unique point count.
- [ ] V004-153 Validate engineering minimum path length.
- [ ] V004-154 Block points more than `1.0 mm` from target surface.
- [ ] V004-155 Warn for points more than `0.25 mm` from target surface.
- [ ] V004-156 Warn for fewer than twelve points.
- [ ] V004-157 Warn for abnormal spacing.
- [ ] V004-158 Warn for possible folded or self-crossing geometry.
- [ ] V004-159 Validate target-scan signature.
- [ ] V004-160 Reject validation during an active session.
- [ ] V004-161 Separate blocking errors from warnings.

## Explicit Review and Approval

- [ ] V004-162 Implement margin verification checks.
- [ ] V004-163 Display point count.
- [ ] V004-164 Display path length in millimeters.
- [ ] V004-165 Display mean and maximum surface distance.
- [ ] V004-166 Display blocking-error and warning counts.
- [ ] V004-167 Add explicit warning acknowledgment.
- [ ] V004-168 Add explicit visual-review confirmation.
- [ ] V004-169 Implement explicit margin approval.
- [ ] V004-170 Store approved local-space points.
- [ ] V004-171 Store approved target signature.
- [ ] V004-172 Store approval summary and diagnostics.
- [ ] V004-173 Set `step_3_status = VERIFIED` only on approval.
- [ ] V004-174 Set `step_3_valid = true` only on approval.
- [ ] V004-175 Keep the approved margin visible by default.
- [ ] V004-176 Display non-clinical diagnostic notice.

## Invalidation and Persistence

- [ ] V004-177 Invalidate Step 3 after Step 1 invalidation.
- [ ] V004-178 Invalidate Step 3 after Step 2 invalidation.
- [ ] V004-179 Set `UPSTREAM_INVALID` when preserved geometry cannot currently be approved.
- [ ] V004-180 Preserve usable restoration setup during temporary upstream invalidation.
- [ ] V004-181 Preserve usable margin geometry during temporary upstream invalidation.
- [ ] V004-182 Remove a margin after its target scan is removed.
- [ ] V004-183 Remove a margin after its target scan is replaced.
- [ ] V004-184 Preserve unrelated restoration artifacts.
- [ ] V004-185 Detect material approved-margin point changes.
- [ ] V004-186 Detect margin metadata changes.
- [ ] V004-187 Detect target-scan identity changes.
- [ ] V004-188 Clear review confirmation after invalidation.
- [ ] V004-189 Clear warning acknowledgment after invalidation.
- [ ] V004-190 Verify save and reopen persistence of setup.
- [ ] V004-191 Verify save and reopen persistence of margin points.
- [ ] V004-192 Verify save and reopen persistence of approval and diagnostics.

## User Interface

- [ ] V004-193 Display `Step 1 of 3`.
- [ ] V004-194 Display `Step 2 of 3`.
- [ ] V004-195 Display `Step 3 of 3`.
- [ ] V004-196 Add explicit Step 2-to-Step 3 transition.
- [ ] V004-197 Display upstream completion summary.
- [ ] V004-198 Display restoration type.
- [ ] V004-199 Display target arch controls contextually.
- [ ] V004-200 Display target tooth controls contextually.
- [ ] V004-201 Display restoration creation and reset controls.
- [ ] V004-202 Display target scan focus and visibility controls.
- [ ] V004-203 Display margin-session controls contextually.
- [ ] V004-204 Display drawing guidance.
- [ ] V004-205 Display editing and reprojection controls.
- [ ] V004-206 Display errors and warnings.
- [ ] V004-207 Display diagnostics at normal sidebar width.
- [ ] V004-208 Display review and approval controls.
- [ ] V004-209 Display completed Step 3 summary.
- [ ] V004-210 Add safe Back-to-Step-2 behavior.

## Registration Lifecycle

- [ ] V004-211 Register new classes in deterministic order.
- [ ] V004-212 Avoid duplicate Step 3 monitoring behavior.
- [ ] V004-213 Remove modal handlers safely on cancellation and failure.
- [ ] V004-214 Unregister classes and properties in reverse order.
- [ ] V004-215 Verify repeated enable and disable cycles.
- [ ] V004-216 Verify script reload does not duplicate registration state.
- [ ] V004-217 Verify registration does not create restoration artifacts.
- [ ] V004-218 Verify registration does not change scan objects.

## Validation and Local Verification

- [ ] V004-219 Validate the extension manifest.
- [ ] V004-220 Build the `0.0.4` extension package.
- [ ] V004-221 Inspect package contents.
- [ ] V004-222 Install and enable the package.
- [ ] V004-223 Open a v0.0.3 case safely.
- [ ] V004-224 Re-run Step 1 regression scenarios.
- [ ] V004-225 Re-run Step 2 regression scenarios.
- [ ] V004-226 Verify Step 3 entry gating.
- [ ] V004-227 Verify Single Arch restoration setup.
- [ ] V004-228 Verify Dual Arch upper restoration setup.
- [ ] V004-229 Verify Dual Arch lower restoration setup.
- [ ] V004-230 Verify invalid FDI combinations are unavailable or rejected.
- [ ] V004-231 Verify target-only surface picking.
- [ ] V004-232 Verify missed clicks do not add points.
- [ ] V004-233 Verify minimum point enforcement.
- [ ] V004-234 Verify finish creates a cyclic candidate.
- [ ] V004-235 Verify reset restores exact points.
- [ ] V004-236 Verify cancel removes a new draft.
- [ ] V004-237 Verify cancel restores an existing margin.
- [ ] V004-238 Verify Apply Candidate does not approve.
- [ ] V004-239 Verify edited-point reprojection.
- [ ] V004-240 Verify unsupported curve structures are rejected.
- [ ] V004-241 Verify surface-distance blocking and warning thresholds.
- [ ] V004-242 Verify explicit warning acknowledgment.
- [ ] V004-243 Verify explicit visual-review confirmation.
- [ ] V004-244 Verify explicit approval.
- [ ] V004-245 Verify approval persists after reopen.
- [ ] V004-246 Verify margin edits invalidate approval.
- [ ] V004-247 Verify Step 2 invalidation preserves usable geometry and invalidates approval.
- [ ] V004-248 Verify target-scan replacement removes only the dependent margin.
- [ ] V004-249 Verify case reset removes only managed case artifacts.
- [ ] V004-250 Verify scan transforms remain unchanged.
- [ ] V004-251 Verify scan mesh coordinates and topology remain unchanged.
- [ ] V004-252 Verify registration lifecycle and console cleanliness.

## Documentation and Completion

- [ ] V004-253 Record actual implementation results and deviations.
- [ ] V004-254 Record final PowerShell validation and build commands.
- [ ] V004-255 Record executed manual verification results.
- [ ] V004-256 Update PRD status after acceptance.
- [ ] V004-257 Update plan status after acceptance.
- [ ] V004-258 Mark tasks only after implementation or verification is complete.
- [ ] V004-259 Confirm every PRD acceptance criterion.
- [ ] V004-260 Update README for v0.0.4.
- [ ] V004-261 Prepare v0.0.4 for review and squash merge.

## Completion Record

Version `v0.0.4` is not complete.

Completion requires:

- Approved documentation.
- Completed implementation tasks.
- Passed local verification.
- Regression-free Step 1 and Step 2 behavior.
- Reversible manual margin sessions.
- No imported scan mesh modification.
- Explicit margin approval.
- Updated final documentation and README.
- A non-draft pull request prepared for **Squash and merge**.
