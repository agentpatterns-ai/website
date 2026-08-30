---
title: "Forked vs Fresh Subagents: When to Inherit the Parent Conversation"
term: "Forked vs Fresh Subagents"
description: "Subagents either fork from the parent's full conversation or start fresh with a brief — the choice trades cache reuse and mental-model fidelity against bias and prompt-injection containment."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - fork vs fresh subagent
  - subagent context inheritance
  - forked subagent
last_reviewed: 2026-08-18
maturity: emerging
---

# Forked vs Fresh Subagents: When to Inherit the Parent Conversation

> Fork when the parent's mental model is an asset; start fresh when bias, trifecta exposure, or token budget makes inherited context a liability.

Learn it hands-on with the [Forked vs Fresh Subagents guided lesson](https://learn.agentpatterns.ai/multi-agent/forked-vs-fresh/), which includes quizzes.

A forked subagent inherits the parent's entire system prompt, tools, and message history; a fresh subagent starts with only the task brief the orchestrator constructs. Claude Code first exposed the choice through `CLAUDE_CODE_FORK_SUBAGENT=1` and `/fork`, available since v2.1.117 ([Claude docs](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation)). Since v2.1.232 fork *mode* is on by default in interactive sessions and stays off by default under `-p` and in the Agent SDK ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-232), [Claude docs](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation)). Mode on means the option is available without the variable or `/fork`: a spawn is a fork only when it asks for `subagent_type: "fork"`, and that fork then inherits the full conversation and prompt cache. The same axis exists implicitly in every harness that spawns child agents — and the choice is per-task, not global: one orchestrator can fork for one delegation and start fresh for the next.

## The decision

| Spawn fresh when | Spawn a fork when |
|---|---|
| The subagent needs to question a parent decision (code review, security audit, adversarial test) | The subagent needs to extend a parent decision (design variation, continuation, mid-stream draft) |
| The parent has touched untrusted content (web fetches, MCP server output) and the child has egress | The parent's reasoning is load-bearing and a brief would be lossy |
| The task is one-off — no parallel siblings to amortize cache warmup | Two or more siblings will run from the same starting point |
| The child must reset bias to disagree with the parent | The child must preserve the parent's nuance to agree intelligently |

## Why it works

A fork's first request shares the parent's prefix exactly — same system prompt, same tool definitions, same message history. The Claude API prompt cache matches on exact prefix, so the fork reads from cached tokens and bills only the appended fork directive. From the [Claude Code prompt-caching docs](https://code.claude.com/docs/en/prompt-caching#subagents-and-the-cache): "A fork ... inherits the parent's system prompt, tools, and conversation history exactly, so its first request reads the parent's cache." Cache reads bill at roughly 10% of the standard input rate ([same page](https://code.claude.com/docs/en/prompt-caching#check-cache-performance)).

A fresh named subagent has a different system prompt and tool set, so its prefix does not match the parent's cache. Its first call has no cache hits and it warms its own (5-minute TTL) cache from scratch ([Claude docs](https://code.claude.com/docs/en/prompt-caching#subagents-and-the-cache)).

The mechanism has a downside too. Forks are cheap because they carry the parent's entire input distribution. That is also why they inherit its biases, blind spots, and accumulated tool results. Fresh subagents reset that distribution, which makes them useful for adversarial work.

## When this backfires

Forking a code review or audit. The fork remembers why every decision was made, so confirmation bias rubber-stamps the work. A direct test reported in [Mejba Ahmed's field write-up](https://www.mejba.me/blog/forked-subagents-claude-code-anthropic): a forked subagent reviewing authentication code returned cosmetic suggestions; a fresh subagent on the same code flagged a missing constant-time token comparison — a real security bug. Anthropic's own design rationale for making forking opt-in cites the same concern: "Clean slate is sometimes better. For example, a code review agent probably benefits from fresh perspective without anchoring bias from the conversation" ([claude-code#16153](https://github.com/anthropics/claude-code/issues/16153)).

Forking a single small task. Cache warmup is real on the first fork after a heavy parent. A one-off fork on a 180k-token parent pays the cache-write tax without parallel siblings to amortize against. Forks earn their keep when batched.

Forking a trifecta-sensitive child. A fork pulls in every accumulated tool result, including web fetches and MCP output. The [Claude docs](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation) call this out directly: a fork "drops the input isolation that subagents otherwise provide." If the parent has any [lethal-trifecta](../../security/lethal-trifecta-threat-model.md) exposure, the fork inherits the injection surface. Fresh containment — only what the orchestrator chose to pass — is still the safer choice for any child that can act. Fork mode being on does not erode that by itself, because a fork still has to be asked for; to remove the option in a session that handles untrusted content, deny the type with an `Agent(fork)` rule or set `CLAUDE_CODE_FORK_SUBAGENT=0`.

Forking past the [context cliff](../../context-engineering/context-window-dumb-zone.md). Forks copy the entire parent window, so a parent already past the degradation threshold hands the fork a degraded baseline. Forking propagates session bloat rather than solving it.

Forking when the task must challenge prior decisions. Counterfactual exploration breaks when the explorer remembers why each option was rejected. Fresh context is the lever that lets a subagent disagree.

## Side effects of fork mode

Turning fork mode on changes two things, and only one of them is about forks ([Claude docs](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation)):

- Claude gains the `fork` subagent type. Untyped spawns still get the general-purpose subagent, and subagents spawned from a definition such as Explore work as usual — so fresh remains what you get unless a fork is requested.
- Spawns run in the background, forks and non-forks alike, apart from the documented foreground cases. Claude Code removes the Agent tool's `run_in_background` parameter, so Claude cannot ask for the foreground; `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` keeps spawns synchronous.

Before v2.1.232 the mode required `CLAUDE_CODE_FORK_SUBAGENT=1` in every session. Now `1` extends the default to non-interactive mode and the SDK, and `0` turns it off everywhere. The `/fork` command still works for a manual, one-off fork. A fork cannot spawn further forks ([same docs section](https://code.claude.com/docs/en/sub-agents#fork-the-current-conversation)).

## Example

A team is 140k tokens into a design-system session — color tokens, component patterns, and spacing rules are all established in the conversation. Two parallel tasks come up:

1. Generate two Kanban-card variations that fit the existing system. Fork twice. Both forks see the full design system byte-for-byte and produce variations consistent with it. A fresh subagent would receive Claude's compressed summary ("project uses Tailwind, dark theme, Inter font") and lose the specific spacing scale and shadow treatments that make variations belong together.
2. Review the authentication module the team just wrote for security issues. [Spawn fresh](sub-agents-fan-out.md). The fresh subagent has no investment in the implementation choices and can flag the constant-time-comparison gap the author missed.

Both delegations happen in the same session. The fork-vs-fresh choice is per-task, not per-session.

## Key Takeaways

- The fork/fresh axis is a per-task choice, not a global setting — fork mode on by default makes the type available, not automatic, and untyped and named spawns still start fresh.
- Forks share the parent Claude prompt cache; their first request bills at cache-read rates because the prefix matches.
- Fresh is the right default for reviews, audits, and any child that needs to disagree with the parent.
- Forks earn their keep when the parent's reasoning is load-bearing and at least two siblings will run from the same starting point.
- A fork drops input isolation — never fork a child that holds egress when the parent has touched untrusted content.

## Related

- [Sub-Agents for Fan-Out Research and Context Isolation](sub-agents-fan-out.md) — the fresh-default model that forks deliberately break.
- [Agent Handoff Protocols: Passing Work Between Agents](agent-handoff-protocols.md) — the structured-brief alternative to forking that minimizes information loss without inheriting bias.
- [Cross-Tool Subagent Comparison](cross-tool-subagent-comparison.md) — how Claude Code, Gemini CLI, and Copilot CLI differ on subagent context isolation.
- [Subagent Schema-Level Tool Filtering](subagent-schema-level-tool-filtering.md) — narrowing what a subagent can do, complementary to narrowing what it sees.
- [Async Non-Blocking Subagent Dispatch](async-non-blocking-subagent-dispatch.md) — orchestrator-side concurrency model that pairs with the fork/fresh choice on each spawn.
- [Agent as Tool vs Handoff: Who Keeps the Conversation](../agent-design/agent-as-tool-vs-handoff.md) — the control-return axis, orthogonal to the context-inheritance axis this page covers.
- [The Subagent Inheritance Contract: What Crosses Down](subagent-inheritance-contract.md) — what a fresh spawn still carries, and how Codex and Claude Code invert their defaults.
