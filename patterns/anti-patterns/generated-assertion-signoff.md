---
title: "Overtrusting Human Sign-Off on Generated Assertions"
term: "Generated-Assertion Sign-Off Gate"
description: "Developers confirm correct LLM-generated assertions well but catch incorrect ones near chance while staying equally confident, so reviewer sign-off is a weak gate."
tags:
  - human-factors
  - testing-verification
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - generated-assertion sign-off gate
  - reviewer sign-off on generated checks
last_reviewed: 2026-07-13
maturity: emerging
status: current
---

# Overtrusting Human Sign-Off on Generated Assertions

> Developers confirm correct LLM-generated assertions well but catch incorrect ones at near chance, while staying equally confident, so sign-off is a weak gate.

## The anti-pattern

An agent augments code with generated assertions or postconditions, often with a natural-language comment explaining each one. A developer reads them, they look right, and the reviewer signs off. The team now treats that sign-off as verification that the checks are correct. It is not. Human review of generated assertions catches correct ones far better than it catches wrong ones, and reviewers cannot tell the two situations apart from their own confidence.

## The measured gap

A controlled experiment with 86 Python programmers judging 260 generated postcondition assertions found the asymmetry: developers judged correct assertions at 73.9% accuracy but incorrect ones at only 49.0% — near chance ([Kaufman et al. 2026](https://arxiv.org/abs/2607.08885)). The odds of correctly judging a correct assertion were nearly three times the odds for an incorrect one (OR=2.94, p<0.001). Confidence stayed uniformly high across both cases (about 3.98–4.14 out of 5, no significant difference), so the reviewer's own certainty carries no signal about which judgments are wrong ([Kaufman et al. 2026](https://arxiv.org/abs/2607.08885)).

Natural-language explanations do not rescue the gate. They gave no overall accuracy benefit, and under-specified explanations actively reduced accuracy versus exact ones (OR=0.58, p=0.037) while raising confidence versus no comment (4.25 vs 3.99, p=0.005) — more perceived understanding without real comprehension ([Kaufman et al. 2026](https://arxiv.org/abs/2607.08885)).

## Why it works

The failure has three cited causes: an acceptance bias toward AI-generated specifications, a cognitive-demand asymmetry in which confirming correct logic is easier than detecting incorrect logic, and a clause-comparison heuristic where reviewers match assertion clauses against the docstring — which breaks for implications (OR=0.69) and element-property assertions (OR=0.66) ([Kaufman et al. 2026](https://arxiv.org/abs/2607.08885)). The confidence inflation from a plausible-but-weak explanation is automation-induced complacency: a confident-looking rationale shifts attention away from independent cross-checking, an effect present in novices and experts alike ([Parasuraman and Manzey 2010](https://journals.sagepub.com/doi/10.1177/0018720810376055)). Warning reviewers does not close it — in a separate study, people failed to catch critical flaws in AI output even when told the AI errs and paid to find mistakes ([Kabir et al. 2025](https://arxiv.org/abs/2508.06484)).

## When this backfires

Treating sign-off as a weak gate is not the same as treating it as worthless — and the finding has boundaries.

- Reviewers were right 73.9% of the time on correct assertions. Where generated checks are usually correct and the cost of a rare false accept is low, light sign-off can be cheaper than the failure it prevents.
- The study used single-function HumanEval stimuli, US-recruited participants, and short review windows of about 95–115 seconds ([Kaufman et al. 2026](https://arxiv.org/abs/2607.08885)). Multi-function code, longer review, richer IDE context, and other populations were not tested — do not over-generalize the exact numbers.
- Where the assertions are actually executed — run against a reference implementation, mutation-tested, or gated by CI — verification no longer rests on reviewer judgment, so the miscalibration matters less.

## Example

**Before — sign-off treated as verification:**

```python
def median(l: list):
    """Return the median of elements in the list l."""
    ...
# generated postcondition + explanation:
assert result == sorted(l)[len(l) // 2]
# "Checks the result equals the middle element of the sorted list."
```

The explanation reads plausibly, so the reviewer approves. The assertion is wrong for even-length lists — the median averages the two middle elements — an error class reviewers catch at near chance ([Kaufman et al. 2026](https://arxiv.org/abs/2607.08885)).

**After — sign-off backed by execution:**

Keep the human read for intent, but make correctness the machine's job: run the assertion against a trusted reference implementation and a mutation-tested input set before it can gate a merge. Reviewer approval becomes one input, not the barrier.

## Key Takeaways

- Human sign-off on generated assertions is asymmetric: about 74% accurate on correct assertions, near chance (49%) on incorrect ones ([Kaufman et al. 2026](https://arxiv.org/abs/2607.08885)).
- Reviewer confidence is flat across right and wrong judgments, so certainty is no signal — the gate cannot self-diagnose.
- Natural-language explanations do not help and, when under-specified, lower accuracy while raising confidence.
- Do not treat reviewer approval as verification; back it with executable checks — reference comparison, mutation testing, or CI — for the cases that matter.

## Related

- [Trust Without Verify](trust-without-verify.md) — accepting polished output without independent checks; this page is the reviewer-calibration evidence behind it.
- [Assertion-Free Test Theater in Agent-Authored Patches](assertion-free-test-theater.md) — generated tests with no oracle; the upstream failure to the one reviewers then wave through.
- [Tab-Accept Rate as a Proxy for Critical Engagement](tab-accept-critical-engagement-gap.md) — the same automation-complacency mechanism measured at the completion-acceptance level.
- [Model Confidence as Security Verification](model-confidence-as-security-verification.md) — confidence not tracking correctness, on the model side rather than the reviewer side.
- [LLM Comprehension Fallacy](../../fallacies/llm-comprehension-fallacy.md) — correct-looking output read as understanding; the belief this anti-pattern operationalizes.
