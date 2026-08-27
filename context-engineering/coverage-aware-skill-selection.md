---
title: "Coverage-Aware Skill Selection Under a Token Budget"
term: "Coverage-Aware Skill Selection"
description: "Score candidate skills against the capabilities your selected set still leaves uncovered, then keep the best prefix under the token budget."
aliases:
  - coverage-aware skill selection
  - set-level skill selection
  - complementarity-first skill selection
  - best prefix selection
tags:
  - context-engineering
  - tool-agnostic
  - skills
  - arxiv
last_reviewed: 2026-08-23
maturity: emerging
---

# Coverage-Aware Skill Selection Under a Token Budget

> Score candidate skills against the capabilities your selected set still leaves uncovered, then keep the best prefix under the token budget.

Ranking skills independently by semantic relevance and packing the top few prefers a near-duplicate of a skill you already loaded over one that supplies a capability nothing else in the set covers. Chen and colleagues model task success as coverage of a latent capability demand and measure the gap. On a contamination-controlled BigCodeBench variant, BPS, the algorithm that maximizes their fitted objective, "outperforms all the baselines, reaching 0.73 measured task success" against 0.20 to 0.52 for released skill routers, text retrievers, and the executor's own selection, on 28% fewer tokens than the strongest released router ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)).

That headline comes from one controlled testbed. Four conditions decide whether it reaches your library.

## When coverage-aware selection pays

| Condition | Why it decides |
|---|---|
| You log pass/fail outcomes against the set that was loaded | The skill-to-capability matrix is fitted from execution results, never from description text. Chen and colleagues recover it with 281 parameters at 0.996 AUC over 155 (skill, capability) pairs, so ordinary run logs carry the signal ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). |
| Candidate skills overlap in capability | The benefit function is submodular only because covering ground twice adds almost nothing ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). Where skills are genuinely additive, independent top-k scoring is already optimal. |
| Skill bodies enter context upfront | The model charges a per-token penalty on the whole selected set. Anthropic's Agent Skills load description metadata first, and only once Claude judges a skill relevant will it "load the skill by reading its full `SKILL.md` into context" ([Anthropic](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)). That shrinks the penalty the optimizer trades against. |
| The library and executor are stable between re-fits | Parameters were fitted for one 31-skill library and one executor, Qwen3-32B. Deployment beyond them "requires encoding tasks and skills from their text", which the paper does with a neural encoder reaching 0.68 measured success, "0.05 below the lookup-table instantiation" ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). A library that gains skills weekly invalidates the fit faster than you can re-estimate it. |

## Why it works

Benefit multiplies across capability dimensions and is concave within each one ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). Concavity means a second skill covering the same ground buys little. One uncovered capability holds the whole product near zero however well the rest are served. Per-skill relevance sees neither effect, because it scores each candidate against the query rather than against what the already-selected set leaves open. The ablation shows the shape directly: a set covering both required capabilities reached 93% success, a redundant addition bought one point of success for 225 tokens, and a task-irrelevant addition cost 23 points ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). Concurrent work applies the same submodular selection framing to general context assembly ([PACMS, arXiv:2606.20047v1](https://arxiv.org/abs/2606.20047v1)).

Packing order matters too. The two heuristics that score whole sets — density greedy and best-of-100 random — "reach it on only 45% and 44%" of the 80 selection instances; recording every prefix along the greedy chain and returning the best-scoring one reached it on all 80 ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). The guarantee is bicriteria: the selected set recovers at least a 1−1/e fraction of any feasible set's capability benefit while paying that set's full context penalty.

## Applying it without fitting a model

Two moves follow from the numbers above without fitting anything. Filter hard on relevance first, because the irrelevant skill is the expensive mistake at 23 points against a redundant skill's one ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). Then rank the remaining candidates on the capability the current set does not yet supply, rather than re-ranking against the original query.

## When this backfires

- Token pressure is not your binding constraint. Song and Wei decompose the cost of a growing skill library and find context overhead "small and indistinguishable from zero", with wrong selection carrying the damage ([arXiv:2605.24050v2](https://arxiv.org/abs/2605.24050v2)). A budget-constrained optimizer then solves a constraint that is not binding.
- Your logs only contain sets your current router chose. A top-k history is a narrow slice of the set space, so the fit must extrapolate. Chen and colleagues test that directly. Under their extrapolation protocol a model "trains only on sets of at most two skills and must predict sets of three or more", and the structured objective's "predicted rates fall within one percentage point of the measured ones" ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). Measure the same extrapolation on your own logs first.
- The shortlist is short. The published algorithm costs O(dL⁴) in the shortlist size L, not the registry size ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). Below roughly a dozen candidates, exhaustive search is cheap and the machinery buys nothing.
- The reported margin does not transfer as a number. Tasks entered the benchmark only when they required all their capabilities, and the same executor passes 85% of the original BigCodeBench with no skills at all ([arXiv:2608.19993v1](https://arxiv.org/abs/2608.19993v1)). The testbed is built for the regime where skill choice matters most, so read 0.73 against 0.20 as a direction rather than a forecast.

## Key Takeaways

- Filter on relevance first and coverage second: an irrelevant skill cost 23 points of task success, a redundant one cost about a point.
- The selection signal is learnable from ordinary pass/fail logs, so instrument which set was loaded before you invest in a router.
- Check whether skill bodies actually enter context upfront; under progressive disclosure the token penalty this method trades against is much smaller.
- Re-rank remaining candidates on the uncovered capability once the first skill is chosen, not on the original query.
- Re-fit whenever the library or the executor changes. The lookup-table fit is specific to one library and one executor; generalizing needs the text-encoder instantiation, which measured 0.05 lower.

## Related

- [Skill Loadout Curation for Coding Agents](skill-loadout-curation.md) — which skills to install at all, and why colliding descriptions matter more than token count
- [Compositional Skill Routing](compositional-skill-routing.md) — decomposing a query into sub-tasks and retrieving one skill per sub-task at MCP-library scale
- [When a Skill Graph Cannot Beat the Ranker](skill-graph-topology-bound.md) — the reach limit on a skill graph built from the retriever's own embedding neighbors
- [Context Budget Allocation](context-budget-allocation.md) — dividing a fixed context window across competing consumers
