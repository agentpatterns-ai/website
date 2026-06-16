---
title: "Context-Usage Attribution: Per-Source Breakdown of Agent Context"
term: "Context-Usage Attribution"
description: "An always-on observability surface that breaks the context window into rules, skills, MCP returns, subagent transcripts, and conversation history — so operators prune the right source instead of guessing."
tags:
  - observability
  - context-engineering
  - tool-agnostic
aliases:
  - Context Usage Breakdown
  - Per-Source Context Attribution
last_reviewed: 2026-06-13
maturity: adopted
---

# Context-Usage Attribution: Per-Source Breakdown of Agent Context

> Break the context window into rules, skills, MCP returns, subagent transcripts, and conversation — so operators prune the source actually responsible, not the wrong one.

## Two Cuts of the Same Telemetry

A single *"78% of the context window"* indicator names the symptom, not the cause. Two attribution cuts close it:

- **Per-tool attribution** — which tool calls dumped the most tokens. Claude Code's [`/context` command](../context-engineering/context-window-diagnostic-tooling.md) is the developer-facing example ([Claude Code changelog](https://code.claude.com/docs/en/changelog)).
- **Per-source attribution** — which configuration source (rules, skills, MCP servers, subagents, conversation) is consuming the budget, regardless of which call put it there.

Cursor shipped per-source attribution on 2026-05-06: *"You can now see a breakdown of your agent's context usage"* ([Cursor changelog](https://cursor.com/changelog)). The categories — rules, skills, MCPs, subagents — match the units an operator can act on: unload a skill, disable an MCP server, prune a rule file, kill a subagent.

```mermaid
graph LR
    C[Context window<br/>78% full] --> T[Per-tool cut]
    C --> S[Per-source cut]
    T -->|grep dumped 8k| TR[Truncate / filter the call]
    S -->|skills 22%, MCP 31%| SR[Unload skill / disable server]
```

## Categories the Breakdown Should Expose

Each category maps to a distinct remediation surface. A breakdown that collapses two of them — *"static prompt: 36%"* — leaves the operator unable to choose between unloading a skill and pruning a rule.

| Category | Why it's separate | Remediation |
|----------|-------------------|-------------|
| Rules / instruction files | Loaded at session start, persistent | Prune CLAUDE.md / AGENTS.md against the rule budget |
| Skill definitions | Descriptions always-on; full body loads on use | Mark low-value skills `name-only` or `off` via [skill overrides](https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings) |
| MCP tool returns | Grow with each call; cumulative | Drop server, narrow tool selection, audit tool-output token cost |
| Subagent transcripts | Forwarded back to parent on completion | Tighten subagent output schema, summarise instead of forward |
| Tool outputs (non-MCP) | File reads, grep, build logs | Truncate at the call site; apply [observation masking](../context-engineering/observation-masking.md) |
| Conversation history | Compounds with turns | Compact, or split into a fresh session |
| Cache prefix | Read-only; cheap but counts against window | Stable across turns — flag only when prefix bloats |

## OTel Path: The Same Cut, Exported

Claude Code's OTel exporter ships the attributes that make per-source attribution computable from telemetry rather than UI inspection. The `claude_code.token.usage` metric carries ([Claude Code monitoring reference](https://code.claude.com/docs/en/monitoring-usage)):

- `type` — `"input"`, `"output"`, `"cacheRead"`, `"cacheCreation"`
- `query_source` — `"main"`, `"subagent"`, `"auxiliary"`, or compaction/auxiliary thread names
- `model`, `effort`, request-id correlation

Grouping by `query_source` produces the subagent-vs-main split; grouping by `type` separates active-input from cached-prefix tokens. The UI breakdown and the OTel export consume the same counts — Cursor's panel is the always-on surface, an OTel collector the post-hoc audit path. See [agent observability via OTel](agent-observability-otel.md) for export wiring.

## Action Signals

A breakdown without thresholds is just a chart. Useful signals:

- **MCP returns > 30% with rising trend** — at least one server's outputs are unbounded. Drill into per-server tool-output token cost to find the offender.
- **Skills > 20% on a session that didn't invoke them** — descriptions are too verbose; move low-priority skills to `name-only`.
- **Subagent transcripts > 15%** — handoff schemas are missing; agents forward raw transcripts.
- **Cache prefix > 50% with active < 30%** — the harness pays full attention cost on cached tokens. Confirm cache hit rate via OTel `cacheRead`.

## When the Cut Is Wrong

Per-source attribution is the right axis when configuration sources are non-trivial. It misleads when:

- **Tool calls dominate the session.** A long agentic run buckets file reads and grep output into one giant "tools"/"MCP" slice that points at no specific call. Switch to per-tool attribution ([`/context`](../context-engineering/context-window-diagnostic-tooling.md)).
- **Single-shot deterministic prompts.** No compounding, no point in attribution.
- **Tightly-pruned harnesses.** When rules, skills, and MCPs are already minimal, the breakdown reports rounding noise.
- **The harness can't act on the cut.** Without per-skill or per-MCP unload commands, knowing skills consume 22% offers no remediation path beyond restarting the session.
- **The headline counts only a subset of token types.** A breakdown is trustworthy only when it sums input, output, and cache tokens; counting input alone undercounts the budget — Claude Code's percentage showed ~20% while the session was at its limit ([claude-code#28167](https://github.com/anthropics/claude-code/issues/28167), [#17959](https://github.com/anthropics/claude-code/issues/17959)). Confirm the denominator covers every `type` before trusting a slice.

The two cuts are complementary — exposing both lets operators pick the axis matching the suspected cause. [The Infinite Context anti-pattern](../anti-patterns/infinite-context.md) is the failure both work against; per-source attribution is the cheaper always-on signal, pointing at slow-growing static sources before an emergency compaction.

## Example

A session is at 82% full after twelve turns. Without attribution, the operator's options are: compact, restart, or guess.

The per-source breakdown shows: rules 8%, skills 28%, MCP returns 34%, subagent transcripts 6%, conversation 6%. The skills slice is the surprise — the session never explicitly invoked a skill. Listing loaded skills shows fourteen descriptions in the always-on context, each averaging 1,200 characters. The operator marks ten of them `"name-only"` in `skillOverrides` ([Claude Code skills reference](https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings)). The next session at the same point loads at 64%.

The breakdown made the difference between *"prune skills"* (right answer) and *"compact the conversation"* (the default reflex when only a single percentage is visible).

## Key Takeaways

- A single "X% full" indicator names the symptom, not the cause. Attribution cuts the same number into a remediation surface.
- Per-source and [per-tool attribution](../context-engineering/context-window-diagnostic-tooling.md) are complementary — different cuts of the same telemetry, each pointing at a different class of remediation.
- The categories must match the remediation primitives: rules, skills, MCPs, subagents, tool outputs, conversation, cache prefix. Collapsing two of them defeats the cut.
- Claude Code's OTel exporter already carries the attributes (`type`, `query_source`) needed to compute the breakdown from telemetry; the UI surface is one consumer, an OTel collector is another.
- When configuration sources are minimal and tool calls dominate, per-tool attribution is the more actionable cut — pick the axis matching the suspected cause.

## Related

- [Context-Window Diagnostic Tooling: Identifying Context-Heavy Tools](../context-engineering/context-window-diagnostic-tooling.md) — per-tool attribution, the complementary cut
- [Context Budget Allocation: Every Token Has a Cost](../context-engineering/context-budget-allocation.md) — the budget the breakdown serves
- [The Infinite Context anti-pattern](../anti-patterns/infinite-context.md) — the failure mode attribution prevents
- [Agent Observability: OTel, Cost Tracking, Trajectory Logs](agent-observability-otel.md) — the export path for attribution telemetry
- [Agent Debug Log Panel](agent-debug-log-panel.md) — the adjacent always-on surface for events rather than tokens
- [Per-Plugin Token-Cost Attribution via `claude plugin details`](plugin-token-cost-attribution.md) — the same attribution axis at plugin granularity
