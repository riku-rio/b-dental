# Product Requirements Document: v0.0.6

## Document Information

- **Product:** B-Dental
- **Version:** v0.0.6
- **Status:** Planned
- **Target branch:** `feat/v0.0.6-automated-preparation-die-crown-bottom`
- **Target merge branch:** `main`
- **Workflow stage:** Step 5 — Automated Preparation Die & Crown Bottom
- **Merge strategy:** Squash and merge

## Product Overview

B-Dental v0.0.6 adds the first production restoration-geometry stage. It consumes approved Step 3 margins and approved Step 4 insertion-axis analysis to generate a non-destructive preparation die, an insertion-axis-aware blocked-out preparation, and one or more crown-bottom or intaglio candidates.

The normal supported workflow is automation-first. The user configures bounded engineering settings, requests generation, reviews measurable results and warnings, and approves a candidate. Manual work is limited to constrained correction or explicit expert override.

## Product Goal

For every approved single-unit anatomical crown restoration, automatically produce a persistent and reviewable internal restoration foundation that:

1. Reconstructs a bounded preparation die from the approved margin and target scan.
2. Removes path-of-insertion undercuts without modifying the imported scan.
3. Applies configurable marginal and internal relief zones.
4. Produces a continuous margin seal band.
5. Generates a crown-bottom candidate suitable for the later anatomy stage.
6. Measures geometric quality and rejects invalid candidates explicitly.
7. Preserves deterministic settings, dependency signatures, ownership, and reproducibility.

Step 5 is complete only when at least one restoration exists and every Step 4-approved restoration has an independently approved Step 5 candidate.

## Accepted Scope

Version v0.0.6 includes:

- Step 5 entry only after aggregate Step 4 approval.
- Independent persistent Step 5 state for every restoration.
- One non-destructive preparation-die artifact per restoration.
- One insertion-axis-aware blockout artifact per restoration.
- One or more generated crown-bottom candidates per restoration, with one selected candidate.
- Configurable engineering settings for:
  - marginal gap;
  - cement gap;
  - spacer-start distance from the margin;
  - axial relief;
  - occlusal relief;
  - seal-band width;
  - blockout clearance;
  - candidate resolution and bounded optimization policy.
- Deterministic preparation-region extraction from the approved margin and target surface.
- Automatic side-wall and cap construction for the preparation die.
- Automatic undercut blockout along the approved insertion axis.
- Region-aware relief field generation.
- Continuous seal-band construction and validation.
- Candidate scoring, ranking, rejection, and explicit failure reporting.
- Per-candidate metrics, warnings, dependency signatures, settings snapshots, and runtime records.
- Non-destructive viewport display and visibility controls.
- Constrained correction and override sessions that operate only on managed Step 5 artifacts.
- Explicit visual review, warning acknowledgment, validation, and per-restoration approval.
- Aggregate Step 5 completion derived from all restorations.
- Safe migration from v0.0.5 with empty Step 5 defaults and no automatically generated artifacts.
- Packaging as extension version `0.0.6`.

## Out of Scope

Version v0.0.6 does not include:

- Automatic margin detection or correction.
- Automatic insertion-axis search or clinical axis selection.
- Crown external anatomy, tooth libraries, cusp or ridge generation.
- Proximal contact or occlusal optimization.
- Final shell joining, manufacturing export, sprues, supports, or nesting.
- Bridges, implant restorations, veneers, inlays, onlays, dentures, orthodontic appliances, or multi-unit restorations.
- Destructive editing of imported scans, approved margins, or Step 4 artifacts.
- Unbounded freeform sculpting as the primary workflow.
- Clinical certification of fit or manufacturability.
- Third-party Python dependencies unless separately accepted.

## Workflow Preconditions

Entering Step 5 requires:

- An initialized case.
- Valid Step 1.
- Approved Step 2.
- Aggregate Step 3 status `VERIFIED`.
- Aggregate Step 4 status `VERIFIED`.
- At least one restoration.
- For every restoration:
  - a valid approved margin;
  - a valid approved insertion axis;
  - a current Step 4 analysis result;
  - no active margin or axis edit session.

Entering Step 5 must not modify scans, transforms, materials, approved margins, antagonist regions, insertion axes, or Step 4 analysis data.

## Authoritative Inputs

The authoritative inputs for each restoration are:

- target preparation scan and its current evaluated geometry;
- approved ordered margin points;
- approved target-local insertion axis;
- current source-unit scale;
- current Step 3 and Step 4 dependency signatures;
- current Step 5 settings.

Viewport artifacts, object names, transient selections, and display state are not authoritative inputs.

## Persistent State

Each restoration stores:

- Step 5 status and validity.
- Generation settings and their schema version.
- Preparation-die, blocked-die, and crown-bottom object pointers.
- Candidate collection metadata, selected candidate identifier, rank, and score.
- Generation state, runtime, iteration count, and policy version.
- Geometry metrics and constraint results.
- Errors, warnings, summary, review confirmation, and warning acknowledgment.
- Approved candidate identifier, settings snapshot, metrics snapshot, and dependency signatures.
- Constrained-correction session snapshots when applicable.

Aggregate Step 5 status and validity are derived from the restoration collection.

## Geometry Contract

### Preparation Region

The approved margin defines the preparation-region boundary. The implementation must derive a bounded target-surface patch without automatic tooth segmentation by using deterministic surface traversal and insertion-axis-aware filtering.

The extracted patch must:

- remain associated with the owning restoration;
- include the preparation surface inside the approved margin;
- exclude unrelated target geometry where deterministically possible;
- preserve a reproducible ordered boundary corresponding to the approved margin;
- fail explicitly when a stable bounded patch cannot be constructed.

### Preparation Die

The preparation die is a managed duplicate derived from the target surface. It must not alter the target scan.

The die must include:

- the extracted preparation surface;
- a margin-aligned boundary;
- insertion-axis-aware side walls below the margin;
- a closed base cap;
- consistent normals and manifold topology where the source allows it.

### Undercut Blockout

The blocked die is derived from the preparation die along the approved insertion axis.

For each crown-bottom sample, the blocked surface represents the first accessible envelope along the seating or removal path, with configurable blockout clearance. The result must eliminate inaccessible internal concavities relative to the approved path of insertion without changing authoritative upstream geometry.

### Relief Field

The internal offset is not one uniform distance. It is a deterministic field based on distance from the approved margin and surface classification.

Required regions:

1. **Margin seal region:** zero or marginal-gap relief only.
2. **Spacer transition:** smooth bounded transition starting at the configured spacer-start distance.
3. **Axial region:** cement gap plus axial relief.
4. **Occlusal region:** cement gap plus occlusal relief.

The field must be continuous within configured tolerances and must not introduce inverted offsets, folds, or discontinuities.

### Margin Seal Band

A continuous seal band must be generated around the full approved margin loop.

The band must:

- be topologically continuous;
- preserve the ordered margin correspondence;
- satisfy configured width and gap targets within tolerance;
- avoid gaps, branch points, flipped segments, and self-intersections;
- connect continuously to the relieved internal surface.

### Crown-Bottom Candidate

A candidate is a managed internal surface bounded by the seal band and generated from the blocked die plus the relief field.

A candidate must be rejected when any blocking constraint fails. Rejected candidates may retain diagnostic metadata but must not be eligible for approval.

## Candidate Generation and Ranking

The generator may produce one or more bounded candidates by varying accepted policy parameters such as sampling resolution, transition smoothing strength, or blockout strategy.

Candidate generation must:

- use deterministic ordering;
- use bounded runtime, iteration count, and candidate count;
- produce identical results for unchanged inputs and settings unless a documented fixed seed is used;
- preserve rejected-candidate reasons;
- rank accepted candidates using explicit normalized objective terms.

The initial score should include:

- margin fidelity;
- seal-band continuity;
- insertion-path clearance;
- relief-target error;
- surface continuity and smoothness;
- self-intersection penalty;
- topology and manifoldness penalty;
- candidate complexity and runtime penalty.

No hidden visual-only heuristic may silently override a blocking geometric constraint.

## Required Metrics

At minimum, each candidate records:

- source and generated vertex, edge, and face counts;
- margin sample count and correspondence coverage;
- maximum and mean margin deviation;
- seal-band continuity state and minimum band width;
- mean and maximum gap by region;
- insertion-path collision count and maximum blocking depth;
- self-intersection count or detected state;
- boundary-loop count;
- non-manifold edge count;
- degenerate face count;
- minimum local feature size supported by the implementation;
- optimization iterations;
- generation duration;
- final score and rejection reasons.

Thresholds are engineering defaults and must be documented as non-clinical.

## Validation and Warnings

Blocking errors include:

- invalid upstream state;
- missing, stale, or changed target, margin, axis, or Step 4 analysis;
- active upstream edit session;
- invalid or non-finite settings;
- inability to derive one bounded preparation patch;
- missing or corrupt managed artifacts;
- open or branching margin correspondence;
- discontinuous seal band;
- insertion-path obstruction above tolerance;
- self-intersection;
- invalid normals, degenerate geometry, or non-manifold topology beyond accepted repair policy;
- stale settings or dependency signatures;
- selected candidate not generated by the owning restoration.

Engineering warnings include:

- low source resolution;
- weak preparation-region separation from adjacent anatomy;
- relief values near configured bounds;
- high smoothing or repair demand;
- small local feature size;
- large margin deviation still within warning tolerance;
- candidate ranking ambiguity;
- high runtime near the bounded limit;
- geometry suitable only for constrained expert review.

## Constrained Correction and Override

Manual editing is not the default generation path.

A constrained correction session may permit only accepted operations on managed Step 5 artifacts, such as:

- localized offset adjustment inside bounded distance limits;
- seal-band reprojection to the approved margin;
- bounded smoothing that preserves the boundary and insertion-path constraints;
- switching between generated candidates;
- regenerating a local region from current settings.

The session must support Start, Reset, Cancel, Capture, and Apply. Apply invalidates previous validation and approval. Direct edits outside an active managed session must invalidate the candidate and surface a blocking error.

An expert override must be explicit, recorded, warning-gated, and must never suppress objective validation failures that make the candidate structurally unusable.

## Approval

Approval is independent for each restoration and requires:

- no blocking errors;
- a selected current candidate;
- current settings and dependency signatures;
- completed geometric validation;
- explicit visual review of the die, blockout, seal band, and crown bottom;
- warning acknowledgment when warnings exist;
- no active correction session.

Approval stores the selected candidate, settings, metrics, policy versions, and dependency signatures. Aggregate `step_5_valid` becomes true only after every restoration is independently verified.

## Invalidation and Cleanup

- Step 1–4 invalidation clears aggregate Step 5 validity.
- Margin changes invalidate only the owning restoration where possible.
- Target replacement invalidates dependent Step 5 state and removes unsafe generated artifacts.
- Axis or Step 4 analysis changes invalidate blockout and all crown-bottom candidates.
- Any Step 5 setting change clears current validation and approval and marks generated results stale.
- Missing, manually modified, or ownership-corrupted artifacts invalidate safely.
- Removing a restoration removes only its Step 5 artifacts.
- Case reset removes all B-Dental-managed Step 5 artifacts while preserving unrelated scene content.

## Migration

Existing v0.0.5 files open with safe empty Step 5 defaults. No die, blockout, candidate, or correction artifact is created automatically. Existing scans, restorations, margins, antagonist regions, axes, analyses, approvals, and transforms remain preserved.

## Performance and Safety Boundaries

- Generation and validation must be bounded by explicit sample, iteration, candidate-count, and runtime policies.
- Long-running work must report progress and remain cancel-safe where Blender permits.
- Failure or cancellation must not replace a previously approved candidate or modify upstream geometry.
- Temporary meshes and evaluated-mesh copies must be released safely.
- Managed objects must carry ownership and schema metadata.
- The implementation must use Blender-supported APIs and remain compatible with Blender 4.2 or newer.

## Acceptance Criteria

Version v0.0.6 is accepted when:

1. v0.0.5 scenes migrate with empty Step 5 state and no generated artifacts.
2. Step 5 remains inaccessible until every restoration has approved Step 3 and Step 4 state.
3. Every restoration has independent Step 5 settings, artifacts, validation, and approval.
4. Preparation-region extraction is deterministic, bounded, and fails safely.
5. Preparation-die generation is non-destructive and restoration-owned.
6. Undercut blockout follows the approved insertion axis and removes path obstruction within tolerance.
7. Relief zones implement marginal gap, spacer start, cement gap, axial relief, and occlusal relief.
8. The seal band is continuous and margin-correspondent.
9. Candidate generation is deterministic, bounded, measurable, and reproducible.
10. Invalid candidates are rejected with explicit reasons.
11. Candidate ranking uses documented objective terms.
12. Constrained correction is reversible and cannot silently bypass validation.
13. Imported scans and approved upstream artifacts remain unchanged.
14. Stale or manually corrupted state invalidates safely.
15. Aggregate completion requires every restoration.
16. Step 1–4 regression scenarios pass.
17. Manifest validation, package build, installation, lifecycle, migration, full Step 5 scenario verification, and scan-safety checks pass locally.

## Completion Definition

The release is complete only after implementation, packaging, local verification, documentation updates, and a non-draft pull request prepared for **Squash and merge**.