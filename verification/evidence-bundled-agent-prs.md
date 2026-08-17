---
title: "Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort"
term: "Evidence-Bundled Agent PR"
description: "Attach the reproduction, probe, and test an agent already ran to its pull request, so a reviewer picks a depth per change instead of reading every diff alike."
tags:
  - testing-verification
  - code-review
  - tool-agnostic
  - arxiv
aliases:
  - evidence-bundled pull request
  - agent PR evidence chain
  - fit and risk assessment on agent PRs
last_reviewed: 2026-08-14
maturity: emerging
---

# Evidence-Bundled Agent PRs: Sizing the Reviewer's Effort

> Attach the artifacts an agent already produced to its pull request, so reviewers spend depth where the change earns it.

An evidence-bundled agent PR carries the reproduction, the failing probe, and the executed test the authoring agent ran, together with a short statement of fit and risk. The reviewer reads the bundle first and picks a depth for that one change. Vercel built its `ai-sdk-factory` around this goal: "a comprehensive assessment of each change for both fit and risk, including a full chain of documented evidence, making it easy for reviewers to apply the right amount of effort". Its published tiers run from "a quick glance for verification" on docs fixes to "deep review" on a new public API ([Vercel, 2026](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)).

Adjacent patterns size review effort from outside the change. [Risk-score threshold calibration](../code-review/risk-score-threshold-calibration.md) scores a diff with an independent learned model and decides whether a human reviews at all, and [tunable effort levels](../code-review/tunable-review-effort.md) put the dial on the reviewing agent. This one is the producer-side artifact: the author ships its own working notes so a human can size the read.

## The conditions it depends on

Four conditions carry the pattern. Drop one and the bundle becomes a persuasive surface instead of a routing signal.

- Ship the artifacts and let the reviewer judge. A "low risk" label from the authoring agent is a self-report, and an LLM evaluator "scores its own outputs higher than others' while human annotators consider them of equal quality" ([Panickssery et al., NeurIPS 2024](https://arxiv.org/abs/2404.13076v1)). Stated confidence is no better as a queue-ordering signal: on five open-weight models tested it carried almost no information, though the one proprietary model in the same study did have informative confidence ([arXiv:2607.28317v1](https://arxiv.org/abs/2607.28317v1)). See [audit-budget allocation](audit-budget-allocation-agent-fleets.md) for the screen a score must pass first.
- A human approval gate stays. Vercel's results hold under an explicit rule that "nothing is merged without approval from a human on the AI SDK team" ([Vercel, 2026](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)).
- The author and the reviewer are different agents. Vercel builds "a single agent for each specific task", listing separate agents for "Bug reproduction, Bug fixes, PR reviews, Backports, Documentation updates, Feature analysis, Feature implementation" ([Vercel, 2026](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)). Collapsing those roles restores the self-evaluation setup the first condition exists to avoid.
- Reviewers know the code. Unfamiliar files were named a major reason for failing to understand a change ([Bacchelli and Bird, ICSE 2013](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)).

## What goes in the bundle

Every element is something the reviewer can re-run rather than something they have to believe. The quoted artifacts below are ones Vercel's agents attached in production ([Vercel, 2026](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)).

| Element | What the reviewer does with it |
|---|---|
| The failing state before the change, as a runnable check | Confirms the problem was real without rebuilding it |
| A probe that fails on pre-change behavior, as when "The failing probe proved the feature was missing on main" | Reads one file to see the defect addressed |
| The end-to-end run performed, such as "executing an OpenAI web search with wikipedia.org blocked" | Checks the command and its output instead of re-deriving coverage |
| For a backport, the conflict hit and its resolution | Goes straight to the only judgment call in the diff |
| The fit and risk statement | Orients the read. Carries no evidentiary weight |

Vercel sorts each run as success, flawed, blocked, or manual, where "Only success ships, so the rest are signal that re-enters the system as feedback". Over four weeks the factory authored 25 to 35% of weekly merged PRs, closed over 75% of July's closed issues, and took open issues from a peak of 1,022 in late June to 844 by early August ([Vercel, 2026](https://vercel.com/blog/building-a-software-factory-for-ai-sdk)).

## Why it works

Review time goes on reconstruction, not inspection. Interviews at Microsoft found that "understanding is their main challenge when doing code reviews", and that "no other code review challenge emerged as clearly as understanding the submitted change" ([Bacchelli and Bird, ICSE 2013](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)). The same study reports the payoff from closing that gap: "When reviewers have a priori knowledge of the context and the code, they complete reviews more quickly and provide more valuable feedback to the author." A bundle hands over reconstruction the agent already did, so the reviewer pays that cost once and cheaply. The causal lever is lowered reconstruction cost rather than an accurate risk label, which is why the artifacts matter and the verdict does not.

## When this backfires

- The bundle ships a graded score instead of artifacts. The first condition above fails, and the reviewer ends up allocating depth by the producer's opinion of its own work.
- Attention arrives without depth. Labeling code as LLM-generated added about 5 seconds on 6 lines, "approximately a 33% increase", and 15 seconds on 25 lines, "a 60% increase", while "the presence of an LLM-label does not change the length of saccades within an area of interest" ([Khojah et al., arXiv:2606.26505v1](https://arxiv.org/abs/2606.26505v1)). Metadata beside a diff buys attention that stays at the same depth.
- The floor is already zero. Across the AIDev dataset, "84.0% (28246/33596) of agent-authored PRs either receive no recorded review or are reviewed exclusively by agents" ([Duma et al., arXiv:2605.02273v1](https://arxiv.org/abs/2605.02273v1)). A device for spending less effort on low-risk PRs enters a population with little effort left to redistribute.
- Reviewers habituate. The eye-tracking study names a different limit on its own generalization, that "the participants' stance towards LLM-generated code may affect their trust and, hence, moderate the effect of the LLM-label" ([Khojah et al., arXiv:2606.26505v1](https://arxiv.org/abs/2606.26505v1)). What sustained agent-PR volume does to that attention lift is taken up in [Reviewer Habituation in Agent PR Review](../code-review/reviewer-habituation-decay.md).
- A deterministic gate already answers the question. Where a path allowlist, type check, or coverage threshold settles the risk at no marginal cost, the bundle spends agent runtime per PR on a weaker second copy.
- The description does the work alone. Reviewers told the Microsoft study that a change description is not sufficient by itself, since an author can state one thing while doing several more ([Bacchelli and Bird, ICSE 2013](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)).

## Key Takeaways

- Ship artifacts a reviewer can re-run. The fit-and-risk statement orients the read; the reproduction, probe, and executed test are what let a reviewer shorten it.
- The mechanism is reduced reconstruction cost, so the bundle pays off where understanding the change is expensive and the reviewer has standing to judge it.
- A producer-authored risk grade is the weakest part of the artifact and the part most likely to be trusted. Treat it as a table of contents.
- Measure whether the bundle changes what reviewers catch, not whether it changes how long they look.
- Keep the approval gate and a separate reviewing agent. Both Vercel conditions are load-bearing for the reported numbers.

## Related

- [The Software Factory Model: Industrializing Agent Loops](../workflows/software-factory-model.md) — why the review gate is the binding constraint this artifact tries to widen
- [Audit-Budget Allocation for Agent Fleets](audit-budget-allocation-agent-fleets.md) — screening a self-reported confidence score before letting it order a review queue
- [Agent-Generated Verification Reports](agent-generated-verification-report.md) — the per-sub-task variant with a verdict channel routing back to the agent
- [Risk-Score Threshold Calibration for Auto-Approval](../code-review/risk-score-threshold-calibration.md) — the independent learned score that decides whether a human reviews at all
- [Reviewer's Playbook for Agent-Authored Pull Requests](../code-review/reviewers-playbook-agent-authored-prs.md) — the inspection order a reviewer applies once the depth is chosen
