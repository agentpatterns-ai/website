---
title: "Knowledge Cutoff as a Documentation Boundary"
term: "Cutoff-Derived Documentation Boundary"
description: "A model's published cutoff date does not mark where its knowledge of your product ends. Across 336 graded Dev Proxy tasks the passes and failures scatter on both sides of it."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - cutoff-derived documentation boundary
  - cutoff date as a capability proxy
  - version-boundary context budgeting
last_reviewed: 2026-09-23
maturity: emerging
---

# Knowledge Cutoff as a Documentation Boundary

> A published cutoff date does not tell you which product versions a model knows, so it cannot decide which documentation to load.

Deriving a documentation budget from a cutoff date fails at the first step: the date is not a version. Waldek Mastykarz tested GPT-5.6 Luna against Dev Proxy and SharePoint Framework with documentation and web search removed, one graded task per suitable product change. OpenAI lists that model's cutoff as February 16, 2026; asked where its Dev Proxy knowledge ended, the model named 0.29.0, which shipped on June 25, 2025 ([Mastykarz, 2026](https://devblogs.microsoft.com/blog/knowledge-cutoff-is-a-poor-proxy-for-model-capability/)).

## What the results look like

Noise rather than a decay curve. Across 336 Dev Proxy tasks over 53 versions the model passed 61, or 18%; SharePoint Framework gave 61 passes from 413 tasks over 40 versions, or 15%. Dev Proxy 0.3.0 passed four of five tasks while 0.4.0 passed none; 2.3.4, 3.0.0 and 3.1.0 each passed one of two despite shipping after the cutoff ([Mastykarz, 2026](https://devblogs.microsoft.com/blog/knowledge-cutoff-is-a-poor-proxy-for-model-capability/)).

The two error directions differ in price. Below the boundary the model answered a Dev Proxy 0.5.0 question with `devproxy` when the executable was still `mgdp`. On SharePoint Framework 1.11.0 it wrote plausible module-loader advice while missing that the release removed SystemJS support from the local workbench ([Mastykarz, 2026](https://devblogs.microsoft.com/blog/knowledge-cutoff-is-a-poor-proxy-for-model-capability/)). Those gaps surface as confident wrong answers. Above the boundary the rule spends context on releases the model already handles.

## Why it works

Three causes stack, none ordered by date. A published cutoff caps the corpus, not one resource. Measured effective cutoffs differ from reported ones, because CommonCrawl dumps carry old data forward and deduplication misses near-duplicates ([Cheng et al., 2024](https://arxiv.org/abs/2403.12958v2)). Presence is not recall. Answer accuracy tracks how many pretraining documents support a fact, so a low-traffic product sits in the long tail whatever its release date ([Kandpal et al., 2023](https://arxiv.org/abs/2211.08411v2)). And a pass above the boundary can come from generalization instead of memory, indistinguishable from knowledge at the output ([Mastykarz, 2026](https://devblogs.microsoft.com/blog/knowledge-cutoff-is-a-poor-proxy-for-model-capability/)).

Replace the date with a measurement: run tasks drawn from your real work with no product knowledge, then add documentation and measure the delta ([Mastykarz, 2026](https://devblogs.microsoft.com/blog/knowledge-cutoff-is-a-poor-proxy-for-model-capability/)).

## When this backfires

- You have no recurring workload. Unrelated one-off tasks give the task set nothing stable to cover, and it costs more than it saves.
- The information boundary leaks. A local install, web search, or a docs server hands the agent the answer, so you measure retrieval instead.
- You copy the sample size. One to five tasks per version carries no signal alone; only the shape across 53 versions does.
- The product post-dates the model. With nothing shipped before the cutoff, the date is informative.
- The aggregate evidence points the other way. LiveCodeBench reports a marked drop on LeetCode problems released after a model's cutoff ([Jain et al., 2024](https://arxiv.org/abs/2403.07974v2)). A later ACL paper removes that decay by rewriting the same problems, so the signal is partly an artifact of question construction ([Zhang et al., 2026](https://arxiv.org/abs/2509.00072v4)).

## Key Takeaways

- The date and the model's product knowledge are two boundaries, here about eight months apart in the direction nobody plans for.
- An 18% pass rate scattered across 53 versions is not a curve you can round to a version number.
- Budget for the expensive direction. Wasted context is recoverable; a wrong pre-cutoff fact reaches review looking fine.
- A measured baseline is pinned to one model. Re-run it on upgrade; do not carry the number forward.

## Related

- [The Consistent Capability Fallacy](../../fallacies/consistent-capability-fallacy.md) — the general case: success on one task does not predict success on a neighboring one.
- [Training-Data Gravity](training-data-gravity.md) — what the model does with a gap at generation time, reaching for the deprecated API that dominates the corpus.
- [Grounding Agents in Code the Model Has Never Seen](../../context-engineering/grounding-zero-prior-code.md) — the zero-prior end of the same axis, where no version of the product is in training data.
- [Answer-Reachable Eval Environments](answer-reachable-eval-environments.md) — why the information boundary has to be enforced before any of these numbers mean anything.
- [Purpose-Built Eval Suites](../../verification/purpose-built-eval-suites.md) — building the workload-shaped task set that replaces the date.
