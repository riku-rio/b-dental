# Plan 0001: Automated Preparation Die & Crown Bottom

## Metadata

- **Version:** v0.0.6
- **Status:** Planned
- **Target branch:** `feat/v0.0.6-automated-preparation-die-crown-bottom`
- **Target merge branch:** `main`
- **Merge strategy:** Squash and merge
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related tasks:** [`../TASKS.md`](../TASKS.md)
- **Related verification:** [`../VERIFICATION.md`](../VERIFICATION.md)
- **Related decisions:**
  - [`../decisions/0001-use-restoration-owned-non-destructive-step-five-artifacts.md`](../decisions/0001-use-restoration-owned-non-destructive-step-five-artifacts.md)
  - [`../decisions/0002-derive-the-preparation-region-from-the-approved-margin.md`](../decisions/0002-derive-the-preparation-region-from-the-approved-margin.md)
  - [`../decisions/0003-use-an-insertion-axis-aligned-accessible-envelope-for-blockout.md`](../decisions/0003-use-an-insertion-axis-aligned-accessible-envelope-for-blockout.md)
  - [`../decisions/0004-use-a-region-aware-continuous-relief-field.md`](../decisions/0004-use-a-region-aware-continuous-relief-field.md)
  - [`../decisions/0005-require-a-continuous-margin-correspondent-seal-band.md`](../decisions/0005-require-a-continuous-margin-correspondent-seal-band.md)
  - [`../decisions/0006-rank-only-candidates-that-pass-blocking-constraints.md`](../decisions/0006-rank-only-candidates-that-pass-blocking-constraints.md)
  - [`../decisions/0007-limit-manual-work-to-reversible-constrained-correction.md`](../decisions/0007-limit-manual-work-to-reversible-constrained-correction.md)

## Objective

Implement Step 5 as an automation-first, per-restoration workflow that generates a preparation die, insertion-axis-aware undercut blockout, continuous seal band, and measurable crown-bottom candidates from approved Step 3 and Step 4 state.

## Proposed Source Structure

```text
extension/
├── __init__.py
├── crown_bottom_candidates.py
├── crown_bottom_geometry.py
├── crown_bottom_overlay.py
├── crown_bottom_scoring.py
├── preparation_die.py
├── preparation_region.py
├── relief_field.py
├── seal_band.py
├── step_five_operators.py
├── step_five_session.py
├── step_five_validation.py
├── axis_geometry.py
├── preparation_analysis.py
├── properties.py
├── restoration_utils.py
├── scene_utils.py
├── blender_manifest.toml
└── ui.py
```

Exact module boundaries may change during implementation, but state, geometry construction, scoring, validation, sessions, operators, and viewport display should remain separated.

## Architecture

### Persistent State

Extend each restoration with:

- Step 5 status and validity;
- generation settings and schema versions;
- preparation-die and blocked-die pointers;
- candidate collection metadata;
- selected candidate identifier;
- scores, ranks, rejection reasons, metrics, iterations, and runtime;
- correction-session snapshots;
- diagnostics, review, warning acknowledgment, and approval signatures.

Extend workflow state with aggregate Step 5 status and validity.

### Authoritative Geometry Inputs

Use only current approved upstream data:

- evaluated target scan;
- approved ordered margin;
- approved target-local insertion axis;
- current Step 4 dependency signature and analysis;
- current Step 5 settings.

Generated objects are outputs and interaction artifacts, not substitutes for upstream state.

### Evaluated Mesh Handling

Use Blender's evaluated dependency graph and temporary mesh copies for source evaluation. Convert geometry to a deterministic triangulated representation for traversal, BVH queries, metrics, and signature generation. Always release temporary evaluated meshes after success, failure, or cancellation.

### Preparation Region

Build a deterministic target-surface graph and map the approved margin to stable surface anchors. Extract one bounded surface patch using margin-boundary classification plus insertion-axis-aware filtering. Reject ambiguous, open, branching, or multi-region results instead of guessing.

### Preparation Die

Duplicate the accepted patch into a managed mesh, regularize only within bounded policy, construct axis-aligned side walls below the margin, and cap the base. Preserve margin correspondence and record topology metrics.

### Blockout

Transform the problem into an insertion-axis-aligned domain. Construct the accessible preparation envelope along the approved seating/removal direction, apply blockout clearance, and reconstruct a bounded blocked surface. Validate the result by repeating path-obstruction tests against generated geometry.

### Relief Field

Compute distance from the approved margin and classify internal regions. Build a continuous scalar offset field with distinct seal, transition, axial, and occlusal targets. Apply offset along stable surface directions, then detect inversion, folding, and local collapse.

### Seal Band

Construct one margin-correspondent band from the approved margin loop to the relieved internal surface. Preserve ordered correspondence and reject gaps, branches, flipped faces, self-intersections, or insufficient width.

### Candidate Generation

Generate a primary candidate and only a small bounded set of documented variants. Candidates must have stable identifiers and ownership metadata. Never replace a previously approved candidate until a new candidate is approved.

### Validation and Scoring

Evaluate blocking constraints first. Only accepted candidates receive a rank. The score combines normalized objective terms for margin fidelity, path clearance, relief accuracy, continuity, smoothness, topology quality, complexity, and runtime. Stable tie-breaking ensures reproducible ranking.

### Correction Sessions

Provide reversible, managed correction sessions with Start, Reset, Cancel, Capture, and Apply. Allowed operations are bounded and boundary-preserving. Applying changes clears validation and approval and requires the complete validation pipeline again.

## Implementation Phases

### Phase 1 — State, Migration, and Workflow Contract

- Add Step 5 workflow and restoration properties.
- Add safe v0.0.5 migration defaults.
- Add entry, return, restoration-switch, and session gating.
- Add settings validation and aggregate synchronization.

### Phase 2 — Geometry and Ownership Foundations

- Add evaluated-mesh and deterministic triangulation helpers.
- Add point, direction, scale, tolerance, and signature helpers.
- Add managed Step 5 artifact metadata, recovery, visibility, and cleanup.
- Add generated-mesh change detection.

### Phase 3 — Preparation-Region Extraction

- Map approved margin points to source-surface anchors.
- Build adjacency and boundary classification.
- Extract one bounded preparation patch.
- Add ambiguity and adjacent-anatomy diagnostics.
- Verify target-scan safety and deterministic repetition.

### Phase 4 — Preparation Die

- Duplicate the extracted patch.
- Preserve and regularize the margin boundary.
- Generate insertion-axis-aligned walls and base cap.
- Validate topology, normals, closure, and ownership.

### Phase 5 — Undercut Blockout

- Build the insertion-axis-aligned accessible envelope.
- Apply blockout clearance.
- Reconstruct blocked geometry.
- Verify residual path obstruction and reject invalid results.

### Phase 6 — Relief Field and Seal Band

- Compute distance-from-margin and region classification.
- Apply marginal, cement, axial, and occlusal relief targets.
- Smooth bounded transitions.
- Construct and validate the continuous seal band.

### Phase 7 — Candidate Generation and Ranking

- Generate the primary crown-bottom candidate.
- Generate bounded variants when policy allows.
- Compute geometry metrics and blocking constraints.
- Score and rank accepted candidates deterministically.
- Preserve rejected-candidate diagnostics.

### Phase 8 — Correction, Validation, and Approval

- Add reversible constrained correction sessions.
- Add direct-edit detection and explicit override metadata.
- Add structured errors and warnings.
- Require visual review, acknowledgment, fresh validation, and independent approval.

### Phase 9 — Invalidation, Cleanup, and UI

- Monitor upstream and generated dependencies.
- Add scoped invalidation and pointer recovery.
- Extend case reset and restoration removal cleanup.
- Add Step 5 controls, progress, metrics, candidate list, visibility, diagnostics, correction, and approval UI.

### Phase 10 — Packaging and Verification

- Update manifest version and module paths.
- Run syntax and manifest validation.
- Build and inspect `b_dental-0.0.6.zip`.
- Install and verify lifecycle behavior.
- Execute migration, Step 1–4 regression, and the complete Step 5 matrix.
- Record performance, defects, corrections, limitations, and deviations.
- Update README and mark release documents complete only after acceptance.

## Initial Settings Contract

The implementation should define explicit defaults and accepted ranges after fixture-based engineering review. Settings must remain user-visible and non-clinical. The initial state model includes:

- marginal gap;
- cement gap;
- spacer-start distance;
- axial relief;
- occlusal relief;
- seal-band width;
- blockout clearance;
- source/candidate sampling resolution;
- transition smoothing strength;
- maximum candidate count;
- maximum iterations and runtime policy.

Changing any material setting invalidates current generation, validation, and approval.

## Failure Strategy

The generator must fail explicitly when it cannot construct safe geometry. It must not silently fill holes, merge unrelated regions, ignore residual undercuts, suppress self-intersections, or approve the visually closest candidate.

On failure or cancellation:

- upstream state remains untouched;
- an existing approved candidate remains authoritative;
- temporary meshes and objects are removed;
- diagnostics identify the failed phase and measurable reason;
- aggregate Step 5 validity remains false unless an earlier approved candidate is still current.

## Safety Requirements

- Never modify imported scan data.
- Never modify approved margin, antagonist, axis, or Step 4 analysis artifacts.
- Scope every managed artifact to one restoration.
- Preserve unrelated objects and collections.
- Reject stale, foreign, or corrupted artifacts.
- Keep all generation bounded and deterministic.
- Separate engineering validation from clinical correctness.

## Performance Strategy

Performance should be bounded through:

- preparation-region-local geometry rather than full-arch processing where possible;
- deterministic sample caps;
- BVH acceleration;
- bounded candidate count;
- bounded smoothing and optimization iterations;
- reusable immutable source representations inside one generation run;
- explicit cancellation checkpoints between phases.

Representative performance must be recorded during verification, but no fixed target is accepted until real fixtures are measured.

## Completion Definition

The plan is complete only when:

- Step 5 state persists safely;
- every restoration can independently generate, inspect, correct, validate, and approve a crown-bottom candidate;
- preparation extraction, die construction, blockout, relief, and seal-band generation are deterministic and non-destructive;
- invalid geometry is rejected explicitly;
- candidate ranking is measurable and reproducible;
- aggregate completion requires all restorations;
- v0.0.5 migration and Step 1–4 regressions pass;
- package, lifecycle, performance, cancellation, persistence, cleanup, UI, and scan-safety verification pass;
- implementation results and limitations are documented.