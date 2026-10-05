# External Project Management Plan

Status: ACTIVE  
Owner: EngineeringOS  
First external acceptance project: KangarooMath / 袋鼠数学

## Product goal

EngineeringOS must be able to manage a real product without requiring its owner to operate Git, CI, agents, MCP tools, or deployment mechanics.

The human owns product intent. EngineeringOS owns engineering execution only inside explicit, evidence-backed authority boundaries.

## Canonical onboarding state machine

DISCOVERED -> CONNECTED_READ_ONLY -> BASELINED -> A2_MANAGED -> RELEASE_MANAGED -> PRODUCTION_MANAGED

No state may be skipped merely because an agent, model, tool description, or UI claims an operation is safe.

### CONNECTED_READ_ONLY

The repository is known and may be inspected. Mutation Autopilot is disabled.

Required evidence:
- canonical repository identity;
- canonical real path;
- origin identity;
- current branch and HEAD;
- working-tree state;
- bounded list/count of modified and untracked paths;
- existing verification/build entrypoints;
- no target mutation during inspection.

### BASELINED

EngineeringOS has classified existing repository state and can distinguish pre-existing human/agent work from EngineeringOS-owned work.

A dirty repository is not an error and must not be cleaned, reset, stashed, committed, or overwritten automatically. It is PROTECTED_EXISTING_WORK until independently converged by its owner/current worker or explicitly adopted through a later policy.

### A2_MANAGED

Safe autonomous planning/coding is allowed only when:
- project registry explicitly enables Autopilot;
- assurance ceiling is A1/A2;
- repository source identity is stable;
- working tree is clean at planning and convergence boundaries;
- admitted contract declares exact allowed paths and verification argv;
- candidate passes isolated verification;
- convergence gate proves exact diff/path/source identity;
- completion has durable evidence.

### RELEASE_MANAGED / PRODUCTION_MANAGED

Commit, push, release, deploy, production verification, rollback, data migration, user-data mutation, billing, credentials, and destructive operations remain separate authority lanes. They are never inferred from A2 coding permission.

## Tool-surface drift invariant

Tool/catalog metadata is treated as observed capability evidence, never as durable authority.

For every execution backend, EngineeringOS must eventually maintain a canonical capability snapshot containing:
- backend identity;
- tool name;
- input/output schema digest;
- declared behavioral annotations;
- task/continuation semantics where applicable.

A catalog/schema/annotation mismatch is TOOL_SURFACE_DRIFT. It blocks affected autonomous execution and triggers machine reconciliation. It must not silently widen or narrow authority, and must not be fixed by inventing alternate tool semantics.

## Approval semantics invariant

There is one explicit authority chain:

Human intent -> EngineeringOS policy/admission -> execution-backend authorization -> host/provider approval when required -> deterministic evidence.

Rules:
- MCP/OpenAI annotations are behavioral hints, not authorization.
- readOnlyHint is true only for actions that cannot mutate state.
- destructiveHint/idempotentHint describe real behavior; they do not grant permission.
- tool descriptions must match actual side effects and prerequisites.
- sensitive/consequential actions keep their explicit approval boundary.
- a model, coding agent, planner, tool annotation, or successful previous call cannot manufacture approval.
- approval for action A never implies approval for action B.
- a host approval prompt is not a product-intent question.
- machine authorization/approval failures do not become NEEDS_INTENT unless the product choice itself is genuinely ambiguous.

These constraints follow the current OpenAI MCP/plugin guidance and MCP ToolAnnotations semantics and must be kept in sync with official documentation rather than local assumptions.

## External-project baseline refresh

The singleton Supervisor owns a read-only baseline lane. It may inspect registered repositories but may not modify them.

Baseline output is runtime projection, not source truth. It contains only bounded repository facts and must never contain file contents, credentials, private data, or secret values.

Baseline states:
- CLEAN_CONNECTED
- PROTECTED_EXISTING_WORK
- INVALID_REPOSITORY
- UNAVAILABLE

A connected project with PROTECTED_EXISTING_WORK stays visible in the commercial shell as protected/read-only. Autopilot remains disabled until the repository has a clean source boundary and the project is explicitly promoted.

## KangarooMath acceptance

Current canonical project:
- technical identity: KangarooMath
- user-facing name: 袋鼠数学
- canonical repository alias: /mnt/disk1/Code/Math-Competition-Lab
- origin: star8592/Kangaroo-Practice-Simulator
- current onboarding state: CONNECTED_READ_ONLY

Current repository contains pre-existing modified and untracked work. EngineeringOS must preserve it unchanged.

Acceptance to reach BASELINED:
1. read-only scan succeeds;
2. canonical path/origin/branch/HEAD are captured;
3. dirty paths are classified without reading their contents;
4. existing npm verification/build entrypoints are enumerated;
5. commercial projection shows protected existing work;
6. no mutation occurs in the KangarooMath repository;
7. Supervisor restart preserves and refreshes the baseline safely.

Acceptance to reach A2_MANAGED later:
1. pre-existing work is converged or explicitly adopted;
2. repository is clean;
3. baseline HEAD is current;
4. safe verification entrypoint is selected from project-owned scripts;
5. Autopilot is explicitly enabled with A2 ceiling and dedicated workspace root;
6. first real natural-language product intent completes PLAN -> CODE -> VERIFY -> COMMIT -> RESOLVED without touching unrelated files.

## Implementation sequence

EP-01 DONE: commercial multi-project shell and CONNECTED external project visibility.
EP-02 NOW: durable read-only external-project baseline and dirty-work protection.
EP-03 DONE: conversation -> automatic project routing -> durable command ingress.
EP-04 ACTIVE: A2 promotion gate implemented; first KangarooMath autonomous change waits for protected existing work to converge.
EP-05: preview/browser acceptance bound to artifact feedback.
EP-06: release authority lane and production evidence.
EP-07 BASELINE DONE: backend-owned capability evidence, TOOL_SURFACE_DRIFT admission and Host-observation separation; automatic refresh/reconciliation remains ongoing.

## EP-03 Conversation routing baseline — 2026-10-05

State: IMPLEMENTED_BASELINE.

The conversation gateway now routes natural language to a registered project using deterministic evidence rather than repository names supplied by the human. Stable technical identity, display name, and aliases are distinct registry concepts. Cross-project alias collisions are rejected.

Routing order is explicit project mention, explicit selected/current project, durable conversation binding, then the only registered project. Multi-project ambiguity returns NEEDS_PROJECT_SELECTION rather than guessing.

A new DESIRE receives a system-derived intent id and, when the transport supplies no semantic capability list, a conservative capability-planning requirement derived from the user's statement. Follow-up CORRECTION/REVERSAL/FEEDBACK/APPROVAL may bind to the recent intent in the same durable conversation when unambiguous. The coding/planning authority boundary is unchanged.

The frontend-neutral CLI `scripts/engineeringos_conversation.py` exercises the same gateway used by future chat/voice/web transports. It is an internal ingress surface, not a public unauthenticated write API. The commercial web shell remains read-only until authenticated write ingress is added.


## EP-04 A2 promotion gate — 2026-10-05

State: GATE_IMPLEMENTED / LIVE_PROJECT_BLOCKED_BY_EXISTING_WORK.

Promotion to A2 is evidence-driven and separate from the boolean Autopilot switch. The gate checks a clean baseline, canonical origin, managed branch/upstream, zero upstream divergence, project-owned verification entrypoint, safe A1/A2 assurance ceiling and dedicated workspace root. The registered runner re-evaluates this evidence before Planner/Coder execution; `autopilot_enabled=true` alone is insufficient.

KangarooMath declares target `A2_MANAGED`, canonical origin `star8592/Kangaroo-Practice-Simulator`, managed branch `main`, project-owned quality gate `verify:public`, A2 ceiling and a dedicated isolated workspace root. Its current promotion result is `BLOCKED / PROTECTED_EXISTING_WORK`, so Autopilot remains disabled. A live accidental-enable acceptance proved that even a temporary config with `autopilot_enabled=true` returns `PROMOTION_BLOCKED` before any provider factory is invoked.

## EP-07 Backend tool-surface drift baseline — 2026-10-05

State: IMPLEMENTED_BASELINE.

EngineeringOS now has a backend-owned surface observation path for DevControl rather than a duplicated tool registry. The adapter converts only the Host-observable fields exposed by ChatGPT into DevControl's own devcontrol.chatgpt-host-surface.v2 evidence schema. DevControl's own source/live checker and Host verifier remain the authority.

A deterministic backend-surface admission contract separates ordinary Host-dependent execution from release acceptance:
- missing evidence => DENY;
- source/live mismatch => DENY;
- Host observable mismatch => DENY;
- observable contract match => execution may proceed where Host acceptance is not required;
- release/final acceptance lanes may additionally require immutable host_acceptance=ACCEPTED.

The current live observation reports DevControl 3.1.28, 26 Host-visible tools, source/live PASS, Host observable PASS, zero stale DevControl 2 markers, and host_acceptance=NOT_PROVEN_BY_SURFACE_OBSERVATION. This is deliberately not called full Host acceptance.

EngineeringOS local self-hosting Autopilot is not coupled to this Host evidence because it does not execute through the ChatGPT DevControl tool surface. The gate applies only to workflows that actually depend on that backend surface.

### EP-07 automatic freshness

The singleton Supervisor now refreshes the backend canonical/live surface at a bounded interval and compares its semantic catalog hash with the last real ChatGPT Host observation. Repository/source changes that leave the tool contract unchanged do not invalidate Host evidence. A canonical tool-contract change produces HOST_OBSERVATION_STALE; source/live disagreement produces TOOL_SURFACE_DRIFT. Backend-surface admission requires freshness=CONVERGED in addition to a matching Host observation.

A live acceptance immediately exercised this path: DevControl still exposed 26 tools and source/live remained PASS, while 10 Host-observable descriptors/contracts had changed. EngineeringOS correctly denied Host-dependent admission instead of accepting the matching count.
