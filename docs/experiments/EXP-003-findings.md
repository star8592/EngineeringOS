# EXP-003 Initial Findings

Date: 2026-10-03

The first typed Convergence Debt pass keeps dimensions separate and preserves underlying evidence.

## Current pressure indicators

- Duplicate-state debt: 3 exact-head alias groups.
- Divergence debt: 17 active development branches are not contained in `origin/main` and are at least 20 commits behind it.
- Overlap debt: 4 independent branch pairs modify >=30% overlapping changed-path surfaces without an ancestor relationship.
- Role debt: 0 among branch-attached worktrees under the initial classifier; current roles are 34 development, 6 release, 2 documentation, 1 forensic.
- Dirty-workspace debt: 10 branch-attached worktrees contain uncommitted state, including one release workspace.
- Verification debt: deliberately `UNKNOWN`, not zero. CI, release, deployment, and production evidence are not yet joined to the World Model.

## Important finding

Unknown evidence must remain unknown. EngineeringOS must not convert absence of evidence into a healthy score. This is especially important for production verification and release qualification.

Dirty workspaces also require typed semantics: an active coding workspace may legitimately be dirty, while a release or production-reference workspace being dirty is a materially different condition.

## Next step

EXP-004 will add the Evidence Plane: GitHub/CI check state, release/version lineage, deployment references, production smoke evidence, and contract/spec-drift evidence. Only after those facts are joined can verification debt be computed.
