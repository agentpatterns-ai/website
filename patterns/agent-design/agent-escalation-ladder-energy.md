---
title: "The Agent Escalation Ladder Priced in Energy and Latency"
term: "Agent Escalation Ladder"
description: "On self-hosted open-weight models one agent costs 1.20x a direct call's energy, two 3.06x and four 6.36x, while accuracy stays flat on four of five tasks."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - per-rung agent cost
  - non-agentic baseline escalation
  - energy-priced agent topology
last_reviewed: 2026-10-06
maturity: emerging
---

# The Agent Escalation Ladder Priced in Energy and Latency

> On self-hosted open-weight models, one agent costs 1.20x a direct call's energy, two 3.06x, four 6.36x, with accuracy flat on four of five tasks.

The rungs between a stateless model call and a four-agent workflow carry separate prices. Astekin and colleagues metered 1,840 runs across five software engineering tasks, six open-weight models, two prompt strategies and three hardware platforms ([Astekin et al., 2026](https://arxiv.org/abs/2610.03010v1)). The runs used about 651.7 kWh in total. Averaged over all of it, one agent consumes 1.20x the energy of a direct stateless query and runs 1.23x as long. Two agents reach 3.06x and 3.32x. Four reach 6.36x and 6.07x. The worst individual task-hardware pair reached 160x. Log parsing on the mid-range workstation took 50,186 seconds under four agents against 313 seconds direct.

Those prices hold inside one envelope. The models are 4B to 20B open-weight. They are served locally through Ollama at a 4096-token context with temperature fixed at 0, and they answer single-pass prompts over curated benchmark items. Repository-scale and tool-augmented tasks are named as future work rather than measured. The authors mark the boundary themselves: "The results may not generalize to tasks such as code review, test generation, repository-level maintenance, or autonomous development". Read the ladder as a cost curve for self-hosted inference on single-pass work rather than a verdict on agent topology generally.

## What each rung buys

Accuracy does not climb with the price. The direct call has the highest mean score on four of the five tasks: code generation, technical debt detection, log parsing and log analysis. Four agents lead on one, vulnerability detection, at 55.4% F1 against 49.7% for the direct call ([Astekin et al., 2026](https://arxiv.org/abs/2610.03010v1)).

The asymmetry runs deeper than the means. Energy differs significantly by agentic configuration on all five tasks, while accuracy does so on one: vulnerability detection, at p=0.0162 on the omnibus test. Even there the post-hoc pairwise test does not separate four agents from the direct call. The paper states the limit: "the differences among MA, NA, and SA are not significant under the paired hardware-balanced test". Across the 15 task-hardware pairs the accuracy-energy frontiers hold 66 configurations in total, of which 36 are non-agentic, 23 single-agent, 6 dual-agent and 1 four-agent.

That makes a frontier the evidence standard, since a win on the accuracy axis alone can still fail a multi-objective comparison. Here the only such win did.

## Why it works

The study decomposes multi-agent latency into three parts: model loading, orchestration overhead, then inference for every agent involved ([Astekin et al., 2026](https://arxiv.org/abs/2610.03010v1)). Each added agent contributes its own token generation on top of the messages the agents exchange. A coordination round therefore multiplies the work rather than adding to it. On a local GPU that multiplier is the whole cost, because "local inference on the same hardware draws roughly constant power". Energy and wall-clock correlate at r=0.987 in log-log space. The paper reports savings on the two as largely co-achieved: "a configuration change that reduces one will almost always reduce the other".

Every extra round costs its multiple whatever the task is. It pays only when it supplies information the first pass lacked. The cost is structural, the benefit contingent. Hardware adds to that: on the hardware-balanced subset accuracy varies by under 3 percentage points across the three platforms, while platform latency differences grow from about 2-3x for the direct call to about 3.4x for four agents.

## Try the cheaper levers first

Prompt and model choice moved these tasks further than topology did. Few-shot prompting took log-parsing accuracy from 3.4% to 54.3% and cut energy by 24% to 41% at the same time. Model choice swung log-parsing latency by up to 136.5x between two open-weight models ([Astekin et al., 2026](https://arxiv.org/abs/2610.03010v1)). Neither lever points the same way on every task: few-shot examples made code generation worse, 92.7% against 97.3% zero-shot.

## When this backfires

- Breadth-first retrieval over independent sub-queries. Anthropic reports a multi-agent system that "outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval" at roughly 15 times the tokens of a chat interaction ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). A 6x multiplier is cheap against that. The same post narrows it: "most coding tasks involve fewer truly parallelizable tasks than research".
- Repository-scale repair with execution feedback. AgentForge's five agents, a sandbox and three debug retries took SWE-bench Lite resolution from 14.0% under single-agent GPT-4o to 40.0%, for about 2.7x the per-task API cost ([Kumar et al., 2026](https://arxiv.org/abs/2604.13120v1)). That is 26 points for a smaller multiplier than the ladder charges, on work this study excludes.
- Hosted or cloud serving. Batching, virtualization, cooling and grid carbon intensity all move the multiplier, and a hosted API exposes no energy figure to meter.
- Format-bound tasks. Where output structure is the bottleneck, as in log parsing, the prompt lever dominates and escalating agents spends 6x on the wrong axis.
- Batch work nobody waits on. A 6.07x runtime penalty costs an overnight job nothing, and the carbon figure rests on a fixed grid-intensity assumption the authors call a conservative lower bound.
- Baselines already near ceiling. All four configurations scored between 94.2% and 96.8% Pass@1 on code generation, which leaves coordination nothing to buy.

## Example

Vulnerability detection is the one case the ladder appears to justify. Four agents in a mock-court arrangement — security researcher, code author, moderator, review board — reached 55.4% F1 against 49.7% for a direct call on 386 paired PrimeVul functions. That 5.7-point gain is the only task in the study where an agentic configuration beat the direct call on mean accuracy ([Astekin et al., 2026](https://arxiv.org/abs/2610.03010v1)).

Then price it. The four-agent configuration is the balanced pick on the three-objective frontier for none of the 15 task-hardware pairs. Table 23 selects the direct call in 11 and a single agent in 4. The pairwise test against the baseline returns p=0.339. The paper's §4.4.2 prose says four agents appear on the balanced front for one pair, which Table 23 does not show. A team reading only the F1 column ships the mock court everywhere. A team reading all three columns escalates here and nowhere else.

## Key Takeaways

- On self-hosted open-weight inference, price the rungs separately. The agent abstraction itself costs 1.20x the energy and 1.23x the runtime of a direct call, the second agent costs 3.06x and 3.32x, the fourth 6.36x and 6.07x ([Astekin et al., 2026](https://arxiv.org/abs/2610.03010v1)).
- On self-hosted inference energy and wall-clock move together, correlated at r=0.987, so savings on the two are largely co-achieved instead of traded against each other.
- Judge an escalation on a frontier rather than one axis. Of the 66 configurations on the study's accuracy-energy frontiers, 59 are non-agentic or single-agent and 1 is four-agent. On the three-objective frontier that adds latency, four agents are the balanced pick for none of the 15 task-hardware pairs.
- Exhaust prompt and model choice first. Few-shot prompting beat every topology change on log parsing and reduced energy by 24% to 41% while doing it.
- The envelope is narrow: 4B-to-20B local models, single-pass benchmark prompts, no repository context. Breadth-first retrieval and execution-grounded repair both pay their multipliers back.

## Related

- [Over-Orchestrated Agent Architecture](../anti-patterns/prefer-simplest-agent-architecture.md) — the same escalation discipline as an anti-pattern, with context loss rather than energy as the mechanism
- [Difficulty-Aware Topology Selection](difficulty-aware-topology-selection.md) — routes topology per task on hosted models, priced in dollars and fitted with a learned router
- [Agentless vs Autonomous](agentless-vs-autonomous.md) — the two-phase pipeline that beat autonomous agents on SWE-bench Lite at $0.70 a task
- [Routing Break-Even](routing-break-even.md) — the same marginal-cost arithmetic applied to model choice instead of agent count
- [The Model Economics of Agent Swarms](../multi-agent/model-economics-agent-swarms.md) — what caps fan-out width once decomposability has already said yes
