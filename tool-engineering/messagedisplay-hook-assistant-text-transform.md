---
title: "MessageDisplay Hook: Transforming Assistant Text at the Display Boundary"
description: "MessageDisplay fires on every outbound assistant message and lets a hook rewrite or hide the text before the user or downstream system sees it — the display-side analogue of PostToolUse output replacement."
tags:
  - tool-engineering
  - instructions
  - claude
aliases:
  - assistant text transformation hook
  - outbound message hook
last_reviewed: 2026-05-27
---

# MessageDisplay Hook: Transforming Assistant Text at the Display Boundary

> `MessageDisplay` fires on every outbound assistant message and lets a hook transform or hide the text before display.

## What Changed

Claude Code v2.1.152 ([2026-05-27](https://code.claude.com/docs/en/changelog)) added the `MessageDisplay` hook event. The changelog entry verbatim:

> Added a `MessageDisplay` hook event that lets hooks transform or hide assistant message text as it is displayed ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

The event sits on the outbound text path — between the model emitting a message and the harness rendering it to the terminal, IDE pane, or downstream consumer. Use this page only when the goal is to interpose on what the **user** sees; to interpose on what the **model** sees from a tool call, use [`updatedToolOutput` on `PostToolUse`](posttooluse-output-replacement.md) instead.

At time of writing, the [hooks reference](https://code.claude.com/docs/en/hooks) does not yet document the `MessageDisplay` payload schema or return shape; consult it once it lands for field-level detail.

## Where It Sits in the Lifecycle

`MessageDisplay` is the symmetric primitive to `PostToolUse` output replacement. The same harness-owned rewrite boundary, applied to a different channel:

| Hook | Channel | Reader |
|------|---------|--------|
| `UserPromptSubmit` | Inbound user text | Model |
| `PostToolUse` (`updatedToolOutput`) | Inbound tool output | Model |
| `MessageDisplay` | Outbound assistant text | User / downstream |
| `PreToolUse` | Outbound tool call | External system |

`PreToolUse` and `PostToolUse` gate or rewrite tool invocations and their results; `UserPromptSubmit` sees inbound user text before it reaches the model; `MessageDisplay` is the missing fourth corner — outbound text — that previously had no harness-side enforcement surface ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)).

## Practitioner Use Cases

Four use cases motivate dedicated `MessageDisplay` handling rather than prompt-side instruction:

- **PII redaction on user-visible output.** A regex or named-entity classifier strips emails, phone numbers, or internal hostnames before the terminal renders the message. Distinct from upstream redaction of tool output ([PII Tokenization in Agent Context](../security/pii-tokenization-in-agent-context.md)); this is the last-mile guard for what reaches a screen-share viewer or shared transcript.
- **Citation insertion.** A hook appends inline citations to claims based on a per-session sources file. Citations the model forgot to include get added at the boundary instead of relying on the model to remember.
- **Banner injection on long-running tasks.** Prepend a "agent is operating in autonomous mode" banner so a downstream operator UI cannot miss the context.
- **Audit-trail capture of every model utterance.** A side-effect hook (returning the original text unchanged) writes the message to an append-only log; the action is the *capture*, not the transformation.

For all four, prompt-side instruction is probabilistic and reverts under pressure across multi-turn sessions. Hook enforcement is deterministic because the harness — not the model — runs it ([Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)).

## Why It Works

The harness — not the model — owns the display boundary. The model decides what to say; the harness decides what to show. Moving redaction, citation insertion, and audit capture *after* generation guarantees the transformation runs regardless of what the model chose. This is the same deterministic property that makes `PreToolUse` and `PostToolUse` load-bearing enforcement points: *"Hooks are user-defined shell commands that execute at specific points in Claude Code's lifecycle. They provide deterministic control over Claude Code's behavior, ensuring certain actions always happen rather than relying on the LLM to choose to run them"* ([Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)).

Prompt-side guidance shapes generation but cannot guarantee output shape. Hook enforcement runs after the model decided, which is why the rewrite primitive belongs on the harness — not in CLAUDE.md or system prompts.

## When This Backfires

- **Audit-trail divergence.** A hook that rewrites or hides text creates an invisible disagreement between what the agent said and what the user saw. Without dual logging (pre-transform plus post-transform), incident review cannot reconstruct the actual model utterance. This is the same failure mode covered in [PostToolUse Output Replacement § Audit-vs-context divergence](posttooluse-output-replacement.md), mirrored to the display boundary — the transcript must capture both versions, not just one.
- **False sense of PII safety.** Display-side redaction does not prevent the model from reasoning over the secret — the secret already entered context. A user-facing redaction hook reduces *display* exposure but does not close the leak path through subsequent tool calls or chained sessions. For true PII safety the redaction must happen upstream (via [`PostToolUse` output replacement](posttooluse-output-replacement.md) on tool output, or by not putting the data in context at all). `MessageDisplay` is the last-mile guard, not the primary control.
- **Hook latency on every assistant turn.** Unlike `PreToolUse`/`PostToolUse` which fire per tool call, `MessageDisplay` fires on every assistant message. A 200 ms hook becomes 200 ms of perceived latency on every turn. Heavy hooks (classifier-based PII detectors, LLM-graded filters) that are tolerable on `PostToolUse` become user-visible drag here. Keep the hot path to regex or string substitution; defer slow classifiers to `PostToolUse` upstream of generation.
- **Race with downstream consumers.** When the displayed text drives multiple downstream systems (a transcript stored to a separate audit DB, a Slack relay, a screen-share viewer), a `MessageDisplay` hook that mutates text *after* one consumer has already read it produces consumer-specific views. If multiple `MessageDisplay` hooks are registered, the [hooks reference](https://code.claude.com/docs/en/hooks) follows the same pattern as `PreToolUse` `updatedInput` and `PostToolUse` `updatedToolOutput` — concurrent rewrites do not have a documented deterministic merge order. Register at most one rewriting hook per matcher.
- **Stable changelog claim, unstable payload.** At time of writing, the [hooks reference](https://code.claude.com/docs/en/hooks) does not yet document the `MessageDisplay` payload schema or return shape. Hooks authored against an inferred schema may break when the docs land. Pin the hook's expected fields by reading the reference at the version you ship; treat any code in this page as a sketch, not a spec.

## Key Takeaways

- `MessageDisplay` was added in Claude Code v2.1.152 (2026-05-27) and lets hooks transform or hide assistant message text before display ([changelog](https://code.claude.com/docs/en/changelog)).
- It is the display-side analogue of [`PostToolUse` output replacement](posttooluse-output-replacement.md) — same harness-boundary rewrite pattern, different channel.
- Useful for PII redaction at the screen, citation insertion, banner injection, and audit capture — anywhere prompt-side instruction is probabilistic.
- A redaction hook here does not close upstream leak paths; the secret already entered context. Pair with `PostToolUse` redaction for true safety.
- Hooks fire on every assistant message, so latency is user-visible. Keep transforms cheap; defer classifiers to upstream events.
- The payload schema is not yet in the [hooks reference](https://code.claude.com/docs/en/hooks) — consult the reference at the version you ship.

## Related

- [PostToolUse Output Replacement: Hooks That Rewrite Tool Results](posttooluse-output-replacement.md)
- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
- [Hook Catalog](hook-catalog.md)
- [Claude Code Hooks](../tools/claude/hooks-lifecycle.md)
- [PII Tokenization in Agent Context](../security/pii-tokenization-in-agent-context.md)
