---
title: "The LLM Laziness Deficit Fallacy: Restraint Comes From Harness, Not Instruction"
description: "The belief that agents can be instructed into the human virtue of laziness. LLMs pay no time cost for code, so restraint must come from objective harness gates — diff caps, complexity budgets, deletion targets — not from 'be concise' prompts."
tags:
  - instructions
  - workflows
  - tool-agnostic
aliases:
  - laziness deficit
  - LLM laziness virtue
  - effort-cost asymmetry
---

# The LLM Laziness Deficit Fallacy

> The belief that agents can be instructed into the human virtue of laziness. Because LLMs pay no time cost for the code they write, restraint must come from objective harness gates — not from attitude prompts.

## The Fallacy

Larry Wall named laziness a programmer virtue: the drive to produce crisp abstractions so future you spends less time on clunky ones. Bryan Cantrill's ["The peril of laziness lost"](https://bcantrill.dtrace.org/2026/04/12/the-peril-of-laziness-lost/) identifies the cost function that produces it: *"The best engineering is always borne of constraints, and the constraint of our time places limits on the cognitive load of the system that we're willing to accept."*

LLMs do not pay that cost. *"Work costs nothing to an LLM. LLMs do not feel a need to optimize for their own (or anyone's) future time, and will happily dump more and more onto a layercake of garbage"* ([Cantrill](https://bcantrill.dtrace.org/2026/04/12/the-peril-of-laziness-lost/), via [Simon Willison](https://simonwillison.net/2026/Apr/13/bryan-cantrill/)).

The fallacy is the response: add "be concise," "prefer simplicity," or "write minimum code" to the system prompt and expect restraint to follow. The asymmetry is in the cost function, not the attitude — and prompts do not change cost functions.

## Why Instruction Alone Fails

Attitude instructions have a documented backfire mode. Cursor found that telling a Codex agent to "preserve tokens" caused it to refuse substantive work rather than execute more cheaply ([Cursor](https://cursor.com/blog/codex-model-harness)). See [Token Preservation Backfire](../anti-patterns/token-preservation-backfire.md).

Empirical signal without restraint gates:

- Median PR size grew 33% during 2025 (57 → 76 lines) as AI adoption rose; "too large" is a top-three PR rejection reason ([Xiao et al., 2025](https://arxiv.org/html/2509.14745v1)).
- Lines of code rose 76% and cognitive complexity 39% in agent-assisted repositories ([Agile Pain Relief](https://agilepainrelief.com/blog/ai-generated-code-quality-problems/)).
- Agents scaffold "1,000 lines where 100 would suffice" ([Addy Osmani](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)).

## The Correct Mental Model

Human laziness is an emergent property of time scarcity. The agent equivalent must be an emergent property of the harness — objective constraints applied where output meets a measurable gate.

Three gate categories bind:

- **Diff-size budgets** — hard limits per change, split enforced by tooling. Large PRs are a top-three rejection cause ([Xiao et al., 2025](https://arxiv.org/html/2509.14745v1)); a cap forces consolidation because the tool rejects sprawl.
- **Complexity budgets** — cyclomatic complexity, function length, and duplication thresholds in CI detect bloat mechanically ([Addy Osmani](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)).
- **Deletion targets** — a "delete more than you add" rule, or periodic garbage-collection passes. Martin Fowler documents this as harness-engineered cleanup ([Fowler/Böckeler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)).

Each is an objective constraint the agent can observe. The prompt does not ask for laziness; the environment makes sprawl expensive.

## Where Restraint Gates Are Wrong

Gates are not universal:

- **Exploratory generation inside a harness** — when the harness curates and discards intermediate output, per-call gates add latency without quality gain ([venture-bystander](https://venture-bystander.ghost.io/garry-tan-loc-maxxing-and-code-abundance/)): intermediate code is search, not product.
- **Known-growth systems** — when a factory or registry is on the near-term roadmap, a diff cap forces a later refactor. Scope gates to the current task.
- **Small single-author projects** — one person's cognitive-load budget is their own; layered review adds process without addressing debt that may never be paid.

The operative question is not "are agents lazy enough?" but "does my harness impose a cost the agent can observe?"

## Example

**Applying the fallacy — attitude instruction without gates:**

The team adds to `CLAUDE.md`: *"Prefer simple solutions. Do not over-engineer. Write minimum code."* An agent ships a notification feature: one function requested, six classes delivered, plus a rate limiter and retry policy nobody asked for ([Fowler/Garg case study](https://martinfowler.com/articles/reduce-friction-ai/design-first-collaboration.html)). PR merges. Next week, the same prompt produces another 800-line change. The instruction was read; the cost function was unchanged.

**Avoiding the fallacy — harness gates that enforce the constraint:**

The team removes the "be concise" instruction and installs three gates:

- CI fails any PR over 400 changed lines without the `large-change` label and a linked design doc.
- Cyclomatic complexity per function capped at 10; CI rejects over.
- A weekly `cleanup` agent runs and must produce net-negative diffs.

The same agent hits the 400-line cap on the first attempt, splits the change, and prunes two speculative classes to fit. The restraint is a property of the pipeline, not the prompt.

## Key Takeaways

- Human laziness is produced by time scarcity; LLMs have no equivalent cost function, so instruction alone cannot reproduce it.
- Attitude prompts like "be concise" either do nothing or backfire by changing *whether* the agent works, not *how*.
- Restraint that binds is objective and external: diff-size caps, complexity budgets, deletion targets, review gates.
- Gates are not universal — exploratory harness calls, known-growth systems, and small single-author projects have different constraints.

## Related

- [Abstraction Bloat](../anti-patterns/abstraction-bloat.md) — the observable output pattern this fallacy explains
- [Token Preservation Backfire](../anti-patterns/token-preservation-backfire.md) — why naive efficiency instructions make agents do less, not better
- [Effortless AI Fallacy](../anti-patterns/effortless-ai-fallacy.md) — the adjacent belief that AI should work without effort
- [Harness Engineering](../agent-design/harness-engineering.md) — the environment-design frame for agent constraints
- [Deterministic Guardrails](../verification/deterministic-guardrails.md) — mechanical enforcement of constraints prompts cannot hold
- [Hooks for Enforcement vs Prompts for Guidance](../verification/hooks-vs-prompts.md) — when to mechanise a constraint
- [Instruction Polarity](../instructions/instruction-polarity.md) — positive constraints over negative attitude rules
