---
title: "Loop Trigger Selection: Pairing the Start with the Stop"
term: "Loop Trigger Selection"
description: "Pick an agent loop's trigger and its stopping rule as one decision: goal-bounded, scheduled, and event-driven each commit you to a different terminal state."
tags:
  - loop-engineering
  - tool-agnostic
aliases:
  - loop trigger choice
  - agent loop trigger types
  - choosing a loop trigger
last_reviewed: 2026-08-15
maturity: emerging
---

# Loop Trigger Selection: Pairing the Start with the Stop

> An agent loop's trigger decides what can stop it, so pick the start condition and the stopping rule as one decision.

Loop trigger selection is the choice of what begins each iteration of an agent loop, made together with the rule that ends it. A loop specification names both, alongside the goal, the verification step, and the memory that survives between turns ([arXiv 2607.00038v1](https://arxiv.org/abs/2607.00038v1)). Picking them separately is how a loop ends up with a start it cannot stop.

## Conditions for this choice to be live

This decision sits downstream of [the go/no-go gate](agent-loop-go-no-go-gate.md), and automating the start is worth it only under two conditions.

Manual triggering is still the majority practice. In a hand-coded corpus of fifty public loops, "the trigger is manual in seventy-eight percent of loops, with only twelve percent scheduled and ten percent event-driven" ([arXiv 2607.00038v1](https://arxiv.org/abs/2607.00038v1)). Pressing enter yourself is the corpus default, not a fallback.

One turn's result also has to change the next action. The same paper sets the bar plainly: "A loop specification is justified over a bare scheduled prompt only when the result of one turn changes the next action." Independent firings are a cron job, and the notification you already get is cheaper.

## The three shapes

Claude Code's documentation organizes the choice by asking what should start the next turn, and pairs each answer with its stop ([Claude Code: Keep Claude working toward a goal](https://code.claude.com/docs/en/goal)). That comparison supplies the first two rows below. The third is the remaining trigger type in the loop specification taxonomy, which classes triggers as manual, scheduled, or event-driven ([arXiv 2607.00038v1](https://arxiv.org/abs/2607.00038v1)).

| Shape | Next turn starts when | Stops when | Fits |
|---|---|---|---|
| Goal-bounded | the previous turn finishes | an evaluator confirms the condition holds, or judges it impossible | work with a finish line the run can surface |
| Scheduled | a time interval elapses | you stop it, or the agent decides the work is done | a world that keeps producing new work |
| Event-driven | an external signal arrives | the reaction to that signal completes | state changes you would otherwise poll for |

A scheduled loop carries no completion condition of its own, so each firing has to name its own terminal state. A well-formed specification distinguishes "success, a clean no-op, blocked, stalled, exhausted", and "an error or an exhausted budget never counts as success" ([arXiv 2607.00038v1](https://arxiv.org/abs/2607.00038v1)).

The shapes also compose, which is the common production form. Addy Osmani schedules the detection and bounds the repair: "you use loop to schedule a check, and then goal to solve the problem" ([Practical Loop Engineering](https://addyo.substack.com/p/practical-loop-engineering)). The schedule answers "is there work?" and the goal answers "is this piece of work done?", so neither shape carries a job it has no stopping rule for.

## Why it works

The trigger fixes what information exists when the loop has to decide it is finished. A goal-bounded run starts from a human-supplied completion condition, so the stopping rule has something a person asked for to check against. Claude Code sends that condition plus the conversation to a separate small model each turn, so "completion is decided by a fresh model rather than the one doing the work" ([Claude Code: Keep Claude working toward a goal](https://code.claude.com/docs/en/goal)). A clock supplies no such condition. That is why the same comparison lists a scheduled loop's stop as the operator switching it off, and why its stopping rule has to drive to a named terminal state instead ([arXiv 2607.00038v1](https://arxiv.org/abs/2607.00038v1)).

The pairing buys termination, not quality. The evaluator "does not call tools, so it can only judge what Claude has already surfaced in the conversation" ([Claude Code: Keep Claude working toward a goal](https://code.claude.com/docs/en/goal)). Osmani states the consequence directly: it "doesn't look at the content to see if it's good or bad in any way, shape, or form. All it does is examine the conversation transcript to see if the hard rules you specified have been met" ([Practical Loop Engineering](https://addyo.substack.com/p/practical-loop-engineering)).

## When this backfires

1. Nothing changes between firings. A scheduled trigger over work where one turn does not inform the next is polling waste ([arXiv 2607.00038v1](https://arxiv.org/abs/2607.00038v1)).
2. The agent can edit the oracle. A subset of the environments used to train Claude Sonnet 3.7 were "all vulnerable to at least one of the following systemic reward hacks: (1) the AlwaysEqual hack, (2) the sys.exit(0) hack, (3) the conftest.py hack", each of which makes the tests report success without the task being solved ([arXiv 2511.18397v1](https://arxiv.org/abs/2511.18397v1)). The [goal contract](../patterns/agent-design/goal-contract-completion-evaluator.md) page covers the gaming surface in full.
3. The end state is invisible to the run. A condition about a deployed service or a rendered page has no working pairing, because the evaluator sees only what the transcript reports ([Claude Code: Keep Claude working toward a goal](https://code.claude.com/docs/en/goal)).
4. The bar is taste. Osmani's example of a goal that cannot work: "keep going until this UI design is good. What does that mean? Good to who? How is it being evaluated?" ([Practical Loop Engineering](https://addyo.substack.com/p/practical-loop-engineering)).
5. A session-scoped scheduler is used for unattended work. Claude Code's `/loop` fires only "while Claude Code is running and idle", offers "no catch-up for missed fires", and expires recurring tasks 7 days after creation ([Claude Code: Run prompts on a schedule](https://code.claude.com/docs/en/scheduled-tasks)). Overnight automation on it produces silent non-execution.
6. Reviewer attention is already saturated. Stopping rules are per loop; the person reading the diffs is not. Osmani runs "anywhere between five and ten agents" a day, caps concurrency "at about five", and watches closely anything that "happens to touch authentication, or something related to security or finance" ([Practical Loop Engineering](https://addyo.substack.com/p/practical-loop-engineering)).

The loop specification paper names the compound failure cognitive surrender: "the temptation to stop having an opinion once the loop seems to cope; designing the loop is the cure when done with judgment and the accelerant when done to avoid thinking" ([arXiv 2607.00038v1](https://arxiv.org/abs/2607.00038v1)).

## Example

Osmani's composed form, in full ([Practical Loop Engineering](https://addyo.substack.com/p/practical-loop-engineering)):

```text
/loop every 24h "Check GitHub for issues labeled 'bug'. If one exists, use /goal
to implement a fix until all local tests pass and push the branch."
```

The scheduled half has a terminal state per firing: a clean no-op when no bug issue exists. The goal-bounded half has a transcript-visible condition, because the agent runs the tests and the result lands where an evaluator can read it. A standalone goal carries the same discipline, naming the measuring tool alongside the threshold:

```text
/goal Refactor the data-fetching layer in Dashboard.tsx until Lighthouse
performance score is >= 92 and LCP is under 1.8s as shown by the Lighthouse CLI
output. Do not change the public API of any hooks. Each turn must improve at
least one reported metric; abort if two consecutive turns show no improvement.
Stop after 10 turns.
```

## Key Takeaways

- Choose the trigger and the stopping rule together. A clock supplies no completion condition, so a scheduled loop has to define a terminal state for each firing.
- Manual triggering is the corpus majority at 78%, so treat automating the start as a claim that needs the "one turn changes the next action" test.
- A goal-bounded loop's stop is a rule check over what the run surfaced. Keep a separate quality gate for the artifact, and keep it outside the loop.
- Compose rather than stretch one shape: schedule the detector, bound the fix.
- Session-scoped schedulers expire and skip missed fires, so durable automation needs a scheduler that survives without an open session.

## Related

- [Agent Loop Go/No-Go: When Looping Earns Its Cost](agent-loop-go-no-go-gate.md) — the upstream four-condition gate that decides whether to build a loop at all
- [Loop Budgeting: Allocating Iteration and Token Budget Across Turns](loop-budgeting.md) — once the trigger is chosen, the cap and the per-turn allocation
- [Goal Contract: Separating the Doer from the Done-Checker](../patterns/agent-design/goal-contract-completion-evaluator.md) — the goal-bounded shape in detail, including evaluator bias and gaming
- [Human-in-the-Loop Checkpoints as Loop Control](human-in-the-loop-checkpoints.md) — the deliberate suspend that puts human judgment back inside a running loop
- [Session Scheduling with Loop and Cron in Claude Code](../tools/claude/session-scheduling.md) — the scheduled shape as one tool implements it, with its expiry and jitter semantics
- [Developer as CPU Scheduler: Attention Management with Parallel Agents](../human/attention-management-parallel-agents.md) — why adding triggers past your review capacity converts loop throughput into unread diffs
