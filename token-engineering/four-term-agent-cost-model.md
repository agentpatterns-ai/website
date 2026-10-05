---
title: "The Four Terms That Decide What an Agent Task Costs"
term: "Four-Term Agent Cost Model"
description: "An agent task's input bill is turns times average context times effective input price, so turns, cache-read share and model price compound while output adds."
tags:
  - token-engineering
  - cost-performance
  - claude
  - arxiv
aliases:
  - four-term agent cost model
  - agent task cost decomposition
  - agent task cost breakdown
applies_to: "claude-code@2.x"
last_reviewed: 2026-10-01
maturity: emerging
---

# The Four Terms That Decide What an Agent Task Costs

> An agent task's input bill is turns times average context times effective input price, so turns and cache hit rate compound.

The four-term agent cost model prices one task as turns, cache-read share, output tokens, and model price. Turns, cache-read share and model price multiply each other on the input side of the bill, so they are not four independent dials. Output tokens are the one term that adds rather than multiplies. Claude Code's cost guidance names the same four: "Four things set what the loop costs" ([claude.dev, "What a task costs on Opus 5.5", 2026-09-25](https://claude.dev/blog/what-a-task-costs-on-opus-5-5/)). Use it to diagnose a finished session, not to forecast the next one.

## The conditions that bound it

Three limits bound the arithmetic, and all three come from the source that publishes it.

It prices API list rates. On a subscription plan, "The dollar figure is computed on your machine at list price, so on a subscription it is a guide to how much work you did, not a bill" (claude.dev).

Cache writes are a missing fifth term, and not a rounding error. The published examples "leave out cache writes" by the author's own statement. On Claude Opus 5.5 a five-minute write lists at $5 per million tokens against a $0.20 read ([Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)). One write costs 25 reads, so a session that pauses, or that [switches model mid-run](../patterns/anti-patterns/mid-session-config-cache-invalidators.md), pays a line the four terms never show.

Every figure is a worked illustration. The author says so directly: "The token counts are illustrations." Carry the method, never the numbers.

## What each term is worth

Every ratio below falls out of the Opus 5.5 price row: $4 per million input tokens, $20 per million output, $0.20 per million cache reads ([Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)).

| Term | Why it moves the bill | Size on Opus 5.5 |
|---|---|---|
| Turns | Each turn resends every earlier turn | 40 turns over a context growing 20K to 120K send about 2.8M input tokens |
| Cache-read share | The repeated prefix bills at the read rate | A cache hit costs 5% of the input price |
| Output tokens | Priced highest, and thinking counts in full | Output is 5x input and 100x a cache read |
| Model | Sets the price of every token in the session | Fable 5.1 lists at 2.5x the Opus 5.5 input and output price |

The price list hides what the first two rows do together. That same 2.8M input tokens costs $11.20 with no cache, $1.62 at a 90% hit rate, and about $0.99 at 96% (claude.dev). Cutting the task to 25 turns moves it to roughly 1.75M tokens and about $1.02.

## Why it works

The loop resends state, which makes input cost a product instead of a sum. Claude Code "sends your full conversation with every request, and each time Claude uses tools it sends another request carrying that batch of tool results" ([Manage costs effectively](https://code.claude.com/docs/en/costs)). A task's input bill is therefore turns multiplied by the average context each turn carries, multiplied by the effective per-token price, and prefix caching sets that third factor. Turns and cache share scale the same quantity, so a long session with a cold cache pays both penalties at once. Output sits outside that product, and reasoning is billed whether or not you see it: "You are billed for the full thinking process, not the thinking content visible in the response" ([Steering thinking](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost)). The asymmetry follows from that split. The published example puts a task's 60K output tokens at $1.20, "the same as reading 6M tokens from cache". Six points of cache hit rate move the same session's input line by about 40%.

Independent measurement sizes the cache term. Across more than 500 agent sessions on three vendors, prompt caching cut API cost by 41% to 80% ([Lumer et al., "Don't Break the Cache", arXiv:2601.06007v2](https://arxiv.org/abs/2601.06007v2)). Those sessions used a 10,000-token system prompt, and the authors credit most of the saving to caching that stable prompt. A coding session that grows past 100K weights the terms differently.

## Reading the terms off a session

Run `/usage` at the end of a task. A low cache share points at an invalidation, so look for a pause, a model switch or a mid-session config change. Heavy output on a small change points at effort set too high, or at a retry loop. When total input runs many times the size of the conversation, the session took many turns, and the transcript shows where the loop repeated. Each reading has a different fix, which is the reason to decompose at all.

## When this backfires

Minimizing one term raises another. GitHub shortened its agent's tool output, won on tokens per call, and lost on the task, because the omitted text forced reruns that added turns: "We saved tokens locally and spent more globally" ([GitHub Blog, 2026-09-02](https://github.blog/ai-and-ml/github-copilot/how-we-make-ai-coding-more-cost-efficient-without-sacrificing-task-quality/)). GitHub bounds that result to "the integration and workloads we tested, not to every RTK configuration or to output compression in general". What survives the caveat is that an efficiency change has to be priced across the whole task.

Instructing the model to economize backfires, because it changes which work the model will attempt at all. Cursor put a token-thrift instruction in its harness prompt and found "this message was impacting the model's willingness to perform more ambitious tasks or large-scale explorations" ([Cursor, "Improving Cursor's agent for OpenAI Codex models"](https://cursor.com/blog/codex-model-harness)). The bill falls, and the task goes unfinished. See [Token Preservation Backfire](../patterns/anti-patterns/token-preservation-backfire.md).

Two shapes of work fall outside the model entirely. Below a provider's minimum cacheable prefix the cache term cannot engage: "When prompts fall below these thresholds, caching cannot activate" ([Lumer et al., arXiv:2601.06007v2](https://arxiv.org/abs/2601.06007v2)). That study still measured positive cost savings at every prompt size it tested, so read the floor as a reason to check your own numbers rather than to skip caching. A one-shot call cannot recover the write premium either, since "caching pays off after one cache read for the 5-minute duration" ([Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)). In the other direction, agent teams "use approximately 7x more tokens than standard sessions when teammates run in plan mode" ([Manage costs effectively](https://code.claude.com/docs/en/costs)), so terms priced on one context window miss most of a team run.

## Key Takeaways

- Price a task, not a token. Turns and cache share multiply the same quantity, so they compound.
- Derive the ratios yourself from the price table. On Opus 5.5 output is 5x input and 100x a cache read, and a five-minute cache write is 25 reads.
- Treat the model as a diagnostic. Turns and cache hit rate are outputs of a run, so the decomposition explains a bill it cannot predict.
- Cache writes are the term the published arithmetic drops. Add them back before pricing a session that switches model or pauses.

## Related

- [Mid-Session Config Changes as Invisible Cache Invalidators](../patterns/anti-patterns/mid-session-config-cache-invalidators.md) — what breaks the cache-read term, and what the next turn pays
- [Request Shaping to Cut Wasted Agent Turns](request-shaping-wasted-turns.md) — the turn term, and where more specification stops paying
- [Harness-Controlled Token Economics (The Harness Effect)](harness-token-economics.md) — the same bill read across orchestration layers rather than within one session
- [The Token Price Index Fallacy in Agent Cost Planning](../fallacies/token-price-index-fallacy.md) — why a published price-per-token figure answers a different question
- [GitHub's Copilot Cost Levers at Constant Task Quality](copilot-cost-levers-fixed-quality.md) — four harness levers measured against task quality, not tokens per call
