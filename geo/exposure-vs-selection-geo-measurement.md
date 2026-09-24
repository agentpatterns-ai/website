---
title: "Separating Exposure From Selection in GEO Measurement"
term: "Exposure-Selection Split"
description: "Why an engine-free page score estimates query-page fit rather than AI search visibility, and which quantities to report separately instead of one composite."
aliases:
  - "exposure and selection split"
  - "engine-free GEO scoring limits"
  - "GEO visibility decomposition"
tags:
  - geo
  - technique
  - tool-agnostic
last_reviewed: 2026-09-23
maturity: emerging
---

# Separating Exposure From Selection in GEO Measurement

> An engine-free page score estimates query-page fit. Visibility also needs engine-specific exposure, and cross-engine citation overlap runs from 0.0079 to 0.237.

Observed citation is the product of two probabilities. One is whether an engine exposes your page to its answer process. The other is whether it cites the page given exposure. A deterministic score computed without a live engine reaches the second factor's inputs. It cannot reach the first, because exposure is a property of one engine's search triggering, query rewriting, retrieval, and reranking ([Tannenbaum, 2026 — arXiv:2609.22655v1](https://arxiv.org/abs/2609.22655v1)).

## When the split is worth paying for

Reach for the split when you are about to act on a single visibility number. That covers comparing engines, attributing a citation change to a content edit, and reporting coverage to someone who will read one score as "AI search". If you monitor one engine and your readers use one engine, engine identity is not a confound. The paper draws the same line: "This does not imply that every use case requires four engines. It does imply that engine choice is a sampling decision and should be visible in the metric definition."

## Why it works

The two factors are not separately identifiable from the product alone. "Two production engines can therefore share the same conditional preference over exposed pages and yet produce arbitrarily different end-to-end citation distributions if their exposure functions differ" ([arXiv:2609.22655v1](https://arxiv.org/abs/2609.22655v1)). A controlled experiment that hands the model a fixed candidate list holds exposure at 1 by construction, so it measures selection alone. The authors of the engine-free score under critique reach the same conclusion from their own data, "repositioning query-agnostic scores as quality filters rather than citation predictors" ([Bajemon and Rochet, 2026 — arXiv:2609.07559v1](https://arxiv.org/abs/2609.07559v1)).

## What the audit measured

One observational audit ran 15 commercial prompts against ChatGPT, Microsoft Copilot, Google, and Perplexity on 6 June 2026, collecting 589 citation rows over 528 distinct URLs ([arXiv:2609.22655v1](https://arxiv.org/abs/2609.22655v1)). Across 73 same-prompt engine pairs, mean exact-URL Jaccard overlap was 0.0079 and 84.9% of pairs shared no URL ([arXiv:2609.22655v1](https://arxiv.org/abs/2609.22655v1)). On the ten prompts observed on all four engines, top-five exact-URL overlap was zero in all 60 pairwise comparisons. Single-engine recall of the four-engine URL union ran from 11.4% (Copilot) to 42.6% (ChatGPT) on that same subset ([arXiv:2609.22655v1](https://arxiv.org/abs/2609.22655v1)).

## How far apart engines actually are

Treat those near-zero figures as the low end of a wide range. That audit covers 15 prompts in one self-referential vertical, and its author founded the company whose infrastructure collected the benchmark. An academic study of 11,500 queries across Google Search, AI Overviews, and Gemini Flash 2.5 reports that "the retrieved sources are substantially different for each search engine (<0.2 average Jaccard similarity)" ([Grossman et al., 2026 — arXiv:2604.27790v1](https://arxiv.org/abs/2604.27790v1)). A vendor study of 161,286 prompts puts domain-level pairwise overlap between 0.119 and 0.237. On the 70,879 prompts where all four engines returned citations, 72 to 73% of cited domains appeared on exactly one engine ([Writesonic, 2026](https://writesonic.com/blog/ai-citation-source-overlap-study)). The argument for splitting the score survives at 0.2 overlap; the specific claim that engines share nothing does not.

## What to report instead

Report four quantities and keep them recoverable, even behind a composite dial:

| Quantity | What it answers | Instrument |
|---|---|---|
| Query-page fit | Is this page a good answer to this request? | Deterministic page score, no engine |
| Exposure | Did this engine surface the page at all? | Live run, per engine, logged |
| Conditional selection | Given exposure, was it cited? | Fixed-candidate experiment |
| Observed visibility | Did the answer cite or name it? | Live run, per engine, per date |

Record the engine, locale, date, product mode, and run frequency alongside the number. In the same audit, same-engine URL sets turned over 67.0% between 5 and 6 June across ChatGPT, Copilot, and Perplexity ([arXiv:2609.22655v1](https://arxiv.org/abs/2609.22655v1)). A single run is a draw, not a measurement.

## When this backfires

- Your pages are below the quality floor. Query-page fit is then the binding constraint, and the four-coordinate report costs money to change no decision.
- You read per-engine exposure off one run. At that turnover rate, splitting one noisy number into four gives you four noisy numbers and the appearance of rigor.
- Your vertical is nothing like the benchmark. The authors restrict their own result: "The numerical overlap rates should not be generalized to travel, health, shopping, local search, news, or other verticals without replication."
- Your content is syndicated or mirrored. Exact-URL matching counts a canonical and a syndicated copy as divergence. The paper flags the same gap: "Different URLs may host duplicate, syndicated, canonicalized, translated, or semantically equivalent information" ([arXiv:2609.22655v1](https://arxiv.org/abs/2609.22655v1)).

## Key Takeaways

- A page score that moves is evidence about your page. A citation count that moves is evidence about your page or about the engine, and the score cannot tell you which.
- Published cross-engine overlap spans 0.0079 to 0.237. Check the prompt count, the vertical, and whether matching is by URL or by domain before you quote one of those numbers.
- Engine choice is a sampling decision, so it belongs in the metric definition rather than in a footnote.
- Set the run schedule before you read a trend. One run per engine tells you what that engine did that day.

## Related

- [How AI Engines Cite](how-ai-engines-cite.md) — the retrieval architecture behind each engine's exposure function
- [Measuring GEO Performance](measuring-geo-performance.md) — the metric vocabulary and monitoring tools this reporting discipline sits on top of
- [What is GEO](what-is-geo.md) — the shift from rank to citation that makes the estimand question matter
- [SEO vs. GEO](seo-vs-geo.md) — why deterministic rank measurement does not carry over to probabilistic citation
