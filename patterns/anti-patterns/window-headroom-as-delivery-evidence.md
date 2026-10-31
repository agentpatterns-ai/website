---
title: "Reading Window Headroom as Proof Tool Results Arrived Whole"
term: "Headroom as Delivery Proof"
description: "A harness cut a third of tool results while its largest prompt used 23k of a 400k window. The shipped cut cost 28% more tool calls on one fault class, 43% with key order also reversed, not wrong answers."
aliases:
  - window headroom as delivery evidence
  - unmeasured tool-result delivery
  - empty window read as complete delivery
tags:
  - anti-pattern
  - context-engineering
  - arxiv
  - tool-agnostic
last_reviewed: 2026-10-28
maturity: emerging
status: current
---

# Reading Window Headroom as Proof Tool Results Arrived Whole

> Window headroom did not stop a third of tool results being cut. In 15 runs per arm, the cut raised median calls 28%.

Window occupancy records what the harness decided to send. It carries no information about what the tool produced. One agent diagnosing injected faults from Linux kernel traces sent a largest prompt of 23k tokens against a 400k window across 720 runs, and 3,827 of its 11,189 tool results were still cut before the model read them, every cut one arriving as invalid JSON ([Sehgal et al., arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)). That is one harness, one domain, and one model at temperature 0, so the shape transfers and the magnitudes stay local.

## The conditions that make headroom misleading

In this study, headroom hid a positional cut over stably ordered output. A prefix slice at a fixed character count removes whichever keys sit late in the string, in full, however much room the window had. In the measured harness one container list reached the model in 4.7% of 742 calls while a second list in the same payload reached it in 99.3% ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)).

It also needs a payload class big enough to cross the cap. The defect touched 2.5% of all calls yet broke 50% of process-listing calls against 1% of small summaries, which is why it survives review: "quiet on most calls, fatal on the few that matter" ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)).

Whether you see errors or only a bill turns on the last condition. Where the agent can reach the same answer another way, the loss costs work instead of accuracy.

## What to measure instead

Store the full tool result alongside the text actually sent, then report two counts per call: how many top-level fields of the produced result appear in the delivered text, and whether the delivered payload still parses. Neither check needs a model, so both are cheap enough to run in continuous integration. This is a different question from the one [context-window diagnostic tooling](../../context-engineering/context-window-diagnostic-tooling.md) answers, which attributes the tokens that did arrive to the calls that produced them. The study's summary number, yield, is "findings recorded divided by computations run" ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)).

Replay settles it deterministically. Across 864 recorded results from 31 runs, every result over budget broke under the shipped prefix slice and none broke under a row-aware cut ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)). You check your own cutter by reading its source. Of seven frameworks the authors examined, langchain-core 1.6.12 sliced serialized tool output to 500 characters keeping the front, and smolagents 1.26.0 deleted the middle of any observation over 20k characters; "Neither looks at the structure of what it cuts" ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)).

## Why it works

Field survival under a prefix slice is decided by character offset. JSON emits its keys in a stable order, so a late field is removed whole rather than shortened, and no amount of unused window changes that. The loss happens upstream of attention: "a field past the cut is not attended to less, it is gone before attention ever gets the chance to see it" ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)).

A log of delivered text alone cannot reveal what the tool produced. The agent's answer to a missing field is to compute it again. On the 15 spawned-culprit runs, median tool calls rose from 53 under the repaired harness to 68 with the shipped cut reintroduced, a 28% rise, and to 76 once key order was also reversed, a 43% rise over repaired; computations went from 18 to 36, and yield fell from 0.61 to 0.31 while recorded findings stayed at 11 throughout ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)).

Latency hides what is left. In kernel traces from two production coding agents, over 10 uncapped runs, waiting on the model took a median 84% of wall clock ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)), so extra calls barely move the number teams watch.

## When this backfires

- Expecting to recover accuracy. Both defect arms scored 15 of 15 correct against 14 of 15 for the repaired harness, so the cut cost no accuracy on that fault class. The authors state the limit plainly: "Whether the data cut truly causes the accuracy drop is still an open question." The field-data split between fault classes "remains correlation, not cause" ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)).
- A second route to the evidence. The registered prediction that reversing key order would drop accuracy was refuted: the culprit was absent from every listing payload and the agent still named it in 15 of 15 runs, because at 14.0% of kernel events it landed in the surviving first rows of every sorted table ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)).
- A window that really is the constraint. Context management earns its keep as the budget tightens, "with most of its benefit coming from preventing context-overflow failures" ([Fan et al., arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)). A cutter under genuine pressure is doing necessary work, and [half-life tool result truncation](../../context-engineering/half-life-tool-result-truncation.md) is the policy for that case.
- Treating any loss of tool output as costly. Masking environment observations in SWE-agent "halves cost relative to the Raw Agent while matching, and sometimes slightly exceeding, the solve rate of LLM-Summary" across five model configurations on SWE-bench Verified ([Lindenbauer et al., arXiv:2508.21433v3](https://arxiv.org/abs/2508.21433v3)). Discarding a result deliberately differs from corrupting one by accident.
- Reaching for recoverability as the fix. Making elided content retrievable "adds machinery that models rarely use and yields no accuracy gain" ([arXiv:2609.20804v1](https://arxiv.org/abs/2609.20804v1)), and the study's own page-on-request mechanism never fired.
- Quoting the magnitudes as effect sizes. Five recordings per fault class with paired repeats of those same five recordings is not five independent fault instances, and the authors wrote the defect themselves before reintroducing it under registered predictions.

## Example

One trace and one prompt, run under both harness conditions: a 21-container deployment with a single service held under a CPU limit, whose listing result ran to 33,370 characters against the shipped 6,000-character budget. This culprit was "already running before the trace starts, with no second, independent way for the agent to spot it" ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)), so it is the no-second-route case rather than the spawned class the controlled arms scored.

**Before** — shipped prefix slice:

```text
record delivery (replay): 30 of 118 early-list records
                          0 of 128 late-list records
payloads:                 every run broken, 10 to 14 per run
named the service:        0 of 5 runs
```

**After** — repaired delivery:

```text
payloads:                 0 of 6 runs broken
named the service:        3 of 6 runs
```

The culprit's evidence lived entirely in the late list, which is the half the slice deleted. Three of the six repaired runs were still wrong "for reasons unconnected to data loss" ([arXiv:2610.36114v1](https://arxiv.org/abs/2610.36114v1)), so this comparison carries the delivery result and not an accuracy result.

## Key Takeaways

- Window occupancy cannot report delivery loss, because the cut lands as the result is serialized into the prompt and what survives sits well inside capacity.
- Log the produced result beside the delivered text, then count surviving top-level fields and whether the payload parses. Neither check needs a model.
- Read your harness's cutter for a positional slice over ordered output. Two of seven surveyed frameworks ship one.
- Expect the first symptom as extra work rather than wrong answers: median calls 53 to 68 with the shipped cut and 76 with key order reversed, yield 0.61 to 0.31, accuracy unmoved.
- Do not carry the accuracy claim further than the authors do. They leave causation open and call the field-data split correlation.

## Related

- [Shortening Old Tool Results Under Context Pressure (Half-Life Truncation)](../../context-engineering/half-life-tool-result-truncation.md) — positional truncation prescribed as a treatment, for the case where the window genuinely binds
- [Measuring Reacquisition Cost Under Context Compaction](../../context-engineering/reacquisition-cost-measurement.md) — the same extra-retrieval signature read off a compaction setting rather than a serialization cut
- [A Guard Hook Approves the Truncated Input It Was Handed](guard-approves-truncated-input.md) — silent truncation where the actor ruling on the fragment is a policy gate
- [The Infinite Context](infinite-context.md) — the opposite reading of the same metric, where a full window rather than an empty one is taken as informative
- [Observation Masking: Filter Tool Outputs from Context](../../context-engineering/observation-masking.md) — removing a tool result on purpose, which the counter-evidence here measures as cheap
