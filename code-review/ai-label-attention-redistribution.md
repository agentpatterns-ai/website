---
title: "AI Label as Reviewer Attention Redistribution"
term: "AI Label Attention Effect"
description: "Surfacing the LLM label and the originating prompt lifts reviewer fixation time and shifts evaluation to criteria-based or prompt-guided strategies — but the eye-tracking proxy for inspection thoroughness does not move."
aliases:
  - LLM label review attention
  - prompt-as-review-aid
  - AI label code review effect
tags:
  - code-review
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-28
maturity: emerging
---

# AI Label as Reviewer Attention Redistribution

> Labelling code as LLM-generated raises reviewer fixation time +33–60% and shifts strategy toward criteria or prompt-guided review, but measured scanning thoroughness stays flat.

## When this technique applies

The label-and-prompt effect lands cleanly in three conditions: reviewers see one labelled PR at a time (not a sustained queue), the originating prompt is surfaced alongside the code, and the reviewer pool has not yet habituated to agent PRs. Outside those conditions — high agent-PR volume, repeat within-reviewer exposure, or trusting priors — the attention shift compresses or inverts ([arXiv:2606.26505 §Threats to Validity](https://arxiv.org/abs/2606.26505); [Reviewer Habituation in Agent PR Review](reviewer-habituation-decay.md)).

## The measured effect

A Wizard-of-Oz eye-tracking study of 32 software engineers across 20 European organisations (average 7.0 years of experience) reviewed four Python files (avg 77 lines, pre-ChatGPT cutoff) with and without an LLM label that included a timestamp and the originating prompt ([arXiv:2606.26505](https://arxiv.org/abs/2606.26505)):

| Signal | Direction | Magnitude |
|--------|-----------|-----------|
| Fixation duration, simple code (6 LoC) | up | +33% (~5 s extra) |
| Fixation duration, complex code (25 LoC) | up | +60% (~15 s extra) |
| Saccade length (thoroughness proxy) | flat | 85–110 px both conditions, 95% CI [-0.07, 0.10] |
| Reviewers adjusting evaluation criteria | — | 37.5% (n=12) |
| Reviewers using the prompt during review | — | 43.75% (n=14) |

The fixation effect is credible (95% CI [0.09, 0.56]) and scales with code complexity. The saccade-length non-effect is the constraint: "the presence of an LLM-label does not change the length of saccades" — "shorter saccades indicate more detailed inspection" ([arXiv:2606.26505 §Results](https://arxiv.org/abs/2606.26505)). Extra time at the label goes into more passes of the same scanning pattern, not deeper inspection.

## Two prompt-usage patterns

The 43.75% who reached for the prompt split into two qualitatively distinct gaze patterns ([arXiv:2606.26505 §Interview Analysis](https://arxiv.org/abs/2606.26505)):

- Requirement validation (n=5) — back-and-forth gaze between prompt and code, treating the prompt as the contract and checking the code against it.
- Documentation support (n=7) — label-first reading then code inspection, treating the prompt as an entry point into the change's intent.

The two patterns have opposite review-quality implications. Requirement validation cross-checks the code against an external statement of intent and surfaces gaps when the code diverges. Documentation support anchors the review to the prompt's stated intent, which means a fabricated contract (the agent picked a plausible-sounding intent that does not match the codebase) passes both the prompt cross-check and the surface scan ([Reviewer's Playbook for Agent-Authored Pull Requests](reviewers-playbook-agent-authored-prs.md) lists this as the fabricated-contract failure mode).

## Three operational moves

The technique reduces to three moves a team can wire into the review surface:

- Surface the originating prompt alongside the code. PR description, commit message, or in-IDE annotation — whichever channel the reviewer already reads first. The label without the prompt produces fixation-time gain only; the prompt is what triggers the criteria-shift and the cross-check pattern ([arXiv:2606.26505 §Results](https://arxiv.org/abs/2606.26505)).
- Route labelled PRs through a criteria-based checklist. The 37.5% criteria-shift is voluntary in the lab; pairing the label with a structural inspection order ([Reviewer's Playbook for Agent-Authored Pull Requests](reviewers-playbook-agent-authored-prs.md)) converts it from "if the reviewer remembers" into "the queue routes it."
- Use the prompt as cross-check, not as documentation. The requirement-validation pattern is the higher-quality of the two — train reviewers to gaze prompt → code → contract rather than prompt → code-as-described. The documentation-support pattern is what anchors review to a fabricated contract.

## Why it works

Explicitly labelling code as LLM-generated flags the region as warranting verification, so reviewers spend longer fixating on it (+33–60%) and a substantial minority adjust their evaluation strategy — toward logical-correctness criteria for 37.5%, and toward prompt-guided review for 43.75% ([arXiv:2606.26505 §Results](https://arxiv.org/abs/2606.26505)). The label and the prompt together act as a category prior that summons existing review skills more deliberately. The mechanism is attention redistribution, not skill acquisition: the same reviewer applies the same scanning pattern over more time, which is why total fixation time rises while saccade-length thoroughness stays flat.

## When this backfires

Five conditions degrade or invert the lab effect:

- High agent-PR volume. The within-reviewer longitudinal data on 400 repeat reviewers over seven months shows approval rates rise 30.1% → 36.8% (p < 10⁻⁶), inline comments fall 22%, and latency triples once exposure compounds ([Reviewer Habituation in Agent PR Review](reviewer-habituation-decay.md)). The label that prompted +33% fixation in a one-shot session loses that effect under sustained exposure.
- Documentation-support gaze pattern. Seven of the fourteen prompt-users read the prompt as documentation rather than as a cross-check ([arXiv:2606.26505 §Interview Analysis](https://arxiv.org/abs/2606.26505)). When the agent fabricates a plausible intent — common for agent PRs — the prompt cross-check confirms the fabrication.
- Saccade-length plateau as silent failure. Measured inspection thoroughness did not move ([arXiv:2606.26505 §Results](https://arxiv.org/abs/2606.26505)). A team treating the label as a thoroughness lever misses the same boundary-case defects as without it; the additional time goes into more passes of the same pattern. The technique is for attention routing, not for catching what surface review already misses.
- Reviewer-sentiment dampening. Empirical PR-review data shows reviewers express fewer negative emotions toward AI-generated PRs than toward human ones, despite the code carrying substantially higher redundancy ([arXiv:2601.21276](https://arxiv.org/abs/2601.21276)). The label can soften critical pushback rather than sharpen it.
- Positive prior toward LLMs. The paper's threats-to-validity section flags unmeasured "participant stance toward LLMs" as a moderator ([arXiv:2606.26505 §Threats to Validity](https://arxiv.org/abs/2606.26505)). Trusting reviewers may show smaller or inverted fixation shifts; the lab population's effect size does not transfer to a team selected for AI enthusiasm.

The mechanism is sub-deliberate either way. Pair the label with structural guards — risk-routing, mandatory checklists, revert telemetry tied to specific approvals — rather than relying on it to summon scrutiny.

## Example

A team integrating an agent that opens PRs against a public API repo wires the label and the originating prompt into the PR template:

```markdown
<!-- agent-authored -->
**Origin**: claude-code session 2026-06-25T14:02Z
**Prompt**:
> Add a per-IP rate limiter to the `/messages` endpoint. Default to 60 req/min,
> overridable via `RATE_LIMIT_RPM`. Return 429 when the window is exhausted.

## Changes
- handlers/messages.go: added `withRateLimit` middleware
- handlers/messages_test.go: added rate-limit boundary test
```

A reviewer following the requirement-validation pattern reads the prompt, scans the diff, and cross-checks: does the middleware return 429 when the window is exhausted, or only when it is exceeded? The prompt asserts the contract; the code is the implementation. The cross-check catches the off-by-one — the middleware fires on `requests >= limit + 1` instead of `requests > limit`.

A reviewer following the documentation-support pattern reads the prompt, accepts it as the contract, scans the diff for surface plausibility, and approves. Same label, same prompt, opposite outcome — the gaze pattern is what determines whether the technique works.

## Key Takeaways

- Labelling code as LLM-generated and surfacing the prompt raises fixation time +33% on simple code and +60% on complex code in a one-shot lab study ([arXiv:2606.26505](https://arxiv.org/abs/2606.26505)).
- Saccade length — the eye-tracking proxy for inspection thoroughness — does not change. The label redistributes attention; it does not deepen inspection.
- 37.5% of reviewers adjust evaluation criteria and 43.75% use the prompt during review, splitting into requirement-validation (n=5) and documentation-support (n=7) gaze patterns with opposite review-quality implications.
- The lab effect compresses or inverts under high agent-PR volume, habituated reviewer pools, the documentation-support gaze pattern, dampened reviewer sentiment, and positive priors toward LLMs.
- Treat the label as an attention-routing lever paired with structural guards (criteria-based checklist, requirement-validation training, revert telemetry), not as a thoroughness lever.

## Related

- [Reviewer's Playbook for Agent-Authored Pull Requests](reviewers-playbook-agent-authored-prs.md) — the structural inspection order this technique routes labelled PRs into
- [Reviewer Habituation in Agent PR Review](reviewer-habituation-decay.md) — the longitudinal counterpoint: the same label loses its attention-shift effect under repeat exposure
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — why surfacing the prompt has to stay high-signal to avoid contributing to alert fatigue
- [PR Description Style as a Lever](pr-description-style-lever.md) — the surface where the prompt and label most naturally land, and the merge-rate consequences of getting it wrong
- [Human-AI Review Synergy](human-ai-review-synergy.md) — adoption-rate baselines that bound how much an attention-redistribution lever can shift outcomes

## Sources

- [arXiv:2606.26505](https://arxiv.org/abs/2606.26505) — Khojah, Gomes de Oliveira Neto, Mohamad, Frattini, Leitner (June 2026): "Same Scrutiny, More Time: Eye Tracking Insights into Reviewing LLM-Labelled Code", ASE 2026.
- [arXiv:2601.21276](https://arxiv.org/abs/2601.21276) — Reviewer sentiment and code-quality study on AI-generated pull requests.
