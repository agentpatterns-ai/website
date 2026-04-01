---
title: "Progressive Disclosure for Layered Agent Definitions"
description: "Keep agent definitions minimal — identity and scope only — and load task knowledge on demand through skills rather than embedding all procedures upfront."
aliases:
  - on-demand skill loading
  - lazy loading agent instructions
tags:
  - agent-design
  - tool-agnostic
---

# Progressive Disclosure for Agent Definitions

> Keep agent definitions minimal — identity and scope only — and load detailed task knowledge on demand through skills rather than front-loading everything into the definition.

## The Problem with Monolithic Definitions

Every token in an agent definition consumes [context budget](../context-engineering/context-budget-allocation.md) on every invocation, whether or not that instruction is relevant to the current task. A monolithic agent definition embedding all possible instructions, checklists, and procedures for every task the agent might handle will be mostly irrelevant noise for any given task.

An agent asked to draft a blog post does not need its complete code review checklist loaded into context. An agent running a deployment does not need its content style guide. Yet monolithic definitions load everything unconditionally.

## The Pattern

Structure agent definitions in two layers:

**Layer 1 — The definition (always loaded):** Identity, scope, quality bar, and references to available skills. This is small — typically under 50 lines. It answers: who is this agent, what is it for, what standards does it hold, and where can it find detailed procedures?

**Layer 2 — Skills (loaded on demand):** Detailed how-to knowledge, checklists, step-by-step procedures, domain-specific rules. Each skill is self-contained and loaded by the agent when a task requires it.

The agent reads the definition, understands its role and capabilities, then reads only the skills relevant to the current task.

## What Goes Where

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

## Context Budget Impact

A monolithic agent definition of 2000 tokens loads 2000 tokens on every invocation. Separated into a 200-token definition and five 400-token skills, a task requiring two skills loads 200 + 400 + 400 = 1000 tokens — half the baseline, with the same available knowledge.

For long-running agents and agents spawned as sub-agents at scale, this compounds. Each sub-agent inheriting a bloated definition multiplies the waste across the entire fan-out.

## Implementation

Agent definitions reference skills by name or path. The agent reads them when the task requires it:

```
# Content Writer Agent

You are the content writer for the documentation site.

**Scope:** Writing pattern, technique, and workflow pages from researched issue content.

**Skills available:**
- writing-rules: style, tone, structure standards
- accuracy-framework: source verification and [unverified] marking
- content-pipeline: label transitions and PR conventions

Read the relevant skill before beginning each task.
```

The skills live in `.github/skills/` or `.claude/skills/` — separate files loaded when needed, not embedded.

The [Agent Skills standard](../standards/agent-skills-standard.md) formalizes this pattern with a portable `SKILL.md` entrypoint format supported across Claude Code, GitHub Copilot, Cursor, and other tools. [unverified]

## Self-Contained Skills

Each skill must be self-contained — it should work without the agent having to cross-reference other skills. A `writing-rules` skill that depends on `style-guide` being loaded creates implicit ordering requirements that the agent may not follow.

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

Each skill lives in its own file (e.g., `.claude/skills/lint-check.md`) and is loaded only when that specific check runs. A lint-only invocation loads 120 + 350 = 470 tokens instead of 1800.

## Key Takeaways

- Agent definitions should be under 50 lines: identity, scope, quality bar, skill references
- Skills carry the detailed knowledge: procedures, checklists, templates
- The agent reads skills on demand — irrelevant knowledge never enters the context
- Context budget savings compound across sub-agent fan-out
- The [Agent Skills standard](../standards/agent-skills-standard.md) provides a portable format for skills across tools

## Related

- [Agents vs Commands: Separation of Role and Workflow](agents-vs-commands.md)
- [Agent Composition Patterns: Chains, Fan-Out, Pipelines, Supervisors](agent-composition-patterns.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)
- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent Architecture](cognitive-reasoning-execution-separation.md)
- [Sub-Agents for Fan-Out Research and Context Isolation](../multi-agent/sub-agents-fan-out.md)
- [Controlling Agent Output](controlling-agent-output.md)
- [Cost-Aware Agent Design](cost-aware-agent-design.md)
- [Persona as Code](persona-as-code.md)
- [Task-Specific vs Role-Based Agents](task-specific-vs-role-based-agents.md)
- [Harness Engineering for Building Reliable AI Agents](harness-engineering.md)
- [Agent Harness: Initializer and Coding Agent Pattern](agent-harness.md)
