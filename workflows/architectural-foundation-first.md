---
title: "Lay the Architectural Foundation by Hand Before Delegating"
description: "Build the structural skeleton and a few representative features yourself before handing a project to an agent — the foundation is the primary investment that makes large-scale delegation safe."
tags:
  - context-engineering
  - agent-design
  - human-factors
---

# Lay the Architectural Foundation by Hand Before Delegating to Agents

> Build the structural skeleton and a few representative features yourself before handing a project to an agent — the foundation is the primary investment that makes large-scale delegation safe.

## The Cost of Skipping the Foundation

Prompting an agent to build a feature or application from scratch without a foundation produces output that compiles but deviates from your architectural goals. The agent defaults to patterns it has seen frequently in training, which may not match your team's standards for modularity, layer separation, or naming.

[OpenAI's Sora Android team](https://openai.com/index/shipping-sora-for-android-with-codex/) discovered this directly. Their initial prompt — "Build the Sora Android app based on the iOS code. Go." — produced code that was technically functional but had structural problems: extra view models, logic placed in the wrong architectural layer, and patterns inconsistent with the team's standards.

Thoughtworks frames the same phenomenon through ["ambient affordances"](https://martinfowler.com/articles/harness-engineering.html) — structural properties of the codebase that make it legible and tractable to the agent. Clear module boundaries, consistent package structure, and established patterns act as implicit constraints that raise the agent's success rate without needing to be re-specified in every prompt.

## What the Foundation Includes

Human engineers should personally build:

- **Modularization**: the module boundaries and package structure
- **Dependency injection**: the DI setup and how components are wired
- **Navigation**: the navigation framework and routing conventions
- **Authentication**: the auth flow and session management
- **Representative features**: two to three features end-to-end that embody the correct patterns

The representative features are the most important element. They demonstrate correct patterns in concrete, executable form. The agent can match against them. "We needed to show Codex what's 'correct' on our team" — examples beat instructions.

## What to Document

After building the foundation, document what the agent needs to know to extend it correctly:

- Which architectural layer owns which responsibilities
- How to add a new feature using the existing pattern (point to the example features)
- Mandatory CI commands (linting, formatting) that must run before every commit
- Any constraints that are not visible from the code alone

This documentation belongs in AGENTS.md or equivalent instruction files, not in the prompt. It needs to persist across every agent session.

## The Result of Getting This Right

The Sora team shipped an Android app where 85% of the final codebase was agent-written, with a 99.9% crash-free rate at launch ([source](https://openai.com/index/shipping-sora-for-android-with-codex/)). The foundation — built by hand — made that ratio possible.

The investment in the foundation is not overhead. It is the primary control mechanism that determines whether agent-written code meets your standards or requires constant correction.

## The Tradeoff

Building the foundation yourself takes time upfront. The alternative — prompting without a foundation — produces architectural drift that compounds with every agent session. Correcting structural problems after the fact is significantly more expensive than establishing the structure before delegation begins.

The rule of thumb: if you cannot describe the correct architectural pattern in code, the agent cannot infer it from your instructions.

## Example

The following shows an `AGENTS.md` file that communicates the hand-built architectural foundation to the coding agent. Without this file, the agent defaults to whatever patterns it encountered most frequently in training — which may not match the team's standards.

```markdown
# AGENTS.md

## Architecture

This project uses Clean Architecture with strict layer separation:
- `app/` — Android Application class and DI setup (Hilt). Do not add business logic here.
- `feature/<name>/` — one module per feature. Each module contains `ui/`, `domain/`, and `data/` packages.
- `core/` — shared utilities, network client, and base classes. No feature code belongs here.

## How to Add a New Feature

Follow the pattern in `feature/auth/` end-to-end:
1. Create `feature/<name>/ui/` — Compose screens and ViewModels only. No repository calls directly from ViewModel; go through use cases.
2. Create `feature/<name>/domain/` — use cases and repository interfaces.
3. Create `feature/<name>/data/` — repository implementations and data sources.
4. Register the Hilt module in `feature/<name>/di/<Name>Module.kt`.

## Before Every Commit

```bash
./gradlew ktlintCheck         # must pass
./gradlew test                # must pass for the feature module
```

Do not commit if either command fails.
```

This file is the boundary between the foundation you built by hand and every agent session that follows. The agent reads it at the start of each session and matches its output against the `feature/auth/` reference implementation.

## Key Takeaways

- Build modularization, DI, navigation, and auth by hand before the agent touches the project.
- Implement a few representative features end-to-end — examples communicate what instructions cannot.
- Document the patterns in AGENTS.md so the agent inherits them across sessions.
- The foundation is not overhead; it is the mechanism that makes reliable agent delegation possible.
- Without a foundation, even a capable agent introduces structural drift that compounds over time.

## Related

- [Session Initialization Ritual](../agent-design/session-initialization-ritual.md)
- [Encode Project Conventions in AGENTS.md Files](../instructions/agents-md-distributed-conventions.md)
- [The Plan-First Loop](plan-first-loop.md)
- [Codebase Readiness for Agents](codebase-readiness.md)
- [Skeleton Projects as Scaffolding](skeleton-projects-as-scaffolding.md)
- [Agent-Driven Greenfield Product Development](agent-driven-greenfield.md)
- [Bootstrapping an Agent-Driven Project from Scratch](bootstrapping-agent-driven-project.md)
