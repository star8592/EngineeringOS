# Engineering World Model

The primary object is not a branch or chat, but a causal graph of engineering reality.

Node classes initially include intent/invariant, architecture decision/contract, task/dependency, conversation/agent execution, repository/branch/worktree/commit/PR, test/CI/evidence, release/artifact/deployment/production, and incident/regression/learning.

The model must answer: why does a change exist, what authorizes it, what implements it, what proves it, where is it deployed, and what happened in reality?

Lifecycle: DISCOVERED -> SPECIFIED -> ARCHITECTURE_CHECKED -> PLANNED -> DEVELOPING -> IMPLEMENTED -> QUALIFIED -> CONVERGING -> INTEGRATED -> RELEASED -> PRODUCTION_VERIFIED -> CLOSED. BLOCKED and SUPERSEDED are explicit states.

Health signals: Convergence Debt, Architecture Drift, Contract Drift, Production Drift, stale worktrees, orphan tasks, superseded work, and Mean Time to Convergence.
