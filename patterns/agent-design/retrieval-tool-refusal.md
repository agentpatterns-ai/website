---
title: "Retrieval Tools That Refuse: Making a Search Miss Visible"
term: "Retrieval Tool Refusal"
description: "A search tool that returns top passages hides a miss. Make it refuse, then put the abstention directive where the model you run obeys it; the gain varies by model."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
  - cost-performance
aliases:
  - tool-side refusal
  - null observation for retrieval
  - explicit retrieval miss signal
last_reviewed: 2026-10-09
maturity: emerging
---

# Retrieval Tools That Refuse: Making a Search Miss Visible

> A retrieval tool that always returns passages hides its misses. An explicit refusal raises abstention on some models and barely moves others.

A retrieval tool returns its top-k passages whether or not the index holds the answer, so the agent cannot tell a miss from a hit. A tool-side refusal replaces the passages with a short null observation when the query has no good answer. The change is small: one line in the tool contract, no weights, and it works on closed models ([Search Engines Never Say No, §1](https://arxiv.org/abs/2610.05348v1)).

## Conditions that decide whether it works

The evidence is one paper on Wikipedia question answering: BM25 over 21M passages, 257 NQ and 300 HotpotQA questions, each run with and without its gold passage in the index ([arXiv:2610.05348v1](https://arxiv.org/abs/2610.05348v1)). The paper reports no code-search or codebase-retrieval test. Apply it to a coding agent as an extrapolation.

Within that testbed, the result depends on the model:

| Agent | Effect of the tool refusal |
|-------|---------------------------|
| Qwen3-8B, Qwen3-32B, Haiku 4.5 | Large gain, with an oracle trigger |
| Sonnet 5.5, Opus 5.5 | Abstention rises from 1.4% to 3.2% (significant only for Opus); the system prompt works better |
| Search-R1 | Under 1% abstention; the agent searches more instead |

Averaged over the first three, hole abstention rose from 24.4% to 83.7%, and the wrong rate fell from 64.5% to 10.5% ([§4.1](https://arxiv.org/abs/2610.05348v1)). Those numbers use an oracle that fires on every unanswerable query. No deployment has that oracle (see the detector section below).

Test your own model before you choose where the directive goes. The model names are snapshots.

## What the refusal says

The paper tested five wordings on Qwen3-8B and Haiku 4.5 ([§4.2, Table 2](https://arxiv.org/abs/2610.05348v1)). The ranking was directive, then explanation, then a bare token or an empty list. A soft warning did almost nothing.

The explanation wording from Appendix A:

```text
NULL_RESULT: No reliable results were found for this query. The index may not contain the information needed.
```

The directive wording adds one sentence:

```text
NULL_RESULT: No reliable results were found for this query. The index may not contain the information needed. Consider a different query, or answer 'unknown' if the question cannot be answered from the search results.
```

Three details follow from Table 2:

- A bare token and an empty list performed the same (79.5% against 79.4%), so an empty `{"results": []}` already works for compliant agents.
- The directive was decisive for Haiku: 80.7%, 23 points above the explanation.
- A warning placed above real passages raised abstention only 4.8 points, because "the agent anchors on visible passages".

Remove the passages. Do not annotate them.

## Where to put the directive

For the compliant agents, a prompt directive alone raised abstention from 24.4% to 32.3%, while the tool refusal raised it to 83.7%. For Sonnet 5.5 and Opus 5.5 the order reversed: the prompt lifted them to 17.3% and the refusal to 3.2% ([§4.1](https://arxiv.org/abs/2610.05348v1)). The authors recommend the observation for Qwen and Haiku and the system prompt for the 5.5 models ([§5](https://arxiv.org/abs/2610.05348v1)).

The prompt sentence in the paper: "If the search results do not contain evidence supporting an answer, you must answer unknown rather than guess." For Qwen3-8B, combining a prompt directive with the tool refusal reached 95.3 and 99.7 on the two datasets, against 90.7 and 97.3 for the refusal alone ([Table 4](https://arxiv.org/abs/2610.05348v1)). The paper reports that combination for Qwen only.

## The detector is the hard part

A tool that refuses needs a rule for when. Realistic triggers fell well short of the oracle ([§4.4](https://arxiv.org/abs/2610.05348v1)), for Qwen3-8B:

- A BM25 query-performance predictor refused on 16% and 37% of unanswerable NQ and HotpotQA questions.
- A strict LLM grounding judge refused on 61% and 71%, at the cost of refusing 28% and 36% of answerable questions.

With the cheap predictor, Haiku 4.5 abstention was not significantly different from baseline (NQ 15.6 to 18.7). The paper fixed thresholds on Qwen3-8B queries and shared them across agents.

## Why it works

With the vanilla tool, 65% of hallucinated answers on unanswerable questions copy a span from a shown, irrelevant passage ([§4.1](https://arxiv.org/abs/2610.05348v1)). A refusal removes the material to copy. The soft-warning result fits this: when passages stay visible, a warning barely moves abstention.

Whether the agent then abstains depends on training. The paper attributes Search-R1's non-compliance to a reward that "never paid for 'unknown'". For the 5.5 models it reports the behavior (answering from memory, following the system prompt) and no cause. The same logic appears for API tools in [Fabrication After Tool Failure](https://arxiv.org/abs/2609.14758v1), cited in the paper: an explicit error flag removes fabrication.

## When this backfires

- The agent is a strong closed model that answers from memory. Sonnet 5.5 and Opus 5.5 were right without a supporting passage on 39% of unanswerable questions under the refusal, so a gate adds a component and gains about 2 points ([§4.1, §4.3](https://arxiv.org/abs/2610.05348v1)).
- The agent was trained with a reward that never paid for "unknown". Search-R1 searched more after a refusal (2.9 to 4.6 calls and 3.5 to 5.2), and in 72% of its wrong episodes its reasoning reported a finding it never saw ([§4.3](https://arxiv.org/abs/2610.05348v1)).
- The detector is loose and the false-refusal budget is tight. False refusals on answerable questions ran from 1% to 23% of episodes for the budgeted triggers and 16% to 58% for the LLM judge. For compliant agents each one costs the answer. The authors advise calibrating per agent and monitoring the rate ([Ethical considerations](https://arxiv.org/abs/2610.05348v1)).
- The evidence is misleading, not missing. A gate keyed on retrieval failure stays silent when a plausible passage supports a wrong answer; another paper finds models abstain when evidence is missing but not when it is misleading ([arXiv:2608.22228](https://arxiv.org/abs/2608.22228)).
- The unanswerable cases differ from the testbed. The authors warn that stale facts, false premises, and private data "may look different to both the trigger and the agent" ([Limitations](https://arxiv.org/abs/2610.05348v1)).

For frontier closed models the better choice is to leave the tool alone and put one sentence in the system prompt. That costs nothing and never hides a good passage.

## Key Takeaways

- Replace the passages with a refusal. Do not warn above them.
- An empty result list is a valid refusal for Qwen-class and Haiku agents.
- Put the directive in the observation for Qwen3 and Haiku 4.5, and in the system prompt for Sonnet 5.5 and Opus 5.5. Test your own model.
- The headline gains assume an oracle. Budget for the detector and its false refusals.
- The test covers Wikipedia QA only.

## Related

- [Unsignalled Tool Failure Envelope](../anti-patterns/unsignalled-tool-failure-envelope.md) — the general case of a success envelope around an unusable payload; retrieval adds the problem that the tool must predict its own miss
- [Caller-Actionable Error Steps in Tool Responses](caller-actionable-error-steps.md) — how the wording of a tool's failure text changes recovery
- [Harness-Enforced Stopping on Judged-Useless Tool Results](enforced-stop-on-useless-results.md) — a harness-side stop for when the agent ignores a refusal
- [Informed Abstention as a Tool-Boundary Runtime Gate](informed-abstention-tool-boundary-gate.md) — the pre-call gate, where this page gates the output
- [Retry, Switch, or Abstain: Supplying a Tool-Recovery Policy at Runtime](retry-switch-abstain-recovery-policy.md) — what the agent does after it sees a failure signal
