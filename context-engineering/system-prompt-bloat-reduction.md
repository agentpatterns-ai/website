---
title: "Reducing System-Prompt Token Bloat in Coding Agents"
term: "System-Prompt Bloat Reduction"
description: "Measure what fills a coding agent's shipped system prompt, then switch off the tools, skills, and features you never use so the fixed prefix stops crowding out task context."
tags:
  - context-engineering
  - cost-performance
  - claude
aliases:
  - system prompt trimming
  - trimming tool definitions
applies_to: "claude-code@2.x"
last_reviewed: 2026-07-17
maturity: adopted
---

# Reducing System-Prompt Token Bloat in Coding Agents

> Measure what fills a coding agent's system prompt, then cut the tools, skills, and features you never use to free the token budget.

System-prompt token bloat is the static payload — tool definitions, a skills catalogue, and feature instructions — that a coding agent re-sends on every request whether you touch those features or not. You reduce it by measuring the payload first, then switching off the parts that do not earn their place, so the fixed prefix shrinks and more of the context window stays free for your task.

Two conditions shape the payoff before you cut anything: with prompt caching active the win is mostly context-window headroom, not a large per-turn cost cut, and every cut disables a feature. Trim what you do not use, keep what your workflow relies on.

## Measure before you trim

Run `/context` in a Claude Code session. It breaks the context window into system prompt, system tools, MCP tools, memory files, and messages, each with a token count and its share of the window ([AI Hero — How To Kill The Bloat](https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt); [Claude Code — Manage costs](https://code.claude.com/docs/en/costs)). Note the numbers before changing anything so you can compare afterward.

`/context` reports tools as one group, so it will not tell you which single tool is largest. To rank individual tools, route the CLI through a logging proxy that records each request untouched. Matt Pocock's proxy prints a ranked table — one run showed `69 tools · 154,946 tool bytes · 65,538 real input tokens`, with the `Workflow` tool alone at roughly 5,307 tokens ([AI Hero — How To Kill The Bloat](https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt)). The ranked list is your cut list. For the diagnostic side in more depth, see [context-window diagnostic tooling](context-window-diagnostic-tooling.md).

## What to cut, and how

Two Claude Code settings do the trimming, both in `~/.claude/settings.json` (all projects) or `.claude/settings.json` (one project).

`disable*` flags switch off a whole feature and everything it carries: `disableBundledSkills` removes Anthropic's bundled skills and workflows while leaving their slash commands typable, `disableWorkflows` removes the `Workflow` tool, and `disableRemoteControl`, `disableClaudeAiConnectors`, and `disableArtifact` remove those features ([Claude Code — Settings](https://code.claude.com/docs/en/settings)).

A `permissions.deny` rule with a bare tool name removes an individual tool's definition from the payload. The distinction matters: a bare name (`"NotebookEdit"`) drops the definition, while a scoped rule (`"Bash(rm *)"`) only blocks the matching call and leaves the schema in the payload, so it saves no tokens ([AI Hero](https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt), observed by reading the proxied requests). When `disableBundledSkills` is too blunt, `skillOverrides` set to `"off"` or `"user-invocable-only"` drops individual bundled skills instead.

Then restart and re-run `/context` to confirm the drop. Do not hand-prune MCP servers first: Claude Code already defers MCP tool definitions by default through tool search, so the trimmable weight is mostly built-in tools, skills, and features, not MCP ([Claude Code — Manage costs](https://code.claude.com/docs/en/costs); [Anthropic — advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)).

## Why it works

Each turn is a stateless API request that re-sends the whole system prompt and every tool schema before the model reaches your task ([Claude Code — Manage costs](https://code.claude.com/docs/en/costs); [MCP schema overhead, issue #2808](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/2808)). Tool and feature definitions sit in that fixed prefix, so removing a definition shrinks the prefix permanently. Token cost scales with context size and the window is finite, so a smaller prefix leaves more room for task context and less for the model to read past before it reaches your problem.

## When this backfires

Trimming is conditional, not free:

- Prompt caching already bills the repeated prefix as cache reads at a fraction of the base input cost, so the per-turn dollar saving is smaller than the raw token delta implies ([Claude Code — Manage costs](https://code.claude.com/docs/en/costs)). The durable win is context-window headroom, not a large cost cut.
- Every cut disables a feature. `disableWorkflows` removes the `Workflow` tool that background jobs and multi-agent runs depend on, and denying plan-mode or notebook tools removes those too ([AI Hero](https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt)). Keep what your workflow uses.
- A shared `.claude/settings.json` deny list strips the tool for every teammate and every project — a blunt instrument that produces confusing capability gaps.
- If your real cost driver is conversation history or large file reads, the static preamble is a rounding error. Clearing between tasks with `/clear` and keeping CLAUDE.md lean do more ([Claude Code — Manage costs](https://code.claude.com/docs/en/costs)).

## Example

A settings block that trims features you have measured as unused, drawn from Matt Pocock's published configuration ([AI Hero](https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt)):

```json
{
  "permissions": {
    "deny": ["NotebookEdit", "CronCreate", "CronDelete", "CronList"]
  },
  "disableBundledSkills": true,
  "disableWorkflows": true,
  "disableArtifact": true
}
```

The bare names in `deny` remove those tool definitions from every request; the `disable*` flags remove whole feature clusters. Treat it as a menu, not a prescription — keep any feature your own `/context` run shows you actually use.

## Key Takeaways

- The shipped system prompt re-sends unused tool, skill, and feature definitions on every stateless turn; those tokens occupy the fixed prefix.
- Measure with `/context` and a logging proxy before cutting, so you remove the exact tools you do not use instead of guessing.
- Trim with `disable*` flags for whole features and bare-name `permissions.deny` rules for individual tools; scoped deny rules block calls but save no tokens.
- With prompt caching active, the payoff is context-window headroom more than per-turn cost, and each cut removes a capability — keep what your workflow needs.

## Related

- [Context-Window Diagnostic Tooling](context-window-diagnostic-tooling.md) — the measurement step: attribute context growth to specific tools before you trim.
- [Context Budget Allocation](context-budget-allocation.md) — the finite-budget principle this technique applies.
- [Dynamic System Prompt Composition](dynamic-system-prompt-composition.md) — assembling prompts at runtime, distinct from removing dead weight.
- [Exclude Dynamic System Prompt Sections for Cross-Machine Cache Sharing](exclude-dynamic-system-prompt-sections.md) — a different Claude Code system-prompt saving, aimed at cache sharing.
- [Prompt Caching: Architectural Discipline for Agents](prompt-caching-architectural-discipline.md) — the caching economics behind the cost caveat above.
- [Re-Auditing Context Engineering Across Model Generations](generation-scoped-context-engineering.md) — the generation-jump trigger that turns bloat reduction from one-off cleanup into a recurring audit.
