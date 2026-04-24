---
title: "Assumption Propagation: Compounding Agent Misunderstandings"
description: "The agent misunderstands a requirement early and builds on the faulty premise, reinforcing the wrong assumption until the error is too expensive to unwind."
tags:
  - agent-design
  - testing-verification
  - source:osmani-80-percent
---

# Assumption Propagation

> The agent misunderstands a requirement early and builds on the faulty premise — each step reinforcing the wrong assumption until the error is too expensive to unwind.

## What It Looks Like

The agent forms a wrong interpretation and starts building. Output compiles and passes checks, deepening investment in the wrong direction. The error is at the root — looking correct until compared against the actual requirement.

## How It Differs from Objective Drift

| Property | [Objective Drift](objective-drift.md) | Assumption Propagation |
|---|---|---|
| Onset | Gradual, long sessions | Immediate, at interpretation |
| Cause | Lost context | Wrong initial understanding |
| Consistency | Decreasing | High throughout |
| Self-correction | Possible | Near zero without external check |
| Signal | Format or scope drift | Solves the wrong problem |

## Why Agents Are Susceptible

Agents do not seek clarification or push back on ambiguity ([Osmani, 2025](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)). RLHF reward models favour high-confidence answers over surfacing uncertainty ([Leng et al., ICLR 2025](https://arxiv.org/abs/2410.09724)); on underspecified tasks, models assume rather than ask — even when interaction would improve outcomes by up to 74% ([Vijayvargiya et al., ICLR 2026](https://arxiv.org/abs/2502.13069)).

Architecture compounds this: coding agents optimise for autonomous execution and do not decouple underspecification detection from code generation, so every instruction is treated as actionable ([Edwards & Schuster, 2026](https://arxiv.org/abs/2603.26233)).

## Detection Signals

- **Polished deliverable, wrong question.** Output solves a related but different problem.
- **Tests pass but cover the wrong behaviour.** Tests encode the agent's interpretation, not the spec.
- **Multiple PRs share the same wrong foundation.** The error compounds across reviews.
- **Late-stage rework requires a rewrite, not a patch.**

## Mitigation Ladder

### Level 1: Restate the task

The agent writes back its understanding before coding; review catches misinterpretation in seconds.

```markdown
Before writing any code, state:
1. What problem you are solving
2. What the expected input and output look like
3. What constraints apply
```

### Level 2: Spec-first development

Implement against a spec file on disk, not a chat message. [Spec-driven development](../workflows/spec-driven-development.md) survives context resets.

### Level 3: Verification gates

Human checkpoint between interpretation and building — the [plan-first loop](../workflows/plan-first-loop.md).

### Level 4: Fresh-context review

A separate agent reviews output against the spec, blind to the implementer's reasoning. See [loop strategy spectrum](../agent-design/loop-strategy-spectrum.md).

### Level 5: Spec-derived tests

Tests written from the spec before implementation — the agent passes tests it did not write, encoding the requirement, not its interpretation.

## Example

**Task:** "Add a `--dry-run` flag to the deploy command that shows what would be deployed without deploying."

**What the agent builds:** A `--dry-run` flag that runs the full deployment pipeline in a sandboxed environment and rolls back afterward. The implementation is thorough — sandbox creation, deployment execution, rollback logic, cleanup. Tests pass. The PR is large and internally consistent.

**What was wanted:** A flag that prints the deployment plan to stdout and exits. No execution, no sandbox, no rollback. Ten lines of code, not two hundred.

The agent assumed "shows what would be deployed" meant "deploys and then shows what happened." Every subsequent decision — sandbox architecture, rollback strategy, cleanup logic — was consistent with that wrong assumption. The fix is not a patch; it is a rewrite.

**With Level 1 mitigation:** The agent restates: "I will implement `--dry-run` by executing the deployment in a sandboxed environment and rolling back." The developer catches the misunderstanding in thirty seconds and corrects it before any code is written.

## When This Backfires

Mitigation adds cost. The ladder is not worth climbing when:

- **The spec is precise.** Universal Level 1 trains reviewers to rubber-stamp summaries.
- **The task is throwaway.** A wrong first attempt is cheaper to discard than prevent.
- **No reviewer is present.** CI or batch pipelines with nobody reading a restatement give false confidence.
- **Ambiguity is deliberate.** Early restatement collapses design decisions that should stay open.
- **Requirements drift mid-task.** The restatement goes stale when the spec changes.
- **The spec itself is wrong.** Level 2 catches interpretation errors, not requirement errors.

Apply the ladder when the cost of a wrong direction exceeds the cost of the check.

Concrete failure modes observed in the wild:

- **Spec-first on bounded changes inflates overhead.** Spec-kit on a date-display feature produced 8 files and 1,300+ lines; Kiro turned a small bug fix into four user stories with sixteen acceptance criteria ([Fowler, 2025](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)).
- **Specs frozen before discovery lock in the wrong premise.** Prototype, then spec ([Augment Code, 2026](https://www.augmentcode.com/guides/what-is-spec-driven-development)).
- **Checkpoints at every step become rubber-stamps** once volume exceeds what the reviewer can read ([Faros AI, 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026)).

## Related

- [Objective Drift](objective-drift.md)
- [Spec-Driven Development](../workflows/spec-driven-development.md)
- [Plan-First Loop](../workflows/plan-first-loop.md)
- [Incremental Verification](../verification/incremental-verification.md)
- [The Yes-Man Agent](yes-man-agent.md)
- [The Implicit Knowledge Problem](implicit-knowledge-problem.md)
- [Trust Without Verify](trust-without-verify.md)
- [Spec Complexity Displacement](spec-complexity-displacement.md)
- [Context Poisoning](context-poisoning.md)
- [Demo-to-Production Gap](demo-to-production-gap.md)
- [Pattern Replication Risk](pattern-replication-risk.md)
- [Abstraction Bloat](abstraction-bloat.md)
- [Copy-Paste Agent](copy-paste-agent.md)
