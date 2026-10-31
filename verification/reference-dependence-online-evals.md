---
title: "Reference Dependence Decides Which Evals Run in Production"
term: "Reference Dependence"
description: "Production traces usually lack reference outputs. Check evaluator inputs and calibrate reference-free judges before comparing online and offline scores."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - reference-free evaluator
  - online eval portability
  - reference-free judge leniency
last_reviewed: 2026-10-28
maturity: emerging
---

# Reference Dependence Decides Which Evals Run in Production

> Reference-dependent evaluators need an expected answer, which production traces usually lack; reference-free judges need calibration on the tasks they score.

Reference dependence means an evaluator requires an expected answer to score a run. LangChain says production traces usually lack reference outputs. Its guidance on reusing offline evaluators online therefore requires evaluators that work without those outputs ([LangChain](https://www.langchain.com/blog/common-questions-about-agent-evals)). The constraint is the available input: a reference-dependent evaluator cannot score an unlabeled trace until you supply its expected answer. Sort evaluators by their required inputs before choosing a production monitor.

## Conditions for comparing evaluation lanes

Before comparing an online number with the [offline score](../workflows/offline-eval-integration-test.md), establish each lane's baseline and calibrate the online judge.

- Read each lane against its own baseline. The offline-to-online delta mixes different evaluators and different traffic samples. It cannot establish an agent regression on its own.
- Calibrate the online judge on a human-labeled sample from its domain. Across three judges and three languages, "NR-to-RV flips range from 0.09 to 0.85". The largest effects concentrated on Telugu, because "reference visibility can have a stronger effect in lower-resource settings" ([arXiv:2607.12885v1](https://arxiv.org/abs/2607.12885v1)). On English, that study's maximum flips from no-reference to reference-comparison were 0.18 for Gemini3.1-FlashLite-Preview and 0.24 for Gemma3-27B. Qwen3-32B scored 0.29 to 0.37. A number borrowed from someone else's judge tells you nothing about yours.

## Why it works

Removing the reference turns grading back into solving. A judge with no stored answer has to work out what a correct response would be before scoring the one in front of it, so its verdict inherits its own competence at the task. Krumdick and colleagues measured this across 1,200 expert-annotated long-form responses. Without a correct reference, judges show high agreement with human experts "only on questions the judges were able to correctly answer themselves". When GPT-4o graded against its own answer, "the Cohen's κ decreases from 0.86 to 0.16 in the pairwise case on questions GPT-4o could not answer" ([arXiv:2503.05061v4](https://arxiv.org/abs/2503.05061v4)). Their domain is business and finance QA plus a hard subset of MT-Bench, not agent trajectories.

Deutsch and colleagues analyze reference-free metrics for generated text. They describe this scoring as "equivalent to using one generation model to evaluate another". Their analysis finds these metrics "inherently biased toward models which are more similar to their own" ([arXiv:2210.12563v1](https://arxiv.org/abs/2210.12563v1)). A separate tool-calling study finds higher scores without references. McNemar's test on paired judge decisions found "the reference effect is statistically significant for both judges on GPT-Realtime-1.5 and Gemini-3.1-Flash-Live (p<0.001)" ([arXiv:2605.15104v3](https://arxiv.org/abs/2605.15104v3)).

## When this backfires

The reference is no neutral oracle either, so the gap between your lanes has causes pulling in opposite directions.

- The gold label encodes one acceptable path. In the one agent-domain study here, a factually correct answer "was judged 'incorrect' by both LLM judges because the expected action in the gold_answer was a RAG_query tool call to retrieve the information, rather than providing it directly". Without the reference "it was judged as 'correct' by the judges" ([arXiv:2605.15104v3](https://arxiv.org/abs/2605.15104v3)). On a second case the two reference-free judges split. In that example the annotators preferred Gemini-2.5-Pro: "Our human annotators prefer Gemini-2.5-Pro judgment in such a case." Across 200 disagreements, humans split 52% to 48% between the judges, so "neither judge is clearly preferred by humans".
- You only need a relative verdict. Model rankings were "broadly stable across judges and reference modes" ([arXiv:2605.15104v3](https://arxiv.org/abs/2605.15104v3)), so a reference-free judge can preserve relative rankings in that setting. This does not establish that it detects every regression.
- One judge runs the online lane. Two judges "disagree significantly on Gemini-3.1-Flash-Live responses in both settings (p<0.001)". One favored its own model family ([arXiv:2605.15104v3](https://arxiv.org/abs/2605.15104v3)). Compare judges and check their verdicts against human labels before attributing a score change to the agent.
- A code check or an end-state assertion already answers the question. Either can run without a stored answer if it checks a general invariant. A check against an expected output remains reference-dependent.
- Someone treats the online score as a target. Deutsch and colleagues are blunt that reference-free metrics "are certainly useful statistics to report, but improving their values as much as possible should not be the goal" ([arXiv:2210.12563v1](https://arxiv.org/abs/2210.12563v1)). Hill-climbing it optimizes for resembling the judge.
- The offline references have gone stale, which costs more than it looks: "providing slightly incorrect references can be worse than providing no reference at all" ([arXiv:2503.05061v4](https://arxiv.org/abs/2503.05061v4)).

## Example

LangChain separates evaluators by whether they need a reference output ([agent evals FAQ](https://www.langchain.com/blog/common-questions-about-agent-evals)). Apply that test to the evaluator's inputs:

| Evaluator input | Reference-dependent? | Production use |
|---|---|---|
| Generated answer and stored expected answer | Yes | Needs a labeled example |
| Trace and rubric, with no expected answer | No | Can score live traces; calibrate the judge |
| Trace and a general code invariant | No | Can score live traces if the required state is recorded |

## Key Takeaways

- Sort evaluators into reference-dependent and reference-free as you write them. An entirely reference-dependent suite cannot score production traces that lack the expected answers it needs.
- Calibrate the online judge against human labels from the domain it will score. Published flip rates spanned 0.09 to 0.85 across judges and languages, so none of them substitutes for measuring yours.
- Read each lane against its own baseline. Different evaluators and traffic samples confound the offline-to-online delta.
- Compare multiple judges in the online lane and validate disagreements with human labels.
- When gold labels prescribe a trajectory, inspect whether a low score reflects a wrong answer or a different tool-use path.

## Related

- [Offline Evaluation as an Integration Test for LLM Features](../workflows/offline-eval-integration-test.md) — the offline lane in depth, including what a green run does and does not certify
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — how to run the human-labeled calibration this page requires
- [Detecting Self-Preference in a Single LLM Judge](judge-self-preference-detection.md) — the family-preference bias a single-judge online lane hides
- [Traces Need Feedback to Power Learning](../observability/traces-need-feedback-to-power-learning.md) — where online verdicts get attached, and the sampling rules that bound their cost
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md) — the stability half, separate from the reference question
