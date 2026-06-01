---
title: "Six-Shape Approval Response Taxonomy: Beyond Binary Allow/Deny"
description: "The Claude Agent SDK exposes six distinct responses to a tool-approval prompt — approve, approve with changes, approve and remember, reject, suggest alternative, redirect entirely — composed from three callback knobs."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - approval response taxonomy
  - tool approval response shapes
  - canUseTool response taxonomy
last_reviewed: 2026-05-30
---

# Six-Shape Approval Response Taxonomy

> Six distinct approval responses — approve, approve-with-changes, approve-and-remember, reject, suggest alternative, redirect entirely — compose from three callback knobs over a binary protocol.

The underlying protocol is binary: a `canUseTool` callback returns either `PermissionResultAllow(updated_input=...)` or `PermissionResultDeny(message=...)` ([Claude Agent SDK — Handle approvals and user input](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests)). The six-shape taxonomy is what those two return types compose into when three independent knobs — input mutation, persisted permission updates, and the deny message — are treated as design surfaces. The Agent SDK doc enumerates the six shapes verbatim; harness authors decide which to surface and operators decide when to reach for them.

## The Three Underlying Knobs

Every shape is a permutation of these three primitives:

| Knob | Where it lives | What it does |
|------|----------------|--------------|
| `updatedInput` | Allow return | Mutates the tool input before execution — the agent does not see the change, only the result |
| `updatedPermissions` | Allow return | Echoes one or more `PermissionUpdate` entries from `context.suggestions` back so matching calls skip the prompt next time |
| `message` | Deny return | Free-text reason returned to the model; Claude reads it and adapts its plan |

A fourth path — sending an entirely new instruction over [streaming input](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode) — sits outside the callback and produces the sixth shape.

## The Six Shapes

### 1. Approve

Return the input unchanged. The tool executes exactly as the model proposed.

```python
return PermissionResultAllow(updated_input=input_data)
```

The baseline shape. Use it when the proposed action is correct and you accept it as-is ([Claude Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests)).

### 2. Approve with Changes

Mutate `updated_input` before returning allow. The tool runs against the new input; the model is not told the user changed anything — it only sees the (changed) tool result.

The SDK doc's example sandboxes a Bash command's path silently:

```python
async def can_use_tool(tool_name, input_data, context):
    if tool_name == "Bash":
        sandboxed_input = {**input_data}
        sandboxed_input["command"] = input_data["command"].replace(
            "/tmp", "/tmp/sandbox"
        )
        return PermissionResultAllow(updated_input=sandboxed_input)
    return PermissionResultAllow(updated_input=input_data)
```

Useful for scoping access, sanitising parameters, or adding constraints the prompt forgot ([Claude Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests)).

### 3. Approve and Remember

The third callback argument carries a `suggestions` array — ready-made `PermissionUpdate` entries the SDK pre-computed for this call. Echo one back in `updated_permissions` and the rule persists; matching calls skip the prompt next time. A suggestion with `destination: "localSettings"` writes to `.claude/settings.local.json` so future sessions also skip the prompt ([Claude Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests); requires `claude-agent-sdk` 0.1.80+).

```python
if choice == "always":
    persist = [s for s in context.suggestions if s.destination == "localSettings"]
    return PermissionResultAllow(
        updated_input=input_data, updated_permissions=persist
    )
```

The user is *not* writing the permission rule freehand — the SDK proposes a candidate and the UI binds it to a button. That constraint keeps the persisted rule scoped to the call the user actually saw.

### 4. Reject

Return deny with a message explaining why. The model receives the message and may try a different approach ([Claude Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests)).

```python
return PermissionResultDeny(message="User rejected this action")
```

The minimum deny. Use it when no follow-up direction is appropriate.

### 5. Suggest Alternative

Structurally identical to reject — same `PermissionResultDeny` return — but the `message` carries steering text the model reads as guidance. The SDK doc gives an `rm`-to-archive example:

```python
if tool_name == "Bash" and "rm" in input_data.get("command", ""):
    return PermissionResultDeny(
        message="User doesn't want to delete files. They asked if you could compress them into an archive instead."
    )
```

The model adapts on its own — no new turn from the user is required ([Claude Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests)). This shape teaches the model in a way that "approve with changes" does not: the model sees the correction text, learns the constraint, and is more likely to apply it on subsequent calls in the same session.

### 6. Redirect Entirely

The only shape that exits the callback frame. Instead of returning allow or deny, the harness sends a new instruction over [streaming input](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode), cancelling the pending tool request and giving Claude entirely new direction ([Claude Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests)).

Reserve it for *broad* course-correction, not single-call adjustment. The five callback shapes resolve a tool request; redirect throws the request away.

## Why It Works

The approval prompt is the **highest-context moment** in the agent loop for the human: the agent has stated intent, the proposed action is visible with its full input, and the user already has the cognitive context loaded. Reducing this moment to allow/deny throws away the user's ability to apply small corrections — a path fix, a scope narrow, an alternative direction — at the only point in the loop where they are cheap.

Treating the six as a taxonomy — rather than as a stack of independent features — clarifies which shape an operator should reach for in which condition. Because each shape is a composition of the three primitives above and not a new feature, the harness only has to surface the right UI; the protocol does not need to change.

The Claude Code hooks protocol mirrors the same shape under different field names: `PreToolUse` returns `permissionDecision: allow | deny | ask | defer` and `PermissionRequest` returns `decision.behavior: allow | deny` with `updatedInput` ([Claude Code hooks](https://code.claude.com/docs/en/hooks)). The mechanism transfers across surfaces.

## When This Backfires

Richer prompts are not the same as better approval. The taxonomy adds value only when the prompt rate is already low enough that a thoughtful per-call decision is realistic.

- **High-volume prompt streams.** When the user is approving dozens of prompts per task, six buttons amplify fatigue rather than mitigating it. Anthropic notes: *"Constantly clicking 'approve' slows down development cycles and can lead to 'approval fatigue', where users might not pay close attention to what they're approving, and in turn making development less safe"* ([Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)). The first defence is reducing prompts via sandboxes and allowlists — Anthropic reports an 84% reduction ([Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)) — not enriching the surviving prompts.
- **Headless or non-interactive runs.** None of the six shapes apply when there is no human at the surface. The [Deferred Permission Pattern](deferred-permission-pattern.md) is the right primitive — pause the session, hand the pending call to the caller, resume after out-of-band approval.
- **Approve-with-changes when the agent should adapt.** Silently mutating the input hides the correction from the model. The same wrong input reappears on the next call. When the agent should learn from the correction, "suggest alternative" (shape 5) carries the teaching signal that shape 2 deliberately suppresses.
- **Approve-and-remember on a sample of one.** Persisting a permission rule from a single observed call is how blanket allowlists get over-broad. The user is in the worst position to write a precise rule mid-flow. The SDK mitigates this by pre-computing rule candidates in `context.suggestions` — relying on the freeform-rule path defeats the safeguard. [Bootstrap Evidence-Based Allowlist](../agent-readiness/bootstrap-evidence-based-allowlist.md) is the steady-state pattern for promoting rules after N successful manual approvals.
- **Redirect-entirely as a habit.** Repeated redirects without a corrective signal mask underlying instruction-following problems. The model learns nothing about why its plan was wrong. Use redirect for genuine course-correction, not as a substitute for a clearer system prompt.
- **Smoother is not better.** [Tool Confirmation Carousel](tool-confirmation-carousel.md) notes the same trap at the UI level: a cleaner approval surface can lower review quality if the user starts dispatching the queue reflexively. The taxonomy makes the *shapes* available; the harness still has to make the *moment of review* worth the user's attention.

## Example

Below is a single `canUseTool` callback that surfaces all five in-callback shapes through a multi-choice UI prompt (the sixth — redirect — happens outside the callback, via streaming input).

```python
async def can_use_tool(tool_name, input_data, context):
    choice = await ask_user(
        f"Allow {tool_name}?",
        ["approve", "approve-with-changes", "approve-always", "reject", "suggest"]
    )

    if choice == "approve":
        # Shape 1
        return PermissionResultAllow(updated_input=input_data)

    if choice == "approve-with-changes":
        # Shape 2 — mutate input silently (see shape 2 above for a concrete sandbox)
        return PermissionResultAllow(updated_input=sanitise(input_data))

    if choice == "approve-always":
        # Shape 3 — echo back the pre-computed local-settings rule
        persist = [s for s in context.suggestions if s.destination == "localSettings"]
        return PermissionResultAllow(
            updated_input=input_data, updated_permissions=persist
        )

    if choice == "suggest":
        # Shape 5 — deny with steering text the model reads as guidance
        return PermissionResultDeny(
            message="User prefers archiving over deletion. Compress these files into an archive instead."
        )

    # Shape 4 — plain reject
    return PermissionResultDeny(message="User rejected this action")
```

The same five branches map onto Claude Code hooks via `permissionDecision` and `updatedInput` ([Claude Code hooks](https://code.claude.com/docs/en/hooks)).

## Key Takeaways

- The six shapes are compositions of three SDK primitives (`updatedInput`, `updatedPermissions`, deny `message`) plus one out-of-callback path (streaming input) — not six independent features.
- "Approve with changes" hides the correction from the model; "suggest alternative" surfaces it. Pick deliberately based on whether the model should learn.
- "Approve and remember" should only persist a pre-computed `PermissionUpdate` from `context.suggestions` — never a freeform user-written rule.
- Richer prompts do not fix approval fatigue. Reduce the prompt rate first ([Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)); then surface the right shapes on what remains.
- Headless flows route to [Deferred Permission Pattern](deferred-permission-pattern.md), not to the six shapes. The taxonomy assumes a human is at the prompt.

## Related

- [Deferred Permission Pattern](deferred-permission-pattern.md) — pause a headless session at a tool call and resume after out-of-band approval; the right primitive when no human is at the surface
- [Tool Confirmation Carousel](tool-confirmation-carousel.md) — a UI surface for the residual prompts the six shapes have to land on, and the same approval-fatigue trap surfaced at the UI level
- [Classifier-Gated Auto-Permission](classifier-gated-auto-permission.md) — a different shape entirely; classify silently and only surface the prompt on escalations, reducing the per-prompt budget
- [Permission Framework Choice Outweighs Model Choice](../security/permission-framework-over-model.md) — the framework (ask-to-continue vs permissive) dominates the model choice; the six shapes only matter inside the ask-to-continue arm
- [Interactive Clarification for Underspecified Tasks](interactive-clarification-underspecified-tasks.md) — the `AskUserQuestion` path, which uses the same `canUseTool` callback but for clarifying questions rather than tool approval
