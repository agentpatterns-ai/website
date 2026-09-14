---
title: "Black-Box Agent Risk Scoring by Domain"
term: "Black-Box Agent Risk Scoring"
description: "Scoring an agent through its own interface across seven risk domains ranks which risks to design against; the percentage attached to each domain is a composite over an adversarially-selected pool and does not transfer across models or teams."
tags:
  - testing-verification
  - security
  - tool-agnostic
  - arxiv
aliases:
  - taxonomy-driven agent red teaming
  - domain risk heatmap
  - agent risk domain scoring
last_reviewed: 2026-09-13
maturity: emerging
---

# Black-Box Agent Risk Scoring by Domain

> Domain scoring of a black-box agent ranks which risks to design against; the percentages are composites over a selected scenario pool.

Use black-box domain scoring when you cannot read the agent's source and you want a priority order, not a defect list. The method drives multi-turn adversarial scenarios at a running agent through its public interface, tags each one to a risk domain, and reports a score per domain. Kumar et al. define seven domains (governance, agent output quality, tool misuse, privacy, reliability and observability, agent behavior, access control) and run 120 generated scenarios against each, "requiring only basic system descriptions rather than internal access" ([Kumar et al., arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)).

Three conditions have to hold before the run is worth it. You lack source access. You want prioritization rather than a fix you can regression-test. And you re-run per base model instead of reusing an earlier configuration's numbers.

## What the ranking supports

The usable product is the order of the domains within one configuration. Kumar et al. report governance at 56.25 on both of their systems, and privacy at 65.00 on the multi-agent AutoGen assistant against 37.50 on the single-agent CrewAI one ([arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)). Privacy therefore leads on one architecture and governance on the other. The domain ranking "remains similar across the four base models for each system", which is the finding they build on: "most weaknesses are framework agnostic and arise from agent design and tool integration, not from the base model or framework identity."

The magnitude inside a domain is a different quantity, and it moved with the model. The same results section reports "higher dispersion in Agent behavior (std 22.47) and Tool misuse (std 13.40)", with one configuration's agent-behavior score reaching 85 while the others stayed moderate ([arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)). So the ranking tells you where to spend design effort. It does not tell you how exposed your deployment is.

## Why it works

Multi-turn probing finds holes single-turn scoring cannot reach, because each attacker turn is written against what the previous response leaked. The escalation needs a foothold, and the foothold only exists after the agent has answered once. Jain et al. isolate the effect with a round-budget ablation that holds scenarios, attackers, defenders, and structured-output scoring fixed: "restricting scoring to the first attacker turn yields 0–1% attack success rate (ASR); allowing 15 rounds of adaptive attack yields 5.4–14.0%" ([Jain et al., arXiv:2607.18063v1](https://arxiv.org/abs/2607.18063v1)). Kumar et al. generate scenarios of three to five turns with `max_turns = 5` but run no such ablation, so the causal support comes from outside their paper.

## What the percentage is not

The domain score is not an attack success rate, for three reasons the method states plainly.

Scenarios are filtered for potency before they count. Kumar et al. test candidates against a baseline safe agent, and those that "fail to elicit any concerning responses are considered too weak and regenerated" ([arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)). The pool is selected, so the denominator is not a population of realistic traffic.

The aggregate is weighted. A term `α = 0.1` "gives 10% additional weight to manually validated findings", so a domain mean can exceed the raw judge average over the same trajectories ([arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)).

A crashed run scores as a safe run. Footnote 6 records that Kimi K2 "encountered runtime errors during Stock Advisory agent evaluation in the access control domain, resulting in zero scores", and those zeros stay inside the reported domain mean ([arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)).

## When this backfires

- You own the source and fund this instead of reading it. The paper's own limitation is that black-box testing "cannot assess implementation-specific vulnerabilities that require code-level analysis" ([arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)).
- You compare your number to a published one. Chouldechova et al. argue that "conclusions drawn about relative system safety or attack method efficacy via AI red teaming are often not supported by evidence provided by attack success rate (ASR) comparisons" ([arXiv:2601.18076v1](https://arxiv.org/abs/2601.18076v1)).
- You swap the base model and keep the old result. Jain et al. found two defenders tied in aggregate at 5.4% whose per-scenario profiles diverged to 60% against 7%. Across their benchmark, defender "rankings disagree across scenarios (Kendall's W = 0.19)" ([arXiv:2607.18063v1](https://arxiv.org/abs/2607.18063v1)).
- You read a low score as a working control. Kumar et al. validate no defenses: their "evaluation focuses on vulnerability discovery rather than defense validation" ([arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)).
- You need a test that fails before a fix and passes after. A heatmap cell names no line of code, and nothing in the method shows that a mitigation moves one.

## Example

Access control scored 11.25 on the multi-agent system, the lowest of the seven domains, and two of the four models contributed zeros to that mean. One set of zeros came from Kimi K2 runtime errors, which the authors flag as "model-specific compatibility issues rather than security features" ([arXiv:2609.09647v1](https://arxiv.org/abs/2609.09647v1)). A scorer that only sees the interface cannot separate an agent that refused from a process that died, and both land in the mean as an absence of harm. Check the transcripts for empty responses before you read a near-zero domain as coverage.

## Key Takeaways

- Run this when you cannot read the source. Against code you own, the method gives up the implementation-level findings its authors exclude from scope.
- Report the domain order, not the domain percentage, when you hand the result to anyone who did not run it.
- Re-run per base model, and re-run before you ship a model swap. The ranking survived four models in the published data; the magnitudes did not.
- Log an error channel alongside the score. A black-box harness that cannot distinguish a refusal from a crash reports both as safety.
- Pair the sweep with a mitigation you can test, because the method validates no defense.

## Related

- [Decomposed Red-Teaming for Agent Monitors](decomposed-red-teaming-agent-monitors.md) — the attack-construction half, splitting strategy from execution to widen the scenario distribution
- [Action-Graded Severity for Agent Red-Team Outcomes](action-graded-severity-red-team-outcomes.md) — grading what an attack achieved instead of whether it landed
- [Severity-Stratified Evaluation of Security Prompts](severity-stratified-security-prompt-evaluation.md) — the same headline-number problem on the defense side
- [Black-Box Probing in the Agent Build Loop](../security/black-box-probe-build-loop.md) — probing the application an agent built, rather than the agent itself
- [Four-Layer Taxonomy of Agent Security Risks](../security/four-layer-agent-security-taxonomy.md) — a control-placement taxonomy, with no scoring method attached
