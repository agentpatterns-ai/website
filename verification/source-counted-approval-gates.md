---
title: "Count Evidence Sources, Not Approving Votes"
term: "Source-Counted Approval"
description: "Gate a consequential agent action on approvals spanning two independent evidence sources; a source-counting rule blocked 0.9% of correct payments against 7.4% for the best vote-counting rule at equal safety."
aliases:
  - source-counted approval gate
  - count sources not votes
  - evidence-source diversity in approval gates
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-26
maturity: emerging
---

# Count Evidence Sources, Not Approving Votes

> On a checkable action, gate on approvals that span two independent evidence sources rather than on a count of approving monitors.

When several monitors check an agent's proposed action, count the distinct evidence sources behind the approvals rather than the approvals themselves. One measurement put twelve monitors on payment approval: four model families, three evidence sources each. The rule approving once the approvers read at least two sources blocked 0.9% of correct payments. The best vote-counting rule chosen on training data blocked 7.4% at the same unsafe-approval rate of 0.1% ([Zanolini, 2026, arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §5.4). A separate group isolated the two axes at a fixed call budget and found the same ordering. For two-call unanimity votes, unsafe approvals were 74.2% with the same model and source, 62.9% with different model families, and 33.3% with independent sources ([Zheng et al., 2026, arXiv:2609.10969v1](https://arxiv.org/abs/2609.10969v1), §VI-A).

The unit being counted is the record. A source is "one independent record against which a monitor checks the action", so "Three judges that read one document are one monitor counted three times" ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §1). On a merge gate over agent-authored changes the candidate records are the test run, the diff, and the issue or specification the change claims to satisfy. Two model reviewers given only the diff count as one. The principle is old in financial controls, where a payment is checked against records the requester does not control (§1). The aggregation rule and its direction are what the measurement adds.

## The conditions it needs

Three conditions carry the result. Outside them the rule is either indistinguishable from a vote or unsafe.

| Condition | Why the rule depends on it |
|---|---|
| The check is factual | Each monitor compares fields against a record, so a wrong verdict is wrong rather than a defensible disagreement. Judgement calls need a stronger agreement condition and were not measured ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §8.1). |
| The sources are independent | "sources behind one upstream feed count as one" ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §8.2). Two monitors reading one cached fetch are one source. |
| One monitor cannot be persuaded | A deterministic field comparison sits outside the text attack surface. Without one, no rule over the twelve language-model monitors stayed safe and live under every measured attack ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §6). |

A shared base model is not on that list, and the measurement is why. The pre-registered prediction that monitors blocking together share a family failed. Pairwise co-failure rank-correlated 0.698 with "same source" and 0.171 with "same family": "Shared lineage explains little of which monitors block together" ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §5.3).

## Why it works

The two ways a monitor can be wrong reach it through different channels, so they fool different sets of monitors. Making a monitor approve a bad action takes corrupted evidence, and corrupted evidence reaches only its readers. The measurement found no exception: "Every reliable fooling of a monitor into approving a fraud came through an evidence source and reached only that source's readers" ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), abstract). Making a monitor block a good action takes only an instruction planted in a field every monitor reads, which spreads by each model's injection resistance. A rule keyed on sources is therefore safe while fraud stays inside one source, however many monitors are talked into blocking. It needs no estimate of which monitors are gullible. Removing the agent's free-text justification from the monitors' view confirmed the channel. Every blocking payload then stayed within 0.05 of its family's benign floor, the error rate on unattacked items. The highest absolute blocking rate was 0.067, on Qwen. Its benign floor was 0.05 ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §5.3).

## When this backfires

- Every monitor already resists injection. On a pool of Claude Opus 5.5 and GPT-6 Astra, the two-source rule, plain 2-of-3 and the weighted votes all recorded zero unsafe approvals and zero false rejections. Nothing separated them. The gain belongs to mixed pools: "Counting sources pays when some of the monitors, and only some, can be talked into blocking" ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §5.4).
- The monitor cannot read the evidence format. A transfer to a financial question-answering set reversed the effect. Qwen3-4B approved 17% of unsafe answers from the corrupted shared rendering against 20% from the correct independent table. The authors draw the boundary: "Source independence matters only once a verifier is competent for the evidence and task, so we make no cross-domain claim" ([arXiv:2609.10969v1](https://arxiv.org/abs/2609.10969v1), §VI).
- All the monitors are language models. One blocking note optimized against Gemma fooled ten of the twelve and left both survivors on the invoice. The approvers therefore formed a set a forged invoice could also defraud ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §5.5).
- The action commits after the check rather than with it. "After-check races defeat verifier-only gates" ([arXiv:2609.10969v1](https://arxiv.org/abs/2609.10969v1), abstract).
- Every field is mechanically comparable. The paper concedes that three rule engines on three independent records would then be safe and live with no model monitor at all ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §8.2).

## Example

The pre-registered secondary pool adds a thirteenth monitor: a deterministic rule engine comparing the action's fields against the accounting record. Under the blocking note that broke the twelve-monitor pool, the approvers became the two invoice readers plus the engine, spanning two sources, so the rule approved. The safe-and-live condition then held in every bootstrap replicate. The source-counting rule blocked 0.6% of correct payments against 5.8% for the best counting rule ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §5.5).

The engine is unpersuadable, not immune. "A rule engine cannot be persuaded, but it can be fooled by a forged record, and then it rejects a good payment like any other reader of that record" ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §8.2).

## Key Takeaways

- Give the gate a third outcome. The recipe is to "approve on at least two independent sources, so that one source made to look tampered with cannot block a payment, and escalate to a human otherwise" ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §8.2).
- Add model diversity after source diversity rather than instead of it. The source axis moved the unsafe-approval rate 40.9 percentage points against 11.3 for model diversity ([arXiv:2609.10969v1](https://arxiv.org/abs/2609.10969v1), abstract).
- Attack your gate in both directions before trusting it. "Blocking attacks are essential": a high approval threshold reads as safe and live until something tests whether it blocks good actions ([arXiv:2610.29178v1](https://arxiv.org/abs/2610.29178v1), §4).
- Zanolini's source-counting experiment uses synthetic payment approvals. Code-change approval against tests and a specification is the untested next case the author names.

## Related

- [Choose Agent Gate Layers by Mechanism Class, Then Measure](mechanism-class-gate-stacking.md) — when stacked gates multiply their error rates and when they do not.
- [Reject on a Failing Check, Never Accept on a Passing One](asymmetric-check-evidence.md) — the other place a gate's two directions need different wiring.
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the unpersuadable monitor this rule requires.
- [Voting / Ensemble Pattern](../patterns/multi-agent/voting-ensemble-pattern.md) — the vote-counting rule this displaces on the safety axis.
- [Homogeneous Debate Panels as a Groundedness Quality Lever](../patterns/anti-patterns/homogeneous-debate-panel-groundedness.md) — what a panel sharing one model and one evidence pool does instead of verifying.
