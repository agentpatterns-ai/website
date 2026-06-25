---
title: "Skill as Knowledge Pattern for AI Agent Development"
term: "Skill as Knowledge Pattern"
description: "Design skills as pure knowledge containers — domain rules, heuristics, and reference material — not executable behavior, so they remain portable across agents, tools, and sessions without modification."
tags:
  - agent-design
  - instructions
  - tool-agnostic
  - tool-engineering
aliases:
  - skill as knowledge container
  - knowledge-only skills
last_reviewed: 2026-06-24
maturity: established
---

# Skill as Knowledge Pattern

> Design skills as knowledge containers — domain rules, heuristics, and reference material — not executable behavior, so they remain portable across agents, tools, and sessions.

**Learn it hands-on:** [Skills as a Tool-Engineering Surface](https://learn.agentpatterns.ai/tool-engineering/skills-as-a-tool-surface/) — guided lesson with quizzes.

## Knowledge, Not Behavior

A skill's primary content is what the agent needs to *know*, not *do*. Domain rules, URL patterns, style guides, and quality checklists are knowledge; tool calls, shell commands, and execution sequences are behavior.

The [Agent Skills open standard](https://agentskills.io/what-are-skills) defines a skill as a folder containing a `SKILL.md` file — the core content is markdown knowledge, with scripts as an optional secondary artifact in a separate `scripts/` subdirectory. The standard's [progressive disclosure model](https://agentskills.io/specification) layers knowledge loading (metadata, then instructions, then resources), not execution staging.

Claude Code's skill documentation draws an [explicit distinction between "reference content" and "task content"](https://code.claude.com/docs/en/skills). Reference content adds domain rules and conventions that run inline. Task content provides step-by-step action instructions with `disable-model-invocation: true`. This structural separation exists precisely because knowledge and execution have different design constraints.

## Why Knowledge-Only Skills Are Portable

Skills encoded as markdown knowledge work across [30+ tools](https://agentskills.io) — Claude Code, Cursor, VS Code Copilot, Gemini CLI, Codex, and others — because markdown knowledge has no tool-specific dependencies. A skill that names authoritative URL patterns works identically in any agent; a skill that embeds `claude_code_tool_call()` works in exactly one.

[Anthropic's best practices guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) reinforces this by framing skill content as the delta of domain-specific knowledge the model lacks. The "degrees of freedom" framework maps from high (heuristic knowledge with multiple valid approaches) to low (deterministic scripts) — knowledge skills sit at the high end where portability and flexibility are greatest.

Microsoft's developer guidance offers a concrete sizing heuristic for this delta: omit what the base model already knows — standard SDK and API patterns — and include only the project-specific knowledge the model lacks ([Microsoft: Stop Overloading Your Skills](https://developer.microsoft.com/blog/stop-overloading-your-skills)).

## Independent Change Cadence

Knowledge and execution change for different reasons:

| Trigger | Knowledge layer (skill) | Execution layer (agent) |
|---------|------------------------|------------------------|
| Domain rules update | Skill changes | Agent unchanged |
| Workflow process changes | Skill unchanged | Agent changes |
| New tool or environment | Skill unchanged | Agent adapts |
| Source URLs rotate | Skill changes | Agent unchanged |

Embedding knowledge in agents means a domain change forces agent changes; embedding execution in skills means a tool change forces skill changes. Separating the two so each evolves on its own cadence is the [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle) applied to agent layers.

This mirrors the [harness engineering](../agent-design/harness-engineering.md) pattern at the system level: Anthropic describes encoding feature requirements in `feature_list.json` and progress in `claude-progress.txt` — externalizing domain knowledge from the coding agent's execution logic ([Anthropic: Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

## The Anti-Pattern: Skill Scripts

The failure mode is skills that embed tool calls, API sequences, or shell commands directly. [Anthropic's engineering blog](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) positions skills as "procedural knowledge captured from human workflows" — the emphasis is on expertise as the primary content, with code as a secondary mechanism for deterministic operations only.

[Anthropic's advanced tool use patterns](https://www.anthropic.com/engineering/advanced-tool-use) confirm this split: "JSON schemas define what's structurally valid, but can't express usage patterns." The gap between structural definitions (execution) and behavioral guidelines (knowledge) is exactly what skills fill. Skills that collapse back into execution logic lose this advantage.

## Example

**Before** — skill script embedding execution logic (non-portable):

```markdown
# Skill: Check Documentation Links

## Steps
1. Run `claude_code_tool("bash", "find docs/ -name '*.md' -exec grep -l 'http' {} +")`
2. For each file, run `claude_code_tool("bash", "curl -s -o /dev/null -w '%{http_code}' $URL")`
3. Collect failures into `broken-links.json`
```

**After** — knowledge-only skill (portable across any agent or tool):

```markdown
# Skill: Documentation Link Standards

## Link quality rules
- Every external link must point to a primary source, not a secondary summary
- Vendor documentation links must target versioned URLs (e.g., /v2/docs/) not unversioned roots
- Replace links returning 404 with the closest equivalent from the same domain

## Authoritative domains
- Vendor docs: docs.anthropic.com, code.claude.com, docs.github.com
- Standards: agentskills.io, llmstxt.org, agents.md
- Research: arxiv.org (cs.AI, cs.SE sections)

## Known URL patterns
- Anthropic engineering blogs: anthropic.com/engineering/{slug}
- GitHub docs: docs.github.com/en/{product}/{topic}
```

The first version works only in Claude Code and breaks if the tool API changes. The second version works in any agent that can read markdown — it tells the agent *what good links look like*, and the agent determines *how* to check them in its own execution environment.

## Key Takeaways

- Skills encode what the agent should know (domain rules, heuristics, quality constraints), not what it should do (tool calls, shell commands).
- Knowledge-only skills are inherently portable — they work across any agent in any tool without modification.
- Separating knowledge from execution prevents coupled change: domain updates touch skills, process updates touch agents.
- Skills that embed execution sequences ("skill scripts") are brittle, non-portable, and collapse the [separation of knowledge and execution](../agent-design/separation-of-knowledge-and-execution.md).

## When This Backfires

Knowledge-only skills fail when:

- **The "knowledge" is actually a procedure.** If a skill encodes a fixed sequence — run script A, then B, then C — calling it "knowledge" is a mislabel. Execution-heavy workflows belong in agents or task skills with `disable-model-invocation: true`.
- **Portability isn't a goal.** Single-tool deployments (Claude Code only, no cross-tool requirement) gain no portability benefit from avoiding tool calls. The overhead of factoring knowledge from execution is only worthwhile when the skill must run in multiple environments.
- **The domain knowledge is too sparse to warrant a skill.** A skill that encodes one URL or one formatting rule adds indirection without payoff. Inline context or CLAUDE.md serves better below a few hundred tokens of domain knowledge.
- **Knowledge becomes a reference dump.** Skills with 500+ lines of domain rules degrade discovery and slow invocation. Progressive disclosure (main SKILL.md + reference files) is needed at that scale, or the knowledge should be split into narrower skills.

## Related

- [Separation of Knowledge and Execution](../agent-design/separation-of-knowledge-and-execution.md)
- [Skill Authoring Patterns](skill-authoring-patterns.md)
- [Skill Library Evolution](skill-library-evolution.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)
- [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md)
- [Skill Tool as Enforcement](skill-tool-runtime-enforcement.md)
- [SKILL.md Frontmatter Reference](skill-frontmatter-reference.md)
- [On-Demand Skill Hooks](on-demand-skill-hooks.md)
