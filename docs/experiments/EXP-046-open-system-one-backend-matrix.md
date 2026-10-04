# EXP-046: Open System-One backend matrix

Date: 2026-10-04

EngineeringOS now evaluates open System-One engines through one provider-neutral Jev-compatible HTTP contract instead of embedding backend-specific semantics in the control plane.

## Implemented adapter boundary

`JevCompatibleHTTPProvider` owns the shared `/v1/systemone` request/response contract. `LayaLocalProvider` and `DecisProvider` are thin endpoint/health adapters. The EDB runner accepts `--backend laya|decis`, so backend comparison no longer requires modifying scheduler, policy, approval, authority, or benchmark semantics.

## Live comparison

The same 12-case EDB v2 corpus and the same deterministic DevControl authority policy were used for both engines.

| Backend | Device | Lane accuracy | High-risk raw miss | Lane ECE | Median latency |
| --- | --- | ---: | ---: | ---: | ---: |
| Laya `typed-decisions` | CUDA | 66.7% | 80.0% | 0.212 | 9.8 ms |
| Decis `kev-0.8b` | CPU fp32 | 91.7% | 0.0% | 0.361 | 9905.3 ms |

Human-authority policy remained deterministic and scored 12/12 with zero unresolved or mismatched rules for both runs.

## Interpretation

kev is materially better on the seed lane-classification set, especially on high-assurance cases, but it is not eligible for promotion:

- the corpus has only 12 adjudicated cases, below the 100-case admission minimum;
- calibration error is 0.361, above the 0.10 gate;
- the normalized provider-reported CPU engine latency is roughly 9.9 seconds median on this host, far too slow for the default shadow loop compared with the existing CUDA Laya path;
- the comparison is a seed experiment, not evidence for changing authorization or execution policy.

Laya also remains unqualified. Its advantage is latency, not correctness. EngineeringOS therefore keeps Laya as the active **shadow-only** backend while expanding EDB and evaluating calibration/fine-tuning or a GPU kev deployment.

No model backend may affect human-authority policy, authorize execution, or reduce deterministic/formal assurance.

## Durable evidence

The measured summary is stored in `benchmarks/results/system-one-open-backends-2026-10-04.json`.

The canonical Decis response identified the tested model as `decis/kev-0.8b@vendored-90990a5`; the canonical Laya response identified `typed-decisions`.
