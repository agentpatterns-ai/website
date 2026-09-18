---
title: "Difficulty-Aware Topology Selection for Coding Agents"
term: "Difficulty-Aware Topology Selection"
description: "The gain from agent collaboration rises from 2.4 to 21.1 pass@1 points across difficulty tertiles while its price stays ten times higher, so the topology decision belongs to the task rather than to the deployment."
tags:
  - agent-design
  - cost-performance
  - multi-agent
  - tool-agnostic
  - arxiv
aliases:
  - per-task topology routing
  - difficulty-aware collaboration budget
  - topology selection per problem
last_reviewed: 2026-09-17
maturity: emerging
---

# Difficulty-Aware Topology Selection for Coding Agents

> Collaboration between agents buys almost nothing on easy tasks and about twenty points on hard ones, at the same tenfold price.

Choose the collaboration structure per task instead of fixing one for the whole system, under two conditions. Difficulty has to be estimable from the request before anything runs, and you need each structure's measured hit rate on your own workload to estimate from. The second condition is where most teams should stop and keep their single agent.

## What the payoff curve looks like

Hong ran five topologies over 614 problems from APPS, HumanEval+ and LiveCodeBench, holding the backbone identical inside every topology so the comparison isolates structure from model choice ([Hong, 2026](https://arxiv.org/abs/2609.13890v1)).

| Topology | Calls | Price vs one agent | pass@1 |
|---|---|---|---|
| Single | 1 | 1.00× | 62.21% |
| Chain (propose, critique, revise) | 3 | 5.10× | 69.38% |
| Star (hub plus three workers) | 4 | 5.35× | 66.61% |
| FullMesh (three peers, two rounds) | 6 | 8.74× | 70.52% |
| Hierarchical (manager, leads, workers) | 5–8 | 9.95× | 73.62% |

That last column hides the finding. Split the same problems into difficulty tertiles and the five topologies sit inside a 2.4-point band on the easy third, 10.7 points on the middle third, and 21.1 points on the hard third, while every price ratio above holds throughout. On the easy third the hierarchical mesh spends $0.94 per problem to move 91.7% to 94.1% ([Hong, 2026](https://arxiv.org/abs/2609.13890v1)).

Read the table's middle rows and call count does not rank accuracy either: the three-call chain beats the four-call star on every suite and is statistically indistinguishable from the six-call mesh (p=0.628) at 71% less cost. The same difficulty progression reappears on 400 mathematical reasoning problems, 2.5 points to 20.9 ([Hong, 2026](https://arxiv.org/abs/2609.13890v1)).

## Why it works

Coordination has a fixed price and a variable payoff. Price ratios follow from the number and shape of calls, so they hold to within three percent across backbones. What that spend buys depends on the problem, on two axes at once. Difficulty moves the gap from 2.4 to 21.1 points, and category moves it again: a router trained on cached outcomes sends 65% to 73% of implementation, sorting and string problems to a single call, and graph problems to the hierarchical mesh 49% of the time, told nothing in advance about which category suits which structure ([Hong, 2026](https://arxiv.org/abs/2609.13890v1)). Solvability is close to monotone in coordination order, so the live question is never whether a topology succeeds but whether the next-heavier one's marginal gain beats its marginal cost. A fixed topology pays one price for a benefit that varies by an order of magnitude.

## Setting the knob

Run the topology that maximizes predicted success minus λ times normalized cost. Because λ sits on the scale of a probability, it reads as a price: at λ=0.06, upgrading from one agent to the hierarchical mesh must buy at least 5.4 predicted points. Fit λ by bisection against a spend target rather than tuning it for accuracy, and one predictor then serves every budget without retraining. At 40% of always-hierarchical spend the router reached 77.69%, against 73.62% for always-hierarchical and 74.27% for the strongest learned competitor.

One corollary outlives the router. Any method trading accuracy against cost through a coefficient defines a curve rather than a point, and a shared coefficient acts on each method's own score scale. Given the same λ=0.2, six cost-aware routers spent between 30.3% and 51.9% of the reference budget, and two outranked the paper's own method. Calibrating each to equal realized spend compressed that spread to 1.7 points and reversed both comparisons ([Hong, 2026](https://arxiv.org/abs/2609.13890v1)). Print realized spend beside accuracy, or the table cannot be read.

## When this backfires

Every figure in this list comes from the same study ([Hong, 2026](https://arxiv.org/abs/2609.13890v1)), except where another source is named.

- Difficulty is not legible from the task text. The features here are lexical and structural over a self-contained problem statement. On LiveCodeBench, whose contest statements are stylistically uniform, the router reached 68.7% against an 88.7% oracle, the widest gap in the study. A repository issue ticket carries far less of that structure.
- You have no cached outcome grid. The predictor trains on every topology's result for every problem, and producing that grid took 12,280 executions and roughly $1,807. No grid means no predictor and no λ.
- The workload is easy-dominated. On the easy third the whole five-topology band is 2.4 points, less headroom than the routing machinery costs to build.
- The comparison is not spend-matched against sampling. The 21.1-point figure sets one sample of one agent against a structure costing ten times as much. With reasoning tokens held constant, single-agent systems "consistently match or outperform" multi-agent ones on multi-hop reasoning ([Tran and Kiela, 2026](https://arxiv.org/abs/2604.02460v2)). Ten samples under self-consistency is the arm this study does not run.
- Latency or variance matters. Budget matching equalizes expected spend and nothing else. The hierarchical mesh has a 38.6-second median against 8.4 seconds for one call, and a router meeting its budget by occasionally buying the most expensive structure counts as matched against one that never does.
- The backbone changes. Transferring the router costs 2.28 points and its advantage over always-hierarchical stops being significant. The problem ordering transfers; the probability scale λ acts on does not.

## Example

Run over the same 614 problems at 40% of the always-hierarchical budget, the trained router sends 301 problems to a single call, 163 to the three-call chain, and 80 to the hierarchical mesh. The split tracks difficulty rather than any hand-written rule: 131 of 164 HumanEval+ problems take one call, while 47 of 100 APPS-Competition problems take the mesh ([Hong, 2026](https://arxiv.org/abs/2609.13890v1)). Half the workload never pays for collaboration, and the half that does is concentrated where the measured gap is 21 points rather than 2.

## Key Takeaways

- The multi-agent premium is not a constant. Across 614 problems it runs from 2.4 pass@1 points on the easy third to 21.1 on the hard third at a flat 9.95× price ([Hong, 2026](https://arxiv.org/abs/2609.13890v1)).
- Cost is set by call count and message structure; benefit is set by the task. That asymmetry, rather than any particular router, is the argument for deciding per task.
- More calls is not more accuracy. A three-call chain beat a four-call star on every suite and matched a six-call mesh costing 71% more.
- Express the decision as one price, λ, fitted to a spend target rather than to accuracy, so the operating point moves by editing a number.
- Treat the grid of cached per-topology outcomes as the real adoption cost, and treat any cost-aware comparison without realized spend printed beside accuracy as uninterpretable.
- The headline gap compares one sample against ten times the spend. Before buying collaboration, price the same money as repeated sampling from one agent.

## Related

- [Multi-Agent Topology Taxonomy](../multi-agent/multi-agent-topology-taxonomy.md) — picks a topology from task structure and shared state, fixed once for the system
- [Parsimonious Agent Routing](../multi-agent/parsimonious-agent-routing.md) — a learned router over a heterogeneous model roster, emitting decomposition, worker and budget together
- [Over-Orchestrated Agent Architecture](../anti-patterns/prefer-simplest-agent-architecture.md) — the uniform version of this decision, and the equal-budget evidence behind it
- [Delegation Threshold Calibration](delegation-threshold-calibration.md) — the standing delegate-or-inline threshold, hand-set from handoff cost and review tax
- [Routing Break-Even](routing-break-even.md) — the same cost arithmetic applied to model choice rather than to topology
