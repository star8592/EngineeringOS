# EXP-037: Continuous Project Supervisor

Date: 2026-10-04

EngineeringOS now runs the complete G2 DevControl management loop continuously instead of requiring an operator to invoke individual experiments.

## Runtime contract

The supervisor executes:

`live evidence -> reconciliation -> manager -> durable queue -> outcome reconciliation -> scheduler -> shadow command loop -> evidence -> replay -> Control Room projection`

Every cycle remains G2 shadow-only. `target_mutation_authorized=false` is preserved in the snapshot, action brief, control-loop projection and supervisor status.

## Runtime/state boundary

Repository-backed `.engineeringos/**` files remain historical baselines and curated engineering evidence. Mutable continuous state lives only under ignored `.engineeringos/runtime/`. This prevents EngineeringOS from manufacturing its own dirty-workspace/convergence debt while preserving repository history.

Live runtime outputs:

- `.engineeringos/runtime/supervisor/status.json` — current supervisor health and last completed cycle;
- `.engineeringos/runtime/time-series.jsonl` — append-only repeated G2 observations;
- `.engineeringos/runtime/time-series-summary.json` — bounded recent convergence trend;
- `.engineeringos/runtime/action-brief.json` — deterministic top-priority work from the live queue;
- `.engineeringos/runtime/work-queue.json` — live durable queue;
- `.engineeringos/runtime/control-loop/**` — live command events/evidence/projection;
- `.engineeringos/runtime/shadow/**` — repeated observation snapshots.

`dashboard/runtime/**` remains a disposable read-only projection of this same live state.

## First live cycles

The initial supervisor implementation completed a full real DevControl observation in 25.568 seconds. After separating mutable runtime state from repository evidence, the first clean-root cycle completed in 18.757 seconds with `HEALTHY` status and six active work items.

The current top advisory work was:

1. close artifact identity gap (`UNKNOWN`);
2. close deployment identity gap (`PARTIAL`);
3. review five overlapping development-line pairs;
4. triage twelve dirty branch-attached worktrees;
5. reconcile three exact-head alias groups.

The exact counts are observations, not constants; subsequent cycles update them automatically.

## Operational surface

- `scripts/engineeringos_service.sh install` installs/enables the 5-minute user service;
- `scripts/engineeringos_status.py` prints concise supervisor health, convergence trend and top actions;
- Control Room at `http://127.0.0.1:8777/` renders supervisor health, action brief, project state, shadow execution and convergence trend.

## Safety/failure semantics

- singleton `flock` prevents overlapping supervisors;
- subprocesses are timeout bounded;
- status is atomically written as `HEALTHY` or `DEGRADED`;
- repeated time-series run IDs are idempotent;
- service restarts on process failure;
- no DevControl mutation is authorized in G2;
- Control Room remains projection-only and owns no approval semantics.

## Result

The repeated-observation portion of G2 is now operational rather than manual. EngineeringOS can continuously tell the operator what changed and what deserves attention next without requiring a fresh conversational status reconstruction.
