# Commercial Shell

## Product promise

AI开发经理不是面向程序员的代码编辑器，而是面向产品拥有者的持续软件团队：

> 人只负责表达想要什么，系统负责把它长期可靠地变成软件。

## Primary information architecture

The commercial surface has five primary destinations:

1. 产品 — all managed products and the current product status.
2. 对话 — the primary future write interface for desires, corrections, feedback and reversals.
3. 进展 — ordinary-language development outcomes and current work.
4. 需要你决定 — only genuine product-intent conflicts.
5. 设置 — product connection and advanced engineering diagnostics.

Git, branches, commits, SHA, CI, providers, MCP and agent routing are not primary-user concepts. They remain available only in the collapsed Engineering Details surface.

## Commercial projection boundary

The browser never reads the project registry or project journals directly. commercial_projection.py derives a privacy-safe read model from registered projects and durable journals. It exposes only:

- product identity and connection state;
- whether safe Autopilot is enabled;
- user-facing status: HEALTHY, WORKING, or NEEDS_INTENT;
- bounded ordinary-language active work;
- bounded recently completed outcomes;
- bounded intent questions.

It MUST NOT expose repository paths, workspace paths, source SHAs, allowed paths, verification commands, provider diagnostics, or commit receipts.

This projection is the multi-project contract. Registering another real project, such as a mathematics product, should make it appear automatically without hard-coded UI entries.

## v0.1 boundary

The current commercial shell is intentionally read-only. The conversation composer is visible to establish the final interaction model, but sending is disabled until the authenticated conversation-command write API is attached. The UI must never pretend a user request was accepted when no durable intent event was written.

EngineeringOS Control Room remains available under Settings -> Engineering Details for advanced diagnosis and evidence inspection.
