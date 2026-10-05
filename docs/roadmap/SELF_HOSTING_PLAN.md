# Self-Hosting Work Plan

Status: ACTIVE

## SH-01 Conversation → Intent Ledger
Outcome: natural chat/voice turns persist as DESIRE / FEEDBACK / CORRECTION / REVERSAL / APPROVAL / QUESTION / ARTIFACT / INTERRUPTION.
Evidence: conversation-intent invariants.
State: IMPLEMENTED_BASELINE.

## SH-02 Intent → Capability Reconciliation
Outcome: desired outcomes reconcile against observed capabilities without model self-certification.
Evidence: VERIFIED / DISCOVERED / UNKNOWN / NEEDS_INTENT invariants.
State: IMPLEMENTED_BASELINE.

## SH-03 Capability Gap → Work Graph
Outcome: UNKNOWN gaps that are machine-resolvable become work items automatically; NEEDS_INTENT alone may interrupt the human.
Evidence: deterministic mapping tests and dependency graph.
State: IMPLEMENTED_BASELINE — UNKNOWN gaps deterministically become work items; NEEDS_INTENT is excluded from machine work.

## SH-04 Work Graph → Scheduler
Outcome: work is assigned to deterministic/reasoning/high-assurance lanes from policy and assurance requirements.
Evidence: scheduler tests; no user agent-selection burden.
State: INTEGRATED_BASELINE — generated work items now pass through the existing dependency graph and scheduler.

## SH-05 Execution → Evidence → Capability
Outcome: agent/tool claims become evidence only after declared verification; successful evidence upgrades capability state.
State: INTEGRATED_BASELINE — first bounded self-hosting verification produced an evidence-backed execution receipt and closed a capability gap.

## SH-06 Preview Feedback Binding
Outcome: screenshot/live-preview feedback is bound to the artifact and active intent, then creates revision work.
State: INTEGRATED_BASELINE — feedback binds to artifact/context, increments intent generation, supersedes safe obsolete work, protects unsafe in-flight work, and reschedules revision work.

## SH-06A Autopilot Control Loop
Outcome: one deterministic tick consumes durable conversational intent, reconciles capabilities and obsolete work, creates/reschedules work, and emits a durable runtime projection.
State: IMPLEMENTED_BASELINE — pure tick plus atomic runtime projection; execution authority remains policy/assurance gated.

## SH-07 Self Project Supervisor
Outcome: EngineeringOS continuously supervises its own canonical repository and detects drift, incomplete work, stale claims, and convergence debt.
State: INTEGRATED_ADVISORY — continuous Supervisor now consumes Autopilot projections, deduplicates unchanged states, waits on genuine intent, and exposes ADVANCE/SLEEP/WAIT decisions while execution remains policy-gated.

## SH-08 Conversation-first Shell
Outcome: minimal UI is conversation + voice + artifact/result cards + passive status; engineering details are secondary.
State: PLANNED AFTER CONTROL LOOP.

## SH-09 Durable Voice Session Handoff
Outcome: audio session can disconnect/reconnect while backend tasks and intent survive.
State: PLANNED.

## SH-10 Verified Self-Release
Outcome: EngineeringOS can prepare, verify, release, verify production, and clean up its own bounded releases under policy.
State: LATER AUTONOMY GATE.

## SH-07A Safe Autopilot Execution
Outcome: Supervisor ADVANCE decisions pass through an explicit admission boundary before any command exists.
State: IMPLEMENTED_BASELINE — safe non-side-effecting actions (verification, project-state reads, preview builds) are allowlisted through A2; PROTECT, blocked, unknown, higher-assurance, or unmapped actions are denied. Deterministic command/idempotency identity includes project, work item, action and subject SHA. First real self-hosting verification closed the Autopilot Control Loop capability with PASS evidence bound to source SHA.

Mutation authority is intentionally not implied by ADVANCE or by model reasoning. Write-code, Git mutation, release and production actions require later explicit policy lanes and stronger assurance.

## First user-visible self-hosting acceptance — 2026-10-05

Intent: “给 EngineeringOS 做一个可以看到当前开发状态的简单页面”。

Observed outcome:
- Control Room exposes an ordinary-user home surface before engineering details.
- It shows current development state, what the system is doing, and whether the human must decide anything.
- Engineering detail remains available under a secondary disclosure surface.
- Real headless-browser rendering verified the user-facing state and text.
- After verification evidence was supplied, durable Autopilot projection converged from WORKING to VERIFIED with zero remaining work items and zero dispatch items.
- Supervisor time-series retention is bounded and systemd output uses journald rather than an unbounded append log.

This is the first acceptance where the self-hosting loop produced a visible product result and then stopped automatically after evidence-backed completion.

## First controlled self-mutation — 2026-10-05

EngineeringOS performed its first code mutation through the isolated mutation lane. The proposal was bound to an exact source SHA and one declared file (`dashboard/index.html`). The first attempt was correctly denied while the source workspace was dirty. After the mutation-lane baseline was committed, a stale proposal was correctly denied with `SOURCE_SHA_DRIFT`. A fresh proposal created a detached worktree, changed only the declared file, passed verification, produced a diff digest, and left main untouched. The convergence gate then rechecked clean main, exact source SHA, exact mutation surface, and diff evidence before applying the patch to main and rerunning verification. The result stopped at `CONVERGED_UNCOMMITTED`; commit/push authority remains a separate boundary.

## SH-07B Coding Agent candidate lane — 2026-10-05

State: IMPLEMENTED_BASELINE. Coding agents are proposal generators, never execution authorities. A Task Envelope binds goal, exact source SHA, complete allowed path set, verification argv, and context. Provider output is schema-closed to the allowed paths and becomes a Mutation Proposal only after validation. Codex CLI is integrated in read-only/ephemeral structured-output mode; its process lifetime is bounded and timeout kills the isolated process group. Provider failure is machine work (`REOPENED / WAITING_PROVIDER`), never `NEEDS_INTENT`. A provider pool may fall back to another coding backend without changing authority semantics.

## SH-07C Autonomous supervisor execution loop — 2026-10-05

State: IMPLEMENTED_BASELINE. The generic Supervisor consumes scheduler dispatches and executes only work items carrying an explicit mutation contract (`allowed_paths`, `verification_argv`, source SHA). Missing contracts remain `WAITING_CONTRACT`; provider failures become `REOPENED / WAITING_PROVIDER`; neither is an intent interruption. Successful coding candidates pass the isolated mutation lane, deterministic verification, convergence gate, post-convergence verification, and commit receipt. A commit receipt binds source SHA, result SHA, changed paths, and diff SHA256 as capability evidence. One Supervisor tick converges at most one commit so later work must reconcile against the new HEAD before execution.

## SH-07D Durable project journal and restart recovery — 2026-10-05

State: IMPLEMENTED_BASELINE. Intent and autonomous Work lifecycle now have a CAS-protected per-project JSONL journal that is replayable into current project state. Runtime projections are caches, not authority. The durable Supervisor can recover Intent and Work from the journal after process restart, reschedule unfinished work, persist provider/contract failures as machine states, persist commit receipts, and avoid re-executing resolved work. Local mutation verification may automatically resolve only A1/A2 capability-evidence predicates; A3–A5 work remains committed but unresolved until the required higher-assurance runtime/production evidence arrives. The legacy manager-plan JSON queue remains compatibility input and must not become a second authoritative Autopilot write path.

## SH-07E Continuous registered Autopilot — 2026-10-05

State: IMPLEMENTED_BASELINE. The existing singleton Supervisor process now owns a separate generic Project Autopilot lane; no second daemon is introduced. Projects must be explicitly registered in runtime policy before autonomous mutation is eligible. Legacy projects may still use autopilot_enabled=true; target-managed projects use management_target plus promotion evidence. In both cases the current safe lane requires max_assurance A1/A2. Stable project state sleeps without journal growth, machine/provider failures use persisted exponential backoff (30s doubling to 1800s), restart recovery comes from the project journal, and unchanged `NEEDS_INTENT` is notified once rather than repeatedly. Project Autopilot failures are isolated from the legacy DevControl G2/G3 shadow lane. EngineeringOS is Project Zero; its first live idle run produced OBSERVE followed by SLEEP with zero journal growth and zero repository mutation.

### Runtime activation evidence

The existing `engineeringos-supervisor.service` was already enabled and active. After SH-07E landed it was restarted through the repository service script, remained `active/running` with `NRestarts=0`, and retained the single-process service model. Historical logs showed an older crash/restart burst before the current stable run; failure status now persists a bounded traceback so future daemon failures are diagnosable from runtime state rather than only a systemd exit code.

## SH-08A Conversation command ingress — 2026-10-05

State: IMPLEMENTED_BASELINE. A frontend-neutral Conversation Command Envelope now persists user turns into the authoritative project journal. `command_id` is the retry/idempotency boundary; intent generation is calculated from durable state rather than supplied by a UI or model. DESIRE/CORRECTION create or revise durable intent and capability-planning work; REVERSAL deactivates the intent; FEEDBACK/APPROVAL/ARTIFACT/INTERRUPTION remain durable turns without falsely advancing product generation. Correction/reversal automatically supersede older safe work and PROTECT unsafe in-flight work. Clear Desire can start engineering automatically, but does not receive a mutation contract from natural language alone.

A read-only Planning Provider may propose `allowed_paths` and `verification_argv`. Deterministic contract admission rejects path escape, arbitrary shell wrappers, and assurance above the A1/A2 safe lane. An admitted contract is persisted as `WORK_CONTRACT_ADMITTED` before any coding provider may execute it. Fixture end-to-end acceptance proves: conversation Desire -> durable intent -> planning work -> admitted contract -> coding candidate -> isolated verification -> commit receipt -> RESOLVED; a subsequent correction advances the same intent to generation 2.

## SH-08B Continuous planning-to-execution loop — 2026-10-05

State: IMPLEMENTED_BASELINE. The registered continuous Autopilot now treats capability planning as a durable phase before coding. A tick with unplanned `CAPABILITY_PLANNING` work invokes the read-only planning-provider pool, passes the proposal through deterministic contract admission, binds the contract to the current repository source SHA, persists `WORK_CONTRACT_ADMITTED`, and stops. A later tick replays that durable contract before invoking a coding provider. Planner failures are machine failures and use the existing bounded exponential backoff; they do not become human intent questions. If HEAD changes between planning and execution, the executor returns `SOURCE_SHA_DRIFT`, the durable contract is invalidated, and the work returns to planning after backoff instead of repeatedly executing a stale plan. End-to-end registered-runner acceptance proves PLAN -> ADVANCE/commit/RESOLVED -> stable state, plus stale-plan invalidation and replan.

## SH-08C Provider runtime resilience — 2026-10-05

State: IMPLEMENTED_BASELINE. Project Zero live acceptance showed Codex authentication/network is healthy (minimal read-only request ~8s), while a real three-file full-replacement candidate (~15KB input surface) completed in ~107s. The registered runner had incorrectly overridden the Codex provider's native 180s budget with 60s, creating false `WAITING_PROVIDER` failures. Provider-native budgets are now authoritative unless a project explicitly overrides them. Provider routing records elapsed time per attempt. Claude CLI is present but not authenticated and is classified fail-fast as `CLAUDE_NOT_AUTHENTICATED`, not as a timeout.

The same live run exposed a retry-storm bug: the runner cleared the machine-failure latch before classification and then incremented failures every tick. Backoff now has one authority. Provider failures use bounded exponential retry; source-SHA drift is a reconciliation transition, invalidates stale contract evidence, clears stale provider diagnostics, and does not count as provider failure. Successful planning/reconciliation resets failure count.

### Registry timeout semantics

Project registry policy may select explicit per-provider runtime budgets through `provider_timeouts`, keyed by provider identity. The legacy shared `provider_timeout` field is forbidden because providers have materially different latency envelopes and native defaults. Project Zero intentionally carries no provider timeout override: Codex and Claude use their provider-owned defaults. Runtime registry remains mutable activation policy, while accepted field semantics are code/schema invariants and are regression-tested.


## EP-02 External-project safe baseline — 2026-10-05

State: IMPLEMENTED_BASELINE. External projects now enter through an explicit read-only onboarding path before autonomous mutation. The Supervisor owns a separate baseline lane that records canonical repository identity, source HEAD, branch/upstream, bounded modified/untracked paths, and project-owned verification entrypoint names without reading or copying file contents. Dirty repositories become `PROTECTED_EXISTING_WORK`; the commercial surface shows that state in ordinary language. A registry project may set `require_clean_baseline=true`; if such a project is accidentally enabled for Autopilot while its baseline is missing or dirty, the registered runner returns `BASELINE_BLOCKED` before planning or coding. This is a machine safety condition and does not become `NEEDS_INTENT`.

The first external project is `KangarooMath` / 袋鼠数学. Its canonical repository alias resolves to `star8592/Kangaroo-Practice-Simulator`. The initial live baseline observed pre-existing modified and untracked work, preserved the repository byte-for-byte at the Git-status/HEAD boundary, and therefore keeps the project connected/read-only until that work is independently converged. See `docs/roadmap/EXTERNAL_PROJECT_MANAGEMENT_PLAN.md`.

## EP-03 Conversation -> project -> durable intent — 2026-10-05

State: IMPLEMENTED_BASELINE. Multi-project natural-language routing is deterministic and replayable. Explicit product mentions and registered aliases route directly; selected UI context and durable conversation history provide follow-up context; ambiguity never silently chooses a repository. Process-control turns such as “继续” do not create product-intent generations. Command retries are idempotent by command-envelope fingerprint. Conversational APPROVAL is explicitly PRODUCT_FEEDBACK_ONLY and does not satisfy engineering/host/release authority. A frontend-neutral CLI acceptance proved natural-language project routing -> durable intent/work and a following “继续” -> zero journal growth.


## EP-04 External A2 promotion gate — 2026-10-05

State: IMPLEMENTED_GATE. External A2 management requires promotion evidence in addition to registry enablement. Canonical origin, branch/upstream identity, clean baseline, zero source divergence, declared project verification entrypoint, A1/A2 ceiling and isolated workspace are checked before planning/coding. Promotion evidence is projected by the singleton Supervisor. This prevents a config typo or stale registry flag from widening mutation authority. KangarooMath is intentionally blocked by protected pre-existing work.

## EP-07 Backend-owned tool-surface evidence — 2026-10-05

State: IMPLEMENTED_BASELINE. Tool-surface drift is now represented as evidence and admission, not prose. EngineeringOS does not copy DevControl's canonical 26-tool registry. It invokes DevControl's own canonical source/live checker, adapts the current ChatGPT Host-observable surface into DevControl's evidence schema, and invokes DevControl's own Host verifier. Surface match and immutable Host acceptance are distinct states. Host-dependent workflows can deny execution on TOOL_SURFACE_DRIFT without coupling local EngineeringOS Autopilot to unrelated ChatGPT metadata.

### EP-07 freshness hardening — 2026-10-05

Backend Host observations are no longer timeless. Supervisor refreshes canonical/live surface evidence on a bounded cadence and compares semantic catalog identity with the last Host observation. Admission requires current freshness convergence. A live 26-vs-26 DevControl case with descriptor drift was detected and denied, proving that tool count is not used as a parity proxy.


## ADR-030 management authority convergence — 2026-10-05

State: IMPLEMENTED_BASELINE. External project management no longer requires two independent approval switches. management_target is the durable human/policy authority goal; promotion evidence is the runtime eligibility gate; effective Autopilot is derived. The legacy autopilot_enabled boolean remains compatibility only for projects not yet migrated to a management target. This prevents both false disablement after an already-approved management decision and accidental privilege widening by flipping a boolean.

## SH-08C Git/journal crash-window reconciliation — 2026-10-05

State: IMPLEMENTED_BASELINE. Autonomous commits now carry deterministic recovery trailers bound to project, item, intent generation, source SHA, allowed paths, verification argv and the exact binary diff hash. On restart, the durable supervisor reconciles Git before provider dispatch. A valid unjournaled commit is reconstructed into a commit receipt and the missing WORK_COMMITTED/RESOLVED events are appended without re-running the coding provider. HEAD movement without full recovery evidence still fails closed. See ADR-031.

## EP-02B Protected external work reconciliation — 2026-10-05

State: IMPLEMENTED_BASELINE. External dirty work is now fingerprinted, structurally grouped, quiet-window tracked and isolated-verifiable without source mutation. Candidate groups are explicitly non-authoritative. Differential verification separates pre-existing baseline debt from regressions introduced by the protected snapshot. The first KangarooMath run produced four candidate groups across 11 paths and BASELINE_RED_SAME_FAILURE against the project-owned public quality gate.

## EP-04B Protected-work adoption — 2026-10-05

State: GATE_IMPLEMENTED. Protected external work can transition from PROTECTED_EXISTING_WORK to ADOPTABLE only through ADR-032. Quiet time, process inactivity, exact inventory identity, selected candidate hashes, path containment, canonical Git identity and composed full verification are all required. The gate grants no mutation authority by itself.
