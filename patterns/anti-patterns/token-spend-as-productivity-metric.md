---
title: "Token Spend as an Engineer Productivity Metric"
term: "Token Spend as Productivity Metric"
description: "In a 404-engineer JetBrains panel, token spend tracked agent use more than output: at similar commit counts it varied 39 to 240-fold, and doubling spend went with about 10% more commits."
tags:
  - anti-pattern
  - cost-performance
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - tokenmaxxing
  - token leaderboard
  - tokens per commit as efficiency
last_reviewed: 2026-11-19
maturity: emerging
---

# Token Spend as an Engineer Productivity Metric

> In a JetBrains study, token spend tracked agent use: at similar commit counts, the 90th-percentile week used 39 to 240 times the 10th's tokens.

The anti-pattern is reading an engineer's token spend as output or efficiency. A panel study of 404 JetBrains engineers names the forms it takes: usage leaderboards, minimum spending targets, and token cost per merged pull request reported as return on investment. The same study found that spend tracks output weakly. Its authors recommend "using token spend at most for resource accounting, and evaluating agent-assisted work with evidence about tasks and outcomes" ([Agarwal et al., arXiv:2611.13396v1](https://arxiv.org/abs/2611.13396v1)).

## What the panel measured

The study joined five weeks of gateway-metered tokens to the same engineers' commits. It compared engineers with each other, and each engineer's weeks with one another to hold the person fixed ([Agarwal et al.](https://arxiv.org/abs/2611.13396v1)):

- "Among weeks with similar commit counts, the 90th percentile of spend was 39 to 240 times the 10th."
- "Within an engineer, doubling spend was associated with about 10% more commits."
- "Available work metrics explained 38% of the variation in spend between engineers and 13% of the week-to-week variation within an engineer."
- Who the engineer was explained 79% of the deviance in weekly tokens in sample. Role, manager status, and team did worse than the weekly average on held-out engineers.

The weak slope survived two checks. Using lines changed as an instrument for noisy commit counts raised the within-person slope to 0.48, "still well short of proportional". Delayed output does not explain it either, because the day-level spend-commit correlation peaked on the same day ([Agarwal et al.](https://arxiv.org/abs/2611.13396v1)).

## Tokens per commit misranks engineers

Dividing spend by output does not fix the metric. The paper gives three reasons from its own data ([Agarwal et al.](https://arxiv.org/abs/2611.13396v1)):

- A week with twice an engineer's usual commits has about 1.2 times the tokens, so tokens per commit fall 40%. Busy weeks look efficient.
- At the top, the ranking churns: "only 17 of the 34 engineers in the top decile by tokens per commit in odd weeks remain there in even weeks".
- The ratio moves with the model. Weeks on a newly released model had about 45% more tokens at the same commit count.

The authors' alternative is to "record at the gateway which issue or task each session served", so spend joins to task outcomes instead of commit counts.

## Why it works

Token spend counts an input, and most of that input is context. "Most tokens are context re-sent on every turn: the median call sends about 400 times as many tokens as it receives." Spend therefore scales with the context in each call and with the model in use. Weeks with more spend than their commits predicted had longer sessions and more use of the new model. Much agent work also never reaches a commit. Technical respondents reported a non-coding use such as analysis, research, or planning in 89% of evaluations. The authors draw the contrast with lines of code: "tokens count an input, recorded whether or not anything is produced, and in our data they reflect output only weakly" ([Agarwal et al.](https://arxiv.org/abs/2611.13396v1)).

## When this backfires

Ignoring spend entirely goes too far. The paper keeps one use for it, resource accounting, and DORA proposes a second:

- Budgeting. "five-week totals rank engineers consistently (projected rank reliability 0.87)", so past spend forecasts who needs budget ([Agarwal et al.](https://arxiv.org/abs/2611.13396v1)).
- Finding people. DORA goes further than the paper: it notes that token tracking "can also serve as a highly effective diagnostic tool for identifying power users of AI". It also warns that "individual scores are harmful" ([DORA](https://dora.dev/insights/finding-balance-in-the-era-of-tokenmaxxing/)).

The evidence has limits. It is one company that builds AI coding tools, five weeks, voluntary use, and commits as the output measure. The estimates are associations, so they do not predict what an imposed target would do. Vendor data on 12,000 developers across 200 companies agrees on direction. Jellyfish found that "more tokens do correlate with more output", at a much higher cost per merged pull request ([Jellyfish](https://jellyfish.co/blog/is-tokenmaxxing-cost-effective-new-data-from-jellyfish-explains/)).

## Example

The paper works through one cost decision: a per-person cap versus cheaper calls. A cap mostly limits the heaviest third of users, who spent 79% of all tokens. That group had the lowest share of spend not tied to output (36%), yet by volume it still held most of that spend. "A company that caps therefore cuts spend tied to output along with spend that is not, and the token count does not show which." The paper suggests context management, caching, and routing routine calls to cheaper models before capping, measured in billed cost rather than tokens ([Agarwal et al.](https://arxiv.org/abs/2611.13396v1)).

## Key Takeaways

- Do not rank, reward, or set targets on engineers by token spend as a measure of output. The paper's authors recommend spend "at most for resource accounting". If the association were causal, doubling spend would raise commits by about 10%.
- Do not report tokens per commit as efficiency. It rewards busy weeks and shifts with each model release.
- Use multi-week spend totals for budget forecasts, and record which issue or task each agent session served so spend can join to outcomes.

## Related

- [Agent Headcount as a Vanity Metric](agent-headcount-vanity-metric.md) — the same input-for-output error on agent count; its cost-per-merged-PR suggestion meets the ratio problems above
- [Density-Normalized Quality Metrics Mask AI-Driven Code Growth](density-normalized-quality-metric.md) — another AI-era ratio whose moving denominator tells the wrong story
- [Token Reduction Mistaken for Cost Reduction](token-reduction-not-cost-reduction.md) — why cost cuts should be measured in billed cost, not tokens
- [Agent Spend Is Set by Velocity, Not by Agent Payoff](../../token-engineering/spend-payoff-decoupling.md) — simulation evidence that a spend figure cannot report payoff
- [Rolling Out CLI Coding Agents at Organization Scale](../../human/org-scale-cli-agent-rollout.md) — measuring retention and quality-adjusted impact instead of usage counts
