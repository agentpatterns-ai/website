---
title: "Head-to-Head Evaluation of Competing MCP Servers"
term: "Head-to-Head MCP Server Evaluation"
description: "Choose between MCP servers offering the same capability by scoring them under one fixed agent configuration, and decide on consistency and cost, because quality usually ties."
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
aliases:
  - MCP server selection eval
  - comparing MCP servers head to head
last_reviewed: 2026-08-05
maturity: adopted
---

# Head-to-Head Evaluation of Competing MCP Servers

> Score competing MCP servers under one fixed agent configuration, then decide on consistency and cost, because a small eval rarely separates them on quality.

Run this comparison under four conditions. Without them it burns hundreds of agent runs and returns a tie you could have assumed.

- You run the workflow often enough that a per-run cost or duration gap compounds.
- You can afford repeat trials on each task, because consistency is usually where servers separate.
- You have a scorer you can calibrate against a known-good answer.
- Where your source of truth already lives has not settled the choice for you.

## Hold everything except the server fixed

A score measures the [whole configuration](purpose-built-eval-suites.md), so the server is only legible once every other part is pinned. Braintrust spawned a fresh headless Claude Code subprocess per eval row. One model, one prompt, one tool allowlist, and `--strict-mcp-config` to guarantee the agent saw only its assigned server ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)). MCPBench applies the same control, comparing servers "using the same LLM and prompt in a controlled environment" ([Luo and others, 2025](https://arxiv.org/abs/2504.11094v2)).

Pin the task to the server as well. Braintrust's prompt required building the design in the MCP tool before deriving any HTML, because early smoke tests showed agents skip design tools entirely when given the choice ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)). A candidate that routes around the server under test scores the model, not the server.

## Calibrate the scorer before ranking anything

Feed the scorer a known-perfect answer first and record what it returns. Braintrust scored the benchmark's own ground-truth HTML against its own screenshot. It got 1.0 on every metric except CLIP visual similarity, which capped at 0.93, because re-rendering produces slightly different pixels ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)). Without that step, a server at 0.85 reads as a failure rather than near-ceiling.

## Buy repeat trials, then read the distribution

Repeat trials turn run-to-run consistency from noise into an axis. Braintrust ran each of its 27 complex designs three times per server, which is what made a variance ratio reportable at all ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)). Read the per-design spread as well as the mean. Two outright collapses drove most of the aggregate gap in that eval, while margins elsewhere were small and ran in both directions.

Report cost per unit of quality, not raw cost, so a server that is cheap per run but needs more attempts is not flattered.

## Why it works

A server's internal representation predicts its failure mode, which is why the secondary axes carry more signal than the mean. Paper's canvas is HTML and CSS, the medium the agent ships, so it reads back the actual CSS values on each element. Figma stores designs in its own format, so the agent works through a translation layer. A Figma composition also has a fixed frame size, and nothing forces it to fill a browser viewport once it becomes HTML. That gap produced the eval's largest failure. The agent built one illustration correctly, then rendered it as a small badge in empty space, and its own self-checks missed that, because they screenshot the Figma canvas where the composition looks right ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)). A representational mismatch produces rare, total failures rather than a uniform penalty, so it surfaces as variance and outliers while averaging out of the mean.

## When this backfires

- The decision is cheap to reverse. Server selection is per-run configuration, so when swapping costs one line and the workflow runs a few times a week, the eval costs more than the mistake.
- The comparison is underpowered for the gap you care about. Braintrust's 27 designs at three trials each could not resolve a 0.038 quality difference (p = 0.21). Central-limit error bars understate uncertainty below a few hundred datapoints anyway ([Bowyer, Aitchison and Ivanova, 2025](https://arxiv.org/abs/2503.01747v3)). Treat a small comparison as a screen that rejects a broken candidate, never as a ranking.
- You are scoring a configuration artifact. MCPBench found server accuracy "can be substantially enhanced by involving declarative interface" ([Luo and others, 2025](https://arxiv.org/abs/2504.11094v2)), so a gap may be a wrapper you could fix on the losing server in an afternoon.
- The capability you want is not reachable by an agent yet. Braintrust could not exercise Figma's shader beta, because shader IDs are scoped to a file a fresh agent session cannot reach ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)).
- Your scorer cannot see the property that matters. Across 248 generated files, Figma emitted semantic HTML tags at over three times Paper's rate, a maintainability difference no pixel-similarity metric registers ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)).

## Example

Braintrust compared the Paper and Figma MCP servers as design tools for a coding agent, on 40 pages sampled from the [Design2Code](https://huggingface.co/datasets/SALT-NLP/Design2Code-hf) benchmark and 27 hand-picked design-heavy pages at three trials each ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)).

| Axis | Paper | Figma |
|---|---|---|
| Visual similarity, simple pages | 0.741 | 0.744 |
| Visual similarity, complex designs | 0.716 ±0.027 | 0.679 ±0.043 |
| Duration per run | 400s | 568s |
| Cost per run | $2.02 | $2.53 |
| Cost per quality point | $2.82 | $3.73 |

The quality axis the eval was built around returned nothing. Its paired gap on the complex set was 0.038 at p = 0.21, which the author reports as statistically indistinguishable. Separation came from elsewhere: Figma's run-to-run variance was about 1.9 times Paper's, and it ran 42% longer and cost 32% more per point of visual quality ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)).

A second measured behavior returned nothing either. Both agents spontaneously screenshotted their own canvas to self-correct, but across 160 runs the correlation between self-check count and final quality was r = +0.01 for Paper and r = −0.19 for Figma ([Braintrust, 2026](https://www.braintrust.dev/blog/paper-vs-figma-mcp)).

## Key Takeaways

- Decide what would change your mind before you run anything, because the quality axis usually ties and an unplanned tie becomes a vote.
- Budget the comparison against the cost of being wrong: server choice is per-run configuration, so a reversible decision rarely justifies hundreds of agent runs.
- Spend your run budget on repeat trials rather than more tasks, since consistency is the axis that separates and it needs repetition to exist.
- Locate the metric's ceiling before ranking against it, and treat any score you cannot reproduce on a known-good answer as uncalibrated.
- Write up a tie as a result, so the next team reaches for the cost and consistency numbers instead of re-running the same comparison.

## Related

- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — the general form of this decision, and how to size a suite to it
- [Benchmark-Driven Tool Selection for Code Generation](benchmark-driven-tool-selection.md) — choosing a public benchmark when the unit under test is the model
- [Decomposing Agent Output Variability by Layer (Sampling vs Orchestration State)](sampling-state-agent-variability-layers.md) — which layer the run-to-run variance you measured comes from
- [Comparative Judging for Agent Configuration Ranking](comparative-judging-config-ranking.md) — ranking configurations once the scores are too noisy to separate
- [MCP Server Design](../tool-engineering/mcp-server-design.md) — the interface choices that a head-to-head comparison ends up scoring
