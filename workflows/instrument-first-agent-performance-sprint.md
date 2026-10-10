---
title: "Instrument First, Then Let the Agent Hill-Climb"
term: "Instrument-First Performance Sprint"
description: "Anthropic's two-week claude.ai sprint built comparable measurements before asking agents to optimize. Copy the loop only if field data, a gaming-proof evaluator, and review capacity exist."
tags:
  - workflows
  - agent-design
  - tool-agnostic
aliases:
  - measurement-first agent optimization
  - agent-run performance sprint
  - instrument then climb
last_reviewed: 2026-10-09
maturity: emerging
status: current
---

# Instrument First, Then Let the Agent Hill-Climb

> An agent hill-climbed claude.ai performance for two weeks and merged more than 3,000 changes, after the team instrumented first.

An instrument-first performance sprint is a campaign in which an agent first builds comparable measurements of user-facing journeys, then optimizes against them in many narrow threads, with humans approving every change. It applies only when the team has field telemetry, keeps the evaluator out of the agent's write path, and can absorb the review load. Every outcome figure below comes from one vendor account of its own product, produced with an internal research model ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)).

## Conditions where the pattern applies

Check these before you copy the loop. When they fail, a short manual profiling pass is the better choice.

- Field telemetry exists for real users, so you can confirm that a lab win shows up in production.
- The agent cannot edit the benchmark, the correctness check, or the CI gate it is climbing. An agent that reaches the evaluator optimizes the evaluator.
- Each lab proxy has been shown to track user-facing latency for the kind of change in question.
- Changes ship behind flags with a staged rollout.
- Reviewers can read every pull request at the volume the agent produces.

## The measurement problem

The authors state the mechanism in one line: "Once Claude can measure something, it can make it faster." They add that measurement "used to be step zero", where a team adds a metric and waits for data, and that with an agent it became "step one of the climb" ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)). Wall-clock time is the metric users feel, but it is noisy. The Rust compiler team notes that wall time has high variance and that small changes under 1% are hard to detect with it ([Nethercote, 2019](https://internals.rust-lang.org/t/what-is-perf-rust-lang-org-measuring-and-why-is-instructions-u-the-default/9815)). The sprint's layers below exist to give an agent a number it can trust.

## Four layers

### Layer 1: Pick journeys and make them comparable

The team focused on "four journeys that make up 95% of user activity". Those journeys came to thirteen measurements across web and desktop. The team added instrumentation until each measurement "started with a user interaction, ended once the result was rendered, and disambiguated client and server work" ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)).

The sprint began with about twenty hand-picked projects, each aimed at one journey. Claude estimated each project in milliseconds, and the team aggregated the estimates into sprint targets. The team hit twelve of the thirteen targets by day three. That pace fits the authors' note that Claude by default "hedges on feasibility, and pads its estimates". It does not show the estimates were accurate.

### Layer 2: Build deterministic lab benchmarks and prove them

The authors wanted every benchmark to do two jobs. It gives Claude a metric it can move in the lab, and it gives CI a guardrail "with a number that could only ratchet down". They discarded any benchmark that was flaky or did not correlate with user latency, "rather than let Claude climb the wrong hill" ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)).

Claude could work for hours without waiting for field data, and instruction counts were deterministic. Claude still had to prove that the counts tracked wall-clock time. On two hot paths, it cut instructions by 48% and 31%, and wall-clock time fell 78% and 44%. The team then added two ratchets. A pull request that raised those counts failed CI, and a daily job lowered each ceiling when the count dropped. The post publishes this check for those two paths only.

### Layer 3: Ship small flagged pull requests

Each thread followed one loop. Claude traced the flow and found or built a benchmark that showed the problem. It then opened pull requests "sized for risk and review", with anything user-visible behind a flag. If performance improved, Claude ratcheted the benchmark down. If not, "it turned the flag off and iterated" ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)).

When existing metrics miss a problem, the agent builds a new one. The standard layout-shift score read about 0.008 for each shift, "well within the good threshold of 0.1". Claude built a region-tagged layout-shift event and a test that "went red 20 of 20 runs on main, and green 20 of 20 on the PR". Field data then showed "31% of web page loads moved something after the page was usable".

### Layer 4: Keep humans on goals, tradeoffs, and approval

The post splits the work this way: Claude "found bottlenecks, built benchmarks, shipped improvements, and watched every deploy", while the team "steered by setting goals, making tradeoffs, and approving every change". It also says the loop "wasn't autonomous" ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)).

- Every thread had a named human owner. Claude attached before-and-after screenshots or recordings to any user-perceptible change for that owner to rule on.
- Humans vetoed complexity. One 900-line pull request drew a one-line reply that 2 ms per send was not worth maintaining a build plugin.

## What the zero-incident claim rests on

The claim is "more than three thousand changes without a single customer-facing incident or rollback". The post credits these controls, set up before the sprint ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)):

- Automated review on every pull request, with at least one human approval.
- Unit tests written before optimizations.
- A short-lived feature flag on anything that could cause a user-visible problem. The sprint introduced nearly two hundred flags, and more than half were cleaned up by the end.
- Staged rollout for high-risk changes: employees, then one percent of users, then everyone.

Two limits apply. Turning a flag off is part of the loop, and the post does not say whether that counts as a rollback. And the internal release surfaced a layout shift that "none of our metrics could see", four hours after the static composer shipped. Claude traced it to Chrome's prerender behavior on managed browsers, not to the shipped code.

## Reading the headline number

The 3.1x figure is the geometric mean over thirteen before-and-after timings at the 75th percentile of real users, measured on August 13 and August 27. It is not a per-journey result. The spread is wide ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)):

| Measurement | Before | After | Change |
|-------------|--------|-------|--------|
| claude.ai fresh load | 3,085 ms | 550 ms | 5.6x |
| Desktop cold start | 6,310 ms | 3,328 ms | 1.9x |
| Cowork cloud session load | 2,566 ms | 728 ms | 3.5x |
| Cowork send message | 928 ms | 48 ms | 19x |

## Why it works

An agent can iterate overnight against a lab number, but it cannot wait on field data at every step. A deterministic, low-variance measurement turns optimization into a tight local search with a clear accept test. The authors say Claude could work "asynchronously for many hours, even overnight", validating prototypes without waiting for field reads ([Anthropic, 2026](https://claude.dev/blog/how-we-made-claude-ai-faster/)). The variance argument has independent support: the Rust compiler's performance project reports that instruction counts reliably detect changes as small as 0.3% ([Nethercote, 2019](https://internals.rust-lang.org/t/what-is-perf-rust-lang-org-measuring-and-why-is-instructions-u-the-default/9815)). The ratchet then locks each win, so later pull requests cannot undo it.

## When this backfires

- The agent can reach the evaluator. Sakana's CUDA engineer found exploits in the evaluation code that let it bypass accuracy validation, which the company called reward hacking ([TechCrunch, 2025](https://techcrunch.com/2025/02/21/sakana-walks-back-claims-that-its-ai-can-dramatically-speed-up-model-training/)). See [Anti-Reward-Hacking](../verification/anti-reward-hacking.md).
- The proxy diverges from user latency. The same Rust thread notes that changes to IO behavior, threading, or page faults can break the link between CPU time and wall time ([Rust internals](https://internals.rust-lang.org/t/what-is-perf-rust-lang-org-measuring-and-why-is-instructions-u-the-default/9815)). The sprint post validates the link on two paths only.
- Agent-reported evidence is form without substance. A study of agent performance pull requests warns that agents may reproduce the form of validation reports without improving measurement practice, and that CI benchmarking built for human workflows is "unlikely to scale to agent-driven workloads" ([Peng et al.](https://arxiv.org/abs/2610.03969v1)). Re-time claims yourself, as in [Re-Run an Agent's Speed-Up Claim Before Merging](rerun-agent-speedup-claims.md).
- Wall-clock CI gates are noisy. The authors say milliseconds are too flaky to use as a CI gate. See [Audit the Noise Floor Before Trusting a Benchmark Gap](../verification/benchmark-noise-floor-audit.md).
- Review capacity is short. The safety claim rests on a human approving each pull request, and more than two hundred changes landed on the busiest days. A small team either stalls or approves without reading.
- There is no field telemetry or staged rollout. The "watch the deploy, read the field data" step then has nothing to read.
- The standing cost outweighs the gain. Each benchmark is code to maintain, each ratchet can block unrelated pull requests when the proxy drifts, and fewer than half of the nearly two hundred flags were still live when the sprint ended. For many teams, fixing the first few profiler findings by hand may capture most of the user-visible gain, though no source measures that.

## Key Takeaways

- Build comparable measurements of user journeys before asking an agent to optimize, and let the agent build the missing instruments.
- Prove each lab proxy against wall-clock time before it gates CI, and keep the evaluator outside the agent's write path.
- Quote 3.1x only as a geometric mean over thirteen p75 timings, ranging from 1.5x to 19x.
- The zero-incident claim rests on flags, tests first, human approval, and staged rollout, and the post does not say whether flag-offs count as rollbacks.
- All sprint figures are a vendor self-report on an internal model, so try the loop on a small scope first.

## Related

- [Re-Run an Agent's Speed-Up Claim Before Merging](rerun-agent-speedup-claims.md)
- [Require the Metric the Optimization Should Move](../verification/expected-metric-gate-performance-prs.md)
- [Audit the Noise Floor Before Trusting a Benchmark Gap](../verification/benchmark-noise-floor-audit.md)
- [Anti-Reward-Hacking: Rubrics That Resist Gaming](../verification/anti-reward-hacking.md)
- [Harness Hill-Climbing](../patterns/agent-design/harness-hill-climbing.md)
