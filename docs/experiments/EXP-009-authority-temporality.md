# EXP-009: Authority and Temporal Reconciliation

## Goal

Make Fact Registry reconciliation predicate-specific and time-aware.

## Work

- define authority policies by predicate rather than globally;
- distinguish observation time from validity time;
- model stale claims without deleting historical truth;
- ingest live runtime identity as runtime evidence;
- connect release ID to full source SHA/artifact digests where evidence exists;
- produce `RESOLVED`, `DRIFT`, `CONTRADICTION`, `STALE`, and `UNKNOWN` reconciliation states.

## Guardrail

Authority chooses how a question is resolved; it does not erase lower-authority evidence. Conflicting evidence remains inspectable.
