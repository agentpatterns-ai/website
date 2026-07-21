---
title: "Macro Evals for Agentic Systems: Population-Level Behavior Patterns"
term: "Macro Evals for Agentic Systems"
description: "Aggregate per-trace findings across a corpus of agent runs to surface recurring behavior patterns that single-trace evals cannot expose — when volume, judge quality, and selection bias permit."
tags:
  - testing-verification
  - evals
  - observability
  - tool-agnostic
aliases:
  - macro evaluation for agents
  - population-level agent evaluation
  - whole-task agent scoring
last_reviewed: 2026-07-21
maturity: established
---

# Macro Evals for Agentic Systems

> Macro evaluation aggregates per-trace findings across a corpus of agent runs to surface recurring behavior patterns that single-trace evals cannot expose.

Learn it hands-on with the [Evals at Scale guided lesson](https://learn.agentpatterns.ai/verification/evals-at-scale/), which includes quizzes.

Macro evaluation is the population-level layer above per-call and per-trace evals: it asks which problems repeat, where they concentrate, and which part of the workflow to inspect first — questions a single trace cannot answer because the signal is statistical, not local ([OpenAI Cookbook, 2026](https://developers.openai.com/cookbook/examples/partners/macro_evals_for_agentic_systems/macro_evals_for_agentic_systems)). Below the conditions where it earns its keep, it substitutes a heavy unsupervised pipeline for what a sorted frequency table would surface. For the agent-driven route to the same population-level question — scout agents proposing failure hypotheses that an investigator verifies against the corpus — see [Corpus-Level Trace Diagnostics](corpus-level-trace-diagnostics.md).

## When this layer applies

Three conditions decide whether the macro layer is the right tool ([OpenAI Cookbook, 2026](https://developers.openai.com/cookbook/examples/partners/macro_evals_for_agentic_systems/macro_evals_for_agentic_systems)):

- Trace volume in the thousands. The reference run analyzes 992 traces. Below this order of magnitude, density-based clustering (HDBSCAN over UMAP-reduced embeddings) either reports everything as noise or merges unrelated cases into spurious groups.
- A per-trace `eval_finding` reliable enough not to amplify bias systematically. Macro aggregation concentrates judge bias rather than averaging it out. Below ~70% judge precision, "behavior patterns" can be recurring judge mistakes ([AgentRewardBench, 2025](https://arxiv.org/abs/2504.08942)). Designing those per-trace criteria well is a discipline of its own: Microsoft's practitioner guidance on agent-experience (AX) evals argues for structuring eval scenarios and criteria to produce real signal rather than vanity pass rates ([Microsoft, 2026](https://developer.microsoft.com/blog/building-ax-evals-that-actually-work/)) — the more so at corpus scale, where macro aggregation over a vanity metric only concentrates its blind spots. Running an LLM-as-judge across thousands of traces is also a cost question: LangChain reports distilling a small task-specific judge that runs roughly 100× cheaper than a frontier judge, which keeps per-trace grading affordable at corpus scale ([LangChain, 2026](https://blog.langchain.com/blog/building-a-100x-cheaper-trace-judge-with-fireworks)).
- Cross-trace structure worth aggregating. Multi-specialist workflows where the same agent recurs across scenarios, or where conditions (tariffs, capacity, compliance) vary across runs, expose patterns that clustering can find. One-shot CI bots returning a patch per task do not.

When these hold, macro evals catch failures the [trajectory-opaque evaluation gap](eval-blind-spots.md) and [outcome grading](grade-agent-outcomes.md) cannot see — population properties of a workflow, not of any single run.

## The four-label taxonomy

The cookbook's reference implementation tags every analyzable trace with four labels ([OpenAI Cookbook, 2026](https://developers.openai.com/cookbook/examples/partners/macro_evals_for_agentic_systems/macro_evals_for_agentic_systems)):

| Label | What it captures | Granularity |
|-------|------------------|-------------|
| `case_type` | The generated business scenario (clean order, supplier substitution, pricing exception, compound) | Per-trace |
| `run_outcome` | How the workflow ended (completed, awaiting review, blocked, failed) | Per-trace |
| `eval_finding` | The local rubric symptom from per-call evals (final decision quality, policy compliance, routing, market drift, review appropriateness) | Per-trace, judge-graded |
| `behavior_pattern` | The recurring pattern surfaced by clustering across the corpus | Per-cluster |

The first three are inputs; the fourth is the macro output. Patterns rank by an `impact_score = prevalence × severity_weighted_prevalence` heuristic, so investigation time goes to patterns that occur often and hurt when they occur.

## Pipeline shape

```mermaid
graph TD
    A[Agent runs ~1000 traces] --> B[Per-call rubrics<br>5 categories via Promptfoo]
    B --> C[Per-trace findings<br>case_type + run_outcome + eval_finding]
    C --> D[Embed trace documents]
    D --> E[UMAP dim reduction]
    E --> F[HDBSCAN density clustering]
    F --> G[Label clusters<br>c-TF-IDF terms]
    G --> H[Rank by impact_score]
    H --> I[behavior_pattern]
```

The cookbook uses BERTopic-style ingredients: an embedding model, UMAP for dimensionality reduction, HDBSCAN for density clustering, and c-TF-IDF for distinctive cluster labels. The cluster step is an engineering choice. What matters is the shift in unit of analysis, not the specific algorithm ([OpenAI Cookbook, 2026](https://developers.openai.com/cookbook/examples/partners/macro_evals_for_agentic_systems/macro_evals_for_agentic_systems)).

## Why it works

Some failure classes are not properties of any single trace. An agent that drops a constraint in step 2, drifts when two conditions interact, or triggers review for the wrong cases produces individually plausible traces. The failure is the concentration of similar suboptimal decisions across runs, not the badness of any one. Shifting the unit of analysis to a labeled subset of the corpus makes a cluster with poor `eval_finding` concrete evidence of recurring system behavior that per-trace scoring cannot expose ([OpenAI Cookbook, 2026](https://developers.openai.com/cookbook/examples/partners/macro_evals_for_agentic_systems/macro_evals_for_agentic_systems)). Independent corroboration comes from trace-grounded rubric evaluation, which finds state-tracking inconsistency 2.7× more prevalent in failed runs than passing runs ([TraceSIR, 2026](https://arxiv.org/abs/2603.00623)).

## Example

A synthetic EV order workflow runs 992 traces. Specialist agents handle pricing, compliance, supply risk, factory routing, scheduling, and release decisions while market conditions vary. Per-call evals (helpfulness, policy compliance, routing correctness) report acceptable scores — the same [outcome-grading](grade-agent-outcomes.md) view that sees each trace in isolation. The macro layer surfaces a different signal:

```
Cluster 7 — pricing-incentive-omission (impact_score: 0.42)
  prevalence:  18% of supplier-substitution case_type
  severity:    8/14 traces ended awaiting-review
  pattern:     pricing agent ignored the supplier-substitution incentive
               when stockout flag also present
  next step:   inspect pricing-agent prompt under compound conditions
```

No individual trace looked broken — the pricing agent answered every turn correctly given its inputs. The macro layer reveals that pricing systematically ignores the substitution-incentive interaction whenever stockout pressure compounds with it. The fix is at the prompt or specialist boundary, not at any single response.

## When this backfires

Macro evaluation is a heavy pipeline and a noisy aggregator. Narrow the scope when:

- Trace volume is low. Below ~1,000 traces, HDBSCAN reports noise or collapses unrelated cases together. Macro evals on a 50-trace set are theater; a frequency table of `(case_type, error_code)` carries the same signal at zero pipeline cost.
- The per-trace judge is below the precision floor. AgentRewardBench measured 12 LLM judges on 1,302 web-agent trajectories, and none cleared human inter-annotator agreement, with errors clustering around grounding mismatch and misunderstood actions ([AgentRewardBench, 2025](https://arxiv.org/abs/2504.08942)). TRAIL found long-context LLMs score only 11% on trace-debugging tasks ([TRAIL, 2025](https://arxiv.org/abs/2505.08638)). Macro aggregation amplifies these errors, so clusters become recurring judge mistakes that look like system behavior.
- The analysis pool is selection-biased. The cookbook's pipeline only clusters traces already carrying failure, review, or Promptfoo signals ([OpenAI Cookbook, 2026](https://developers.openai.com/cookbook/examples/partners/macro_evals_for_agentic_systems/macro_evals_for_agentic_systems)). Reading the clusters as "how the system behaves" is wrong; they describe the pathology of flagged traces. Acting on them as a triage queue is correct.
- Agents are one-shot, not corpus-shaped. A CI agent that takes a task and returns a patch has no recurring cross-trace structure; the relevant failure modes are per-trace (correctness, safety) and per-call (tool selection). [pass@k metrics](pass-at-k-metrics.md) and [trajectory decomposition](trajectory-decomposition-diagnosis.md) cover the workload.
- Spec churn changes the case-type distribution faster than the suite regenerates. Clusters labeled last week describe a system that no longer exists; impact scores become a moving target rather than a comparable signal across releases.
- The eval definitions are locked to one platform. The macro pipeline runs its per-call rubrics through Promptfoo, but a corpus-scale suite outlives any single harness. Keep eval definitions framework-agnostic so a platform deprecation does not strand the suite. OpenAI's cookbook walks through porting an existing suite off the deprecated OpenAI Evals product into Promptfoo for exactly this reason ([OpenAI Cookbook — moving from OpenAI Evals to Promptfoo, 2026](https://developers.openai.com/cookbook/examples/evaluation/moving-from-openai-evals-to-promptfoo)).
- Clusters are mistaken for diagnosis. The cookbook itself warns that clustering is not proof of causality, and suspect scoring guides inspection rather than locating the fault ([OpenAI Cookbook, 2026](https://developers.openai.com/cookbook/examples/partners/macro_evals_for_agentic_systems/macro_evals_for_agentic_systems)). A cluster labeled "pricing-incentive-omission" is a hypothesis to test, not a verdict to ship a fix against.

Macro evaluation pairs with per-call rubrics, trajectory-aware safety auditing, and outcome grading; it does not replace them. It is the third eval tier when the first two are in place and the workload supplies the corpus to aggregate over.

## Key Takeaways

- Macro evals are the population-level layer above per-call and per-trace evals, surfacing recurring patterns that are properties of the corpus, not of any single run.
- The four-label taxonomy (`case_type`, `run_outcome`, `eval_finding`, `behavior_pattern`) separates per-trace inputs from the per-cluster macro output.
- Pipeline: per-call rubrics → embed traces → UMAP + HDBSCAN → c-TF-IDF labelling → impact-score ranking. The shift in unit of analysis, not the clustering algorithm, is the mechanism.
- Three pre-conditions must hold: thousands of traces, judge precision above ~70%, cross-trace structure. Outside those, frequency tables do the same job.
- Clusters are hypotheses, not diagnoses — the selection-biased pool describes flagged-trace pathology, not full-system behavior.

## Related

- [Trajectory-Opaque Evaluation Gap](eval-blind-spots.md) — Per-trace safety blindness; macro evals are the population-level analogue across the corpus.
- [Multi-Turn Conversation Evaluation](multi-turn-conversation-evaluation.md) — Per-turn plus trace-level scoring within one conversation; macro evals extend the pattern across many conversations.
- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — Per-trace outcome grading; macro evals aggregate outcomes plus findings across runs.
- [Trajectory Decomposition: Diagnose Where Coding Agents Fail](trajectory-decomposition-diagnosis.md) — Per-trace stage-level diagnosis; macro evals look at recurring stage failures across the corpus.
- [Structural Coverage Criteria for Agent Workflows](structural-coverage-agent-workflows.md) — Adequacy floor for declared workflow edges; macro evals score behavior across runs against declared structure.
- [Corpus-Level Trace Diagnostics](corpus-level-trace-diagnostics.md) — The agent-driven route to the same population-level question: scout-proposed failure hypotheses verified against the corpus, viable from ~100 traces where this page's clustering needs ~1,000.
