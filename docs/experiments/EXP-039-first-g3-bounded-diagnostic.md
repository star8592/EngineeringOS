# EXP-039: First G3 bounded deterministic diagnostic

Date: 2026-10-04

EngineeringOS executed its first real G3 bounded action against DevControl without mutating the target repository.

## Action

Work item: `RESOLVE_MAIN_QUALIFICATION`

Bounded action: `run_main_static_qualification`

Execution contract:
- admission action: `run_deterministic_checks`;
- execution backend: DevControl;
- approval authority: host protocol;
- source: exact `origin/main` SHA;
- isolation: `git archive` into a temporary snapshot;
- command: `./scripts/release_gate.sh static`;
- target mutation: forbidden;
- durable command intent and dispatch recorded before execution;
- result and bounded stdout/stderr retained as evidence;
- retries converge by command/idempotency identity derived from item + source SHA + action spec.

## Observed result

The first bounded run checked DevControl source `ae5a68040a6b21e15827a4caa3be5f5903e574ce` and returned `PASS` / exit code `0`. The static gate included version consistency, regression and official-doc contracts, ChatGPT/plugin contracts, Rust formatting/clippy, and workspace tests. No DevControl worktree was modified by EngineeringOS.

## Semantic correction discovered during dogfood

A local static gate PASS is diagnostic evidence; it is not the authoritative definition of `MAIN_QUALIFICATION`. EngineeringOS defines source qualification from the GitHub `DevControl 3 CI` result for the exact source SHA. Therefore the bounded executor must never close `RESOLVE_MAIN_QUALIFICATION` solely from a local static gate.

The G3 controller now behaves as follows:
- authoritative CI `SUCCESS` -> `NO_ACTION`;
- authoritative CI in progress/queued -> `DEFER`;
- authoritative CI `FAILURE` -> bounded local diagnostic may run;
- CI missing/unknown -> bounded local diagnostic may run once per source/action identity.

This prevents EngineeringOS from competing with an already-running authoritative CI job while still providing deterministic diagnosis when authoritative evidence is missing or failed.

## Gate significance

This is a G3 pilot, not full G3 graduation. Merge, rebase, delete, deploy, publishing, authentication changes, and unrestricted shell execution remain outside the allowed surface.

## Continuous-loop closure result

On the next continuous supervisor cycle, GitHub `DevControl 3 CI` for the exact checked source SHA completed successfully. EngineeringOS therefore did **not** repeat the local bounded check. The G3 event log remained at three events (intent, dispatch, confirmed result), while the queue reconciler closed `RESOLVE_MAIN_QUALIFICATION` using authoritative evidence:

- verifier: `engineeringos-authoritative-ci-reconciler`;
- closure kind: `AUTHORITATIVE_CI_SUCCESS`;
- evidence: exact GitHub Actions run URL + exact source SHA.

The P1 item disappeared from the Action Brief automatically. This is the first complete EngineeringOS path from observed engineering uncertainty -> bounded diagnostic -> authoritative external evidence -> deterministic queue closure, without target-project mutation.
