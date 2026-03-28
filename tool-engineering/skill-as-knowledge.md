---
title: "Skill as Knowledge Pattern for AI Agent Development"
description: "Design skills as pure knowledge containers — domain rules, heuristics, and reference material — not executable behavior, so they remain portable across agents"
tags:
  - agent-design
  - instructions
aliases:
  - skill as knowledge container
  - knowledge-only skills
---

# Skill as Knowledge Pattern

> Design skills as pure knowledge containers — domain rules, heuristics, and reference material — not executable behavior, so they remain portable across agents, tools, and sessions.

## Knowledge, Not Behavior

A skill's primary content should be what the agent needs to *know*, not what it needs to *do*. Domain rules, URL patterns, style guides, accuracy constraints, and quality checklists are knowledge. Tool calls, shell commands, and execution sequences are behavior.

The [Agent Skills open standard](https://agentskills.io/what-are-skills) defines a skill as a folder containing a `SKILL.md` file — the core content is markdown knowledge, with scripts as an optional secondary artifact in a separate `scripts/` subdirectory. The standard's [progressive disclosure model](https://agentskills.io/specification) layers knowledge loading (metadata, then instructions, then resources), not execution staging.

Claude Code's skill documentation draws an [explicit distinction between "reference content" and "task content"](https://code.claude.com/docs/en/skills). Reference content adds domain rules and conventions that run inline. Task content provides step-by-step action instructions with `disable-model-invocation: true`. This structural separation exists precisely because knowledge and execution have different design constraints.

## Why Knowledge-Only Skills Are Portable

Skills encoded as domain knowledge in markdown work across [30+ tools](https://agentskills.io) — Claude Code, Cursor, VS Code Copilot, Gemini CLI, OpenAI Codex, Roo Code, Goose, JetBrains Junie, and others. This portability exists because markdown knowledge has no tool-specific dependencies. A skill that encodes "these URLs are authoritative sources" works identically in any agent. A skill that embeds `claude_code_tool_call()` invocations works in exactly one.

[Anthropic's best practices guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) reinforces this by framing skill content as the delta of domain-specific knowledge the model lacks. The "degrees of freedom" framework maps from high (heuristic knowledge with multiple valid approaches) to low (deterministic scripts) — knowledge skills sit at the high end where portability and flexibility are greatest.

## Independent Change Cadence

Knowledge and execution change for different reasons:

| Trigger | Knowledge layer (skill) | Execution layer (agent) |
|---------|------------------------|------------------------|
| Domain rules update | Skill changes | Agent unchanged |
| Workflow process changes | Skill unchanged | Agent changes |
| New tool or environment | Skill unchanged | Agent adapts |
| Source URLs rotate | Skill changes | Agent unchanged |

When you embed knowledge in agents, a domain change forces agent changes. When you embed execution in skills, a tool change forces skill changes. Separating them means each changes only when its own concern changes. [unverified]

This mirrors the [harness engineering pattern](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) at the system level: Anthropic describes encoding feature requirements in `feature_list.json` and progress in `claude-progress.txt` — externalizing domain knowledge from the coding agent's execution logic.

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

## Unverified Claims

- Knowledge and execution change on different cadences — domain rules update independently of workflow processes `[unverified]`

## Related

- [Separation of Knowledge and Execution](../agent-design/separation-of-knowledge-and-execution.md)
- [Skill Authoring Patterns](skill-authoring-patterns.md)
- [Skill Library Evolution](skill-library-evolution.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)
- [Progressive Disclosure for Agent Definitions](../agent-design/progressive-disclosure-agents.md)
- [Trajectory Logging via Progress Files and Git History](../observability/trajectory-logging-progress-files.md)
- [Skill Tool as Enforcement](skill-tool-runtime-enforcement.md)
- [SKILL.md Frontmatter Reference](skill-frontmatter-reference.md)
- [On-Demand Skill Hooks](on-demand-skill-hooks.md)
