# ADR-029: Deterministic conversation-to-project routing

Status: Accepted

## Decision

Natural conversation may select a project automatically, but project selection is a deterministic routing decision rather than model authority.

Routing precedence is:

1. explicit project name/display name/registered alias in the current utterance;
2. explicit current-project context supplied by the UI/session;
3. durable conversation binding from prior accepted turns;
4. the only registered project, when exactly one exists;
5. otherwise NEEDS_PROJECT_SELECTION.

If multiple project identities are explicitly mentioned, EngineeringOS does not guess. Cross-project aliases are forbidden by registry validation.

## Process control

Process-control turns such as “继续” are not new product intent. They may resume or continue already-routed work but MUST NOT append a new DESIRE/CORRECTION merely because the user asked the system to proceed.

## Intent identity

For a new DESIRE, the transport does not require the human to provide an intent identifier. EngineeringOS derives one deterministically. A later CORRECTION, REVERSAL, FEEDBACK, or product-level APPROVAL may bind to the most recent intent in the same durable conversation when unambiguous.

## Idempotency

command_id is the transport retry boundary.

- same command id + same normalized command envelope => idempotent success, no journal growth;
- same command id + different envelope => IDEMPOTENCY_CONFLICT.

This prevents network/client retries from creating duplicate intent generations or duplicate work.

## Approval scope

Conversational APPROVAL means product feedback acceptance only and is durably marked PRODUCT_FEEDBACK_ONLY.

It cannot satisfy:
- project execution admission;
- MCP/host tool approval;
- authentication/authorization;
- release approval;
- deployment/production approval;
- destructive/data-mutation approval.

Those remain separate deterministic/protocol authority boundaries under ADR-023.

## Consequences

The user may say “袋鼠数学，计算训练入口还是不明显” without selecting a repository or engineering tool. The route is explainable and replayable. Models may classify conversational semantics, but cannot silently choose a conflicting project or manufacture engineering authority.
