---
title: "Interactive Clarification for Underspecified Tasks"
term: "Interactive Clarification"
description: "Agents that explore the codebase first and ask targeted clarification questions lift resolution on underspecified tasks by up to 74% over non-interactive runs."
tags:
  - agent-design
  - instructions
  - arxiv
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: emerging
---

# Interactive Clarification for Underspecified Tasks

> Agents that explore the codebase first, then ask targeted questions, lift resolution on underspecified tasks by up to 74% over non-interactive runs.

## The problem: agents assume instead of asking

Given incomplete instructions, agents fill the gaps with assumptions. They produce output that looks correct but solves the wrong problem. This is [assumption propagation](../anti-patterns/assumption-propagation.md), the default behavior across models. Knowing when to ask is itself an open research problem. Estimating the value of a clarifying question means reasoning over the space of possible user intents, not just the immediate input ([Zhang and Choi, NAACL 2025](https://arxiv.org/abs/2311.09469)).

The Ambig-SWE benchmark tested this by creating underspecified variants of real GitHub issues. Interactivity improved resolution rates by up to 74% on underspecified tasks. But models consistently struggled to detect underspecification without explicit prompting ([Vijayvargiya et al., ICLR 2026](https://arxiv.org/abs/2502.13069)).

## Two types of missing information

The research identified two categories, each needing a different strategy:

| Type | What's Missing | Example |
|------|---------------|---------|
| Informational | Expected behavior, error nature, acceptance criteria | "Fix the auth bug" — which bug? What should correct behavior look like? |
| Navigational | File locations, module boundaries, where to change | "Update the config" — which config file, in which service? |

Codebase exploration resolves navigational gaps, including [domain-scoped parallel localization](domain-scoped-parallel-localization.md) when the change spans subsystems. Informational gaps need the user — no amount of code reading reveals expected behavior.

## Exploration first, questions second

The effective strategy is not more questions. It is fewer, better ones.

Claude Sonnet 4 asked 50% fewer questions than Qwen 3 Coder but achieved comparable extraction. Sonnet explored the codebase first, resolving navigational ambiguity independently, then asked only about informational gaps requiring human knowledge ([Vijayvargiya et al., ICLR 2026](https://arxiv.org/abs/2502.13069)).

```mermaid
flowchart LR
    A[Receive task] --> B[Explore codebase]
    B --> C{Gaps remaining?}
    C -- Navigational --> B
    C -- Informational --> D[Ask targeted question]
    C -- None --> E[Execute]
    D --> F[Integrate answer]
    F --> C
```

The anti-pattern is asking questions the agent could answer by reading code. Reserve questions for information only the user holds: expected behavior, business rules, design intent.

## Designing for detection

Detecting underspecification before committing to an approach is the hardest part. Three interventions help:

Explicit detection prompt: add to system instructions: "Before implementing, identify ambiguous or missing requirements. List what you know, what you're assuming, and what you need confirmed." This improved detection accuracy in benchmark evaluation ([Vijayvargiya et al., ICLR 2026](https://arxiv.org/abs/2502.13069)).

Assumption surfacing: require the agent to state assumptions before proceeding: "I'm assuming the error should return a 404 rather than a 500. Correct me if wrong."

Plan-phase review: the [plan-first loop](../../workflows/plan-first-loop.md) surfaces underspecification — reviewing a plan reveals gaps that reviewing code would miss.

## When to block versus when to surface

Not every gap needs a blocking question. Decide on the cost of being wrong:

| Reversibility | Action |
|--------------|--------|
| Easily reversible (formatting, variable naming) | State the assumption, proceed |
| Costly to reverse (API contract, data migration) | Ask before proceeding |
| Irreversible (destructive operations, published interfaces) | Block until confirmed |

This maps to the [agent pushback protocol](agent-pushback-protocol.md) — pushback gates on request quality, clarification gates on information completeness. When [steering a running agent](steering-running-agents.md) mid-task with underspecified follow-ups, the same heuristic applies.

## Performance reality

The 74% improvement is the peak result (Claude Sonnet 3.5, synthetic underspecification). Caveats:

- Stronger models show compounding gains — Sonnet 4 recovered 89% of fully-specified performance versus Sonnet 3.5's 80%, suggesting capability shifts the bottleneck from detection to integration ([Vijayvargiya et al., ICLR 2026](https://arxiv.org/abs/2502.13069))
- Some models showed "complete non-responsiveness to interaction prompts" — following rigid protocols regardless of input ([Vijayvargiya et al., ICLR 2026](https://arxiv.org/abs/2502.13069))
- High extraction does not guarantee success — integrating answers matters more than asking the right questions

## Example

A user submits: "Fix the authentication bug in the API." The agent applies exploration-first clarification:

1. Explore: search for auth-related files, recent error logs, and failing tests. The agent finds that `auth/token_validator.py` has a recent regression where expired tokens bypass validation.
2. Resolve the navigational gap: identify the relevant file and test without asking the user.
3. Detect the informational gap: the fix could either reject expired tokens with a 401 or silently refresh them. This is a business rule the code does not reveal.
4. Ask one targeted question: "The token validator currently accepts expired tokens. Should expired tokens return a 401 requiring re-login, or should the API attempt a silent refresh?"
5. Integrate and execute: the user confirms 401 behavior, and the agent implements the fix with a test covering the expired-token path.

The agent resolved the navigational ambiguity (which file, which bug) independently and asked only the informational question that required human judgment.

## Key Takeaways

- Agents default to assuming — explicit instruction to detect underspecification is required
- Explore first to resolve navigational gaps; ask only about informational gaps requiring human knowledge
- Fewer, targeted questions outperform broad ones — integration quality matters more than extraction quantity
- Match strategy to reversibility: surface assumptions for low-cost decisions, block for high-cost ones
- Stronger models gain more from interactivity — the bottleneck shifts from detection to integration as capability scales

## Related

- [Assumption Propagation](../anti-patterns/assumption-propagation.md) — the failure mode when agents do not ask
- [Agent Pushback Protocol](agent-pushback-protocol.md) — structured agent-initiated clarification on request quality
- [Plan-First Loop](../../workflows/plan-first-loop.md) — plan review as a lightweight underspecification check
- [Steering Running Agents](steering-running-agents.md) — mid-run redirection where underspecified follow-ups require the same clarification heuristics
- [Spec-Driven Development](../../workflows/spec-driven-development.md) — upstream approach to eliminating ambiguity before agent execution
- [TDD for Agent Development](../../verification/tdd-agent-development.md) — tests as unambiguous executable specification
- [Issue Requirements Preprocessing](issue-requirements-preprocessing.md) — automated clarification of issue text before execution begins
- [Semantic Collapse Under Underspecified Prompts](../anti-patterns/semantic-collapse.md) — why you cannot detect underspecification by sampling for output variance: the model collapses onto one confident, wrong reading
- [Stated-Understanding Checks](../../human/stated-understanding-checks.md) — the reverse direction, where the developer states the assumption and the agent checks it
