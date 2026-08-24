---
title: "Assumption Propagation: Compounding Agent Misunderstandings"
term: "Assumption Propagation"
description: "The agent misunderstands a requirement early and builds on the faulty premise, reinforcing the wrong assumption until the error is too expensive to unwind."
tags:
  - agent-design
  - testing-verification
  - tool-agnostic
  - anti-pattern
last_reviewed: 2026-06-12
maturity: established
---

# Assumption Propagation: Compounding Agent Misunderstandings

> The agent misunderstands a requirement early and builds on the faulty premise, reinforcing the wrong assumption until the error is too expensive to unwind.

Related lesson: [Objective Drift](https://learn.agentpatterns.ai/anti-patterns/objective-drift/) — this concept features in a hands-on lesson with quizzes.

## What it looks like

The agent forms a wrong interpretation and starts building. The output compiles and passes checks, which deepens investment in the wrong direction. The error sits at the root. It looks correct until you compare it against the actual requirement.

## How it differs from objective drift

| Property | [Objective Drift](objective-drift.md) | Assumption Propagation |
|---|---|---|
| Onset | Gradual, long sessions | Immediate, at interpretation |
| Cause | Lost context | Wrong initial understanding |
| Consistency | Decreasing | High throughout |
| Self-correction | Possible | Near zero without external check |
| Signal | Format or scope drift | Solves the wrong problem |

## Why agents are susceptible

Agents do not seek clarification or push back on ambiguity ([Osmani, 2025](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)). RLHF reward models favor high-confidence answers over surfaced uncertainty ([Leng et al., ICLR 2025](https://arxiv.org/abs/2410.09724v2)). On underspecified tasks, models assume rather than ask, even when asking would improve outcomes by up to 74% ([Vijayvargiya et al., ICLR 2026](https://arxiv.org/abs/2502.13069v3)).

Architecture compounds this. Coding agents optimize for autonomous execution. They do not separate underspecification detection from code generation, so they treat every instruction as actionable ([Edwards & Schuster, 2026](https://arxiv.org/abs/2603.26233)).

## Detection signals

- The deliverable looks polished but answers the wrong question. It solves a related but different problem.
- Tests pass but cover the wrong behavior. They encode the agent's interpretation, not the spec — a gap [spec-driven development](../../workflows/spec-driven-development.md) closes by deriving tests from the spec.
- Multiple PRs share the same wrong foundation, so the error compounds across reviews.
- Late-stage rework needs a rewrite, not a patch.

## Mitigation ladder

### Level 1: Restate the task

The agent writes back its understanding before coding. Review catches the misinterpretation in seconds.

```markdown
Before writing any code, state:
1. What problem you are solving
2. What the expected input and output look like
3. What constraints apply
```

### Level 2: Spec-first development

Implement against a spec file on disk, not a chat message. [Spec-driven development](../../workflows/spec-driven-development.md) survives context resets.

### Level 3: Verification gates

Put a human checkpoint between interpretation and building — the [plan-first loop](../../workflows/plan-first-loop.md).

### Level 4: Fresh-context review

A separate agent reviews output against the spec, blind to the implementer's reasoning. See [loop strategy spectrum](../../loop-engineering/loop-strategy-spectrum.md).

### Level 5: Spec-derived tests

Write tests from the spec before implementation. The agent passes tests it did not write, which encode the requirement, not its interpretation.

## Example

Task: "Add a `--dry-run` flag to the deploy command that shows what would be deployed without deploying."

What the agent builds: a `--dry-run` flag that runs the full deployment pipeline in a sandbox and rolls back afterward. The implementation is thorough — sandbox creation, deployment execution, rollback logic, cleanup. Tests pass. The PR is large and internally consistent.

What was wanted: a `--dry-run` flag that prints the deployment plan to stdout and exits. No execution, no sandbox, no rollback. Ten lines of code, not two hundred.

The agent assumed "shows what would be deployed" meant "deploys and then shows what happened." Every later decision (sandbox architecture, rollback strategy, cleanup logic) stayed consistent with that wrong assumption. The fix is not a patch. It is a rewrite — the property that distinguishes this from [objective drift](objective-drift.md), where output degrades gradually instead.

With Level 1 mitigation, the agent restates: "I will implement `--dry-run` by executing the deployment in a sandbox and rolling back." The developer catches the misunderstanding in thirty seconds and corrects it before any code is written.

## When this backfires

Mitigation adds cost. The ladder is not worth climbing when:

- The spec is precise. Universal Level 1 trains reviewers to rubber-stamp summaries.
- The task is throwaway. A wrong first attempt is cheaper to discard than to prevent.
- No reviewer is present. CI or batch pipelines where nobody reads a restatement give false confidence — [trust without verify](trust-without-verify.md) with no human in the loop.
- Ambiguity is deliberate. Early restatement collapses design decisions that should stay open.
- Requirements drift mid-task. The restatement goes stale when the spec changes.
- The spec itself is wrong. Level 2 catches interpretation errors, not requirement errors.

Apply the ladder when the cost of a wrong direction exceeds the cost of the check. Failure modes seen in the wild:

- Spec-first on bounded changes inflates overhead. Spec-kit on a date-display feature produced 8 files and more than 1,300 lines. Kiro turned a small bug fix into sixteen acceptance criteria ([Fowler, 2025](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)).
- Specs frozen before discovery lock in the wrong premise. Prototype, then spec ([Augment Code, 2026](https://www.augmentcode.com/guides/what-is-spec-driven-development)).
- Checkpoints at every step become rubber-stamps once volume exceeds what the reviewer can read ([Faros AI, 2026](https://www.faros.ai/blog/best-ai-coding-agents-2026)).

## Key Takeaways

- The error is at the root: a wrong interpretation that compiles, passes tests, and stays internally consistent until checked against the actual requirement.
- It differs from objective drift — immediate rather than gradual, and near-impossible to self-correct without an external check.
- The mitigation ladder runs from restating the task (Level 1) to spec-derived tests (Level 5); climb only when a wrong direction costs more than the check.
- Mitigation backfires on precise specs, throwaway tasks, and unattended pipelines — apply it deliberately, not universally.

## Related

- [Objective Drift](objective-drift.md)
- [Spec-Driven Development](../../workflows/spec-driven-development.md)
- [Plan-First Loop](../../workflows/plan-first-loop.md)
- [Incremental Verification](../../verification/incremental-verification.md)
- [The Yes-Man Agent](yes-man-agent.md)
- [The Implicit Knowledge Problem](implicit-knowledge-problem.md)
- [Trust Without Verify](trust-without-verify.md)
- [Spec Complexity Displacement](spec-complexity-displacement.md)
- [Entity Binding Failures in Tool-Augmented Agents](entity-binding-failures.md) — an unverified entity binding is an assumption that cascades into the wrong action.
- [Semantic Collapse Under Underspecified Prompts](semantic-collapse.md) — the upstream cause: an underspecified prompt collapses onto one confident, wrong interpretation that seeds the assumption.
- [The Patchwork Problem in LLM-Generated Code](patchwork-problem.md) — a sibling single-artifact failure: structurally incoherent code rather than a wrong interpretation.
