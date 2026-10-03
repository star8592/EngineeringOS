# EXP-006: Open System-One Benchmark

## Goal

Select or reject open/self-hosted fast-judge candidates using an Engineering Decision Benchmark built from real DevControl engineering history.

## Phase 1

1. Define provider-neutral typed judge contract.
2. Build a small high-confidence gold set from existing DevControl evidence.
3. Establish a deterministic baseline and a general-purpose local-model baseline.
4. Evaluate candidate open fast judges on identical inputs.
5. Measure calibration and false negatives in addition to headline accuracy.

## Guardrails

- No paid/closed model becomes a required runtime dependency.
- No candidate is selected before local reproducible evaluation.
- Judge output remains probabilistic evidence; high-risk decisions escalate.
- Training/fine-tuning is considered only after baseline data shows where specialization adds value.
