# EXP-042: Replace hosted Jev with local open Laya

Date: 2026-10-04

EngineeringOS selects **Laya** as the first default open System-One backend.

Why Laya:

- open source and self-hostable;
- model weights are Apache-2.0;
- native non-autoregressive typed decisions: \`choice\`, \`score\`, and \`noul\`;
- exposes a Jev-compatible \`POST /v1/systemone\` HTTP protocol;
- returns per-option probabilities and \`answer_confidence\`;
- can run entirely on localhost.

EngineeringOS does **not** treat Laya as an authorization engine. The provider adapter maps Laya output into the existing advisory-only System-One contract. Deterministic project policy remains authoritative, and high-assurance work is escalated regardless of model confidence.

The Supervisor integration begins in **shadow advisory** mode. Each cycle records Laya's suggested lane next to the deterministic scheduler lane. The result is evidence for the Engineering Decision Benchmark (EDB), not permission to execute.

Activation requires:

1. local health succeeds;
2. EDB raw accuracy meets the configured threshold;
3. high-risk raw miss rate remains below the configured threshold;
4. no System-One result can produce authorization;
5. provider failure degrades to deterministic/reasoning behavior rather than stopping the control plane.

The first seed EDB contains representative deterministic, reasoning, formal/high-assurance, and human-authority cases. It is intentionally small and will be expanded from real dogfood outcomes.

## Confidence semantics

EngineeringOS gates on Laya's \`answer_confidence\` (the probability mass of the selected answer), not Laya's generic \`confidence\` field. Laya documents that \`confidence\` has type-specific entropy semantics for \`choice\`/\`score\`, while \`answer_confidence\` is the calibrated answer probability. A Jev threshold must therefore never be copied blindly to Laya.
