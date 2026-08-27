---
title: "Specification Portability Across Coding Agents"
term: "Specification Portability"
description: "Swapping the agent that implements a specification moves the output in both directions, so re-run the spec against a baseline before trusting the swap."
tags:
  - instructions
  - workflows
  - tool-agnostic
  - arxiv
aliases:
  - cross-agent specification transfer
  - foreign specification ingestion
last_reviewed: 2026-08-24
maturity: emerging
---

# Specification Portability Across Coding Agents

> Handing one agent's specification to another changes the generated code, in both directions, so measure the swap against a baseline before you trust it.

Specification portability is how well a specification written under one agent environment keeps its effect when a different agent implements from it ([Grynets et al., 2026](https://arxiv.org/abs/2608.21208v1)). It is a property you measure per spec and per agent pair, not one you inherit from the fact that both agents read Markdown.

## What the measured transfers did

One study exchanged specifications between Amazon Kiro, Antigravity with Gemini, and Spec Kit with Copilot on an Oracle-to-PostgreSQL migration over 1,802 scripts. The three foreign transfers did not point the same way ([Grynets et al., 2026](https://arxiv.org/abs/2608.21208v1)):

| Implementing agent | Spec origin | SQL syntax validity | AST similarity |
|---|---|---|---|
| Kiro | Kiro (native) | 33.74% | 0.207 |
| Kiro | Gemini | 43.51% | 0.31 |
| Gemini | Gemini (native) | 45.54% | 0.69 |
| Gemini | Kiro | 0% | 0.08 |
| Copilot | Copilot (native) | 43.51% | 0.257 |
| Copilot | Kiro | 43.4% | 0.55 |

Kiro got better on every metric reading a foreign spec. Copilot held its syntax validity and more than doubled structural similarity. Gemini collapsed. A repeat run of that cell returned Token F1 0.035 and 2.33% validity. It reproduces the collapse, not the magnitude: the first run scored Token F1 0.68 ([Grynets et al., 2026](https://arxiv.org/abs/2608.21208v1)).

Size predicted nothing. Kiro's specification ran about 1,597 lines and Gemini's about 193; the longer one did not produce better code ([Grynets et al., 2026](https://arxiv.org/abs/2608.21208v1)).

## Why it works

The cause sits in representation, not in missing content. When Gemini was asked to rewrite the same Kiro specification into its own preferred form before generating code, syntax validity went from 0% to 43.62% with the knowledge source unchanged. The authors conclude that "part of cross-agent degradation may arise from representation compatibility rather than purely from missing knowledge" ([Grynets et al., 2026](https://arxiv.org/abs/2608.21208v1)). They separate what a spec contains from how an agent operationalizes it, and state that the two "are not identical".

No source explains why one agent reads a particular layout badly. Each condition bundles a model with a harness and a framework, so the effect cannot be pinned on the model.

## How to check a swap

Keep the last good run of the outgoing agent as the baseline. Re-run the same specification through the incoming agent and compare against whatever oracle the project already has: the test suite, the build, a diff against a reference implementation. Where there is no oracle, that gap is the real problem and portability testing will not fill it.

Two adjustments are worth trying. Ask the target agent to rewrite the spec into its own form, and keep it only if it measures better: that rewrite rescued Gemini and dropped Copilot from 43.4% to 14.09% syntax validity. Then try giving the agent retrieval access to a structured spec instead of pasting the whole document. Retrieval "did not outperform all alternative ingestion approaches across every metric", and its case is narrower. It was "the only common strategy represented on the per-agent Pareto frontiers for both Gemini and Copilot, indicating the most consistent cross-agent trade-off among the evaluated strategies" ([Grynets et al., 2026](https://arxiv.org/abs/2608.21208v1)).

## When this backfires

- One agent writes and reads the spec. Nothing transfers, so there is nothing to measure.
- A real oracle already exists. A passing suite answers what those similarity metrics only approximate. The study says as much about its own runnability figure: it "should be interpreted as a lower bound, because testing was performed against an empty live database with generated stubs rather than the exact production schema" ([Grynets et al., 2026](https://arxiv.org/abs/2608.21208v1)).
- The spec is cheap to regenerate. Gemini's was 193 lines. Below some size, regenerating it inside the target agent beats measuring whether the old one ports.
- One run per configuration. Setting temperature to 0 "does not guarantee determinism in code generation" ([Ouyang et al., 2024](https://arxiv.org/abs/2308.02828v2)), and the study's own repeat run moved Token F1 by a factor of 19 on a single cell.
- The artifact is an ordinary prompt. Prompts transfer between models well enough that a research line exists to stop it: copying one to a different underlying LLM "preserves strong performance" without countermeasures ([Li et al., 2026](https://arxiv.org/abs/2605.05974v2)). Spec Kit "works with coding agents like GitHub Copilot, Claude Code, and Gemini CLI" from one specification ([GitHub, 2025](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)).

Read the absolute numbers first. The best configuration produced immediately runnable output 28.75% of the time, and the cross-agent table sat under 2.4% throughout ([Grynets et al., 2026](https://arxiv.org/abs/2608.21208v1)). This is a swap-time check, not a way to make migration work.

## Key Takeaways

- Measure the swap on the oracle you already have; a foreign spec helped two of three agents tested and destroyed the third.
- A longer, more complete spec is not a safer one to hand over; pick what to re-verify from the agent pair, never from artifact size.
- Try the rewrite before retrieval, and measure both. The rewrite rescued one agent and cut the other's syntax validity by two thirds, so neither is a safe default.
- The absolute quality ceiling was low throughout, so treat portability as a change-detection check rather than a quality technique.

## Related

- [The Specification as Prompt](specification-as-prompt.md) — using existing formal artifacts as the instruction itself
- [Prompt-Rewrite Discipline on Cross-Generation Model Migration](prompt-rewrite-on-cross-generation-migration.md) — the same rebuild-and-retune move applied to a model hop rather than an agent hop
- [Probe-and-Refine Tuning of Repository Guidance for Coding Agents](probe-and-refine-guidance-tuning.md) — evidence that a guidance artifact tuned for one model does not transfer
- [Spec-Driven Development](../workflows/spec-driven-development.md) — the workflow that produces the artifact under test here
- [Documentation-Guided Legacy Migration](../workflows/documentation-guided-legacy-migration.md) — the migration setting these measurements come from
