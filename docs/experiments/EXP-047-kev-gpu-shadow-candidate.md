# EXP-047: GPU kev parallel-shadow candidate

Date: 2026-10-04

EngineeringOS evaluated Decis `kev-0.8b` natively on the same RTX 5070 Ti that hosts the active Laya shadow provider.

## Reproducible runtime

- Decis source revision: `ae7c27be7774efc75411b97037a9d2f9ff98abc3` (0.4.0).
- kev adapter revision: `54f4f8777356cd5bbbb6c6919c657f26e6f2f6d8`.
- Qwen3.5-0.8B base revision: `dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68`.
- Device: CUDA, dtype bfloat16.
- Adapter is passed with the documented `--model-path kev-0.8b=<path>`.
- Service runs with `HF_HUB_OFFLINE=1` after installation, so runtime does not depend on network availability.
- No Decis source patch is applied.

## Seed EDB result

On the same 12-case EDB v2 corpus:

| Backend | Lane accuracy | High-risk raw miss | Lane ECE | Median latency |
| --- | ---: | ---: | ---: | ---: |
| Laya typed-decisions / CUDA | 66.7% | 80.0% | 0.212 | 9.8 ms |
| Decis kev-0.8b / CPU fp32 | 91.7% | 0.0% | 0.361 | 9905.3 ms |
| Decis kev-0.8b / CUDA bf16 | **91.7%** | **0.0%** | 0.362 | **22.3 ms** |

GPU kev therefore removes the CPU latency blocker while preserving the seed accuracy/high-risk advantage. It is eligible to run as a **parallel shadow candidate**, but not to influence routing.

## Why it is not promoted

Provider admission remains unchanged:

- at least 100 adjudicated EDB cases are required; current gold corpus has 12;
- lane ECE must be <= 0.10; observed kev ECE is ~0.362;
- human authority remains deterministic project policy regardless of model quality.

No threshold is lowered to fit the model.

## Upstream 0.4.0 observations

Two pinned-version behaviors were found during native deployment:

1. `decis models` reports a cache-only downloaded engine as `needs weights` because its status path treats only a local model directory as ready while the resolver represents the default Hugging Face cache as a Hub source.
2. `decis download` intentionally fetches only the declared kev adapter files, while serving the adapter through its Hub repository path may ask Hugging Face for a fuller repository snapshot. In offline mode that can fail despite the required adapter files being present.

EngineeringOS does not patch Decis. The managed service uses its documented `--model-path` override for the adapter and a pinned cached base model, which makes offline startup deterministic.

## Decision

Keep Laya as the active shadow backend for continuity. Run GPU kev in parallel shadow only, collect real comparative observations, expand adjudicated EDB, and reassess promotion only through the existing admission contract.
