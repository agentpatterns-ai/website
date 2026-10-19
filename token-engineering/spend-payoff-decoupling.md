---
title: "Agent Spend Is Set by Velocity, Not by Agent Payoff"
term: "Spend-Payoff Decoupling"
description: "Project velocity and token price set what a team spends on agents while capability decides the payoff, so a spend figure cannot report whether agents earn their cost."
tags:
  - token-engineering
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - spend-payoff decoupling
  - agent spend is not a payoff signal
  - token budget per developer
last_reviewed: 2026-10-18
maturity: emerging
---

# Agent Spend Is Set by Velocity, Not by Agent Payoff

> In simulation, project velocity and token price set agent spend; capability decides whether that spend bought anything.

A team's agent spend and the payoff from its agents move on different variables. How much goes to agents follows the volume of work the project demands and the price of the tokens that absorb it. Whether that money beat a human-only team follows agent capability, which the bill never records. A simulation that searched for cost-optimal mixed human-agent teams states the split directly: "the project velocity determines how much is spent on agents, while the capability of the agents determines whether agents are worth using at all" ([Herbold, arXiv:2610.20394v1](https://arxiv.org/abs/2610.20394v1)).

## The conditions this rests on

This is simulation evidence, so carry the direction and leave the magnitudes behind. The model is a discrete-time stochastic process over sprints, searched with Monte Carlo and evolutionary optimization across "432 scenarios varying developer capability, project velocity, debt dynamics, agent capability and price, and bug costs" (Herbold). Agent capability comes from SWE-bench Verified and CyberBench scores on a third-party leaderboard, and the author names the direction of that error: "All of the estimates above are optimistic, both regarding the capabilities and the costs of agents." The paper then names the two parameters its results lean on hardest, and one of them is the term this page asks you to price: "Future work should validate our model against data from real projects that use agents, in particular regarding the capability of agents to detect bugs and the costs of escaped bugs, which our results depend on most strongly" (Herbold).

The grid includes a deliberately pessimistic agent tier built to break the conclusion, so the direction survives bad assumptions. No individual figure survives the same way.

## What a spend figure leaves out

At realistic velocities the cost-optimal teams pay people more than they pay for tokens. "The developer costs exceed the agent costs for 65% of the optimal teams, with a median ratio of agent to developer costs of 0.32" (Herbold). Treat 0.32 as the middle of a distribution over 432 scenarios and not as a budget, because the same model puts agent spend above 100 times developer spend in some very high velocity cases.

Payoff tracks capability instead, and it separates sharply. Agent teams beat the human-only baseline in 71.6% of scenarios overall, but that average hides the split: high-tier agents won 98.8% of the time, low-tier agents 55.6% and the pessimistic tier 44.4%, which the paper calls "closer to a coin flip" (Herbold).

Cheap tokens did not produce cheap projects. The low agent tier buys the cheapest tokens in the grid and lands second-worst on total cost: "the overall costs increase by a factor of 7.6 at the low tier, even though the tokens are cheaper" (Herbold).

The highest agent-to-developer spend ratio in the whole grid belongs to the pessimistic tier, the one that cleared the baseline less than half the time. That pairing is not evidence that weak agents cause high spend. The tier is expensive by construction, since it "combines the capability of the low tier with ten times the cost of the high tier" (Herbold), so it tests the conclusion under hostile price assumptions rather than showing causation.

## Why it works

Delivery is a constraint in this model rather than an outcome: the team has to ship the features the project demands. Agent spend is then whatever quantity of agent satisfies that demand at the going token price, which is why velocity and price set the size of the bill.

Payoff turns on a cost line the token bill never touches. "Bug impact is also the largest driver of the total costs", worth 72.6 times between its cheapest and most expensive tier (Herbold). Capable agents inject fewer bugs and need less supervision, so their advantage arrives as defects that never reached production and review hours nobody spent. The optimal teams put most of the agent budget there rather than into writing code: "on average, 61% of the agent costs are spent on the Security Audit (33%), Code Review (24%), and Test Development Agents (4%)", against 28% for feature implementation (Herbold). A spend figure measures the input to that process and reports none of its output.

## What to measure instead

The paper names the replacement metric: "We thus believe that token consumption is a poor indicator for the productivity of AI-native development. A better measure is the total cost per delivered feature, including the cost of the bugs that reach production" (Herbold).

Two terms have to be real before that ratio means anything: a count of delivered features, and a price for a bug that escapes to production. Build the second one first, because it carries most of the total. A cost-per-feature figure computed without it is the spend metric with extra arithmetic in front of it.

The ratio also needs a comparison. Every payoff claim in the simulation rests on one: "An important baseline to understand the impact of agents on software development is to compare mixed teams against a baseline with only human developers" (Herbold). A cost per feature improving against its own history cannot say the agents were the cause.

## When this backfires

- You have no price for an escaped bug. The dominant term goes missing and the replacement metric inherits the flaw it was meant to fix. Pair it with [cost-quality Pareto measurement](cost-quality-pareto-measurement.md), which keeps the quality axis visible while the cost axis is incomplete.
- Your work has no countable feature stream. The model assumes a feature pipeline with fixed effort per item. Platform, infrastructure, and research work has no such denominator, and inventing one makes the metric gameable in the way token counts already are.
- You run at very high velocity, where the advice inverts. Agent spend should dominate there, so a team reading a large agent bill as a warning sign under-provisions where the simulation says agents are mandatory. Human-only teams could not reach the top demand tier at all: against a target of 1,000 issues per sprint, "the best human-only team of only senior developers manages to deliver 310 features per sprint" (Herbold).
- Your reporting period is short. Escaped-bug cost lands release cycles after the spend that caused it, so a quarterly review reads the two terms against the wrong spend decision.
- The throughput premise may not hold on your codebase. In a randomized trial on mature repositories, "allowing AI actually increases completion time by 19%" ([Becker et al., arXiv:2507.09089v2](https://arxiv.org/abs/2507.09089v2)). The simulation treats agent throughput as a dial to turn up. On the repositories that trial measured, the dial ran backwards, which removes the velocity term driving agent spend in the first place.

## Key Takeaways

- Stop asking the agent bill a question it cannot answer. Spend reports the demand you faced and the price you paid, never whether the purchase was worth making.
- Argue about agent capability in budget reviews, not about the token line. Capability is what separated the tiers that reliably paid off from the coin-flip ones, and the paper's own advice to practitioners is "Focus on capability, not price per token" (Herbold).
- Price your escaped bugs before you adopt cost per delivered feature. Bug impact moved total cost 72.6 times across this grid's tiers, so a denominator without it is missing the term that dominates.
- Keep an agent-off comparison. A cost per feature that improves on its own history cannot attribute the improvement.
- Do not carry any ratio off this page as a target, the 0.32 median included. The paper's conclusion is that no universal token budget per developer and no universal agentic team structure exist.

## Related

- [Pricier-Per-Token Models That Cost Less Per Task](pricier-per-token-cheaper-per-task.md) — the model-selection half of capability over price, inside one harness rather than across a team budget
- [Cost-Quality Pareto Measurement for Agent Configurations](cost-quality-pareto-measurement.md) — the measurement frame to reach for when the cost axis alone is misleading
- [The Four Terms That Decide What an Agent Task Costs](four-term-agent-cost-model.md) — the same bill one altitude down, decomposed for a single task
- [The Token Price Index Fallacy in Agent Cost Planning](../fallacies/token-price-index-fallacy.md) — a published price-per-token figure answering a different question again
- [Human-Equivalent Hours for Autonomous Coding Agent Productivity](../human/human-equivalent-hours-agent-productivity.md) — the other side of the denominator problem, on the output unit
