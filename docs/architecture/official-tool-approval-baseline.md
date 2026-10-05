# Official Tool / Approval Baseline

Updated: 2026-10-05

This document records the external protocol/product facts EngineeringOS relies on. It is a baseline, not a substitute for refreshing official documentation when behavior changes.

## OpenAI official documentation

- MCP servers / approvals: https://developers.openai.com/api/docs/guides/tools-connectors-mcp
  - remote MCP tool calls have an explicit approval mechanism;
  - approval policy can be configured with `require_approval`;
  - approval request/response are protocol-visible items, not an EngineeringOS-specific UI convention.
- Plugin tool design: https://developers.openai.com/plugins/plan/tools
  - tool descriptions must state actual behavior, limits, and prerequisites;
  - `readOnlyHint`, `destructiveHint`, and `openWorldHint` must match real behavior;
  - annotations do not replace server-side authorization, validation, or consequential-action confirmation;
  - tool surfaces should map to coherent user outcomes and similar tools must not have overlapping descriptions that create selection ambiguity.
- MCP server authentication/authorization: https://developers.openai.com/plugins/build/mcp-server
  - private-data reads and user actions require authentication when applicable;
  - authorization is enforced server-side for every request and must never be delegated to the model.
- Agents guardrails / human review: https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
  - approval pauses execution and returns resumable state;
  - the same run is resumed after approval/rejection;
  - validation should live adjacent to the side-effecting tool boundary.
- Plugin reference: https://developers.openai.com/plugins/reference
  - confirmation-gated UI must tolerate arguments not being available before approval;
  - host-delivered tool input after approval is part of the host/tool lifecycle.
- OpenAI Docs MCP: https://developers.openai.com/learn/docs-mcp
  - official documentation should be consulted directly for OpenAI API/product behavior.

## MCP official documentation / SDK specification

- Tool annotations (official MCP SDK docs): https://py.sdk.modelcontextprotocol.io/zh/servers/tools/
  - `read_only_hint`, `destructive_hint`, `idempotent_hint`, and `open_world_hint` describe behavior;
  - annotations are hints, not a security mechanism and must not be treated as authorization.
- MCP Apps authorization: https://apps.extensions.modelcontextprotocol.io/api/documents/authorization.html
  - authentication/authorization is enforced at the protocol/HTTP boundary rather than encoded as ad-hoc tool errors.
- MCP Tasks extension: https://tasks.extensions.modelcontextprotocol.io/specification/draft/tasks
  - durable asynchronous task state is an explicit protocol concept; this extension is currently treated as reference material unless/until adopted by the project compatibility baseline.

## EngineeringOS interpretation

EngineeringOS separates four concepts that must never be conflated:

1. **Authentication/authorization** — who/what may access the server or capability.
2. **Project policy** — whether this project permits the proposed action in the current state.
3. **User/host approval** — an explicit confirmation requested/resumed through the host protocol when required.
4. **Execution evidence** — whether the side effect actually occurred and what outcome was verified.

Tool annotations help classify a proposed action. They cannot grant permission, bypass project policy, manufacture host approval, or prove execution success.
