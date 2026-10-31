---
title: "Model Qualification for Self-Managed Compaction"
term: "Model-Qualified Context Self-Management"
description: "Handing a model the compaction decision pays off only when it compacts at all, keeps hand-offs short, and the vendor charges dearly for cache reads."
aliases:
  - self-managed context qualification
  - model-decided compaction
  - prompt-only context management
tags:
  - context-engineering
  - cost-performance
  - arxiv
  - tool-agnostic
last_reviewed: 2026-10-29
maturity: emerging
---

# Model Qualification for Self-Managed Compaction

> Self-managed compaction pays off only when the model compacts at all, keeps its hand-offs short, and the vendor charges dearly for cache reads.

Whether to replace a token threshold with model-decided compaction depends on which model you run. Across seven frontier models given the same two tools and the same paragraph of guidance, the two that managed their context well cut session cost by 16 to 58%, while another ran 20% more expensive than with no context management at all ([CTXAgent, arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)). Qualify the model against three measurements before you take the window out of your config.

## The three measurements

Run repeated long sessions with the context tools and repeated sessions without, then read off:

| Measurement | Disqualifies when |
|---|---|
| Compact calls per session | Zero, or so frequent that cache invalidation outruns the saving |
| Hand-off summary length | Summary output cost erases input savings against the baseline you test |
| Vendor cache-read price, as a fraction of fresh input | Cheap — a fortieth rather than a tenth |

The third says nothing about your model's behavior and still decides the sign of the result. Two models that kept their context equally small diverged on the price list alone: "At list prices, a similar behaviour therefore yields a reduction of around 50 % for Astra and of around 0 % for Fable" ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)).

## What a qualifying model looks like

Claude Opus 5.5 passed all three. It compacted three to four times per mixed session, always at a task boundary. Its hand-off summaries ran 1 to 2k tokens and its live context never exceeded 80k. Opus, Sol, and Astra all cut at 50k to 80k, "around a third of the occupancy at which Claude Code or Codex would cut." For Opus the bill came in 34% below the cheapest Claude Code setting tested and 49% below its default, at the same number of model requests, 233 against 228, and at about the same benchmark score ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)).

Opus saved around 30% or more in most of the paper's harness-comparison settings; treat that as the paper's figure, not one you inherit. Three of the seven models "do not manage their context successfully" ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)).

## Why it works

The bill for a long session is dominated by the prefix re-sent on every turn: "The dominant cost of a long agent session is the prefix re-sent with every request" ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)). Cutting at 50k to 80k instead of the roughly 168k where Claude Code cut shrinks that prefix for every remaining turn, so an earlier cut compounds. A threshold cannot find the earlier cut, because the signal is not in the token count: "The model, which is the only party that knows that a task has just finished and that the files read for it are no longer needed, is not consulted, and the operator has to choose a window that suits every task at once" ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)).

One paragraph of guidance hands over that knowledge. The same paragraph carries the ceiling on it: "Every rewrite invalidates the prompt cache from the cut, so do not rewrite after every step" ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)). That is the ordinary [prompt-cache arithmetic](prompt-caching-architectural-discipline.md) of any prefix rewrite. Frequency and summary length both bill against the saving, so net cost is the product of three model-specific quantities and one vendor-specific one. That product, not the policy, is what differed across the seven models.

## When this backfires

- Some models never fire the tool. Haiku 5.5 and Muse Wonder made no compact calls in six sessions, and their curate calls invalidated cache while shrinking the context by a few thousand tokens. Muse Wonder's bill rose 20%, dominated by "provider-side cache misses that occur with no rewrite at all, to which the curate calls add" ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)).
- A model that acts can still lose to a threshold harness on hand-off length. GPT-6.1 Sol cut cost against no context management, yet compacted about eight times per mixed session: "Its hand-off summaries are considerably longer, which eats up the savings: on the mixed sessions it costs 16 % more than Codex at 200k." On a 212-turn session the self-managed arm wrote five times Codex's output tokens and cost $26.29 against $12.14 ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)).
- A model can act inconsistently. Sonnet 5.5 compacted in one session of three and behaved like the no-tools arm in the other two, for a mean cost ratio of 0.84 ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)). A policy that fires a third of the time is not one you can budget against.
- Standing instructions get thinner protection, since more cuts mean more chances to drop a rule. Adherence held above 99% on the mixed sessions for every model except Muse Wonder, at 83%, and fell to 80 to 99% on the harder ones ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)). The compactors in a separate study retain only 17% of injected side constraints on average ([Lost in Context Compaction, arxiv 2608.11242v2](https://arxiv.org/abs/2608.11242v2)).
- The published figure is not a procurement number. Each vendor CLI ran on its own vendor's model, so harness and model are confounded, and the run count was small ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)). Identical runs of one agent-model pairing "varied more than the pairings differed from one another, so comparisons of a few runs ranked them unreliably" ([Identical Runs, Different Results, arxiv 2609.33812v1](https://arxiv.org/abs/2609.33812v1)).

Keeping the threshold has a real case: one number, auditable, unchanged by a model upgrade. Self-management moves cost and retention into a property you re-measure on every model bump. Then again, the threshold you keep may not be doing the job you think. Claude Code did not auto-compact at its default window for Opus 5.5 at all, and "its context reached 277k tokens without a cut" ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)).

Earlier work reached the opposite conclusion on weaker models, and it still holds there. SelfCompact is blunt about the prompt-only form: "The tool alone is unevenly used across open-weight models, often invoked at unhelpful moments or not at all." It paired the tool with a rubric, and in its agentic-search setup added four admission gates plus a backstop that "forces a compress once the prompt crosses" 30% of the window regardless of the rubric ([arxiv 2606.23525v2](https://arxiv.org/abs/2606.23525v2)). Where a model fails qualification, that rubric and gate set is the fallback.

## Example

The whole policy for a qualifying model is one paragraph, and the load-bearing parts are the trigger, the hand-off contents, the cache warning, and the carve-out. From the paper's own system prompt ([arxiv 2610.34425v1](https://arxiv.org/abs/2610.34425v1)):

> compact\_context is for task boundaries: when a substantial body of work is finished and the next work does not need its details, replace it by a handoff summary (goal, decisions and why, files changed, results, open issues, segment ids worth recalling)

The same paragraph carries the carve-out that keeps the side-constraint failure out of scope: facts the user stated and standing instructions must survive both tools. Write that line, then test that it held. Adherence is the measurement that slipped on the hard sessions.

## Key Takeaways

- Qualify the model, not the pattern. Run repeated long sessions with the tools and without, and compare the bill and the score before you remove the threshold.
- Curation alone can raise cost: Muse Wonder cost 20% more, while Haiku's cost ratio was 0.99 against no management.
- Check the hand-off length, since output tokens are the leak that turned an eight-cuts-per-session model into one that cost 16% more than Codex at 200k.
- Look up your vendor's cache-read-to-input ratio before you estimate the saving. At a fortieth, there is almost nothing to recover.
- Re-measure on every model upgrade. One instruction spanned a 16 to 58% cut for two models and a 20% increase for a third, so the policy's value is a property of the pairing.

## Related

- [Agent-Initiated Rubric-Gated Self-Compaction](agent-initiated-self-compaction.md) — the scaffolded form, with a firing rubric for models that fail qualification.
- [Scoring a Compaction Policy on Latency and Billed Cost](compaction-policy-latency-and-cost.md) — how to run the measurement this page asks for, once you have two arms to compare.
- [Per-Agent Compaction Windows for Orchestrator and Worker](per-agent-compaction-window.md) — the declarative alternative, where the harness keeps the trigger per agent.
- [Per-Type Retention Policy for Agent Compaction (Knowledge Triage)](per-type-retention-under-compaction.md) — pinning standing constraints so earlier, more frequent cuts stop dropping them.
- [Size Agent Comparisons by Run-to-Run Variance](../verification/size-agent-comparisons-by-run-variance.md) — how many runs a cost comparison like this one needs before it ranks anything.
- [Model Rankings Reverse Across Agent Harnesses](../patterns/agent-design/model-rankings-reverse-across-harnesses.md) — why the harness-versus-harness number travels badly to a different model.
