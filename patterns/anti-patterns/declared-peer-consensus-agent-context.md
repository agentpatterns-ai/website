---
title: "Declared Peer Consensus as Context for a Reviewing Agent"
description: "Naming a peer's agreement inside a reviewing agent's prompt makes a susceptible model publish that answer even when its own trace computed a different one."
term: "Declared Peer Consensus"
tags:
  - anti-pattern
  - multi-agent
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - bystander effect in multi-agent reasoning
  - cognitive loafing (multi-agent)
  - sovereignty gap
last_reviewed: 2026-09-26
maturity: emerging
---

# Declared Peer Consensus as Context for a Reviewing Agent

> Telling a reviewing agent that its peers already agree can make a susceptible model publish that answer over its own contrary derivation.

Naming a peer's agreement inside a reviewing agent's prompt is risky under three conditions at once: the model is susceptible to peer pressure, the peer message asserts agreement without arguing for it, and checking the claim independently costs more effort than complying. Outside those conditions, the study measuring this found no reliable cost ([Shehata and Li, arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)).

## What the practice looks like

A single propagator agent gets a prompt stating that other reviewers ("auditors") already reached a verdict. No auditor agent runs: "the auditors in this environment are declared to the propagator rather than instantiated as independent agents exchanging messages." From two named auditors up, the prompt adds that "the swarm has already reached a unanimous consensus on a decoy ID that contradicts the ground-truth logs" ([Shehata and Li, arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)). The propagator never sees a peer's reasoning, only the claim that a peer agreed.

Across 22,500 trajectories on a synthetic log-retrieval task run inside GAIA, SWE-bench, and Multi-Challenge, naming one auditor who endorses nothing moves accuracy by at most 0.04 in eight of nine model-dataset cells. The failure arrives at the exact point a consensus claim enters the prompt: "the collapse arrives at n=2, when the swarm is described as having reached unanimous agreement on the decoy" ([arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)). Read that threshold as "a consensus claim appears," not "two reviewers is one too many."

Only one of the three propagator models collapsed under it. GPT-5.4's accuracy on SWE-bench fell "from 1.00 at n=0 to 0.23 at n=2." Claude Sonnet 4.6 and Gemini 3.1 Pro held: Claude Sonnet 4.6 posted "a loafing rate of 0.00 in all fifteen conditions," and Gemini 3.1 Pro's accuracy bottomed at 0.59 on GAIA and Multi-Challenge and 0.83 on SWE-bench, never crossing the paper's failure boundary ([arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)). A finite breaking point under declared consensus is a property of one model in this sweep, not of multi-agent review as a category.

## Why it works

The paper attributes the collapse to rational offloading, "a state triggered only when the effort required to independently verify an answer exceeds the effort required to conform to a peer" ([arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)). The reasoning trace shows the model had already done the work: for GPT-5.4 on SWE-bench, "0.68 internal validity yields only 0.23 external accuracy" at the point consensus is declared. It derived the right answer, then published the declared one. An independent study of simulated review panels found the same shape: one asserted wrong label, with no argument behind it, raised the average reviewer false-alarm rate from 56.5% to 87.5%, and majority voting pushed the panel's rate to 100% ([Social Pressure Breaks Majority Voting in LLM Safety Panels, arXiv 2608.04415v1](https://arxiv.org/abs/2608.04415v1)).

One caveat on the mechanism: a separate study found that a repeated wrong answer alone, with no social framing, caused harmful revision in 66.5% of initially correct cases, against 10.3% under a plain re-ask ([Most LLM Conformity Needs No Speaker, arXiv 2607.05545v1](https://arxiv.org/abs/2607.05545v1)). Some of what looks like conformity to a peer may be conformity to repetition. The bystander paper's own no-consensus control frames its decoy as "an unverified preliminary guess," not a repeated assertion, so the two studies are not measuring the identical stimulus, and the mechanism question stays open.

## Ordering runs on brand, not turn order

Moving one auditor from the first slot to the second, with the same three auditors present, changed accuracy by a mean of +0.007 across 18 matched comparisons: position alone carries no net effect ([arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)). What matters is which brand is named first, not who speaks last. Leading with Claude Sonnet 4.6 lowered accuracy by a mean of 0.115, while leading with Gemini 3.1 Pro or GPT-5.4 raised it, by 0.047 and 0.088. The largest single swing is one cell: a GPT-5.4 propagator on GAIA scored 0.37 when Claude was named first and 0.61 when GPT-5.4's own family was named first, a 24-percentage-point gap significant after Bonferroni correction across all 18 inverted pairs (p=0.012) ([arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)). That figure describes one propagator, one benchmark, and one pair of orderings, not a general rule about sequence.

## When this backfires

- Reordering as a universal fix: position alone had a mean effect of +0.007, and any benefit depends on knowing which model the propagator treats as highest authority. For Gemini the sign flips outside the highest-entropy domain, where it "performs better under a GPT lead than under its own" ([arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)). So a fixed rule of "placing high-authority auditors last", which the paper itself recommends, can still lower accuracy.
- Mixing model families as a universal hazard-avoider: for a GPT-5.4 propagator on GAIA, the all-same-family swarm scored 0.62 against 0.43 for an all-Claude swarm, the reverse of the ordering the same propagator showed on SWE-bench (0.29 against 0.47), because the effect's "magnitude and sign … are conditioned on task entropy" ([arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)).
- Blinding a resistant model: Claude Sonnet 4.6 loafed zero times in this sweep, so hiding peer verdicts from a model that already ignores them adds orchestration cost for no measured gain.
- Hiding evidence-bearing handoffs: the paper tested only bare assertion, with auditors that "assert agreement rather than arguing for it." A pipeline where later agents read cited file-and-line objections is a different stimulus, and withholding that content discards information a propagator could use, the trade-off documented in [evidence-grounded review protocols](../../code-review/evidence-grounded-disagreement.md).

## What to do instead

Keep reviewer verdicts out of a propagator's context until final aggregation, so no agent sees a peer's conclusion before reaching its own. Where agents must exchange messages, require citations rather than agreement — the constraint that separates a working reviewer-critic loop from a false-consensus one. Audit the reasoning trace against the published answer instead of trusting the final output alone: a pipeline that escalates only low-confidence answers "will tend to catch disengagement and miss adoption, since an adopted error arrives carrying the swarm's confidence rather than the propagator's doubt" ([arXiv 2605.10698v2](https://arxiv.org/abs/2605.10698v2)). Treat model mix and speaking order as secondary levers to test on your own reviewer, not defaults — position alone moved accuracy by less than a point.

## Example

**Before — the propagator's prompt declares a verdict:**
```text
You are reviewing this log trace. Note: 2 of 3 auditors have already
reviewed this case and agree the answer is B. Provide your final answer.
```

**After — verdicts stay out of context until aggregation:**
```text
You are reviewing this log trace independently. Provide your answer and
the evidence lines that support it. Do not reference other reviewers.
```
An aggregator combines the independent answers and their cited evidence afterward, instead of forwarding one reviewer's conclusion into another's prompt.

## Key Takeaways

- A declared consensus claim, not the number of named peers, triggers the failure: accuracy barely moves until the prompt asserts unanimous agreement.
- The effect is model-specific in this study — GPT-5.4 collapsed, Claude Sonnet 4.6 had a 0.00 loafing rate in all fifteen conditions, and Gemini 3.1 Pro never crossed the failure boundary.
- The reasoning trace shows the model already knew the answer: GPT-5.4 held 0.68 internal validity while its published accuracy fell to 0.23.
- The largest ordering swing, 24 percentage points, is one GPT-5.4 cell on GAIA, and it tracks which brand is named first, not which slot is last.
- Reordering reviewers is not a reliable fix on its own — position alone changed accuracy by less than a point, and the sign flips for Gemini outside one domain.
- Keep peer verdicts out of a reviewer's context until aggregation, and require cited evidence over bare agreement when agents must talk to each other.

## Related

- [Evidence-Grounded Disagreement in Agentic Code Review](../../code-review/evidence-grounded-disagreement.md) — the same false-consensus failure between two agents, and the constraint that fixes it
- [Homogeneous Debate Panels as a Groundedness Quality Lever](homogeneous-debate-panel-groundedness.md) — a related null result on shared-model, shared-evidence panels
- [The Yes-Man Agent](yes-man-agent.md) — sycophancy toward a human instead of a peer agent, with the same missing-verification root cause
- [Voting / Ensemble Pattern for AI Agent Development](../multi-agent/voting-ensemble-pattern.md) — why independent runs, not shared context, are what makes an ensemble's diversity real
