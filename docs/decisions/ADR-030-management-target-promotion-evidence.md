# ADR-030: Management target is authority; promotion evidence is eligibility

Status: Accepted

## Problem

External projects previously had two overlapping controls: management_target=A2_MANAGED and autopilot_enabled. Requiring both created an approval ambiguity: a human could authorize A2 management while the runner remained disabled by a second legacy switch, or an operator could flip the boolean and appear to widen authority.

## Decision

EngineeringOS separates durable authority from runtime eligibility.

- management_target expresses the human/policy management goal.
- promotion evidence proves whether the project currently satisfies the engineering conditions for that goal.
- effective Autopilot is derived from those two facts.
- the legacy autopilot_enabled flag remains only for projects that have not yet migrated to management_target.

For A2_MANAGED, effective autonomous execution requires current promotion evidence to be eligible. No second boolean approval is required. Conversely, setting the legacy boolean cannot bypass promotion.

## Safety

Promotion still requires the clean baseline, canonical origin, managed branch/upstream, zero upstream divergence, project-owned verification entrypoint, safe A1/A2 assurance ceiling, and dedicated workspace root.

A blocked promotion is a machine safety state, not a product-intent question. It does not become NEEDS_INTENT and does not invoke Planner/Coder.

## Consequence

KangarooMath can remain physically protected while existing work is dirty. Once that work independently converges and all promotion gates pass, its already-authorized A2 management target becomes effective automatically. The user is not asked to approve the same management decision twice.
