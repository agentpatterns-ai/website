---
title: "Slop Detectors Fail as Per-Item Review Gates"
term: "Slop Detection Gate"
description: "Model-free AI-content signals are corpus-level estimators. Used to gate a single diff they score formatting conventions, and the strongest code features are the ones an autoformatter erases."
aliases:
  - slop detection review gate
  - AI authorship review gate
  - statistical AI content detection
tags:
  - testing-verification
  - tool-agnostic
last_reviewed: 2026-08-10
maturity: adopted
---

# Slop Detectors Fail as Per-Item Review Gates

> Statistical slop detectors estimate what share of a corpus is model-written; asked to judge one diff, they score formatting conventions rather than authorship.

The published model-free signals for AI-generated content are population statistics, and their authors say so. Kobak et al. measured excess vocabulary across roughly 15 million PubMed abstracts, put a floor under 2024 LLM use at "13.5%" reaching "40% for some subcorpora", and then bounded the method directly: "Our analysis is performed on the corpus level and cannot identify individual abstracts that may have been processed by an LLM" ([arXiv:2406.07016v5](https://arxiv.org/abs/2406.07016v5)). A review gate is a per-item decision, so it asks the one question the method declines to answer.

## What the code-domain numbers show

Feature-driven detection of machine-written code scores well in benchmark and leans on layout. A random forest over 600,000 samples reports "ROC-AUC 0.995, PR-AUC 0.995, F1 0.971", with "average leading spaces, average leading tabs, and blank-line ratio" ranking highest ([arXiv:2601.19264v1](https://arxiv.org/abs/2601.19264v1)). Those three features are what an autoformatter exists to make constant. The paper also runs no reformatting, cross-generator, or cross-language ablation, so the figure carries no evidence about a formatted repository.

Detection also degrades in the regime that describes real work. CoDet-M4 reports 98.65% F1 in-domain for UniXcoder against 93.22% on unseen generators, 88.96% on unseen languages, 55.01% on unseen domains, and 39.36% on code mixing human- and machine-written portions ([arXiv:2503.13733v2](https://arxiv.org/abs/2503.13733v2)). Every agent-assisted diff is that mixed case: a human prompts, the agent writes, the human edits. UniXcoder is a trained transformer, and handcrafted-feature models show "greater sensitivity to distribution shifts" than learned encoders ([arXiv:2601.19264v1](https://arxiv.org/abs/2601.19264v1)), so a model-free heuristic starts below that floor.

General-purpose text detectors do not carry over either. "Existing training-based or zero-shot text detectors are ineffective in detecting code", and the method that does work needs "a surrogate white-box model to estimate the probability of the rightmost tokens" ([arXiv:2310.05103v1](https://arxiv.org/abs/2310.05103v1)), reintroducing the model the technique was supposed to avoid.

Base rate closes the case before accuracy is even reached. Where an agent authors most changes, the flag is positive nearly everywhere, so it orders nothing at any threshold.

## Why it works

A slop detector separates style populations rather than authors, which is why the corpus-level score and the per-item score come apart. Every published model-free signal (excess vocabulary, indentation habit, blank-line ratio, perplexity) is a frequency statistic over surface conventions, so it discriminates to exactly the degree that two corpora were written under different conventions.

Liang et al. show the same statistic misfiring on humans. Seven commercial detectors flagged TOEFL essays at an "average false positive rate: 61.22%" while scoring near-perfect accuracy on US 8th-grade essays, and the unanimously misclassified essays had "significantly lower perplexity compared to the others" ([arXiv:2304.02819v3](https://arxiv.org/abs/2304.02819v3)). The mechanism is perplexity, so anything that narrows word choice reads the same way to the detector: a second language, a filled-in template, a house style guide. A gate reading that statistic charges the writer for the convention.

## What to gate on instead

Spend the gating budget on properties a single item can settle. Does the change build, do its tests run, does the diff touch what the description claims, is the changed code covered? Each is deterministic and per-item, each is cheap for the same reason the detector was cheap, and none needs an authorship inference to reach a verdict. [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) sets out the general shape; [Diff-Coverage Gating for Agent-Authored Pull Requests](diff-coverage-gate-agent-prs.md) is the per-item version aimed at this queue.

The corpus-level use survives intact. How much of your own docs corpus drifted into model-shaped prose over a year is the question the excess-vocabulary estimator was built for ([arXiv:2406.07016v5](https://arxiv.org/abs/2406.07016v5)), and it answers without classifying a page.

## When this backfires

Four conditions make an authorship signal worth running anyway:

- Low base rate with routing-only use. On an inbound queue from strangers, most submissions are human and triage time is the scarce resource, so a weak flag can order the queue at positive expected value provided it never closes an item. A 61.22% false-positive rate ([arXiv:2304.02819v3](https://arxiv.org/abs/2304.02819v3)) is affordable when a human resolves each error on open, and unaffordable when the flag is the decision.
- Prose measured at population scale. The excess-vocabulary estimator is sound for the job it was designed for; what fails is the per-item cast of it ([arXiv:2406.07016v5](https://arxiv.org/abs/2406.07016v5)).
- Unformatted codebases. Where no formatter runs, the layout features survive and the benchmark numbers are closer to reachable ([arXiv:2601.19264v1](https://arxiv.org/abs/2601.19264v1)). Adopting a formatter is the better move, and it decays the gate.
- Disclosure policy rather than quality control. Where the requirement is that contributors declare AI assistance, a flag that opens a question is doing policy work, and the accuracy bar is lower than for a merge gate.

## Example

Black documents that it "ignores previous formatting and applies uniform horizontal and vertical whitespace to your code" and that it "will allow single empty lines inside functions, and single and double empty lines on module level left by the original editors" ([Black code style](https://github.com/psf/black/blob/main/docs/the_black_code_style/current_style.md)).

**Before** — the author's own indentation width and double blank line:

```python
def parse(raw):
        items = []


        for line in raw.splitlines():
            items.append(line.strip())
        return items
```

**After** — uniform whitespace, and the single empty line Black allows inside a function:

```python
def parse(raw):
    items = []

    for line in raw.splitlines():
        items.append(line.strip())
    return items
```

Leading spaces and leading tabs are now the formatter's values, whoever wrote the code. Those are the two highest-ranked features in the detector above ([arXiv:2601.19264v1](https://arxiv.org/abs/2601.19264v1)). Blank-line ratio survives in part, because Black keeps the single empty lines the author chose, so a pre-commit hook does not zero the signal. It removes the strongest part of it before review ever starts.

## Key Takeaways

- Check what unit a published detection number was measured on before you gate on it; a corpus-level estimate is not a per-item verdict, and the excess-vocabulary authors say so outright ([arXiv:2406.07016v5](https://arxiv.org/abs/2406.07016v5)).
- Measure your repo's agent-authorship base rate before costing a detector. Where it is already high, no accuracy figure rescues the flag, because it fires everywhere.
- Read a detection benchmark for its ablations, not its headline. No reformatting or cross-generator arm means the score is unmeasured on your codebase.
- Ask whether the flag routes or decides. Routing tolerates a 61% false-positive rate; a decision does not, and the difference is a policy choice rather than a threshold.
- Run the estimator on your corpus once a year rather than on each item, which is the use its authors validated.

## Related

- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — the per-item deterministic checks that replace an authorship gate
- [Diff-Coverage Gating for Agent-Authored Pull Requests](diff-coverage-gate-agent-prs.md) — a worked gate on the changed lines rather than on who wrote them
- [Verification Capacity as the Agent Quality Ceiling](verification-capacity-quality-ceiling.md) — why cheap per-item gates matter once generation outpaces review
- [AI Label as Reviewer Attention Redistribution](../code-review/ai-label-attention-redistribution.md) — what a declared authorship label does to reviewers, measured rather than assumed
- [Agent-Laundered Bug Reports](../patterns/anti-patterns/agent-laundered-bug-reports.md) — the inbound-queue failure that motivates reaching for a detector

## Sources

- [arXiv:2406.07016v5](https://arxiv.org/abs/2406.07016v5) — Kobak et al., "Delving into LLM-assisted writing in biomedical publications through excess vocabulary" (Science Advances, 2025).
- [arXiv:2601.19264v1](https://arxiv.org/abs/2601.19264v1) — Nirob, Ehsan, Rahman, Haque, "Whitespaces Don't Lie" (January 2026).
- [arXiv:2503.13733v2](https://arxiv.org/abs/2503.13733v2) — "CoDet-M4: Detecting Machine-Generated Code in Multi-Lingual, Multi-Generator and Multi-Domain Settings".
- [arXiv:2304.02819v3](https://arxiv.org/abs/2304.02819v3) — Liang, Yuksekgonul, Mao, Wu, Zou, "GPT detectors are biased against non-native English writers" (Patterns, 2023).
- [arXiv:2310.05103v1](https://arxiv.org/abs/2310.05103v1) — Yang et al., "Zero-Shot Detection of Machine-Generated Codes".
- [Is This Slop? Detecting AI-Generated Content Without a Model](https://towardsdatascience.com/is-this-slop-detecting-ai-generated-content-without-a-model-2/) — Towards Data Science; the model-free signal catalog this page evaluates.
