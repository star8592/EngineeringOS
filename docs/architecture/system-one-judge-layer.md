# Open System-One Judge Layer

EngineeringOS should support a provider-neutral, self-hosted fast judgment layer for high-volume engineering events.

## Purpose

Fast judges classify and route events such as duplicate-task candidates, semantic-conflict candidates, architecture drift, approval/tool-surface changes, and whether deeper reasoning or formal verification is required.

They are scouts/routers, not proof kernels.

## Desired cascade

engineering events
→ small fast open judge
→ deterministic automation when confidently low-risk
→ larger local judge for uncertain cases
→ strong reasoning model for complex/high-risk semantics
→ model checking/formal proof for critical invariants.

## Requirements

- open-weight/self-hostable by default;
- provider-neutral typed interface;
- calibrated probabilities, not only labels;
- replaceable implementations;
- benchmarked on EngineeringOS/DevControl evidence rather than vendor leaderboards;
- false-negative cost measured explicitly for safety-critical routing.

## Open backend boundary

EngineeringOS consumes open System-One engines through a provider-neutral Jev-compatible HTTP contract. The shared adapter owns `/v1/systemone`; backend adapters only define endpoint, health/readiness, authentication, and default model names. Replacing Laya with Decis/kev or another compatible engine must not change queue, scheduler, policy, human-authority, approval, or execution semantics.

The currently active shadow backend is **Laya `typed-decisions`**, because it is already running locally on CUDA with low latency. This is an operational default, not an architectural dependency or a quality endorsement. EXP-046 shows that Decis `kev-0.8b` materially outperforms it on the seed EDB but still fails the calibration/sample-size admission gates.

All model backends begin in `SHADOW_ADVISORY` mode. Recommendations are recorded beside the deterministic scheduler lane and cannot mutate scheduler state. Backend unavailability must degrade to deterministic/reasoning behavior; it must never create an execution-authority fallback.

Admission uses measured EDB accuracy, safety-critical misses, calibration and sample size. Backend-specific confidence fields are normalized into `answer_confidence`; no vendor threshold is copied into EngineeringOS policy.

## Two-axis routing contract

System-One routing has two axes with **different authorities**:

1. **Processing lane** — `DETERMINISTIC_CANDIDATE`, `REASONING_REVIEW`, or `FORMAL_OR_HIGH_ASSURANCE`. Laya may provide shadow advisory evidence for this axis.
2. **Human authority** — `NO_HUMAN_AUTHORITY`, `HUMAN_AUTHORITY_REQUIRED`, or `AUTHORITY_POLICY_UNRESOLVED`. This axis is decided only by deterministic project policy.

`HUMAN_REVIEW` remains readable as a legacy single-axis route in persisted evidence, but it is not part of the current processing-lane domain.

This separation prevents approval semantics from being collapsed into engineering-assurance semantics. A work item may require high-assurance engineering treatment and also require final human authority; neither dimension substitutes for the other. The model is never allowed to create, remove, or satisfy human authority.

The active routing contract identifier is `processing-lane+authority-policy/v2`. Shadow observation identity includes this contract identifier so evidence collected under older semantics cannot be silently deduplicated against current observations.

Unknown work kinds do not get guessed into yes/no authority. They become `AUTHORITY_POLICY_UNRESOLVED` until the project profile defines an explicit rule.


## EDB curation boundary

Continuous shadow observations are not benchmark truth. EngineeringOS deterministically groups repeated observations by engineering semantics into an EDB candidate pool, but every generated candidate remains `edb_gold=false`, with `expected_lane=null` and `label_source=null`.

The curation layer may prioritize disagreement, high-assurance, low-confidence, and unresolved-policy examples for review, but it cannot adjudicate them. Missing semantic context yields `BLOCKED_INCOMPLETE_CONTEXT`; unresolved human-authority policy yields `BLOCKED_AUTHORITY_POLICY_UNRESOLVED`.

Only a later explicit adjudication step may create gold labels. Control Room is projection-only and exposes candidate counts/status; it does not provide a parallel approval or implicit labeling path.
