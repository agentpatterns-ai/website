---
title: "Exhaustive Retrieval for Listing Questions"
term: "Exhaustive Retrieval for Listing Questions"
description: "Ranked retrieval returns the top k passages with no signal that the answer needed more, so a listing question needs an external completeness signal before an enumeration loop is worth building."
aliases:
  - listing question retrieval
  - set-valued retrieval completeness
  - complete enumeration retrieval
tags:
  - context-engineering
  - workflows
  - technique
  - tool-agnostic
last_reviewed: 2026-08-12
maturity: emerging
---

# Exhaustive Retrieval for Listing Questions

> Ranked retrieval returns the best k passages and reports no truncation, so a listing question needs a completeness signal outside the ranker.

A listing question asks for every item that matches. Which modules call this deprecated API, which config flags gate the rollout: the correct answer to each is a set. Ranked retrieval hands back the top k passages and says nothing about what fell below the cut, so the agent writes a fluent answer that omits the rest ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-listing-questions-when-the-answer-is-every-passage-not-the-top-one/)).

## When this applies

All four conditions must hold:

- The correct answer is a set whose size you do not know in advance.
- The corpus is too large for the context window, so you cannot skip retrieval and read everything.
- No deterministic index already enumerates the set. A codebase or a schema'd database does not qualify, because an AST walk or a `SELECT` is complete by construction.
- You hold a completeness signal external to the model. Without one the loop exits on the model's own judgment, which is where it breaks.

Otherwise a single pass is the stronger default. Adaptive-k picks k from the distribution of query-passage similarity scores in one shot, matches or outperforms fixed-k baselines, and uses up to 10× fewer tokens than full-context input while retrieving 70% of relevant passages, with no fine-tuning and no extra inference calls ([Taguchi et al., 2025](https://arxiv.org/abs/2506.08479v3)). That work also reports iterative methods such as Self-RAG struggling on aggregation QA, where optimal context size varies by query.

## Pick the completeness signal first

Three signals can tell a retrieval loop it is finished, and their strength differs sharply ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-listing-questions-when-the-answer-is-every-passage-not-the-top-one/)).

| Signal | What it reads | Strength |
|--------|---------------|----------|
| Structural | A region the document itself delimits: section tree, table rows, numbered list | Complete by construction |
| Cardinality cue | A count stated in the text, such as "the Framework Core consists of six Functions" | Verifiable against the extracted set |
| Model self-assessment | The model's own verdict on whether its answer looks complete | Weakest |

Design down that list. Self-assessment is the fallback, and the calibration evidence runs against it: nominal 99% confidence intervals from several current models cover the true answer only 65% of the time on average ([Epstein et al., 2025](https://arxiv.org/abs/2510.26995v1)). A loop whose only exit is the model reporting that it found everything inherits that overconfidence.

## The enumeration loop

Where only semantic aggregation is left, the loop retrieves broadly, extracts candidate items, tests the completeness signal, then expands keywords and re-retrieves when the test fails. It stops on any of three conditions: no new passages were retrieved, the completeness check passed, or the iteration cap was hit, set to three in the reference implementation ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-listing-questions-when-the-answer-is-every-passage-not-the-top-one/)). The cap is load-bearing, because new items per pass decay quickly and an uncapped sweep buys latency instead of coverage. [Loop budgeting](../loop-engineering/loop-budgeting.md) covers how to size it.

## Why it works

Ranked retrieval optimizes precision at the head of a list against a fixed budget k, which is the wrong objective for a query whose answer is a set. The field treats this as its own problem rather than a tuning detail. NIST ran a [TREC Total Recall Track](https://trec.nist.gov/pubs/trec24/papers/Overview-TR.pdf) for tasks needing near-complete recall plus an explicit stopping rule, and benchmarks such as [QUEST](https://arxiv.org/abs/2305.11694v2) and [RoMQA](https://arxiv.org/abs/2210.14353v2) exist because retrieval systems struggle once one query maps to many correct answers.

Nothing in a ranker's output separates "these five are all of them" from "these five scored highest among nine." The loop works when it substitutes an external oracle for that missing signal, and the substitution is the causal ingredient rather than the iteration. On Total Recall QA, extra agent sub-queries "primarily retrieve more distracting entities and very few new gold entities" ([Rafiee et al., 2026](https://arxiv.org/abs/2603.18516v1)).

## When this backfires

- No external signal is available. The exit collapses to self-assessment and the loop stops confidently at an arbitrary point.
- A deterministic index exists. For "which modules call this deprecated API," an AST walk enumerates exactly, in one pass, with a guarantee the loop cannot offer.
- The true answer set is large, as in RoMQA ([Zhong et al., 2022](https://arxiv.org/abs/2210.14353v2)). Raising document count degrades most models by up to 20% even at constant context length ([Levy et al., 2025](https://arxiv.org/abs/2503.04388v3)), so a completed sweep can yield a worse answer from better evidence.
- Synthesis is the real bottleneck. Under oracle retrieval on TRQA-Wiki1, Claude Sonnet 4.5 reaches 50.30% exact match and GPT-5.2 reaches 56.80%, with over 90% of remaining errors attributed to reasoning ([Rafiee et al., 2026](https://arxiv.org/abs/2603.18516v1)). Fixing coverage does not move the dominant error source.
- Latency or cost dominates. Every iteration adds a retrieval call and an inference round trip against a shrinking return.

## Example

Two documented runs show a cardinality cue doing work the model's own verdict could not ([Shi, 2026](https://towardsdatascience.com/loop-engineering-for-listing-questions-when-the-answer-is-every-passage-not-the-top-one/)).

Against the NIST Cybersecurity Framework, pattern matching returned six Functions on the first pass. The document states on page 8 that the Framework Core consists of six Functions, so the cardinality check confirmed the extraction and the loop exited after one iteration.

Against the Transformer paper, the first extraction found two regularization techniques where the text states there are three. The mismatch triggered a second pass, which recovered attention dropout through keyword expansion. Neither run asked the model to certify its own completeness.

## Key Takeaways

- Treat the completeness signal as the design input. Structural extraction, a stated count, and model self-assessment are not interchangeable, and only the first two hold up when the model is miscalibrated.
- Check for a deterministic index before writing any loop. Code, schema'd data, and documents with machine-readable structure are enumerable exactly, so a loop over them adds cost and a failure mode.
- Cap iterations and instrument new items per pass. Extra sub-queries mostly surface distractors, so the cap protects against paying for coverage that is not arriving ([Rafiee et al., 2026](https://arxiv.org/abs/2603.18516v1)).
- Measure whether the retrieved set covers every answer. A recall@k score computed against one gold passage cannot see the failure this technique targets.
- Budget for the synthesis ceiling. Complete retrieval still leaves frontier models near half the answers on Total Recall QA, so retrieval work alone will not close the gap ([Rafiee et al., 2026](https://arxiv.org/abs/2603.18516v1)).

## Sources

- Angela Shi, [Loop Engineering for Listing Questions](https://towardsdatascience.com/loop-engineering-for-listing-questions-when-the-answer-is-every-passage-not-the-top-one/) (2026) — the loop shape, signals, and termination conditions
- Rafiee et al., [Total Recall QA](https://arxiv.org/abs/2603.18516v1) (SIGIR 2026) — agent scores, oracle ceiling, distractor finding
- Taguchi, Maekawa, Bhutani, [No Tuning, No Iteration, Just Adaptive-k](https://arxiv.org/abs/2506.08479v3) (EMNLP 2025) — the single-pass alternative
- Levy et al., [More Documents, Same Length](https://arxiv.org/abs/2503.04388v3) (2025) — document count degrades accuracy on its own
- Epstein et al., [LLMs are Overconfident](https://arxiv.org/abs/2510.26995v1) (2025) — calibration evidence against self-assessment
- Malaviya et al., [QUEST](https://arxiv.org/abs/2305.11694v2) (ACL 2023) and Zhong et al., [RoMQA](https://arxiv.org/abs/2210.14353v2) (2022) — multi-answer retrieval benchmarks
- NIST, [TREC 2015 Total Recall Track Overview](https://trec.nist.gov/pubs/trec24/papers/Overview-TR.pdf) — prior art on stopping rules

## Related

- [Convergence Detection in Iterative Agent Refinement](../loop-engineering/convergence-detection.md) — stopping signals read from the agent's own output, where these are read from the corpus
- [Silent Handoff Failure in Delegated Code Search](silent-handoff-failure-delegated-search.md) — the other way a search result comes back incomplete without saying so
- [LLM-Driven Logical Retrieval](llm-driven-logical-retrieval.md) — Boolean queries whose empty result set is a sharp not-found signal
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — the on-demand retrieval pattern this technique modifies
- [Loop Budgeting](../loop-engineering/loop-budgeting.md) — choosing the iteration cap that bounds the enumeration sweep
- [Long Context vs Retrieval: The Break-Even Decision](long-context-vs-retrieval-break-even.md) — what the top-*k* completeness gap costs to close by reading the whole corpus instead
