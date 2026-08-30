---
title: "The Subagent Inheritance Contract: What Crosses Down"
term: "Subagent Inheritance Contract"
description: "A fresh subagent is never empty. Codex inherits the parent session's settings by default; Claude Code drops the conversation and injects the rule hierarchy."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - subagent inheritance
  - what crosses the subagent boundary
  - subagent brief contract
last_reviewed: 2026-08-29
maturity: emerging
---

# The Subagent Inheritance Contract: What Crosses Down

> A subagent that starts fresh still starts loaded. What crosses down unasked, and what comes back, decide what the delegation actually cost.

The subagent inheritance contract is what a harness copies from parent to delegate without being asked, plus the single thing it sends back up. Two shipped implementations now let you compare. Codex spawns each subagent in its own thread and returns findings "to the main agent for synthesis" ([Guo, From One Agent to a Team](https://towardsdatascience.com/from-one-agent-to-a-team-understanding-codex-subagents/)); Claude Code gives each one "a fresh, isolated context window" and returns a summary ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)). They agree on the return path and invert their defaults on the way down.

## When the isolation argument holds

Delegate when the parent's attention is the binding constraint, the subtasks share no constraint you would restate in each brief, and enough turns remain for the isolation to pay back.

Outside those conditions the roster loses. Under one normalized execution and logging protocol, "at most one of six tested MAS exceeds the matched single-agent anchor on benchmark-balanced average accuracy", and the remaining five "trail by 2.56-11.29 points" ([Fu et al., Do More Agents Help?, arXiv 2606.05670v1](https://arxiv.org/abs/2606.05670v1)).

## What each harness hands down

| Crosses down | Codex | Claude Code |
|---|---|---|
| Model, tools, web search | Inherited from the main session when the agent file does not override them | Declared per agent file, and absent from the six items the docs list as crossing down |
| Conversation so far | Not part of the documented walkthrough | Dropped, unless the spawn asks for a fork |
| Project rules | `AGENTS.md` or a skill file can request delegation | "every level of the CLAUDE.md hierarchy the main conversation loads" |
| Injected without asking | Not documented | Full text of every skill named in `skills:`, plus a git-status snapshot and a sibling roster, each of which the docs gate on its own condition |

Sources: [Codex subagents walkthrough](https://towardsdatascience.com/from-one-agent-to-a-team-understanding-codex-subagents/), [Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents).

The Codex article states the inheritance rule plainly: "If we do not override those settings here, the three specialists will inherit them from the main Codex session." Claude Code inverts it. Its delegate "doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read", and still arrives loaded with the rest. Neither default is wrong. Both stay invisible until a delegate acts on something you never wrote in the brief, or fails on something you assumed it had.

## Why it works

Isolation saves the parent because the delegate's intermediate work never enters the parent's window. Claude Code states the causal step for a fork, the case that inherits most: "The fork's own tool calls still stay out of your conversation and only its final result comes back, so your main context window stays clean." A plain delegate starts from "a fresh, isolated context window" and likewise returns only its summary ([Claude Code sub-agents](https://code.claude.com/docs/en/sub-agents)). Codex reaches the same place at thread granularity: each subagent "works in its own thread" and only its findings return.

The saving is the delegate's tool trace, not its answer, so a delegate returning a 2,000-word report has spent most of what the isolation bought. The same accounting prices a thin brief. Measured across 724 takeover runs per model, handoffs that carried context cut cumulative prompt tokens by 42 to 63 percent against a repository-state-only takeover, while "Solved-rate effects are smaller and model-dependent" ([KC and Budathoki, Handoff Debt, arXiv 2606.02875v1](https://arxiv.org/abs/2606.02875v1)). A good brief buys efficiency. It does not reliably buy correctness.

## When this backfires

- The subtasks share a constraint that stayed in the parent's head. "Inter-agent misalignment" is one of the three categories holding the 14 failure modes in a taxonomy built from 1600+ annotated traces across 7 frameworks ([Cemri et al., Why Do Multi-Agent LLM Systems Fail?, arXiv 2503.13657v3](https://arxiv.org/abs/2503.13657v3)).
- The session is nearly over. Isolation is paid on the way down and recovered over the parent's remaining turns, so delegating near the end leaves nothing to recover it against.
- Concurrency is capped below your fan-out. The Codex walkthrough runs with `max_concurrent_threads_per_session = 3`, so a six-way split serializes while every handoff cost stays.
- The delegate needed what you dropped. Claude Code's fresh delegate cannot see files the parent already read, and rediscovers them at your expense.
- The roster grew faster than the work. Past the 15,000-token description warning you pay context rent on specialists that may never be dispatched.

## Example

Two config surfaces decide most of the contract, and neither one lives in the brief. On the Codex side it is the agent's own TOML file under `.codex/agents/`: every setting you leave out there resolves to the main session's value. On the Claude Code side it is the `skills:` field, because whatever you name reaches the delegate as full text ahead of the brief.

Write the brief as though nothing carries, then delete the lines the table above says are already there. That order catches the omission. The reverse order catches nothing, because an assumption about inheritance never announces itself.

## Key Takeaways

- Ask what the harness injects before you tune what you write. On both implementations the unasked payload is larger than the brief.
- Codex inherits the parent session's settings by default and Claude Code does not, so a mental model built on one tool mispredicts the other.
- The isolation buys you the delegate's tool trace. A verbose return value spends it.
- If you cannot name what the delegate will arrive carrying, you are not ready to write its brief.

## Related

- [Forked vs Fresh Subagents](forked-vs-fresh-subagents.md) — the per-task choice of whether the conversation crosses down at all.
- [Cross-Tool Subagent Comparison](cross-tool-subagent-comparison.md) — definition format, recursion depth, and tool scoping across Claude Code, Gemini CLI, and Copilot CLI.
- [The Orchestrator's Attention Budget](../agent-design/orchestrator-attention-budget.md) — why to delegate at all, priced in attention rather than time.
- [Agent Handoff Protocols](agent-handoff-protocols.md) — the structured form of what crosses a boundary between agents.
- [Static Roster vs Runtime Subagent Definition](static-roster-vs-runtime-subagent-definition.md) — who fixes a delegate's identity, and when.
