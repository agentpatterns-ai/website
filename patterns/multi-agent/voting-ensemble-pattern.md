---
title: "Voting / Ensemble Pattern for AI Agent Development"
term: "Voting / Ensemble Pattern"
description: "Run the same task N times in parallel and aggregate via voting to trade compute for confidence in classification and security decisions."
aliases:
  - Self-Consistency
  - Majority Voting
  - Multi-Model Consensus
tags:
  - agent-design
  - cost-performance
  - workflows
  - multi-agent
  - tool-agnostic
last_reviewed: 2026-06-13
maturity: established
---

# Voting / Ensemble Pattern

> Run the same task N times in parallel, then aggregate results through voting to trade compute for confidence.

Related lesson: [Fan-Out and Synthesis](https://learn.agentpatterns.ai/multi-agent/fan-out-and-synthesis/) — this concept features in a hands-on lesson with quizzes.

!!! note "Also known as"
    Self-Consistency, Majority Voting, Multi-Model Consensus. For the complementary pattern that merges strengths rather than voting, see [Fan-Out Synthesis](fan-out-synthesis.md). For specialized multi-lens review, see [Committee Review](../../code-review/committee-review-pattern.md).

## Structure

```mermaid
graph TD
    A[Task] --> B[Run 1]
    A --> C[Run 2]
    A --> D[Run N]
    B --> E[Aggregator]
    C --> E
    D --> E
    E -->|Consensus reached| F[Accept]
    E -->|No consensus| G[Escalate / Re-run]
```

Unlike fan-out synthesis (which assembles the best parts from diverse outputs) or committee review (which applies different lenses), voting runs identical tasks and picks the answer the runs agree on.

## Three fan-out tactics

| Tactic | Setup | Diversity source |
|--------|-------|-----------------|
| Self-consistency sampling | Same model, same prompt, high temperature | Stochastic variation across reasoning paths |
| Prompt ensembles | Same model, varied prompts | Different framings surface different reasoning |
| Multi-model consensus | Different models, same prompt | Independent training data and failure modes |

Multi-model consensus provides the strongest diversity: calling one model N times repeats its mistakes, while different models fail independently.

## When voting helps

Voting works best on tasks with discrete, verifiable outputs where the correct answer exists but a single run might miss it:

- Classification — is this input malicious, compliant, or out-of-scope?
- Security flagging — does this diff introduce a vulnerability? (the [adversarial multi-model](adversarial-multi-model-pipeline.md) use case)
- Content moderation — does this output violate policy?
- Code correctness checks — does this function handle the edge case?

Voting adds little value for creative synthesis, open-ended generation, or real-time responses where latency matters more than marginal accuracy.

## Choosing N

The original self-consistency paper ([Wang et al. 2023](https://arxiv.org/abs/2203.11171)) showed +17.9% accuracy on GSM8K by majority-voting over sampled reasoning paths. But more is not always better.

| N | Effect |
|---|--------|
| 1 | Baseline — no voting benefit |
| 3 | Strong gains for most classification and verification tasks |
| 5 | Marginal improvement over 3; good ceiling for most use cases |
| 7+ | Diminishing or inverted returns — more calls can hurt on hard queries |

Kore.ai's [scaling law research](https://blog.kore.ai/cobus-greyling/performing-multiple-llm-calls-voting-on-the-best-result-are-subject-to-scaling-laws) confirms that performance first increases then decreases with N — more calls help on easy queries but hurt on hard ones. The best count depends on the task, so measure it empirically.

## Aggregation strategies

Simple majority voting treats all runs equally, but misses easy accuracy gains.

| Strategy | Mechanism | Trade-off |
|----------|-----------|-----------|
| Majority vote | Most common answer wins | Simple; ignores model quality differences |
| Weighted vote | Runs scored by model capability or historical accuracy | Better accuracy; requires calibration data |
| Confidence-weighted | Weight by model's reported confidence score | ~46% compute reduction at equivalent accuracy ([Taubenfeld et al. 2025](https://arxiv.org/abs/2502.06233)) |
| Unanimous | All runs must agree; else escalate | High precision, low recall — good for safety-critical |
| Semantic similarity | Cluster answers by meaning, pick densest cluster | Handles paraphrased equivalents |

Advanced methods like Optimal Weight and Inverse Surprisingly Popular algorithms consistently outperform standard majority voting by accounting for model heterogeneity and answer correlations ([Ai et al. 2025](https://arxiv.org/abs/2510.01499)).

## Cost trade-off

N runs costs N× tokens. Confidence-weighted voting cuts this nearly in half by early-stopping when confidence is high — start with N=3 and scale to 5 only if accuracy justifies it; if 3/3 agree confidently, skip the rest.

For routine tasks with strong single-run baselines, voting is wasteful. Reserve it for decisions where a false positive or false negative carries real cost.

## Why it works

LLMs are stochastic: the same prompt draws from a distribution of reasoning paths. Wrong answers scatter — each error follows its own spurious chain of thought — while correct answers cluster, because independent paths converge on the same consistent logic. Majority voting picks the answer most paths agree on, drowning out one-off errors ([Wang et al. 2023](https://arxiv.org/abs/2203.11171)).

[Multi-model consensus](multi-model-plan-synthesis.md) strengthens this further. Different models have independent failure modes rooted in distinct training data and architectures, so an error that is systematic for one model is uncorrelated with errors in another — the correct answer remains the densest cluster even as ensemble size grows.

This whole argument rests on errors being independent, and that assumption is fragile. When the runs share training lineage — same base model, or smaller models distilled from a common teacher — their mistakes correlate, and correlated wrong answers cluster just as tightly as correct ones, so the majority can confidently converge on the same error. Distillation makes nominally "different" models behave alike; tracking pairwise [agent-genealogical similarity](../../verification/distillation-induced-similarity-metrics.md) surfaces when the ensemble's diversity is an illusion and the voting gain has collapsed.

## Example

Security review of a pull request using 3-model consensus:

```python
import asyncio, json
from anthropic import Anthropic
from openai import OpenAI

PROMPT = "Review this diff for security vulnerabilities. Return JSON: {\"verdict\": \"SAFE\" | \"UNSAFE\", \"findings\": [...]}\n\n"

async def review_with_model(name, call_fn, diff):
    resp = await call_fn(PROMPT + diff)
    return {"model": name, **json.loads(resp)}

async def vote_on_diff(diff: str):
    results = await asyncio.gather(
        review_with_model("claude", call_claude, diff),
        review_with_model("gpt4", call_gpt4, diff),
        review_with_model("gemini", call_gemini, diff),
    )
    unsafe = sum(1 for r in results if r["verdict"] == "UNSAFE")
    if unsafe >= 2:
        return {"action": "BLOCK", "findings": merge_findings(results)}
    if unsafe == 1:
        return {"action": "MERGE", "dissent": [r for r in results if r["verdict"] == "UNSAFE"]}
    return {"action": "MERGE", "findings": []}
```

The three models have independent failure modes: a vulnerability one model misses, another is likely to catch.

## Key Takeaways

- Voting trades compute for confidence — same task, multiple runs, aggregated verdict
- Multi-model diversity beats same-model repetition for genuine independence
- 3-5 runs covers most use cases; beyond that, returns diminish or invert
- Confidence-weighted aggregation cuts compute by ~46% versus naive majority voting ([Taubenfeld et al. 2025](https://arxiv.org/abs/2502.06233))
- Reserve voting for discrete, verifiable tasks (classification, security, compliance) — not open-ended generation
- Distinct from fan-out synthesis (which merges complementary strengths) and committee review (which applies specialized lenses)

## Related

- [Fan-Out Synthesis Pattern](fan-out-synthesis.md)
- [Committee Review Pattern](../../code-review/committee-review-pattern.md)
- [Adversarial Multi-Model Pipeline](adversarial-multi-model-pipeline.md)
- [LLM Map-Reduce](llm-map-reduce.md)
- [Multi-Model Plan Synthesis](multi-model-plan-synthesis.md)
- [Orchestrator-Worker](orchestrator-worker.md)
- [Multi-Agent Topology Taxonomy](multi-agent-topology-taxonomy.md)
- [Cost-Aware Agent Design](../../token-engineering/cost-aware-agent-design.md)
