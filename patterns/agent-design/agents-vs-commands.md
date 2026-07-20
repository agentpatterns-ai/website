---
title: "Agents vs Commands: Separation of Role and Workflow"
term: "Agents vs Commands"
description: "Commands define what to do; agents define who does it — separating orchestration from expertise lets you change either without touching the other."
tags:
  - agent-design
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: emerging
---

# Agents vs Commands: Separation of Role and Workflow

> Commands define what to do; agents define who does it — separating orchestration from expertise lets you change either without touching the other.

Learn this hands-on with the [Commands vs Agents lesson](https://learn.agentpatterns.ai/harness-engineering/commands-vs-agents/) — a guided lesson with quizzes.

## The split

Two concerns often collapse into a single file when you do not deliberately separate them: workflow orchestration and domain expertise. Orchestration covers what steps run, in what order, and under what conditions. Expertise covers how to do a specific job well.

Commands are workflow definitions. They describe the pipeline: fetch the issue, research the topic, draft the content, review it, open a PR. Commands name the steps, sequence them, and define what passes between them — the [knowledge and execution split](separation-of-knowledge-and-execution.md). They do not know how to research or how to draft. That is someone else's job.

Agents carry expertise. An agent definition sets the role, quality bar, constraints, and relevant skills. It knows what good output looks like for its domain (see [Specialized Agent Roles](specialized-agent-roles.md)). It does not know, or need to know, what pipeline called it.

This mirrors how effective teams work: a project manager defines the process and specialists do the work. You can separate the process from the people — the [delegation decision](delegation-decision.md) in agent terms.

## Why it matters

When orchestration and expertise live in the same file, every change touches both. Adding a pipeline step means editing the expert's definition. Improving an agent's quality bar means editing the pipeline. The two change at different rates and for different reasons, so separating them is the [composition](agent-composition-patterns.md) win.

Once separated, they become composable. The same `content-writer` agent can serve a `draft-content` command and an `implement-issue` command. The same `research-topic` command can delegate to a different specialist depending on the domain. Neither change means touching the other file.

Concrete examples of this split in a repository:

- A commands directory (for example `.claude/commands/` or `.github/commands/`) — pipeline definitions: step sequences, delegation targets, handoff criteria
- An agents directory (for example `.claude/agents/` or `.github/agents/`) — expertise definitions: content-writer, researcher, reviewer

## The anti-pattern

A single command file holds both the pipeline logic and the full domain instructions for every agent it calls. You can recognize it by these symptoms:

- Commands exceed 300 lines because they embed all agent knowledge inline
- The same expert instructions are copy-pasted across multiple commands
- Updating quality standards requires editing N command files instead of one agent definition
- Swapping one agent for a specialist alternative requires rewriting the command

## Scope boundaries

| Concern | Command | Agent |
|---------|---------|-------|
| Step sequence | Yes | No |
| Conditional branching | Yes | No |
| Delegation targets | Yes | No |
| Quality bar definition | No | Yes |
| Domain knowledge | No | Yes |
| Skill references | No | Yes |
| Success criteria | Handoff-level | Execution-level |

## Example

This shows the separation in a `.claude` directory. The command defines the pipeline and the agent carries the expertise. Neither file knows the internals of the other.

```
.claude/
  commands/
    implement-issue.md     # pipeline: fetch issue → research → draft → review → PR
  agents/
    content-writer.md      # expertise: tone, structure, quality bar for written output
    researcher.md          # expertise: source evaluation, synthesis, citation standards
```

```markdown
<!-- .claude/commands/implement-issue.md -->
# Implement Issue

1. Fetch the issue body from GitHub using `gh issue view $ISSUE_NUMBER`
2. Delegate research to @researcher — produce a 200-word summary of the problem space
3. Delegate implementation to @content-writer — produce the draft following their quality bar
4. Open a PR with `gh pr create`
```

```markdown
<!-- .claude/agents/content-writer.md -->
# Content Writer

You write documentation pages for the Agent Patterns repo.

- Keep prose under 25 words per sentence
- Every factual claim must be sourced; unsourceable claims are rewritten weaker or removed
- Headings follow the established page schema: Problem → Technique → Example → Key Takeaways
```

You can extend the command with new pipeline steps, for example an extra review stage, without editing `content-writer.md`. You can tighten the agent's quality bar without touching any command file.

## When this backfires

The pattern adds overhead without payoff in three conditions:

1. Single-use pipelines: If a command will never be reused and only one agent ever runs it, the separation is pure indirection. The cost of two files and an indirection layer outweighs a composability benefit that never arrives.
2. Rapidly changing scope: When both the pipeline and the domain expertise change at the same time, keeping the boundary slows iteration. Every decision means updating two files to stay coherent.
3. Solo projects without reuse: When agent definitions are never shared across commands, the abstraction is notional. The separation only pays off when the same agent serves multiple callers, or when the pipeline evolves independently of the expert definition.

The principle comes from [separation of concerns](https://en.wikipedia.org/wiki/Separation_of_concerns) and the [single-responsibility principle](https://en.wikipedia.org/wiki/Single-responsibility_principle). Both are foundational software design heuristics with well-documented trade-offs: they improve long-term maintainability at the cost of upfront complexity and indirection. The same cost-benefit calculus applies here.

## Key Takeaways

- Commands own orchestration (what, when, to whom); agents own execution (how, to what standard)
- One agent can serve multiple commands without modification
- Commands can swap agent targets without changing pipeline logic
- Monolithic command files that embed agent expertise are the failure mode

## Related

- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md)
- [Task-Specific Agents vs Role-Based Agents](task-specific-vs-role-based-agents.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Delegation Decision](delegation-decision.md)
- [Specialized Agent Roles](specialized-agent-roles.md)
- [Persona-as-Code: Defining Agent Roles as Structured Docs](persona-as-code.md)
- [Progressive Disclosure for Agent Definitions](progressive-disclosure-agents.md)
- [Classical SE Patterns as Agent Analogues](classical-se-patterns-agent-analogues.md)
