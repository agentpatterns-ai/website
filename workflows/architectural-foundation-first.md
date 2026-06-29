---
title: "Lay the Architectural Foundation by Hand Before Delegating"
description: "Build the structural skeleton and a few representative features yourself before handing a project to an agent — the foundation is the primary investment that makes large-scale delegation safe."
tags:
  - context-engineering
  - agent-design
  - human-factors
  - tool-agnostic
  - workflows
last_reviewed: 2026-06-12
maturity: established
---

# Lay the Architectural Foundation by Hand Before Delegating to Agents

> Build the structural skeleton and a few representative features by hand before delegating — the foundation is the investment that makes large-scale delegation safe.

## The cost of skipping the foundation

Prompt an agent to build a feature or application from scratch with no foundation, and you get output that compiles but drifts from your architectural goals. The agent falls back on the patterns it saw most often in training. Those patterns may not match your team's standards for modularity, layer separation, or naming.

[OpenAI's Sora Android team](https://openai.com/index/shipping-sora-for-android-with-codex/) hit this directly. Their first prompt — "Build the Sora Android app based on the iOS code. Go." — produced code that ran but had structural problems: extra view models, logic placed in the wrong architectural layer, and patterns that did not match the team's standards.

Thoughtworks describes the same effect as ["ambient affordances"](https://martinfowler.com/articles/harness-engineering.html) — structural properties of the codebase that make it easy for the agent to read and work in. Clear module boundaries, a consistent package structure, and established patterns act as implicit constraints. They raise the agent's success rate, and you do not have to restate them in every prompt.

## What the foundation includes

Human engineers should build these by hand:

- Modularization: the module boundaries and package structure
- Dependency injection: the DI setup and how components are wired
- Navigation: the navigation framework and routing conventions
- Authentication: the auth flow and session management
- Representative features: two or three features end-to-end that show the correct patterns

The representative features matter most. They show correct patterns in concrete, runnable form, and the agent can match against them. As the Sora team put it, "We needed to show Codex what's 'correct' on our team" — examples beat instructions.

## What to document

After you build the foundation, document what the agent needs to know to extend it correctly:

- Which architectural layer owns which responsibilities
- How to add a new feature using the existing pattern (point to the example features)
- Mandatory CI commands (linting, formatting) that must run before every commit
- Any constraints that are not visible from the code alone

This documentation belongs in AGENTS.md or equivalent instruction files, not in the prompt. It needs to persist across every agent session.

## The result of getting this right

The Sora team shipped an Android app where 85% of the final codebase was agent-written, with a 99.9% crash-free rate at launch ([OpenAI's Sora for Android writeup](https://openai.com/index/shipping-sora-for-android-with-codex/)). The hand-built foundation made that ratio possible.

The investment in the foundation is not overhead. It is the main control you have over whether agent-written code meets your standards or needs constant correction.

## The tradeoff

Building the foundation yourself takes time upfront. The alternative — prompting without a [skeleton foundation](skeleton-projects-as-scaffolding.md) — produces architectural drift that compounds with every agent session. Correcting structural problems after the fact costs far more than setting up the structure before delegation begins.

The rule of thumb: if you cannot describe the correct architectural pattern in code, the agent cannot infer it from your instructions.

## When this backfires

The steelman for skipping the hand-built foundation is real. For the right project, the upfront investment never pays back, and committing to a structure too early locks in choices you have not yet earned the right to make. Foundation-first is the wrong call when:

- The project is a throwaway prototype or spike. When the goal is to learn whether an idea is viable, the foundation is sunk cost — the code is meant to be discarded. Let the agent build the fastest path to a runnable answer, then rebuild on a foundation only if the idea survives — the [prototype-before-optimizing](prototype-before-optimizing.md) ordering.
- The architecture is genuinely unknown. If you cannot yet describe the correct pattern in code because the problem is unexplored, hand-building a foundation is premature architecture — you risk encoding the wrong invariants and forcing the agent to match a flawed exemplar. Explore first, then codify the foundation once the shape is clear.
- The project is small enough that drift never compounds. A single-module script or a few-hundred-line tool has no layer separation to protect — the same size threshold below which [agent-driven greenfield](agent-driven-greenfield.md) setup stops paying back. The foundation's payoff scales with the volume of agent-written code that has to match it. Below a threshold, the setup cost exceeds the correction cost it prevents.

## Example

The following shows an `AGENTS.md` file that conveys the hand-built architectural foundation to the coding agent. Without this file, the agent falls back on whatever patterns it saw most often in training — which may not match the team's standards.

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
- [Codebase Readiness for Agents](../agent-design/codebase-readiness.md)
- [Skeleton Projects as Scaffolding](skeleton-projects-as-scaffolding.md)
- [Agent-Driven Greenfield Product Development](agent-driven-greenfield.md)
- [Bootstrapping an Agent-Driven Project from Scratch](bootstrapping-agent-driven-project.md)
