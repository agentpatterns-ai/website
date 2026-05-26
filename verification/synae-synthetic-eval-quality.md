---
title: "Measuring Synthetic Eval Data Quality (SynAE)"
description: "Score synthetic tool-calling agent eval datasets on three axes — validity, fidelity, diversity — across four trace components, before letting a synthetic suite gate deploys against a production distribution it may have drifted from."
tags:
  - testing-verification
  - evals
  - tool-agnostic
aliases:
  - synthetic eval quality measurement
  - SynAE framework
---

# Measuring Synthetic Eval Data Quality (SynAE)

> Score synthetic tool-calling agent eval datasets on validity, fidelity, and diversity across task instructions, tool calls, final outputs, and downstream eval results — before letting a synthetic suite gate deploys against a production distribution it may have drifted from.

SynAE is a quality-measurement layer for synthetic eval datasets used to test multi-turn tool-calling agents. It compares a synthetic set against a real production-trace reference along three pillars — validity, fidelity, diversity — for each of four trace components, producing a per-axis diagnostic instead of an opaque pass/fail ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).

## When the Framework Applies

Four preconditions must hold ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)):

- **A real production-trace reference exists.** Fidelity and diversity are distances against a real distribution. Greenfield products have nothing to compare against.
- **The agent is multi-turn and tool-calling.** Metric categories collapse on single-turn or non-tool-using agents.
- **The synthetic set is large enough for distributional metrics.** Vendi Score and embedding-based precision/recall are unstable on small samples.
- **The team can absorb the judge cost.** Validity scoring runs 450+ LLM-as-judge calls per dataset at F1 = 0.86 against humans — 14% disagreement at the measurement layer itself.

If any precondition fails, a [golden query pair](golden-query-pairs-regression.md) or [incident-derived regression](incident-to-eval-synthesis.md) suite gives a stable signal at lower overhead.

## The Three Pillars

Three orthogonal axes apply to each of four trace components — task instructions and intermediate responses, tool calls, final outputs, downstream eval outcomes ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)):

| Pillar | What it measures | Sample metric |
|--------|------------------|---------------|
| **Validity** | Do synthetic tool calls and outputs successfully fulfil the given instructions? | Validity Rate from LLM judge or rule checker |
| **Fidelity** | How close is the synthetic distribution to the real one? | Key Node Dependency, embedding precision/recall, downstream task-difficulty distance |
| **Diversity** | How much of the real-data spread does the synthetic set cover? | Vendi Score, Attribute Diversity |

A set can score high on one axis and fail on another. The decomposition exists because the authors found "no single metric is sufficient to fully characterize synthetic data quality" ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).

## Why It Works

Synthetic eval datasets diverge from production silently because the generator's prior is not the user's prior. Generators sample from model-induced distributions — templated prompts, in-context examples, fixed tool schemas — while production samples from real intents, tool errors, and multi-step plans. A synthetic suite that passes can still let a deploy regress against real users.

SynAE works by decomposition: scoring each trace component on each pillar attributes ranking distortion to a specific axis instead of a black-box pass/fail. The paper grounds this in controlled experiments where each generation failure mode moves a predictable pillar in a predictable direction ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).

## Diagnostic Patterns

Five controlled failure modes the authors injected and the pillar signatures they produced ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)):

| Generation choice | Validity | Fidelity | Diversity | What to do |
|-------------------|----------|----------|-----------|------------|
| **Blank Filling** — mask tokens, resample | — | Down | Up | Tighten the mask or constrain regeneration |
| **Oversampling** — duplicate frequent sequences | — | Down | Down | Stratify against the real distribution |
| **In-Context Generation** with fixed examples | — | Mixed | Capped | Rotate exemplars; watch fidelity per metric |
| **Invalidation** — traces that do not work | Down | — | — | Add validity filters before entry |
| **Naive Relabeling** — keyword substitution | Down | — | Up | Use semantically grounded transformations |

Read the pillar movements together — a single failing axis often points to one specific generation choice.

## How to Use It

1. Pull a stable production-trace reference; [incident-to-eval synthesis](incident-to-eval-synthesis.md) is one source.
2. Run all three pillars on all four components — a single score hides cross-axis trade-offs.
3. Match failure signatures to fixes using the table above.
4. Recheck after each intervention; verify lightweight fixes do not move a non-target pillar wrong ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).
5. Do not collapse to a single score — the authors note averaging normalized metrics "is not necessarily the most meaningful way as they may scale differently."

## When This Backfires

Skip or replace the framework when:

- **No production reference exists.** Fidelity and diversity reduce to noise; a small [golden query pair](golden-query-pairs-regression.md) suite is the cheaper substitute.
- **Single-turn or non-tool-calling agents.** The four-component decomposition collapses; standard output grading is equally informative.
- **Pure frozen smoke-test usage.** If the set is a fixed gate for known issues, distributional fidelity is irrelevant — a pass/fail suite costs a fraction of the judge calls.
- **Vendor platforms already bundle validity and fidelity scoring** into the generator ([Databricks](https://www.databricks.com/blog/streamline-ai-agent-evaluation-with-new-synthetic-data-capabilities), [Tonic.ai](https://www.tonic.ai/guides/synthetic-data-for-agentic-ai-workflows)) — a separate measurement layer becomes redundant.
- **Uncalibrated LLM-as-judge setup.** Without [judge calibration](anti-reward-hacking.md), the framework's outputs mislead more than they help.
- **Interactive or multi-agent settings.** The paper scopes SynAE to single-agent multi-turn tool-calling; extensions are flagged as future work, not validated ([arxiv.org/abs/2605.22564](https://arxiv.org/abs/2605.22564)).

## Relation to Adjacent Practices

SynAE measures the eval suite itself; the suite it scores is built from techniques like [golden query pairs](golden-query-pairs-regression.md) and [incident-to-eval synthesis](incident-to-eval-synthesis.md). It does not replace [benchmark contamination defences](benchmark-contamination-eval-risk.md) — contamination is about whether the eval set leaked into training, while SynAE is about whether the eval set resembles production at all.

## Key Takeaways

- Synthetic eval data drifts silently from production; SynAE catches the drift before a deploy gate trusts the synthetic suite.
- Score on three orthogonal pillars across four trace components — the matrix is the artefact, not an aggregated number.
- Five known generation failure modes have predictable pillar signatures; read the signatures to pick the right fix.
- Skip when there is no production reference, the agent is single-turn, the set is small, or the LLM judge is uncalibrated.
- The framework's own validity check is bounded by LLM-judge F1 of 0.86 against humans — treat the measurement layer as one more component that needs calibration.

## Related

- [Golden Query Pairs as Continuous Regression Tests for Agents](golden-query-pairs-regression.md)
- [Incident-to-Eval Synthesis: Production Failures as Evals](incident-to-eval-synthesis.md)
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md)
- [Data Fidelity Guardrails](data-fidelity-guardrails.md)
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](anti-reward-hacking.md)
