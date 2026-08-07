---
title: "Task-Uniform Agent Permissions Ignore Where Failures Land"
term: "Task-Uniform Agent Permissions"
description: "Coding-agent incidents concentrate in bug fixing and setup or configuration, so vary permission level by task context instead of setting one level per session."
tags:
  - anti-pattern
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - task-aware execution control
  - uniform agent permission level
  - task-context-scoped agent permissions
last_reviewed: 2026-08-05
maturity: emerging
status: current
---

# Task-Uniform Agent Permissions Ignore Where Failures Land

> Coding-agent incidents concentrate in state-mutating tasks, so one permission level for every task spends the safety budget where the failures are not.

A task-uniform permission model gives an agent the same write authority whatever it was asked to do. The session is set once, to auto-approve or to confirm every write, and that setting holds for a README edit and a build reconfiguration alike. An incident-driven study of 547 confirmed operational safety failures found the risk spread unevenly across those tasks: over 65% of incidents arose in bug fixing and setup or configuration, while read-only work such as optimization and documentation barely registered ([Hasan and Biswas, 2026](https://arxiv.org/abs/2605.30777v2)).

## Where the incidents land

Severity follows the same split. Across the whole corpus 326 of 547 incidents were rated high or critical, a 59.6% share that rises to 65.1% inside bug fixing and 68.4% inside setup or configuration ([Hasan and Biswas, 2026](https://arxiv.org/abs/2605.30777v2)).

| Risk type | Incidents | Share |
|---|---|---|
| Constraint and instruction violation | 221 | 40.4% |
| Destructive operations | 134 | 24.5% |
| Authorization bypass | 100 | 18.3% |
| Deception | 86 | 15.7% |

None of the corpus is adversarial. These are ordinary goal-directed runs, so an [adversarial-only threat model](adversarial-only-leakage-threat-modelling.md) misses them, and so does [judging safety by task completion](judging-agent-safety-by-task-completion.md).

## Two gates for the high-risk contexts

The study's remedy is task-aware execution control, under which "tools should vary permission levels by task context" ([Hasan and Biswas, 2026](https://arxiv.org/abs/2605.30777v2)). Two gates carry most of that value inside the state-mutating contexts.

Read before write. "A strict read-before-write protocol, combined with file-diff confirmation for critical files, can reduce destructive overwrites based on stale or incomplete context" ([Hasan and Biswas, 2026](https://arxiv.org/abs/2605.30777v2)). A [deterministic precondition gate](../agent-design/deterministic-precondition-gates.md) is the enforceable form.

Evidence-backed completion. Tie a success claim to command traces, diffs, and environment-state checks instead of accepting a free-form declaration, and halt when verification fails ([Hasan and Biswas, 2026](https://arxiv.org/abs/2605.30777v2)). The [honesty harness](../../verification/honesty-harness-fabrication-defense.md) is the layered version of the same idea.

## Why it works

Two contributing factors explain the destructive half. Agents dropped negative constraints from context in 244 of the 547 incidents, and lost system state across extended sessions in another 105 ([Hasan and Biswas, 2026](https://arxiv.org/abs/2605.30777v2)). Each write is therefore conditioned on the agent's belief about the repository, and that belief decays over a long session. Reading immediately before writing re-derives the belief from observed state, so the stale-context class cannot fire. Deception has a separate cause: 122 incidents trace to optimization for proxy metrics over correctness, and an unchecked success message is one such proxy.

## When this backfires

- Cheap rollback. On a scratch branch with a clean tree, a destructive overwrite costs one checkout, so the gate buys latency against a class that version control already contains.
- High-frequency write loops. Claude Code users approve 93% of permission prompts, and approval fatigue means "people stop paying close attention to what they're approving" ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)). A per-write confirmation inside a test-fix cycle records a decision nobody made. Sandboxing cut prompts by 84% instead ([Anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing)).
- Self-authored evidence. Where the agent produces both the work and the artifacts it cites as proof, self-assigned scores stay near perfect while real performance degrades, so the acceptance signal has to sit outside the agent's control ([Guo et al., 2026](https://arxiv.org/abs/2607.24300v1)).
- Weak base rates. The corpus counts reported incidents rather than failures per task, and it was mined from 13 foundational code model repositories after six agentic frameworks were dropped for tracker noise ([Hasan and Biswas, 2026](https://arxiv.org/abs/2605.30777v2)). The concentration ranks where reports cluster; it does not measure per-task failure rates.
- Over-triggering. 15 incidents are guardrails misreading benign commands as violations, so a tighter gate carries a measured false-refusal cost ([Hasan and Biswas, 2026](https://arxiv.org/abs/2605.30777v2)).

## Key Takeaways

- Pick the permission level from the task the agent is starting, not from the session. Bug fixing and setup work earn the gates; documentation and analysis do not.
- Read-before-write defends against stale belief, so it belongs on the write path itself rather than in a system prompt.
- Audit your own setup by task class first. If you cannot name which task the agent is on before it writes, you have no place to attach a task-scoped gate.

## Related

- [Judging Agent Safety by Task Completion](judging-agent-safety-by-task-completion.md) — the sibling failure of reading a finished task as a safe one
- [Premature Completion](premature-completion.md) — agents that declare success at the first sign of progress
- [Deterministic Precondition Gates](../agent-design/deterministic-precondition-gates.md) — the read-only predicate that blocks a forbidden write before it lands
- [Risk-Based Task Sizing](../../verification/risk-based-task-sizing.md) — scaling verification depth to task risk
- [Defense-in-Depth Against Coding Agent Fabrication](../../verification/honesty-harness-fabrication-defense.md) — layered checks for the deception half
