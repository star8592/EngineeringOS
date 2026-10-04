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

State: IMPLEMENTED_BASELINE. The existing singleton Supervisor process now owns a separate generic Project Autopilot lane; no second daemon is introduced. Projects must be explicitly registered in runtime policy before autonomous mutation is eligible. The current safe lane requires `autopilot_enabled=true` and `max_assurance` A1/A2. Stable project state sleeps without journal growth, machine/provider failures use persisted exponential backoff (30s doubling to 1800s), restart recovery comes from the project journal, and unchanged `NEEDS_INTENT` is notified once rather than repeatedly. Project Autopilot failures are isolated from the legacy DevControl G2/G3 shadow lane. EngineeringOS is Project Zero; its first live idle run produced OBSERVE followed by SLEEP with zero journal growth and zero repository mutation.
