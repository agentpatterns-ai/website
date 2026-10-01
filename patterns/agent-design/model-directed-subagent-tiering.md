---
title: "Model-Directed Subagent Tiering: Lead Model Picks the Tier"
term: "Model-Directed Subagent Tiering"
description: "Let the lead agent pick subagent kind, tier, effort and reuse at each dispatch instead of a router or one fixed sidekick, and check three conditions first."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - core-loop delegation
  - agent-chosen subagent tier
  - model-directed delegation
last_reviewed: 2026-09-30
maturity: emerging
---

# Model-Directed Subagent Tiering: Lead Model Picks the Tier

> The lead agent picks the subagent tier, effort and reuse at each dispatch, in place of a router or a fixed sidekick.

Model-directed subagent tiering gives the lead model (Replit calls it the core loop) a small menu at each step: what kind of subagent to send, at what size and effort, whether to return to one it has already briefed, and how hard to think ([Replit: Free the models](https://replit.com/blog/free-the-models)). It is a third option next to a [router](router-imposed-quality-ceiling.md) and a fixed lead plus sidekick split. It fits when three conditions hold: the lead model delegates without being told, the provider keeps its cache across effort changes, and you can re-run evals on each model release. All evidence comes from one vendor post, run by the vendor on its own product, so treat the numbers as a claim to test.

## How it works

Replit exposes four choices to the lead model ([Replit](https://replit.com/blog/free-the-models)):

- Domain-aware subagents, such as read-only explorers and reviewers beside a general worker.
- Tiers with an effort level: "Small, standard, and large, each a step up in cost and capability, and an effort level within the tier." The lead picks both at each dispatch.
- Reusable subagents: "any number of subagents stay warm across kinds and tiers, and it picks which to wake", in place of one long-lived sidekick.
- Dynamic effort tuning for the lead itself.

Replit's example: "a mechanical rename goes to small at low effort, while generating hypotheses for a stubborn bug goes to large at high effort". The harness still sets the menu: "For now, the harness still decides which specialists exist; the core loop decides when and how to use them."

The stated reason is the router argument. Replit argues that a router, whether heuristic or a small model that reads each turn, will always be less capable than the model it chooses for, and "Replit Agent lets the model decide instead".

Effort is not purely the model's call. Replit "trained an escalation system that checks the trajectory at each step and matches effort to task difficulty" ([Replit](https://replit.com/blog/free-the-models)), a learned controller close to [trajectory-conditioned model escalation](trajectory-conditioned-model-escalation.md).

## The evidence

Replit ran one single-variable ablation: a sidekick architecture, "the same configuration with one change: its subagent primitives replaced by a single long-lived worker" ([Replit](https://replit.com/blog/free-the-models)). Replit's own runs are means of four repetitions.

| Benchmark | Replit Agent | Sidekick architecture | Astra alone, low effort | Astra alone, xhigh effort |
|-----------|--------------|-----------------------|-------------------------|---------------------------|
| DeepSWE v1.1 | 72% at $2.11 per task | 61% at $1.34 | 67% at $1.60 | 74% at $4.43 |
| Terminal-Bench 4.0 | 49% at $2.53 per task | 33% at $1.84 | 42% at $2.25 | 60% at $5.86 |

Replit Agent beats the sidekick by 11 and 16 points. "The sidekick costs less, and gives up a sixth to a third of the score for it." Terminal-Bench runs exclude three GPU tasks, and the Astra figures are published mini-swe-agent baselines, not Replit's own runs ([Replit](https://replit.com/blog/free-the-models)).

Only the sidekick arm changes one thing, the subagent primitives. The Astra columns compare one model in another harness against Replit's tiered setup, so they carry the caveat in [model-set parity for harness claims](model-set-parity-harness-claims.md). Astra alone at xhigh effort scores 2 points higher on DeepSWE and 11 higher on Terminal-Bench, at about 2.1 and 2.3 times the cost (arithmetic from the table). Replit's summary is "Neither baseline wins on both cost and score." The result is a better trade of cost against score, not a higher ceiling.

## Why it works

Replit asserts two causes and does not isolate either, so the mechanism is vendor-asserted. First, Replit says its escalation system, unlike a router, acts mid-turn on the work in progress, not once on the request ([router-imposed quality ceiling](router-imposed-quality-ceiling.md)). Second, cost is price times tokens, and a lead that hands routine work to cheaper tiers moves tokens to a lower price. Replit says it observed expensive models "naturally delegate to less costly subagents, keeping their own tokens for the decisions that need them" ([Replit](https://replit.com/blog/free-the-models)). [Cognition's cost analysis](../../token-engineering/pricier-per-token-cheaper-per-task.md) points the same way for a lead plus sidekick design.

The ablation shows that many warm, tiered subagents beat one long-lived worker. The research found no source that ablates kinds, tiers, reuse and effort tuning separately, so the post does not show which one drives the gain.

## When to use it

- The lead model delegates on its own. At medium effort, turns that hand work to a general worker were 0.9% for Fable 5, 2.3% for Fable 5.1 and 20% for GPT-6 Astra ([Replit, Table 1](https://replit.com/blog/free-the-models)). The data covers one week per model, so read your own traces first.
- Your provider keeps the cache. Replit says effort changes preserve cache on the GPT-6 family and Fable 5.1, and "Elsewhere, effort changes and model switches rebuild the cache" ([Replit](https://replit.com/blog/free-the-models)).
- You can re-test each release. Replit writes that "Each new model sends us back to re-test what we held firmly". Delegation habits differ by model, as Table 1 shows.

## When this backfires

- The lead does not delegate. The tier menu goes mostly unused and the harness work buys little.
- A hard per-task budget applies. The sidekick is cheaper on both benchmarks ($1.34 against $2.11, $1.84 against $2.53), and a model swap can change the bill under model-chosen delegation.
- Quality outranks cost. Astra alone at xhigh scores higher on both benchmarks.
- The work is tightly coupled. Anthropic notes "most coding tasks involve fewer truly parallelizable tasks than research" ([Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system)). Cognition argues parallel agents make conflicting implicit decisions ([Cognition](https://cognition.ai/blog/dont-build-multi-agents)), yet later shipped a lead plus sidekick design, so the sources disagree on how much delegation is safe.
- Agents misjudge effort. Anthropic wrote: "Agents struggle to judge appropriate effort for different tasks, so we embedded scaling rules in the prompts." That is 2025 evidence on older models, and Replit reports that it trained its own escalation system to match effort to task difficulty.
- The gain may come from extra compute. One study concludes that "many reported advantages of multi-agent systems are better explained by unaccounted computation and context effects rather than inherent architectural benefits" ([Tran and Kiela](https://arxiv.org/abs/2604.02460v2)). It covered multi-hop reasoning, not coding agents.
- You cannot run evals. A model swap then changes delegation with no signal.

## Key Takeaways

- The lead model picks subagent kind, tier, effort and reuse per dispatch, and the harness still fixes which specialists exist.
- Replit's sidekick ablation is the only single-change evidence: 11 and 16 points better than one long-lived worker, at higher cost.
- Astra alone at xhigh scores higher at more than twice the cost, so the win is a trade of cost against score.
- Adopt it when the model delegates unprompted, the cache survives effort changes, and evals can re-test each release.
- All results are vendor-run, and none shows which of the four choices drives the gain.

## Related

- [Router-Imposed Quality Ceiling](router-imposed-quality-ceiling.md) covers why a router that commits before output caps quality.
- [Utility-Model Split](utility-model-split.md) covers static cheaper-model routing for background calls.
- [Trajectory-Conditioned Model Escalation](trajectory-conditioned-model-escalation.md) covers escalation decided from a partial trajectory.
- [Model-Set Parity in Harness Claims](model-set-parity-harness-claims.md) covers harness comparisons when the model sets differ.
- [Dispatch-Time Reasoning Level](dispatch-time-reasoning-level.md) covers a human choosing effort at hand-off.
- [Pricier per Token, Cheaper per Task](../../token-engineering/pricier-per-token-cheaper-per-task.md) covers the lead plus sidekick cost inversion.
- [Provider-Hosted Subagent Delegation](provider-hosted-subagent-delegation.md) covers the hosted form of the same delegation decision, where the tree shares one model and no tier can be chosen.
