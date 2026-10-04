# Conversational Product Interface

Status: CANONICAL PRODUCT PRINCIPLE

## Principle

EngineeringOS is conversation-first, not dashboard-first.

The normal user interaction is the ancient human loop:

**Say what you want → the system acts → show/tell the outcome → the human reacts, corrects, or changes direction → continue.**

Voice and chat are two transports for the same durable conversation. Voice is a first-class default, not transcription bolted onto a form workflow.

The user must not adapt to software-engineering machinery. EngineeringOS adapts the machinery to the user's natural expression.

## Frontstage / backstage

### Frontstage — what the human experiences
- talk naturally;
- interrupt naturally;
- change their mind;
- show an image/screenshot/file when easier than describing it;
- receive a concise spoken/text update while work continues;
- see the actual result when visual inspection matters;
- say "这个不对，改回去" without specifying implementation mechanics;
- answer only genuine product-intent questions.

### Backstage — what EngineeringOS owns
- turn segmentation and conversation state;
- intent extraction and versioning;
- task decomposition and delegation;
- project/world-model updates;
- Git/source-control mechanics;
- tests, CI, formal/static checks;
- security and permission enforcement;
- deployment and rollback;
- evidence/provenance;
- convergence and cleanup;
- durable task continuation.

The backstage must not leak into the frontstage merely because an engineering operation is difficult.

## The Ping-Pong Loop

Every meaningful turn is classified as one or more of:

- `DESIRE`: "我想加一个微信登录。"
- `FEEDBACK`: "这个首页太复杂了。"
- `CORRECTION`: "不是给学生，是给家长。"
- `REVERSAL`: "这个功能先不要了。"
- `QUESTION`: "现在做到哪了？"
- `APPROVAL`: "这个效果可以。"
- `ARTIFACT`: screenshot/file/example/reference.
- `INTERRUPTION`: stop/yield/change direction while the system is speaking or working.

These are not forms. Classification is internal.

Each turn updates a durable Intent Ledger. Engineering work is derived from the ledger, not from isolated chat messages.

## Response contract

Normal system responses contain at most the information the user currently needs:

1. **Acknowledgment of understood intent**, only when useful.
2. **Current action/status**, in ordinary language.
3. **Result/preview/evidence**, when available.
4. **One decision request**, only if a genuine intent conflict blocks progress.

Do not expose branch names, SHAs, CI jobs, worktrees, package managers, merge strategies, deployment internals, or agent orchestration in normal mode.

Engineering details are an optional inspection surface, never required homework.

## Work while talking

Conversation and backend work are decoupled.

A long-running engineering task must not freeze the conversation. The user can interrupt, add constraints, or reverse direction. New turns update task intent; EngineeringOS determines whether to continue, supersede, cancel, or safely converge in-flight work.

A speech interruption is not automatically a task cancellation. "别说了" means yield speech; "这个功能不要了" changes task intent.

## Feedback rhythm

Do not narrate every internal operation. Surface feedback according to significance:
- immediate lightweight acknowledgment for accepted intent;
- passive progress for ongoing work;
- preview when human judgment is valuable;
- completion only after evidence verifies the outcome;
- interruptive confirmation only for material irreversible/user-authority boundaries;
- intent question only when the system cannot infer the desired outcome safely.

## Voice architecture

Preferred product architecture:
- realtime/full-duplex conversational front end;
- durable backend EngineeringOS control plane;
- backend tools/agents perform long-running work;
- conversation stays responsive while delegated work continues;
- interruptions and corrections are first-class events;
- text transcript is a secondary durable representation, not the user's required input format.

Voice transport is replaceable. Product state must live in the backend Intent Ledger / World Model, not only inside an ephemeral audio session.

## Visual result loop

Software is often easier to judge than to specify. EngineeringOS therefore optimizes for:
**show early → react naturally → revise safely**.

For UI/product work, the system should proactively produce a runnable preview, screenshot, or live result at meaningful checkpoints. The human may respond with natural evaluative language ("这里太挤", "这个感觉对了", "把左边那个去掉"). EngineeringOS binds that feedback to the relevant artifact/context.

## Design test

For every new UI control ask:
> Could an ordinary person accomplish this by simply telling the system what they want?

If yes, conversation is primary and the control is optional acceleration/visibility.
If no, determine whether the control represents a genuine human decision or leaked engineering machinery.

## Success metrics

- User Engineering Burden.
- turns from desire to verified outcome;
- percentage of turns requiring engineering vocabulary (target ~0);
- unnecessary clarification rate;
- intent-correction recovery rate;
- interruption recovery rate;
- time to first meaningful preview;
- verified completion accuracy;
- spoken completion claim vs actual final-state agreement.

## Default status surface

The primary status surface answers only three ordinary-user questions: **现在怎么样？正在做什么？需要我决定什么？** Engineering evidence, queues, receipts, assurance levels, and control-plane internals remain available as optional Engineering Details and are not required to use the product.
