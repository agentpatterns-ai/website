---
title: "Post-Merge Fix Signals for Agent Merges"
term: "Post-Merge Fix Signal"
description: "Agent merges attract a verified follow-up fix at 1.62 times the odds of human merges in the same repositories, and the merge-time signal that predicts one is commit count, not review time."
aliases:
  - follow-up fix rate
  - post-merge watch window
  - rework count as a defect signal
tags:
  - testing-verification
  - code-review
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-24
maturity: emerging
---

# Post-Merge Fix Signals for Agent Merges

> Agent merges draw a follow-up fix at 1.62 times the odds of human merges in the same repositories, and commit count predicts which.

Keep watching an agent pull request for a week after it merges, and choose which ones by the commits it took to land. Across 891 repositories and five agents, 4.5% of merged agent pull requests drew a verified follow-up fix within 30 days ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)). The human comparison uses a narrower sample, the 2,012 agent merges that share an observation window with the human baseline, so its agent rate differs. There the rate was 3.68% against 2.34%, a Mantel-Haenszel odds ratio of 1.62 stratified over the 218 repositories where both cohorts appear (95% CI 1.10 to 2.39, p=0.015) ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)).

## Two conditions before you build anything

The absolute gap is 1.34 percentage points, so merge volume decides whether this is a practice or a statistic.

- Enough agent merges to produce events. At a 3.68% verified rate, a repository merging ten agent pull requests a month expects roughly one verified follow-up fix a quarter. Below that, just read the fixes as they arrive.
- Fix authorship you can attribute. The study dropped OpenAI Codex from its commit-level measurement because Codex "does not sign its commits (only PR-level)" and "fewer than 2 % carry any marker" ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)). A dashboard reading authorship from markers records that agent's work as human.

## Which merges to watch

Pooled across the cohort, merges that later needed a fix look almost identical at merge time to merges that did not. Every effect size came out negligible or small, and the two that reached significance point the awkward way: merges that got fixed had slightly shorter review, not longer ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)).

Comparing inside a repository changes that. Holding the repository and the count of non-boilerplate files fixed, a conditional logistic regression gives these odds of a verified fix for two merges ten times apart on each signal ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)):

| Merge-time signal | Odds ratio at tenfold | p |
|---|---:|---|
| Commits to complete the pull request | 6.1 | <0.001 |
| Review items | 2.4 | 0.022 |
| Post-first-push churn | 1.3 | <0.001 |
| Time under review | not significant | 0.18 |

Commit count is the signal. Review duration is not one, which stings, because it is the number a merge queue makes easy to read. Size the window from the timing: "half of the 30-day incidence accumulates within the first week", in the agent and the human cohort alike ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)).

## Who shows up

Route the fix back to the agent that shipped the merge. Of 263 verified fixes on agent merges, 69.6% were opened by the same agent, 27.4% by a human, and 3.0% by a different agent. Human merges were fixed by humans 89.1% of the time ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)). The agent writes them too, at an average 87.4% agent-authored share per pull request, and 76.4% of fix pull requests are agent-authored in every commit, against 78.8% and 54.1% on the same agents' ordinary merges ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)).

Read that as a correction to the file-level picture rather than a contradiction of it. [Agent-generated code maintenance asymmetry](../code-review/agent-code-maintenance-asymmetry.md) reports humans doing 83.21% of all maintenance commits on AI-generated files. At the granularity of the pull request that fixes one specific merge, the agent comes back.

## Why it works

Agent merges pass a lighter review, so defects a reviewer would have caught land in the default branch and surface later as a fix. The review gap is measured: 61.4% of agent pull requests receive no recorded human review, a figure the authors cite as their motivation ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)). An independent study of 182 repositories adds the dose-response half, finding that "each 10 percentage-point increase in a project's no-review rate is associated with roughly a 6% increase in agentic maintenance burden on average", alongside agentic lines receiving "corrective maintenance at a 49% higher rate than human lines" ([arXiv:2607.09902v1](https://arxiv.org/abs/2607.09902v1)).

Commit count predicts because it records how hard the change was to converge on, and that difficulty does not stop at the merge: "the PRs that needed many rounds of work before the merge are the ones most likely to need more work after it" ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)).

## When this backfires

- You trigger on the heuristic instead of the verified label. The candidate rate is 22.9% against a verified rate of 4.5%, so file co-location plus a fix-type tag flags about five non-fixes for every real one. The study closed that gap with human annotators and an LLM judge at 90% direct-fix precision ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)).
- You turn commit count into a merge gate. That 6.1 is an odds ratio against a 4.5% base rate ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)), so most high-commit merges still need nothing afterward, and a block stops mostly clean work.
- Your repository already reviews every agent pull request. The maintenance-burden association runs on the no-review rate, so a team at zero has less of it to recover ([arXiv:2607.09902v1](https://arxiv.org/abs/2607.09902v1)).
- You read the 30-day rate as the true rate. The linking rule "can miss cross-file fixes, fixes slower than 30 days, and fixes folded into non-fix-typed PRs", so every number here is a floor ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)).
- You expect line-level survival data to agree. AI-authored lines carry a 16% lower hazard of modification (HR = 0.842, p < 0.001) ([arXiv:2601.16809v1](https://arxiv.org/abs/2601.16809v1)). Less modification overall and more corrective modification are both true, and only the second says anything about defects.
- Your repositories sit outside the studied population. The cohort is five agents in AIDev repositories with more than 500 GitHub stars, and the authors state their findings "for this population rather than for agent PRs in general" ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)).

## Example

The paper gives three numbers a watch rule needs: a 4.5% verified rate, a 6.1 odds ratio per tenfold commit count, and half the incidence inside the first week ([arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1)). Written as a rule over merged agent pull requests:

```text
Trigger    an agent PR merges
Rank       commits on the PR, against this repository's own median
Watch      the merges well above that median, for 7 days after the merge
Look for   a later merged fix-typed PR touching any non-boilerplate file
           this merge touched
Route      hand the fix to the agent that authored the merge, not a human queue
Do not     block the merge on commit count; at a 4.5% base rate most
           high-commit merges need nothing
```

Rank against the repository's own median rather than a fleet-wide threshold, because the 6.1 comes from a within-repository comparison and the pooled distributions barely separate.

## Key Takeaways

- Watch an agent merge through its first week, because half the 30-day fix incidence lands there
- Rank what to watch by commit count, not by how long review took; review time carries no within-repository effect (p=0.18)
- Expect the agent to open and write the fix, so give it the merge event rather than filing a ticket for a human
- Treat the 4.5% verified rate and the 1.62 odds ratio as floors, since fixes past 30 days and across files are invisible to the linkage
- Attribute the fix from something other than commit markers where your agent leaves none

## Related

- [Agent-Generated Code Maintenance Asymmetry](../code-review/agent-code-maintenance-asymmetry.md) — the file-level view, where humans do 83.21% of maintenance commits; this page is the narrower fix granularity, where the agent returns
- [PR-Subscribed Agent Ownership](../patterns/agent-design/pr-subscribed-agent-ownership.md) — the design that makes self-fixing deliberate, and the conditions it needs before the merge
- [Evidence-Bundled Agent PRs](evidence-bundled-agent-prs.md) — the pre-merge counterpart, sizing a reviewer's effort per change instead of watching after the fact
- [Diff-Coverage Gate for Agent PRs](diff-coverage-gate-agent-prs.md) — a gate on the same population at merge time, where the signal is tested lines rather than commit count
- [CRA-Only Review and the Merge Rate Gap](../code-review/cra-merge-rate-gap.md) — reviewer composition at merge, the input the no-review association runs on

## Sources

- [arXiv:2609.26847v1](https://arxiv.org/abs/2609.26847v1) — Takerngsaksiri, Duong, Barnett: Who Finishes the Job? A Study of Follow-Up Fixes and Commit Authorship on AI Coding Agent Pull Requests
- [arXiv:2607.09902v1](https://arxiv.org/abs/2607.09902v1) — Do These Violent Delights Have Violent Ends? Measuring the Post-Merge Fate of Agentic Code
- [arXiv:2601.16809v1](https://arxiv.org/abs/2601.16809v1) — Will It Survive? Deciphering the Fate of AI-Generated Code in Open Source
