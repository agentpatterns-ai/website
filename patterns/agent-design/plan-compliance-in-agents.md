---
title: "Plan Compliance in Agents: Measure What They Execute, Not What You Wrote"
term: "Plan Compliance in Agents"
description: "Agents silently deviate from instructed plans; plan quality, phase alignment, and periodic reminders determine whether the plan you wrote actually runs."
tags:
  - agent-design
  - instructions
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-12
maturity: emerging
---

# Plan Compliance in Agents: Measure What They Execute, Not What You Wrote

> Agents do not reliably execute the phases you instruct. Plan quality, phase alignment, and periodic reminders determine whether the written plan actually runs.

## The silent gap

Writing a plan into a system prompt does not mean the agent follows it. A 16,991-trajectory study of SWE-agent gave the first systematic measurement of plan compliance in programming agents ([Liu et al., 2026](https://arxiv.org/abs/2604.12147)). It ran four LLMs on SWE-bench Verified and SWE-bench Pro under eight plan variations. The core finding: "without an explicit plan, agents fall back on workflows internalized during training, which are often incomplete, overfit, or inconsistently applied."

Until you measure compliance, a pass rate blends two different sources of success. One is strategic reasoning that the instructed plan drives. The other is memorized pattern-matching against benchmark-adjacent training data. Resolution rate alone cannot tell them apart ([Liu et al., 2026](https://arxiv.org/abs/2604.12147)).

## Four empirical effects

```mermaid
graph TD
    A[No plan] -->|worse| B[Standard plan]
    B -->|better| C[Standard plan + reminders]
    A -->|worse than no plan| D[Subpar plan]
    B -->|sometimes worse| E[Plan + misaligned early phases]
```

Each effect comes directly from [Liu et al., 2026](https://arxiv.org/abs/2604.12147):

1. Standard plans beat no plans. A phase sequence such as navigation → reproduction → patch → validation resolves more issues than unprompted execution.
2. Periodic reminders reduce violations. [Re-injecting the plan during execution](../../instructions/event-driven-system-reminders.md) reduces drift and improves task success.
3. Subpar plans underperform no plan. A low-quality plan actively hurts — worse than leaving the agent to its training priors.
4. Misaligned extra phases degrade performance. Early-stage phases that conflict with the model's internal problem-solving strategy can lower resolution rates.

Effects 3 and 4 overturn the assumption that more plan, earlier plan, is always better.

## Why compliance fails without reminders

Adjacent work documents how compliance decays. Agents drift from the goal as context grows, and pattern-matching gets more likely with it. All tested models drift to some degree. The best case held near-perfect adherence only up to about 100,000 tokens under specific conditions ([Arike et al., 2025](https://arxiv.org/abs/2505.02709v1)). Instruction fade-out is a separate, documented failure mode that event-driven system reminders are built to counter ([Bui, 2026](https://arxiv.org/abs/2603.05344)).

Re-injecting the plan as the context lengthens pushes it back into the high-attention recency zone. This is the same structural defense that [goal recitation](../../context-engineering/goal-recitation.md) uses for objectives and [critical instruction repetition](../../instructions/critical-instruction-repetition.md) uses for hard constraints.

## Applying this in practice

Treat the plan as an engineered artifact, and ask four operational questions:

- Does the plan match the model's strategy? If early phases contradict how the model naturally approaches the problem class, performance drops below no-plan baselines. Pilot the plan against the unprompted trajectory before you lock it in.
- Is the plan high quality? A bad plan is worse than no plan. [Iterate on phase boundaries and success criteria](../../workflows/plan-first-loop.md) rather than shipping a first draft.
- Are there reminders? Without mid-run reinjection, plan adherence decays in long sessions. Inject reminders at phase boundaries or on token thresholds.
- Is compliance measured? Pass rate hides non-compliance. Compare executed trajectories against the instructed phases — [deviation rate is the signal](../../instructions/task-list-divergence-diagnostic.md).

Measurement turns the plan from a hope into a testable contract. Without it, every benchmark number risks being a pattern-match from training rather than a product of the plan you wrote.

## Example

Two agents handle the same SWE-bench issue. Both produce a passing patch.

Agent A runs with no plan. It greps for the error string, opens the matched file, edits the apparent cause, runs the failing test, and patches until green. It skips the reproduction and validation phases entirely.

Agent B runs with an instructed plan (navigation → reproduction → patch → validation) and a reminder at each phase boundary. It locates the module, writes a minimal reproducer, confirms the failure, patches, runs the full test subset, and verifies no regression.

Looking at [resolution rate](goal-monitoring-progress-tracking.md) alone, both succeed. Looking at the trajectory-to-plan diff, only Agent B followed the instructed strategy. If the benchmark is near the training distribution, Agent A's success may generalize poorly. Agent B's success traces to the plan and is likelier to hold on unseen issues. This is the distinction [Liu et al., 2026](https://arxiv.org/abs/2604.12147) identify as invisible without compliance analysis.

## Key Takeaways

- Writing a plan does not mean the agent executes it — measure compliance, not just pass rate.
- Standard plans outperform no plans; subpar plans underperform no plans.
- Extra early-stage phases [degrade performance](../anti-patterns/objective-drift.md) when they misalign with the model's internal strategy.
- Periodic plan reminders during execution reduce violations and improve task success.
- Pass rate without compliance analysis cannot distinguish strategic reasoning from training-data pattern matching.

## Related

- [The Plan-First Loop: Design Before Code](../../workflows/plan-first-loop.md) — upstream: building the plan with the agent before execution
- [Goal Recitation: Countering Drift in Long Sessions](../../context-engineering/goal-recitation.md) — agent-initiated objective reinjection, complementary to plan reminders
- [Critical Instruction Repetition](../../instructions/critical-instruction-repetition.md) — author-placed repetition for hard constraints
- [Event-Driven System Reminders](../../instructions/event-driven-system-reminders.md) — harness mechanism for injecting reminders on detected conditions
- [The Instruction Compliance Ceiling](../../instructions/instruction-compliance-ceiling.md) — compliance decay driven by rule count
- [Task List Divergence as Instruction Quality Diagnostic](../../instructions/task-list-divergence-diagnostic.md) — divergence in generated plans as an instruction-quality signal
- [Goal Monitoring and Progress Tracking](goal-monitoring-progress-tracking.md) — observing whether the agent executed what was planned
- [Splitting the Drift Judge from the Advisor (LivePlan)](judge-advisor-split.md) — acting on a detected compliance violation mid-run rather than measuring it after
- [Objective Drift: When Agents Lose the Thread](../anti-patterns/objective-drift.md) — the failure mode plan reminders mitigate
