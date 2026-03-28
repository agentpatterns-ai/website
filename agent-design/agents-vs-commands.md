---
title: "Agents vs Commands: Separation of Role and Workflow"
description: "Commands define what to do; agents define who does it — separating orchestration from expertise lets you change either without touching the other."
tags:
  - agent-design
  - tool-agnostic
---

# Agents vs Commands: Separation of Role and Workflow

> Commands define what to do; agents define who does it — separating orchestration from expertise lets you change either without touching the other.

## The Split

In agent-driven projects, two distinct concerns collapse into a single file when not deliberately separated: workflow orchestration (what steps run, in what order, with what conditions) and domain expertise (how to do a specific job well).

**Commands** are workflow definitions. They describe the pipeline: fetch the issue, research the topic, draft the content, review it, open a PR. Commands name the steps, sequence them, and define what passes between them. They do not know how to research or how to draft — that is someone else's job.

**Agents** carry expertise. An agent definition specifies role, quality bar, constraints, and relevant skills. It knows what good output looks like for its domain. It does not know, or need to know, what pipeline called it.

This mirrors how effective teams operate: a project manager defines the process; specialists execute the work. The process is separable from the people.

## Why It Matters

When orchestration and expertise live in the same file, every change touches both concerns. Adding a pipeline step requires editing the expert's definition. Improving an agent's quality bar requires editing the pipeline. The two evolve at different rates and for different reasons.

Separated, they become composable. The same `content-writer` agent can serve a `draft-content` command and an `implement-issue` command. The same `research-topic` command can delegate to a different specialist depending on the domain. Neither change requires touching the other file.

Concrete examples of this split in a repository:

- A commands directory (e.g. `.claude/commands/` or `.github/commands/`) — pipeline definitions: step sequences, delegation targets, handoff criteria
- An agents directory (e.g. `.claude/agents/` or `.github/agents/`) — expertise definitions: content-writer, researcher, reviewer

## The Anti-Pattern

A monolithic command file that contains both the pipeline logic and the complete domain instructions for every agent it calls. Recognizable symptoms:

- Commands exceed 300 lines because they embed all agent knowledge inline
- The same expert instructions are copy-pasted across multiple commands
- Updating quality standards requires editing N command files instead of one agent definition
- Swapping one agent for a specialist alternative requires rewriting the command

## Scope Boundaries

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

The following shows the separation in a `.claude` directory. The command defines the pipeline; the agent carries the expertise. Neither file knows the internals of the other.

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
- Every claim must link to a source or be marked `[unverified]`
- Headings follow the established page schema: Problem → Technique → Example → Key Takeaways
```

The command can be extended with new pipeline steps (e.g., an additional review stage) without editing `content-writer.md`. The agent's quality bar can be tightened without touching any command file.

## Key Takeaways

- Commands own orchestration (what, when, to whom); agents own execution (how, to what standard)
- One agent can serve multiple commands without modification
- Commands can swap agent targets without changing pipeline logic
- Monolithic command files that embed agent expertise are the failure mode

## Related

- [Separation of Knowledge and Execution](separation-of-knowledge-and-execution.md)
- [Progressive Disclosure for Agent Definitions](progressive-disclosure-agents.md)
- [Task-Specific Agents vs Role-Based Agents](task-specific-vs-role-based-agents.md)
- [Agent Composition Patterns](agent-composition-patterns.md)
- [Cognitive Reasoning Execution Separation](cognitive-reasoning-execution-separation.md)
- [Delegation Decision](delegation-decision.md)
- [Specialized Agent Roles](specialized-agent-roles.md)
