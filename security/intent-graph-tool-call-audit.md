---
title: "Intent-Graph Audits for Least-Privilege Agent Tool Calls"
term: "Intent-Graph Tool-Call Audit"
description: "Write a tool plan from the user's objective before any tool output, then check every agent call against it in code. The allowlist does most of the work."
tags:
  - security
  - tool-agnostic
  - arxiv
aliases:
  - intent DAG audit
  - least-privilege tool-call auditing
  - plan-derived tool allowlist
last_reviewed: 2026-11-19
maturity: emerging
---

# Intent-Graph Audits for Least-Privilege Agent Tool Calls

> An intent graph written before any tool output gates each agent tool call. On replayed AgentDojo traces, its allowlist did most of the work.

An intent-graph audit has an LLM write a plan once per task, before the agent reads any tool output. The plan lists the tools, argument values, and order the user's objective needs. Plain code then checks every tool call against that graph and blocks or flags the calls it does not cover. "Because the graph is produced from the trusted objective and the static tool catalog only, an injected instruction cannot enlarge it" ([Shavit, arXiv:2611.11305v1](https://arxiv.org/abs/2611.11305v1)).

The planner sees the objective and the full tool catalog, never session data, and follows three rules ([§4.2](https://arxiv.org/abs/2611.11305v1)):

- List only the tools the objective needs. Every unlisted tool is blocked.
- Constrain an argument only to a value the objective fixes.
- Add an order edge only when one step needs another's result or the objective states the order.

## Conditions on the evidence

- Every security figure is a replay of logged AgentDojo traces from gpt-4o-2024-05-13, an older agent. In a live pilot with a current agent, "the agent followed the injection in 0 of 20 runs", so there was no attack left to stop ([§10](https://arxiv.org/abs/2611.11305v1)).
- Replay withholds a flagged call. It "overstates security, because an agent might route around a block, and understates utility" ([§7](https://arxiv.org/abs/2611.11305v1)).
- The paper does not test attacks adaptive to the audit. Zhan et al. bypassed all eight injection defenses they evaluated with adaptive attacks, at over 50% success on InjecAgent; on AgentDojo the adaptive attacks were less effective ([arXiv:2503.00061v2](https://arxiv.org/abs/2503.00061v2)). See [adaptive evaluation of out-of-band defenses](adaptive-evaluation-out-of-band-defenses.md).

## What each check buys

On 76 held-out tasks, the full audit cut trace-level attack success from 45.7% to 3.3% and flagged 40% of benign tasks ([Shavit, arXiv:2611.11305v1](https://arxiv.org/abs/2611.11305v1)).

| Check | Attack success | Benign tasks blocked |
|---|---|---|
| No defense | 45.7% | n/a |
| Tool allowlist from the plan | 10.2% | 16.2% |
| Allowlist plus argument scopes | 5.5% | 16.2% |
| Full audit with ordering edges | 3.3% | 31.1% |

The allowlist carries the result. Across all attacked runs, 80.6% of 1,776 malicious-call evaluations were blocked as outside the plan or out of order ([§6](https://arxiv.org/abs/2611.11305v1)). Adding ordering edges to scopes lowered attack success by 2.2 points and nearly doubled blocked benign tasks. The paper calls ordering "the weakest component per unit of utility lost". On the development tasks, unmet ordering preconditions caused 26 of 35 flagged benign calls.

The paper's own baseline makes the same point. AgentDojo's LLM tool filter, which picks tools from the task description before the agent runs, reached 6.5% attack success "with benign utility unchanged at 69.7%" ([§7](https://arxiv.org/abs/2611.11305v1)). The author writes "We do not claim that our audit beats the tool filter."

## Two ways to win back benign tasks

Let local reads skip the audit. The author hand-classified 69 tools into 44 local reads, one external read (`get_webpage`), and 24 writes. With local reads bypassed, allowlist plus scopes blocked 8.8% of benign tasks at 4.3% attack success at the harmful step ([§6](https://arxiv.org/abs/2611.11305v1)). Keep any read that can carry data out under audit. In the full design, also bypassing `get_webpage` raised harmful-step attack success by 3.7 points, from 2.0% to 5.8%.

Escalate only flagged calls to a reasoning model. The guardian sees the objective, the plan, prior calls with their arguments, and the flagged call. "It never sees tool outputs, so injected text in documents cannot reach it" ([§4.6](https://arxiv.org/abs/2611.11305v1)). After the read bypass, it overrode 22 to 25% of the remaining flagged benign calls (31.5% in the full design without the bypass) and none of 226 to 242 flagged harmful calls ([§8](https://arxiv.org/abs/2611.11305v1)). A guardian decision took a median of 3.6 s. In the scope-only design with the bypass, flagged benign tasks fell from 27.6% to 21.1%.

The deterministic check costs a median of 5.7 microseconds per call. Writing the plan costs a median of 3.6 s per task ([§6](https://arxiv.org/abs/2611.11305v1)).

## Why it works

The plan is fixed from trusted inputs before untrusted text enters the context, and code that never reads tool output enforces it. An injection can still make the agent ask for a call, but the request cannot change what the plan allows. The read bypass works for a second reason: nearly every labeled attack did its harm at a write or outward step, which stays audited ([§10](https://arxiv.org/abs/2611.11305v1)). AgentDojo reports the same asymmetry for its tool filter, which works where "the user task only requires read-access to a model’s state (e.g., reading emails), while the attacker’s task requires write-access (e.g., sending emails)" ([Debenedetti et al., arXiv:2406.13352v3](https://arxiv.org/abs/2406.13352v3)).

## When this backfires

- The task's tools are enough for the attack. AgentDojo puts this at 17% of its test cases, where its tool filter fails ([arXiv:2406.13352v3](https://arxiv.org/abs/2406.13352v3)). 61% of plan nodes left arguments unconstrained, and 10.6% of malicious-call evaluations were allowed ([Shavit, §6 and §10](https://arxiv.org/abs/2611.11305v1)).
- The tool list cannot be planned up front. AgentDojo names this case for its tool filter ([arXiv:2406.13352v3](https://arxiv.org/abs/2406.13352v3)), and in the replay at least 15% of benign tasks needed a tool the plan omitted ([Shavit, §6](https://arxiv.org/abs/2611.11305v1)).
- A tool classified as a local read can leak data. The bypass then opens a path the audit never sees, and the paper names this limit ([§10](https://arxiv.org/abs/2611.11305v1)).
- The injection changes a result, not a call. AgentDojo's example is a hotel listing that injects the model to always pick it ([arXiv:2406.13352v3](https://arxiv.org/abs/2406.13352v3)).
- Someone else takes over the session. New requests redefine the task, so the audit's score "has nothing to say about who is asking" ([§10](https://arxiv.org/abs/2611.11305v1)).

## Key Takeaways

- Start with a tool allowlist written from the objective before any tool output. In this replay it did most of the work, and AgentDojo's LLM tool filter matched it on security.
- Add argument scopes before ordering edges. Ordering cost the most benign tasks per point of attack success.
- Bypass reads of the user's own state, never reads that can send data out.
- A reasoning model on flagged calls cleared 22 to 25% of the benign ones left after the read bypass. Keep tool outputs out of its context.
- Treat every figure as replay on an older agent with no adaptive attacker.

## Related

- [Plan-Then-Execute as the Default for Web Agents](plan-then-execute-web-agents.md)
- [Task-Based Access Control with Hybrid Inspection](task-based-access-control-hybrid-inspection.md)
- [Intent-Governed Tool Authorization for AI Agents (IGAC)](intent-governed-tool-authorization.md)
- [CaMeL: Defeating Prompt Injections by Separating Control and Data Flow](camel-control-data-flow-injection.md)
- [Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses](adaptive-evaluation-out-of-band-defenses.md)
