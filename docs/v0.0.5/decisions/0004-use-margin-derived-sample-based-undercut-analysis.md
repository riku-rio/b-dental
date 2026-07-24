# Decision 0004: Use Margin-Derived Sample-Based Undercut Analysis

## Metadata

- **Version:** v0.0.5
- **Status:** Accepted
- **Related requirements:** [`../PRD.md`](../PRD.md)
- **Related plan:** [`../plans/0001-preparation-analysis-insertion-axis.md`](../plans/0001-preparation-analysis-insertion-axis.md)

## Context

The MVP needs preparation analysis before crown-bottom design, but it does not yet include tooth segmentation, die extraction, survey-line generation, or mesh repair.

Analyzing the entire jaw would include excessive adjacent anatomy and create unnecessary cost. Modifying the scan to isolate a preparation would violate the project's non-destructive workflow.

## Decision

- Define an analysis neighborhood from the approved margin.
- Use the arithmetic mean of approved target-local margin points as the initial center, projected to the target surface when required.
- Derive the default analysis radius from margin extent and clamp it to a documented engineering range.
- Allow the user to adjust the radius before analysis.
- Select deterministic evaluated-mesh samples inside the neighborhood.
- Bound sample count and computation time.
- Use the direction opposite the stored seating axis as the removal direction.
- For each sample, test whether movement along the removal direction is blocked by another target surface after a scale-aware self-intersection offset.
- Store analyzed count, undercut count, ratio, mean blocking depth, and maximum blocking depth.
- Display clear and undercut samples through a non-destructive overlay.
- Do not write scan coordinates, topology, materials, color attributes, or other mesh data.
- Treat the result as an engineering approximation rather than segmented clinical anatomy.

## Rationale

A margin-derived neighborhood focuses computation near the preparation while preserving imported geometry. Deterministic bounded sampling is suitable for the MVP, supports reproducible metrics, and avoids requiring third-party geometry libraries.

## Rejected Alternatives

- **Analyze the entire jaw:** rejected because adjacent teeth and soft-tissue geometry would dominate results and runtime.
- **Automatically segment the preparation:** rejected because reliable segmentation is outside scope.
- **Create a destructive trimmed die:** rejected because scan editing violates the current workflow contract.
- **Use only face-normal angle tests:** rejected because orientation alone does not prove that removal is geometrically blocked.
- **Generate permanent colored mesh attributes:** rejected because analysis visualization must not alter imported data.
- **Require third-party geometry packages:** rejected because extension packaging currently uses Blender and the Python standard library only.

## Consequences

- Analysis quality depends on neighborhood radius and sampling density.
- Adjacent anatomy may still enter the neighborhood and must be disclosed as a limitation.
- Analysis signatures must include target, margin, axis, radius, and sampling settings.
- Radius or axis changes invalidate the result.
- Verification must include determinism, bounded runtime, self-hit avoidance, clear cases, and obstructed cases.
- Later segmentation may replace neighborhood sampling without changing the approved axis contract.