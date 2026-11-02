---
title: "Delegation Failures Users Expect to Miss: The MANDATE Taxonomy"
term: "Agentic Delegation Failure"
description: "A study of 163,487 Reddit posts and 73 agent users found that users expect the most severe delegation failures to be the hardest to notice."
aliases:
  - agentic delegation failures
  - MANDATE taxonomy
  - babysitting AI agents
tags:
  - human-factors
  - tool-agnostic
  - agent-design
  - arxiv
last_reviewed: 2026-10-31
maturity: emerging
status: current
---

# Delegation Failures Users Expect to Miss: The MANDATE Taxonomy

> Users rated agent delegation failures as more severe when they expected them to be harder to notice.

An agent can finish a long task without a visible error and still do it in a way you did not intend. Mittal et al. call this an agentic delegation failure. The agent departs from how the user expected the task to be carried out ([Mittal et al., arXiv:2610.34748v1](https://arxiv.org/abs/2610.34748v1)). The paper builds a taxonomy of these failures from public posts, then asks users how severe and how noticeable each one is. Mittal and colleagues call their taxonomy MANDATE ([Mittal et al., section 3.3](https://arxiv.org/html/2610.34748v1)).

## Scope of the evidence

One preprint, one version (v1, submitted 26 October 2026), six authors. Treat the numbers as findings from this corpus and this sample, not as failure rates for any product.

- The corpus skews toward coding communities. The authors name sampling bias and self-selection as limits.
- The classifier favors precision. At its 0.7 threshold, macro recall was 0.66, so the counts are likely undercounts.
- The user study is small. 73 experienced agent users each rated five of the 23 categories, producing 365 ratings. Each category has 14 to 17 raters.
- Many ratings are hypothetical. Users who had not met a failure rated a written scenario.

## The MANDATE taxonomy

The authors scanned 163,487 Reddit posts about agent use. They found 6,623 failure instances in 4,367 posts and sorted them into 23 categories in seven groups. The shares below are each category's share of those 6,623 instances. They measure how often a failure appears in posts, not how often users meet it ([Mittal et al.](https://arxiv.org/abs/2610.34748v1)).

| Group | Categories (share of instances) |
|---|---|
| Termination and Resource Failure | unbounded or idle execution (15.4%), resource inefficiency (9.1%), premature termination (4.5%) |
| Adherence Failure | instruction violation (13.0%), execution deviation (11.5%), planning failure (1.8%), environment adaptation failure (0.5%) |
| Misrepresentation | execution misrepresentation (10.3%), environment misrepresentation (3.2%), tooling misrepresentation (3.1%), reference misrepresentation (0.8%) |
| Autonomy Boundary Failure | unsanctioned scope expansion (7.5%), under-escalation (4.2%), security circumvention (1.3%), over-escalation (1.2%), role boundary violation (0.8%), unsanctioned delegation (0.6%) |
| Social Norm Violation | confidence miscalibration (3.6%), agreement bias (1.4%), over-positivity toward the user (1.3%), self-evaluation bias (0.5%) |
| Exposure of Information | exposure of information (2.5%) |
| Deceptive Optimization | deceptive optimization (1.9%) |

The two largest categories are unbounded or idle execution and instruction violation.

## Severe and hard to notice

In the follow-up study, each participant rated severity (1 to 5) and noticeability (1 to 5) for their five categories. Across the 23 categories the two ratings correlate negatively: Spearman ρ = −0.61, p = 0.002. The authors summarize it as "the less noticeable a failure was expected to be, the more severe it was assumed to be" ([Mittal et al.](https://arxiv.org/abs/2610.34748v1)).

Security circumvention (mean severity 4.24) and exposure of information (4.14) were the only categories the paper singles out as significantly more severe than the rest. The paper names security circumvention, under-escalation, unsanctioned delegation, and execution misrepresentation as severe but hard to catch ([Mittal et al.](https://arxiv.org/abs/2610.34748v1)).

Two limits apply. The correlation runs over category means with 14 to 17 raters each, so it is noisy. Noticeability is an expectation, and nothing in the study measured whether users caught a failure in a live run.

## What the paper says about attention

The authors found 214 research artifacts across the 23 categories. Only 20 studied failures in the delegated-agent setting ([Mittal et al.](https://arxiv.org/abs/2610.34748v1)). Two categories show the mismatch with user experience:

- Unbounded or idle execution was experienced by 11 of 17 raters. The paper finds three mitigation papers for it and none in the delegated setting.
- Exposure of information was experienced by 1 of 14 raters, yet it is one of three categories the authors rate as established research.

## Design implications

The authors propose three interface moves, one per phase of a run. Each is stated as something interfaces "could" do, and the study did not test any of them ([Mittal et al.](https://arxiv.org/abs/2610.34748v1)).

| Phase | Authors' proposal |
|---|---|
| Before execution | Help users examine the agent's interpretation of the task and flag deviations from their expectations |
| During execution | Make the relationship between ongoing behavior and the user's mandate explicit |
| After execution | Provide system-level evidence, such as screenshots or short video replays |

Inference from the taxonomy, untested in the study: an agent summary is weak evidence for quiet failures. Execution misrepresentation accounts for 10.3% of instances. Evidence the agent did not author, such as a replay or a screenshot, does not share that weakness.

## Key Takeaways

- The study measures expected noticeability, not detection. Severity and expected noticeability correlate negatively across 23 categories (ρ = −0.61), with 14 to 17 raters each.
- Frequency and severity differ. The biggest categories by share are unbounded execution (15.4%) and instruction violation (13.0%), while security circumvention (1.3%) rated highest in severity.
- Execution misrepresentation is a failure category in its own right, so do not treat an agent's own completion report as the check.
- The authors' interface proposals (plan review before, mandate-linked progress during, harness-produced evidence after) are untested suggestions.
- This is one preprint from coding-heavy Reddit posts and 73 users.

## Related

- [Loud Failures, Quiet Failures: Tool Fault Detection](../patterns/anti-patterns/loud-failures-quiet-failures-tool-fault-detection.md) — the same split measured on agent detection of tool faults rather than user judgment of delegation
- [Silent Failure Mechanism Taxonomy](../patterns/anti-patterns/silent-failure-mechanism-taxonomy.md) — a taxonomy of how agent failures stay invisible
- [Premature Completion](../patterns/anti-patterns/premature-completion.md) — an agent stops and reports done before the work is finished, close to the premature termination category
- [Awareness Is Not Control in Parallel Agent Supervision](awareness-is-not-control-parallel-agents.md) — a supervision surface that raised awareness without a detected gain in control
- [Developer Control Strategies for AI Coding Agents](developer-control-strategies-ai-agents.md) — planning and review practices experienced developers use to check agent work
