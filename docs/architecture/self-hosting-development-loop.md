# Self-Hosting Development Loop

Status: CANONICAL

EngineeringOS must manage its own development before it is trusted to manage other people's software.

## The loop

```
conversation
  ↓
durable intent / decision
  ↓
capability gap
  ↓
work graph
  ↓
scheduler / agents / execution backend
  ↓
deterministic verification
  ↓
preview or outcome
  ↓
human feedback
  ↓
intent revision
  ↓
convergence / release / cleanup
  ↺
```

Discussion is not completion. A product discussion is durable only when its accepted conclusions have been projected into:
1. current product principles or architecture;
2. an ADR when a durable choice was made;
3. acceptance scenarios/tests;
4. executable work items when implementation remains;
5. evidence when implementation is claimed complete.

## Self-management rule

EngineeringOS is project zero. Every new product capability should, where feasible, be exercised on EngineeringOS itself before external autonomy is increased.

The system maintains two synchronized views:
- **Human view:** what we are trying to achieve, what changed, what is ready, what needs a real decision.
- **Machine view:** facts, evidence, tasks, dependencies, leases, assurance, receipts, source/runtime identity.

Neither view replaces the other.

## Automatic orchestration

Accepted intent becomes a capability gap. Capability gaps become work items with:
- expected outcome;
- dependency edges;
- required evidence;
- required assurance;
- autonomy policy;
- rollback/recovery boundary;
- completion predicate.

The scheduler chooses the execution lane. The user does not choose agents, branches, merge strategies, test runners, or deployment mechanics.

## Completion

A work item is not DONE because an agent says it is done.

Completion requires its declared evidence predicate. Product-facing completion additionally requires that the observed capability reconciles with active intent.

## Iteration

Feedback may:
- refine active intent;
- correct it;
- reverse it;
- approve it;
- introduce a new intent.

EngineeringOS then reconciles in-flight work. Superseded implementation is converged safely; it is not left as permanent development debris.

## Documentation convergence

The system should eventually generate/update documentation projections from durable state. Until that automation is complete, canonical docs + ADRs + executable tests are mandatory.

The goal is not more documents. The goal is **one durable truth expressed through the right projections**.

## First closed self-hosting loop — 2026-10-04

EngineeringOS verified its own Conversation Intent Ledger using the executable conversation-intent invariants. The bounded verification produced an execution receipt with explicit evidence, transitioned the work item through claim and pending-resolution, and closed it only after verifier evidence. The resulting capability state is VERIFIED.

A missing-evidence path was also tested and is required to remain UNKNOWN/REOPENED. Agent completion claims are therefore insufficient for closure.

During this integration, the execution-receipt success path was reviewed and the regression was strengthened so a rejected evidence-free success transition cannot leave a false terminal success state.

## Intent revision and feedback convergence

Natural feedback is revision of durable intent, not an unrelated new task. Each material DESIRE/CORRECTION/REVERSAL advances an intent generation. Work from an older generation may become SUPERSEDED only when safe; in-flight work without safe-supersession evidence is PROTECT. Revision work retains the preview/artifact reference that grounded the human feedback and re-enters the existing scheduler.

## Continuous supervision and bounded idleness

The continuous Supervisor consumes durable Autopilot projections. A stable projection fingerprints to SLEEP rather than generating repeated work or logs. A repeated NEEDS_INTENT condition is deduplicated so the human is not repeatedly interrupted for the same unresolved decision. Dispatchable machine work yields ADVANCE, but this advisory decision does not itself grant mutation authority; existing policy and assurance gates remain authoritative. Runtime histories must be bounded/compacted rather than grow without limit.

## Safe Autopilot execution boundary

ADVANCE is scheduling intent, not execution authority. A separate admission gate checks work state, scheduler disposition, unresolved human authority, an action allowlist, and assurance ceiling before creating a deterministic command. The first enabled lane is non-side-effecting verification. Its receipt binds PASS evidence to the subject source SHA and only then permits capability VERIFIED and work RESOLVED.

## Controlled mutation lane

Autonomous code changes are proposed against an exact source SHA in an isolated detached worktree. A proposal declares its complete allowed mutation surface and verification command. Protected runtime/Git paths and path escape are denied. A verified isolated patch is only `READY_FOR_CONVERGENCE`; it cannot mutate main. Convergence separately requires clean main, unchanged source SHA, exact changed-path equality, and matching diff evidence, then reruns verification after applying the patch. Commit, push, release, and production remain later authority boundaries.

## Coding-agent boundary

Coding models do not receive convergence, commit, push, release, or production authority. They receive a Task Envelope and may return only candidate replacement content for explicitly allowed paths. The provider adapter runs with the narrowest available sandbox and structured output. Candidate validation, isolated mutation, verification, diff evidence, convergence, and later release authority remain deterministic system responsibilities. Provider outage/timeout is a machine failure and must not be escalated as an intent question.

## Supervisor convergence unit

A dispatchable work item is not executable merely because an agent can reason about it. Autonomous mutation requires an explicit mutation contract. The Supervisor may converge at most one commit per tick; after a successful commit, the repository HEAD becomes new world state and remaining work must be reconciled again. This prevents stale-source parallel candidates from being blindly applied. Commit evidence is the transition boundary from a verified candidate to durable source truth; agent success alone never closes work.

## Durable project journal

Autopilot durable truth is an append-only per-project event journal with compare-and-swap sequencing. Intent revisions and Work lifecycle transitions are replayed from that journal; projections may be regenerated and therefore are not authoritative. Restart recovery must require no conversational memory. A local verified commit can close only work whose required assurance is A1/A2 and whose completion predicate explicitly accepts capability evidence. Higher-assurance work requires the corresponding runtime, CI, release, or production evidence before resolution.

## Continuous runtime and explicit project authority

Continuous Autopilot runs inside the existing singleton Supervisor rather than a competing daemon. Project discovery never grants mutation authority: autonomous execution requires an explicit runtime registry entry and a bounded assurance ceiling. Machine failures are retried with persisted bounded exponential backoff; stable state sleeps; unchanged human-intent waits are deduplicated. A project lane failure must not widen permissions or disable unrelated supervision lanes.

## Conversation command boundary

Chat, voice, web, and future clients are transports, not intent databases. They submit idempotent Conversation Command Envelopes; EngineeringOS derives generation from the durable project journal. Models may classify or propose, but they do not author durable generation numbers or mutation authority. Process-control utterances such as “continue” must not automatically become new product intent. Product corrections and reversals reconcile existing work: safe stale work is superseded, unsafe in-flight work is protected.

Natural-language clarity is not mutation authority. New desires first create capability-planning work. A read-only planner may propose a mutation contract, but only deterministic contract admission can persist executable paths and verification argv. Coding execution consumes only that admitted durable contract.
