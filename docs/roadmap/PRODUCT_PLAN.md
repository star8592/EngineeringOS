# Product Development Plan — Software Autopilot

Status: ACTIVE  
Canonical product: EngineeringOS

## 0. Product invariant

All work is evaluated against: **Human owns intent. System owns engineering.**

EngineeringOS may expose deep engineering evidence for debugging/admin use, but the default customer experience must never require software-engineering knowledge.

## 1. Preserve the existing control-plane core

Do not rebuild the existing World Model, Fact/Evidence registry, Policy Plane, Work Queue, Scheduler, Contract Graph, assurance ladder, event log, provenance chain, or dogfood gates. They are the reliability substrate.

The product work adds:
- non-engineer product language;
- project onboarding;
- Doctor diagnosis;
- living intent;
- intent-conflict detection;
- autonomy/permission levels;
- user-facing outcome reporting;
- multi-project SaaS tenancy and billing later.

## 2. Phase P0 — Dogfood convergence

Targets: Math Competition Lab, DevControl, CycleAlpha/CommerceFlow, then ShortDrama.

Exit:
- generic project profile ingests repository/worktree/branch/CI/release evidence;
- branch disposition supports KEEP / CONVERGE / RETIRE / ARCHIVE / PROTECT;
- capability-equivalence can supersede patch-equivalence when backed by explicit tests/evidence;
- dirty/unproven work is never silently deleted;
- user-facing status reduces to HEALTHY / WORKING / NEEDS_INTENT / AT_RISK plus plain-language explanation.

## 3. Phase P1 — Free Doctor MVP

### Inputs
1. Public GitHub repository URL — no installation required where public APIs suffice.
2. Private repository — GitHub App, read-only minimum permissions.
3. Uploaded archive — ephemeral isolated analysis workspace; archive is deleted according to retention policy.

### Deterministic scan
- repository/default branch/head identity;
- branch divergence and merged state;
- manifests/lockfiles/dependency graph where available;
- CI/check state;
- repository rules/protection state;
- release/deployment evidence where observable;
- stale/duplicate branches and worktrees when local agent evidence exists;
- secrets/security findings only through authorized providers/scanners;
- docs/architecture/current-intent consistency signals.

### Semantic scan
- infer project purpose and active capabilities;
- identify likely superseded work;
- detect conflicting architectural/product instructions;
- explain findings in domain language;
- never turn semantic inference into destructive authorization.

### Report
- overall health;
- "what is actually wrong";
- "what can be ignored";
- "what needs your intent";
- "what EngineeringOS can safely handle";
- evidence links for every material claim.

Exit: a non-programmer can understand the report without Git terminology.

## 4. Phase P2 — Connect & Care

Use a GitHub App rather than broad personal tokens. Request minimum permissions and subscribe only to required webhook events. Webhook ingestion is idempotent and queued; delivery IDs are deduplicated.

Capabilities:
- continuous project health;
- Living Intent + Decision Ledger;
- change/event timeline;
- daily/weekly plain-language project pulse;
- drift/convergence detection;
- agent-work discovery;
- no write action by default.

Exit: EngineeringOS can supervise multiple repositories for 30 days without stale-state false closure.

## 5. Phase P3 — Safe Autopilot

Enable write scopes incrementally.

First actions must be deterministic, reversible, and evidence-gated:
- create/update EngineeringOS check runs;
- prepare convergence PRs;
- close/archive proven-obsolete internal work only under project policy;
- rerun allowed checks;
- update durable EngineeringOS metadata;
- no autonomous production mutation yet.

Use repository rulesets/status checks as external deterministic guards. EngineeringOS does not bypass branch protections merely because it has credentials.

## 6. Phase P4 — Managed release

Integrate release/deployment evidence rather than replacing existing deployment systems.

Requirements:
- exact source SHA;
- qualification/check evidence;
- artifact/build provenance where available;
- environment identity;
- deployment result;
- production verification;
- rollback path.

GitHub artifact attestations may strengthen provenance but do not prove that an artifact is safe; policy/test evidence remains separate.

## 7. Phase P5 — Full Software Autopilot

User workflow:
1. State intent.
2. EngineeringOS detects whether this is new intent, refinement, reversal, experiment, or conflict.
3. Coding/execution agents implement.
4. Deterministic assurance validates.
5. EngineeringOS converges and releases.
6. Production is verified.
7. Residual branches/worktrees/artifacts are retired or archived.
8. Living intent and decision memory converge.
9. User receives outcome, not engineering chores.

## 8. SaaS architecture

### Control plane
- Tenant / User / Project / Connection
- Intent / Decision / Constraint
- Engineering World Model
- Evidence / Receipt / Provenance
- Policy / Autonomy Level
- Work Queue / Scheduler / Lease
- Report / Notification / Billing

### Adapter plane
- GitHub App
- generic Git
- CI providers
- deployment providers
- coding agents
- DevControl/local execution
- observability/security providers

### Execution plane
Untrusted repository code never runs in the web/control-plane process. Analysis/build/test execution occurs in ephemeral isolated workers with explicit CPU/memory/time/network/secret policies. Private source access is short-lived and scoped.

### Data plane
Store normalized facts, evidence metadata, hashes, decisions, and derived world-model state. Avoid retaining source blobs when not required. Tenant boundaries are explicit.

## 9. GitHub integration baseline

Follow GitHub's official GitHub App model:
- no permissions by default; request minimum required permissions;
- installation-scoped access;
- webhook secret verification;
- HTTPS;
- asynchronous webhook processing;
- delivery-ID deduplication;
- explicit event/action validation;
- rulesets/status checks remain external guards.

Doctor starts read-only. Checks/write, contents/write, pull-request/write, administration, or deployment permissions are capability-specific upgrades, never baseline permissions.

## 10. UX

Home:
- "Tell us what you want your software to do."
- Add project: GitHub URL / Connect GitHub / Upload project.
- Project card: HEALTHY / WORKING / NEEDS YOUR DECISION / AT RISK.
- "What changed", "What I handled", "What I need from you".

Never make Git vocabulary the primary navigation.

Advanced engineering evidence exists behind an optional "Engineering details" surface for experts/support/debugging.

## 11. Business funnel

Free Doctor -> Connect read-only -> Care subscription -> Safe Autopilot -> Managed Engineering.

Pricing is not frozen before usage/cost/conversion evidence. Meter the real cost drivers first: repository size, scan frequency, isolated compute, model reasoning, connected environments, and autonomous actions.

## 12. Near-term build order

1. Promote product vision/invariant into canonical EngineeringOS docs.
2. Add generic Project Doctor report schema and UEB metric.
3. Import Math Competition Lab governance state as pilot evidence.
4. Build public-repository Doctor CLI/API before SaaS UI.
5. Add GitHub App read-only onboarding.
6. Add webhook/event ingestion.
7. Build plain-language report renderer.
8. Dogfood on at least four heterogeneous projects.
9. Only then add write scopes and paid Autopilot actions.
