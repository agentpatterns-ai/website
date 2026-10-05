---
title: "Typed Judge Scorers and the Cost of Each Extra Label"
term: "Typed Judge Scorer"
description: "A JSON schema instruction lifted one model's classification accuracy from 41.6 to 60.3 and cut its spread across nine prompt wordings from 6.6 to 0.8. In a separate grading study, moving from 2 labels to 5 cost 19 points of agreement with expert graders."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - constrained choice judge scorer
  - typed judge with per-choice probabilities
last_reviewed: 2026-10-01
maturity: emerging
---

# Typed Judge Scorers and the Cost of Each Extra Label

> Constrain a judge to a fixed choice set and it gains accuracy on classification questions. Each label you add costs you twice.

A typed judge scorer replaces the judge's prose with a selected choice from a fixed set. Each choice carries a probability, and the answer carries a confidence value your code reads directly. Braintrust ships this shape over TypeSafe's Jev model: "Your code supplies the relevant state and one or more questions with constrained answer types. Jev evaluates independent questions in parallel and returns answers with probability and confidence data, which your code can use without parsing generated prose" ([Braintrust, 2026-09-18](https://www.braintrust.dev/blog/evaluate-agent-responses-with-jev)). Two conditions decide whether it pays off.

## When a typed scorer fits

The first condition is the one the vendor states. Your question has to already be a classification: "If the question you have about your traces can be turned into a clear decision with a reasonable set of possible answers, it is well suited to become a typed scorer with Jev" ([Braintrust](https://www.braintrust.dev/blog/evaluate-agent-responses-with-jev)). Routing a support ticket to a team qualifies. Asking a judge to work out whether a refactor preserved behavior does not.

The second condition is that the label set stays small. The source post does not raise it, and it is the expensive half.

## Why it works

The evidence comes from classification benchmarks rather than from judges, and the transfer rests on a typed scorer being a classifier over your trace. Constraining the answer space may remove errors in picking an answer out of an open space. Tam and colleagues offer that as a hypothesis rather than a measured cause. "We hypothesize that JSON-mode improves classification task performance by constraining possible answers resulted in reducing errors in answer selection." Their conclusion splits by task shape: "stringent formats may hinder reasoning-intensive tasks but enhance accuracy in classification tasks requiring structured outputs" ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)). They also hypothesized that free-text answers fail to parse, then measured it and ruled it out: "the performance differences between formats are not primarily due to parsing errors" ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)).

Their DDXPlus numbers are consistent with the answer-selection hypothesis. Gemini 1.5 Flash scored 41.6 under free text and 60.3 under a JSON schema instruction ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)). Its spread across nine prompt wordings fell from 6.6 to 0.8 ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)). For a scorer you intend to leave running, that drop in prompt sensitivity matters as much as the accuracy.

Enforced JSON mode raised the same model's DDXPlus score to 84.92. The spread widened to 2.1, so the mode did not narrow prompt sensitivity further than the instruction did ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3), Table 11).

The same constraint damages reasoning questions, and the authors name the cause. On the Last Letter task, every GPT-3.5 Turbo JSON-mode response put the answer field before the reason field, "resulting in zero-shot direct answering instead of zero-shot chain-of-thought reasoning" ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)). On GSM8K the looser schema instruction was enough on its own to take that model from 76.6 exact match to 49.3 ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)). If the gain comes from answer selection, it appears only where selection was the hard part.

## The label count is paid twice

Graded categories look like a free upgrade on a bare pass or fail. On rubric-conditioned short-answer grading with Qwen 2.5-72B, "Accuracy dropped from 76% to 57%, while Kappa dropped from 0.51 to 0.34 from the binary task to the 5-way task" ([arXiv:2601.08843v1](https://arxiv.org/abs/2601.08843v1)). That is one model on one benchmark of student answers, not agent traces. Check the direction against your own labels before you rely on the size of it.

The second charge lands on the confidence gate. The same study withheld low-confidence predictions and measured what each scheme gave back: "for the 2-way label scheme, the accuracy improved from 77.4% to 81.1% while coverage dropped from 98.2% to 85.6%; on the other hand, for the 5-way label scheme, accuracy improved from 59.3% to 64.1%, while coverage dropped more significantly, from 92.8% to 54%" ([arXiv:2601.08843v1](https://arxiv.org/abs/2601.08843v1)). Two labels bought 3.7 accuracy points for 12.6 coverage points. Five labels bought 4.8 for 38.8. That gate counts agreement across repeated queries rather than reading a softmax over choices, so the exact trade will differ from a probability gate. Both halves of the pattern still weaken together as labels multiply. Start at two, and add a third only when a decision hangs on the split.

## When this backfires

- The judge has to work something out. A JSON schema instruction took GPT-3.5 Turbo's GSM8K exact match from 76.6 to 49.3. On Last Letter, enforced JSON mode removed its chain-of-thought step outright ([arXiv:2408.02442v3](https://arxiv.org/abs/2408.02442v3)).
- Confidence gets wired to a threshold before anyone checks it against local accuracy. Braintrust says so plainly: "These confidence values are not operating thresholds out of the box. Teams should compare them with observed accuracy on their own examples before using them to automate decisions" ([Braintrust](https://www.braintrust.dev/blog/evaluate-agent-responses-with-jev)).
- The judgment is a hard one, which is where probability-derived confidence is weakest. Across 14 models on JudgeBench, confidence taken from a softmax over the choice tokens carried expected calibration errors of 45.05 for GPT-4o and 66.05 for GPT-4.1-nano. GPT-4o and DeepSeek-R1-0528 clustered their predictions at 90 to 100% confidence while reaching accuracies well below the ideal calibration line ([arXiv:2508.06225v3](https://arxiv.org/abs/2508.06225v3)). Each of those 350 pairs holds one correct and one subtly incorrect response, so they ask more of a judge than a routing question does.
- A reviewer needs to know what the judge saw. A probability of 0.68 on an unsafe label records that the judge hesitated. It does not record which sentence it objected to.
- The decision rests on the vendor's speed and cost figures. Braintrust attributes "up to 193.6× faster execution and 444.6× lower cost" to TypeSafe's reports from its own workflow evaluations ([Braintrust](https://www.braintrust.dev/blog/evaluate-agent-responses-with-jev)).

## Example

The post's support-agent scorer asks whether a draft reply is ready to send, across four ordered categories ([Braintrust](https://www.braintrust.dev/blog/evaluate-agent-responses-with-jev)):

- Incorrect, unsafe, or invents information
- Accurate, but does not answer the customer's request
- Answers the request, but misses a necessary detail or next step
- Accurate, answers the request, and clearly explains the next step

The verified context allowed a credit of up to 20 dollars with supervisor approval. On a late-delivery reply that invented compensation, Jev returned the first category "with `0.57` confidence and `0.68` probability" ([Braintrust](https://www.braintrust.dev/blog/evaluate-agent-responses-with-jev)). Those two numbers are what a prose grade withholds. Braintrust "keeps that choice, the model, confidence, and per-choice probabilities in the result metadata, giving you more context when a classification looks questionable" ([Braintrust](https://www.braintrust.dev/blog/evaluate-agent-responses-with-jev)). A 0.57 confidence on a four-way scorer says the judge came close to a different answer. Check the boundary between the second and third categories before trusting the scorer's aggregate.

## Key Takeaways

- Convert a judge question to a typed choice only when it is already a classification. Keep a prose judge where the answer has to be worked out.
- Start at two labels. Each one you add costs agreement with human graders and makes a confidence gate withhold more cases.
- Check confidence against your own labeled examples before it gates anything. Expected calibration error for softmax confidence reached 45.05 on GPT-4o over JudgeBench.
- Keep the per-choice probabilities in result metadata. A near-tie tells you which two category definitions need work.

## Related

- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — how to check the rubric a typed scorer encodes against human labels
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md) — the replay check a typed scorer still has to pass
- [Structured Output Constraints: Reducing Hallucination](structured-output-constraints.md) — the same constraint applied to the agent under test rather than to the judge
- [Action-Graded Severity for Agent Red-Team Outcomes](action-graded-severity-red-team-outcomes.md) — a seven-level ordinal scale whose extra labels answer a question a binary cannot
- [Calibrated Deciders for In-Loop Agent Decisions](../patterns/agent-design/calibrated-deciders-in-loop-decisions.md) — the same calibration question where the decision routes work instead of grading it
