---
title: "Gate Generation on Retrieval Sufficiency, Not Model Confidence"
term: "Retrieval Sufficiency Gate"
description: "Where a codebase's own code dominates, the model has no prior to be uncertain against, so a pre-generation gate has to score retrieval coverage from the repository rather than read confidence off the model."
aliases:
  - retrieval confidence layer
  - structural sufficiency gating
  - pre-generation retrieval check
tags:
  - context-engineering
  - tool-agnostic
  - arxiv
  - rag
last_reviewed: 2026-09-13
maturity: emerging
---

# Gate Generation on Retrieval Sufficiency, Not Model Confidence

> Where a codebase's own code dominates, the model has no prior to be uncertain against, so a pre-generation sufficiency signal must come from the repository.

A retrieval sufficiency gate sits between retrieval and generation. It scores whether the retrieved context structurally covers the query; below a calibrated threshold it fires a follow-up retrieval or routes the output to human review instead of generating against thin context.

The named proposal is RCL, which pairs a call-graph-derived coverage score with a novelty score estimating how far a query depends on knowledge outside the model's prior ([Ravuri, arxiv 2609.11023v1, 2026](https://arxiv.org/abs/2609.11023v1)). Read it as a design, not a result: a single-author position paper with no HTML rendering on arXiv and an evaluation section I could not verify. No number below is attributed to RCL.

## When a structural gate earns its cost

Three conditions have to hold together, and the first rules out most candidates.

The private surface has to be large enough that a novelty score varies across queries. A thin wrapper over a public SDK scores near zero everywhere, so the gate never fires and the layer is pure overhead.

The call graph has to be trustworthy. Reflection, dependency injection, and dynamic dispatch leave holes in a static graph, and coverage computed over holes is wrong in both directions.

Something downstream has to consume the "insufficient" verdict. Labeling output for human review needs a staffed queue, or the gate turns a wrong answer into a stalled one.

If a fast type-checker already runs in the loop, start there. The compiler answers "did you call an API that does not exist" exactly, after generation, with no threshold to calibrate and no graph to keep current.

## What the gate reads

Most adaptive-retrieval work reads the model. TARG takes token entropy and logit margins from a draft prefix, needs no training, and cuts retrieval by 70 to 90 percent while matching EM/F1 across five QA benchmarks ([Wang et al., arxiv 2511.09803v2](https://arxiv.org/abs/2511.09803v2)). On public corpora that signal is enough, and far cheaper than a maintained call graph.

A structural gate reads the repository instead: which symbols the query touches, which of their callers and callees appear in the retrieved chunks, and how much of that surface has no public analogue. The two signals answer different questions — whether the model feels uncertain, and whether the evidence could support a correct answer at all.

## Why it works

Models do not abstain when their context is insufficient. They answer wrong. Joren et al. stratified RAG errors by context sufficiency and found that Gemini 1.5 Pro, GPT-4o, and Claude 3.5 "excel at answering queries when the context is sufficient, but often output incorrect answers instead of abstaining when the context is not" ([arxiv 2411.06037v3](https://arxiv.org/abs/2411.06037v3)). The uncertainty a retry needs is missing exactly when it would be useful.

On private code it is worse than missing. The correct API carries no probability mass in the pretrained distribution, so there is nothing for the model to be uncertain against, and handing it the documentation does not close the gap: "even given accurate required knowledge, LLMs still struggle to invoke private-library APIs effectively" ([Zhang et al., arxiv 2603.15159v4](https://arxiv.org/abs/2603.15159v4)).

A structural score comes from the repository rather than the model, which is why it survives that case. Julka measured the blind spot by separating the answer surface, the retrieved evidence, and the retrieval state. At five samples per question, 42% of KG-RAG errors and 59% of dense-retrieval errors carried zero answer dispersion, so sampling agreement ranked none of them, "while evidence- and retrieval-state checks still flag most of them" ([arxiv 2606.22728v1](https://arxiv.org/abs/2606.22728v1)).

## When this backfires

- Thin retrieval is not where most failures live. In ReCUBE's full-context setting, GPT-5 reached "only 37.57% strict pass rate" ([arxiv 2603.25770v1](https://arxiv.org/abs/2603.25770v1)). A gate that catches only insufficient context leaves the larger share untouched.
- The gate costs coverage. Accepting an answer only when the answer, evidence, and retrieval checks all agree reached 91.9% pooled precision against a 69.7% accept-all rate, and Julka names the trade plainly: "The cost is coverage: it certifies only 7.7% of answers as low-risk" ([arxiv 2606.22728v1](https://arxiv.org/abs/2606.22728v1)).
- Dynamic code defeats the coverage score. Python metaprogramming, Java reflection, and container-wired dependencies all produce call edges a static analysis never sees.
- Thresholds drift silently. The gate fires below a calibrated threshold ([Ravuri, arxiv 2609.11023v1](https://arxiv.org/abs/2609.11023v1)), calibration is per repository and per model, and a gate that has stopped firing looks exactly like a codebase that got easier.
- Fine-tuning has the stronger evidence. PriCoder's graph-based training-data synthesis added over 20% pass@1 in many settings on private-library benchmarks ([Zhang et al., arxiv 2603.15159v4](https://arxiv.org/abs/2603.15159v4)). That result is measured; a sufficiency gate's is not.

## Key Takeaways

- Decide what the gate reads before deciding where to put it. Model-internal confidence and structural coverage fail on different queries, and only the second one works where the model has no prior.
- Do not build this for a thin wrapper over a public SDK. The novelty score has to vary across queries or the gate is dead weight.
- Price the coverage loss up front. Most queries will not clear a strict gate, and where they go — a second retrieval, a review queue, or generation anyway — is the design decision, not the threshold.
- RCL is a design, not a measured result. Take the framing that structure and model confidence are different signals; do not take the architecture on trust ([arxiv 2609.11023v1](https://arxiv.org/abs/2609.11023v1)).
- A compiler is a sufficiency oracle that needs no calibration. Reach for the gate when the failure is silent, not when a type error would have caught it.

## Related

- [Grounding Agents in Code the Model Has Never Seen](grounding-zero-prior-code.md) — the same zero-prior premise, answered with a static always-loaded identity layer rather than a runtime gate. Read that page for what to put in context; this one for whether to generate at all.
- [Exhaustive Retrieval for Listing Questions](exhaustive-retrieval-for-listing-questions.md) — the same shape in question answering: the ranker reports no truncation, so the completeness signal has to come from outside it.
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md) — the call graphs and dependency edges a structural coverage score is computed over.
- [Corpus Shape as a Retrieval Design Constraint](corpus-shape-retrieval-architecture.md) — the diagnostic that separates retrieval failures a re-ranker can fix from recall ceilings above tuning.
- [Evidence-Conditioned Execution: Gate Edits on Observations](../verification/evidence-conditioned-execution.md) — the sibling gate one stage later, holding the edit until the trajectory shows the observations it depends on.
- [State-Conditioned Evidence Selection for Mid-Task Retrieval](state-conditioned-evidence-selection.md) — scores sufficiency against what the agent has not yet read, rather than against the query.
