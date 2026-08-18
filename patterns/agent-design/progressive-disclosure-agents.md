---
title: "Progressive Disclosure for Layered Agent Definitions"
term: "Progressive Disclosure"
description: "Keep agent definitions minimal — identity and scope only — and load task knowledge on demand through skills rather than embedding all procedures upfront."
aliases:
  - on-demand skill loading
  - lazy loading agent instructions
tags:
  - agent-design
  - tool-agnostic
last_reviewed: 2026-08-18
maturity: adopted
---

# Progressive Disclosure for Layered Agent Definitions

> Keep agent definitions minimal — identity and scope only — and load task knowledge on demand through skills rather than front-loading everything.

Learn it hands-on: [Skills & Progressive Disclosure](https://learn.agentpatterns.ai/harness-engineering/skills-and-progressive-disclosure/) — guided lesson with quizzes.

## The problem with monolithic definitions

Every token in an agent definition consumes [context budget](../../context-engineering/context-budget-allocation.md) on every invocation, whether relevant to the current task or not. A monolithic definition embedding every checklist and procedure is mostly noise for any given task.

An agent drafting a blog post does not need its code review checklist loaded. An agent running a deployment does not need its content style guide. Monolithic definitions [load everything unconditionally](../../token-engineering/cost-aware-agent-design.md).

## The pattern

Structure agent definitions in two layers:

Layer 1 — the definition (always loaded): identity, scope, quality bar, and references to available skills. Typically under 50 lines. It answers four questions. Who is this agent? What is it for? What standards apply? And where are the detailed procedures?

Layer 2 — skills (loaded on demand): detailed how-to knowledge, checklists, step-by-step procedures, and domain-specific rules. Each skill is self-contained, and the agent loads it when a task requires it.

The agent reads the definition, then reads only the skills relevant to the current task.

## What goes where

| Content | Definition | Skill |
|---------|-----------|-------|
| Agent name and role | Yes | No |
| Scope / what it handles | Yes | No |
| Quality standards summary | Yes | No |
| Skill references | Yes (names only) | No |
| Step-by-step procedures | No | Yes |
| Domain checklists | No | Yes |
| Templates and examples | No | Yes |
| Tool-specific instructions | No | Yes |

## Context budget impact

A monolithic 2000-token definition loads 2000 tokens on every invocation. Split it into a 200-token definition and five 400-token skills, and a task that needs two skills loads 200 + 400 + 400 = 1000 tokens. That is half the baseline, with the same knowledge available.

For sub-agents spawned at scale, this compounds. Each one that inherits a bloated definition multiplies the waste across the whole fan-out.

Claude Code's built-in `claude-api` skill cut its context cost from over 200,000 tokens to about 25,000. It moved reference documentation to on-demand loading instead of bundling it up front ([Claude Code changelog, August 2026](https://code.claude.com/docs/en/changelog#2-1-234)).

## Implementation

Agent definitions reference skills by name or path; the agent reads them on demand:

```
# Content Writer Agent

You are the content writer for the documentation site.

**Scope:** Writing pattern, technique, and workflow pages from researched issue content.

**Skills available:**
- writing-rules: style, tone, structure standards
- accuracy-framework: source verification and claim sourcing rules
- content-pipeline: label transitions and PR conventions

Read the relevant skill before beginning each task.
```

The skills live in `.github/skills/` or `.claude/skills/` — separate files loaded when needed, not embedded.

The [Agent Skills standard](../../standards/agent-skills-standard.md) formalizes this pattern with a portable `SKILL.md` entrypoint format supported across Claude Code, GitHub Copilot, Cursor, and other tools ([agentskills.io](https://agentskills.io)).

## Self-contained skills

Each skill must be self-contained. It should work without the agent having to cross-reference other skills. A `writing-rules` skill that depends on `style-guide` being loaded creates implicit ordering requirements that the agent may not follow.

Skills that grow large are a signal to decompose further, not to merge back into the definition.

## Example

A CI review agent handles three tasks: lint check, security scan, and license audit. The monolithic approach embeds all three procedures in the definition:

```markdown
# CI Review Agent (monolithic — 1800 tokens)

You are the CI review agent. You run lint, security, and license checks.

## Lint Procedure
1. Run `eslint . --format json`
2. Parse output for errors vs warnings
3. Post summary comment on the PR
...50 more lines of lint instructions...

## Security Scan Procedure
1. Run `trivy fs . --format json`
2. Filter by severity >= HIGH
...40 more lines of security instructions...

## License Audit Procedure
1. Run `license-checker --json`
2. Compare against allowlist in `.license-policy.yml`
...30 more lines of license instructions...
```

With progressive disclosure, the definition shrinks to a skill index:

```markdown
# CI Review Agent (progressive — 120 tokens)

You are the CI review agent.

**Scope:** Running automated checks on pull requests.

**Skills available:**
- lint-check: ESLint execution and PR comment formatting
- security-scan: Trivy scan, severity filtering, and reporting
- license-audit: dependency license verification against policy

Read only the skill matching the requested check before executing.
```

Each skill lives in its own file (for example, `.claude/skills/lint-check.md`) and loads only when that specific check runs. A lint-only invocation loads 120 + 350 = 470 tokens instead of 1800.

## Why it works

Context window size directly affects inference quality. Give an agent a 2000-token monolithic definition and its attention mechanism must spread weight across all 2000 tokens — including the 80% irrelevant to the current task. This is attention dilution: critical instructions compete with noise, which lowers the chance that the model weights them correctly ([Marta Fernández García, Feb 2026](https://medium.com/@martia_es/progressive-disclosure-the-technique-that-helps-control-context-and-tokens-in-ai-agents-8d6108b09289)). Irrelevant rules in the same context window can also cause instruction interference. The model enters self-reconciliation mode when rules that do not apply to the task appear to conflict with rules that do, producing hedged output rather than precise execution. Smaller, focused contexts remove both failure modes.

## When this backfires

Progressive disclosure adds complexity that creates its own failure modes:

- Skill index rot: if the definition lists skills by name but the skill files drift — renamed, moved, or deleted — the agent tries to load a skill that no longer exists and either fails or falls back to guessing. Keep the index in sync with the filesystem.
- Wrong skill loaded: agents use their own judgment to pick the relevant skill. Ambiguous task descriptions or [poorly named skills](../../standards/agent-skills-standard.md) lead the agent to load the wrong skill and run against the wrong procedures.
- Orchestration overhead: each skill load is another read operation. For tasks that genuinely need all skills at once, progressive disclosure adds round-trips without reducing token load.
- Self-contained skill violations: if a skill quietly depends on another skill loading first (shared terminology, referenced templates), the agent may produce inconsistent output when it loads skills in a different order or loads only one.

The pattern works best when tasks are clearly scoped and [skills are genuinely orthogonal](separation-of-knowledge-and-execution.md). It degrades when the agent's task space is broad and overlapping.

## FAQ

**How much context does progressive disclosure actually save?**

It depends on how many skills a task needs. A monolithic 2000-token definition loads all 2000 tokens on every invocation; split into a 200-token definition plus five 400-token skills, a task that needs two skills loads 1000 — half the baseline with the same knowledge reachable. The CI review example goes further: a lint-only run loads 470 tokens instead of 1800.

**Why must each skill be self-contained?**

A skill that depends on another skill being loaded first creates an implicit ordering requirement the agent may not follow. Because the agent picks which skills to read, it may load them in a different order or load only one, producing inconsistent output. Skills that grow large are a signal to decompose further, not to merge back into the definition.

**When does progressive disclosure cost more than it saves?**

When the task genuinely needs every skill at once: each load is another read operation, so the pattern adds round-trips without reducing the token load. Broad, overlapping task spaces make it worse — ambiguous task descriptions lead the agent to load the wrong skill, and a stale skill index points at files that were renamed, moved, or deleted.

## Key Takeaways

- Agent definitions should be under 50 lines: identity, scope, quality bar, skill references
- Skills carry the detailed knowledge: procedures, checklists, templates
- The agent reads skills on demand — irrelevant knowledge never enters the context
- Context budget savings compound across sub-agent fan-out
- The [Agent Skills standard](../../standards/agent-skills-standard.md) provides a portable format for skills across tools

## Related

- [Agent Skills: Cross-Tool Task Knowledge Standard](../../standards/agent-skills-standard.md)
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md)
- [Agents vs Commands: Separation of Role and Workflow](agents-vs-commands.md)
- [Agent Definition Formats: How Tools Define Agent Behavior](../../standards/agent-definition-formats.md)
- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md)
- [Sub-Agents for Fan-Out Research and Context Isolation](../multi-agent/sub-agents-fan-out.md)
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md)
