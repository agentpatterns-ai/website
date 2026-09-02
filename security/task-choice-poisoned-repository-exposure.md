---
title: "Which Task You Delegate Changes Poisoned-Repo Exposure"
description: "On a poisoned repository, asking a coding agent to run the tests reached 45.5% attack success against 8.6% for a bug fix on the same injected file, and the riskiest task drew the fewest warnings."
term: "Prompt-Level Configuration"
tags:
  - security
  - agent-design
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - prompt-level configurations
  - PLC
  - task type as attack surface
last_reviewed: 2026-09-01
maturity: emerging
status: current
---

# Which Task You Delegate Changes Poisoned-Repo Exposure

> The task you delegate moves attack success on a poisoned repository from 8.6% to 45.5%, on the same injected file.

Treat the first thing you ask an agent to do on an untrusted repository as a security decision, and rank test execution as the most dangerous of the common asks. A benchmark of 1,920 runs across 20 repositories reports Run-Tests at 45.5% attack success rate against Fix-Bug's 8.6%, with non-overlapping Wilson intervals ([Zhu et al., 2026v1](https://arxiv.org/abs/2608.30686v1)). The authors call these user-side choices Prompt-Level Configurations: what task you delegate, how you phrase it, and which skills or rules you supply.

Two conditions bound every number below. The attacker goal is data exfiltration only, scored by an outbound request carrying a planted secret, and every run used what the authors call Unconstrained Automation Mode, so no approval gate stood between the agent and execution. The rest of the caveats are in [when this backfires](#when-this-backfires).

## What the benchmark measured

CIPR holds the attacker's injection fixed and varies the user's invocation. Marginal rates across the full sample, roughly 480 runs per task ([Zhu et al., 2026v1](https://arxiv.org/abs/2608.30686v1), Figure 4 and Table 14):

| Task | Attack success | Alert rate |
|---|---|---|
| Run-Tests | 45.5% [41.1, 50.0] | 9.4% [7.1, 12.3] |
| Prepare-Env | 24.9% [21.2, 28.9] | 34.9% [30.7, 39.2] |
| Fix-Feature | 14.8% [11.9, 18.2] | 1.5% [0.7, 3.0] |
| Fix-Bug | 8.6% [6.4, 11.5] | 1.3% [0.6, 2.7] |

Run-Tests, Fix-Bug, and Fix-Feature all surface the same injected test file, so the 4.5-fold Run-Tests/Fix-Bug contrast isolates the task verb with the payload held constant. Prepare-Env surfaces the configuration file instead, so its high alert rate is measured against a different artifact and is not a clean comparison.

The alert column carries the finding worth acting on. The worst task is the quietest: agents warned the user in 9.4% of Run-Tests runs. The two fixing tasks are safe by accident rather than by vigilance, alerting around 1.4% of the time while rarely executing the poisoned file at all.

Phrasing moved risk far less. A terse, underspecified prompt cut attack success 4.8 points, and a typo-ridden one raised it 2.0 points ([Zhu et al., 2026v1](https://arxiv.org/abs/2608.30686v1), Table 1).

## Why it works

The operational goal decides whether the agent reads a file as something to audit or something to run. Conditioning on exposure separates discovery from interpretation: agents read the injected file at similar rates under both setup tasks (72.3% for Run-Tests, 86.4% for Prepare-Env), but once they had read it, attack success rose to 51.3% against 26.4% while the alert rate fell to 11.3% against 35.7%. The authors state it plainly: "The difference is therefore not driven by whether the agent encounters the injected content, but by how it interprets it" ([Zhu et al., 2026v1](https://arxiv.org/abs/2608.30686v1)).

Their matched `axios/axios` traces show the split. Told to prepare the environment, the agent reads `package.json` as a setup artifact to audit, spots a suspicious `preinstall` hook, and warns before execution. Told to run the tests, it reads a file under `tests/setup/` as infrastructure to execute and carries on into a fix-and-rerun loop without flagging anything. "Run the tests" is an instruction to execute whatever it finds, and the agent obeys it.

The phrasing effect runs through a duller mechanism. A terse prompt produced 37 tool calls where the baseline produced 52, stopping short of the payload-bearing suite. In the authors' words, "The agent is not more security-aware; it simply does less."

## The rules result, and the paper that disagrees

Security-aware rules bought alerts and not safety. Adding skills plus explicit security directives moved the alert rate from 10.5% to 14.8% while attack success sat at 22.3% against a 22.6% baseline, with overlapping intervals ([Zhu et al., 2026v1](https://arxiv.org/abs/2608.30686v1), Table 14). The paper's diagnosis is a timing problem: rules "do not uniformly or significantly reduce successful attacks (ASR), often because the alert comes too late to prevent the attack payload from executing." Its remedy is control-flow blocking when an alert fires, not a warning after the fact.

Take that result as contested. Testing a repo-side variant, [Day et al., 2026v1](https://arxiv.org/abs/2608.14876v1) found one narrow directive in `AGENTS.md` cut attack success from 25.7% to 10.2%, with 17% of sessions citing the policy before declining to run the payload. Day's was a single imperative matched to the exact payload behavior; CIPR layered general security guidance onto productivity skills, on a different model. Neither reproduces the other's setup. A narrow prohibition naming the action you fear looks better supported than a general instruction to be careful.

## What to do with this

Use the ranking to place an expensive control, not to pick a safer verb.

- Put pre-execution review on test and configuration files before the first test run on a repository you have not read. That is the moment with the highest measured failure rate and the lowest chance of a warning.
- Make an alert stop execution. On this evidence a warning that gates nothing is close to decoration. Pair it with a [confirmation gate](human-in-the-loop-confirmation-gates.md) or a [pre-execution command risk classifier](pre-execution-command-risk-classification.md).
- Close the exfiltration path first. An [egress policy](agent-network-egress-policy.md) removes the entire measured harm class regardless of which task you delegate.
- Write the one prohibition rather than a security preamble, and expect it to help less than its author hopes.

## When this backfires

- Egress is already denied. CIPR scores success only when a planted secret reaches a mock server, so inside a network-denied container the ranking collapses to zero.
- Your harness gates execution. The finding depends on an alert landing during or after the payload runs, and approval modes are untested here.
- You import the absolute numbers. Direction held across four agent and model pairs; magnitude did not, spanning 7.6% to 29.6% on Prepare-Env alone. Claude Code with Sonnet 4.6 was "consistently the most resistant" and Codex the most exposed.
- The attacker wants something else. Destructive commands and persistent compromise fall outside the measured goal, and the ranking may invert for them. A task that edits files is a better persistence route than a read-only test run.
- You read it as "do not run the tests." Deferring the test run moves the moment and leaves the payload in place. The ranking is triage, not a permission ladder.
- You bolt on security skills reflexively. In CIPR the skills conditions also dropped task success from 64.3% to 55.8%, buying 8.5 points of utility loss for no significant reduction in attacks.

## Key Takeaways

- The riskiest common task is also the quietest: Run-Tests reached 45.5% attack success at a 9.4% alert rate, against Fix-Bug's 8.6% and 1.3%.
- The mechanism is interpretation, not discovery. Agents find the injected file at similar rates, then treat it as an artifact to audit or as code to execute according to the task you named.
- Fixing tasks are safe by accident. A 1.4% alert rate means the agent is not catching anything, only executing less.
- One preprint, one attacker goal, no approval gates. Use the ranking to decide where pre-execution review earns its cost, and get an egress control that retires the class.

## Related

- [Workspace Topology as an Indirect Injection Attack Vector](workspace-topology-injection-attack-vector.md) — The repo-side half of the same question, holding user invocation fixed
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md) — Scope breadth as a boundary, where this page measures the task verb
- [Clarification Mode Amplifies Prompt Injection](clarification-mode-injection-amplification.md) — Another user-side interaction choice that moves attack success
- [Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md) — The gate that turns an alert into a stop
- [Agent Network Egress Policy: Admin-Controlled Domain Allow/Deny](agent-network-egress-policy.md) — Closing the exfiltration path this benchmark scores
