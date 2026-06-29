---
title: "Six-Shape Approval Response Taxonomy: Beyond Binary Allow/Deny"
term: "Six-Shape Approval Response Taxonomy"
description: "The Claude Agent SDK exposes six distinct responses to a tool-approval prompt — approve, approve with changes, approve and remember, reject, suggest alternative, redirect entirely — composed from three callback knobs."
tags:
  - agent-design
  - tool-agnostic
  - long-form
aliases:
  - approval response taxonomy
  - tool approval response shapes
  - canUseTool response taxonomy
last_reviewed: 2026-06-12
maturity: adopted
---

# Six-Shape Approval Response Taxonomy

> Six distinct approval responses — approve, approve-with-changes, approve-and-remember, reject, suggest alternative, redirect entirely — compose from three callback knobs over a binary protocol.

The underlying protocol is binary: a `canUseTool` callback returns either `PermissionResultAllow(updated_input=...)` or `PermissionResultDeny(message=...)` ([Claude Agent SDK — Handle approvals and user input](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests)). Six shapes emerge when three independent knobs — input mutation, persisted permission updates, and the deny message — are treated as design surfaces. The Agent SDK doc enumerates the six verbatim.

## The three underlying knobs

Every shape is a permutation of these three primitives:

| Knob | Where it lives | What it does |
|------|----------------|--------------|
| `updatedInput` | Allow return | Mutates the tool input; the agent sees only the result |
| `updatedPermissions` | Allow return | Echoes `context.suggestions` entries so matching calls skip the prompt |
| `message` | Deny return | Free-text reason the model reads and adapts to |

A fourth path — a new instruction over [streaming input](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode) — sits outside the callback and produces the sixth shape.

## The six shapes

All citations below point to the [Claude Agent SDK docs](https://code.claude.com/docs/en/agent-sdk/user-input#respond-to-tool-requests).

### 1. Approve

Return the input unchanged; the tool executes as proposed. The baseline shape.

```python
return PermissionResultAllow(updated_input=input_data)
```

### 2. Approve with changes

Mutate `updated_input` before returning allow. The model is not told it changed — it sees only the result. This helps you scope access or sanitize parameters. The SDK doc sandboxes a Bash path silently:

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

### 3. Approve and remember

The third callback argument carries a `suggestions` array — `PermissionUpdate` entries the SDK pre-computed for this call. Echo one back in `updated_permissions` and the rule persists. A suggestion with `destination: "localSettings"` writes to `.claude/settings.local.json` so future sessions skip it (requires `claude-agent-sdk` 0.1.80+).

```python
if choice == "always":
    persist = [s for s in context.suggestions if s.destination == "localSettings"]
    return PermissionResultAllow(
        updated_input=input_data, updated_permissions=persist
    )
```

The user is not writing the rule freehand. The SDK proposes a candidate and the UI binds it to a button, so the rule stays scoped to the call the user actually saw.

### 4. Reject

Return deny with a message explaining why; the model receives it and may try another approach. The minimum deny, when no follow-up direction fits.

```python
return PermissionResultDeny(message="User rejected this action")
```

### 5. Suggest alternative

Structurally identical to reject — same `PermissionResultDeny` return — but the `message` carries steering text the model reads as guidance. The SDK doc gives an `rm`-to-archive example:

```python
if tool_name == "Bash" and "rm" in input_data.get("command", ""):
    return PermissionResultDeny(
        message="User doesn't want to delete files. They asked if you could compress them into an archive instead."
    )
```

The model adapts on its own, with no new turn required. Unlike "approve with changes," it sees the correction text and is likelier to apply it on later calls.

### 6. Redirect entirely

The only shape that exits the callback frame. Instead of returning allow or deny, the harness sends a new instruction over [streaming input](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode), canceling the pending request and giving Claude entirely new direction. Reserve it for broad course-correction: the five callback shapes resolve a tool request; redirect throws the request away.

## Why it works

The approval prompt is the highest-context moment in the agent loop for the human: intent is stated and the proposed action is visible with its full input. Reducing it to allow/deny discards the chance to apply small corrections — a path fix, a scope narrow, an alternative direction — at the one point in the loop where they are cheap.

Each shape composes the three primitives rather than adding a feature, so the harness only surfaces the right UI; the protocol never changes. The Claude Code hooks protocol mirrors the shape under different field names: `PreToolUse` returns `permissionDecision: allow | deny | ask | defer` and `PermissionRequest` returns `decision.behavior: allow | deny` with `updatedInput` ([Claude Code hooks](https://code.claude.com/docs/en/hooks)). The mechanism transfers across surfaces.

## When this backfires

Richer prompts are not better approval. The taxonomy adds value only when the prompt rate is low enough for a thoughtful per-call decision.

- High-volume prompt streams: at dozens of prompts per task, six buttons amplify fatigue rather than reducing it. Anthropic notes that "constantly clicking 'approve'... can lead to 'approval fatigue', where users might not pay close attention to what they're approving" and reports an 84% prompt reduction from sandboxes and allowlists ([Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)).
- Headless runs: none of the six apply with no human at the surface. The [Deferred Permission Pattern](deferred-permission-pattern.md) is the right primitive — pause, hand the call to the caller, resume after out-of-band approval.
- Approve-with-changes when the agent should adapt: silent mutation hides the correction, so the same wrong input reappears. "Suggest alternative" (shape 5) carries the teaching signal shape 2 suppresses.
- Approve-and-remember on a sample of one: persisting a rule from a single call is how blanket allowlists get over-broad. The SDK's pre-computed `context.suggestions` reduce this risk, so bypassing them for a freeform rule defeats the safeguard.
- Redirect-entirely as a habit: repeated redirects without a corrective signal mask instruction-following problems — the model learns nothing about why its plan was wrong.
- Smoother is not better: [Tool Confirmation Carousel](tool-confirmation-carousel.md) flags the same trap at the UI level. A cleaner surface lowers review quality if the user dispatches the queue reflexively.

## Example

A single `canUseTool` callback that surfaces all five in-callback shapes through a multi-choice UI prompt (the sixth — redirect — happens outside the callback, via streaming input).

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
