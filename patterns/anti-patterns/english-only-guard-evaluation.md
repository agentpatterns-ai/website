---
title: "Treating English-Only Guard Evals as Language Evidence"
term: "English-Only Guard Evaluation"
description: "Translating only the user request moved 12.1% of one 7B guard's verdicts. Guards under 13B and purpose-built guards move most, frontier guards barely."
aliases:
  - english-only guard evaluation
  - request language as a guard surface
  - per-language step-level guard evaluation
tags:
  - anti-pattern
  - security
  - testing-verification
  - tool-agnostic
  - arxiv
  - benchmarks
last_reviewed: 2026-10-19
maturity: emerging
---

# Treating English-Only Guard Evals as Language Evidence

> Translating only the request changed 12.1% of one 7B guard's verdicts, so an English evaluation misses how small guards treat non-English users.

An English-only guard evaluation measures a step-level guard on one request language, and the resulting score is then read as if it covered the languages users actually write in. LinguaGuardBench re-ran 19 guards over 1,220 labeled tool-call steps with the trajectory, candidate action and label held byte-identical and only the user instruction translated, so "any change in a verdict is attributable to language alone" ([Demirkiran and Ernstberger, 2026 §3](https://arxiv.org/abs/2610.22244v1)). Of 77 guard-by-language cells, 39 showed a significant shift in false positives or recall ([§4.1](https://arxiv.org/abs/2610.22244v1)).

## Which guards move, and on which languages

The study concentrates the largest shifts in small or purpose-built guards, languages far from English, and long requests. These are prioritization signals, not necessary conditions.

Among the nine guards below 13B parameters, the mean placebo-adjusted flip rate "rises from +1.5 pp on French and +2.1 on German through +3.1 on Turkish to +4.2 on Swahili and +4.4 on Amharic" ([§1](https://arxiv.org/abs/2610.22244v1)). The four guards built specifically to judge agent actions, run with their authors' own prompts, are the most language-dependent in the study, at mean placebo-adjusted flip rates under translation of +3.4 pp (TS-Guard), +2.9 (Safiron), +4.3 (AgentDoG) and +7.7 (ShieldAgent) ([§4.4](https://arxiv.org/abs/2610.22244v1)). The authors bound that term in the next sentence. It means "verdict instability, not harm", and ShieldAgent's error rates improve under translation ([§4.4](https://arxiv.org/abs/2610.22244v1)).

The two strongest guards did not show this effect on the tested benchmark. Gemini 3.8 Flash and Claude Sonnet 5 showed no significant change in false positives or recall under any language tested, Gemini across all five and Claude across the three pre-registered ones ([§4.5](https://arxiv.org/abs/2610.22244v1)).

## Two failure modes, split by guard size

No guard of 12B parameters or more showed a significant recall loss in a tested language, and the large shifts there are extra blocks on benign steps, up to +5.0 pp false positives for Nemotron 3.5 30B on Amharic. Every significant recall loss sits below 10B, the worst being Nemotron Nano 9B at −7.4 pp on Amharic ([§4.1](https://arxiv.org/abs/2610.22244v1)). TS-Guard, at 7.6B, over-blocks like the larger group, so the paper calls this "a tendency, not a threshold" ([§4.2](https://arxiv.org/abs/2610.22244v1)). Neither mode appears in an English evaluation, and they are not degrees of one fault. The over-blocker still recognizes attacks, while the sub-10B guard that under-blocks has lost the signal ([§4.2](https://arxiv.org/abs/2610.22244v1)).

## Why it works

The authors' post-hoc explanation is a mismatch between channels: translation leaves the agent's own reasoning in English while changing the request. Where the history restates the request, "these guards see two channels that disagree, and their verdict moves"; where nothing restates it, the over-blockers "treat the foreign request itself as suspicious" ([§4.7](https://arxiv.org/abs/2610.22244v1)). The English paraphrase control separates language from wording: across typos, four model styles and a human rewrite, "no general guard's verdict flip rate exceeds its own placebo by more than 1.4 pp" ([§4.8](https://arxiv.org/abs/2610.22244v1)). A guard that survives rewording but not translation "has learned the language, more than the register, as a feature" ([§4.8](https://arxiv.org/abs/2610.22244v1)).

The benchmark consequence runs deeper than the robustness one. The strongest guard agreed with a control that had the request field deleted on 100.0% of 3,660 paired verdicts, so "a benchmark cannot test a guard's use of the trusted channel if the untrusted channel already contains it" ([§4.5, §5](https://arxiv.org/abs/2610.22244v1)).

The direction is not specific to agent guards. On content guards, SEALGuard reports that multilingual unsafe and jailbreak prompts drop LlamaGuard's Defense Success Rate "by 9% and 18%, respectively, compared to its performance on English-only prompts" ([Shan et al., 2025](https://arxiv.org/abs/2507.08898v3)).

## When this backfires

- Every user writes English. The extra conditions multiply guard-suite cost and measure a channel nobody exercises.
- The benchmark history already supplies the request. Neither of the two best guards moved significantly in a tested language, and the strongest returned the same verdicts as a control that never saw the request ([§4.5](https://arxiv.org/abs/2610.22244v1)).
- The gate fails on any flip. ShieldAgent's false-positive rate fell in all five languages while recall held, so a flip-count gate would flag a guard whose errors improved ([§4.4](https://arxiv.org/abs/2610.22244v1)).
- The gate fires on a one-point shift. The authors note "the intervals are likely too narrow", because the bootstrap clusters by trajectory (589) while the intervention is per instruction (58) ([§5](https://arxiv.org/abs/2610.22244v1)).
- The fix is translate-then-guard. "We evaluated no mitigation; translate-then-guard or per-language thresholds are untested candidates for the over-blocking regime" ([§5](https://arxiv.org/abs/2610.22244v1)), and the hop carries its own latency and fidelity cost.
- All five translations came from one model that is also a guard, so its measured invariance is a lower bound, and nobody on the team read Swahili or Amharic ([§5](https://arxiv.org/abs/2610.22244v1)).

## Example

The paper's own diagnostic is cheap because it needs no new labels. The concentration in long enumerated instructions "suggests a cheap diagnostic: evaluate guards on translated *long* instructions specifically, and on a low-resource language, where the effect is largest" ([§5](https://arxiv.org/abs/2610.22244v1)).

1. Take the longest enumerated requests from a labeled trajectory set you already have and translate the request field only. Holding the history, candidate action, environment and label byte-identical is what makes a verdict change a language effect ([§3](https://arxiv.org/abs/2610.22244v1)).
2. Add a placebo condition, such as a trailing space, and read every flip rate against it. Placebo floors in the study run from 0.000 to 0.127, so an unadjusted rate reports a guard's own noise ([§4.5](https://arxiv.org/abs/2610.22244v1)).
3. Report false positives and recall separately, because the two size bands fail in opposite directions ([§4.2](https://arxiv.org/abs/2610.22244v1)).
4. Check the per-instruction view before averaging. TS-Guard flips 9.3% of verdicts on Turkish overall, but one instruction goes "from 12% to 92%" blocked, which is 81% of that instruction's steps ([§4.6](https://arxiv.org/abs/2610.22244v1)).

## Key Takeaways

- An English guard score is evidence about English requests. Translate the instruction and nothing else, and half the guard-by-language cells in the study moved.
- Use the observed size trend to choose what to measure, not to predict an untested guard. Over-blocking showed up at 12B and above, every significant recall loss below 10B, and TS-Guard at 7.6B over-blocked anyway.
- Purpose-built agent guards were the least stable class measured, and instability ran in both directions, so measure the direction per guard rather than assuming harm.
- Test one low-resource language and the longest enumerated requests first. Amharic produced the largest shifts in both failure modes, and single instructions carry most of the flips.
- Subtract the placebo floor before acting, and treat shifts around a point cautiously. The paper's own intervals are likely too narrow.

## Related

- [Mid-Trajectory Guardrail Selection for Multi-Step Tool Calls](../../security/mid-trajectory-guardrail-selection.md) — the other axis guards get picked on, where efficacy tracked structured-data competence rather than safety training
- [Treating a Detector's Benchmark Score as Deployment Evidence](detector-benchmark-score-as-deployment-evidence.md) — the same selection error across benchmarks, where detection rank on one injection benchmark barely predicted rank on another
- [Audit the Noise Floor Before Trusting a Benchmark Gap](../../verification/benchmark-noise-floor-audit.md) — why a placebo condition belongs in any perturbation suite
- [Cross-Lingual Prompt Preprocessing (Local-LLM Token Arbitrage)](../../context-engineering/cross-lingual-prompt-preprocessing.md) — the cost and fidelity conditions on the translate-to-English hop that an untested mitigation would add
- [A Guard Hook Approves the Truncated Input It Was Handed](guard-approves-truncated-input.md) — the adjacent case where a guard rules on an input that is not the one being executed
