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

## Selected default backend

EngineeringOS uses **Laya** as the first default open System-One provider. The provider runs on localhost and exposes the Jev-compatible `/v1/systemone` wire protocol. The EngineeringOS adapter remains provider-neutral so another open implementation can replace Laya without changing queue, policy, approval, or execution semantics.

Laya begins in `SHADOW_ADVISORY` mode. Its recommendation is recorded next to the deterministic scheduler lane but cannot mutate scheduler state. Provider unavailability must degrade to deterministic/reasoning behavior; it must never degrade the Supervisor into an execution-authority fallback.

For routing thresholds, EngineeringOS uses `answer_confidence`, not Laya's type-specific entropy-style `confidence`. Thresholds are learned from Engineering Decision Benchmark data and are not copied from hosted Jev.

## Two-axis routing contract

System-One routing is intentionally split into two independent typed decisions:

1. **Processing lane** — `DETERMINISTIC_CANDIDATE`, `REASONING_REVIEW`, or `FORMAL_OR_HIGH_ASSURANCE`.
2. **Human authority** — `NO_HUMAN_AUTHORITY` or `HUMAN_AUTHORITY_REQUIRED`.

`HUMAN_REVIEW` remains readable as a legacy single-axis route in persisted evidence, but it is not part of the v2 processing-lane domain.

This separation prevents approval semantics from being collapsed into engineering-assurance semantics. A work item may simultaneously require `FORMAL_OR_HIGH_ASSURANCE` processing and `HUMAN_AUTHORITY_REQUIRED`; neither dimension substitutes for the other. System-One still cannot authorize execution.

The routing contract identifier `processing-lane+human-authority/v2` is persisted with shadow projections and observation identities. Changing routing semantics therefore creates new observations even when the snapshot, work item, and model revision are unchanged.
