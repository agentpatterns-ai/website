---
title: "Stop-and-Report Instructions Need a Resuming Loop"
term: "Stop-and-Report Instruction"
description: "A one-line prompt change telling a Codex-based agent to stop when unsure raised mean scores on two game benchmarks at 2-52% more token cost, and left a terminal-coding benchmark mixed."
tags:
  - instructions
  - tool-agnostic
  - arxiv
aliases:
  - return-of-control instruction
  - report-when-unsure instruction
last_reviewed: 2026-10-16
maturity: emerging
---

# Stop-and-Report Instructions Need a Resuming Loop

> What this instruction changes is when the agent returns control, so the measured gain belongs to the agent and its resuming loop together.

Three conditions decide whether this instruction earns its place. Something must re-invoke the agent after it returns. The run must have room for more tokens. And the effect has to be measured on your own tasks, because the study that measured it found a gain on two benchmarks and none on a third.

The change is a single line in the text a harness sends at the start of a run and again on every continuation. One study ran a Codex-based agent in two variants differing only in that line, deployed unchanged across three benchmarks, on GPT-5.5 at high and xhigh reasoning effort and GPT-5.6-sol at xhigh and max ([Rodionov, 2026](https://arxiv.org/abs/2610.22289v1)). The baseline reads "Continue working until you have completed your task." The replacement reads:

> Continue working on the task as long as you can proceed confidently. If you encounter a problem, ambiguity, unexpected issue, or anything that makes you unsure how to proceed, stop and report it back to me before taking further action.

## Nobody answers the report

The report has no reader. "Here, 'report it back to me' refers to the automated controller, not a human: the controller does not answer the report or supply a task-specific suggestion" ([Rodionov, 2026](https://arxiv.org/abs/2610.22289v1)). A script resumes the same conversation and workspace with a fixed reminder of the goal and a suggestion to reread the environment description. The baseline variant receives that same reminder whenever it returns, so what the instruction changes is when the agent gets there. "The intended difference is therefore when the same task-solving process returns control, not a change in its tools or environment-specific capabilities."

## Where it transferred and where it did not

Every figure below comes from the same study, as means over three evaluation blocks per condition, and the cost ranges are its own approximations ([Rodionov, 2026](https://arxiv.org/abs/2610.22289v1)).

| Benchmark | Comparisons | Change in mean score | Change in mean cost tokens |
|---|---|---|---|
| ARC-AGI-3, 25 games | higher in 4 of 4 | +1.4 to +7.3 percentage points RHAE | +2% to +52% |
| AGI Maze, 106 targets | higher in 8 of 8 | +0.37 to +4.95 percentage points RHAE70 | +7% to +39% |
| Terminal-Bench 2.1, 89 tasks | mixed direction | -1.50 to +2.25 percentage points reward | lower in 1 of 4 configurations, slightly higher in the rest |

AGI Maze is the result that argues for transfer rather than tuning, because "AGI Maze performance was not used to select this instruction" ([Rodionov, 2026](https://arxiv.org/abs/2610.22289v1)). The line was developed on ARC-AGI-3. Terminal-Bench argues against adopting it blind, and the author refuses to read that null as a tie: "The small, mixed differences in mean Terminal-Bench scores do not establish that Stop-and-report is at least as effective as Baseline."

Read every figure above as descriptive. Each condition is a mean over three repetitions, and "Contrasts are descriptive differences between means; their direction alone does not establish statistical significance or non-inferiority."

## Why it works

The study names two candidate causes and separates neither. The first is reconsideration: returning control puts the agent back at a continuation prompt pointing it to the goal and the environment description, which "creates an opportunity for reconsideration rather than enforcing a reflection procedure" ([Rodionov, 2026](https://arxiv.org/abs/2610.22289v1)). The second is inference volume, since writing the report and then resuming may add reasoning at the moments the agent is least sure. Within every ARC-AGI-3 configuration the ordering of mean cost matched the ordering of mean score across the four agents compared, which "makes additional inference a plausible contributor to the gains, but does not establish that greater expenditure causes the improvement."

Both candidates run through the same two steps, the return and the resumption that follows it.

## Moving a decision into the controller

ARC-AGI-3 hands the agent its reset rule: "The environment description already tells the agent to reset after GAME_OVER and avoid unnecessary resets otherwise" ([Rodionov, 2026](https://arxiv.org/abs/2610.22289v1)). A diagnostic variant added only a reset-management intervention on top of Stop-and-report: "Codex is instructed not to call RESET, and the controller issues it at GAME_OVER." That recovered "roughly one-third to three-fifths of the gap between Stop-and-report and twma_v1.61, without closing it", where twma_v1.61 is the ARC-AGI-3-specific agent the general one still trails. The study does not claim the scripted policy is optimal: an agent that spots an unrecoverable attempt early could save the actions spent reaching GAME_OVER.

## When this backfires

- No loop resumes the agent. Every measured run sat behind a controller that resumes the same conversation and workspace when the agent returns early, and a harness that just ends the run turns this line into "stop".
- Your tasks look more like Terminal-Bench 2.1 than like a game. That is the one tested environment family where the effect disappeared, and the study does not say why.
- The run is under a token budget. Cost rose 2-52% on ARC-AGI-3 and 7-39% on AGI Maze, and the comparisons are not at matched inference cost.
- You borrow the number instead of measuring. Three repetitions per condition, four model-effort configurations, one Codex version.
- You assume more relevant context helps for the same reason. Prefixing seven tutorials to each AGI Maze target lowered scores for both GPT-5.5 agents at both effort settings; "the same curriculum can therefore help or hurt depending on the model-effort configuration".
- Your domain is code and the tasks are genuinely underspecified. There the measured intervention is a scaffold rather than a prompt line: a multi-agent system that "decouples underspecification detection from code execution" reached a 69.40% task resolve rate on an underspecified variant of SWE-bench Verified ([Edwards and Schuster, 2026](https://arxiv.org/abs/2603.26233v3)).

## Key Takeaways

- What the line changes is when the agent hands control back. The measured variant hands it to a controller that resumes the same conversation and workspace, so budget for that controller before budgeting for the line.
- In the study measuring it, the line raised mean scores in all 4 ARC-AGI-3 comparisons and all 8 AGI Maze comparisons, and moved a terminal-coding benchmark by -1.50 to +2.25 percentage points with no consistent direction. The author treats that null as unresolved rather than as parity.
- Price it. The game-benchmark gains came with 2-52% and 7-39% more cost tokens, against a baseline not held to matched inference spend.
- The adjacent diagnostic carries the stronger lesson. Moving one decision the agent already knew the rule for out of the prompt and into the script recovered roughly a third to three-fifths of the gap to a specialized agent.

## Related

- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — a measured counterweight, where rules telling an agent to stop contributing scored 0% compliance while this mid-task return of control did move the score
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — the SWE-bench result on which rule types help coding agents, in the same domain where this instruction showed no consistent direction
- [The No-Op Test: Prune Agent Docs by Behavior, Not Length](behavioral-no-op-test.md) — the per-environment measurement this page asks for, as a repeatable procedure
- [Probe-and-Refine Tuning of Repository Guidance for Coding Agents](probe-and-refine-guidance-tuning.md) — how to develop a guidance line against your own tasks rather than importing one
- [Escape Hatches: Unsticking Stuck Agents](../workflows/escape-hatches.md) — the operator-driven version of the same recovery, for when the agent does not return on its own
