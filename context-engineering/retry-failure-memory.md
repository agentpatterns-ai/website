---
title: "Failure Memory on Agent Retry"
term: "Retry Failure Memory"
description: "A repair study finds inconclusive pass-rate gains from failure memory; lessons show no demonstrated advantage over transcripts on bug-revealing tests."
tags:
  - context-engineering
  - memory
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - failure memory on retry
  - same-task failure memory
last_reviewed: 2026-11-03
maturity: emerging
---

# Failure Memory on Agent Retry

> Failure memory shows inconclusive retry pass-rate gains; lessons show no demonstrated advantage over transcripts on bug-revealing tests in one repair study.

Failure memory is whatever you hand a retried agent about the attempt that just failed: the transcript, a model-written lesson, or a deterministic digest of the test output. One study selected 75 real Python bugs and retried 181 failed repair attempts from 52 of them, once per condition. A plain retry fixed 29.8% of them, every memory condition scored higher by between 5.5 and 9.9 points in point estimate, and none of those differences survived Holm correction ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1)). The pass-rate evidence is inconclusive; it does not establish equivalence or justify choosing memory over extra plain retries at equal cost.

## What the result is conditional on

The selected BugsInPy tasks span 12 pure-Python projects; failures come from 11, because keras has none. The authors bound the scope: "the results apply to small, pure-Python repositories with issue-style task statements" ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1)). Two models of one family ran them, gpt-5.4-mini and gpt-5.4. The harness is tight: eight responses per attempt, 3,000 output tokens per response, low reasoning effort, and many attempts ended by exhausting it. The primary outcome counts only the bug-revealing tests, which differs from passing the full suite.

## Summarization adds cost without a demonstrated resolution advantage

The lesson condition and the transcript condition received the same truncated failure record, so their difference isolates the act of summarizing. The resolution difference was -1.7 points for gpt-5.4-mini (95% CI [-8.7, +4.9]) and -3.5 points for gpt-5.4 (CI [-14.1, +8.2]). The authors report "so we see no benefit from summarising" ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1)). Both intervals include possible benefits and harms. The lesson also costs an extra model call. Against a plain retry at roughly $0.021 per failure, the transcript added $0.004 and the lesson $0.009, and lesson-bearing retries ran about 21 to 23 seconds longer.

A bare failure announcement also lacks a demonstrated benefit over a plain retry. A retry told only that the previous attempt had failed moved editing behavior by 1.9 points for gpt-5.4-mini (CI [-6.3, +9.9]), for neither model significantly. The transcript beat that notice on resolution by 12.2 points (CI [+4.2, +20.0]), the only one of twelve contrasts in the notice-only follow-up classed as positive, from a partial run of 156 failures, and not significant for gpt-5.4 ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1)).

## What changes in retry behavior

The transcript increases editing in this harness; the study does not establish a causal mechanism for resolution gains. A plain retry edited no source file in 30.9% of the failures. With the transcript appended that share fell to 13.8%, mainly because only 4 retries declared the task done without an edit, which is a rise of 17.1 points in retries that edited a source file (CI [+7.9, +26.1]); the gpt-5.4 replication finds a significant editing increase of 14.1 points (CI [+5.1, +24.1], Holm-adjusted p=0.033) ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1)).

File placement is already near ceiling in this sample. In every condition 94% to 98% of the retries that edited anything already touched a file the reference fix changes, and "Retries that left the fix files untouched practically never passed" (1 of 215 across conditions). The resolution point estimate is about what the raised editing rate predicts. The authors label this decomposition descriptive rather than causal. What the record carries, and the notice does not, is "the concrete record of what was tried and how it failed" ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1)).

## When this backfires

On the full suite, the transcript and lesson point estimates reverse order. In a post hoc check against each project's whole test suite, 11 of 71 resolved transcript retries broke a test the reference fix passes, against 3 of 67 for the lesson. The transcript's gain over a plain retry then falls to 5.0 points while the lesson holds 7.2, and the authors conclude that "On the full-suite outcome the lesson was slightly ahead, so the choice between the two is open" ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1)).

The transcript is the record that most often ran out of room. It reached the harness input bound in 11 retries, against 6 for a plain retry and 5 for the lesson ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1)). That makes it a [context budget allocation](context-budget-allocation.md) decision wherever the input budget is tight.

Cross-task reuse has separate evidence. STAIR supplies abstracted plans from past repairs to agents handling new issues. Its ablations find that "raw, unabstracted trajectories transfer substantially worse" ([arXiv 2607.29658v1](https://arxiv.org/abs/2607.29658v1)). The repair study discusses repository-context files and cross-task memory systems separately from same-task retry memory ([Section II](https://arxiv.org/abs/2610.41433v1)). These retry results do not establish how a persistent [memory synthesis](../patterns/agent-design/memory-synthesis-execution-logs.md) layer should abstract experience.

Reflexion is a separate same-task iterative-refinement result. Its programming agent retains one experience between trials and reports 91% HumanEval pass@1 against GPT-4's 80%. Its generated tests and repeated refinement differ from the BugsInPy retry conditions ([arXiv 2303.11366v4](https://arxiv.org/abs/2303.11366v4), Section 4.3). The result does not test cross-task transfer.

## Example

The three records the study appended, for one tornado failure whose first attempt declared the task done without editing any file. Further abridged from the paper, with `[…]` marking omissions ([arXiv 2610.41433v1](https://arxiv.org/abs/2610.41433v1), Fig. 1).

The transcript condition:

```
Record of the previous attempt: FAILED ATTEMPT: --- AGENT OPERATION 1 ---
{"action":"done"} FINAL EVALUATION OUTPUT OF THE SELECTED TESTS:
[pytest log including] E RuntimeError: current IOLoop already exists
 | tornado/ioloop.py:253: RuntimeError
```

The lesson condition, written by the same model from that same record:

```
Notes written after the previous attempt: Suspected files: tornado/ioloop.py,
tornado/test/ioloop_test.py. Suspected functions: IOLoop.initialize,
TestIOLoopCurrent.test_force_current. Root cause: The failure output shows an
inverted existence check in IOLoop.initialize(make_current=True) […] Next
steps: Inspect tornado/ioloop.py around IOLoop.initialize and fix the
make_current=True branch […]
```

The deterministic digest condition:

```
Observed results of the previous attempt: Final evaluation status:
test_failures_observed. Failing selected tests:
tornado/test/ioloop_test.py::TestIOLoopCurrent::test_force_current (call).
Error lines from the final test output: E RuntimeError: current IOLoop already
exists. Files the previous attempt modified: none.
```

Every memory condition opens on the same header, which states that the previous attempt did not pass and that the workspace has been reset. The plain retry receives the first-attempt prompt unchanged. On this failure all five retries resolved the bug ([Fig. 1](https://arxiv.org/abs/2610.41433v1)).

## Key Takeaways

- Measure memory against additional plain retries under a matched budget. This study compares single retries and leaves pass-rate gains inconclusive ([Section V](https://arxiv.org/abs/2610.41433v1)).
- Track editing and resolution separately. The transcript significantly increased editing in the gpt-5.4 replication; resolution gains remained inconclusive ([Section IV-D](https://arxiv.org/abs/2610.41433v1)).
- Evaluate the full suite before choosing a format. Lessons show no demonstrated advantage on bug-revealing tests, but lead transcripts in the full-suite point estimate ([Section V](https://arxiv.org/abs/2610.41433v1)).
- Include input limits in the comparison. The transcript hit the harness input bound in 11 retries against the lesson's 5 ([Table I](https://arxiv.org/abs/2610.41433v1)).

## Related

- [Error Preservation in Context](error-preservation-in-context.md) — why failed actions stay in the window at all, which is the prior question to which record you forward
- [Context-Injected Error Recovery](context-injected-error-recovery.md) — the same information handed back inside one run, after a single failed tool call
- [Memory Synthesis: Extracting Lessons from Execution Logs](../patterns/agent-design/memory-synthesis-execution-logs.md) — extracting reusable lessons from execution traces for later tasks
- [Verbatim Failure Records in Small-Model Agent Transcripts](../patterns/anti-patterns/verbatim-failure-records.md) — where echoing the failed call back raises the odds of repeating it
- [Blind Resampling Over Self-Repair in Small Code Models](../loop-engineering/blind-resampling-over-self-repair.md) — whether to attach the failure at all, measured at a budget held equal below 7B
