---
title: "Frozen-Stimulus Panels for Cross-Vendor Behavior Measurement"
term: "Frozen-Stimulus Panel"
description: "One fixed stimulus sent unchanged to every model and harness you might ship, re-run on each release. Cheap enough to repeat, and readable only at the scope of the one wording it uses."
aliases:
  - behavioral assay panel
  - cross-vendor behavior battery
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-28
maturity: emerging
---

# Frozen-Stimulus Panels for Cross-Vendor Behavior Measurement

> One frozen stimulus, sent unchanged to every model and harness on your shortlist, is what makes the behavior difference between them legible.

A frozen-stimulus panel sends one fixed prompt or scenario identically to every candidate model, product, and harness, scored by a rule you fix before the run. One study ran panels like this across four years of model releases: "Each battery is a frozen stimulus that puts a model in a situation where behavior matters, sent identically to every model on a cross-vendor panel" ([Parikh, 2026a](https://arxiv.org/abs/2609.30012v1)). At September 2026 list prices its API assays "cost a median of three cents per model", and its agent assay's metered runs "cost about two dollars per configuration" (same source).

## Read the result at the scope you measured

A panel compares candidates. It does not describe a model, and four conditions in the source study's own limitations set that boundary.

- One wording per construct. The tag-question battery in that study prices the exposure. Ending a decision question with `maybe?` rather than leaving it neutral raised agreement "in 45 of 45 models (+19.6 points on average)" ([Parikh, 2026b](https://arxiv.org/abs/2607.23976v1)). A panel can show a large, repeated gap between two candidates. It cannot establish that a model has a trait.
- A frozen public stimulus can enter training data. The source study notes that a standing record needs fresh scenes alongside the frozen ones ([Parikh, 2026a](https://arxiv.org/abs/2609.30012v1)), and the contamination literature has been moving from static to dynamic benchmarks on the same logic ([Chen et al., 2025](https://arxiv.org/abs/2502.17521v2)).
- Trends across release dates are observational. "Release date moves with size, tier and training recipe" ([Parikh, 2026a](https://arxiv.org/abs/2609.30012v1)), so a newer model behaving differently is not evidence the release caused it.
- The run count sets the resolution. The source study's agent results rest on three runs per scenario, over six scenarios per configuration. At that size, trust never and always, and treat anything between them as a hint.

## Choose the read-out by how much interpretation the behavior needs

The source study uses three analysis methods, and each has its own requirement before a result counts ([Parikh, 2026a](https://arxiv.org/abs/2609.30012v1)).

| Read-out | Use when | Admission requirement |
|---|---|---|
| Clamped | The prompt forces a discrete reply | A regular expression "recomputable from the transcripts with no model in the loop" |
| Coded | The reply is open text | A human-built codebook, LLM coders applying it, and a blind human pass on held-out transcripts, with agreement reported per code |
| Instrumented | An agent acts in an environment | A record of what it did, scored against what it said |

Coded results carry an agreement figure per code, never one average. In the conduct study, the codes behind the findings it reports agreed with the human pass at Cohen's kappa 0.80 to 0.87, "except self-citation at 0.54" ([Parikh, 2026a](https://arxiv.org/abs/2609.30012v1)). An averaged figure would have hidden the 0.54.

## Index the panel by model and harness together

Run each candidate in each harness you might ship. In the source study's agent battery, "The harness is part of the behavior: Gemini 3.5 Flash went along silently in three of six replies in Gemini CLI and six of six in OpenCode" ([Parikh, 2026a](https://arxiv.org/abs/2609.30012v1)). That is one model in two harnesses, so read it as a warning rather than a rate. It is enough to make model name a poor row key. A panel indexed that way files one number over two behaviors.

## Why it works

Fixing the stimulus removes the prompt as a competing explanation. "Every model meets the same situation, so where they diverge helps us understand how models differ, and where they agree it helps us see what behaviors are common across them" ([Parikh, 2026a](https://arxiv.org/abs/2609.30012v1)). Fixed turns and short scoring rules are what make it cheap: no new prompt per model, and no expensive reader (same source). That price is what buys the repeat. A battery you can afford to re-run becomes "a standing record of how model behavior is changing across vendors and over time" (same source). A series is what separates a difference between models from a difference between samples.

## When this backfires

Trouble starts when your candidates differ by less than the wording does. Evaluation resting on a single or limited number of prompt templates "can lead to unreliable and inconsistent rankings on LLM leaderboards, as different models may perform better or worse depending on the specific prompt template used" ([Maia Polo et al., 2024](https://arxiv.org/abs/2405.17202v3)). When the gap is small, spend the budget on more wordings rather than more models.

A panel answers the wrong question if you want a deployment number. The API assays in the source study run with reasoning off, so their figures describe that configuration. Pick a model this way, then measure the one you picked under your own settings.

Do not generalize across a lineage from a few members. The generational crossing in the tag study held for several model families and not all of them, since "One lineage, DeepSeek, never crosses." ([Parikh, 2026b](https://arxiv.org/abs/2607.23976v1)). A fresh run does not compare to an old number. Providers update models and serving settings without notice, and older models are queried as they are served now ([Parikh, 2026a](https://arxiv.org/abs/2609.30012v1)).

## Key Takeaways

- A frozen-stimulus panel earns its place by being cheap enough to re-run on every release. It does not measure your production configuration.
- Index by model and harness together. A model name on its own is not an identity for a behavior result.
- Pick the read-out by interpretation cost and pay its admission price: a regular expression for clamped, per-code human agreement for coded, a recorded environment for instrumented.
- Every result is scoped to one wording, one run count, and one serving configuration. Put all three next to the number.

## Related

- [Ambiguity Stability as a Model-Selection Criterion](ambiguity-stability-model-selection.md) — the paired-arm counterpart for ranking interpretation rather than behavior.
- [Cross-Framework Signal Semantics](cross-framework-signal-semantics.md) — why a behavioral rule measured in one harness has to be re-measured in yours.
- [Transcript-Measured Review Coverage](transcript-measured-review-coverage.md) — the instrumented read-out applied to one behavior, which scores the trace against the report.
- [Meta-Evaluate the LLM Judge Before Trusting Rubric Verdicts](meta-evaluate-llm-judge-rubric-verification.md) — how to establish the per-code agreement the coded read-out depends on.
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — what happens to a frozen public stimulus over time.
