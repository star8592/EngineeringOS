# ADR-026: Human owns intent; system owns engineering

Status: ACCEPTED  
Date: 2026-10-04

## Decision

EngineeringOS adopts **Human owns intent. System owns engineering.** as its highest product invariant.

The primary target user needs software capability but must not be required to become a software engineer. Software-engineering mechanics are system responsibilities. Human escalation is reserved for material intent ambiguity/conflict or authority explicitly required by policy.

## Consequences

1. User Engineering Burden is a first-class product metric and should trend toward zero.
2. Git/CI/deployment terminology is not the default customer interaction model.
3. LLM reasoning cannot be execution authority. Deterministic evidence/policy boundaries remain authoritative.
4. Existing EngineeringOS control-plane rigor is retained and becomes the hidden reliability substrate of the simpler product.
5. Product autonomy is progressive and permission-scoped; read-only diagnosis precedes mutation.
6. Machine-resolvable engineering problems must not be converted into user chores.
7. A request to reverse or change a feature is treated as intent evolution; EngineeringOS owns the engineering consequences.
