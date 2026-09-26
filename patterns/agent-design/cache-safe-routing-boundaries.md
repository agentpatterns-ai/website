---
title: "Cache-Safe Routing Boundaries: Where a Router May Act"
term: "Cache-Safe Routing Boundaries"
description: "A model choice may only move where no warm prompt cache dies: session start, a fresh side lane, or a subagent launch. A mid-task switch pays two cold writes."
tags:
  - agent-design
  - cost-performance
  - arxiv
  - tool-agnostic
aliases:
  - natural cache boundaries
  - cache boundary routing
  - cache-safe model switching
last_reviewed: 2026-09-25
maturity: emerging
---

# Cache-Safe Routing Boundaries: Where a Router May Act

> The prompt cache decides where a router may act: a session's first prompt, a fresh side lane, a subagent launch.

Cache-safe routing boundaries are the three points in an agent session where changing the model destroys no warm prompt cache. Move work anywhere else and the cheap cache reads a running turn lives on become a full cold write of the whole conversation. When the user returns to the original model, that is a second cold write ([Abbasi, Aqrawi and Kwartler, arXiv 2609.28919v1 §4.1](https://arxiv.org/abs/2609.28919v1)).

## The conditions that make this bind

Three things have to hold before the boundary matters. Cache reads must be discounted: Anthropic bills them at 0.1x the input price, 0.025x on Fable 5.1, and bills writes at 1.25x for the five-minute cache and 2x for the hour ([Anthropic, Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)). The cache must belong to one model: "Each model has its own cache. Switching with `/model` means the next request reads the entire conversation history with no cache hits, even though the content is identical" ([Claude Code, Prompt caching](https://code.claude.com/docs/en/prompt-caching#switching-models)). And the cache must be warm. Claude Code acts on that last condition itself, asking you to confirm a switch only while the cache still lives: "once that time passes, the cache has expired, so Claude Code switches without asking" ([Claude Code](https://code.claude.com/docs/en/prompt-caching#switching-models)). A cold return is a free re-choice.

## The payback arithmetic

A turn with `k` tool steps is `k+1` requests, each re-sending the whole conversation, so "an agentic turn of eighteen tool steps re-sends the conversation nineteen times" ([arXiv 2609.28919v1 §2.1](https://arxiv.org/abs/2609.28919v1)). Write `R` for a model's cache-read price per token and `W` for its write price. A mid-task switch pays back only if the cheaper stretch lasts

`n* = (W_target + W_home − R_target − R_home) / (R_home − R_target)` requests,

falling to `(W_target − R_target) / (R_home − R_target)` when the turn never returns. On Anthropic's list prices of 21 September 2026 that is 27 requests from Opus 5 down to Sonnet 5 with a return and 8 without, and 291 and 46 from Fable 5.1 ([arXiv 2609.28919v1 §4.2](https://arxiv.org/abs/2609.28919v1)). Most tasks end well before either figure.

The three boundaries dodge the payment. Session start has no prefix to lose. A side lane seeded with a compact project ledger writes a few thousand tokens instead of re-reading the transcript: a one-line change inside an 805k-token session costs $0.88 in place on Fable 5.1 against $0.36 in a ledger lane on Sonnet 5. The lane owes the home conversation two things on its way out, and both are easy to forget: one empty request to refresh the home cache, then its result appended as a note rather than edited into an earlier turn ([arXiv 2609.28919v1 §4.4](https://arxiv.org/abs/2609.28919v1)). A subagent is a fresh conversation, so picking its model costs nothing in cache terms, and five typical subagents cost $4.88 inheriting Fable 5.1 against $1.27 on Sonnet 5 ([arXiv 2609.28919v1 §4.4](https://arxiv.org/abs/2609.28919v1)).

## Why it works

A warm turn reads nearly all of its input at the cheap rate; a moved turn writes the entire prefix at a premium and reads nothing back. That asymmetry, not the classifier's accuracy, is what decides a router's bill on long sessions. Two shipped routers reached the rule without publishing the formula. GitHub states that Copilot's auto selection routes "along natural cache boundaries to avoid additional cache related costs" and that "switching models mid-session has shown increased cost without ample improvements in quality" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/models/auto-model-selection)). OpenRouter's sticky routing "pins follow-up requests to the provider holding the warm cache", and routes them back only "when that provider's cache-read pricing is cheaper than normal input" ([OpenRouter](https://openrouter.ai/blog/tutorials/prompt-caching-sticky-routing/)). One team measured the penalty from outside: across three days of Copilot traces, "every switch also throws away the cache, so the whole context is sent again at the new model's price. One trivial turn cost more than the six others together" ([Michelin](https://blogit.michelin.io/copilot-auto-mode-off-by-default/)).

## When this backfires

- Flat cache-read pricing. Under a uniform 0.1x read rule across tiers, the emulated saving falls from 13.8% to 5.2%, because the long-session cost crossover it leans on disappears ([arXiv 2609.28919v1 Table 4](https://arxiv.org/abs/2609.28919v1)).
- Short sessions with few tool steps. At half the base tool steps and tool-result tokens the saving is 1.6%; at double it is 24.0% ([arXiv 2609.28919v1 Table 4](https://arxiv.org/abs/2609.28919v1)). With little cached context there is nothing for the boundary to protect.
- Caches that were cold already. On the pause-heavy corpus, where 27% of turns follow a gap over five minutes, the saving is 7.4% ([arXiv 2609.28919v1 Table 4](https://arxiv.org/abs/2609.28919v1)). Check which lifetime you are on first: Claude Code requests the one-hour cache for the main conversation on a Claude subscription and five minutes on "Usage credits, API key, or cloud provider" ([Claude Code](https://code.claude.com/docs/en/prompt-caching#which-ttl-each-request-gets)), which is how a gateway connects.
- A gateway that drops the cache markers. When one "removes the markers while returning success", then "your entire conversation history bills as uncached input on every turn" ([Claude Code](https://code.claude.com/docs/en/prompt-caching#where-the-cache-lives)), and no routing decision recovers that.
- Moving on weak evidence. Dropping the router's confidence threshold from 0.8 to 0.7 cut the saving from 13.8% to 9.8% ([arXiv 2609.28919v1 Table 4](https://arxiv.org/abs/2609.28919v1)). Lower it to 0.5 and 46% more turns move, "a fifth of them false downgrades whose correction chains cost more than the moves save" ([arXiv 2609.28919v1 §5.4](https://arxiv.org/abs/2609.28919v1)).
- A cheap managed default would do instead. Michelin turned Copilot's auto mode off and defaulted new sessions to a cheap model, having found the router's draws irreproducible at identical scores: "renaming a variable cost 0.23 credits when the draw landed on MAI-Flash and 3.24 when it landed on Terra, for the same prompt on the same day" ([Michelin](https://blogit.michelin.io/copilot-auto-mode-off-by-default/)). Most of the money sits in what a session opens on, which a managed default captures with no classifier to build.

## Key Takeaways

- Treat the prompt cache, not the classifier, as the thing that decides when a model choice may be re-opened.
- Act at three places only: the session's first prompt, a side lane seeded with a ledger rather than the transcript, and a subagent launch.
- Before any mid-task switch, compute `n*` from the two models' cache read and write prices. On Anthropic's September 2026 sheet it ran longer than most tasks do.
- An expired cache is a free re-choice, so a cold return is where to change model, effort, or context strategy.
- Route subagents at launch first. It is the boundary with nothing to weigh against it, and dropping it took the emulated saving from 13.8% to 11.7% ([arXiv 2609.28919v1 Table 4](https://arxiv.org/abs/2609.28919v1)).
- Check the cache lifetime and the gateway's marker handling before building anything. Either can void the arithmetic outright.

## Related

- [Routing Break-Even: When a Cheaper Model Actually Pays](routing-break-even.md) — the other gate on the same decision, priced as the judge's cost against the gap between the two models.
- [Mid-Session Config Changes as Invisible Cache Invalidators](../anti-patterns/mid-session-config-cache-invalidators.md) — the full catalog of actions that break the prefix, beyond a model switch.
- [Model-Switch Lifecycle Hooks: Gating a Mid-Session Model Change](../../tool-engineering/model-switch-lifecycle-hooks.md) — the harness event that can enforce this boundary, with a re-cache cost estimate attached.
- [Forked vs Fresh Subagents: When to Inherit the Parent Conversation](../multi-agent/forked-vs-fresh-subagents.md) — what the subagent boundary trades away when the delegate starts from a brief.
- [Harness-Controlled Token Economics (The Harness Effect)](../../token-engineering/harness-token-economics.md) — the wider claim this sits under, that the orchestration layer sets the bill.
