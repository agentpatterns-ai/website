---
title: "Treating a Resolved Task as a Defect-Free Change"
term: "Resolved Task as Defect-Free"
description: "Eleven coding agents resolved 60.7% of tasks on average but avoided the defect a later PR fixed in only 14.8%. Told the defect, five of them fixed 91%."
aliases:
  - foresight resolve rate gap
  - latent defect after task resolution
  - unstated defect anticipation
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-05
maturity: emerging
---

# Treating a Resolved Task as a Defect-Free Change

> A resolved task shows the agent did what the ticket asked. Whether the change also broke something the ticket never named is a separate question.

The evidence for this comes from one benchmark, and its defects already got past review in real projects. Read the numbers with both limits in mind.

Foresight-SWE pairs a merged pull request with the later pull request that fixed a defect the first one introduced: 212 instances from 35 open-source repositories in 4 languages ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)). The agent gets the repository and the first task, with nothing about the later fix. The paper reports three metrics. Resolve rate counts instances where the agent passes the first PR's tests. The anticipation score is the mean fraction of the later PR's fail-to-pass tests the agent passes. The foresight resolve rate (FRR), the primary metric, counts instances where the agent passes the first PR's tests and the later PR's fail-to-pass tests.

Across 11 models, "the average resolve rate is 60.7%, while the average FRR is only 14.8%" ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)). Claude Opus 5 had the best FRR at 24.5%. Qwen3.8 Flash Next resolved the most tasks, 92.0%, and reached an FRR of 20.8%. FRR counts a subset of resolved instances, so most changes that passed the task's tests still carried the later defect.

## What the gap looks like

The missed defects are mostly easy to fix. Of the 212 follow-up fixes, 125 were rated easy, and the paper concludes "the missed defects are often substantially easier to repair than the original tasks were to implement" ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)).

One instance asked the agent to reorder the steps that build a class from its declared fields. Users often passed a generator to a callback in that code, and the reorder read the generator twice, so the second read came back empty. The later PR's fix was one line that wrapped the generator output in a tuple, and the paper reports "all eleven models failed this instance" ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)).

Silent defects are the larger share and the harder one. In 129 of the 212 instances the later test fails on an assertion, not an exception, so the code returns a wrong answer without an error. Agents reached an FRR of 18.5% on loud defects and 12.5% on silent ones ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)).

## Why it works

The task statement and its tests define success, and that signal says nothing about behavior the statement never names. The paper separated finding the defect from fixing it. Five models received the follow-up PR's task description directly and resolved 91.23% of instances. On the same defects left unstated, the same five reached an average FRR of 19.91% ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)). The authors conclude "the primary bottleneck is identifying the latent defect rather than implementing its repair once identified" ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)).

So the agent can write the fix. It rarely finds the break on its own, and asking it to look recovers only part of the gap (next section). Test-based acceptance has the same blind spot on ordinary benchmarks: "because testing is rarely exhaustive, a patch may pass the tests but nevertheless fail to match the developers' expectations" ([arXiv:2503.15223v2](https://arxiv.org/abs/2503.15223v2)).

## What prompting recovers

The paper tested two interventions on three models, alone and combined: a proactive prompt asking the agent to forecast edge cases, and the harness's native review command run after the patch (`/self-review` in Claude Code, `/review` in Codex). The proactive prompt tells the agent to "read how the code you are changing is called, what its neighbours already handle, and which inputs and expected outputs the description never names" ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)).

That prompt "raises FRR for GPT-5.6 Sol and Claude Opus 5 by 13.20 and 8.02 points, respectively, while reducing resolve rate by only 1.88 and 2.36 points" ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)). Opus 5's best FRR across the settings was 35.85%, against 91.51% when the defect was stated.

Native review raised FRR for all three models and lowered resolve rate in every case, by 14.62 points for GPT-5.6 Sol ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)). In one aiohttp instance, the prompted agent found the later fix and then made cleanup changes that failed the original task's tests.

## When this backfires

- The prompt makes this model worse. Claude Sonnet 5 with the proactive prompt dropped from 16.98 to 13.68 FRR and from 59.91 to 44.81 resolve rate ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)). Adding a "consider edge cases" line without measuring both numbers can cost you on both.
- You score agents on defect avoidance alone. The paper states its metric "does not penalize unnecessary defensive changes" ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)). An agent that hardens everything can score well and still produce a diff a reviewer would reject.
- You expect agents to beat human review. Every first PR in the benchmark merged in an open-source project, and the paper says "these are defects that survived review and release" ([arXiv:2611.01181v1](https://arxiv.org/abs/2611.01181v1)), a median of 88 days before the fix. The paper reports no human foresight baseline, so it supports "agents miss these defects," not "agents miss more than people."
- The change has no downstream use. This is inference, not a result from the paper. The proactive prompt points the agent at how the code is called, so a local edit nothing else calls gives it little to read, and the extra check costs a review pass.

## Key Takeaways

- Read a resolved task as evidence about the task. Ask separately what the change could break that the ticket did not mention.
- Point that check at how the changed code is called, and at paths that return a wrong value without an error. Silent defects had the lower FRR, 12.5% against 18.5%.
- Once a defect is named, agents usually fix it. Spend effort on finding the defect, not on a stronger fixer.
- Measure any edge-case prompt or self-review step on resolve rate as well as defect avoidance. Self-review cost resolve rate on all three models tested, and the proactive prompt hurt Sonnet 5 on both numbers.

## Related

- [Happy Path Bias](happy-path-bias.md) — the general tendency to skip error paths and edge cases, of which an unstated downstream defect is one case.
- [Premature Completion: Agents That Declare Success Too Early](premature-completion.md) — the agent stops while stated tests still fail; here every stated test passes.
- [LLM Code Review Overcorrection](llm-review-overcorrection.md) — the cost side of asking a model to look harder at code.
- [LLM Self-Review Failure](self-review-modernization-failure.md) — a model checking its own output for behavior it was not told to preserve.
- [Passing Tests Are Not Evidence a Patch Is Fast](passing-tests-as-performance-evidence.md) — another property a green task suite does not certify.
