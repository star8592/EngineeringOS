# EngineeringOS Development Plan

Status: Active
Updated: 2026-10-03

## Non-negotiable development invariants

1. **Official-source-first.** For OpenAI/MCP/tool/approval/protocol behavior, implementation starts from current official documentation/specification. Secondary projects are references, not authorities.
2. **No temporary semantic patches.** A local workaround may be used only for diagnosis; it cannot become architecture without an explicit contract/ADR and regression evidence.
3. **No tool-surface drift.** EngineeringOS execution uses the explicitly selected backend (currently DevControl). Availability of another tool is not permission to switch execution surfaces.
4. **One approval semantic.** EngineeringOS policy may decide `ALLOW`, `DENY`, or `REQUIRE_HOST_APPROVAL`, but it does not create a second approval system. User approval is collected/resumed through the host/tool protocol boundary.
5. **Tool annotations are evidence/hints, not authorization.** `read_only`, `destructive`, `idempotent`, and `open_world` metadata inform classification; project policy and execution contracts remain authoritative.
6. **Durable intent before side effects.** Side-effecting commands require idempotency identity, execution receipt, durable intent, outcome evidence, and safe retry semantics.
7. **Human UI is a projection.** Control Room reads the same durable state as agents. UI controls must invoke the same policy/command boundary; no dashboard-only state or approval path.
8. **Globally evolving, locally deterministic.** AI may reason about intent and ambiguity; durable state transition, identity, evidence, policy enforcement, and replay are deterministic.

## Official contract baseline

Primary references are recorded in `docs/architecture/official-tool-approval-baseline.md`. When implementation and remembered behavior disagree, refresh the official references before changing code.

## Gate roadmap

### G0 — Core coherence — PASS
Facts, evidence reconciliation, policy, queue, leases, dependencies, scheduler, assurance and closure invariants exist.

### G1 — Genericity — MINIMUM PASS
Second-repository generic Git/workspace ingestion is proven. Generic CI/release/runtime adapters remain incomplete.

### G2 — Shadow DevControl — ACTIVE

Mechanical end-to-end loop status: **PASS (EXP-036)**. Continuous project supervision: **OPERATIONAL (EXP-037)**. Sustained outcome evaluation and queue convergence remain active.
Current priority: use the continuous supervisor time-series and action brief to reduce real DevControl convergence debt and accumulate G3 admission evidence. No target mutation is authorized by G2.

Exit criteria:
- one complete durable shadow loop from work item -> scheduling -> policy -> command intent -> simulated/read-only executor -> outcome evidence -> event commit -> replay -> Control Room;
- refreshed DevControl queue based on current evidence, not stale initial snapshots;
- time-series decision/outcome ledger with false-positive/false-negative review;
- tool/approval contract is machine-checked;
- source/artifact/runtime provenance gaps are explicit and no longer collapsed into one `UNKNOWN`.

### G3 — Bounded deterministic actions — NEXT
Only reversible, deterministic, low-risk actions explicitly listed in a project profile may execute.

Initial candidate action classes:
- refresh/read evidence;
- run deterministic checks/tests;
- create isolated worktrees with collision/lease checks;
- produce reports/snapshots/checkpoints;
- other reversible project-local actions proven by policy.

Explicitly excluded from G3:
- autonomous merge/rebase into protected branches;
- branch/worktree deletion;
- production deploy/release;
- externally visible publishing/sending;
- permission/authentication changes;
- any action lacking an outcome probe or rollback/recovery contract.

Exit criteria:
- G3 admission gate passes machine invariants;
- command processor is the only mutation boundary;
- bounded executor proves at-most-once-or-probe semantics under disconnect/restart;
- Control Room shows execution receipt/evidence without inventing approval state;
- sustained dogfood with no silent duplicate side effects.

### G4 — Controlled convergence
Selected branch/task convergence may run only with dependency, lease, contract-impact, CI, provenance, assurance and rollback evidence.

### G5 — Production-affecting automation
Requires sustained dogfood plus exact release/artifact/runtime identity, project production policy, post-action verification and rollback evidence.

## Immediate execution order

Completed:
- Official tool/approval baseline + machine-readable G3 admission contract.
- First end-to-end Shadow Control Loop using durable command/event machinery (EXP-036).
- First evidence-backed closure of a G2 semantic false-positive (EXP-034/035).
- Continuous 5-minute G2 project supervisor with runtime/repository-state separation and operator action brief (EXP-037).
- Evidence-backed action drill-down for dirty workspaces, overlapping lines, duplicate heads and provenance gaps (EXP-038).
- First G3 bounded deterministic diagnostic with authoritative CI closure (EXP-039).
- First executable A3/A4 formal-assurance gates for command safety (EXP-040).
- Executable System-One/Jev typed-decision contract with an explicit no-authorization boundary (EXP-041).
- Local open Laya provider, shadow routing, and seed Engineering Decision Benchmark (EXP-042).

Current order:
1. Let the continuous G2 supervisor accumulate time-series observations and outcome labels; measure false-positive/false-negative/churn behavior.
2. Use its action brief to reconcile the current DevControl queue, especially artifact/deployment provenance, dirty/overlap/divergence findings, and duplicate heads.
3. Extend the Control Room drill-down from action evidence to command events/receipts/outcome evidence while preserving projection-only semantics.
4. Expand generic CI/release/runtime adapters beyond DevControl-specific profiles.
5. Continue G3 pilot dogfood with the single deterministic-check allowlist; prove deferral, idempotency, evidence closure, and no target mutation before adding any second action class.
6. Run Laya continuously in shadow advisory mode, expand EDB from real outcomes, and only allow its recommendations to influence routing after measured accuracy/calibration thresholds pass.
7. Extend executable assurance from command safety to lease exclusivity and convergence/release state machines.
8. Expand G3 only from observed evidence; after stability, begin G4 convergence actions.

## Definition of Done for a development change

A change is not done because an agent says it is done. It requires, as applicable: code, tests/invariants, documentation/ADR updates, evidence, provenance, queue reconciliation, and a clean committed repository state. Changes to tool surface, approval semantics, execution identity, release semantics, or safety boundaries require explicit regression coverage.
