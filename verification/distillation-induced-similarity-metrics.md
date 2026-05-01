---
title: "Distillation-Induced Similarity Metrics for Tool-Use Agents"
description: "Quantify how much two models share non-mandatory tool-use behaviour using Response Pattern Similarity and Action Graph Similarity — surface correlated failure modes before routing or ensembling treats them as independent."
tags:
  - testing-verification
  - evals
  - agent-design
  - tool-agnostic
aliases:
  - response pattern similarity
  - action graph similarity
  - RPS and AGS metrics
---

# Distillation-Induced Similarity Metrics for Tool-Use Agents

> Quantify how much two models share non-mandatory tool-use behaviour. When fallback or ensemble models are distilled echoes of the primary, treating them as independent inflates routing diversity and consensus voting.

## Why Behavioural Overlap Matters

Cross-vendor routing and ensembling assume vendor diversity buys behavioural diversity. Distillation breaks that assumption: a student trained on a teacher's trajectories inherits the teacher's *non-mandatory* preferences (when to verify after writing, which optional tools to invoke) alongside task capability. Benchmark scores measure success rate, not behavioural overlap, so the inheritance is invisible at the leaderboard layer.

Yang et al. propose two metrics that isolate non-mandatory behaviour, evaluated across 18 models from 8 providers on τ-Bench and τ²-Bench against Claude Sonnet 4.5 (thinking) ([arxiv.org/abs/2604.21255](https://arxiv.org/abs/2604.21255)).

## Response Pattern Similarity (RPS)

RPS measures verbal alignment. Each trajectory is segmented into five canonical stages — authentication, elicitation, execution, verification, notification — and an LLM judge scores style, structure, and alignment per stage on a 0–5 scale. Segmenting before scoring lets the metric compare semantically matched content across variable-length trajectories ([arxiv.org/abs/2604.21255](https://arxiv.org/abs/2604.21255)).

## Action Graph Similarity (AGS)

AGS treats a trajectory as a directed graph — nodes are tool calls, edges are output dependencies — and decomposes similarity into three sub-metrics ([arxiv.org/abs/2604.21255](https://arxiv.org/abs/2604.21255)):

- **SnodeS — optional tool agreement.** Of the tools a model invokes that the task does not require, which overlap?
- **SseqS — local sequence patterns.** Habits like post-write verification, pre-write confirmation, and error-retry shape.
- **SdepS — dependency patterns.** Output-reuse rate, dependency chain depth, fan-out from a single tool's output.

A model can match a teacher on one dimension and diverge on others — verbal style alone (RPS) or topology alone (SdepS) does not capture the full distillation footprint.

## What the Paper Measured

Three findings are load-bearing for routing decisions:

- **Within-family pairs cluster.** Same-provider pairs score 5.9 percentage points higher in AGS than cross-family pairs — measurable but not the dominant effect.
- **Cross-family convergence happens.** Kimi-K2 (thinking) reaches 82.6% SnodeS and 94.7% SdepS against Claude Sonnet 4.5, exceeding Anthropic's own Opus 4.1 on the same metrics. Vendor boundaries do not protect against convergence when a teacher's traces have leaked into a student's training pipeline.
- **RPS and AGS are not redundant.** Pearson r = 0.491 between them — verbal style and tool-invocation choices capture distinct dimensions, so routing decisions need both.

A controlled distillation experiment isolates the mechanism: fine-tuning Qwen2.5-14B-Instruct on Sonnet 4.5 trajectories via LoRA shifted AGS toward the teacher (+0.13) and away from a control (−0.05), while a graph-edit-distance baseline rose equally toward both — the AGS decomposition picks up teacher-specific transfer that simpler graph metrics miss ([arxiv.org/abs/2604.21255](https://arxiv.org/abs/2604.21255)).

## When the Metrics Apply

| Use case | Why the metrics help |
|----------|----------------------|
| [Cross-vendor competitive routing](../agent-design/cross-vendor-competitive-routing.md) | Confirms whether the secondary vendor's failure modes are uncorrelated, or rebranded distillation lineage |
| [Voting / ensemble pattern](../multi-agent/voting-ensemble-pattern.md) | Voting confidence assumes errors are independent — high pairwise AGS invalidates the assumption |
| [Adversarial multi-model pipeline](../multi-agent/adversarial-multi-model-pipeline.md) | Pre-screen candidate adversaries by RPS/AGS distance |
| Fallback model selection | Pick the lowest-AGS competent model, not the closest one |

## Failure Conditions

- **Outside tool-use trajectories.** RPS and AGS are defined over multi-stage tool-call traces. Single-turn classification, RAG QA, and chat tasks need different metrics.
- **Without matched benchmark traces.** Computing RPS/AGS requires running both models on the same task suite under the same harness; teams without τ-Bench-style infrastructure cannot replicate the scores directly.
- **Across model generations.** AGS describes two specific checkpoints. By the time measurement finishes, both providers have shipped a new generation — the metric is a snapshot, not a forecast.
- **When consistency is the goal.** For systems whose parsers and templates depend on consistent verbal style, high RPS to a known-good primary is a feature. The metric tells you the cost-of-redundancy trade-off; it does not declare which side is right.

## Adjacent Failure Modes

The same root cause — correlated blind spots from shared lineage — surfaces at other layers:

| Layer | Pattern | Defence |
|-------|---------|---------|
| Tool-use agents (this page) | Students inherit teacher's optional-tool habits | Measure RPS/AGS before assuming routing diversity |
| Test generation | LLM-written tests share LLM-written code's blind spots ([test-homogenization-trap.md](../anti-patterns/test-homogenization-trap.md)) | Different model for tests vs code; mutation-guided generation |
| Multi-agent analysis | Same-family agents reach the same wrong answer ([nonstandard-errors-ai-agents.md](nonstandard-errors-ai-agents.md)) | Sample across families; treat single-run output as one draw |

## Example

A team running cross-vendor routing with Claude Sonnet 4.5 primary and Kimi-K2 (thinking) fallback assumes a Claude failure on a τ-Bench-style retail task means Kimi has roughly independent odds of recovering it. The paper's measurement says otherwise:

```
Pair: Claude Sonnet 4.5 (thinking) vs Kimi-K2 (thinking)
  SnodeS (optional tool agreement):     82.6%
  SdepS (dependency pattern overlap):   94.7%
  RPS (verbal alignment, 0-5):          3.65
```

These overlaps exceed Sonnet 4.5 vs Opus 4.1 within Anthropic's own family ([arxiv.org/abs/2604.21255](https://arxiv.org/abs/2604.21255)). The routing assumption — different vendor implies different failure modes — is wrong for this specific pair on this task family. Either pick a different fallback whose AGS to Sonnet is lower, or accept that this fallback exists for capacity rather than redundancy and adjust the failure-mode assumptions downstream consumers make.

## Key Takeaways

- Distillation transfers non-mandatory behaviour — optional tool choice, sequence habits, dependency topology — alongside task capability; benchmark scores cannot see this transfer
- RPS measures verbal alignment, AGS measures tool-use graph alignment; the two correlate weakly (r = 0.491) and need to be reported together
- Cross-vendor routing and ensemble voting both assume independent failure modes — measure RPS/AGS before treating two models as independent
- Within-family pairs cluster more (5.9 pp higher AGS) but cross-family convergence still occurs — vendor boundaries do not guarantee behavioural diversity
- The metrics are a snapshot of two checkpoints, defined over tool-use trajectories — they do not transfer to single-turn tasks or generalise across model generations

## Related

- [Cross-Vendor Competitive Routing](../agent-design/cross-vendor-competitive-routing.md) — the routing pattern these metrics test
- [Voting / Ensemble Pattern](../multi-agent/voting-ensemble-pattern.md) — independence assumption that AGS can falsify
- [Adversarial Multi-Model Pipeline](../multi-agent/adversarial-multi-model-pipeline.md) — adversarial review depends on different failure modes
- [Test Homogenization Trap](../anti-patterns/test-homogenization-trap.md) — the same correlated-blind-spot failure at the test-generation layer
- [Nonstandard Errors in AI Agents](nonstandard-errors-ai-agents.md) — model-family clustering observed in agent analysis tasks
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — adjacent measurement-integrity risk
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — complementary trajectory analysis at finer granularity
