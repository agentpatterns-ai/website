---
title: "Measuring Synthetic Eval Data Quality (SynAE)"
term: "Measuring Synthetic Eval Data Quality"
description: "Score synthetic tool-calling agent eval datasets on three axes — validity, fidelity, diversity — across four trace components, before letting a synthetic suite gate deploys against a production distribution it may have drifted from."
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
aliases:
  - synthetic eval quality measurement
  - SynAE framework
last_reviewed: 2026-06-12
maturity: emerging
---

# Measuring Synthetic Eval Data Quality (SynAE)

> Score synthetic tool-calling eval datasets on validity, fidelity, and diversity across four trace components before trusting them to gate deploys against production.

SynAE is a quality-measurement layer for synthetic eval datasets that test multi-turn tool-calling agents. It scores a synthetic set against a real production-trace reference along three pillars — validity, fidelity, and diversity — across four trace components. The result is a per-axis diagnostic, not a single pass or fail ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).

## When the framework applies

Four preconditions must hold: a real production-trace reference exists, the agent is multi-turn and tool-calling, the synthetic set is large enough for distributional metrics (Vendi Score and embedding precision/recall are unstable on small samples), and you can absorb the judge cost. Validity scoring runs 450+ LLM-as-judge calls per dataset at F1 = 0.86 against humans ([arxiv.org/abs/2605.22564v1](https://arxiv.org/abs/2605.22564v1)).

If any fails, a [golden query pair](golden-query-pairs-regression.md) or [incident-derived regression](incident-to-eval-synthesis.md) suite gives a stable signal more cheaply.

## The three pillars

Three orthogonal axes apply to each of four trace components — task instructions and intermediate responses, tool calls, final outputs, downstream eval outcomes ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)):

| Pillar | What it measures | Sample metric |
|--------|------------------|---------------|
| Validity | Do synthetic tool calls and outputs successfully fulfill the given instructions? | Validity Rate from LLM judge or rule checker |
| Fidelity | How close is the synthetic distribution to the real one? | Key Node Dependency, embedding precision/recall, downstream task-difficulty distance |
| Diversity | How much of the real-data spread does the synthetic set cover? | Vendi Score, Attribute Diversity |

A set can score high on one axis and fail another. The decomposition exists because the authors found "no single metric is sufficient to fully characterize synthetic data quality" ([arxiv.org/abs/2605.22564v1](https://arxiv.org/abs/2605.22564v1)).

## Why it works

Synthetic datasets diverge from production silently because the generator's prior is not the user's. Generators sample from model-induced distributions — templated prompts, in-context examples, fixed tool schemas — while production samples real intents, tool errors, and multi-step plans. A passing synthetic suite can still let a deploy regress where a [golden query pair](golden-query-pairs-regression.md) suite would not.

SynAE counters this by decomposition: scoring each trace component on each pillar attributes ranking distortion to a specific axis rather than a black-box verdict. The paper grounds this in controlled experiments where each generation failure mode moves a predictable pillar ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).

## Diagnostic patterns

Five failure modes the authors injected, and the pillar signatures they produced ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)):

| Generation choice | Validity | Fidelity | Diversity | What to do |
|-------------------|----------|----------|-----------|------------|
| Blank Filling — mask tokens, resample | — | Down | Up | Tighten the mask or constrain regeneration |
| Oversampling — duplicate frequent sequences | — | Down | Down | Stratify against the real distribution |
| In-Context Generation with fixed examples | — | Mixed | Capped | Rotate exemplars; watch fidelity per metric |
| Invalidation — traces that do not work | Down | — | — | Add validity filters before entry |
| Naive Relabeling — keyword substitution | Down | — | Up | Use semantically grounded transformations |

Read the pillar movements together — a single failing axis often points to one generation choice.

## How to use it

1. Pull a stable production-trace reference; [incident-to-eval synthesis](incident-to-eval-synthesis.md) is one source.
2. Run all three pillars on all four components — a single score hides cross-axis trade-offs.
3. Match failure signatures to fixes using the table above.
4. Recheck after each intervention; verify a fix does not move a non-target pillar ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).
5. Do not collapse to a single score — the authors note averaging normalized metrics "is not necessarily the most meaningful way as they may scale differently."

## When this backfires

Skip or replace the framework when:

- No production reference. Fidelity and diversity reduce to noise, and a small [golden query pair](golden-query-pairs-regression.md) suite is cheaper.
- Single-turn or non-tool-calling agents. The four-component decomposition collapses, and output grading is equally informative.
- Frozen smoke-test usage. For a fixed gate on known issues, distributional fidelity is irrelevant, and a pass/fail suite costs a fraction of the judge calls.
- Vendor platforms already bundle validity and fidelity scoring into the generator ([Databricks](https://www.databricks.com/blog/streamline-ai-agent-evaluation-with-new-synthetic-data-capabilities), [Tonic.ai](https://www.tonic.ai/guides/synthetic-data-for-agentic-ai-workflows)), so a separate layer is redundant.
- Uncalibrated LLM judge. Without [judge calibration](anti-reward-hacking.md), the outputs mislead more than they help.
- Interactive or multi-agent settings. The paper scopes SynAE to single-agent multi-turn tool-calling, and extensions are future work, not validated ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).

## Key Takeaways

- Synthetic eval data drifts silently from production — the same idealized-condition inflation [benchmark contamination as eval risk](benchmark-contamination-eval-risk.md) describes; SynAE catches the drift before a deploy gate trusts the suite.
- Score on three orthogonal pillars across four trace components — the matrix is the artifact, not an aggregated number.
- Five known generation failure modes have predictable pillar signatures; read the signatures to pick the right fix.
- Skip when there is no production reference, the agent is single-turn, the set is small, or the LLM judge is uncalibrated.
- The validity check is itself bounded by LLM-judge F1 of 0.86 — treat the measurement layer as one more component that needs calibration.

## Related

- [Golden Query Pairs as Continuous Regression Tests for Agents](golden-query-pairs-regression.md)
- [Incident-to-Eval Synthesis: Production Failures as Evals](incident-to-eval-synthesis.md)
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md)
- [Data Fidelity Guardrails](data-fidelity-guardrails.md)
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md)
