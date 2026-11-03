---
title: "Approve Shell Commands on Observed Effects, Not Predicted"
term: "Consequence-Aware Approval"
description: "Pre-execute a shell command in a snapshotted sandbox and judge its observed effects before committing. Predicted effects cut harm but leave 61.8% of safe twins blocked."
tags:
  - agent-design
  - security
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - pre-execution approval gate
  - observed-effect permission gate
  - effects report approval
last_reviewed: 2026-11-02
maturity: emerging
status: current
---

# Approve Shell Commands on Observed Effects, Not Predicted

> Predicting a command's effects cuts harm as much as observing them and still blocks 61.8% of safe twins; only pre-commit observation fixes both.

Consequence-aware approval executes a proposed shell command inside a snapshotted sandbox before anything reaches the agent. An independent approver then reads a bounded report of the effects that execution produced. An allow keeps the resulting state; a block restores the snapshot and returns a reason the agent can act on. The command runs once either way. In the paper's words: "If the approver allows the command, the snapshot is discarded, the container keeps the post-execution state, and the captured output is returned as the tool result; the command is therefore executed exactly once" ([Wu et al., 2026, arXiv:2610.40753v1 §4.1](https://arxiv.org/abs/2610.40753v1)).

Two rates decide whether the gate is worth running: harm and false blocks. The harm denominator differs by benchmark. On SABER, harm is the fraction of tasks that end in task-specific harm, measured over tasks with a final verdict in every compared system. DeepSeek-V3.2 uses its own judged tasks. On YoloFS-Ext, it is the harmful-outcome rate on the 102 dangerous tasks only. This page labels each harm figure with its benchmark ([arXiv:2610.40753v1 §5.1 and Appendix A](https://arxiv.org/abs/2610.40753v1)).

False blocks are "the fraction of safe twins whose task-completing command is blocked at least once". They exist only on YoloFS-Ext, where each dangerous task has a safe counterpart ([arXiv:2610.40753v1 §5.1](https://arxiv.org/abs/2610.40753v1)).

## Three conditions before the pattern earns its cost

Each of the three is a precondition. The paper measures condition 3 directly. On SABER, the design that breaks it left more harm than running no gate at all.

1. Every effect is reversible inside the sandbox. The authors are blunt about their own rollback: "Effects that leave the container, such as network requests, writes to remote services, or processes the command starts, happen before the approver decides and cannot be undone" ([arXiv:2610.40753v1, Limitations](https://arxiv.org/abs/2610.40753v1)). They buy the guarantee by disabling outbound network in the sandbox, so a gated command reaches a package registry only where the deployment admits the domain.
2. One execution predicts the next. The report describes a single run, which says nothing about a command whose behavior turns on time, randomness, or environment detection.
3. The approver is not the agent, and it decides before the commit. Showing the same effects to the agent that proposed the command scored worse than no gate on SABER (21.2% versus 19.7% harm). On YoloFS-Ext it cut harm from 71.6% to 35.3%, still four times the harm of the full system ([arXiv:2610.40753v1 §5.2, Table 3](https://arxiv.org/abs/2610.40753v1)).

## What the approver reads

A raw trace is unusable as evidence, so the report keeps only boundary-crossing consequences: persistent file transitions with a bounded content diff, network attempts with their destination and actor, user-visible output, and successful reads of credential files. It "targets 4 KiB and is capped at 8 KiB", and execution status plus counts of omitted events survive that budget ([arXiv:2610.40753v1 §4.2](https://arxiv.org/abs/2610.40753v1)).

## Why it works

Approval accuracy is bounded by what the approver can observe, and a shell command's text does not determine its effect. Take a `make clean && make` whose `clean` target "deletes src/ and .git/ in workspace A but only build/ in workspace B": "an approver that sees only the command cannot tell them apart" ([arXiv:2610.40753v1, Figure 1](https://arxiv.org/abs/2610.40753v1)).

Two ablations on YoloFS-Ext separate them. There every dangerous task has a safe twin carrying the same request and command. Feeding a text-only approver more context trades one rate for the other. On YoloFS-Ext, "from the command alone to the full dialogue, harm falls from 44.1% to 17.6% while twin false blocks rise from 52.0% to 61.8%". Predicting effects from the command and its referenced files fixes harm alone. The paper reports: "harm drops as far as with observation, but 61.8% of the twins are still blocked, because a prediction leaves the approver uncertain" ([arXiv:2610.40753v1 §5.3](https://arxiv.org/abs/2610.40753v1)). Those two 61.8% figures are separate measurements that coincide. Only effects observed before the commit move both rates at once: the full system "blocks the harmful command in 84.3% of dangerous tasks while blocking only 1.0% of safe twins".

Condition 3 is measured the same way. YoloFS observes the same file changes but shows them to the agent after the command has run. On YoloFS-Ext that agent reverts in 66 of 102 dangerous runs. Harm falls from 71.6% with no approval to 35.3%, against 7.8% for the full system. On SABER the same design "leaves more harm than no approval at all (21.2% versus 19.7%) because a credential once sent cannot be recalled" ([arXiv:2610.40753v1 §5.2, Table 3](https://arxiv.org/abs/2610.40753v1)).

Anthropic reaches a matching diagnosis about its own deployed classifier. It "finds approval-shaped evidence and stops short of checking whether it's consent for the blast radius of the action". The false-negative rate on real overeager actions is 17% ([Anthropic, How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)).

## When this backfires

- The effects report is a new path for injected text. Anthropic strips tool results from its classifier because "tool outputs are where hostile content enters the context" ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)), and this pattern pipes a filtered version of that material in. The paper tells its approver to treat the packet as evidence rather than instruction. It then concedes an attacker could defeat that "by planting text that the report carries to the approver", and that "neither benchmark contains such an attacker" ([arXiv:2610.40753v1, Limitations](https://arxiv.org/abs/2610.40753v1)).
- An adversary can hide from a sandbox: "In the absence of an 'undetectable', fully transparent analysis sandbox, defense against sandbox evasion is mostly reactive" ([Lindorfer et al., RAID 2011](https://iseclab.org/publications/lindorfer2011detecting_environment-sensitive/)).
- The harm is in a file edit. An edit that plants harmful code "is observed when a later command runs it". An edit that does harm by itself, "such as overwriting a configuration file, is judged only from the call" ([arXiv:2610.40753v1, Limitations](https://arxiv.org/abs/2610.40753v1)).
- The static artifact already answers the question, as in [approval laundering](../../security/approval-laundering-transitive-effects.md). A snapshot buys nothing the file does not say.
- Your environment is not a per-task container. The measured overhead is about "0.5 s per allowed command and 1.5 s per blocked command". That is the cost of the whole sandbox transaction: snapshot, two workspace scans, tracing, and snapshot removal, with a rollback on a block ([arXiv:2610.40753v1 §5.5, Appendix F](https://arxiv.org/abs/2610.40753v1)). The paper runs it in a per-task Docker container. It reports no figure for any other environment. Treat that range as a container number and measure your own before adopting it.

## Example

A user asks for a database migration and the agent proposes `make migrate`. The command is exactly what was requested, Claude Code auto mode allows it, and the `migrate` target also drops three tables. Pre-execution changes what the approver has to go on: "the report shows the database shrinking from 32 KB to 20 KB, providing sufficient evidence to block the command". The block reason then "guides the agent to a safe completion", and the agent "backs up the database and runs only the migration script" ([arXiv:2610.40753v1 §5.4](https://arxiv.org/abs/2610.40753v1)).

## Key Takeaways

- Where all three conditions hold, observed effects move harm and false blocks together; predicted effects fix harm and leave false blocks at 61.8% ([arXiv:2610.40753v1 §5.3](https://arxiv.org/abs/2610.40753v1)).
- Observation after execution gives the acting agent a chance to revert. On SABER that design scored worse than no approval gate (21.2% versus 19.7% harm). On YoloFS-Ext it cut harm from 71.6% to 35.3%, still four times the full system's 7.8% ([arXiv:2610.40753v1 §5.2, Table 3](https://arxiv.org/abs/2610.40753v1)).
- The evidence channel is also an attack surface, and these benchmarks do not test an adversary who uses it. Treat injection-hardening of the report as unfinished.
- The results come from one preprint ([v1, 29 Oct 2026](https://arxiv.org/abs/2610.40753v1)) in which "each system runs each task once", so run-to-run variance in the LLM approver is unreported.

## Related

- [Agent-Native Filesystems: Gating Effects, Not Commands](agent-native-filesystem-mediation.md) — the staging design this pattern is measured against, which shows effects to the agent after the command runs
- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](classifier-gated-auto-permission.md) — the deployed text-based gate, including why it strips tool results
- [Deterministic Precondition Gates for Tool-Using Agents](deterministic-precondition-gates.md) — read-only predicates that check state before a write, with no execution at all
- [Agent Approval Laundering: Effects Beyond the Named Command](../../security/approval-laundering-transitive-effects.md) — the cheaper remedy when the missing information is readable statically
- [Rollback-First Design: Every Agent Action Should Be Reversible](rollback-first-design.md) — the reversibility assumption condition 1 depends on
