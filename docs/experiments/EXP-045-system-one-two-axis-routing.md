# EXP-045: Split System-One processing lane from human authority

Date: 2026-10-04

The first live Laya EDB run exposed a semantic defect in the original single-axis route enum: work such as `AUTH_POLICY` can require both high-assurance engineering treatment and final human authority. A single choice among `FORMAL_OR_HIGH_ASSURANCE` and `HUMAN_REVIEW` cannot represent that state without losing information.

EngineeringOS therefore moves System-One to a two-axis typed contract:

- `engineering_lane`: deterministic, reasoning, or formal/high-assurance;
- `human_authority`: required or not required.

Laya answers both questions in one `/v1/systemone` request, preserving one inference pass. Existing single-question provider calls remain supported for compatibility.

The EDB schema is upgraded to v2 and measures the two axes independently: lane accuracy, human-authority accuracy, high-risk lane misses, human-authority misses, and calibration error for each axis. A v1 EDB report is explicitly `SHADOW_BENCHMARK_SCHEMA_STALE` and cannot qualify a provider.

The shadow observation key now includes `routing_contract`. This prevents data collected under the old single-axis semantics from being silently deduplicated against v2 observations.

Safety remains unchanged: both axes are advisory-only; `authorization=UNAVAILABLE`; deterministic policy/formal assurance may escalate processing, and human authority cannot be synthesized by the model.
