# Tasks: v0.0.6

## Status

- **Version:** v0.0.6
- **Release status:** Planned
- **Workflow:** Step 5 — Automated Preparation Die & Crown Bottom
- **Verification:** Not started
- **Merge strategy:** Squash and merge

## Documentation Foundation

- [ ] V006-001 Define the accepted Step 5 product scope.
- [ ] V006-002 Define authoritative inputs and dependency signatures.
- [ ] V006-003 Define preparation-region extraction behavior.
- [ ] V006-004 Define preparation-die topology and ownership contract.
- [ ] V006-005 Define insertion-axis-aware blockout behavior.
- [ ] V006-006 Define the region-aware relief field.
- [ ] V006-007 Define the continuous margin seal-band contract.
- [ ] V006-008 Define candidate generation, ranking, and rejection.
- [ ] V006-009 Define constrained correction and expert override behavior.
- [ ] V006-010 Define validation, approval, invalidation, and cleanup.
- [ ] V006-011 Define the implementation plan, verification matrix, and architectural decisions.

## Version and Workflow State

- [ ] V006-012 Update the extension manifest to `0.0.6`.
- [ ] V006-013 Add `STEP_5` to the workflow-step enum.
- [ ] V006-014 Add aggregate Step 5 status and validity.
- [ ] V006-015 Add per-restoration Step 5 status and validity.
- [ ] V006-016 Add persistent Step 5 generation settings.
- [ ] V006-017 Add settings schema and generation-policy versions.
- [ ] V006-018 Add managed preparation-die pointer and metadata.
- [ ] V006-019 Add managed blocked-die pointer and metadata.
- [ ] V006-020 Add crown-bottom candidate state and selected-candidate identity.
- [ ] V006-021 Add candidate score, rank, rejection, runtime, and iteration state.
- [ ] V006-022 Add geometry metrics and constraint-result state.
- [ ] V006-023 Add Step 5 diagnostics, review, acknowledgment, and approval snapshots.
- [ ] V006-024 Add constrained-correction session snapshots.
- [ ] V006-025 Add aggregate synchronization across all restorations.

## Step 5 Entry and Navigation

- [ ] V006-026 Add gated Step 5 entry after aggregate Step 4 approval.
- [ ] V006-027 Reject entry while any upstream edit session is active.
- [ ] V006-028 Preserve all Step 1–4 state and artifacts on entry.
- [ ] V006-029 Create no Step 5 geometry automatically on entry.
- [ ] V006-030 Add safe return to Step 4.
- [ ] V006-031 Block restoration switching and navigation during active Step 5 correction sessions.

## Geometry Foundations

- [ ] V006-032 Add finite scalar, vector, matrix, and settings validation helpers.
- [ ] V006-033 Add local/world direction and point conversion helpers.
- [ ] V006-034 Add deterministic evaluated-mesh extraction with guaranteed cleanup.
- [ ] V006-035 Add triangulated surface representation and adjacency tables.
- [ ] V006-036 Add stable geometry and settings serialization.
- [ ] V006-037 Add source, policy, and generated-artifact signatures.
- [ ] V006-038 Add scale-aware tolerances derived from source units and geometry extent.
- [ ] V006-039 Add managed-artifact ownership, schema metadata, recovery, and cleanup helpers.

## Preparation-Region Extraction

- [ ] V006-040 Reconstruct the ordered approved margin in target-local and world coordinates.
- [ ] V006-041 Project or map margin samples to deterministic target-surface anchors.
- [ ] V006-042 Build target-surface triangle adjacency.
- [ ] V006-043 Classify candidate triangles relative to the approved margin loop.
- [ ] V006-044 Traverse and extract one bounded preparation patch.
- [ ] V006-045 Apply insertion-axis-aware filtering to reduce adjacent-anatomy leakage.
- [ ] V006-046 Preserve deterministic boundary correspondence to the approved margin.
- [ ] V006-047 Reject open, branching, ambiguous, or multiply bounded extraction results.
- [ ] V006-048 Record extraction coverage, ambiguity, and source-resolution metrics.
- [ ] V006-049 Ensure extraction never changes the target mesh.

## Preparation-Die Generation

- [ ] V006-050 Duplicate the extracted preparation surface into a restoration-owned managed mesh.
- [ ] V006-051 Rebuild or regularize the margin boundary without changing the approved margin contract.
- [ ] V006-052 Generate insertion-axis-aligned side walls below the margin.
- [ ] V006-053 Generate a deterministic base plane and cap.
- [ ] V006-054 Orient normals consistently.
- [ ] V006-055 Remove accepted duplicate or degenerate elements through bounded repair.
- [ ] V006-056 Validate closure, manifoldness, boundary count, and ownership.
- [ ] V006-057 Add preparation-die focus and visibility controls.
- [ ] V006-058 Preserve upstream geometry and unrelated scene content.

## Insertion-Axis-Aware Undercut Blockout

- [ ] V006-059 Build acceleration geometry for the preparation die.
- [ ] V006-060 Construct an insertion-axis-aligned 2.5D sampling or envelope domain.
- [ ] V006-061 Compute the accessible envelope along the approved seating/removal direction.
- [ ] V006-062 Apply configurable blockout clearance.
- [ ] V006-063 Preserve the margin and seal-band boundary contract.
- [ ] V006-064 Reconstruct blocked geometry with bounded resolution.
- [ ] V006-065 Detect unresolved path obstruction after reconstruction.
- [ ] V006-066 Record blocked area, displacement, collision, and maximum-depth metrics.
- [ ] V006-067 Reject inverted, folded, discontinuous, or unresolved blockout results.
- [ ] V006-068 Keep the blocked die as a separate non-destructive managed artifact.

## Relief Field and Spacer Regions

- [ ] V006-069 Add marginal-gap setting and safe bounds.
- [ ] V006-070 Add cement-gap setting and safe bounds.
- [ ] V006-071 Add spacer-start distance and safe bounds.
- [ ] V006-072 Add axial-relief setting and safe bounds.
- [ ] V006-073 Add occlusal-relief setting and safe bounds.
- [ ] V006-074 Add seal-band width and safe bounds.
- [ ] V006-075 Compute geodesic or surface-distance-from-margin values.
- [ ] V006-076 Classify seal, transition, axial, and occlusal regions deterministically.
- [ ] V006-077 Build a continuous relief scalar field.
- [ ] V006-078 Smooth transitions without changing authoritative boundaries.
- [ ] V006-079 Detect invalid offset directions, folds, inversions, and local collapse.
- [ ] V006-080 Record achieved regional gap metrics and target error.

## Margin Seal Band

- [ ] V006-081 Generate one ordered seal-band loop corresponding to the approved margin.
- [ ] V006-082 Generate the inner seal-band boundary from configured width and gap.
- [ ] V006-083 Connect seal-band boundaries with consistent topology.
- [ ] V006-084 Join the seal band continuously to the relieved internal surface.
- [ ] V006-085 Validate loop continuity, correspondence, orientation, and width.
- [ ] V006-086 Detect gaps, branches, duplicate segments, flipped faces, and self-intersections.
- [ ] V006-087 Record mean/max margin deviation and minimum/mean band width.
- [ ] V006-088 Reject any candidate with a discontinuous or invalid seal band.

## Crown-Bottom Candidate Generation

- [ ] V006-089 Define bounded candidate policies and deterministic ordering.
- [ ] V006-090 Generate the initial crown-bottom surface from blocked geometry and relief field.
- [ ] V006-091 Generate optional bounded variants when the primary policy cannot resolve trade-offs.
- [ ] V006-092 Store every candidate under the owning restoration with stable identifiers.
- [ ] V006-093 Preserve rejected-candidate diagnostics.
- [ ] V006-094 Add candidate selection and visibility controls.
- [ ] V006-095 Prevent candidate generation from modifying previously approved artifacts until replacement is accepted.
- [ ] V006-096 Release all temporary evaluated meshes and intermediate data after success, failure, or cancellation.

## Candidate Validation, Scoring, and Ranking

- [ ] V006-097 Validate margin correspondence and deviation.
- [ ] V006-098 Validate seal-band continuity and width.
- [ ] V006-099 Validate insertion-path clearance using the approved axis.
- [ ] V006-100 Validate achieved gaps by region.
- [ ] V006-101 Detect self-intersections.
- [ ] V006-102 Validate normals, boundary loops, manifoldness, and degeneracy.
- [ ] V006-103 Validate source and generated feature-size limits.
- [ ] V006-104 Compute normalized margin-fidelity objective.
- [ ] V006-105 Compute normalized insertion-clearance objective.
- [ ] V006-106 Compute normalized relief-target objective.
- [ ] V006-107 Compute normalized continuity and smoothness objective.
- [ ] V006-108 Compute topology, intersection, complexity, and runtime penalties.
- [ ] V006-109 Reject candidates before ranking when a blocking constraint fails.
- [ ] V006-110 Rank accepted candidates with stable tie-breaking.
- [ ] V006-111 Report ranking ambiguity when accepted scores are materially close.

## Constrained Correction and Override

- [ ] V006-112 Add Start correction-session behavior.
- [ ] V006-113 Snapshot selected candidate geometry, settings, diagnostics, and approval state.
- [ ] V006-114 Add exact Reset behavior while keeping the session active.
- [ ] V006-115 Add exact Cancel behavior and draft cleanup.
- [ ] V006-116 Add bounded localized offset correction.
- [ ] V006-117 Add boundary-preserving bounded smoothing.
- [ ] V006-118 Add seal-band reprojection to the approved margin.
- [ ] V006-119 Add constrained candidate switching or local regeneration.
- [ ] V006-120 Add Capture and Apply behavior.
- [ ] V006-121 Revalidate all constraints after Apply.
- [ ] V006-122 Invalidate direct out-of-session edits.
- [ ] V006-123 Add explicit expert-override metadata and warning gate.
- [ ] V006-124 Prevent override from suppressing structural blocking errors.

## Validation and Approval

- [ ] V006-125 Validate Step 1–4 upstream state.
- [ ] V006-126 Validate target, margin, axis, analysis, and ownership dependencies.
- [ ] V006-127 Validate settings ranges and finiteness.
- [ ] V006-128 Validate managed die, blockout, and candidate artifacts.
- [ ] V006-129 Validate candidate source identity and current signatures.
- [ ] V006-130 Separate blocking errors from engineering warnings.
- [ ] V006-131 Require explicit review of die, blockout, seal band, and crown bottom.
- [ ] V006-132 Require warning acknowledgment when warnings exist.
- [ ] V006-133 Require a fresh validation pass before approval.
- [ ] V006-134 Store approved candidate, settings, metrics, policy versions, and signatures.
- [ ] V006-135 Synchronize aggregate completion only after all restorations are approved.

## Invalidation, Monitoring, and Cleanup

- [ ] V006-136 Invalidate Step 5 after Step 1–4 changes.
- [ ] V006-137 Scope margin changes to the owning restoration where possible.
- [ ] V006-138 Invalidate after target replacement or material target changes.
- [ ] V006-139 Invalidate after insertion-axis or Step 4 analysis changes.
- [ ] V006-140 Mark generated geometry stale after any Step 5 setting change.
- [ ] V006-141 Detect missing, renamed, reparented, or ownership-corrupted artifacts.
- [ ] V006-142 Detect direct generated-mesh edits outside a managed session.
- [ ] V006-143 Recover valid pointers from ownership metadata.
- [ ] V006-144 Remove one restoration's Step 5 artifacts without affecting others.
- [ ] V006-145 Remove all Step 5 artifacts during confirmed case reset.
- [ ] V006-146 Preserve unrelated scene objects, materials, collections, and transforms.

## Migration

- [ ] V006-147 Add safe v0.0.5 Step 5 defaults.
- [ ] V006-148 Create no Step 5 artifact on file open or migration.
- [ ] V006-149 Preserve all Step 1–4 state and approvals.
- [ ] V006-150 Handle missing or obsolete in-branch Step 5 policy versions safely.

## User Interface

- [ ] V006-151 Display aggregate Step 5 status and restoration progress.
- [ ] V006-152 Display active restoration identity and upstream readiness.
- [ ] V006-153 Display grouped gap, spacer, relief, seal-band, blockout, and resolution settings.
- [ ] V006-154 Add Generate Candidates and Cancel controls.
- [ ] V006-155 Display generation progress and bounded-policy information.
- [ ] V006-156 Display candidate list, rank, score, status, and rejection reason.
- [ ] V006-157 Add die, blockout, seal-band, and crown-bottom visibility/focus controls.
- [ ] V006-158 Display geometry metrics and constraint outcomes.
- [ ] V006-159 Display errors, warnings, and non-clinical disclaimer.
- [ ] V006-160 Add constrained-correction session controls.
- [ ] V006-161 Add explicit review, warning acknowledgment, and approval controls.
- [ ] V006-162 Verify normal Sidebar-width readability.

## Packaging and Verification

- [ ] V006-163 Add all Step 5 modules to `blender_manifest.toml`.
- [ ] V006-164 Run Blender Python syntax validation.
- [ ] V006-165 Validate the extension manifest.
- [ ] V006-166 Build `b_dental-0.0.6.zip`.
- [ ] V006-167 Inspect package contents.
- [ ] V006-168 Install and enable the package.
- [ ] V006-169 Verify repeated enable, disable, restart, and reload.
- [ ] V006-170 Verify v0.0.5 migration.
- [ ] V006-171 Re-run Step 1 regression scenarios.
- [ ] V006-172 Re-run Step 2 regression scenarios.
- [ ] V006-173 Re-run Step 3 regression scenarios.
- [ ] V006-174 Re-run Step 4 regression scenarios.
- [ ] V006-175 Execute the complete Step 5 scenario matrix.
- [ ] V006-176 Verify deterministic repeat generation.
- [ ] V006-177 Verify bounded runtime, cancellation, and temporary-data cleanup.
- [ ] V006-178 Verify imported scan and upstream artifact safety.
- [ ] V006-179 Record implementation results, defects, corrections, and deviations.
- [ ] V006-180 Update README after acceptance.
- [ ] V006-181 Mark PRD, plan, decisions, tasks, and verification complete after local verification.
- [ ] V006-182 Prepare a non-draft PR for **Squash and merge**.

## Completion Record

This checklist remains planned until implementation and local verification are complete. No task may be marked complete solely because code exists; acceptance requires the relevant verification scenario to pass.