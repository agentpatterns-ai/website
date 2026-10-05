---
title: "Task-Distribution Router Fit: Where the Decision Belongs"
term: "Task-Distribution Router Fit"
description: "A model router's accuracy tracks how well its criteria match your real task mix, so the routing decision belongs wherever that mix is known and measured."
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
aliases:
  - harness-side model router placement
  - task-coupled model routing
  - router tier criteria fit
last_reviewed: 2026-10-02
maturity: emerging
---

# Task-Distribution Router Fit: Where the Decision Belongs

> A router's accuracy tracks how well its tier criteria match your real task mix, so the decision belongs where that mix is known.

A model router's accuracy depends on the match between its tier criteria and the traffic it actually sees. That match decides where the router should sit. LangChain built one into the harness of its coding agent Open SWE and gives that reason: "Those criteria are written for Open SWE's task set, so the router is deeply coupled to the tasks Open SWE handles" ([LangChain, 1 October 2026](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness)).

## The condition that makes harness placement pay

Put the router in the harness when you write the tier criteria against your own agent's task set. LangChain states a broader claim, that "An effective model router belongs in the harness, not a generic gateway", and its experiment does not test that claim. The headline A/B test compared the router against an always-frontier baseline, with no gateway-placed arm, and the post concedes the limit: "This result isn't surprising, given the control was our most expensive model" ([LangChain, 1 October 2026](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness)).

No source here tests the generic-criteria case against harness placement. RouteLLM, which trained its routers on public Chatbot Arena data, never discusses placement. It shows only that generic training can fail out of distribution, as the next sections cover ([RouteLLM, LMSYS](https://www.lmsys.org/blog/2024-07-01-routellm/)).

## What the measured run shows

LangChain split 973 threads between the router and a frontier-only control. The median routed thread cost $0.94 against $2.61 on control, 64% less. The mean fell 42% and the p90 fell 37%. Against that frontier-only control, quality did not move. Merged pull requests came in at 29.2% of routed threads against 27.3% of control (p = 0.49). Open rates were flat at 38.9% against 39.6% (p = 0.82). A second test sent half of threads through the router and half to the fast model alone. LangChain ended it within a day, before it could produce statistically meaningful results, because engineers flagged the fast-only arm for low output quality. Of routed threads, 56% went to the balanced tier, 34% to fast, and 10% to performance, across a ladder where "the median thread cost $0.097 on fast, $1.50 on balanced, and $2.88 on performance, a 30× spread" ([LangChain, 1 October 2026](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness)).

## The build order

Each step supplies the input the next one needs, so the order matters more than the tier list. LangChain's run went in this order ([LangChain, 1 October 2026](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness)):

1. Measure the task mix from traces. A week of threads labeled by task type showed code changes dominant: new features at 22%, bug fixes at 17%, test or no-op runs at 16%. Treat the labels as approximate: "categories are heuristics based on each thread's title and metadata". Thread cost and invocation count stood in for complexity.
2. Pick tiers along the cost-intelligence curve. LangChain chose three models from different providers, reading the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index) as of 9 September 2026.
3. Write each tier's criteria from the measured mix plus each provider's own model guidance. This is the step that pins the router to the harness.
4. Instrument an outcome metric before routing anything. "Merged PRs per thread became our main success metric", with thumbs up or down as a secondary signal that stayed sparse, since only a small share of threads get rated.

## Why it works

Routing quality follows the router's fit to the task distribution rather than its distance from the models. RouteLLM demonstrates the failure and its fix. Routers that beat the baseline on MT Bench collapse elsewhere: "all routers perform poorly at a near-random level when trained only on the Arena dataset, which we attribute to most MMLU questions being out-of-distribution". Adding golden-label data from the MMLU validation split, about 1,500 samples and "less than 2% of the overall training data", then "leads to significant performance improvements across all routers". The same routers transfer to an unseen Claude 3 Opus and Llama 3 8B pair with no retraining ([RouteLLM, LMSYS](https://www.lmsys.org/blog/2024-07-01-routellm/)). So the distribution a router must match is the task mix, while swapping the models underneath it is cheap. Harness placement follows from that asymmetry, because the harness is where the task mix is observable.

## When this backfires

- A narrow task distribution leaves nothing to classify. The criteria collapse to a constant and the classifier call becomes overhead, which is the arithmetic in [Routing Break-Even](routing-break-even.md). Open SWE spans features, fixes, tests, and questions, and 34% of its routed threads went to the fast tier.
- Criteria that read the surface form of a request carry bias that harness placement does not fix. A complexity router gave non-standard English registers a lower tier than meaning-equivalent standard English across 37,704 authentic learner sentence pairs, and "the effect is driven by a specific, common routing signal, input length, because non-standard registers omit function words and thus look shorter and therefore simpler" ([arXiv:2609.17542v1](https://arxiv.org/abs/2609.17542v1)).
- One decision per thread caps the result. LangChain's router picks once, on the first human message, before any output exists, which is the ceiling in [Router-Imposed Quality Ceiling](router-imposed-quality-ceiling.md). LangChain lists mid-thread re-routing under what it plans next. It notes that switching models throws the prompt cache away, "so the new model re-reads the thread at full price", and adds that "For async agents that cost is often negligible" ([LangChain, 1 October 2026](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness)). [Cache-Safe Routing Boundaries](cache-safe-routing-boundaries.md) covers where a switch may land instead.
- No outcome metric means no result. The finding rests on merged pull requests per thread, so an agent with no mergeable artifact needs a different signal. Routing with no quality signal at all is [Cost-Driven Model Routing Without Quality Monitoring](../anti-patterns/cost-routing-without-quality-monitoring.md).

## Example

Open SWE's router is one middleware file, [`agent/middleware/model_selection.py`](https://github.com/langchain-ai/open-swe/blob/main/agent/middleware/model_selection.py), with three parts:

- a base prompt telling the classifier to pick the least expensive model likely to complete the task
- a plain-language description of the work each tier should take
- a classifier model that reads the request and picks a tier

It runs on the thread's first human message ([LangChain, 1 October 2026](https://www.langchain.com/blog/how-to-build-a-model-router-in-the-harness)).

## Key Takeaways

- Write the tier criteria before choosing where the router runs. The criteria decide the placement, not the reverse.
- Check a harness-versus-gateway claim for a control arm. LangChain's 64% figure comes from a frontier-only baseline, so it measures routing rather than placement.
- Expect a classifier that reads request text to inherit register bias, and pick signals that do not reduce to input length.
- Ship the outcome metric first. If your agent produces nothing as countable as a merged pull request, solve that before you route.

## Related

- [Routing Break-Even: When a Cheaper Model Actually Pays](routing-break-even.md)
- [Cache-Safe Routing Boundaries: Where a Router May Act](cache-safe-routing-boundaries.md)
- [Router-Imposed Quality Ceiling: Committing Before Output](router-imposed-quality-ceiling.md)
- [Cost-Driven Model Routing Without Quality Monitoring](../anti-patterns/cost-routing-without-quality-monitoring.md)
- [Gateway Model Routing](gateway-model-routing.md)
