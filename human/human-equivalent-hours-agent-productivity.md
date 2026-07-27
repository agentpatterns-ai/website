---
title: "Human-Equivalent Hours for Autonomous Coding Agent Productivity"
description: "Estimate autonomous coding agent productivity in human-equivalent engineering hours so spend can be weighed against delivered value in the same denominator finance and headcount already use."
aliases:
  - "human-equivalent hours metric"
  - "agent productivity in engineering hours"
tags:
  - human-factors
  - cost-performance
  - tool-agnostic
last_reviewed: 2026-06-30
maturity: adopted
status: current
---

# Human-Equivalent Hours for Autonomous Coding Agent Productivity

> Estimate the human engineering hours an autonomous agent's output would have taken — credible only on PR-gated sessions with a paired downstream signal.

## When the metric is credible

Human-equivalent hours estimates counterfactual human time, not measured output. It is credible under specific conditions and misleading outside them. Apply it only when:

- Sessions terminate in a merged PR or pass an independent quality classifier. Cognition's calibration includes a PR-merged session only if any of its PRs merge; non-PR sessions go through a classifier that drops 1–20% as unproductive ([Cognition, 2026-06-04](https://cognition.ai/blog/ai-productivity)).
- The aggregate covers enough sessions to escape the noise floor. Their held-out r_log = 0.74 places ~50% of estimates within a factor of 2; below ~20 sessions, month-over-month deltas sit inside that band ([Cognition, 2026-06-04](https://cognition.ai/blog/ai-productivity)).
- A second, observed signal trends alongside it: PR review time, defect rate, or merge-to-revert ratio. Without one, the metric is unanchored — see [when this backfires](#when-this-backfires).

Outside these conditions, prefer cost per merged PR alongside review-time-to-merge — both are observed, not estimated.

## The definition

Cognition asks "how long would a human engineer have taken to produce the same output?" Hours already denominate salaries and contractor rates, so the result is directly comparable to existing finance and headcount instruments ([Cognition, 2026-06-04](https://cognition.ai/blog/ai-productivity)).

The estimator rests on four design principles:

1. Reason about the human's path, not the agent's — discount retries, setup, and non-core artifacts a human would not produce.
2. Credit only unspecified work — measure the agent's contribution against the user's initial problem statement, [not the full diff](../code-review/agent-pr-volume-vs-value.md).
3. Account for codebase familiarity — infer a human's exploration time in an unfamiliar codebase.
4. Assume relevant expertise — the reference engineer already has the skills; do not credit skill-substitution.

The uncalibrated model is corrected via log-space linear regression:

```text
h = 2.28 × m^0.923
```

where `m` is the uncalibrated estimate and `h` the corrected human-hours figure (a simplified 2.08× constant performs comparably). Calibration: 258 sessions, 126 users; held-out r_log = 0.74 on 233 sessions; F(1,231) = 279.9, p < 10⁻⁵ ([Cognition, 2026-06-04](https://cognition.ai/blog/ai-productivity)).

## Why code volume is not the metric

Regressing lines changed against human-time estimates produces R²_log = 0.27 — code volume captures roughly a quarter of the variance in productive output ([Cognition, 2026-06-04](https://cognition.ai/blog/ai-productivity)). That is the empirical case against task-completion-rate and PR-count metrics: they correlate weakly with the value the team pays for. Under [bottleneck migration](bottleneck-migration.md) the cheap part — generation — is exactly what those metrics count.

## Why it works

Engineering value is already denominated in human time — salaries, contractor rates, and estimates all use hours. Converting agent output back into hours makes ROI directly comparable to the instruments finance and headcount planning already run ([Cognition, 2026-06-04](https://cognition.ai/blog/ai-productivity)). The mechanism is denominator alignment, not ground-truth measurement: it speaks the language of the decisions it informs (renew the seat, raise the cap, hire instead).

Google frames the same measurement challenge for Jules, its agentic coding tool: as agents shift from reactive assistants to proactive contributors, tracking their impact requires rethinking the unit of value — a second vendor perspective that the denominator-alignment approach scales across tool boundaries ([Google Developers Blog — Measuring what matters with Jules](https://developers.googleblog.com/en/measuring-what-matters-with-jules/)).

The denominator is urgent now. Agentic workloads carry 58.9% of token volume on Vercel's AI Gateway, up from 31.6% six months earlier — tool-using requests are ~2.6× more token-heavy than the rest ([Vercel AI Gateway production index, 2026-05-12](https://vercel.com/blog/ai-gateway-production-index)). Uber capped employees at $1,500/month per agentic coding tool after burning the annual AI budget in four months ([TechCrunch, 2026-06-02](https://techcrunch.com/2026/06/02/uber-caps-employee-ai-spending-after-blowing-through-budget-in-four-months/)). Token spend has a denominator; agent output, until now, did not.

## When this backfires

The metric estimates counterfactual human time. Every failure mode below traces back to that one property.

- High-context maintenance on familiar codebases. A randomized controlled trial of experienced open-source developers measured a 19% slowdown with AI tools while developers still reported a 20% speedup — a 39-point perception gap ([METR, 2025-07-10](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)). Cognition's model is calibrated against user reports and its corrected estimates still sit 1.4× below those reports ([Cognition, 2026-06-04](https://cognition.ai/blog/ai-productivity)) — consistent with self-report inflation, not independent of it. Pair with an observed downstream signal; the [productivity-experience paradox](productivity-experience-paradox.md) is the warning that perception and reality diverge here.
- Downstream cost can absorb the gain. AI-assisted teams complete 21% more tasks and merge 98% more PRs while PR review time rises 91% — the [bottleneck migrates](bottleneck-migration.md) ([Osmani, 2025](https://addyo.substack.com/p/the-reality-of-ai-assisted-software)). An hours-saved figure that ignores review time spent is half a ledger.
- Task selection bias inflates apparent value. Agents get the tasks they are best at; the reference human is then estimated for tasks pre-selected to favor the agent. Compare baselines on stratified task mixes, not aggregate counts.
- Small-team noise floor. At r_log = 0.74, ~50% of per-session estimates fall within a factor of 2. A 10-session month sits inside that band; reading a 30% month-over-month change as signal is reading noise.
- Greenfield work has no stable reference. "How long would a human have taken?" assumes a stable counterfactual. For novel problems with no comparable human baseline, the denominator is fabricated and the hours figure is no more grounded than an opinion.

## Example

A platform team runs Devin and Claude Code across two months, defending (or canceling) a $1,500/seat agentic-coding budget.

Before — counting completions:

```text
Month 1: 47 PRs merged, 12,400 lines changed, $9,200 spend
Month 2: 51 PRs merged, 11,800 lines changed, $11,400 spend
```

Lines changed and PR counts both rise; spend rises faster; the conversation stalls on whether 47 PRs are "worth" $9,200.

After — denominating in human-equivalent hours, with downstream signals:

```text
Month 1: 47 PRs merged → 184 estimated human-hours
         PR review time: 38h spent; defect-rate flat
         Implied rate: $9,200 / 184h = $50/h
Month 2: 51 PRs merged → 201 estimated human-hours
         PR review time: 61h spent; defect-rate flat
         Implied rate: $11,400 / 201h = $57/h
```

The estimate is calibrated on PR-merged sessions only (Cognition's gate). The implied $/h is now directly comparable to the team's loaded hourly rate. The 61h of review time is the observed signal that anchors the estimate — if review time were rising faster than agent hours, the gain is being absorbed downstream and the metric must say so.

## Key Takeaways

- The metric: *how long would a human engineer have taken to produce the same output* — chosen because engineering value is already denominated in hours ([Cognition, 2026-06-04](https://cognition.ai/blog/ai-productivity)).
- Cognition's calibration: `h = 2.28 × m^0.923` (or a simplified 2.08× constant) fit on 258 sessions across 126 users; r_log = 0.74 on held-out data; ~50% within a factor of 2.
- Code volume is empirically rejected as the metric — lines-changed regression returns R²_log = 0.27 against human estimates.
- Anti-gaming: include sessions only if a PR merges; for non-PR sessions, run an unproductive-session classifier (drops 1–20%).
- The signal inherits self-report inflation. Pair with an observed downstream signal (PR review time, defect rate) — METR's RCT measured a 19% slowdown while developers perceived a 20% speedup ([METR, 2025-07-10](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)).
- Apply only on PR-gated, multi-month aggregates with a paired downstream signal; small samples and greenfield work sit inside the noise floor.

## Related

- [The Productivity-Experience Paradox in AI-Assisted Development](productivity-experience-paradox.md) — perceived productivity can rise while experience declines; the inflation channel that hours-saved estimates inherit
- [The Bottleneck Migration When Humans Supervise Agents](bottleneck-migration.md) — review time absorbs the generation gain; the downstream signal the metric must be paired with
- [Copilot vs Claude Billing Semantics for Enterprise Teams](copilot-vs-claude-billing-semantics.md) — the cost-side denominator the agent-hours figure is being compared against
- [Token-Cost Profiling and Reduction for Always-On Agentic Workflows](../token-engineering/token-cost-profiling-always-on-workflows.md) — the spend-side instrumentation that anchors the ROI ratio
- [Rigor Relocation: Engineering Discipline with AI Agents](rigor-relocation.md) — verification cost shifts that show up only when the metric is paired with downstream signals
