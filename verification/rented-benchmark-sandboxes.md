---
title: "Rented Sandboxes for Coding-Agent Benchmark Runs"
term: "Rented Benchmark Sandbox"
description: "Renting a fresh sandbox per benchmark trial converts a serial local run into a concurrency quota with a published price, and leaves machine resources and container runtime enforcement as the one variable no submission rule pins."
aliases:
  - rented eval sandbox
  - hosted benchmark sandbox
  - per-trial cloud sandbox
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
last_reviewed: 2026-09-19
maturity: emerging
---

# Rented Sandboxes for Coding-Agent Benchmark Runs

> Renting one sandbox per benchmark trial buys concurrency at a published price and leaves the machine itself unpinned.

Rent per-trial sandboxes when serial wall-clock is what blocks the decision, and only after you have pinned what the provider does not. Terminal-Bench 2.0 holds 89 tasks. Its authors ran each supported model and agent combination "at least five times, resulting in a total of 32,155 trials", on Daytona, at "between 32 and 100 containers in parallel"; most trials finish inside 20 minutes and some run for two hours ([Merrill and others, 2026](https://arxiv.org/abs/2601.11868v1)). No single machine absorbs that shape overnight.

## Conditions that make renting worth it

- You are waiting on the sum of trial durations, not on any one trial.
- Your harness already separates the task from the machine. Harbor runs `harbor run --dataset terminal-bench@2.0` on local Docker, and its README gives the cloud form: "To run it on a cloud provider (like Daytona) pass the `--env` flag" ([Harbor, 2026](https://github.com/laude-institute/harbor)).
- Your model provider's rate limit sits above the concurrency you want. Vercel's guidance is to "raise `--n-concurrent` toward your model provider's rate limits" ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/harbor)).

## Why it works

Trials are independent by construction, so a local run serializes only because one machine holds few of them at once. The resource that binds is the one you can least predict. Across 144 SWE-rebench tasks, "memory, not CPU, is the concurrency bottleneck", spikes reach "up to 15.4x peak-to-average ratio", and "resource demands are highly unpredictable across tasks, runs, and models" ([Zheng and others, 2026](https://arxiv.org/abs/2602.09345v3)). Renting swaps that physical bound for a purchased one: a Vercel Pro plan allows 10,000 concurrent sandboxes against Hobby's 10 ([Vercel, 2026](https://vercel.com/docs/sandbox/pricing)). The same work puts OS-level execution, meaning tool calls plus container and agent startup, at "55-60% of end-to-end task latency" ([Zheng and others, 2026](https://arxiv.org/abs/2602.09345v3)), so per-trial startup is a real share of the bill.

## What the provider pins, and what it does not

Terminal-Bench's leaderboard names everything that has to hold constant, and a provider is not on the list. A submission must run "the exact dataset version pinned in `core/hub.py`", with "`timeout_multiplier` unset/`None` or `1.0`, no agent or verifier timeout overrides, no resource overrides", covering every task with at least five trials ([Terminal-Bench 2.1, 2026](https://github.com/harbor-framework/terminal-bench-2-1/blob/main/leaderboard/SUBMIT.md)). The submission command names the sandbox with its own `-e <sandbox>` flag ([Terminal-Bench 2.1, 2026](https://github.com/harbor-framework/terminal-bench-2-1)), and no rule constrains it.

A hosted backend honors the task's declared shape instead of imposing its own. On Vercel, "a task's CPU and memory requests from `task.toml` are applied to the sandbox", image builds are keyed by task content so "editing a task rebuilds its image and unchanged tasks reuse theirs", and network policy is "enforced outside the VM" ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/harbor)). What survives that is named in the benchmark's own limitations. Tasks are "designed for reproducibility by pinning package versions, providing prebuilt Docker images, and requiring dependencies to be included in the Docker context", yet "variability in machine resources and container runtime enforcement can lead to differences in effective task environments" ([Merrill and others, 2026](https://arxiv.org/abs/2601.11868v1)). So write the provider and plan into the run record beside the dataset version. Microsoft states the general form: "Every eval result should include an environment manifest: OS, tool versions, model version, harness version, and LSP configuration" ([Microsoft, 2026](https://developer.microsoft.com/blog/the-hidden-variables-in-your-agent-eval/)).

## When this backfires

- The suite finishes overnight on hardware you own. A run that size is nowhere near 32,155 trials, and the account setup outlasts the wait you shortened.
- The plan's session cap is shorter than the task timeout. Hobby caps a session at 45 minutes ([Vercel, 2026](https://vercel.com/docs/sandbox/pricing)) and trials reach two hours ([Merrill and others, 2026](https://arxiv.org/abs/2601.11868v1)). The hardest attempts get cut off and scored, not errored.
- The rate limit binds before the quota does. Surplus sandboxes then sit idle accruing provisioned memory at $0.0212 per GB-hour while requests queue ([Vercel, 2026](https://vercel.com/docs/sandbox/pricing)).
- You compare across dataset versions. Terminal-Bench 2.1 modified 26 tasks "to fix bugs, modify timeouts or resources, or improve robustness to reward hacking" ([Terminal-Bench 2.1, 2026](https://github.com/harbor-framework/terminal-bench-2-1)), which breaks comparability before any provider difference does.
- The tasks need a GPU, or several containers behind a hostname allowlist. Vercel supports neither ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/harbor)).
- You expect renting to remove a confound. A developer machine "typically has a fully configured language server", and Microsoft notes an eval rig in a container or CI environment might not ([Microsoft, 2026](https://developer.microsoft.com/blog/the-hidden-variables-in-your-agent-eval/)). That gap belongs to the container, rented or not.

## Example

The same Harbor command runs locally or on rented microVMs, and the flag that changes is the environment ([Vercel, 2026](https://vercel.com/changelog/run-terminal-bench-and-other-harbor-evals-on-vercel-sandbox)):

```bash
harbor run -d terminal-bench/terminal-bench-2-1 \
  --agent fx \
  --model vercel_ai_gateway/anthropic/claude-fable-5 \
  --env vercel \
  --n-concurrent 8
```

A concurrency of 8 "fits every plan's concurrency limit, including Hobby's 10 concurrent sandboxes", and Hobby also needs `sandbox_lifetime_seconds` lowered from Harbor's 24-hour default ([Vercel, 2026](https://vercel.com/docs/sandbox/ecosystem/harbor)). Price the sandbox cost against the model cost before raising that number. Vercel bills Active CPU at $0.128 per hour and provisioned memory at $0.0212 per GB-hour, and publishes a 30-minute, 4-vCPU, 8 GB run at about $0.34 assuming full CPU use ([Vercel, 2026](https://vercel.com/docs/sandbox/pricing)). A whole Terminal-Bench 2.0 run "costs anywhere from one to a hundred dollars, depending on the model's price" ([Merrill and others, 2026](https://arxiv.org/abs/2601.11868v1)).

## Key Takeaways

- Renting buys concurrency. It does not buy comparability: every rule that makes two runs mean the same thing pins the dataset version, the timeouts, and the resource requests, and none of them pins the provider.
- A run record that omits the provider, the plan, and the concurrency it ran at cannot be reproduced, however precisely it pins the dataset.
- Read the plan's session cap and concurrency quota as benchmark parameters. A 45-minute cap against a two-hour trial changes the score without failing the run.
- Find the real ceiling before raising concurrency: the model provider's rate limit usually arrives before the sandbox quota does.

## Related

- [Per-Attempt Sandboxes for Agents That Change the Filesystem](per-attempt-eval-sandboxes.md) — why each trial needs its own container at all, and where the verifier has to sit.
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — sizing the suite to the decision, which comes before sizing the infrastructure.
- [Eval Environment Containment for Cyber-Capable Agents](eval-environment-containment.md) — the network policy the sandbox firewall enforces, and how to verify it from inside.
- [Renting a Cloud Agent's Execution Sandbox](../patterns/agent-design/rented-execution-sandbox.md) — the same rent-or-own choice for production agent runs rather than eval trials.
- [Seed Variance Reporting](seed-variance-reporting.md) — what the repeated trials buy you once you can afford to run them.
