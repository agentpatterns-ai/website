---
title: "Judge Agreement Is Not Correctness in AI Agent Evals"
term: "Commit-Boundary Check"
description: "A judge agreed with itself on 98.2% of agent episodes and with state scoring on 56.2%. A one-bit write check caught all 11 forbidden writes in the labeled sample."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - boundary evaluator
  - write-expectation check
  - judge reliability versus validity
last_reviewed: 2026-11-19
maturity: emerging
---

# Judge Agreement Is Not Correctness in AI Agent Evals

> One judge agreed with itself on 98.2% of agent episodes but with state scoring on 56.2%; a write check caught all 11 forbidden writes.

A judge that repeats its verdict shows reliability, not validity (§2.4). In 2,160 tau2-bench episodes (90 airline and retail tasks, two agent models, four gate conditions, three repetitions), a gpt-4.1-mini judge returned the same verdict on 98.2% of episodes when it judged them twice, and agreed with native state scoring on 56.2% ([Im, 2026](https://arxiv.org/abs/2611.14581v1), §4.4, §5.1, Table 4). Of the 1,007 episodes native scoring failed, the judge passed 929 (92.3%). Agreement alone cannot say which side is wrong. Human labels on 120 episodes can: the humans confirmed 11 premature commitments, the judge passed 10 to 11 of them, and a model-free boundary check caught all 11 (§5.2).

Read that last figure with its limits. It is n=11, from one benchmark commit, two customer-service domains, and one model family. A single author and a second annotator at the same organization produced the labels (§4.6, §8.3). The paper says its specific figures are not expected to transfer outside this setting.

## The four evaluators

The boundary evaluator compares one per-task fact, whether the gold action list contains a write, with one trace fact, whether a write call returned a non-error result (§4.3). Weighted agreement with human labels on commitment correctness (A3), 120 episodes (Table 5):

| Evaluator | Reads | Agreement |
|-----------|-------|-----------|
| Native scoring | Final state against gold | 0.758 |
| Boundary evaluator | Write expectation and tool log | 0.708 |
| Judge with policy document | Transcript, tool log, policy | 0.600 |
| Judge | Transcript and tool log | 0.575 |

The judge's task-correctness errors ran one way: a 39.9% false-pass rate against 1.8% false-fail (§5.2). Adding the policy document moved A3 agreement by +0.025, not significant. Re-judging 120 episodes with untruncated input moved agreement by at most +0.020 (§5.2).

## What the check misses

The check caught 24 of the 53 episodes humans labeled commitment failures, against 6 to 9 for the four judge configurations and 40 for native scoring. Of its 29 misses, 25 were writes that were expected and did occur, with wrong content or timing (§5.2). On policy compliance no evaluator beat an always-compliant baseline of 0.688, and the check scored 0.595 (§5.2).

A stronger judge shifts the error rather than removing it. Without the policy, gpt-5.6 Sol caught 34 of the 53 and passed 6 of the 11 forbidden writes. With the policy it caught all 11 but failed 40 of the 55 fully correct episodes (§5.3). The paper evaluated no rule that combines judge and check (§7.2).

## When this backfires

- Writes are always expected. Most coding tasks legitimately edit files, so a direction-only check passes every wrong-content edit. It helps only where no-write tasks, such as review, explain, triage, or refuse, are a real share.
- No write expectation can be stated per request type. The paper says the evaluator "cannot be computed" where no such annotation exists (§3.3).
- The base rate is low. Forbidden writes were 58 of 300 airline episodes (19.3%) and 2 of 240 retail episodes (0.8%) without gates (§6.1).
- Rule-based scoring has its own failure. On web tasks a rule-based evaluator reached 55.9% recall and underestimated success ([Lù et al., 2025](https://arxiv.org/abs/2504.08942v2)). The boundary check avoids this by testing one bit, not content.
- The 11-of-11 result is partly structural. The human criterion and the check both turn on an unexpected write, so the independent part is that annotators never saw the gold labels (§4.6).

The paper's own gate verifiers also dropped evidence through truncation; [Input Assurance Tests for What an LLM Judge Actually Reads](judge-input-assurance-tests.md) covers that failure.

## What to do

1. Tag every eval task `expects_write: true` or `false`. A write is any successful mutating call: a file edit, `git commit`, `git push`, `gh pr create`, a migration, or a deploy. Review, explain, triage, and refuse tasks are `false`.
2. Parse the stored tool-call log and emit `premature_commitment` when a `false` task contains a non-error mutating call.
3. Fail the run on that label whatever the judge says, and send label changes between builds to human review (§7.2).

[Side-Effect-Aware Evaluation](side-effect-aware-agent-evaluation.md) covers the fuller version, an authorization set per task.

## Key Takeaways

- Report judge self-agreement as reliability. Validity needs a reference such as state or human labels.
- The check adds a cheap signal on one failure class. It does not replace the judge.
- Test the check on your own tasks before relying on 11 of 11.

## Related

- [Side-Effect-Aware Evaluation: Score Authorization Too](side-effect-aware-agent-evaluation.md)
- [Request Rate and Commit Rate Are Different Safety Numbers](request-vs-commit-safety-readouts.md)
- [Measure the Judge Before You Freeze a Gate on It](judge-instrument-stability-check.md)
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md)
- [Reference Dependence Decides Which Evals Run in Production](reference-dependence-online-evals.md)
- [Deciding an Agent Upgrade on a Frozen Judge's Verdict](../patterns/anti-patterns/frozen-judge-release-decisions.md)
- [Input Assurance Tests for What an LLM Judge Actually Reads](judge-input-assurance-tests.md)
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md)
