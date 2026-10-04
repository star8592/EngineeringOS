# Conversation UX Acceptance Scenarios

These scenarios are product-level acceptance tests. The UI is wrong if it forces engineering terminology or unnecessary forms.

1. User: "给家长加微信登录。"
   Expected: record intent, start/plan work, no Git question.

2. During work user: "不是所有人，只给家长。"
   Expected: revise same intent, supersede incompatible in-flight work safely.

3. User interrupts spoken status: "行了别念了，给我看。"
   Expected: stop speech, preserve task, show available result/preview.

4. User after preview: "这里太挤了，按钮放下面。"
   Expected: bind feedback to visible artifact/context and revise; no CSS/layout jargon required.

5. User: "这个功能还是不要了。"
   Expected: record reversal, determine engineering rollback/forward-fix internally; ask only if product consequences are ambiguous.

6. System finds dirty worktree / failed CI / dependency conflict.
   Expected: handle or report ordinary-language status; never ask user to choose merge/rebase/cherry-pick.

7. Two prior user statements conflict materially and both remain plausible.
   Expected: ask one concise outcome question. This is NEEDS_INTENT.

8. Backend task takes 20 minutes.
   Expected: conversation remains usable; new feedback can alter/supersede task; completion is reported only after evidence.

9. Voice session disconnects.
   Expected: durable task/intent survives; reconnect can continue without reconstructing engineering state from transcript alone.

10. System has code/UI presence but no runtime verification.
    Expected: say implementation is found/in progress, not "done".
