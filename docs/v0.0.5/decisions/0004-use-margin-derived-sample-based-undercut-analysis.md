# Decision 0004: Use Margin-Derived Sample-Based Undercut Analysis

## Metadata

- **Version:** v0.0.5
- **Status:** Accepted and Implemented
- **Verification:** Passed locally
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-preparation-analysis-insertion-axis.md`](../plans/0001-preparation-analysis-insertion-axis.md)

## Context

The MVP needs preparation analysis before crown-bottom design, but it does not include tooth segmentation, die extraction, survey-line generation, or mesh repair.

Analyzing the entire jaw would include excessive adjacent anatomy and unnecessary cost. Modifying the scan to isolate a preparation would violate the non-destructive workflow.

## Decision

- Define an analysis neighborhood from the approved margin.
- Use the arithmetic mean of approved target-local margin points as the initial center and project to the target surface when required.
- Derive the default radius from margin extent and clamp it to the documented engineering range.
- Allow the user to adjust the radius before analysis.
- Select deterministic evaluated-mesh triangle-center samples inside the neighborhood.
- Perform radius selection, acceleration geometry, axis conversion, ray casting, and depth measurement in Blender world space.
- Bound sample count and processing time.
- Use the direction opposite the stored seating axis as the removal direction.
- Ignore immediate self-intersection using a scale-aware offset.
- Store analyzed count, undercut count, ratio, mean blocking depth, maximum blocking depth, and duration.
- Convert sample positions back to target-local coordinates for persistent overlay data.
- Display clear and undercut samples through a non-destructive overlay.
- Do not write scan coordinates, topology, materials, color attributes, or other mesh data.
- Treat the result as an engineering approximation rather than segmented clinical anatomy.

## Rationale

A margin-derived neighborhood focuses computation near the preparation while preserving imported geometry. Deterministic bounded sampling supports reproducible metrics without third-party geometry packages.

World-space sampling makes the radius and measured depths physically consistent for imported scans with non-identity object scale while retaining the target-local authoritative axis and persistent sample representation.

## Rejected Alternatives

- **Analyze the entire jaw:** rejected because adjacent teeth and soft tissue would dominate results and runtime.
- **Automatically segment the preparation:** rejected because reliable segmentation is outside scope.
- **Create a destructive trimmed die:** rejected because scan editing violates the workflow contract.
- **Use only face-normal angle tests:** rejected because orientation alone does not prove geometric blocking.
- **Generate permanent colored mesh attributes:** rejected because visualization must not alter imported data.
- **Require third-party geometry packages:** rejected because packaging uses Blender and the Python standard library only.
- **Compare a world-unit radius directly with target-local coordinates:** rejected after verification exposed scale-dependent empty neighborhoods.

## Consequences

- Analysis quality depends on neighborhood radius and sampling density.
- Adjacent anatomy may enter the neighborhood and is disclosed as a warning.
- Analysis signatures include target, margin, axis, radius, settings, and sampling-policy version.
- Radius or axis changes invalidate the result.
- Sampling-policy changes invalidate earlier development results.
- Later segmentation may replace neighborhood sampling without changing the approved axis contract.

## Implementation and Verification Record

Implemented in `preparation_analysis.py`, `axis_geometry.py`, `axis_overlay.py`, and `step_four_validation.py`.

Local verification found and corrected the initial local/world coordinate mismatch. Retesting confirmed deterministic bounded samples, correct behavior with imported scan scale, clear and obstructed cases, axis sensitivity, self-hit avoidance, finite metrics, non-destructive overlays, and representative processing of 2,000 samples in approximately 0.354 seconds.
