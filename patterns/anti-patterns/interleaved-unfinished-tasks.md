---
title: "Interleaving Unfinished Tasks in One Agent Session"
term: "Interleaved Unfinished Tasks"
description: "An agent that sets a multi-stage task aside to advance other unfinished work in the same session resolves it less often, even with the code safe in its own checkout."
tags:
  - context-engineering
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - task-switching resumption gap
  - set-aside task loss
  - interleaved task sessions
last_reviewed: 2026-11-05
maturity: emerging
---

# Interleaving Unfinished Tasks in One Agent Session

> An agent that advances other unfinished tasks in the same session resolves the task it set aside less often, even with that task's code preserved.

Interleaving unfinished tasks means you start a multi-stage task with an agent, switch it to other unfinished work in the same conversation, and come back later to finish the first one. A separate branch or checkout keeps the code safe. It does not keep the requirements, decisions, and pending work, which sit in a conversation now mixed with other tasks.

## Conditions

The evidence comes from one benchmark, Switch-SWE, a version-1 preprint. It applies under these conditions:

- The task you return to has several substantive stages, reconstructed from real issue and review histories, so there is an earlier requirement to forget ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1)).
- The other tasks are also unfinished, come from the same repository, and run in the same continuous agent conversation. Each switched session interleaves the focus task with four of them.
- Every task keeps its own persistent checkout. In the paper's words, this keeps "the comparison focused on session-level task recovery rather than on-disk conflicts."
- The benchmark is Python only: "200 focus tasks from 19 Python repositories", each run once uninterrupted and once switched, with identical requirements and verifiers.

## What the measurements show

The gap appears in every configuration tested. "Across 7 coding agents, interleaved unfinished work produces an average focus-task resolution gap of 11.5 percentage points, ranging from 6.0 to 15.0 percentage points" ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1)). The worst case, DeepSeek-V4.1-Flash on OpenCode, "drops from 46.5% uninterrupted resolution to 31.5% under switching, a relative reduction of 32.3%."

Single-task scores do not predict the result. "Claude Opus 5 with Claude Code achieves the highest uninterrupted resolution at 53.5%, whereas GLM-5.3 with OpenCode leads under switching at 43.0%" ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1)).

Distance matters. Interruptions that touch no shared immediate source directory hurt more: "The average gap is 8.1 % for near interruptions and 14.9 % for far interruptions" ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1)). The authors call this an association, because the near and far groups hold different focus tasks.

Switching also costs tokens. "Full switched sessions consume 4.5-11.1 times as many tokens as uninterrupted sessions" ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1)). That total includes the interruption work itself. The resumed focus stages alone used 1.41 to 2.95 times the tokens of a whole uninterrupted session, and the paper cannot separate how much of that comes from re-reading other tasks' history.

## Two ways the set-aside task goes wrong

The paper names two signatures in the traces ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1), Appendix E.1):

| Signature | What the agent does |
|---|---|
| Requirement-state loss | A later edit or plan "conflicts with an earlier focus requirement or overlooks previously established implementation state" |
| Cross-task interference | "requirements, files, or submission scope from another active task enter the focus task's implementation or finalization" |

In a Click task, the switched agent "successfully adds the later callable-default behavior but does not reconcile it with the earlier literal-default rule." Its own checks passed, and the held-out tests rejected it: the artifact passed 3 of 7 fail-to-pass tests ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1), Appendix E.2).

In a Moto task, the agent returned to the right checkout and made the right repair. At finalization it ran `git diff` across all five workspaces and produced no applicable focus patch. The authors' reading of the trace: "Implementation recovery and submission recovery are separable" ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1), Appendix E.3).

## What to do instead

### Give each unfinished multi-stage task its own session

When you must set a task aside, park it in its own session and start the interruption in another. That is the paper's uninterrupted control: the same task, verifier, and checkout, with no other task's requests in the conversation. Name sessions so you can resume them, as the [Kitchen Sink Session](session-partitioning.md) page describes for Claude Code.

### Keep a per-task state record and restate it on return

If the work must share a session, keep a short record per task: goal, constraints, decisions, completed work, and pending work. Paste it back when you return. The paper tested an automated form of this, not a manual one. Its Task State Memory is an auxiliary model call which "incrementally updates each task's goal, constraints, progress, pending work, relevant files, and uncertainties from completed interactions" ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1), Section 5.2). [Goal recitation](../../context-engineering/goal-recitation.md) and a [session recap](../agent-design/session-recap.md) are the same move at a different boundary.

### Scope the submission to one task

State which checkout and which task the final patch belongs to, and check the diff before you accept it. The Moto failure happened at finalization, after a correct repair.

### Measure with a switched run if your workflow switches

If your team runs agents across several open tasks at once, a single-task benchmark is the wrong evidence for picking a harness. Pair an uninterrupted run with a switched run on the same task and verifier, as Switch-SWE does.

## Why it works

Per-task checkouts preserve code, but the rest of a task's state lives in the conversation. The paper puts it directly: "Relevant history may distribute implemented requirements, earlier decisions, and pending work across many interactions. The source tree does not explicitly capture this state" ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1), Section 5.1). On return, the agent has to find the right history among other tasks' requests and rebuild the cumulative specification.

A separate study of agent handoffs describes a related setup. It runs small open models (Qwen3.6-27B, Gemma 4, Devstral Small 2) on SWE-bench Verified, and it hands a checkpoint from a predecessor run to a successor run. It does not interleave sessions with other tasks. Its framing of the repository-only successor, which gets the checkpointed files and nothing else, is that it has "no record of what the predecessor did. Without predecessor context, the successor must reconstruct what was changed, tested, and observed" ([arXiv:2606.02875v2](https://arxiv.org/abs/2606.02875v2), Section 5). That sentence describes the condition, not a result. The study's finding is lower rediscovery cost, covered under "When this backfires".

An intervention aimed at those two needs narrowed the gap to within 1.0 point for both models it was tested on ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1), Section 5.3). The paper's Resumption Context Manager routes each request to its task's history and injects per-task state memory. "On OpenCode, the module improves focus-task completion under same-repository task switching by 5.5 to 15.5 percentage points across the evaluated models" ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1)).

## When this backfires

- Near, tightly coupled tasks. The gap shrinks when tasks share source directories: GLM-5.3 lost 1.0 point on near interruptions against 11.0 on far ones ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1)). Near gaps ranged from 1.0 to 13.0 points across configurations. The near and far groups hold different focus tasks, so this is an association, and the paper does not test choosing near interruptions.
- One-shot tasks. The measured harm comes from multi-stage tasks suspended and resumed. A task finished in one request has no earlier requirement to lose.
- A wrong state record. In the Click trace the agent "treats the initial reconciliation as already implemented" before the interruption. A summary written from that belief carries the error forward. Check a state record against tests, not only against the conversation.
- Expecting the record to fix pass rates. The handoff study found that "predecessor context primarily reduces rediscovery effort, cutting median agent events and prompt tokens even when solved-rate gains are modest" ([arXiv:2606.02875v2](https://arxiv.org/abs/2606.02875v2)).
- Generalizing the mitigation. The Resumption Context Manager was tested on one harness, OpenCode, with two models, and it adds auxiliary model calls that count toward the execution budget ([arXiv:2611.02017v1](https://arxiv.org/abs/2611.02017v1), Section 5.3).

## Key Takeaways

- Before you switch an agent off an unfinished task, write down its earlier requirements and pending work; the checkout will not hold them.
- On return, re-run tests that cover each earlier requirement, not only the agent's own checks. In the Click trace the agent's checks passed and the held-out tests still rejected the patch, so write a test for each earlier rule before you set the task aside.
- Do not treat a near interruption as a safe way to share a session. The smaller gap for near interruptions is an association across different focus tasks, and the paper does not test choosing them.

## Related

- [The Kitchen Sink Session](session-partitioning.md) — finished, unrelated tasks piling up in one session
- [Objective Drift: When Agents Lose the Thread](objective-drift.md) — compaction losing task specifics within one task
- [Distractor Interference: Why Relevance Is Not Enough](distractor-interference.md) — related but inapplicable instructions lowering compliance
- [Goal Recitation: Countering Drift in Long Sessions](../../context-engineering/goal-recitation.md) — restating objectives at the tail of context
- [Session Recap: Goal-Shaped Handoff at Context Boundaries](../agent-design/session-recap.md) — a fixed-schema state record for resuming work
