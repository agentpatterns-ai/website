---
title: "Host-Controlled Backgrounding for Claude Subagent Calls"
term: "Host-Controlled Subagent Backgrounding"
description: "Check the host, nesting depth, and fork mode before choosing a subagent join strategy. Claude Code uses different defaults for interactive and headless runs."
tags:
  - multi-agent
  - agent-design
  - claude
applies_to: "claude-code@2.1.318"
last_reviewed: 2026-11-06
status: current
maturity: emerging
---

# Host-Controlled Backgrounding for Claude Subagent Calls

> Host-controlled backgrounding sets how Claude subagent calls return, with different rules for interactive sessions and nested headless work.

Host-controlled backgrounding makes dispatch mode part of the runtime configuration. Claude Code 2.1.302 made desktop and VS Code main-conversation subagents run in the background, matching the terminal. Nested calls in those hosts, `claude -p`, and the Agent SDK defaulted to foreground execution ([release notes](https://code.claude.com/docs/en/changelog#2-1-302)).

## Check the host and depth

The current [subagent reference](https://code.claude.com/docs/en/sub-agents#which-subagents-run-in-the-background) distinguishes these cases:

| Call site | Behavior |
|---|---|
| Main conversation in terminal, VS Code, or desktop | Background by default; fork mode prevents waiting |
| Main conversation in `claude -p` or Agent SDK | Background default, but Claude can choose to wait |
| Nested headless call with fork mode enabled | Spawning subagent waits |
| Nested headless call with fork mode disabled | Background; a child that outlasts its parent reports to the main conversation |

The nested rules come from the [nesting reference](https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents). A skill with `context: fork` follows separate skill rules. Fork mode controls availability of the fork type; it does not make every worker inherit the conversation.

## Choose a completion contract

Treat these rules as inputs to orchestration design. Record the host and fork setting beside the task contract. Identify which caller must receive each result before dependent work starts. A fixed dispatch mode does not establish a fixed completion time.

For interactive waiting, the documented procedure disables fork mode, starts a new session, and asks Claude to wait. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` also forces waiting, but disables background shell commands too ([waiting configuration](https://code.claude.com/docs/en/sub-agents#let-claude-wait-for-a-subagent)).

Separate dispatch configuration from throughput claims. Anthropic's research system used synchronous execution because asynchronous execution complicates result coordination, state consistency, and error propagation ([engineering report](https://www.anthropic.com/engineering/multi-agent-research-system)). Choose background work when the caller has useful independent work; define a join before consuming its output.

## Key Takeaways

- Record host and fork settings in a reproducible orchestration test.
- Test the nested headless case separately from the main-conversation case.
- Require completed results before dependent work, even when dispatch returns immediately.

## Related

- [Async Non-Blocking Subagent Dispatch](async-non-blocking-subagent-dispatch.md) — work the orchestrator can do while results are pending
- [Forked vs Fresh Subagents](forked-vs-fresh-subagents.md) — the separate context-inheritance choice
- [Agent Handoff Protocols](agent-handoff-protocols.md) — define the returned artifact
