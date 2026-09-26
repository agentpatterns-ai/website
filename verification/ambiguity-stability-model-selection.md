---
title: "Ambiguity Stability as a Model-Selection Criterion"
term: "Ambiguity Stability"
description: "A clear-spec benchmark score measures synthesis, not interpretation. Rank candidate models on the drop between matched clear and ambiguous versions of your own tasks, after you have repaired the requirements you can repair."
aliases:
  - ambiguity-perturbed model evaluation
  - requirement-ambiguity robustness
tags:
  - testing-verification
  - evals
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-20
maturity: emerging
---

# Ambiguity Stability as a Model-Selection Criterion

> Benchmark rank scores a model on requirements with one intended reading, so make ambiguity stability the selection criterion instead.

Ambiguity stability is how far a model's pass rate falls when the same task arrives with a requirement that admits more than one reading. The source study measures it with two arms: the original requirement, then a rewrite that holds the task fixed and introduces exactly one ambiguity, both scored against the same tests. Across 1,304 function-level tasks and 5,216 ambiguous variants, that design found an average Pass@1 drop of 7.22 percentage points, and the largest single decline was 32.35 points ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)). On your own tasks, add a third, paraphrase arm so the drop belongs to the ambiguity and not to the rewording. The next section explains why.

## Repair what you can repair first

This measurement is the residual control, not the first move, because both cheaper fixes beat the 7.22-point gap you would be ranking on. Ambiguity is a property of the specification, so an edit to the text carries to every model you ever run. SpecFix modified 43.58% of problem descriptions across three code-generation benchmarks, lifted Pass@1 on that modified set by 30.9%, and descriptions repaired against one model improved other models by 10.48% ([Jia et al., 2025](https://arxiv.org/abs/2505.07270v3)). [Interactive clarification](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) is the other, worth up to 74% over non-interactive runs on underspecified tasks ([Vijayvargiya et al., 2026](https://arxiv.org/abs/2502.13069v3)).

Reach for ambiguity stability on the requirements you do not control: a customer-worded ticket, an inherited backlog, an issue tracker nobody is going to rewrite.

## The measurement needs three arms, not two

Run each task three ways and score all three against the unchanged tests.

| Arm | Requirement | What it isolates |
|---|---|---|
| Original | Untouched | Your baseline pass rate |
| Paraphrase | Reworded, one reading | Generic sensitivity to rewording |
| Ambiguous | Reworded, two or more readings | The ambiguity effect, net of the paraphrase arm |

The paraphrase arm is the one teams skip, and without it the delta is unattributable, because an ambiguous variant is also a reworded one. Semantics-preserving perturbations alone degrade model performance by as much as 12%, account for up to half the performance variance of a given model, and a single perturbation changes the relative ranking of models in 63% of cases ([Romanou et al., 2026](https://arxiv.org/abs/2603.13285v2)). The rewording in the Orchid variants is measurable: average perplexity runs 17.78% above the originals on the HumanEval-derived subset ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)).

Rank on the ambiguous-minus-paraphrase delta, and rank per ambiguity type rather than on one pooled number. Sensitivity is uneven inside a single model: Claude-3.5 lost 31.10 points to syntactic ambiguity and 2.44 points to semantic ambiguity on the same subset ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)).

## Two cheap detectors that do not work

Asking the model whether a requirement is ambiguous returns a flag with precision near 50%, which means roughly half of what it flags is a clear requirement; Claude-3.5 reached near-perfect recall by flagging almost everything, and localization of the ambiguous span rarely exceeded 23% across models ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)). A gate at that precision stops as much good work as bad.

Comparing outputs across models and treating disagreement as the alarm has a floor problem. On the BigCodeBench-derived subset the inter-model conflict rate was already 51.04% on the original clear requirements, and ambiguity moved it to 57.28% ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)). Six points of signal on top of a fifty-point floor is not a detector. Repeated sampling from one model has more room: GPT-4's intra-model conflict rate went from 14.09% to 28.29% on the HumanEval-derived subset, and DeepSeek-V3's from 6.83% to 17.45% ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)).

## Why it works

Function-level code benchmarks generally assume that each requirement has a single intended interpretation, which excludes linguistic uncertainty from what the score measures ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)). Handed an ambiguous requirement, a model is forced into determinism: it collapses several plausible readings into one executable implementation with no clarification step. Which reading it picks is a second ability, and the leaderboard never scored it. That is why the size of the drop does not follow from the baseline. GPT-4 dropped more than 28 percentage points on the BigCodeBench-derived subset while Qwen-2.5-Coder, starting lower, lost roughly 8 ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)).

A second group reached the same split from the interactive side. ClarifyCodeBench reports that strong code generation performance does not inherently translate into effective requirement clarification, that raising reasoning effort yields marginal gains in identifying ambiguities, and that clarification quality falls sharply as ambiguity density rises ([Fang et al., 2026](https://arxiv.org/abs/2607.00711v2)).

## When this backfires

- Your requirements already arrive machine-checkable, as typed contracts, executable specs, or tests written first. The ambiguity was removed upstream, and the drop you measure describes an input distribution you do not have.
- The work is repository-level. Orchid's own limitations section scopes it to function-level generation with one ambiguity injected at a single location, and an agent that reads surrounding code resolves much of what looks ambiguous in isolation.
- You skipped the paraphrase arm. The delta then mixes ambiguity with the rewording effect that already reorders models in 63% of single-perturbation cases ([Romanou et al., 2026](https://arxiv.org/abs/2603.13285v2)).
- The model is fixed by contract. A ranking changes nothing, and the budget belongs in specification repair, which transfers across models anyway ([Jia et al., 2025](https://arxiv.org/abs/2505.07270v3)).
- You are reading the published ranking rather than running your own arms. The Orchid panel is GPT-4, Claude-3.5, CodeLlama-34B, Qwen-2.5-Coder, DeepSeek-V3, and DeepSeek-R1, released between March 2023 and January 2025 ([Yang et al., 2026](https://arxiv.org/abs/2604.21505v2)). The method survives the panel; the ordering does not.

## Key Takeaways

- Rank on the paired drop, not the clear-spec score. One benchmark's rewrite cost 7.22 points of Pass@1 on average and 32.35 points at worst, and the size of a model's loss did not follow from where it started.
- Budget the paraphrase arm or do not run the study. Rewording alone accounts for up to half of a model's performance variance.
- Report per ambiguity type. A single model spanned 31.10 points on syntactic ambiguity and 2.44 on semantic.
- Do not gate on the model's own ambiguity flag. Precision sits near 50% and span localization rarely clears 23%.
- Do not gate on cross-model disagreement either, unless you have measured its clear-requirement floor. On one subset that floor was 51.04% and ambiguity added 6.24 points.
- Spend on specification repair first. It is the larger effect and it carries to every model.

## Related

- [Repository Perturbation as Context-Reasoning Diagnosis (RepoMirage)](repository-perturbation-context-reasoning-diagnosis.md) — the same paired-arm shape applied to the repository instead of the requirement.
- [Purpose-Built Eval Suites for Model and Harness Swaps](purpose-built-eval-suites.md) — where the tasks for these arms come from, and how to size the suite to the decision.
- [Test-Driven Intent Clarification](test-driven-intent-clarification.md) — the repair half of the story, using generated tests to surface the ambiguity before code is written.
- [Interactive Clarification for Underspecified Tasks](../patterns/agent-design/interactive-clarification-underspecified-tasks.md) — the alternative control, where the agent asks instead of guessing.
- [Assumption Propagation](../patterns/anti-patterns/assumption-propagation.md) — the downstream failure this measurement is trying to price.
