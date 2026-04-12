---
title: "Convention Over Configuration in Agent Workflow Design"
description: "Reduce agent errors by encoding decisions into naming conventions, directory structure, and label schemes so agents apply patterns rather than invent them."
tags:
  - agent-design
  - workflows
---

# Convention Over Configuration for Agent Workflows

> Reduce agent decision-making by encoding the right choice into naming conventions, directory structure, and label schemes — so agents follow patterns rather than invent them.

## The Problem with Agent Decisions

Every choice an agent makes is an opportunity for a wrong answer. Where should this file go? What should this branch be called? Which label applies? When the answer isn't obvious, an agent guesses — and inconsistent guesses compound over time into a codebase that's hard to navigate and hard to automate further.

Convention over configuration solves this by making the right choice the only obvious choice. [AGENTS.md](https://agents.md) and similar project instruction standards exist specifically to document these conventions in a form agents can read once and apply everywhere.

## Common Convention Categories

### File and Directory Names

Kebab-case, descriptive, no numeric prefixes. An agent writing a new pattern page doesn't need to decide whether to use underscores, camelCase, or prefixes — the convention eliminates the question.

Directory structure maps directly to content type:

```
docs/patterns/          → reusable patterns
docs/techniques/        → specific techniques
docs/workflows/         → end-to-end workflows
docs/patterns/anti-patterns/ → what to avoid
```

An agent given a category label can determine the output path without being told.

### Branch Naming

```
content/<number>-<slug>   → new content
fix/<number>-<slug>       → corrections
feat/<number>-<slug>      → features
```

The formula is complete. An agent with an issue number and a title can generate the correct branch name deterministically.

### Commit Messages

[Conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) (`type(scope): description`) give agents a complete grammar. No creativity required — only application.

### Pipeline Labels

Predefined label sequences (`idea → researching → researched → drafting → reviewing → published`) mean an agent applies the next label in sequence rather than inventing stage names.

## Where Conventions Live

[CLAUDE.md and equivalent project instruction files](https://code.claude.com/docs/en/memory) are the standard location for conventions an agent should internalize at session start. Conventions documented there — file naming rules, directory map, commit format — are applied by the agent without re-reading on each task.

The [AGENTS.md standard](https://agents.md) formalizes this: a single file at the project root that any agent can locate and read to understand the project's conventions.

## The Trade-Off

Conventions reduce decision errors but introduce rigidity. A directory structure that works for five content types may not accommodate a sixth cleanly. The right point on this spectrum:

- Enough convention to eliminate common decision points
- Enough flexibility to handle edge cases without breaking the scheme

A convention that requires exceptions at every turn is a signal it was specified too narrowly.

## Why It Works

Agents have no persistent memory between sessions. Each task starts cold. When naming and placement are deterministic — derivable from the issue number, content category, or file type — an agent needs no context about what previous agents chose. The correct output follows from the inputs alone.

Without conventions, an agent encountering an ambiguous situation guesses. Different agents make different guesses. Later agents must inspect prior outputs to infer which ad-hoc scheme was used — adding a disambiguation step that grows with every task. Conventions eliminate the disambiguation step entirely by removing the ambiguity at the source.

## Anti-Pattern: Per-Task Invention

Agents that invent conventions per task produce inconsistent results: mixed branch naming, arbitrary file locations, ad-hoc commit formats. Each new agent must inspect what previous agents did before proceeding, rather than applying a deterministic formula.

## Key Takeaways

- Conventions convert agent decisions into pattern application, reducing error surface.
- File naming, directory structure, branch naming, and commit format are the highest-value convention categories.
- Document conventions in a project instruction file (AGENTS.md, CLAUDE.md) the agent reads at session start.
- Conventions that require frequent exceptions are over-specified — revise the scheme rather than the exceptions.

## Example

A [content pipeline](../workflows/content-pipeline.md) has agents that create, review, and publish pages. Without conventions, each agent invents its own patterns:

**Without conventions:**

- Agent A creates `docs/patterns/orchestratorWorker.md`
- Agent B creates `docs/Patterns/orchestrator_worker.md` for a related fix
- Agent C can't find either file when searching for `orchestrator-worker`
- Branch names: `update-orch-worker`, `fix_orchestrator`, `orchestrator-worker-changes`
- Later agents must inspect all three to determine which is current

**With conventions (kebab-case filenames, `fix/<issue>-<slug>` branch naming, `docs/<type>/` directories):**

- Agent A creates `docs/patterns/orchestrator-worker.md`
- Agent B opens branch `fix/142-orchestrator-worker` and edits the same file
- Agent C locates the file immediately from the category label alone
- No coordination required — each agent applies the same deterministic formula

The key shift: decisions that previously required judgment (what naming style? which directory?) become lookups against a known scheme.

## Related

- [Separation of Knowledge and Execution](../agent-design/separation-of-knowledge-and-execution.md)
- [Context Priming](../context-engineering/context-priming.md)
- [AGENTS.md as Table of Contents](agents-md-as-table-of-contents.md)
- [AGENTS.md Distributed Conventions](agents-md-distributed-conventions.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Hierarchical CLAUDE.md](hierarchical-claude-md.md)
- [Instruction File Ecosystem](instruction-file-ecosystem.md)
- [Layered Instruction Scopes](layered-instruction-scopes.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [AGENTS.md Design Patterns](agents-md-design-patterns.md)
- [Evaluating AGENTS.md Context Files](evaluating-agents-md-context-files.md)
- [Import Composition Pattern](import-composition-pattern.md)
- [Post-Compaction Reread Protocol](post-compaction-reread-protocol.md)
- [Prompt Governance via PR](prompt-governance-via-pr.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
