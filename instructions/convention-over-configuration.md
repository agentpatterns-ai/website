---
title: "Convention Over Configuration for Agent Workflows"
term: "Convention Over Configuration"
description: "Reduce agent errors by encoding decisions into naming conventions, directory structure, and label schemes so agents apply patterns rather than invent them."
tags:
  - agent-design
  - workflows
  - tool-agnostic
  - instructions
last_reviewed: 2026-06-13
maturity: established
---

# Convention Over Configuration for Agent Workflows

> Reduce agent decision-making by encoding the right choice into naming conventions, directory structure, and label schemes — so agents follow patterns rather than invent them.

## The problem with agent decisions

Every choice an agent makes is a chance for a wrong answer. Where should this file go — and which [scope's instruction file](layered-instruction-scopes.md) governs it? What should this branch be called? Which label applies? When the answer is not obvious, an agent guesses. Inconsistent guesses compound over time into a codebase that is hard to navigate and hard to automate further — the failure [standards as agent instructions](standards-as-agent-instructions.md) is meant to prevent.

Convention over configuration solves this by making the right choice the only obvious choice. The [AGENTS.md standard](../standards/agents-md.md) and similar project instruction standards exist to document these conventions in a form agents can read once and apply everywhere.

## Common convention categories

### File and directory names

Kebab-case, descriptive, no numeric prefixes. An agent writing a new pattern page does not need to decide between underscores, camelCase, or prefixes — the convention removes the question.

Directory structure maps directly to content type:

```
docs/patterns/          → reusable patterns
docs/techniques/        → specific techniques
docs/workflows/         → end-to-end workflows
docs/patterns/anti-patterns/ → what to avoid
```

An agent given a category label can work out the output path without being told — a `pattern` lands in `docs/patterns/`.

### Branch naming

```
content/<number>-<slug>   → new content
fix/<number>-<slug>       → corrections
feat/<number>-<slug>      → features
```

The formula is complete. An agent with an issue number and a title can generate the correct branch name deterministically.

### Commit messages

[Conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) (`type(scope): description`) give agents a complete grammar. No creativity required — only application.

### Pipeline labels

Predefined label sequences (`idea → researching → researched → drafting → reviewing → published`) mean an agent applies the next label in sequence rather than inventing stage names.

## Where conventions live

[CLAUDE.md and equivalent project instruction files](https://code.claude.com/docs/en/memory) are the standard place for conventions an agent should learn at session start. The agent applies conventions documented there — file naming rules, directory map, commit format — without re-reading them on each task.

The [AGENTS.md standard](https://agents.md) makes this formal: a single file at the project root that any agent can find and read to understand the project's conventions.

## The trade-off

Conventions reduce decision errors but introduce rigidity. A directory structure that works for five content types may not accommodate a sixth cleanly. The right point on this spectrum:

- Enough convention to eliminate common decision points
- Enough flexibility to handle edge cases without breaking the scheme

A convention that requires exceptions at every turn is a signal it was specified too narrowly.

## Why it works

Agents have no persistent memory between sessions. Each task starts cold. When naming and placement are deterministic — derivable from the issue number, content category, or file type — an agent needs no context about what previous agents chose, because the answer is [discoverable from the inputs](../context-engineering/discoverable-vs-nondiscoverable-context.md) rather than remembered. The correct output follows from the inputs alone.

Without conventions, an agent that meets an ambiguous situation guesses. Different agents make different guesses. Later agents must inspect prior outputs to work out which ad-hoc scheme was used — the re-derivation cost a project map like [AGENTS.md as a table of contents](agents-md-as-table-of-contents.md) removes — adding a disambiguation step that grows with every task. Conventions remove the disambiguation step entirely by taking out the ambiguity at the source.

## Anti-pattern: per-task invention

Agents that invent conventions per task produce inconsistent results: mixed branch naming, arbitrary file locations, ad-hoc commit formats. Each new agent must inspect what previous agents did before proceeding, rather than applying a deterministic formula.

## Key Takeaways

- Conventions convert agent decisions into pattern application, reducing error surface.
- File naming, directory structure, branch naming, and commit format are the highest-value convention categories.
- Document conventions in a project instruction file (AGENTS.md, CLAUDE.md) the agent reads at session start.
- Conventions that require frequent exceptions are over-specified — revise the scheme rather than the exceptions.

## Example

A content pipeline has agents that create, review, and publish pages. Without conventions, each agent invents its own patterns:

Without conventions:

- Agent A creates `docs/patterns/orchestratorWorker.md`
- Agent B creates `docs/Patterns/orchestrator_worker.md` for a related fix
- Agent C cannot find either file when searching for `orchestrator-worker`
- Branch names: `update-orch-worker`, `fix_orchestrator`, `orchestrator-worker-changes`
- Later agents must inspect all three to work out which is current

With conventions (kebab-case filenames, `fix/<issue>-<slug>` branch naming, `docs/<type>/` directories):

- Agent A creates `docs/patterns/orchestrator-worker.md`
- Agent B opens branch `fix/142-orchestrator-worker` and edits the same file
- Agent C finds the file immediately from the category label alone
- No coordination required — each agent applies the same deterministic formula

The shift: decisions that previously required judgment (what naming style? which directory?) become lookups against a known scheme.

## Related

- [Separation of Knowledge and Execution](../patterns/agent-design/separation-of-knowledge-and-execution.md)
- [AGENTS.md as Table of Contents](agents-md-as-table-of-contents.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [Instruction File Ecosystem](instruction-file-ecosystem.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
