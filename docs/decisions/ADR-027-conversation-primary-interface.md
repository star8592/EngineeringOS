# ADR-027: Conversation is the primary product interface

Status: ACCEPTED
Date: 2026-10-04

## Decision

EngineeringOS adopts conversation—especially natural voice conversation—as the primary human interface.

The canonical interaction loop is:

`human expression → durable intent update → autonomous engineering → result/preview → human feedback → intent update`.

Dashboards, forms, Git/provider screens, queues, and engineering controls are secondary inspection or acceleration surfaces.

## Rationale

Humans should not learn the control structures of software engineering in order to create and operate software. Natural dialogue supports incomplete initial specifications, iterative judgment, interruption, correction, reversal, and progressive refinement better than forcing intent into engineering forms.

## Architectural consequence

Conversation sessions are ephemeral transports; intent and task state are durable backend state. Voice may be interrupted or disconnected without losing the engineering task. Speech interruption and task cancellation are distinct events.

The conversational model does not become engineering authority. It interprets human intent; deterministic policy/evidence controls engineering state transitions and completion claims.
