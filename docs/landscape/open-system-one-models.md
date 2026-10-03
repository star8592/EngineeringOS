# Open System-One / Fast Judge Landscape

Status: research backlog; no model selected yet.

The project will evaluate open/self-hosted Jev-like decision models rather than making a closed paid API foundational infrastructure.

Initial candidate families from the current discussion/research include small encoder/decision-head approaches such as Laya and larger Qwen-derived typed-decision approaches such as Kev/Nimble. These names are benchmark candidates, not dependencies or endorsements.

## Selection rule

Do not select from marketing claims or external leaderboards alone. Build an Engineering Decision Benchmark (EDB) from real DevControl history and compare candidates on the same local workload and hardware.

## EDB target labels

- TASK_DUPLICATE / TASK_DISTINCT
- SEMANTIC_CONFLICT / NO_SEMANTIC_CONFLICT
- ARCHITECTURE_DRIFT / ARCHITECTURE_CONFORMANT
- SAFE_TO_AUTO_CONVERGE / REQUIRES_DEEP_REVIEW
- TOOL_SURFACE_CHANGE / NO_TOOL_SURFACE_CHANGE
- APPROVAL_SEMANTICS_CHANGE / NO_APPROVAL_CHANGE

## Metrics

Accuracy, precision, recall, F1, calibration/ECE, false-negative rate, latency, throughput, VRAM/RAM, CPU viability, and energy/operational cost. Ground truth should preferentially come from deterministic evidence, confirmed architecture decisions, merge/release outcomes, and production incidents rather than synthetic LLM labels.
