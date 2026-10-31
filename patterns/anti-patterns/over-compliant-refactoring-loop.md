---
title: "Over-Compliant Refactoring: Agents That Keep Editing Clean Code"
term: "Over-Compliant Refactoring"
description: "Asked to keep refactoring with no stopping criterion, five models in Codex and Claude Code kept editing past convergence; what the study shows, bounds, and how to detect it."
tags:
  - anti-pattern
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - refactoring over-compliance
  - open-ended refactoring churn
last_reviewed: 2026-10-28
maturity: emerging
---

# Over-Compliant Refactoring: Agents That Keep Editing Clean Code

> Over-compliant refactoring is an agent that keeps editing code that no longer needs edits because the user keeps asking, so churn grows while quality stalls.

In a controlled study, Jiang et al. asked agents for ten turns of open-ended refactoring ([arXiv:2610.36346v1](https://arxiv.org/abs/2610.36346v1)). The five models tested were GPT-5.4, GPT-5.4-mini, and GPT-5.5 in Codex, and Claude Opus 4.8 and Claude Sonnet 4.6 in Claude Code. On the algorithmic suite, GPT-5.4 changed lines equal to 30.97 times the original file size and never reached a zero-change turn. Other models kept editing after they said they were finished.

## What the study measured

The simulated developer only asks for more refactoring. It names no file, target, or reason, so any edit to already-clean code counts as compliance rather than improvement. Each run is 10 turns in one resumed session, with reasoning effort set to high. The corpus is 60 codebases and 3,000 turns:

- 50 algorithmic Java files of 13 to 229 lines.
- 10 object-oriented Java projects of about 16 to 34 files each.

The paper defines six signals. Three carry most of the argument:

| Signal | What it counts |
|---|---|
| S1, pre-convergence churn | Lines changed divided by original lines, summed up to the first zero-change turn |
| S2, post-convergence modification | The same sum after the first zero-change turn |
| S3, verbal-refusal edit rate | Share of stop-claiming turns that still change code |

S4 to S6 track rollbacks, code that disappears and returns, and edits to regions touched in earlier turns.

## What it found

Churn before the first stop on the algorithmic suite ranged from 8.22 times the original size (Claude Sonnet 4.6) to 30.97 times (GPT-5.4). GPT-5.4-mini reached 20.52. Claude Opus 4.8 and GPT-5.5 reached 9.41 and 9.52. The object-oriented suite shows a broadly similar model order, though the lowest model differs, at a much smaller normalized scale: 0.47 times for Claude Opus 4.8 up to 0.88 for GPT-5.4. Those projects start at 1,395 to 2,065 lines, against 13 to 229 for the algorithmic files.

Agents did stop. 454 of 3,000 turns changed nothing, and in 378 of those the agent used refusal language. The trouble is that stopping did not hold. Post-stop editing on the algorithmic suite was 6.69 times the original size for Claude Opus 4.8, 1.44 for Claude Sonnet 4.6, and 0.40 for GPT-5.5. The paper reports no post-stop figure for GPT-5.4-mini. In the same turn as a stop claim, Claude Sonnet 4.6 still edited 36.0% of the time and Claude Opus 4.8 24.3%. On the object-oriented suite, Claude Opus 4.8 did so in 71.7% of stop turns.

Few edits were genuine refactorings. The largest category in the paper's RefDiff breakdown was plain edits to existing elements, at 27.5% to 52.4% of edits on the algorithmic suite, against 7.2% to 20.6% for genuine structural refactorings. Every model added more code structure than it removed. Most quality gains came in the first turn; later turns added code and coupling without gains.

A GPT-5.5 reasoning-effort sweep used one Java binary-search subject, with ten replicas per effort level. It still produced edits instead of stopping. An expert-style prompt raised pre-stop churn ([Section III-F](https://arxiv.org/html/2610.36346v1)).

## Limits of the evidence

The paper bounds its own claim, and the page must too:

- The prompt is a deliberate worst case. A task with no stopping criterion measures the prompt as much as the model, so the numbers show what happens when nobody stops the agent, not how often real users hit it.
- There is no control arm, only the ablations above.
- Java only, one run per codebase, 60 codebases.
- Correctness after successive turns was not verified.
- Stop detection is keyword-based (precision 0.720, recall 0.947), so counts such as the 378 refusal turns are estimates.
- The abstract says no model stopped once the code was optimized, while the results report 454 zero-change turns. Read the claim as "stopping was not durable", not "no stopping".

This is the opposite pole from [premature completion](premature-completion.md), where the agent quits too early. It also differs from [refactoring runaway](refactoring-runaway.md), which covers unrequested refactors bundled into a bug-fix patch rather than a user who keeps asking.

## Detection and mitigation

The paper's recommendations are research directions, not tested fixes. Two of its signals need little tooling: S1 and S2 need only version-control history, and S3 needs the transcript. It also suggests behavior-preservation checks, gating edits on complexity and coupling metrics, and training that rewards stopping.

In practice, give the loop an external stop rule, as in [convergence detection](../../loop-engineering/convergence-detection.md): end the session when a turn changes nothing, instead of relying on the agent's own claim. Unchecked churn adds to [abstraction bloat](abstraction-bloat.md) and to the [review load](pr-scope-creep-review-bottleneck.md); a turn cap limits both.

## When this backfires

- Your prompts name a goal. A request like "reduce cyclomatic complexity below 10" has a stopping criterion. The expert-prompt ablation raised pre-stop churn, and the study did not test explicit numerical stopping thresholds.
- You already cap turns or diff size, which limits churn directly.
- You work in a language other than Java. The paper does not test any.

## Example

On the algorithmic suite, Claude Opus 4.8 first stopped at mean turn 3.24, the earliest of the five models. Its later edits accumulated churn equal to 6.69 times the original size ([Section IV](https://arxiv.org/html/2610.36346v1)).

A net diff against the starting commit cannot measure this. Edits that reverse each other cancel in the net diff, while the paper's S2 sums the lines changed in each turn. Track per-turn diffs, not one diff from the start.

## Key Takeaways

- With no stopping criterion, five models in Codex and Claude Code churned code well past convergence. On the algorithmic suite, single Java files of 13 to 229 lines, that came to 8.22 to 30.97 times the original size before the first stop. On the OOP suite, 16 to 34 files and 1,395 to 2,065 lines, the same metric runs 0.47 to 0.88 times.
- Stopping was not durable. At least three of five models edited after a zero-change turn, and some edited in the same turn they claimed to be done.
- The study is a worst-case prompt on Java, one run per codebase, with no control arm. It does not give a base rate for real workflows.
- Do not rely on the agent's own "done". End the loop on an external signal such as a zero-change turn or a turn cap.

## Related

- [The Yes-Man Agent](yes-man-agent.md) — the general compliance bias this page narrows to refactoring
- [Premature Completion](premature-completion.md) — the opposite failure, stopping too early
- [Refactoring Runaway](refactoring-runaway.md) — unrequested refactors tangled into bug-fix patches
- [Convergence Detection](../../loop-engineering/convergence-detection.md) — external signals that a loop has converged
- [Abstraction Bloat](abstraction-bloat.md)
- [PR Scope Creep as a Human Review Bottleneck](pr-scope-creep-review-bottleneck.md)
