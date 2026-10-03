# EXP-002 Initial Findings

Date: 2026-10-03

Read-only lineage analysis compared 43 non-main local branches against `origin/main` and against related branches.

## Mechanical evidence

- 3 exact-head alias groups exist: multiple differently named work lines point at identical commits.
- 89 relationship candidates were found from ancestry, exact-head identity, or changed-path overlap.
- 21 non-main local branches are already commit-contained in `origin/main`. This does not itself authorize deletion: some are release, forensic, locked, or operational references.
- Four non-ancestor branch pairs have >= 0.30 changed-path overlap. These are high-value convergence-review candidates because they modify substantially overlapping surfaces without a simple lineage relationship.

Notable examples:

- `fix/auth-tool-surface-convergence-3.1.14` vs `work/tool-surface-approval-contract`: 0.565 path overlap, including Agent runtime, approval architecture docs, ChatGPT/MCP integration docs, plugin manifest, and operations skill.
- `feat/android-agent-runtime` vs `work/android-mvp-3.1.10`: 0.436 overlap across Android runtime/capability files.
- `fix/no-inline-device-manager-3.1.15` vs `release/3.1.12-tool-surface-approval`: 0.485 overlap, but version/release semantics make this a strong example of why overlap is evidence rather than a merge recommendation.

## Model refinement

EngineeringOS needs at least four distinct relationship classes:

1. `IDENTICAL_HEAD` — aliases or task labels sharing one exact state.
2. `ANCESTOR_DESCENDANT` — one development line contains another.
3. `OVERLAPPING_SURFACE` — independent lines modify the same engineering surface.
4. `CONTAINED_IN_MAIN` — commits are already reachable from the authoritative remote main line.

None of these means `SAFE_TO_DELETE` or `SAFE_TO_MERGE`. Those are decisions requiring workspace role, release semantics, architecture intent, dirty-state evidence, and production references.

## Next step

EXP-003 will introduce typed workspace roles and a first Convergence Debt model. Debt will be decomposed rather than collapsed into one opaque score: duplicate-state debt, divergence debt, overlap debt, orphan/unknown-role debt, dirty-workspace debt, and verification debt.
