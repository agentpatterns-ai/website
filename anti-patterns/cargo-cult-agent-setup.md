---
title: "Cargo Cult Agent Setup: Copying Without Understanding"
description: "Copying agent configurations without understanding why they work produces agents that follow irrelevant conventions and miss project-specific needs."
tags:
  - human-factors
  - instructions
aliases:
  - cargo cult configuration
  - copy-paste configuration
---

# Cargo Cult Agent Setup

> Copying agent configurations without understanding why they work produces agents that follow irrelevant conventions and miss project-specific needs.

## The Pattern

A developer finds a well-regarded AGENTS.md or agent configuration from a tutorial and copies it into their project. The agent now follows conventions from someone else's React app or data pipeline — none of which match the project at hand. The configuration looks complete but doesn't serve the actual work `[unverified]`.

## Why It Happens

Good configurations are visible; the reasoning behind them is not. Curated repositories surface polished, community-validated configurations that look authoritative. The friction of writing from scratch is real, so copying feels like a safe shortcut.

The result: a cargo cult. The forms are present (AGENTS.md, system prompt, skills directory), but the function is missing.

## What Goes Wrong

**Irrelevant conventions.** An AGENTS.md written for a typed functional codebase pushes an agent toward patterns that conflict with an imperative OOP project. The agent follows the instructions, but the instructions are wrong for the context.

**Missing domain knowledge.** Skills encoding one project's deployment process, test conventions, or API patterns don't transfer. The agent invokes the wrong tools or skips actual workflow steps.

**False confidence.** A populated configuration looks like a working one. Teams assume coverage that doesn't exist and skip verification they would have done with a blank slate.

## What to Copy vs. What to Build

| Copy structural patterns | Build from project knowledge |
|--------------------------|------------------------------|
| Three-layer architecture (skills, agents, commands) | Specific instructions and rules |
| Hook placement conventions | Domain and codebase knowledge |
| Pipeline stage design | Tool-specific configuration |
| Verification gate patterns | Skill implementations |

Structural patterns transfer because they're abstract. Content — instructions, skills, domain rules — is specific and doesn't transfer.

## The Fix

Start your AGENTS.md from the [agents.md open standard](https://agents.md) with only the fields that describe your project's actual architecture. Add instructions when you've identified a recurring problem they would solve. Add skills when a task recurs and benefits from encoded knowledge.

Use community configurations for pattern reference — to see what kinds of instructions work and what structure a skill file can take. Do not copy them as solutions.

## Key Takeaways

- Copied configurations follow the source project's conventions, not yours
- Structural patterns transfer; content (instructions, skills, domain rules) does not
- A configuration that doesn't match project reality produces systematic wrong behavior
- Write AGENTS.md from project-specific needs, using templates only for structural reference

## Example

A Python data pipeline team finds a well-structured AGENTS.md from a popular TypeScript open-source project. It includes instructions to prefer `interface` over `type`, enforce strict null checks, run `npm test` before every commit, and use conventional commit prefixes. They copy it wholesale.

The agent now suggests TypeScript-style patterns when writing Python, tries to run `npm test` in a project with no Node dependency, and applies commit conventions from a JavaScript community that don't match the team's existing history.

The correct approach: start from a blank AGENTS.md with only what the project actually needs.

```markdown
# Project: DataPipe

## Stack
Python 3.11, pandas, SQLAlchemy. No TypeScript, no Node.

## Testing
Run `pytest tests/` before committing. Integration tests require `POSTGRES_URL` env var.

## Commit style
`<type>: <description>` — types: feat, fix, chore, docs.
```

Three instructions, all grounded in project reality. The copied configuration had twenty — none of which applied.

## Unverified Claims

- Copied configuration looking complete but not serving actual work `[unverified]`

## Related

- [The Anthropomorphized Agent](anthropomorphized-agent.md)
- [The Copy-Paste Agent](copy-paste-agent.md)
- [The Prompt Tinkerer](prompt-tinkerer.md)
- [Framework-First Agent Development](framework-first.md)
- [The Implicit Knowledge Problem](implicit-knowledge-problem.md)
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [Pattern Replication Risk](pattern-replication-risk.md)
- [Distractor Interference](distractor-interference.md)
