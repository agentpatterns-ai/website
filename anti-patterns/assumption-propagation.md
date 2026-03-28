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

The agent forms a wrong interpretation and starts building. The output compiles and passes checks, so each commit deepens investment in the wrong direction. By the time the error surfaces, the fix requires rethinking the entire approach.

Unlike a localized bug, assumption propagation is wrong at the root and consistent everywhere — looking correct until compared against the actual requirement.

## How It Differs from Objective Drift

| Property | [Objective Drift](objective-drift.md) | Assumption Propagation |
|---|---|---|
| Onset | Gradual, after compression or long sessions | Immediate, at task interpretation |
| Cause | Lost context nuance | Wrong initial understanding |
| Internal consistency | Decreasing over time | High throughout |
| Self-correction chance | Possible if constraints are re-injected | Near zero without external check |
| Detection signal | Output format or scope changes | Output looks correct but solves the wrong problem |

## Why Agents Are Susceptible

Agents do not seek clarification or push back on ambiguity ([Osmani, 2025](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)). They pick an interpretation and execute confidently. A human developer would ask a question; an agent writes code. The wrong interpretation is never challenged internally, and coherent output on a faulty premise resists review.

## Detection Signals

- **Output solves a related but different problem.** Polished deliverable, wrong question.
- **Tests pass but cover the wrong behaviour.** Tests encode the agent's interpretation, not the spec.
- **Multiple PRs build on the same wrong foundation.** The error compounds across reviews.
- **Late-stage rework is disproportionate.** The wrong assumption is woven throughout, so correction becomes a rewrite.

## Mitigation Ladder

### Level 1: Require the agent to restate the task

Instruct the agent to write back its understanding before implementation. Review before authorising work.

```markdown
Before writing any code, state:
1. What problem you are solving
2. What the expected input and output look like
3. What constraints apply
```

### Level 2: Spec-first development

The agent implements against a specification file on disk — not its interpretation of a chat message. [Spec-driven development](../workflows/spec-driven-development.md) ensures the spec survives context resets and can be re-read to verify alignment.

### Level 3: Verification gates

Insert a human checkpoint between task interpretation and building. The [plan-first loop](../workflows/plan-first-loop.md) formalises this: plan first, human review, then implementation.

### Level 4: Fresh-context review

A separate agent (or the same agent with a clean context) reviews the output against the spec. No access to the implementer's reasoning means misalignment surfaces without anchoring bias — the fresh-context strategy from the [loop strategy spectrum](../agent-design/loop-strategy-spectrum.md) applied to review.

### Level 5: Automated specification tests

Write tests derived from the spec before implementation. The agent must pass tests it did not write — tests that encode the requirement, not the agent's interpretation.

## Example

**Task:** "Add a `--dry-run` flag to the deploy command that shows what would be deployed without deploying."

**What the agent builds:** A `--dry-run` flag that runs the full deployment pipeline in a sandboxed environment and rolls back afterward. The implementation is thorough — sandbox creation, deployment execution, rollback logic, cleanup. Tests pass. The PR is large and internally consistent.

**What was wanted:** A flag that prints the deployment plan to stdout and exits. No execution, no sandbox, no rollback. Ten lines of code, not two hundred.

The agent assumed "shows what would be deployed" meant "deploys and then shows what happened." Every subsequent decision — sandbox architecture, rollback strategy, cleanup logic — was consistent with that wrong assumption. The fix is not a patch; it is a rewrite.

**With Level 1 mitigation:** The agent restates: "I will implement `--dry-run` by executing the deployment in a sandboxed environment and rolling back." The developer catches the misunderstanding in thirty seconds and corrects it before any code is written.

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
