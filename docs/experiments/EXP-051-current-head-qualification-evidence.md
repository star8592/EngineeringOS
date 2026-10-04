# EXP-051: Split current-head CI absence from failure

Date: 2026-10-04

## Problem

The continuous DevControl shadow supervisor previously reported `qualification=UNKNOWN` whenever the current `origin/main` SHA lacked a completed `DevControl 3 CI` result.

That collapsed at least three different situations:

1. no current-head CI run exists;
2. a current-head CI run is still executing;
3. the GitHub workflow query itself failed.

It also made the work queue say only `qualification evidence is unknown`, which was not actionable enough.

## Implementation

EngineeringOS adds a generic workflow-evidence classifier:

- `NO_RUN`;
- `RUNNING`;
- `PASS`;
- `FAIL`.

The DevControl evidence adapter keeps GitHub query transport separate from workflow evidence classification.

The manager keeps stable queue kinds but emits explicit machine-readable `evidence_state` and `reason_code` metadata.

Examples:

- `NO_RUN` → `RESOLVE_MAIN_QUALIFICATION`: current source head has no DevControl 3 CI run;
- `RUNNING` → the same stable work item, but reason says the existing run is still active and must not be duplicated;
- `FAIL` → `RESTORE_MAIN_QUALIFICATION` with the exact non-success conclusion;
- GitHub query error → `RESOLVE_MAIN_QUALIFICATION` with `QUERY_ERROR`.

Control Room action details now include current source SHA, workflow-query transport state, CI evidence state, latest run evidence, and a state-specific suggested resolution.

## Live trigger

At the start of this experiment, DevControl `main=b07fb9e7b7280cf5f6207c7f6fe57b8aab67ca06` had zero workflow runs returned for that exact commit.

Under the new semantics this is `NO_RUN`, not `FAIL`.

## Safety result

The system remains fail-closed for qualification-dependent actions, while removing the semantic ambiguity that previously overloaded `UNKNOWN`.
