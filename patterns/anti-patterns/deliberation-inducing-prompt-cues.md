---
title: "Deliberation-Inducing Cues That Multiply Reasoning Cost"
term: "Deliberation-Inducing Prompt Cues"
description: "Asking a coding agent to compare several approaches multiplies reasoning tokens 2.4-7.4x on small, well-specified tasks, with no measured gain in correctness."
tags:
  - anti-pattern
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - prompt-induced reasoning waste
  - compare several approaches cue
  - deliberation cue cost
last_reviewed: 2026-08-04
maturity: emerging
---

# Deliberation-Inducing Cues That Multiply Reasoning Cost

> On small, well-specified coding tasks, deliberation cues multiply reasoning tokens several times over without a measured gain in correctness.

A deliberation-inducing cue is a prompt phrase that asks a coding agent to think, explore, or weigh options instead of telling it what finished looks like. On tasks of four files or fewer, a preregistered benchmark over six reasoning models and two harnesses, totalling 4,643 valid runs across all its phases, found that these cues multiply reasoning tokens with no matching gain in task success ([Weinberger and Hozez, arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1)).

## The pattern

You add a sentence you believe raises quality. Each cue below was measured against its own model's baseline on eight unseen holdout tasks, five repetitions per cell.

| Cue added to the prompt | Reasoning tokens vs baseline |
|---|---|
| Develop and compare several approaches | 2.4-7.4x |
| Clean up adjacent code while you are there | 3.13-4.25x (two models) |
| Think deeply about this | 1.6-2.2x |
| Make sure you are certain | 1.48-1.85x |
| Restate the requirements at length | ~1.0x |
| Scope, acceptance criteria, stop condition | 0.48-1.16x |

Every row comes from [arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1).

Two results cut against the usual advice on prompt hygiene. Irrelevant prose cost 1.03x and conflicting constraints 1.05x, so noise is close to free. A plausible but wrong architectural hint cost 2.61x, the study's most expensive defect, and the models followed the misdirection rather than catching it ([arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1)). Trimming a prompt for length buys little. Removing an unverified hint buys a lot.

## Why it works

The benchmark reports the effect and offers no mechanism, so the causal account comes from elsewhere. A reasoning trace has an instance-specific completion point past which computation continues with no further performance gain, marked by semantic convergence and repetitive oscillation ([Wei et al., arXiv:2508.17627v2](https://arxiv.org/abs/2508.17627v2)). A cue that mandates enumerating and comparing several candidates adds a sub-goal carrying no termination test, so the trace runs past that point by construction. Agent loops amplify this: reasoning models already favor internal deliberation over acting on the environment, and higher overthinking scores track worse outcomes across 4,018 SWE-Bench Verified trajectories ([Cuadron et al., arXiv:2502.08235v1](https://arxiv.org/abs/2502.08235v1)). The replacement works from the other side, because reasoning length compresses when the prompt carries an explicit budget ([Han et al., arXiv:2412.18547v5](https://arxiv.org/abs/2412.18547v5)). Scope, acceptance criteria and a stop condition are that budget written as a termination test.

## When this backfires

- The task has no obvious path. Generating and evaluating multiple candidates took GPT-4 from 4% to 74% on Game of 24 ([Yao et al., arXiv:2305.10601v2](https://arxiv.org/abs/2305.10601v2)), so bounding exploration away on a real design problem removes what finds the answer.
- The correctness half is a weak null. The benchmark publishes no per-condition success rates and defines a material success gain only qualitatively, and baseline success on one of its two harnesses already sits at 92-97%. Its authors state that effects at real-repository scale are unmeasured ([arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1)).
- Your model already regulates its own thinking. Generic thinking cues cost 1.25-1.30x on Claude Sonnet 5, measured as total output tokens rather than reasoning tokens, which the authors attribute to an adaptive-thinking controller absorbing them ([arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1)).
- You port the ranking across harnesses. Certainty-pressure language was mild on the open-model harness and the costliest family on Claude Sonnet 5 under native Claude Code, at 4.13x of total output tokens ([arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1)).
- The stop condition is wrong. The bounded template was measured against hidden deterministic evaluators, where finished is well defined ([arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1)). A hand-written condition that fires early turns a cost saving into an unfinished change.

## Example

**Before — open-ended deliberation, no stop condition:**

```text
Fix the retry logic in client.py. Think deeply about this and develop
and compare several approaches before choosing one. Make sure you are
certain. Clean up anything else that looks wrong while you are in there.
```

**After — scope, acceptance criteria, stop condition:**

```text
Fix the retry logic in client.py.
Scope: client.py only. Do not touch adjacent modules.
Acceptance: tests/test_client.py passes, including test_retry_backoff.
Stop when those tests pass. Do not add retries elsewhere.
```

The second prompt is no shorter. It replaces four unbounded sub-goals with one termination test.

## Key Takeaways

- Audit standing prompts and instruction files for wrong facts, not for length. An unverified architectural hint costs 2.61x; verbose or irrelevant prose is nearly free ([arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1)).
- Decide by task class. Use the bounded template where the path is already known; keep the invitation to explore alternatives on open-ended design work, where it is what finds the answer.
- Fix the harness before the wording. Harness choice moved cost per success by 5-30x, more than any prompt effect the study measured ([arXiv:2608.01347v1](https://arxiv.org/abs/2608.01347v1)).
- Measure on your own model. Cue rankings shifted between models and reversed between harnesses, so treat the table as a place to start looking rather than a settled ordering.

## Related

- [Request Shaping to Cut Wasted Agent Turns](../../token-engineering/request-shaping-wasted-turns.md) — the positive framing of the same lever, measured on retrieval rather than deliberation
- [Indiscriminate Structured Reasoning](reasoning-overuse.md) — applying mid-stream reasoning tools to every task regardless of fit
- [Harness-Controlled Token Economics](../../token-engineering/harness-token-economics.md) — why the orchestration layer outweighs prompt wording as a cost lever
- [Minimum-Sufficient Execution](../agent-design/minimum-sufficient-execution.md) — the same stop-early principle applied to context gathering
- [Token Reduction Is Not Cost Reduction](token-reduction-not-cost-reduction.md) — why fewer tokens does not automatically mean a smaller bill
