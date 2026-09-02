---
title: "Verbatim Failure Records in Small-Model Agent Transcripts"
term: "Verbatim Failure Record"
description: "Echoing a failed tool call back into the transcript raises the odds of re-emitting it 2.8x per token below 1.7B; substitute a generated description."
tags:
  - anti-pattern
  - agent-design
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - failed tool call echo
  - failure record anchoring
last_reviewed: 2026-08-28
maturity: emerging
---

# Verbatim Failure Records in Small-Model Agent Transcripts

> Recording a failed tool call verbatim multiplies a sub-1.7B model's per-token odds of sending that exact call again by 2.8.

## When this applies

Three conditions bound the result, and all three must hold before you change a harness over it. The model is instruction-tuned and at or below 1.7B parameters, decoding is greedy, and the harness writes the failed call's own text back into the transcript beside the error. [Gumaan, 2026](https://arxiv.org/abs/2608.23651v1) measured six such checkpoints across four families, in simulated tool calling and MBPP program repair.

Outside that box, keep the harness you have. Feeding execution errors back lifts pass rates by 4.9 to 17.1 points on HumanEval and 16.0 to 30.0 points on MBPP across seven models up to Gemini 2.5 Pro ([Arimbur, 2026](https://arxiv.org/abs/2604.10508v1)).

## The pattern

The harness treats the error as corrective information and appends both the call and the message. Scored as the change in log-probability of re-emitting the failed action, that record is worth about -1.03 nats per action token, a factor of 2.8 in the odds of each token, on 90% to 100% of items rather than only on average. Over a fixed candidate set the probability of repeating the failed call rises from 0.06 to 0.54 ([Gumaan, 2026](https://arxiv.org/abs/2608.23651v1)).

## Why it works

Conditioning on a string raises the probability of reproducing it, and the decoder does not exempt a string marked as a failure. Counterfactuals pair the same call with a failure message, a success message, or a valence-free acknowledgement, and split the two candidate causes: "The surface-form term accounts for 83% of the effect" ([Gumaan, 2026](https://arxiv.org/abs/2608.23651v1)). Marking the call failed contributes little, and its sign is inconsistent between environments. Near-identical retries climb from 2-14% to 33-68% on the code side once a model sees its own failed program ([Verma, 2026](https://arxiv.org/abs/2607.26117v1)), and a matched-budget placebo design puts blind resampling 18 net unlocks ahead of bare-code retry, Holm p=0.0021 ([Iscan, 2026](https://arxiv.org/abs/2606.31511v1)).

That split predicts which fixes work. Substituting a runtime-generated description for the call text removes 76% of the inversion at no token cost, and a decoder ban masking the final token of a previously-failed sequence acts on the same term. A "do not repeat" line in the system prompt moves the exact repeat rate by -17 points on matched tasks, on an interval containing zero ([Gumaan, 2026](https://arxiv.org/abs/2608.23651v1)).

## When this backfires

- Clearing the context is worse, not safer. Deleting the failed step restores the exact context that produced the failure, and exact repeats rise from 31% to 80%. The paper bounds this itself: "with temperature sampling, resampling would supply the variation the context no longer does" ([Gumaan, 2026](https://arxiv.org/abs/2608.23651v1)). If your harness samples, the finding does not reach you.
- The scale extrapolation will not hold your weight. The study tops out at 1.7B; its log-linear fit crosses zero at 37.6B, a number the paper reports "in order to argue against it", because holding each checkpoint out in turn moves that crossing between 20B and 79B ([Gumaan, 2026](https://arxiv.org/abs/2608.23651v1)). Above 8B the measured sign is the other way ([Arimbur, 2026](https://arxiv.org/abs/2604.10508v1)), so do not carry this to a frontier coding agent.
- A human debugging the run needs the exact string. Keep the verbatim call in a log the model never reads.
- The description comes from the same harness that let the call through. On a schema violation nobody anticipated it degrades to "the call failed", which carries less than the error did.
- Only typed tool calling and single-function repair were measured ([Gumaan, 2026](https://arxiv.org/abs/2608.23651v1)). Multi-file edits and long-horizon planning are untested.

## Example

The two harness conditions the study compares differ in one thing: whether the failed action's own tokens are still in the window on the next turn.

**Before** — the record keeps the call text, so the next turn conditions on the tokens it is about to re-emit:

```text
<failed action, verbatim>
<error message>
```

**After** — the record keeps the diagnosis and drops the call text:

```text
<runtime-generated description of what failed and why>
```

Same diagnosis, 76% less of the inversion ([Gumaan, 2026](https://arxiv.org/abs/2608.23651v1)). To apply this, audit what your harness writes on a tool error: if the failed arguments are echoed back, that string is the thing to replace. A third option keeps the record from existing at all, by reviewing provisional tool calls before they run: +5.5% on irrelevance detection on BFCL and +7.1% on multi-turn tasks on Tau2-Bench ([Ta et al., 2026](https://arxiv.org/abs/2604.27233v1)).

## Key Takeaways

- Check the three conditions before acting: sub-1.7B model, greedy decoding, failed call echoed into the transcript. Fail any one and the finding does not apply to you.
- Treat the transcript record as a harness design choice with a measurable cost, not as free diagnostic material.
- Fix it where the damage is. The surface form carries 83% of the effect, so the remedies that act on the string work and the one that acts on the model's understanding does not.
- Do not reach for a context wipe as the safe fallback. Under greedy decoding it is the worst of the options measured ([Gumaan, 2026](https://arxiv.org/abs/2608.23651v1)).
- Keep two records: a substituted description for the model, and the verbatim call in a log for the human debugging the run.

## Related

- [Blind Resampling Over Self-Repair in Small Code Models](../../loop-engineering/blind-resampling-over-self-repair.md) — decides whether to retry with the failure attached; this page decides what the record should say once you keep one.
- [Context Poisoning: When Hallucinations Become Premises](context-poisoning.md) — the same context-as-premise failure, where the entry is a fabrication rather than a real failed call.
- [Trusting Tool Error Messages as Implicit Authority (Error-Path Injection)](tool-error-implicit-authority.md) — the security-side cost of what error frames carry into the transcript.
- [Distractor Interference: Why Relevance Is Not Enough](distractor-interference.md) — irrelevant material in the window degrading the next action, of which a stale failed call is one case.
- [Stuck-Loop Recovery: Detecting and Escaping Non-Converging Agent Loops](../../loop-engineering/stuck-loop-recovery.md) — what to do once repetition is already underway rather than preventing it at the record.
