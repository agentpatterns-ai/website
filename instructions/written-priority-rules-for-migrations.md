---
title: "Written Priority Rules for Coding-Agent Migrations"
term: "Written Priority Rules"
description: "State when a new convention takes priority over existing code, then check both functional behavior and adoption of the intended implementation."
tags:
  - instructions
  - migration
  - technique
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-31
maturity: emerging
status: current
---

# Written Priority Rules for Coding-Agent Migrations

> Written priority rules tell coding agents when a new convention takes precedence over existing code during a migration.

A written priority rule names the target implementation and states that it overrides conflicting repository precedent. Use it when new code must follow a convention that existing handlers still contradict. Zhu et al. (2026) study this migration condition in [Precedent or Intent?, sections 3.4 and 4.5](https://arxiv.org/abs/2610.38244v1).

## What the experiment measures

The controlled study uses a purpose-built Flask API. Both implementation choices can pass the same functional tests. When every existing endpoint uses the implementation opposite the agents' shared default, agents follow the repository in 359 of 360 runs. This measures implementation choice, not improved code quality ([sections 3.1, 4.2, and 5](https://arxiv.org/abs/2610.38244v1)).

In the guidance experiment, all existing endpoints contradict the target. Sonnet-4-6 and gpt-6-sol attempt ID serialization and response-envelope tasks. Joint success requires passing functional tests and adopting the target ([section 4.5](https://arxiv.org/abs/2610.38244v1)).

| Guidance | Joint successes in the controlled content experiment |
|---|---|
| None | 0/60 |
| Written priority rule | 59/60 |
| Code example alone | 38/60 |
| Rule plus example | 60/60 |

These are separate arms of the same experiment. Adding an example to the rule gives no statistically detectable improvement ([section 4.5, Figure 7](https://arxiv.org/abs/2610.38244v1)).

## Apply the result to a migration

Steps 1 and 2 apply the study's priority-rule design ([sections 3.4 and 4.5](https://arxiv.org/abs/2610.38244v1)). Steps 3 and 4 are this page's advice, not study results:

1. Name the target choice. Specify string IDs or a response envelope; avoid a vague request to modernize the code.
2. State which existing convention the target overrides. Keep the override scoped to the assigned change.
3. Confirm that the agent receives the rule. Put it in the task or an instruction file that the harness loads.
4. Check the target separately from existing functional tests. Inspect the returned representation as well as whether the endpoint works.

For nearby context, inspect handlers for the resource you are extending. Three supporting local files produce 347/360 adoptions; three sibling-resource files produce 13/360 in the controlled study ([section 4.4](https://arxiv.org/abs/2610.38244v1)). Treat a pattern elsewhere in the repository as supporting context. Write down its intended priority before asking the agent to spread it.

## Example

The paper's motivating task adds a task-detail endpoint beside handlers that return numeric IDs. Its instruction explicitly overrides that precedent ([section 2](https://arxiv.org/abs/2610.38244v1)):

> Serialize task identifiers as strings in the new endpoint. This instruction takes precedence over the ID representations used by existing handlers.

Keep that scope when adapting the rule. Review the new endpoint's ID representation, and decide separately whether older endpoints belong in this change.

## Limits and costs

A separate delivery experiment scores 60/60 for task rules and 60/60 for harness-loaded native-file rules. This does not establish channel equivalence or automatic file discovery ([sections 4.5 and 5](https://arxiv.org/abs/2610.38244v1)).

The open-source validation tests response envelopes across four repositories with the same two guidance agents. Native-file rules raise joint success from 0/120 to 117/120. These results do not establish whole-repository migration reliability ([section 4.6, Table 5, and section 5](https://arxiv.org/abs/2610.38244v1)).

Before adding an override, decide whether the code or the instructions describe your target. [Code precedence over stale instruction files](code-precedence-over-instruction-files.md) addresses the stale-file condition. For migrations, record the intended exception and review its scope as the migration progresses.

## Key Takeaways

- State the target and its priority over the old convention.
- Confirm that the harness supplies the rule to the agent.
- Review functional success and target adoption separately.
- Keep the override scoped to the assigned change.

## Related

- [Code Precedence Over Stale Instruction Files](code-precedence-over-instruction-files.md) — resolving conflicts when instructions describe an abandoned convention
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — choosing the form of guidance
- [Pattern Replication Risk](../patterns/anti-patterns/pattern-replication-risk.md) — reviewing conventions before asking agents to copy them
