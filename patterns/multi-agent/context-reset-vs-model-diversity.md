---
title: "Reviewer Independence: Context Reset or Model Diversity"
term: "Reviewer Independence"
description: "Reviewer independence comes from a fresh context, a different model family, or new evidence, each addressing different errors (inference)."
tags:
  - multi-agent
  - agent-design
  - tool-agnostic
aliases:
  - context reset versus model diversity
  - same-model fresh-context review
  - different-model-family reviewer
last_reviewed: 2026-11-03
maturity: emerging
---

# Reviewer Independence: Context Reset or Model Diversity

> Reviewer independence comes from a fresh context, a different model family, or new evidence, each addressing different errors (inference).

A reviewer can differ from the author in the conversation it sees, the model it runs, and the evidence it reads. [When a Second Model Helps in LLM Review](../../verification/cross-model-review-independence.md) holds the measurements that compare the first two. The table below maps them to error classes.

Two pages on this site take opposite sides. The [critic agent pattern](../agent-design/critic-agent-plan-review.md) asks for a different model. The [Elephant-Goldfish Model](elephant-goldfish-design-review.md) (EGM) runs its Claude reviewers with `model: inherit`, so reviewers use the starting session's model ([EGM Claude integration](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/claude.md#L130-L131)).

## What a fresh context removes and keeps

EGM's design text says "Self-review by the authoring LLM suffers from severe confirmation bias" ([review.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/review.md#L26-L31)). Its fix is a new reviewer that gets no parent deliberation ([Claude integration](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/claude.md#L125-L128)). Reviewers still read files, and the zoom-out reviewer must search the codebase for reuse ([zoom_out](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/zoom_out.md#L45)).

The reset keeps the weights. Song's fresh-session condition also withholds the original request, so it cannot isolate context reset ([v2, §3.2](https://arxiv.org/html/2610.01471v2#S3.SS2)). Its findings overlap same-context review at a rate comparable to within-model session pairs ([§5.3](https://arxiv.org/html/2610.01471v2#S5.SS3)). The study uses Korean artifacts ([limitations](https://arxiv.org/html/2610.01471v2#Sx1)).

The [EGM page](elephant-goldfish-design-review.md#same-model-or-different-model) covers Self-Correction Bench. Tsui scopes the claims "to conversational role rather than authorship" ([Tsui, §4.2](https://arxiv.org/html/2507.02778v3#S4.SS2)). Reasoning models show "a small, even negative" blind spot ([§4.4](https://arxiv.org/html/2507.02778v3#S4.SS4)).

## What a different model family adds and keeps

In Song's data, cross-model pairs shared fewer findings than sessions of one model ([§5.3](https://arxiv.org/html/2610.01471v2#S5.SS3)). One fresh-session review plus one cross-model review also matched more planted errors than two fresh-session reviews. That gain was not significant against two reviews by the stronger cross-model reviewer, so capability and model difference stay confounded ([§5.2](https://arxiv.org/html/2610.01471v2#S5.SS2)).

A second family can still share errors (inference). Across 9 judges from 7 families, "the models make the same mistakes on the same items" ([Kohli](https://arxiv.org/abs/2605.29800v1)). On MNLI, same-family pairs were 0.047 more correlated than the cross-family mean ([§5.3](https://arxiv.org/html/2605.29800v1#S5.SS3)). That study scored natural language inference labels, not review.

Chen et al. measure a model "favoring its exact own output", not its family ([limitations](https://arxiv.org/html/2504.03846v3#A8)). They also find that a long chain of thought before evaluation reduces harmful self-preference ([abstract](https://arxiv.org/abs/2504.03846v3)).

Adding a second family requires another review call and integration (inference). Claude Code's subagent `model` field documents Claude aliases, Claude model IDs, and `inherit` ([Claude Code subagents](https://code.claude.com/docs/en/sub-agents)). A cross-family reviewer there needs another host or a gateway (inference).

## Evidence the author never read

Ao, Gao, and Simchi-Levi note that "Planner, worker, critic, and reviewer modules are often built from the same model family" ([arXiv 2603.26993v1, §1](https://arxiv.org/html/2603.26993v1#S1.p2)). Their Table 1 counts a shared base model and a common prompt as a common signal. Tool calls and API outputs are new private signals ([Table 1](https://arxiv.org/html/2603.26993v1#S2.T1)). Corollary 9 says rereading the terminal information state cannot improve Bayes risk, while nonredundant verifier signals can ([Corollary 9](https://arxiv.org/html/2603.26993v1#Thmtheorem9)). The paper does not test reviewers from different families.

Under that frame, a shared rubric adds no new signal (inference). A code read may add one if it supplies nonredundant evidence (inference). EGM passes a document standard to zoom-out ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L297-L299)). The comprehension reviewer gets "no document standard" ([egm-review](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/skills/egm-review/SKILL.md#L328-L333)). The `codebase_details` reviewer checks the document against source code ([persona](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/agents/codebase_details.md#L47-L48)).

## Decision table

Cells are inference unless marked observed or measured. Song's category F1 estimates lack uncertainty intervals and significance tests ([§5.4](https://arxiv.org/html/2610.01471v2#S5.SS4)).

| Condition | Same model, fresh context | Add a different family | Source |
|---|---|---|---|
| The author's conversation hid a gap | Targets this | No specific gain | [review.md](https://github.com/google/elephant-goldfish-model/blob/36343a16f0e0d830a7ed78b0da97695379ab3243/docs/designs/review.md#L26-L31) |
| A test, tool, or code read can check the claim | Give the reviewer that access | No specific gain | [Ao et al., Corollary 9](https://arxiv.org/html/2603.26993v1#Thmtheorem9) |
| Code in Song's study | Higher observed F1 | Lower observed F1 | [Song, Table 3](https://arxiv.org/html/2610.01471v2#S5.T3) |
| Documents in Song's study | Lower observed F1 | Higher observed F1 | [Song, Table 3](https://arxiv.org/html/2610.01471v2#S5.T3) |
| The judge scores its own exact output | Reason at length before judging | Removes the own-output case | [Chen et al.](https://arxiv.org/abs/2504.03846v3) |
| Many reviewers will vote | Correlated | Still correlated (measured) | [Kohli](https://arxiv.org/html/2605.29800v1#S5.SS3) |

## Key Takeaways

- Name the error class first; choose context, model, or evidence changes to test against it (inference).
- Song changes context and request access together; use evidence checks to test gaps a reset could leave (inference).
- Allow for correlated errors when combining reviewers from different families (inference).
- Do not cite Self-Correction Bench for a second model; it tests conversational role inside one model.

## Related

- [When a Second Model Helps in LLM Review](../../verification/cross-model-review-independence.md) — the measured comparison of fresh-session and cross-model review
- [Elephant-Goldfish Design Review](elephant-goldfish-design-review.md) — the same-model, fresh-context worked example
- [Adversarial Multi-Model Development Pipeline (VSDD)](adversarial-multi-model-pipeline.md) — combines a fresh context with a second model family
- [Critic Agent Pattern: Dual-Model Plan Review](../agent-design/critic-agent-plan-review.md) — asks for a different model as the critic
- [Forked vs Fresh Subagents](forked-vs-fresh-subagents.md) — when a subagent inherits the parent conversation
- [Detecting Self-Preference in a Single LLM Judge](../../verification/judge-self-preference-detection.md) — measuring same-family bias in a judge
