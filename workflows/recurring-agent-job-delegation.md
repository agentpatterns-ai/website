---
title: "Recurring Agent Job Delegation: Widen Remit on Evidence"
term: "Recurring Agent Job Delegation"
description: "Hand a recurring agent job to your team in stages: pick work you would delegate, widen its remit only on per-run evidence, and give it a visible owner."
tags:
 - workflows
 - agent-design
 - tool-agnostic
aliases:
 - delegating recurring work to an agent
 - scheduled agent job operating practice
last_reviewed: 2026-10-15
maturity: emerging
---

# Recurring Agent Job Delegation: Widen Remit on Evidence

> A recurring agent job earns a wider remit one rung at a time, and each rung needs a per-run check that a human can read.

A recurring agent job is a task you describe once in plain language and the agent runs on a schedule or on an event. Linear's Loops feature is one example: it lets you "automate recurring work with the Linear Agent by describing a job in plain language" and choose "whether a loop should run on a schedule or in response to an event" ([Linear](https://linear.app/now/five-principles-working-with-loops)). It applies when each run produces output a human can check and when the job's write scope stays narrow.

The evidence base is thin: one vendor engineer's report with no outcome numbers. No source measures whether this practice lowers error rates for recurring jobs, so treat the steps below as an argued operating practice.

## Five checks

The Linear post gives five principles ([Linear](https://linear.app/now/five-principles-working-with-loops)). Each one turns into a question you can answer for your own job.

| Principle | Question to answer |
|-----------|--------------------|
| Hunt for tasks to delegate | Would I hand this to another person on the team? |
| Be incremental | What is the smallest scope and the cheapest failure for the first run? |
| Lean into the available context | What does the job read, and what can it write? |
| Use the agent to help you iterate | Does my rewrite request name the fault? |
| Keep your team in the loop | Can a teammate open this job and see its last run? |

## Pick work you would delegate

The author frames task choice as delegation: "I try to think about automation the way you might think about delegation, and ask what I'd hand off to an extra pair of hands on the team, or a personal executive assistant" ([Linear](https://linear.app/now/five-principles-working-with-loops)). Include teammates' recurring pain.

A quarterly job gives you few runs to check, so by this page's own rule it widens its remit slowly.

## Widen the remit in stages

The source describes one job grown over three steps ([Linear](https://linear.app/now/five-principles-working-with-loops)):

1. "I started by having the loop identify candidate issues, then used the results to refine the criteria for determining which code should be deleted."
2. "I grew more confident in the results and had it send issues to our triage inbox, including a description of why it would pick a specific assignee (without actually assigning them)."
3. "Finally, with enough trust in its choice of work and owner, I let it assign issues directly and delegate them to an agent, leaving the assigned engineer to review and submit the resulting PR."

The author also "limited it to creating five issues at a time rather than tackling the 80-odd cases in the codebase at once." The stated rule is to "start small, both in the scope of the task and in the consequences of getting it wrong."

This page's reading of those steps pairs each remit with the evidence that would justify the next one (the source states no such criteria):

| Rung | Remit | Evidence that justifies the next rung |
|------|-------|----------------------------------------|
| Identify | Lists candidates only | A refined selection criterion you trust |
| Suggest | Sends issues to a triage inbox with a reason for the suggested assignee, with no assignment | A human compares the suggested owner with the right owner and the match holds |
| Assign and delegate | Assigns issues and hands them to an agent | None needed yet. A human still reviews the resulting PR |

Do not advance on elapsed time. Write down the per-run check before you start, and advance only when the check passes. For the general trust dial, metrics, and rollback, see [Progressive Autonomy with Model Evolution](../human/progressive-autonomy-model-evolution.md). For the same staged spine applied to issue classification, see [Continuous Triage](continuous-triage.md).

## Ask the agent to rewrite the job, with the faults named

The author asks the agent to fix an underperforming job. In the worked example the first output "was too verbose, it didn't find the right Slack channel, and it included some extra description about the process it used to evaluate meeting topics." The author then asked the Linear Agent to update the loop and run it again, and "after a couple minutes of back-and-forth, the result was much closer to what I wanted" ([Linear](https://linear.app/now/five-principles-working-with-loops)).

The human supplied three concrete faults in that example. That matters because Huang et al. report that "LLMs struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction" ([Huang et al.](https://arxiv.org/abs/2310.01798v2)). Huang et al. test reasoning tasks, not job rewrites, so this is an inference: a rewrite request that says "figure out why this underdelivers" gives the agent no outside check on its own diagnosis. List the faults, then ask for the change, and read the diff before the next run.

## Share visibility by harness

Linear makes a job visible by default: "A loop sits inside a team, where any member can open it, see what it's done on each run and change it if needed, or at the workspace level, where everyone can see it and admins manage it" ([Linear](https://linear.app/now/five-principles-working-with-loops)).

Claude Code routines work the other way: "Routines belong to your individual claude.ai account. They are not shared with teammates, and their runs count against your account's usage and limits. Anything a routine does through your connected GitHub identity or connectors appears as you" ([Claude Code routines docs](https://code.claude.com/docs/en/routines)).

| Harness | Who can open the job | Whose identity the actions carry |
|---------|----------------------|----------------------------------|
| Linear Loops | Any team member, or everyone at workspace level | Not stated in the Linear post |
| Claude Code routines | Only the owner | The owner |

On a per-user harness you build the team's view yourself. [Unattended Run Reporting](unattended-run-reporting-contract.md) covers what the posted message must say. Name a second person who can find and stop the job, so it does not orphan when the owner leaves.

## Bound context by write scope

The author leans on the harness's context: "each run can work with the current state of your projects, issues, code, documents, and conversations," so you "don't need to overspecify details when describing a task." One bug autofixing loop "references a team skill for investigating bugs, checks for related or duplicate issues, and reads the documents that define product ownership areas" ([Linear](https://linear.app/now/five-principles-working-with-loops)).

The more the job reads, the narrower its write scope must stay. Re-run the ladder from the first rung when you add an input source, because the earlier evidence covered the old inputs only.

## Why it works

Each rung makes the job's output reviewable before it can cause harm. Identify-only output is cheap to check. A triage inbox with a stated reason lets a human compare the suggested owner with the right owner before any assignment happens. A batch cap of five keeps one bad run small. The author states the aim as limiting "the consequences of getting it wrong" while confidence builds ([Linear](https://linear.app/now/five-principles-working-with-loops)).

Anthropic's usage data shows the same move toward more latitude with experience in interactive Claude Code sessions: "Among new users, roughly 20% of sessions use full auto-approve, which increases to over 40% as users gain experience" ([Anthropic](https://www.anthropic.com/research/measuring-agent-autonomy)). Those are interactive sessions, not scheduled jobs.

## When this backfires

The practice fails under these conditions:

- The job reads untrusted input and can write. Simon Willison's lethal trifecta names "Exposure to untrusted content —any mechanism by which text (or images) controlled by a malicious attacker could become available to your LLM" as one leg ([Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)). A job that reads Slack or inbound reports and can assign work or post holds that leg together with write access. At the assign-and-delegate rung, a prompt-injected report can steer real work.
- Reliable runs erode the checks. Parasuraman and Manzey found that "Automation complacency is found in both naive and expert participants and cannot be overcome with simple practice" ([Parasuraman and Manzey](https://trid.trb.org/View/1085175)). The ladder depends on someone inspecting each run. Parasuraman and Manzey tie complacency to competing tasks that pull attention from the automated one, so this page expects inspection to lapse when the owner is busy.
- Long inputs are used unevenly, so a job that reads more is not a job that reads better. Chroma reports that "models do not use their context uniformly; instead, their performance grows increasingly unreliable as input length grows" ([Chroma](https://www.trychroma.com/research/context-rot)).
- The job has no cheap per-run quality signal, such as meeting agendas or summaries. Trust then grows on familiarity, and the ladder advances by calendar.
- The harness is per-user. Teammates cannot open the job, and its actions appear as the owner.
- The owner asks the agent to rewrite the job with no named fault. The rewrite can degrade the job, and the change has no diff review.

The opposing view treats a recurring job as a scripted trigger with a fixed, reviewed spec. You pin the prompt in version control, keep write scopes fixed and narrow, and review each remit change as a code change. That position is defensible, and it is the safer choice when the job reads untrusted input.

## Key Takeaways

- Pick work you would hand to a teammate, and count teammates' recurring pain.
- Name the per-run check for each rung before you start, and advance on the check, not the calendar.
- Name the faults when you ask the agent to rewrite a job.
- On a per-user harness, build team visibility and name a second owner.
- Keep write scope narrow in proportion to what the job reads, and re-run the ladder when inputs change.

## Related

- [Progressive Autonomy with Model Evolution](../human/progressive-autonomy-model-evolution.md)
- [Continuous Triage](continuous-triage.md)
- [Unattended Run Reporting](unattended-run-reporting-contract.md)
- [Cloud Scheduled Routines](../tools/claude/cloud-scheduled-routines.md)
- [Loop Trigger Selection](../loop-engineering/loop-trigger-selection.md)
