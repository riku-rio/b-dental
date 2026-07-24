# Local Verification: v0.0.4

## Document Status

- **Version:** v0.0.4
- **Status:** Passed
- **Target branch:** `feat/v0.0.4-restoration-setup-manual-margin-definition`
- **Target platform:** Windows
- **Shell:** PowerShell
- **Blender:** 5.0.x
- **Result:** Accepted

This record reflects the completed local verification reported for the v0.0.4 release candidate. Only de-identified dental fixtures were used.

## Package Result

- Manifest validation: **Passed**
- Extension build: **Passed**
- `b_dental-0.0.4.zip` creation: **Passed**
- Package-content inspection: **Passed**
- Installation from disk: **Passed**
- Enablement and registration: **Passed**
- Repeated enable, disable, restart, and reload: **Passed**
- Registration errors: **None observed**

Verified package modules include:

```text
__init__.py
antagonist_region.py
blender_manifest.toml
margin_geometry.py
margin_overlay.py
margin_validation.py
restoration_utils.py
step_three_operators.py
step_three_session.py
ui.py
```

## Migration and Regression Results

- v0.0.3 scene migration and safe empty Step 3 defaults: **Passed**
- Earlier in-branch single-restoration v0.0.4 migration: **Passed**
- Step 1 regression scenarios: **Passed**
- Step 2 regression scenarios: **Passed**
- Registration and lifecycle behavior: **Passed**

## Step 3 Results

The following scenario groups passed:

1. Step 3 entry gating and unchanged scans.
2. First restoration creation.
3. Multiple upper restorations.
4. Mixed upper and lower restorations.
5. Duplicate FDI target rejection.
6. Active-restoration switching and session gating.
7. Independent margin creation and ownership.
8. Target-only picking.
9. Modal drawing controls.
10. Independent reset, cancel, and apply behavior.
11. Margin editing and reprojection.
12. Per-restoration validation and diagnostics.
13. Independent review, warning acknowledgment, and approval.
14. Aggregate Step 3 completion.
15. Adding and removing restorations after aggregate completion.
16. Persistence after save and reopen.
17. Independent edit invalidation.
18. Upstream invalidation.
19. Target-scan replacement.
20. Metadata corruption isolation.
21. Case reset and unrelated-object preservation.
22. Scan matrix, topology, and coordinate safety.
23. UI readability at normal Sidebar width.
24. Margin visibility and viewport overlay behavior.

## Antagonist Region Results

- Automatic opposing-region detection from the margin location: **Passed**
- Manual pick restricted to the opposing scan: **Passed**
- Region radius adjustment: **Passed**
- Focus and visibility controls: **Passed**
- Region clearing and redefinition: **Passed**
- Required review before approval: **Passed**
- Single-arch not-applicable behavior: **Passed**
- Independent ownership across restorations: **Passed**
- Persistence after save and reopen: **Passed**
- Approval invalidation after region changes: **Passed**
- Approval invalidation after opposing-scan changes: **Passed**
- Safe per-restoration removal and case-reset cleanup: **Passed**

## Safety Record

Across the executed scenarios:

- Step 3 did not modify imported scan mesh coordinates or topology.
- Margin operations affected only the active restoration.
- Antagonist operations affected only the active restoration and resolved opposing scan.
- Removing one restoration preserved all unrelated restorations and objects.
- Failed, cancelled, or incomplete operations did not create false approval.
- Engineering validation remained separate from clinical correctness.

## Deviations and MVP Limits

- v0.0.4 trusts the user to select the correct FDI tooth and draw the margin on the intended preparation.
- Automatic tooth segmentation and tooth-number verification remain outside scope.
- Antagonist regions are engineering workflow markers, not extracted anatomical tooth segments.
- Insertion-axis, undercut, crown-bottom, cement-gap, anatomy, contact-adjustment, and export behavior remain deferred.

## Acceptance Record

All required package, migration, regression, Step 3, antagonist-region, persistence, invalidation, cleanup, and safety checks were completed successfully. v0.0.4 is accepted and ready for a non-draft pull request using **Squash and merge**.
