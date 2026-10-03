# EXP-001 Initial Findings

Date: 2026-10-03

The first read-only reconstruction of DevControl proves that convergence is a current operational problem, not a hypothetical future concern.

## Observed state

- 48 Git worktrees: 39 branch-attached, 9 detached, 7 locked.
- 44 local branches.
- Large concern clusters: MCP/protocol 11 branches; approval/tool-surface 10; release 6; browser 5; mobile 4.
- 22 initial mechanical risk signals were emitted. These are evidence candidates, not automatic deletion/merge decisions.
- Several branches are tens of commits behind their configured upstream; some exceed 100 commits.
- The primary DevControl working tree itself contains uncommitted changes, so EngineeringOS must never infer authoritative project state from one checkout alone.

## Important correction to the model

Branch age or divergence cannot by itself mean stale or superseded. Release branches, production snapshots, locked forensic worktrees, and intentional compatibility lines have different semantics. The World Model therefore needs typed workspaces and typed lineage before convergence automation.

## Next experiment

EXP-002 will build a lineage/overlap graph from merge-base, patch identity, changed-file overlap, commit containment, worktree lock state, and branch naming/version evidence. It remains read-only. Semantic conclusions will be separated from mechanical evidence.
