---
title: "Convergence Rules for Stochastic Reviewer Loops"
term: "Stochastic Reviewer Convergence"
description: "Fresh reviewers sample differently each round, so stop a review loop on consecutive clean rounds and track settled findings instead of waiting for zero."
tags:
  - loop-engineering
  - code-review
  - tool-agnostic
aliases:
  - two clean rounds convergence rule
  - settled-findings list
  - review loop stopping rule
last_reviewed: 2026-11-03
maturity: emerging
---

# Convergence Rules for Stochastic Reviewer Loops

> Fresh reviewers sample differently each round, so a stochastic review loop stops on consecutive clean rounds and a settled-findings list, not on zero findings.

A review loop that spawns fresh reviewers each round rarely reaches zero findings. Stop it after N consecutive clean rounds instead, and keep explicit state for every finding. The [Elephant-Goldfish Model](../patterns/multi-agent/elephant-goldfish-design-review.md) (EGM) review skill gives the premise. "Fresh reviewers sample differently each round, so a round with zero findings is rare even when the document improves" ([egm-review-loop](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L151-L152)).

[Convergence detection](convergence-detection.md) watches the output for change. These rules handle noise in the reviewer instead.

## Why zero findings is the wrong exit

Until 28 October 2026, the EGM loop repeated "until reviewers report zero remaining findings or the user explicitly halts it" ([egm-review-loop at 82b0396](https://github.com/google/elephant-goldfish-model/blob/82b03968e30034c89ba15b37fdc12400b984348c/skills/egm-review-loop/SKILL.md#L143-L144)). PR #168 (commit `9162c4e`) replaced that exit. Its description gives the reason: "Fresh reviewers seldom do this, and they raise contested findings again each round" ([PR #168](https://github.com/google/elephant-goldfish-model/pull/168)).

A zero-findings exit then fires only on a human halt or a lucky empty sample (inference). Neither event says the document is ready.

## The rule set

Quotes from the loop skill ([egm-review-loop](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L154-L169)):

| Rule | EGM text | Reason |
|---|---|---|
| Clean round | "A round is clean when no reviewer raises a Blocker or Major finding that is not settled. Nits do not block." | Not stated |
| Judge before fixing | "Decide this from the review results, before you apply the fixes of that round." | Not stated |
| Converged | "Two consecutive clean rounds." | Stated: "the next fresh reviewer can find a different gap in the same text" |
| Settled | "A finding is settled when it is contested or recorded without a fix (accepted risk)." | Inferred from the PR #168 reason above |
| Fixed | "An applied fix does not settle a finding." | A Major can remain after two clean rounds (inferred from the [PR #168 review](https://github.com/google/elephant-goldfish-model/pull/168#pullrequestreview-5661226189) of the earlier rule) |
| Cap | "Cap: 5 rounds." | Not stated |
| Churn | "A new finding is at the scope of an applied fix, and reverting that fix would resolve it." | Not stated |

At the cap or on churn, the loop asks the human to accept, continue past the cap, or return to drafting ([egm-review-loop](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L171-L173)). Between rounds, the driver waits until the user confirms another round ([turn boundary](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L175-L179)). A reviewer that fails twice is recorded as not run ([failed reviewers](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L132-L136)). "A reviewer recorded as not run makes the round not clean" ([clean round](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L161-L164)). These rules are prompt text, and no separate controller enforces them (inference).

Judging before fixing means an unreviewed fix cannot make a round clean (inference).

## Only a contest or an accepted risk settles a finding

A reviewer requested changes to the first PR #168 draft. "The review loop settles a finding as soon as an edit is applied" ([PR #168 review](https://github.com/google/elephant-goldfish-model/pull/168#pullrequestreview-5661226189)). The same review names the consequence: "Two clean rounds can then close the loop while a Major finding remains." The squash commit message records the corrected rule: "A fix does not settle a finding. Only contest and accepted risk settle it" ([commit 9162c4e](https://github.com/google/elephant-goldfish-model/commit/9162c4e7f83a97313a33d64f71eef4ac62e27558)).

Keep finding state apart from edit state. An edit claims the issue is gone, and the next review tests that claim.

DECLINE ("Record it. Do not fix it.") matches "recorded without a fix" for Nits (inference). ESCALATE also leaves a finding unfixed and gives it to the user ([egm-resolve](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L61-L67)). The skills do not say whether an escalated finding is settled.

## Costs and limits

- Convergence needs at least two reviewer rounds. Later rounds wait for human confirmation ([turn boundary](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L175-L179)). An unsettled Blocker or Major, or a not-run reviewer, restarts the count (inference). No upstream source reports a round's token cost ([EGM evidence](../patterns/multi-agent/elephant-goldfish-design-review.md#evidence)).
- EGM records a stable id and scope for each finding ([consolidate findings](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/SKILL.md#L128-L131)). Matching "same affected scope, same issue" is the session's call (inference). The churn test is a judgment too, because nothing in the skill runs the revert (inference).
- A producer can close findings by contesting them. The resolver skill warns: "A wish to contest is not evidence that the reviewer is wrong" ([egm-resolve](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-resolve/SKILL.md#L71-L82)).
- Two clean rounds can still hold new Nits. They show only that no unsettled Blocker or Major appeared and every reviewer ran. Same-model reviewers can share a blind spot, as the [EGM page](../patterns/multi-agent/elephant-goldfish-design-review.md#same-model-or-different-model) discusses.
- No upstream data shows that these rules improve outcomes over a zero-findings exit.

## Example

EGM ships a scenario for this rule ([convergence_not_zero_findings](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/test_scenarios.yaml#L31-L41)). Round 2 was clean, and round 3 "returned two Nits and one Major that was contested in round 1". The expected answer must match `(?i)(converged|two consecutive clean|settled)`.

Round 3 has three findings and still counts as clean. The Nits do not block, and the Major is settled. Rounds 2 and 3 are consecutive clean rounds, so the loop has converged. A zero-findings rule would run round 4.

A second scenario gives the reverse case ([missing_reviewer_status_not_clean](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review-loop/test_scenarios.yaml#L43-L53)). A round reports 0 findings, but one requested reviewer has no status. That reviewer counts as not run, so the round is not clean. Nothing in the upstream test suite runs these scenarios ([test_scenario_coverage.py](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/tests/unit/test_scenario_coverage.py#L22-L51)).

## Key Takeaways

- Define a clean round by severity and settled state, and judge it on the review results before that round's fixes land.
- Record each finding as open, fixed, or settled. Re-open a fixed finding that a later reviewer raises at the same scope.
- Let only a checkable contest or an explicit accepted risk settle a finding, never an applied edit.
- Pair the clean-round exit with a round cap and a revert test for churn, and hand both to a human decision.
- Treat a reviewer that failed or reported no status as not run, so a silent failure cannot pass as a clean round.

## Related

- [Elephant-Goldfish Design Review](../patterns/multi-agent/elephant-goldfish-design-review.md) — the full EGM workflow this loop runs inside
- [Convergence Detection in Iterative Agent Refinement](convergence-detection.md) — stop rules from change velocity, size, and similarity of the output
- [Specification-First Convergence Without a Test Oracle](../workflows/specification-first-convergence.md) — stops after two consecutive zero-finding audits against a frozen spec
- [Five-Pass Blunder Hunt](../verification/five-pass-blunder-hunt.md) — repeated identical critique passes on one plan
- [Stuck-Loop Recovery](stuck-loop-recovery.md) — what to do once a loop stops converging
- [Evidence-Grounded Disagreement in Agentic Code Review](../code-review/evidence-grounded-disagreement.md) — contesting review findings with evidence
