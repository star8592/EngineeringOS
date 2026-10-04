# EXP-046: Open System-One backend matrix

Date: 2026-10-04

## Question

Can EngineeringOS replace its current local Laya shadow judge with another open, self-hosted Jev-compatible backend without changing queue, scheduler, approval, human-authority, or execution semantics?

## Contract

Both backends were evaluated against the same EngineeringOS seed EDB:

- routing contract: `processing-lane+authority-policy/v2`;
- 12 labeled processing-lane cases;
- the same deterministic DevControl authority policy;
- the same lane question and option criteria;
- the same admission thresholds;
- no routing or authorization influence.

The backend-neutral HTTP contract is `/v1/systemone`. Human authority remains deterministic project policy and is not evaluated by either model.

## Backends

### Laya typed-decisions

- provider: local Laya service;
- checkpoint revision: `7b928d828b7b0e022f929d9bd2e44165aa270148`;
- device: CUDA;
- lane accuracy: **66.7%**;
- high-risk raw miss rate: **80%**;
- lane ECE: **0.212**;
- median latency: **9.635 ms**;
- authority policy: **12/12, 0 unresolved, 0 mismatch**.

### Decis kev-0.8b

- Decis version: 0.4.0;
- image: `chaitin/decis:kev-0.8b`;
- image id: `sha256:7604a60d7f8ce9180ca0b524a49fcff8474086aaef4a0e3ff85daafb570c5bec`;
- engine: `kev-0.8b`;
- base model: `Qwen/Qwen3.5-0.8B-Base@dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68`;
- device: CPU float32 for this experiment;
- lane accuracy: **91.7%**;
- high-risk raw miss rate: **0%**;
- lane ECE: **0.361**;
- median latency: **493.898 ms**;
- authority policy: **12/12, 0 unresolved, 0 mismatch**.

## Result

kev materially outperformed Laya on seed routing accuracy and safety-critical raw misses, but it still fails admission:

1. only 12 labeled cases exist, below the 100-case minimum;
2. calibration error 0.361 exceeds the 0.10 gate;
3. CPU latency is materially higher than the current CUDA Laya service.

Therefore **no backend is promoted**. Laya remains the current low-latency shadow backend, but this is an operational default only. kev becomes a measured candidate for future evaluation, especially on GPU or after calibration work.

## Architectural consequence

EngineeringOS now treats open System-One engines as interchangeable implementations behind a generic Jev-compatible HTTP provider. Laya and Decis define only endpoint/health/readiness/auth/default-model details. Core EngineeringOS semantics do not change when an engine changes.

This experiment is evidence for provider neutrality, not authorization to switch production behavior.
