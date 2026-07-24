# B-Dental Product Roadmap

## Product Vision

B-Dental is an **automation-first dental CAD workflow for Blender**.

The long-term objective is to eliminate routine manual restoration design wherever a deterministic, geometry-driven, optimization-based, or Blender-native automated process can produce a safe and reviewable result.

The intended workflow is not a conventional manual CAD system with a collection of drawing and sculpting tools. It is a structured pipeline in which B-Dental:

1. Resolves and validates the available case data.
2. Generates restoration candidates automatically.
3. Optimizes geometry against explicit constraints.
4. Reports measurable errors, warnings, and trade-offs.
5. Presents the result for focused human review.
6. Requires manual intervention only when automation cannot produce an acceptable candidate or when the user intentionally overrides a result.

## Automation-First Principle

Every future production stage must answer this question first:

> Can this operation be generated, solved, fitted, or optimized automatically from the approved upstream state?

If the answer is yes, automatic generation is the primary workflow. Manual tools may exist as:

- A fallback for failed or ambiguous cases.
- A constrained correction mechanism.
- A debugging and verification aid.
- An explicit expert override.

Manual sculpting, unconstrained freeform editing, and repetitive point-by-point construction must not become the default workflow when Blender geometry tools, numerical optimization, search, fitting, projection, collision analysis, or deterministic procedural construction can perform the task.

## Technical Direction

Automation should be built primarily from:

- Blender mesh, curve, BVH, ray-casting, modifier, Geometry Nodes, and dependency-graph capabilities.
- Deterministic computational geometry.
- Constraint solving and bounded numerical optimization.
- Iterative fitting against preparation, margin, adjacent teeth, and antagonist geometry.
- Candidate scoring and measurable objective functions.
- Non-destructive managed artifacts.
- Dependency signatures, reproducible settings, and explicit invalidation.
- Structured validation before approval.

Third-party libraries may be considered in later releases only when their packaging, licensing, platform support, determinism, and maintenance costs are explicitly accepted.

## Human Role

The user remains responsible for:

- Confirming case inputs and restoration intent.
- Reviewing warnings and generated geometry.
- Accepting or rejecting automated candidates.
- Selecting between ranked candidates when the system cannot establish one unambiguous result.
- Applying constrained corrections or expert overrides when required.

The user should not be required to manually design the restoration surface from the beginning in a normal supported case.

## Completed Foundation

### v0.0.1 — Extension Foundation

- Modern Blender Extension package.
- Registration lifecycle and initial UI.

### v0.0.2 — Step 1: Scan Import

- Structured case initialization and managed scan inputs.

### v0.0.3 — Step 2: Occlusion Registration

- Deterministic alignment workflows and explicit approval.

### v0.0.4 — Step 3: Restoration Setup

- Restoration ownership, approved margins, and antagonist regions.
- Manual margin definition remains an early-stage input and a future automation target.

### v0.0.5 — Step 4: Preparation Analysis & Insertion Axis

- Persistent insertion axes.
- Bounded undercut analysis.
- Per-restoration validation and approval.

## Planned Production Roadmap

The exact scope of each release must still be accepted through a PRD, architectural decisions, implementation plan, tasks, and verification matrix.

### Step 5 — Automated Preparation Die & Crown Bottom

Primary goal: automatically generate the internal restoration foundation from approved Step 3 and Step 4 state.

Planned automation:

- Derive a non-destructive preparation die from the approved margin and target scan.
- Generate insertion-axis-aware undercut blockout automatically.
- Generate the crown-bottom or intaglio surface automatically.
- Apply configurable marginal gap, cement gap, spacer start, axial relief, and occlusal relief.
- Generate and validate a continuous margin seal band.
- Optimize internal geometry for path of insertion, continuity, and manufacturability.
- Rank or reject candidates using measurable geometric constraints.

Manual editing should be limited to constrained correction and override paths.

### Step 6 — Automated Crown Anatomy Proposal

Primary goal: generate the external crown form automatically rather than requiring manual sculpting.

Planned automation:

- Select or infer an initial anatomical template.
- Fit anatomy to the margin, crown bottom, available space, neighboring teeth, and arch context.
- Align cusp, ridge, emergence-profile, and contour features procedurally.
- Optimize the proposal against minimum-thickness and shape constraints.
- Produce one or more ranked candidate anatomies when appropriate.

### Step 7 — Automated Contact and Occlusion Optimization

Primary goal: automatically satisfy proximal and occlusal constraints.

Planned automation:

- Detect adjacent-tooth contact targets.
- Detect antagonist penetration, clearance, and occlusal contact regions.
- Adjust the external surface through bounded optimization.
- Preserve margin, crown bottom, insertion path, and minimum thickness.
- Report residual penetrations, excessive clearance, unresolved constraints, and optimization trade-offs.

The user reviews the optimized result instead of manually pushing contact surfaces into place.

### Step 8 — Automated Finalization & Manufacturing Validation

Primary goal: convert the approved optimized candidate into validated manufacturing output.

Planned automation:

- Join and finalize internal and external surfaces.
- Generate a watertight restoration shell.
- Repair safe topology defects automatically.
- Validate normals, manifoldness, self-intersections, minimum thickness, margin continuity, insertion path, and collision state.
- Produce explicit blocking errors and warnings.
- Export approved manufacturing geometry with reproducible settings and metadata.

## Cross-Cutting Automation Work

Automation is not limited to later crown stages. Future releases may replace earlier manual inputs when reliable approaches are available, including:

- Automatic tooth identification.
- Automatic preparation and tooth segmentation.
- Automatic margin detection with editable confidence-ranked candidates.
- Automatic insertion-axis search and optimization.
- Automatic antagonist-region detection.
- Automatic restoration-type inference where safe and explicit.

These upgrades must preserve the same contract: generated candidates are measurable, reproducible, non-destructive, reviewable, and never silently treated as clinically correct.

## Optimization Contract

Optimization features should use explicit objective terms and constraints rather than hidden visual heuristics alone. Depending on the stage, objectives may include:

- Margin fidelity.
- Seating and removal-path clearance.
- Cement-space targets.
- Minimum material thickness.
- Proximal contact location and strength.
- Occlusal penetration and clearance.
- Anatomical smoothness and continuity.
- Emergence profile.
- Surface quality and manufacturability.

Each optimization process must:

- Be bounded in runtime and iteration count.
- Preserve authoritative upstream geometry.
- Store settings and dependency signatures.
- Produce deterministic results when inputs and settings are unchanged, unless a documented seeded search is used.
- Expose failures and unresolved constraints rather than silently returning an invalid result.

## Product Success Definition

B-Dental reaches its intended product goal when a normal supported single-crown case can proceed from imported scans to a manufacturing-ready restoration through an automated pipeline where the user primarily:

- Confirms inputs.
- Reviews generated candidates.
- Selects or approves results.
- Intervenes manually only for exceptional or unsupported geometry.

The system should reduce manual dental CAD work, not reproduce the traditional manual-design workflow inside Blender.
