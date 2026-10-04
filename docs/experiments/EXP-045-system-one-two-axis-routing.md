# EXP-045: Separate System-One processing lane from human authority

Date: 2026-10-04

The first live Laya EDB run exposed a semantic defect in the original single-axis route enum: work such as `AUTH_POLICY` can require both high-assurance engineering treatment and final human authority. A single choice among `FORMAL_OR_HIGH_ASSURANCE` and `HUMAN_REVIEW` cannot represent that state without losing information.

The first attempted v2 design asked Laya to answer both axes. Live evaluation rejected that design: on the 12-case seed EDB the human-authority model question achieved only 16.7% accuracy and overwhelmingly predicted that human authority was required. Adding richer official-style `criteria` descriptions did not materially fix the failure.

EngineeringOS therefore adopts a stricter boundary:

- `engineering_lane` is System-One advisory evidence;
- human authority is deterministic project policy, not a model question.

The DevControl authority profile lives in `project_profiles/devcontrol/system-one-authority-policy.json`. Known work kinds resolve to `NO_HUMAN_AUTHORITY` or `HUMAN_AUTHORITY_REQUIRED`; unknown kinds become `AUTHORITY_POLICY_UNRESOLVED` rather than being guessed.

The EDB schema remains v2 but now evaluates the two responsibilities separately:

- model lane accuracy;
- high-risk lane miss rate;
- lane calibration error;
- deterministic authority-policy mismatches;
- deterministic authority-policy unresolved cases.

Provider admission requires both sufficient model evidence and a clean authority-policy contract. No model score can alter the authority axis.

The shadow observation key includes `processing-lane+authority-policy/v2`, so evidence from prior single-axis or model-authority semantics remains distinguishable.

Safety remains unchanged: `authorization=UNAVAILABLE`; System-One cannot authorize execution; human authority cannot be synthesized, downgraded, or satisfied by AI.
