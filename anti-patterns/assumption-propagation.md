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

The agent forms a wrong interpretation and starts building. Output compiles and passes checks, so each commit deepens investment in the wrong direction. By the time the error surfaces, the fix requires rethinking the entire approach.

Unlike a localized bug, assumption propagation is wrong at the root — looking correct until compared against the actual requirement.

## How It Differs from Objective Drift

| Property | [Objective Drift](objective-drift.md) | Assumption Propagation |
|---|---|---|
| Onset | Gradual, after compression or long sessions | Immediate, at task interpretation |
| Cause | Lost context nuance | Wrong initial understanding |
| Internal consistency | Decreasing over time | High throughout |
| Self-correction chance | Possible if constraints are re-injected | Near zero without external check |
| Detection signal | Output format or scope changes | Output looks correct but solves the wrong problem |

## Why Agents Are Susceptible

Agents do not seek clarification or push back on ambiguity ([Osmani, 2025](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)). Training optimises for complete, helpful output — pausing to surface uncertainty scores lower in human preference data than executing immediately. The model fills gaps with the most plausible interpretation from training data rather than flagging what it does not know, and coherent output on a faulty premise resists review.

The mechanism is training-driven: RLHF reward models are biased toward high-confidence responses — the model is rewarded for authoritative output, not for surfacing uncertainty ([Leng et al., ICLR 2025](https://arxiv.org/abs/2410.09724)). On underspecified tasks, models make unwarranted assumptions rather than ask clarifying questions, even when interaction would improve outcomes by up to 74% ([Mohajer Ansari et al., ICLR 2026](https://arxiv.org/abs/2502.13069)).

The root cause is architectural: current coding agents are optimised for autonomous execution rather than interaction. Underspecification detection is not decoupled from code generation, so the agent treats every instruction as complete and immediately actionable — even when it is not ([Edwards & Schuster, 2026](https://arxiv.org/abs/2603.26233)).

## Detection Signals

- **Output solves a related but different problem.** Polished deliverable, wrong question.
- **Tests pass but cover the wrong behaviour.** Tests encode the agent's interpretation, not the spec.
- **Multiple PRs share the same wrong foundation.** The error compounds across reviews.
- **Late-stage rework is disproportionate.** The wrong assumption is woven throughout — correction becomes a rewrite.

## Mitigation Ladder

### Level 1: Require the agent to restate the task

Before implementation, the agent writes back its understanding. Review before authorising work.

```markdown
Before writing any code, state:
1. What problem you are solving
2. What the expected input and output look like
3. What constraints apply
```

### Level 2: Spec-first development

The agent implements against a specification file on disk — not a chat message. [Spec-driven development](../workflows/spec-driven-development.md) survives context resets; the spec can be re-read to verify alignment.

### Level 3: Verification gates

Human checkpoint between interpretation and building. The [plan-first loop](../workflows/plan-first-loop.md) formalises this: plan, human review, then implementation.

### Level 4: Fresh-context review

A separate agent reviews output against the spec with no access to the implementer's reasoning. Misalignment surfaces without anchoring bias — see [loop strategy spectrum](../agent-design/loop-strategy-spectrum.md).

### Level 5: Automated specification tests

Write tests derived from the spec before implementation. The agent passes tests it did not write — tests that encode the requirement, not its interpretation.

## Example

**Task:** "Add a `--dry-run` flag to the deploy command that shows what would be deployed without deploying."

**What the agent builds:** A `--dry-run` flag that runs the full deployment pipeline in a sandboxed environment and rolls back afterward. The implementation is thorough — sandbox creation, deployment execution, rollback logic, cleanup. Tests pass. The PR is large and internally consistent.

**What was wanted:** A flag that prints the deployment plan to stdout and exits. No execution, no sandbox, no rollback. Ten lines of code, not two hundred.

The agent assumed "shows what would be deployed" meant "deploys and then shows what happened." Every subsequent decision — sandbox architecture, rollback strategy, cleanup logic — was consistent with that wrong assumption. The fix is not a patch; it is a rewrite.

**With Level 1 mitigation:** The agent restates: "I will implement `--dry-run` by executing the deployment in a sandboxed environment and rolling back." The developer catches the misunderstanding in thirty seconds and corrects it before any code is written.

## When This Backfires

Mitigation adds cost. The ladder is not worth climbing when:

- **The spec is already precise.** Requiring a restatement of an unambiguous requirement adds friction with no upside. Teams that apply Level 1 universally train developers to rubber-stamp summaries rather than read them.
- **The task is low-stakes and reversible.** A wrong first attempt on a throwaway script is cheaper to discard than to prevent with upfront checks.
- **Fast-path workflows have no reviewer.** Agentic pipelines running in CI or batch mode have no human present to read a restatement. A checkpoint that nobody reviews gives false confidence without catching errors.
- **Deliberate ambiguity is intentional.** Forcing restatement collapses design decisions that should stay open until implementation reveals constraints.
- **Requirements drift mid-task.** A Level 1 restatement goes stale if the spec changes during implementation, giving false confidence that alignment holds.
- **The spec itself is wrong.** Spec-first development (Level 2) catches interpretation errors, not requirement errors. An agent that propagates faithfully against a wrong spec still produces a wrong result — upstream review of the spec is a separate problem.

Propagation risk scales with autonomy: in tightly supervised flows a wrong assumption surfaces quickly, but in long agentic runs or multi-agent pipelines the error compounds for tens of steps before any human sees output. Apply the ladder when the cost of a wrong direction exceeds the cost of the check, and calibrate oversight to match the autonomy granted.

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
