# EXP-043: Evidence-gated System-One admission

Date: 2026-10-04

EngineeringOS now treats local Laya activation as a measured admission problem rather than a binary installed/not-installed switch.

Admission states:

- `UNAVAILABLE`: provider health is down.
- `SHADOW_NO_BENCHMARK`: provider is healthy but no EDB report exists.
- `SHADOW_INSUFFICIENT_EVIDENCE`: benchmark exists but has fewer than 100 labeled cases.
- `SHADOW_UNQUALIFIED`: enough cases exist but one or more quality thresholds fail.
- `QUALIFIED_ADVISORY`: benchmark thresholds pass; the model remains advisory-only.

Initial thresholds:

- at least 100 labeled EDB cases;
- raw route accuracy >= 0.85;
- high-risk raw miss rate <= 0.05;
- expected calibration error <= 0.10.

Even `QUALIFIED_ADVISORY` carries `authorization=UNAVAILABLE` and `influence_routing=false`. A later, separately reviewed change may allow qualified System-One evidence to influence non-authoritative routing, but it still cannot authorize execution or lower deterministic/formal assurance requirements.

The EDB runner now records correctness and expected calibration error and can persist its report into the EngineeringOS runtime tree. This makes future activation evidence durable and inspectable in Control Room rather than a one-off terminal result.
