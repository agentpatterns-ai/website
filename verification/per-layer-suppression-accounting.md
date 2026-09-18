---
title: "Per-Layer Suppression Accounting in Acceptance Gates"
term: "Per-Layer Suppression Accounting"
description: "Record which layer discarded each item in a stacked acceptance gate — a pre-registered ablation found the deterministic half of one such gate suppressing nothing across 40 runs."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - per-layer suppression counts
  - gate layer attribution
  - suppression attribution by layer
last_reviewed: 2026-09-17
maturity: emerging
---

# Per-Layer Suppression Accounting in Acceptance Gates

> Count suppressions by the layer that performed them; a stacked acceptance gate whose deterministic half suppresses nothing is one filtering layer, not two.

A stacked acceptance gate reports one suppression count, and that count hides which layer earned it. Per-layer suppression accounting records, for every discarded item, the layer that discarded it. A pre-registered 2×2 factorial over 40 runs of an LLM-orchestrated offensive-security agent ran that accounting, crossing a model verifier with a deterministic acceptance layer of severity governor plus accept, refuse and raise verdict policy. The governor's mark-false-positive action fired zero times, and every false-positive suppression beyond the always-on write-time heuristics came from verifier verdicts, 29 across the two verifier arms ([Moutesidis, arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)).

## When this is worth instrumenting

The instrument is small. Every discard record carries the item, the layer that discarded it, and the rule or verdict that fired, and every layer carries an off-switch you can throw on its own. Three conditions decide whether the resulting counts tell you anything.

- The discard criterion is a judgement rather than a predicate. Where a rule can decide the question from fields the record already holds, deterministic filtering works and the counts will show it. A refactoring-aware filter cut semantic-interference false positives by nearly 32% on a labeled dataset, because behavior-preserving refactorings are mechanically detectable ([Lira et al., arXiv:2510.01960v1](https://arxiv.org/abs/2510.01960v1)).
- The workload has discrimination headroom. The study's second lab target "sits at the precision ceiling in every arm" at roughly 1.0 and "carries no discrimination power" ([arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)). No layer's contribution is measurable where every arm already scores full marks.
- The layers can be switched independently. The earlier confirmatory study could ablate only the whole package, so a skeptical reading "cannot say which component earned the result" ([arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)). Per-layer counts need per-layer switches.

## What the counts showed

| Arm | Verifier-verdict suppressions | Governor-rule suppressions | Specificity (false positives caught / candidates) |
|---|---|---|---|
| Neither | 0 | 0 | 0.017 |
| Rules only | 0 | 0 | 0.000 |
| Verifier only | 11 | 0 | 0.175 |
| Both | 18 | 0 | 0.226 |

Source: [arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1), 40 runs, five per cell per target, model-blinded adjudication with the human blind pass still pending.

The zeros are not the worst of it. Rules-only scored below the arm with no gate at all on the informative target, blinded precision median 0.312 against 0.400, while both verifier arms sat above it at 0.444 and 0.500. The deterministic heuristics also made errors that rules alone could not undo: they "false-flagged five genuine findings across the study", three of which verifier arms restored, "while the raw arms shipped their misfires as dead findings" ([arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)).

## Why it works

The split follows what each layer can decide from the stored record. A governor's predicates read fields the write path already holds, and the paper states why the deterministic evidence check cannot reach the question the gate exists to answer: "A matching quote establishes the citation is genuine, not that the conclusion is true" ([arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)). Provenance is decidable, so code decides it. Whether the conclusion holds is a judgement, which leaves one candidate layer, and the counts confirm it got the work. The same asymmetry shows up from the other direction in static analysis, where deterministic analyzers generate the noise and model agents remove it, cutting "an initial FP detection rate of over 92% on the OWASP Benchmark to as low as 6.3% in the best configuration" ([Xiong and Zhang, arXiv:2601.22952v3](https://arxiv.org/abs/2601.22952v3)).

## When this backfires

- A zero in the deterministic column is not an argument for deleting the layer. The authors re-scope their governor's "defensible role to severity governance, duplicate control, and auditability" rather than removing it ([arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)).
- Reading the result as "trust the verifier" inverts it. The counts say one probabilistic layer carries all the filtering, which is the configuration a competing argument treats as the hazard: demote the judge to an advisor and gate it with "a deterministic verification layer the judge cannot override" ([Wahi, arXiv:2609.02246v1](https://arxiv.org/abs/2609.02246v1)).
- Filtering costs retention, and the price here was pre-registered and missed. The full design kept 93.8% of model-adjudicated true candidates, 76 of 81, with a lower one-sided 95% bound of 0.875 against its own 0.90 floor ([arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)).
- Deterministic layers fail by composing, and the log can render the failure as health. Deduplication "matched on type, URL, and title, found an exact match, and silently returned the existing record" when the resubmission was a correction carrying better evidence, and "the audit log recorded a duplicate skipped, which reads as healthy, not a repair refused" ([arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)).
- One system, two lab targets, one author, and an adjudicator from the same model family as the orchestrators it graded. The paper states that "nothing here generalizes to other architectures, stacks, or live engagements" ([arXiv:2609.15887v1](https://arxiv.org/abs/2609.15887v1)). Run the accounting on your own gate rather than importing the zero.

## Key Takeaways

- Tag every discard with the layer that made it. A composite suppression count cannot tell you whether your second layer is working or absent.
- Predict which layer will do the work by asking whether the discard criterion is decidable from the record. Decidable criteria belong to code; judgements fall to the model.
- A deterministic layer that suppresses nothing may still earn its place through severity governance, duplicate control, and auditability, but stop describing the gate as layered defense against false positives.
- Set a retention floor before you switch the filter on, and hold the result against it. The study's own floor was 0.90 and its measured design did not clear it, which is only visible because the floor was fixed in advance.

## Related

- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the general case for hard checks around agent output; this page is the measured qualification of what those checks filter
- [Phantom Symbol Detection for LLM API Migration](phantom-symbol-detection.md) — a deterministic check that does catch what probabilistic judges miss, because its criterion is decidable against a symbol database
- [Layered Accuracy Defense for Reliable Agent Outputs](layered-accuracy-defense.md) — distributing verification across pipeline stages, which this accounting tests rather than assumes
- [Classification Before Repair in an Analyzer Backlog](classification-before-repair-analyzer-backlog.md) — the adjacent finding that deciding whether each analyzer result is real is where the expensive errors live
- [Verification-Gated Agent Autonomy via Automated Review](../patterns/agent-design/verification-gated-agent-autonomy.md) — the same verifier-plus-enforcement shape applied to action approval rather than to what an agent reports
- [Isometric Harness Ablation](../patterns/agent-design/isometric-harness-ablation.md) — one-at-a-time subsystem removal for ranking investment, where this accounting attributes credit inside a single gate
