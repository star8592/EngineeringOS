# EngineeringOS Product Vision

> **Human owns intent. System owns engineering.**
> **人只负责想要什么，系统负责把它长期可靠地变成软件。**

This is the highest product principle. Architecture, UX, automation, pricing, and roadmap decisions are subordinate to it.

## Product thesis

Software creation is moving from professional coding toward natural-language intent. The resulting bottleneck is not code generation alone; it is the engineering burden created after generation: correctness, source control, parallel work, dependencies, tests, security, deployment, rollback, production verification, maintenance, and convergence.

EngineeringOS exists to remove that burden from people who need software but do not want to become software engineers.

The target user may be highly expert in teaching, commerce, research, operations, design, finance, content, or another domain. Lack of software-engineering expertise is not a user defect and must not become a product prerequisite.

## North-star outcome

**User Engineering Burden -> 0**

A user should be able to create, change, undo, and operate software by expressing intent and evaluating outcomes. Git, branches, worktrees, CI, dependency resolution, deployment mechanics, rollback, provenance, and engineering cleanup are implementation details owned by the system.

## Escalation rule

**Machine problems do not escalate to humans. Intent conflicts do.**

The system should resolve deterministic engineering mechanics itself when policy and evidence permit. It should ask the user only when a material ambiguity cannot be resolved without knowing what outcome the user actually wants.

Bad escalation:
- Choose merge, rebase, or cherry-pick.
- Resolve this worktree.
- Select a CI strategy.
- Pick a deployment rollback mechanism.

Good escalation:
- You previously asked for login to be mandatory, but now asked guests to train without login. Which behavior do you want?

## Internal rigor / external simplicity

The simpler the user experience becomes, the stronger the internal engineering system must become.

LLMs may interpret intent, propose implementations, reason about ambiguity, and generate code. Deterministic systems own durable state transitions, identity, policy enforcement, tests, build/release evidence, deployment verification, rollback, and replay.

No model claim such as "done", "safe", or "deployed" is authoritative without the required evidence.

## Product surfaces

### 1. Doctor — free diagnosis
Input: public repository URL, authorized private repository, or uploaded project snapshot.

Output: a plain-language project health report covering canonical source state, convergence debt, stale/duplicate work, CI/test health, dependency/security signals, release/production drift when observable, documentation/intent drift, and actionable priorities.

Doctor is read-only.

### 2. Care — continuous supervision
EngineeringOS continuously observes project events and maintains the Engineering World Model, current intent, decision memory, health state, and plain-language status. It recommends and prepares convergence actions but preserves the project's authority policy.

### 3. Autopilot — managed engineering
EngineeringOS performs evidence-gated engineering operations: safe convergence, verification, release preparation, deployment coordination, rollback, cleanup, and lifecycle closure. User interaction is centered on product intent and outcomes, not engineering mechanics.

## Product boundary

EngineeringOS is not another IDE, coding model, Git implementation, CI engine, or deployment platform. It coordinates those systems through adapters and evidence contracts.

Coding agents create changes. Git/GitHub own source history and merge mechanics. CI owns repeatable checks. Deployment systems own deployment execution. DevControl is the selected machine-execution backend for current dogfooding. EngineeringOS owns the missing semantic/control layer: intent, engineering state, evidence, policy, convergence, lifecycle closure, and user-facing abstraction.

## Trust model

Autonomy is earned progressively:

- L0 DIAGNOSE — read-only one-shot diagnosis.
- L1 OBSERVE — continuous read-only supervision.
- L2 PREPARE — generate plans/fixes without applying them.
- L3 SAFE_AUTOPILOT — reversible, deterministic, policy-authorized operations.
- L4 MANAGED_ENGINEERING — controlled convergence/release/cleanup.
- L5 FULL_AUTOPILOT — production-affecting lifecycle management backed by sustained evidence and rollback.

Permission scope must match autonomy level. Initial GitHub onboarding requests minimum read permissions; write permissions are added only when a user explicitly enables capabilities that require them.

## Product success metrics

Primary:
- User Engineering Burden (UEB): engineering decisions/actions the user had to understand or perform.
- Intent-to-Verified-Outcome time.
- Mean Time to Convergence.
- Verified autonomous closure rate.

Safety/quality:
- false autonomous closure rate;
- rollback success rate;
- production identity/provenance coverage;
- unresolved intent-conflict rate;
- destructive-action escape rate;
- percentage of user interruptions caused by engineering mechanics (target: approach zero).

Growth:
- Doctor scan -> connected project conversion;
- connected project -> paid Care/Autopilot conversion;
- projects remaining healthy without manual engineering intervention.
