---
title: "Plan as Control Flow: Enforce the Plan in the Harness"
term: "Plan as Control Flow"
description: "A plan in the prompt is context the agent can drift from. For long, structured tasks, a harness executor that dispatches each plan unit enforces it."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - plan enforcement in the harness
  - pattern-specific executor
  - enforced plan execution
last_reviewed: 2026-10-04
maturity: emerging
---

# Plan as Control Flow: Enforce the Plan in the Harness

> For long, structured tasks, have the harness dispatch each plan unit instead of leaving the plan in the prompt.

## When this applies

The study suggests plan as control flow pays off for long plans, and for tasks where you can pick the plan shape ahead of time. Those two conditions come from the paper's results. The third, that a bad plan costs less than a drifting one, is this page's heuristic. Outside those conditions, a plan in context is often enough, or enforcement makes things worse. The evidence is one study on three models, so test the conditions on your own agent.

## The pattern

A plan in the prompt is one more piece of context. At each step a ReAct loop picks the next action from the latest observation, and nothing in the control flow compares that action with the plan. A pattern-specific executor moves the plan into the dispatch loop, so the harness decides which plan unit runs next. The authors of the main study describe this as a pattern-specific executor making "that structure part of the execution control flow" ([Oota et al., 2026](https://arxiv.org/abs/2609.38108v1)).

The study compares three conditions:

- Flat ReAct: no plan.
- Plan+ReAct: a planner writes a plan and passes it to a generic ReAct executor. In the authors' words, "the declared plan is not structurally enforced during execution."
- Pattern-specific executors: a deterministic executor for one plan shape, such as sequential, hierarchical, or search, runs the plan.

In a coding assistant, a todo list or plan-mode output sitting in context matches Plan+ReAct. A harness that hands one sub-agent each plan unit, in order, matches the pattern-specific condition. The study does not test Claude Code, Copilot, or Cursor, so that mapping is this page's reading and not a measured result.

## What the evidence shows

Plans in context lose structure on long tasks. Across ALFWorld, Mind2Web, and SWE-bench, "only about 22 – 45% of Plan+ReAct trajectories preserve the declared structure." WebArena is the exception: its plans average 3.3 to 3.8 steps and keep 65.6 to 69.1% of structure ([Oota et al., 2026](https://arxiv.org/abs/2609.38108v1)). On ALFWorld, fidelity falls from 36.5 to 49.6% for 4 to 5 step plans to 4.8 to 21.4% for 6 to 7 steps. Hierarchical plans are hard to preserve, with maintenance "typically below 25%." Search shows a similar pattern.

Read these figures as a direction, not a defect rate. The verifier counts a plan as kept only if every plan unit matches an executed action in declared order. Two human annotators agreed on that judgment at Cohen's kappa 0.35, and the authors note that "deciding whether a free-form ReAct trajectory preserves a declared plan can itself be ambiguous for human annotators." The finding that fidelity falls with plan length is stronger than any single percentage. For background on the measurement gap, see [plan compliance in agents](plan-compliance-in-agents.md).

Enforcement raised task success on ALFWorld and SWE-bench Verified. The abstract reports that "pattern-specific executors raise task success from 0.48 to 0.92 on ALFWorld and from 0.36 to 0.44 on SWE-bench Verified over Plan+ReAct." Those headline numbers are for DeepSeek-V4. Table 5 gives the other two models, comparing Plan+ReAct with the best fixed pattern:

| Benchmark | DeepSeek-V4 | Qwen3.6-35B | Gemma-4-26B |
|---|---|---|---|
| ALFWorld | 0.480 to 0.918 | 0.540 to 0.796 | 0.153 to 0.600 |
| SWE-bench Verified | 0.360 to 0.442 | 0.223 to 0.330 | 0.126 to 0.290 |

The best pattern varied: Search won on ALFWorld for DeepSeek-V4 and Qwen3.6-35B, Gemma-4-26B's best was Hierarchical, and Hierarchical won on SWE-bench for all three. The enforced executors were not scored for fidelity, because they enforce their structure by design, so the 22 to 45% range and a 100% figure are not a measured before and after.

Plan in context adds little over no plan: "generic Plan+ReAct provides limited gains over Flat ReAct, whereas pattern-specific execution yields substantially higher success."

## Who picks the plan shape

Do not let the model pick its own executor. The study measures the gain of the model's declared mode over a task-blind baseline (same mode frequencies, task link shuffled). That gain "lies within the 95% interval of a 5,000-permutation null," so there is "no reliable evidence that current declarations match planning modes to individual tasks better than expected from their overall declaration preferences." Routed execution often trails the best fixed pattern, though Routing@1 still beat Plan+ReAct on ALFWorld and SWE-bench for all three models. On WebArena, Search reaches 0.580 and 0.577 for two models, while Routing@1 reaches 0.460 and 0.404.

Choose the executor per task class instead. In this study SWE-bench favored the Hierarchical pattern for all three models. The paper also reports that after three retries of the strongest fixed pattern, the residual gap to a per-task oracle is only -0.025 to +0.027 on ALFWorld, Mind2Web, and SWE-bench. So picking a task-specific pattern per task adds little over retrying one good fixed pattern.

## Example

This hypothetical example is the page's illustration, not a case from the study. A refactor follows a fixed order: update the interface, migrate callers module by module, then remove the old API. The plan is long and its shape is known ahead of time, so it fits the pattern.

1. A planner writes the plan as a list of units.
2. The harness loop takes the next unit and starts a fresh agent call scoped to that unit.
3. The loop records the result and moves to the following unit, whatever the agent would have chosen next.
4. A final check confirms the removed API has no remaining callers.

## Why it works

A likely cause is where the plan lives. In context, the plan constrains behavior only while the model keeps attending to it, and fidelity falls as plans grow ([Oota et al., 2026](https://arxiv.org/abs/2609.38108v1)). Independent work on 21,120 SWE-agent trajectories found that "periodic plan reminders can mitigate plan violations and improve task success" ([Liu et al., 2026](https://arxiv.org/abs/2604.12147v3)). Reading that as attention to the plan degrading is this page's inference, not a finding of either paper. If it holds, putting the plan in the dispatch loop removes that dependency. The authors state the consequence directly: "A plan provided as prompt context should therefore not be assumed to function as an execution-level commitment."

## When this backfires

- Short tasks. The authors write that a plan in a generic ReAct loop "is often sufficient for short tasks," and that preserving the pattern matters more as horizons grow.
- Exploratory work where the plan is probably wrong, such as debugging an unknown failure. Liu et al. report that "a subpar plan hurts performance even more than no plan at all." A rigid executor removes the agent's chance to route around a bad plan. Anthropic's guidance places agents where "it's difficult or impossible to predict the required number of steps, and where you can't hardcode a fixed path" ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)).
- Web navigation like Mind2Web, where results were mixed. For DeepSeek-V4, Flat ReAct scored 0.058 task success against 0.038 for Plan+ReAct and 0.057 for the best fixed pattern. Qwen3.6-35B went from 0.036 to 0.052 and Gemma-4-26B from 0.043 to 0.147 under the best fixed pattern.
- Tight token or latency budgets. Hierarchical and Search executors generally use more tokens than Plan+ReAct, because they call the model more often.
- Unvalidated transfer. The study ran Qwen3.6-35B-A3B, DeepSeek-V4-Flash, and Gemma-4-26B-A4B-it. No frontier closed model was tested.

If you will not build executors, the cheaper option is to keep the plan in context and re-inject it at phase boundaries, as covered in plan compliance in agents. You can also detect drift instead of preventing it, as in the [judge and advisor split](judge-advisor-split.md).

## Key Takeaways

- A declared plan is not a followed plan: in one study 22 to 45% of Plan+ReAct trajectories kept their structure, measured with low annotator agreement.
- The best fixed executor raised success on ALFWorld and SWE-bench Verified for all three models, and the best pattern varied by benchmark. Model-routed executors recovered only part of that gain (DeepSeek-V4 on ALFWorld: Routing@1 0.721 against 0.918).
- Fix the executor per task class. Model-declared modes did no better than a task-blind baseline.
- Skip enforcement for short tasks and exploratory debugging, and validate before adopting on Mind2Web-style navigation, where results were mixed.
- The results come from three named models, and no frontier closed model was tested. Test on your own agent before you build executors.

## Related

- [Plan Compliance in Agents](plan-compliance-in-agents.md)
- [Splitting the Drift Judge from the Advisor](judge-advisor-split.md)
- [Recurring Control Belongs in Harness Code](recurring-control-in-harness-code.md)
- [Minimum-Sufficient Control Ladder](minimum-sufficient-control-ladder.md)
- [Router-Imposed Quality Ceiling](router-imposed-quality-ceiling.md)
