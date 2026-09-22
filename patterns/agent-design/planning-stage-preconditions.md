---
title: "Planning Stage Preconditions: Budget Headroom and Task Text"
term: "Planning Stage Preconditions"
description: "A planning stage draws from the same token ledger as execution. It earns its place only when the run has headroom above execution's own use and the planner can read the task issue."
aliases:
  - planning stage admission test
  - planning budget displacement
  - when a planning stage earns its tokens
tags:
  - agent-design
  - cost-performance
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-21
maturity: emerging
status: current
---

# Planning Stage Preconditions: Budget Headroom and Task Text

> A planning stage spends the execution budget, so it pays only with ceiling headroom and a planner that sees the task text.

Two conditions decide whether a plan-then-execute contract beats sending the agent straight at the code. The run needs token headroom above what execution alone consumes, and the planning stage needs the task's own issue text. Miss either one and the planner is a tax, because it spends from the ledger execution draws on and the run ends with a plan instead of a patch.

Zhang, Xu and Chen measured both margins on 40 screened SWE-bench Verified tasks, grading every patch through the external Docker harness rather than the agent's own completion claim ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)). Planning and execution share one within-run token ledger there, so a stage that spends is a stage that displaces.

## Precondition one: headroom above what execution alone uses

Measure what direct execution consumes before you set the ceiling. In the matched resource panels, direct execution resolved 143 of 240 assignments (59.6%) at a 12,000-token ceiling and the same 143 at 24,000, using substantially less than either allowance ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)). Doubling a budget that nothing presses against bought that workflow nothing.

The planning workflow was the one under pressure. Its success rose from 87/240 (36.2%) to 123/240 (51.2%) across the same two ceilings, narrowing its deficit against direct execution by 15.0 percentage points (95% task-cluster bootstrap interval 4.2 to 25.8, p=.008) ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)). Read the level as well as the change: planning trailed direct execution at both ceilings, by 23.3 points at 12k and 8.3 points at 24k.

## Precondition two: the task text in the planner's hands

Give the planner the issue, or do not add the planner. Holding the planning tool contract and the ceiling fixed, the same work varied only whether planning could read the task issue; execution received it either way. Issue-hidden planning resolved 70/240 (29.2%), issue-visible planning 109/239 (45.6%), and direct execution 133/240 (55.4%). The information effect is 16.25 to 16.67 points depending on how the single missing endpoint is scored, significant under both completions and after Holm correction ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)).

A planner reconstructing the task from repository inspection alone did worse than no planner at all, costing 26.25 points against direct execution in that panel. Treat planner inputs as a build-time property of the harness, not a prompt you tune later.

## Why it works

Planning tokens are execution tokens the run no longer has. Both stages charge against one within-run logical ledger, so the displacement is structural. The process records show it rather than assume it. At the 12,000-token ceiling, 111 of 240 planning trials (46.2%) hit the budget stop, against 6 of 240 direct-execution trials (2.5%). At 24,000 the planning figure falls to 2 of 240 (0.8%) ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)).

Where the released capacity went settles the causal account. Of the increase in realized use, 89.9% is downstream execution, while mean planning use stays close to flat at 5,565 then 5,714 logical tokens ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)). The higher ceiling did not buy a better plan. It bought execution back the tokens the plan had taken.

The information margin has a separate mechanism. Both planning arms hand the issue to execution, so the treatment changes only which component can act on it. Without it, the planner spends scarce tokens on work that cannot target the actual problem ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)).

## Example

The two conditions collide at their worst point, which is a well-informed planner on a tight budget. In the strict 12,000-token panel, the issue-visible planner reached the execution stage in only 173 of 240 runs, against 216 of 240 for the issue-hidden planner. Of the 67 runs that stopped short, 66 were recorded failures carrying a budget-binding flag ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)).

Better information made the planner spend more, and the spending is what ended those runs. Among runs that did reach execution, the informed arm converted at 109/173 (63.0%) against 70/216 (32.4%) for the hidden arm ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)). The plans were better and the runs still failed, because they failed before any code was written.

## When this backfires

- The ceiling never binds. Direct execution scored identically at both ceilings while using well under each. If your direct runs are not hitting a limit, raising it is not the lever, and a stage competing for the same budget makes things worse.
- The planner cannot see the task. Both panels put issue-hidden planning behind direct execution, so a planning stage that can only inspect the repository is a cost with no matching return.
- You are planning for injection resistance, not throughput. Committing to a program before untrusted content arrives means injected text can move a value inside the graph but cannot synthesize a new action ([arXiv:2605.14290](https://arxiv.org/abs/2605.14290)), and a separate treatment lists cost-efficiency among plan-then-execute's advantages over reactive patterns ([arXiv:2509.08646](https://arxiv.org/abs/2509.08646)). Where control-flow integrity is the goal, do not price the stage on success rate.
- Your workflow interleaves planning with execution. The authors exclude interleaved planning, specialized planner models, and search or repair architectures ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)).
- Your task distribution differs. The pool is 35 Django tasks out of 40, screened to drop every candidate the control policy failed three times out of three, and the authors flag SWE-bench Verified test defects and unverified training-data overlap ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)).

Check the evidence grade before quoting the headline. At the 24,000-token ceiling, task-informed planning reached 198/240 (82.5%) against 127/240 (52.9%) for direct execution, an advantage of 29.6 points (95% interval 20.8 to 38.8). The authors retain that panel as supporting evidence rather than a primary finding, because the strict protocol required valid outcomes on all 1,200 assignments and one run produced none ([arXiv:2609.20449v1](https://arxiv.org/abs/2609.20449v1)). The reversal is the weaker half of the paper. The displacement mechanism is the stronger one.

## Key Takeaways

- Profile direct execution's token use before you add a planning stage. A ceiling nothing presses against is not the constraint, and a planner under it removes budget from the work that produces the patch.
- Wire the task text into the planner at harness level. The measured swing is about 16 points, and the arm without it lost to having no planner.
- Watch stage-reach, not only success rate. A run that never reached execution failed on budget, and counting it as a planning failure points the fix at the wrong stage.
- Keep each number with its campaign. The 82.5% figure belongs to a 24,000-token panel the authors grade as supporting evidence; the primary panels show planning behind direct execution at both ceilings.

## Related

- [Reasoning Budget Allocation: The Reasoning Sandwich](reasoning-budget-allocation.md) — how much reasoning effort each phase gets, a separate dial from how many tokens the phase may spend.
- [Discrete Phase Separation](discrete-phase-separation.md) — running planning and execution in separate conversations, which changes what the shared ledger carries between them.
- [The Plan-First Loop: Always Design Before Writing Code](../../workflows/plan-first-loop.md) — the human-reviewed version of the same contract, bounded by an approval gate rather than a token ceiling.
- [The Research-Plan-Implement Pattern](../../workflows/research-plan-implement.md) — the three-phase structure whose middle phase these preconditions govern.
- [Context Budget Allocation: Spending Every Token Wisely](../../context-engineering/context-budget-allocation.md) — the same displacement logic applied to what gets preloaded into the context window.
