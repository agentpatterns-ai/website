---
title: "Inferring Agent Failure from Conversation Evidence (Perceived Error)"
term: "Perceived Error"
description: "Grade production conversations for in-transcript evidence the agent got it wrong (corrections, repeated requests, rejected actions) when no exception fired and no rating arrived."
tags:
  - testing-verification
  - evals
  - observability
  - tool-agnostic
aliases:
  - inferred failure signal
  - perceived error evaluation
  - conversation-evidence failure detection
last_reviewed: 2026-08-23
maturity: emerging
---

# Inferring Agent Failure from Conversation Evidence (Perceived Error)

> Perceived error grades a conversation for evidence the user hit a mistake, turning unrated production traces into a triage queue.

Perceived error is a judge that reads a production transcript and answers one question: does this conversation contain evidence the agent made a mistake, misunderstood a request, or took the interaction in the wrong direction? LangChain, which ships it as a managed evaluator, uses those exact terms and returns a binary flag, `true` "when the user appears to perceive an error and `false` otherwise" ([LangChain docs, 2026](https://docs.langchain.com/langsmith/tuned-evaluators)). The flag is a triage filter over traces nothing else would have surfaced. LangChain documents the feedback as an input to investigation, comparison of flagged traces "to find repeated failure modes", eval-dataset curation, and routing "ambiguous conversations for human review" ([LangChain, 2026](https://www.langchain.com/blog/introducing-langsmith-tuned-evaluators-starting-with-perceived-error)).

## When this applies

Three conditions decide whether the signal is worth grading on.

The interaction has to be genuinely multi-turn. The evidence is the user's reaction to the agent's output, so a workload with no reaction turn produces nothing to read. LangChain's implementation states the limit plainly: the evaluator "cannot run on individual runs" ([LangChain docs, 2026](https://docs.langchain.com/langsmith/tuned-evaluators)). A CI agent returning one patch per task has zero coverage here, not partial coverage.

No cheaper ground truth is available. Where the outcome is directly observable, such as a suite that passed or a merged pull request that was later reverted, measure that instead. Perceived error targets the residual case the vendor names: "finding failures that produced no system error or explicit user rating" ([LangChain, 2026](https://www.langchain.com/blog/introducing-langsmith-tuned-evaluators-starting-with-perceived-error)).

You will treat the result as a filter. The metric is named for perception, and most of the trouble below starts when a team forgets that and begins trending it.

## What counts as evidence

LangChain splits the evidence into two tiers ([LangChain, 2026](https://www.langchain.com/blog/introducing-langsmith-tuned-evaluators-starting-with-perceived-error)):

| Tier | Signals |
|------|---------|
| Explicit | User correction, repeated request, rejected action |
| Inferred | Contradictory responses, acknowledged mistakes, persistent misunderstandings, unresolved outcomes |

The explicit tier is close to keyword-detectable. The second tier is the one the source says a model has to infer, so it carries whatever error the judge brings.

## Why it works

The supervision signal already sits in the log, unread. In a multi-turn exchange the user's next message answers the agent's last one, so the transcript records whether the output met the need at the moment it either did or did not. Research on satisfaction estimation establishes that this is readable, independent of any vendor selling an evaluator: large language models "can extract interpretable signals of user satisfaction from their natural language utterances more effectively than embedding-based approaches", in both "general-purpose (ChatGPT and Bing Copilot) and task-oriented (customer service chatbot) conversational systems" ([Lin et al., 2024](https://arxiv.org/abs/2403.12388v2)). A study of WildChat and LMSYS logs finds feedback "commonly found in later turns", and splits it by dataset: "In LMSYS, more feedback exists in later turns, whereas in WildChat feedback spreads more evenly" ([Liu et al., 2025](https://arxiv.org/abs/2507.23158v2)), so a thread-scoped judge with a two-exchange minimum has more evidence in front of it than a turn-scoped one.

The mechanism buys observability. Nothing new gets collected; something already collected gets read.

## When this backfires

Fluent wrong answers leave no trace. In a pre-registered experiment with 308 participants, "the presence of explanations increases reliance on both correct and incorrect responses" ([Kim et al., 2025](https://arxiv.org/abs/2502.08554v1)). A user who accepts a confident, wrong answer files no correction, so the signal is biased toward the errors a user notices and away from the ones that cost most.

A low flag rate does not mean the agent is doing well. The same log analysis found that "users tend to praise model output when it does not refuse to provide answers to user's inadequate requests", and that among prompts drawing positive feedback "many of these prompts have the goal of 'jail-breaking' the LLM" ([Liu et al., 2025](https://arxiv.org/abs/2507.23158v2)). Quiet threads can track compliance rather than correctness.

Abandonment is invisible by construction. Eligibility requires two human-AI message pairs plus an elapsed idle period ([LangChain, 2026](https://www.langchain.com/blog/introducing-langsmith-tuned-evaluators-starting-with-perceived-error)), so a user who gives up after one exchange never enters the graded population at all.

The headline accuracy claim is a vendor self-report. LangChain says its post-trained judge "outperformed every frontier model in our benchmark while reducing evaluation cost by 82%", with early-partner savings reaching 98% ([LangChain, 2026](https://www.langchain.com/blog/introducing-langsmith-tuned-evaluators-starting-with-perceived-error)). No precision or recall accompanies it, and the benchmark is unpublished. A Findings of ACL 2025 study reports that this is the result which travels worst: fine-tuned judges "achieve high performance on in-domain test sets, even surpassing GPT-4" while underperforming it "across several dimensions, including generalizability, fairness and adaptability", because such a judge "inherently operates as a task-specific classifier" ([Huang et al., 2025](https://arxiv.org/abs/2403.02839v4)).

Judges age against a moving agent. Across two reasoning datasets, three fine-tuning algorithms, and three backbone models, "future-proofing is challenging for most models", and all models tested degraded when moving from training questions to unseen ones ([Singh et al., 2025](https://arxiv.org/abs/2509.23542v2)). A managed evaluator absorbs the work LangChain itemizes, which includes "producing labels, selecting and benchmarking a judge, and maintaining it as models and production behavior change" ([LangChain, 2026](https://www.langchain.com/blog/introducing-langsmith-tuned-evaluators-starting-with-perceived-error)). What you give up in return is control of the judge's version history.

Trending the flag as a defect rate measures assertiveness too. A user pushing back after changing their own mind scores identically to one correcting a real mistake, because the output is a single boolean ([LangChain docs, 2026](https://docs.langchain.com/langsmith/tuned-evaluators)).

## Example

The managed implementation's eligibility gate is the concrete form of the coverage limit. A thread gets graded only when all of the following hold ([LangChain docs, 2026](https://docs.langchain.com/langsmith/tuned-evaluators)):

- The tracing project uses threads. Individual runs are never eligible.
- A non-empty user message is followed by a non-empty assistant message, in a supported message-list format.
- The thread contains at least two traces.
- The project's thread idle time has elapsed, and the thread matches the evaluator's filters and sampling rate.

Evaluation then completes within 12 hours of eligibility ([LangChain, 2026](https://www.langchain.com/blog/introducing-langsmith-tuned-evaluators-starting-with-perceived-error)). Read that gate as your denominator before reading any flag rate computed over it.

## Key Takeaways

- Scope the signal before you buy it. No reaction turn means no coverage, and the eligibility gate defines the population every flag rate is computed over.
- Decide the destination before you switch it on. A binary perception flag belongs in a work queue that someone drains, not on a quality dashboard where its rate gets trended.
- Pair it with something that catches silent failure. Confidently-wrong answers users accept are the documented blind spot, so an outcome check or a sampled human audit has to cover what the transcript cannot.
- Ask any managed-evaluator vendor for precision and recall on your own traces before trusting a benchmark win, because in-domain judge performance is the finding least likely to generalize.

## Related

- [Multi-Turn Conversation Evaluation](multi-turn-conversation-evaluation.md) — scores a conversation against a rubric once you have decided to look at it, where perceived error decides which ones to look at.
- [Corpus-Level Trace Diagnostics for LLM Agents](corpus-level-trace-diagnostics.md) — the scout-investigator pipeline that turns a pile of flagged traces into named recurring failure modes.
- [Macro Evals for Agentic Systems](macro-evals-agentic-systems.md) — the population-level layer above per-trace grading, including the judge-cost economics this page leaves alone.
- [Using the Agent to Analyze Its Own Evaluation Transcripts](agent-transcript-analysis.md) — the same read-the-transcript move applied to eval runs rather than production threads.
- [Detecting Self-Preference in a Single LLM Judge](judge-self-preference-detection.md) — a judge bias that survives a strong benchmark score, and the reason to stratify verdicts before trusting an aggregate.
