---
title: "Boring Technology Bias: When Agents Recommend by Popularity"
description: "LLMs recommend tools and frameworks proportional to training data frequency, not fitness for the problem. Popular beats optimal by default."
aliases:
  - frequency prior
tags:
  - agent-design
  - instructions
---

# Boring Technology Bias

> LLMs recommend tools and frameworks proportional to training data frequency, not fitness for the problem. Popular beats optimal by default.

## The Problem

When you ask an agent "what should I use for X?", the answer reflects training frequency. Greenfield recommendations cluster around a small set of dominant tools — GitHub Actions for CI/CD, Stripe for payments, shadcn/ui for components, Vercel for deployment — regardless of whether they fit the project. Less-popular alternatives receive lower confidence scores or are omitted entirely.

This is a frequency prior, not a reasoning failure. More training examples of popular tools means higher confidence. Greenfield projects converge on the same narrow stack regardless of requirements.

## Two Distinct Risks

The bias manifests differently by interaction mode:

```mermaid
flowchart LR
    A[Ask agent:<br/>'What should I use?'] --> B[Recommendation bias<br/>Defaults to training frequency]
    C[Tell agent:<br/>'Use this tool'] --> D[Execution capability<br/>Works fine with docs in context]
    B -->|Unquestioned| E[Suboptimal stack adopted]
    D -->|Context provided| F[Correct implementation]

    style B fill:#c0392b,color:#fff
    style D fill:#27ae60,color:#fff
```

**Recommendation bias** — what the agent suggests when asked to choose; skewed toward training frequency.

**Execution capability** — what the agent builds when told what to use; less biased with documentation in context.

Agents are worse advisors than implementers.

## The Feedback Loop

```mermaid
flowchart TB
    A[Agent recommends Tool X] --> B[More developers adopt Tool X]
    B --> C[More Tool X content in training data]
    C --> D[Agent recommends Tool X with higher confidence]
    D --> A

    style A fill:#c0392b,color:#fff
```

Training data representation — not product quality — drives greenfield adoption.

## Concrete Failure: Deprecated API Death Spiral

Google's `google-generativeai` Python library was deprecated in favor of `google-genai`. Models trained on the old library generate non-functional code using the deprecated `GenerativeModel()` pattern. Developers conclude the API is broken and switch to competitors — never producing correct-pattern content, starving training data, and deepening the bias. Documented in [googleapis/python-genai#1606](https://github.com/googleapis/python-genai/issues/1606).

## Mitigation

Pin technology choices in project instruction files to override training data defaults.

```markdown
# CLAUDE.md (or AGENTS.md, copilot-instructions.md)

## Technology Stack
- Deployment: AWS CDK (not Vercel/Railway)
- CI/CD: GitLab CI (not GitHub Actions)
- Payments: Paddle (not Stripe)
- Components: Radix primitives (not shadcn/ui)

## Rules
- Do not suggest alternative tools unless asked
- When generating examples, use the stack above
```

For niche tools, provide seed examples. Few-shot examples compensate for limited training coverage: agents that receive 3-5 representative examples of a niche API produce correct implementations significantly more often than with zero-shot prompting ([arxiv.org/abs/2406.09834](https://arxiv.org/abs/2406.09834)).

| Mitigation | Mechanism |
|---|---|
| Pin stack in instruction files | Overrides default recommendations |
| Provide seed examples for niche tools | Compensates for limited training data |
| Add compiler/linter validation loops | Catches deprecated API usage automatically |
| Treat tool recommendations like a junior dev's | Verify reasoning, don't accept defaults |

## When This Backfires

Overspecifying the technology stack in instruction files creates its own problems:

- **Stack lock-in**: pinning every tool prevents agents from suggesting a better fit when requirements change mid-project.
- **Onboarding friction**: new contributors must learn the project's overridden defaults before the agent behaves predictably.
- **False confidence**: a pinned stack still requires human review — agents implement the pinned tool incorrectly if their training coverage for it is thin, producing confident but broken code.
- **Maintenance burden**: locked stacks drift as pinned libraries release breaking changes, and agents are not notified — the instruction file becomes a source of stale guidance.

Use instruction files to override defaults for non-negotiable choices (regulatory requirements, existing infrastructure) rather than as a blanket constraint on every dependency.

## Related

- [Framework-First Agent Development](framework-first.md) — reaching for frameworks too early (distinct from training-data selection bias)
- [Pattern Replication Risk](pattern-replication-risk.md) — agents absorb and reproduce deprecated APIs and stale patterns from existing codebases, compounding training-data bias
- [Trust Without Verify](trust-without-verify.md) — accepting agent output without verification
- [Instruction File Ecosystem](../instructions/instruction-file-ecosystem.md) — the mechanism for overriding agent defaults
- [CLAUDE.md Convention](../instructions/claude-md-convention.md) — pin technology choices in Claude Code's project instruction file
- [Agent-Driven Greenfield Product Development](../workflows/agent-driven-greenfield.md)
