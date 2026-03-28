---
title: "Encode Project Conventions in Distributed AGENTS.md Files"
description: "Encode team-specific patterns, style rules, and tooling requirements in AGENTS.md files so every agent session inherits consistent project conventions."
aliases:
  - Distributed Conventions
  - AGENTS.md Distributed Conventions
tags:
  - context-engineering
  - instructions
---

# Encode Project Conventions in Distributed AGENTS.md Files

> Capture team-specific patterns, style rules, and tooling requirements in AGENTS.md files throughout the codebase so every agent session inherits consistent guidance.

!!! info "Also known as"
    Distributed Conventions, AGENTS.md Distributed Conventions. For the complementary pattern on **what** to put in AGENTS.md (a pointer map, not an encyclopedia), see [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md).

## The Stateless Agent Problem

Each agent session starts cold. Without persistent conventions encoded in the codebase, the agent defaults to its training-data patterns: common tooling, conventional naming, generic architectural choices. These defaults are frequently wrong for a specific team's standards.

[OpenAI's Sora Android team](https://openai.com/index/shipping-sora-for-android-with-codex/) observed this directly. Without explicit conventions, Codex introduced extra view models, pushed logic into incorrect architectural layers, and ignored CI requirements. The fix was distributing AGENTS.md files that encoded the team's standards — including a mandatory `./gradlew detektFix` before every commit.

## What to Encode

AGENTS.md files at each scope should capture conventions most likely to be violated:

**Repository root** — standards that apply everywhere:

- Mandatory CI commands (linting, formatting, test runner invocations)
- Naming conventions that deviate from language defaults
- Prohibited patterns and why (e.g., "do not use X, we use Y because Z")
- How to run the project locally

**Service or module directory** — standards specific to that area:

- Architecture layer responsibilities in that module
- Different lint rules or build commands from the project default
- Module-specific testing conventions

**Global agent config** — multi-repo context:

- Where local repositories live (for agents operating across multiple repos)
- Cross-repo conventions and personal workflow preferences

## Have the Agent Write and Maintain the Files

[The Sora team](https://openai.com/index/shipping-sora-for-android-with-codex/) had Codex create and maintain its own AGENTS.md files. The agent surfaces what context it actually needs in practice, not what the human guesses in advance [unverified].

To bootstrap this:

1. Ask the agent to attempt a task and note what it had to ask about or look up
2. Ask the agent to encode those learnings in the appropriate AGENTS.md file
3. Validate the encoded conventions before committing them

## What Not to Encode

AGENTS.md files should contain instructions, not documentation. Avoid:

- Architecture diagrams or extended explanations — link to documentation files instead
- Knowledge the agent can discover from the codebase (types, structure, tests)
- Task-specific context that belongs in a prompt
- Instructions that duplicate content already in code comments

Every line in an AGENTS.md file is loaded into context before task work begins [unverified — behavior varies by tool]. Each unnecessary line consumes context budget that could be used for implementation.

## Mandatory CI Commands as Conventions

Mandatory CI commands in AGENTS.md are high-value. Agents that skip linting or formatting introduce expensive build failures. An explicit instruction — "run `./gradlew detektFix` before committing" — converts an advisory reminder into a mandatory step.

This works best paired with a pre-commit hook: the instruction makes the agent comply; the hook catches any bypass.

## Multi-Repo Navigation

For agents operating across multiple repositories, a global config file — `~/.codex/AGENTS.md` or equivalent — should document where local repos are checked out, which repo serves which purpose, and how to navigate between them.

## Example

This example shows a root-level `AGENTS.md` for an Android project alongside a module-level override, demonstrating how distributed convention files prevent the architectural drift described above.

```markdown
# AGENTS.md — repository root

## Mandatory CI steps (run before every commit)
./gradlew detektFix
./gradlew test

## Package manager
Use Gradle only. Do not invoke Maven or the Android Studio GUI.

## Naming conventions
- ViewModel suffix required for all ViewModel classes (e.g. `CheckoutViewModel`)
- Repository suffix required for data-layer classes (e.g. `OrderRepository`)
- Do NOT use `Manager` as a suffix — use `Coordinator`, `Service`, or `Handler` instead

## Prohibited patterns
- Do not push business logic into Fragment or Activity classes; it belongs in the ViewModel
- Do not use `GlobalScope` for coroutines; use a scoped `CoroutineScope` tied to the ViewModel lifecycle
```

```markdown
# AGENTS.md — feature/checkout/

## Architecture
This module follows strict MVVM. The layers are:
  CheckoutFragment → CheckoutViewModel → OrderRepository → OrderApi

Do not add intermediate layers (e.g. UseCases) without a team decision.

## Tests
Run `./gradlew :feature:checkout:test` after any change in this directory.
Integration tests live in `feature/checkout/src/androidTest/`.
```

The root file encodes repo-wide enforcement rules (CI commands, naming, prohibited patterns). The module file adds checkout-specific architecture guidance. An agent opening a file in `feature/checkout/` picks up both layers, preventing it from introducing extra ViewModel abstractions or pushing logic into the wrong layer.

## Key Takeaways

- Every agent session starts cold; AGENTS.md files are the mechanism for persistent conventions.
- Include mandatory CI commands — they convert advisory prompts into enforceable steps.
- Have the agent help write AGENTS.md files; it surfaces what context is actually needed.
- Keep files short and instruction-focused; link to documentation rather than embedding it.
- Multi-repo agents need a global config documenting repository layout.

## Unverified Claims

- The agent surfaces what context it actually needs in practice, not what the human guesses it needs in advance [unverified]
- Every line in an AGENTS.md file is loaded into context before task work begins [unverified — behavior varies by tool]

## Related

- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md) — complementary pattern covering *what* to put in AGENTS.md
- [AGENTS.md Design Patterns: Commands, Boundaries, Personas](agents-md-design-patterns.md)
- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [Layer Agent Instructions by Specificity](layered-instruction-scopes.md)
- [Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels](hierarchical-claude-md.md)
- [Project Instruction File Ecosystem](instruction-file-ecosystem.md)
- [Seeding Agent Context: Breadcrumbs in Code](../context-engineering/seeding-agent-context.md)
- [Convention Over Configuration for Agent Workflows](convention-over-configuration.md)
- [Content Exclusion Gap in Agent Systems](content-exclusion-gap.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Event-Driven System Reminders](event-driven-system-reminders.md)
- [@import Composition Pattern for Instruction Files](import-composition-pattern.md)
- [Standards as Agent Instructions](standards-as-agent-instructions.md)
- [Evaluating AGENTS.md Context Files](evaluating-agents-md-context-files.md)
