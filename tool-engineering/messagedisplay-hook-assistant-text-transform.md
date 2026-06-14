---
title: "MessageDisplay Hook: Transforming Assistant Text at the Display Boundary"
term: "MessageDisplay Hook"
description: "MessageDisplay fires on every outbound assistant message and lets a hook rewrite or hide the text before the user or downstream system sees it — the display-side analogue of PostToolUse output replacement."
tags:
  - tool-engineering
  - instructions
  - claude
aliases:
  - assistant text transformation hook
  - outbound message hook
last_reviewed: 2026-06-03
maturity: established
---

# MessageDisplay Hook: Transforming Assistant Text at the Display Boundary

> `MessageDisplay` fires on every outbound assistant message and lets a hook transform or hide the text before display.

## What Changed

Claude Code v2.1.152 ([2026-05-27](https://code.claude.com/docs/en/changelog)) added the `MessageDisplay` hook event. The changelog entry verbatim:

> Added a `MessageDisplay` hook event that lets hooks transform or hide assistant message text as it is displayed ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).

The event sits on the outbound text path — between the model emitting a message and the harness rendering it to the terminal, IDE pane, or downstream consumer. Use this page only when the goal is to interpose on what the **user** sees; to interpose on what the **model** sees from a tool call, use [`updatedToolOutput` on `PostToolUse`](posttooluse-output-replacement.md) instead.

The [hooks reference](https://code.claude.com/docs/en/hooks) documents the return shape: a hook sets `hookSpecificOutput.displayContent` to replace the on-screen text. The replacement is **display-only** — *"the transcript and what Claude sees keep the original text"* ([hooks reference](https://code.claude.com/docs/en/hooks)). The event has no matcher support and always fires on every assistant message that streams text.

## Where It Sits in the Lifecycle

`MessageDisplay` is the symmetric primitive to `PostToolUse` output replacement — the same harness-owned rewrite boundary on a different channel. It is the missing fourth corner, outbound assistant text, that previously had no harness-side enforcement surface ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)):

| Hook | Channel | Reader |
|------|---------|--------|
| `UserPromptSubmit` | Inbound user text | Model |
| `PostToolUse` (`updatedToolOutput`) | Inbound tool output | Model |
| `MessageDisplay` | Outbound assistant text | User / downstream |
| `PreToolUse` | Outbound tool call | External system |

## Practitioner Use Cases

Four use cases motivate dedicated `MessageDisplay` handling rather than probabilistic prompt-side instruction:

- **PII redaction at the screen.** A regex or named-entity classifier strips emails, phone numbers, or internal hostnames before render — the last-mile guard for a screen-share viewer or shared transcript, distinct from upstream tool-output redaction ([PII Tokenization in Agent Context](../security/pii-tokenization-in-agent-context.md)).
- **Citation insertion.** A hook appends inline citations the model forgot, sourced from a per-session sources file, at the boundary rather than relying on recall.
- **Banner injection.** Prepend an "operating in autonomous mode" banner so a downstream operator UI cannot miss the context.
- **Audit-trail capture.** A side-effect hook returns the text unchanged and writes it to an append-only log; the action is *capture*, not transform.

## Why It Works

The harness — not the model — owns the display boundary: the model decides what to say, the harness decides what to show. Moving redaction, citation insertion, and audit capture *after* generation guarantees the transformation runs regardless of what the model chose. This is the deterministic property that makes hooks "ensure certain actions always happen rather than relying on the LLM to choose to run them" ([Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)). Prompt-side guidance shapes generation but cannot guarantee output shape, which is why the rewrite primitive belongs on the harness — not in CLAUDE.md or system prompts.

## When This Backfires

- **Display/consumer divergence.** The replacement is display-only — the transcript and what Claude sees keep the original text ([hooks reference](https://code.claude.com/docs/en/hooks)), so the utterance is never lost and verbose mode shows the original. The divergence that survives is between the transcript and any *downstream consumer* reading the rendered text (a screen-share viewer, a Slack relay). Unlike [PostToolUse output replacement](posttooluse-output-replacement.md), `MessageDisplay` cannot corrupt the canonical record; log the rendered view separately only if a consumer needs it.
- **False sense of PII safety.** Display-side redaction does not stop the model reasoning over the secret — it already entered context — and does not close the leak path through later tool calls or chained sessions. For true safety, redact upstream (via [`PostToolUse` output replacement](posttooluse-output-replacement.md), or by keeping the data out of context). `MessageDisplay` is the last-mile guard, not the primary control.
- **Hook latency on every assistant turn.** `MessageDisplay` fires on every assistant message, not per tool call, so a 200 ms hook adds 200 ms of perceived latency every turn. Heavy classifier- or LLM-graded filters that are tolerable on `PostToolUse` become user-visible drag here. Keep the hot path to regex or string substitution; defer slow classifiers upstream.
- **Undefined merge order across hooks.** `MessageDisplay` has no matcher support, so every registered hook fires on every message. The [hooks reference](https://code.claude.com/docs/en/hooks) says matching hooks "run in parallel" but documents no merge order for competing `displayContent` values — two rewriting hooks have no defined resolution. Register at most one rewriting hook; reserve the rest for side-effect-only capture.

## Key Takeaways

- `MessageDisplay` was added in Claude Code v2.1.152 (2026-05-27) and lets hooks transform or hide assistant message text before display ([changelog](https://code.claude.com/docs/en/changelog)).
- It is the display-side analogue of [`PostToolUse` output replacement](posttooluse-output-replacement.md) — same harness-boundary rewrite pattern, different channel.
- Useful for PII redaction at the screen, citation insertion, banner injection, and audit capture — anywhere prompt-side instruction is probabilistic.
- A redaction hook here does not close upstream leak paths; the secret already entered context. Pair with `PostToolUse` redaction for true safety.
- Hooks fire on every assistant message, so latency is user-visible. Keep transforms cheap; defer classifiers to upstream events.
- The rewrite is display-only: the transcript and what Claude sees keep the original text ([hooks reference](https://code.claude.com/docs/en/hooks)), so it cannot corrupt the canonical record.

## Related

- [PostToolUse Output Replacement: Hooks That Rewrite Tool Results](posttooluse-output-replacement.md)
- [Hooks and Lifecycle Events](hooks-lifecycle-events.md)
- [Hook Catalog](hook-catalog.md)
- [Claude Code Hooks](../tools/claude/hooks-lifecycle.md)
- [PII Tokenization in Agent Context](../security/pii-tokenization-in-agent-context.md)
