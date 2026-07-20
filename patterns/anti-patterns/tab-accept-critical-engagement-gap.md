---
title: "Tab-Accept Rate as a Proxy for Critical Engagement"
term: "Tab-Accept Critical-Engagement Gap"
description: "Reading a high AI code-completion accept rate as engagement or productivity hides an automation-complacency signal — under the wrong conditions it inverts."
tags:
  - human-factors
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - tab-accept gap
  - accept-rate proxy fallacy
  - autocomplete complacency
last_reviewed: 2026-07-01
maturity: emerging
status: current
---

# Tab-Accept Rate as a Proxy for Critical Engagement

> A high tab-accept rate is not a stand-alone quality signal — under thin-verification conditions its correlation with critical engagement inverts.

Under specific conditions — novice or learning-phase developers, load-bearing (non-boilerplate) completions, and thin downstream verification — a rising tab-accept rate correlates with falling reflective engagement, not with rising productivity. The finding is population- and task-conditional. Treating the raw rate as a stand-alone quality metric hides the second axis needed to interpret it.

## The conditions under which this bites

Read tab-accept rate as an engagement or productivity signal only when all three hold:

- The completions are load-bearing, not boilerplate. Import statements and single-token completions carry no engagement signal; a per-user aggregate is dominated by the trivial accepts.
- The developer has the taste to reject bad suggestions. Professional developers in the top usage quartile show 29.73% accept rates with the highest productivity gains ([Cui et al., 2024, CACM](https://cacm.acm.org/research/measuring-github-copilots-impact-on-productivity/)) — a high rate reflects taste once judgment is intact.
- Downstream verification is thick — CI, tests, mandatory review. Where review catches the errors complacent acceptance would introduce, the accept rate stops being load-bearing on its own.

Miss any of the three and the rate needs pairing with a critical-engagement measure to be interpretable.

## The falsification data point

Clover, a research code-completion tool, logs student interactions with suggestions and embeds attention checks during programming tasks. Higher rates of tab-accept were associated with lower attention-check performance, and increased dwell time was associated with higher attention-check performance ([Hutchison et al., 2026](https://arxiv.org/abs/2606.30549)). The paper also proposes a taxonomy of behavioral interaction metrics for AI-assisted programming, so the accept-rate axis is one dimension of a larger measurement.

The result is on students in a CS-education setting and is correlational, not causal. It falsifies the universal claim that a high accept rate is a positive signal — not the inverse. Students who used generative AI to accelerate toward a solution can maintain an unwarranted illusion of competence, with metacognitive difficulties potentially deepened by AI tooling ([Prather et al., 2024](https://arxiv.org/abs/2405.17739)) — the novice population is where the failure mode shows most sharply.

## Why it works

The mechanism is automation-induced complacency: a confident-looking automated output shifts operator attention away from cross-checking, and this shift is present in both naive and expert participants and is not overcome by simple practice ([Parasuraman and Manzey, 2010, *Human Factors*](https://journals.sagepub.com/doi/10.1177/0018720810376055)). Under multi-task load — a developer typing while a completion previews at the caret — attention allocation favors the manual task over monitoring the automated one, producing the same signature Clover's attention checks pick up. The accept-rate axis measures throughput; a separate axis is needed to measure whether the operator is still monitoring.

## Pair it with a second axis

The second axis measures whether critical engagement is intact:

- Attention checks — Clover-style probes in the tooling. Expensive to instrument, high internal validity ([Hutchison et al., 2026](https://arxiv.org/abs/2606.30549)).
- Dwell-time distribution — time with a suggestion visible before accept or reject. Cheap, noisy on short completions, useful as a distribution not a mean.
- Downstream defect rate — bugs, reverts, or review-comment density on AI-assisted diffs. Late signal, grounded in outcomes.
- Intervention rate segmented by task type — the [intervention rate as a diagnostic north star](../../human/intervention-rate-diagnostic-north-star.md) pattern generalizes: the aggregate is a poor target, the segmented view is a good diagnostic.

The cheapest cross-check is the accept-rate distribution against the downstream defect rate on AI-assisted commits, segmented by task type. If accept rate rises and defect rate rises with it, the second axis is telling you the first is misleading.

## When this backfires

- Teams with thick downstream verification. Where CI, tests, and mandatory review reliably catch complacent acceptances, a two-axis view adds cost without value.
- Experienced developers on familiar stacks. Expertise raises the base rate of correct completions ([Cui et al., 2024, CACM](https://cacm.acm.org/research/measuring-github-copilots-impact-on-productivity/)); Anthropic's expertise data shows expert users trigger about 3,200 words of Claude output per prompt versus about 600 for novices ([Anthropic, 2026](https://www.anthropic.com/research/claude-code-expertise)).
- Attention checks with Hawthorne effects. Embedded probes can change engagement, so instrumentation results may not generalize outside the study context ([Hutchison et al., 2026](https://arxiv.org/abs/2606.30549)).
- Very short completions. Dwell time bins meaningfully around multi-line suggestions; on single-token or same-line completions the signal is noise.

## Key Takeaways

- Tab-accept rate on its own is not a critical-engagement or productivity signal — it is one axis, useful only paired with a second measure ([Hutchison et al., 2026](https://arxiv.org/abs/2606.30549)).
- The correlation between accept rate and engagement inverts under novice populations, load-bearing completions, or thin downstream verification.
- The mechanism is automation-induced complacency from 40 years of human-factors research ([Parasuraman and Manzey, 2010](https://journals.sagepub.com/doi/10.1177/0018720810376055)).
- The cheapest paired signal is the accept-rate distribution against the downstream defect rate on AI-assisted commits, segmented by task type.

## Related

- [Blind Tool Deference: Agents Parroting Callable Tools](blind-tool-deference.md) — the agent-side version of the same automation-complacency mechanism
- [Trust Without Verify](trust-without-verify.md) — accepting output because it looks polished, without independent checks
- [The Effortless AI Fallacy](effortless-ai-fallacy.md) — the belief that AI tools should work without effort, which reinforces low-scrutiny acceptance
- [Suggestion Gating: Fewer Completions, Better DX](../../human/suggestion-gating.md) — the fix-side pattern that lifts accept rate by discarding low-value suggestions before display
- [Intervention Rate as a Diagnostic North Star, Not a Target](../../human/intervention-rate-diagnostic-north-star.md) — parallel argument that a single-number user-interaction metric hides its diagnostic value in the segments underneath
