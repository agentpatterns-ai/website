---
title: "Agent-Generated Verification Reports: A Structured Round-Trip for Human Review"
term: "Agent-Generated Verification Report"
description: "Have each parallel agent emit a per-sub-task report — the request quoted verbatim, what changed, and exact test steps — with verified and not-fixed verdicts that route back to the agent as the completion signal."
tags:
  - testing-verification
  - human-factors
  - tool-agnostic
aliases:
  - agent-generated verification report
  - structured review round-trip for agent work
  - per-sub-task verification report
last_reviewed: 2026-08-28
maturity: emerging
---

# Agent-Generated Verification Reports: A Structured Round-Trip for Human Review

> An agent emits a per-sub-task verification report — request verbatim, change summary, test steps — and the human's verdict routes back as the completion signal.

A verification report is a routing artifact, not evidence. The agent writes down what it was asked, what it changed, and the exact steps to check the change. The human runs those steps and records verified or not-fixed with a comment, and the verdicts return to the agent, which keeps working until every sub-task closes. The report says what to check and where; only the executed check says the work is correct.

## When the round-trip pays off

Adopt it only when all four conditions hold. Drop one and it degrades into the agent grading itself.

- The reviewer executes the test steps against the running system. Reading the summary and clicking verified turns the report into a self-authored verdict, the configuration that fails hardest.
- The change is not cheaply machine-checkable. A unit test or CI gate is independent and costs no human attention per run. Reserve the report for visual behavior, judgement calls, and cross-system flows.
- The verdict channel is wired back to the agent. Without the return path you are writing status comments by hand again — the cost the practice exists to remove.
- Batch size stays inside review capacity. GitHub reports Copilot code review has "processed over 60 million reviews, growing 10x in less than a year", and that "more than one in five code reviews on GitHub now involve an agent" ([Griffiths, GitHub Blog](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)). One practitioner runs 50 to 100 tasks a day this way, spending 30 seconds to one minute verifying each report ([Towards Data Science](https://towardsdatascience.com/how-to-effectively-solve-100-tasks-with-claude-code/)). Past some batch size the report is another skim surface.

## What goes in the report

The practitioner account describing this method asks the agent for one entry per sub-task with four parts ([Kjosbakken, Towards Data Science](https://towardsdatascience.com/how-to-organize-all-of-your-coding-agent-tasks/)):

| Field | What it carries | Why it is load-bearing |
|-------|-----------------|------------------------|
| Original request, verbatim | The task message as sent, unparaphrased | The only baseline for judging whether the change answers what was asked rather than what was built |
| Change summary | Short description of what the agent did | Orients the reviewer; carries no evidentiary weight |
| Test steps | "a bullet point list on exactly how I can test what the agent has done" | The reviewer's script, concrete enough to follow without reconstructing context |
| Verdict control | Verified or not-fixed, plus a comment field | Turns a human judgement into a machine-readable completion signal |

The source asks for the original message "quoted verbatim" for a reason: once the implementing agent paraphrases the request, the reviewer has no independent statement of intent to compare against.

Rendering is an implementation detail. The practitioner account describes an HTML page, which is what carries its verified and not-fixed buttons, and [HTML as Agent Output Format](../instructions/html-as-output-format.md) covers when that choice pays off — but the round-trip is the pattern, and a Markdown checklist or tracker comment carrying the same four fields closes the same loop.

## Two supporting practices

The report only becomes tractable alongside two habits from the same account. Give each task a uniquely named worktree, named so "I can know exactly what work is being done there" — the name alone identifies the work, so parallel agents never collide and context recovery costs no log reading ([Lazy Worktree Isolation](../workflows/lazy-worktree-isolation.md)). Connect the task tracker to the agent over an API or MCP so the agent maintains ticket state itself instead of the human writing progress comments ([Issue-Tracker as Agent Dispatch Surface](../workflows/issue-tracker-agent-dispatch-surface.md)).

## Why it works

The round-trip moves the verdict outside the producer and the procedure outside the reviewer's head. The first half carries the weight. A cross-benchmark decomposition of a production enterprise agent concludes that "the loop's value comes from the independence and specialization of the observer" — replacing the independent verifier with the frontier model judging its own work cut rescues from 6 to 2 on SpreadsheetBench and correct rejections by 4 to 5 percentage points on BullshitBench ([Dastidar and the Leni Team, arxiv 2607.17044v1](https://arxiv.org/abs/2607.17044v1)). The report supplies that independent observer with per-sub-task criteria instead of a whole diff, the construction VeriLA uses to make agent failures attributable while "reducing human cognitive load" ([Sung, Kim and Zhang, arxiv 2503.12651v1](https://arxiv.org/abs/2503.12651v1)). The second half is ordinary cognitive offloading: externalizing what would otherwise sit in working memory supports immediate performance, at a documented cost to later recall of the offloaded material ([Grinschgl, Papenmeier and Meyerhoff, 2021](https://journals.sagepub.com/doi/10.1177/17470218211008060)) — which is fine here, because the reviewer needs the steps to hand, not memorized. The verdict field then closes the loop, handing the remaining work back to the agent rather than to the human.

## When this backfires

- The reviewer trusts the summary. Self-authored verification fails in exactly this shape: across 35 model and game combinations every self-assigned score reached at least 0.70, yet 15 of 35 policies scored below the random baseline in real deployment ([Guo et al., arxiv 2607.24300v1](https://arxiv.org/abs/2607.24300v1)). A report the agent writes is a self-score until a human executes it.
- The test steps are derived from the implementation. The agent that wrote the code also chose what to test, so the reviewer confirms what was built rather than what was asked.
- Presentation raises confidence faster than it raises evidence: "The surface looks clean. The debt is quiet. And reviewers … actually feel better about approving it" ([Griffiths, GitHub Blog](https://github.blog/ai-and-ml/generative-ai/agent-pull-requests-are-everywhere-heres-how-to-review-them/)).
- The change was machine-checkable anyway. On SpreadsheetBench the isolated contribution of the verification loop measured 1.5 percentage points of an 11-point uplift, against 9.5 from scaffolding and prompting ([Dastidar and the Leni Team](https://arxiv.org/abs/2607.17044v1)), so a human checklist over a change that CI already covers spends attention for nothing.
- Reports accumulate faster than they are consumed. At high throughput the per-sub-task entry stops being a bounded checklist and becomes a queue, and review collapses to skimming.

The strongest case against the pattern follows from the same evidence: every field is written by the party under review. An independent reviewer agent that sees only the diff and the original request, or a CI gate the producer cannot optimize against, buys more reliability per unit of effort. The report earns its place only where no cheap machine check exists.

## Key Takeaways

- The report routes attention; it does not certify correctness. Budget it as reviewer overhead, not as a quality gate you can count on.
- Quote the original request verbatim. A paraphrase by the implementing agent removes the reviewer's independent statement of intent.
- Wire the verified and not-fixed verdicts back to the agent, or the report is a document rather than a loop.
- Reserve it for changes a machine cannot check cheaply. A CI gate is independent and costs no attention per run.
- Watch for the reviewer reading the summary instead of running the steps. That failure mode returns the pattern to self-authored verification, which stays green while real performance degrades.

## Related

- [Agent-Recorded Video Demos as a Verification Artifact](agent-recorded-video-demos.md) — the same producer-to-human handoff in a visual modality
- [Verification Ledger for Tracking Agent Output Quality](verification-ledger.md) — the machine-checkable half, where tool and exit code replace the claim
- [Pre-Completion Checklists for AI Agent Development](pre-completion-checklists.md) — gating the agent's own completion signal before a human sees it
- [Author-to-Reviewer Role Inversion in AI-Assisted Teams](../human/author-to-reviewer-role-inversion.md) — why review capacity is the constraint this report spends
- [Parallel Agent Sessions Shift the Bottleneck from Writing](../workflows/parallel-agent-sessions.md) — the parallelism that creates the review load in the first place
- [Per-Task Verification Budget: Size the Task to Fit the Check](../workflows/per-task-verification-budget.md) — the fixed time budget this report is built to fit inside
