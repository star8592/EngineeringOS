# EXP-049: Control Room command receipt and outcome-evidence drill-down

Date: 2026-10-04

## Goal

Make the existing durable command transaction boundary visible to operators without introducing a second execution state.

## Implementation

A new read-only projector replays `control-loop/events.jsonl` and joins replayed command state back to the current control-loop projection.

It surfaces:

- command/event timeline;
- idempotency identity;
- side-effecting flag;
- attempt count;
- replayed outcome;
- retry/probe decision;
- outcome evidence references;
- SHA-256 evidence integrity.

## Safety

The projector never appends events and never executes/probes/retries commands. It is explicitly marked `DERIVED_FROM_COMMAND_EVENT_LOG` and `target_mutation_authorized=false`.

UNKNOWN_COMPLETION remains visible and, for side-effecting commands, maps to `PROBE_REQUIRED`. A successful command with missing or mismatched evidence is reported as evidence-invalid.

## Control Room

The dashboard now shows command count, succeeded commands, unknown completion, probe-required count, verified receipts and invalid evidence. Each item can be expanded to inspect the event timeline and evidence verification.

This closes the operator visibility gap between durable command semantics and the Human Control Room while preserving one execution authority.
