---
title: "Capability Parity Before Cost Parity in Low-Resource Languages"
description: "A vendor pass-rate gain measures capability. Check API cost separately before treating that gain as evidence of cost parity between languages."
tags:
  - token-engineering
  - cost-performance
  - benchmarks
  - arxiv
  - tool-agnostic
aliases:
  - low-resource language parity claim
  - reading a language benchmark parity figure
last_reviewed: 2026-10-20
maturity: emerging
---

# Capability Parity Before Cost Parity in Low-Resource Languages

> Capability gains in low-resource languages do not establish cost parity; compare test pass rate and API cost at the effort setting you use.

Read capability and cost as separate measurements. OpenAI reports that COBOL's MultiLangBench test pass rate rose from 10.9% to 72.1% between GPT-5.6 Sol and GPT-6 Astra at maximum reasoning effort. That comparison measures progress on COBOL; it does not establish COBOL-to-Python cost parity ([OpenAI, October 2026](https://openai.com/index/low-resource-programming-languages/)).

## What the numbers show

[OpenAI reports](https://openai.com/index/low-resource-programming-languages/) these test pass rates at maximum reasoning effort:

| Evaluation scope | GPT-5.6 Sol | GPT-6 Astra |
|---|---|---|
| Mean across 20 languages | 26.8% | 87.4% |
| COBOL | 10.9% | 72.1% |

The released evaluation defines its score as the pair `api_cost` and `test_pass_rate` ([MultiLangBench README](https://github.com/openai/MultiLangBench)). Keep both measurements when comparing configurations. A pass-rate table alone cannot establish a price ratio between languages.

## Why it works

Cost and capability need separate checks because an agent can spend tokens on unsuccessful attempts. Measure that behavior on the model-language pair you plan to use.

[Wu, Anderson and Guha](https://arxiv.org/abs/2607.22807v2) illustrate one failure mechanism with Gemma on OCaml. For that model-language pair, "92% of failed snapshots are compile-time errors and 8% are wrong-answer failures". The pair logs 1,196 self-loops on the stuck state, most often a revert (31%) in which the agent rewrites a byte-identical solution it already tried. A survey separately identifies "severe data scarcity" as a challenge for low-resource languages ([Joel et al.](https://arxiv.org/abs/2410.03981v3)). This example does not establish the same mechanism for every sparse language or model.

An independent measurement points the same way. On Cangjie, released in 2024, [CangjieBench](https://arxiv.org/abs/2603.14501v2) finds the best agent configuration reaching the highest Pass@1 "at 10–120x the token cost of a single prompt". The body gives the same multiple "for a single-digit Pass@1 gain".

## Which part of the budget the figure retires

Start with the effort setting. The reported maximum-effort result does not measure your deployment at a lower setting. Re-run the comparison at your intended setting.

Read each column separately. A score that improves on one axis is not evidence about another, the same reading error as [treating a detector's benchmark score as deployment evidence](../patterns/anti-patterns/detector-benchmark-score-as-deployment-evidence.md).

Match the evaluation unit to your task. MultiLangBench scores the share of a converted SQLite test suite an engine built from scratch passes. The [released eval](https://github.com/openai/MultiLangBench) says the model "is given the documentation" and "No internet access is allowed". [MultiPL-T](https://arxiv.org/abs/2308.09895v6) evaluates function-level pass@1 on MultiPL-E and [Acher and Jézéquel](https://arxiv.org/abs/2606.13763v1) report external Elo. A jump on one is not a newer reading of another.

No pass rate touches the third part. The verification budget on [programming language choice](../human/programming-language-choice-shapes-agent-artefacts.md) answers self-assessment failure. Acher and Jézéquel measured the agent's own in-loop strength signal as "biased 200 Elo–1100 Elo above the external Elo assessment". OpenAI keeps the same caveat: "applying it to production software still requires expert review and testing against the system's business rules and dependencies".

So: narrow the capability part of a language verification budget when the per-language figure sits near parity at the effort setting you run. Keep the [cost part](language-choice-token-cost.md) until the per-language cost ratio narrows. Keep the behavioral part either way.

## When this backfires

- Your language appears in no benchmark. An in-house or proprietary language is a separate regime, and [Giagnorio et al.](https://arxiv.org/abs/2606.16827v1) note that such no-resource languages "remain largely unstudied". The rule returns nothing, so the budget stands.
- The figure is greenfield and your work is maintenance. A from-scratch build with the specification supplied has little in common with a bug fix in a 30-year-old batch system whose business rules exist only in code.
- Effort is pinned below the top rung, so the number on the chart is unreachable.
- Cost is not your binding constraint. Compare the effort of collecting a detailed cost estimate with the budget decision it would change.
- The label does not name one regime. On 2024-era models the gap was already "quite strong for R and Racket, while it is more limited for Julia and Lua" ([Giagnorio et al., 2025](https://arxiv.org/abs/2501.19085v1)). CangjieBench adds that "languages traditionally labelled low-resource", including Lua and R, "have long histories and still appear in modern pre-training corpora, weakening contamination controls". Read your language's row, never the average.

## Key Takeaways

- Record API cost alongside pass rate, as the MultiLangBench score definition requires. A capability gain alone cannot establish cost parity.
- Repeat the evaluation at your intended effort setting before using maximum-effort results to change a deployment budget.
- Measure repair attempts on your model-language pair; Gemma on OCaml supplies one failure analysis, not a universal cost mechanism ([arXiv:2607.22807v2](https://arxiv.org/abs/2607.22807v2)).
- Self-assessment bias is not measured by any pass rate, so the behavioral part of a verification budget survives every version of this result ([arXiv:2606.13763v1](https://arxiv.org/abs/2606.13763v1)).
- Pass@1, suite pass rate, and external strength assessment are three different numbers; re-measure on the one your budget was priced in.

## Related

- [Language Choice as an Agent Token-Cost Lever](language-choice-token-cost.md) — the per-language token multiplier this result leaves standing
- [Programming Language Choice Still Shapes Agent Artifacts](../human/programming-language-choice-shapes-agent-artefacts.md) — the verification budget whose capability part narrows here
- [Cost-Quality Pareto Measurement for Agent Configurations](cost-quality-pareto-measurement.md) — plotting the two columns against each other
- [Probe-Run Calibration for Predicting Agent Token Spend](probe-run-cost-calibration.md) — getting your own cost figure instead of a vendor's
- [The Token Price Index Fallacy in Agent Cost Planning](../fallacies/token-price-index-fallacy.md) — the same shape one level up: a published aggregate is not your realized rate
