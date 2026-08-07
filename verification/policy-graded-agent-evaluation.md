---
title: "Policy-Graded Evaluation of Coding Agents"
term: "Policy-Graded Evaluation"
description: "Score coding agents at each enforced security tier and report success rate and token cost as separate columns, because the model that best preserves success is not the one that best preserves cost."
aliases:
  - policy-graded agent evaluation
  - hardened environment agent benchmarking
  - security policy graded benchmarking
tags:
  - testing-verification
  - evals
  - cost-performance
  - security
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-05
maturity: emerging
---

# Policy-Graded Evaluation of Coding Agents

> Policy-graded evaluation scores an agent at each enforced security tier and reports success and cost separately, because hardening bills the two axes differently.

Run your benchmark once per security tier, up to the policy the agent will actually deploy under, and report success rate and token cost as separate columns. Three conditions decide whether the extra runs pay for themselves. Outside them, the permissive leaderboard has already answered your question.

## When the extra runs are worth it

The policy is enforced by the operating system rather than requested of the agent. A study of 12 model-harness bundles on Terminal-Bench 2.1 graded three nested tiers this way: a permissive control, a non-root tier that drops privilege only, and a NIST-derived high tier restricting network (SC-7), filesystem (AC-3, SC-39), and privilege (AC-6) together. The strict tier routes egress through a default-deny loopback proxy with a 205-domain allow-list, mounts `/usr`, `/bin`, `/etc`, and `/var` read-only, and runs unprivileged with `no_new_privs` set. [Source: [Davidovich and colleagues on policy-graded evaluation of coding agents](https://arxiv.org/abs/2608.02670v1)]

Cost belongs in the decision. Rank order is the part of agent benchmarking that survives environment shift: across eight benchmarks, 33 scaffolds, and 70 or more configurations, absolute score prediction degrades under scaffold and temporal shift while rank-order prediction stays stable. [Source: [Ndzomga on efficient benchmarking of AI agents](https://arxiv.org/abs/2603.23749v1)] A team choosing purely on pass rate can usually skip the re-run. A team that also signs the inference invoice cannot.

Task solvability is audited before any agent runs. The study replayed each task's reference solution under the strict tier. That split the 89 tasks into 50 unaffected, 32 needing a hand-authored policy-compliant solution, and 7 with no admissible solution. Five verifiers also rejected valid solutions, such as one checking only `/usr/local/bin` and missing a workspace build. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)]

## What hardening cost

Under the strictest tier, success fell between 7.1 and 18.3 points across the roster and cost rose between 16.0% and 167.3%. The two extremes belong to different bundles: Claude Sonnet 5 took the 18.3-point success loss, and Grok 4.5 absorbed the 167.3% cost inflation while giving up only 7.1 points. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)]

The frontier also recomposed. Codex bundles traced the Pareto frontier under the control tier; under both hardened tiers Grok 4.5 joined its high-cost end. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)]

## Why it works

A blocked action does not end a run, it restarts one. Across the solvable tasks, success fell from 72.5% to 65.1% while early stops barely moved, from 2.4% to 2.7%; timeouts rose from 12.0% to 16.4% and wrong solutions from 12.8% to 15.5%. The dominant response to a denial was workaround construction, at 97%: the agent abandons the blocked path and rebuilds a tool-chain from source. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)]

The agent does not register the denial as final, so it re-plans instead of reporting the block, and that re-planning is what inflates the bill. Even runs that still passed took 13% more wall-clock time, 14% more tool calls, and 26% more tokens. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)] A permissive sandbox never generates that cost, because nothing there denies the action.

## When this backfires

- Your deployment is not hardened. Agents running as root with open egress on developer machines make a policy-graded suite a measurement of a configuration nobody ships.
- Only the success axis matters. Rank order survives environment shift, so the permissive leaderboard usually reaches the same answer for far less money. [Source: [Ndzomga on efficient benchmarking of AI agents](https://arxiv.org/abs/2603.23749)]
- You skip the solvability audit. A foreclosed task and an over-specified verifier both score as agent failures. An unaudited number therefore measures the policy and the harness instead of the agent. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)]
- The gaps you are reading are small. The study ran three trials per cell at one reasoning-effort setting and calls its own Pareto, sensitivity, and ordering statements descriptive. One bundle also routed through a vendor fallback 29.9% of the time by design. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)]
- The suite is not your workload. Every figure here comes from 89 terminal tasks. [Source: [Merrill and colleagues on Terminal-Bench](https://arxiv.org/abs/2601.11868v1)] A team whose agents edit a large application repository has to rebuild the audit and pay the inference bill again before it transfers.
- You want a security verdict. The tiers are not a certified deployment configuration, and the measurement is performance cost rather than security effectiveness. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)]

## Example

Boundary-Bench is the released form of this method: an MIT-licensed hardening plugin that layers configurable OS-enforced policy onto Terminal-Bench tasks and packages the results as Inspect AI evaluation logs. [Source: [boundary-bench repository](https://github.com/boundary-bench/boundary-bench)]

Its cheapest step runs before any agent does. Replay each task's reference solution under the target policy and record whether it passes unchanged. That compatibility flag anticipates where the policy will cost both money and success. [Source: [arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)]

## Key Takeaways

- Report two columns, success rate and token cost, at every tier. A single number hides the trade the model actually made.
- Run the reference-solution compatibility probe first. It costs no agent inference and tells you which tasks the policy forecloses.
- Repair over-specified verifiers additively before comparing, or a policy-compliant solution scores as a model failure.
- Skip the exercise when the deployment is permissive or when only rank order on success feeds the decision.
- Budget for longer trajectories even where success holds, since passing hardened runs still consumed 26% more tokens.

## Related

- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — sizing a custom suite to the decision it informs, the prerequisite for grading one by policy
- [Benchmark-Driven Tool Selection for Code Generation](benchmark-driven-tool-selection.md) — the same leaderboard-transfer problem measured along task realism rather than policy
- [Eval Environment Containment for Cyber-Capable Agents](eval-environment-containment.md) — restrictions applied to protect the world outside the eval, rather than to reproduce the deployment
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — other measurement gaps a stronger model cannot close
- [Enterprise Agent Hardening: Three Production Gates](../security/enterprise-agent-hardening.md) — the controls a policy-graded run is measuring the price of
- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](../security/agent-network-egress-policy.md) — the allow-list mechanism the strict tier enforces
