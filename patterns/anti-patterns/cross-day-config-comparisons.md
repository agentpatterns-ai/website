---
title: "Cross-Day Config Comparisons Under an Injected Date"
term: "Cross-Day Comparison"
description: "Where a surface injects today's date into the system prompt, two agent eval runs taken on different days received different prompts and are not a controlled comparison."
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - hidden date confound
  - undated eval comparison
  - date injection in the system prompt
last_reviewed: 2026-10-03
maturity: emerging
---

# Cross-Day Config Comparisons Under an Injected Date

> On a surface that injects the current date, the baseline you ran today and the candidate you ran tomorrow saw different system prompts.

A cross-day comparison scores two agent configurations on different calendar days and reads the gap as the configuration's effect. The date is an input to the model. Where it is injected, you do not see it change. Sanz-Guerrero et al. swept every date from January 1 to December 31, 2024 across 9 models and 6 datasets, "keeping the rest of the configuration fixed and deterministic". The worst-to-best spread reached 6% accuracy on multiple-choice QA, 14.42% on GSM8K, and 7.32% pass@1 on HumanEval ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1)).

## When the date is the confound

Three things decide whether this is worth your attention.

- Your effect is small. Each headline number is one model's worst date against its best over a full year. The averages are 2.52% on multiple-choice QA, 7.75% on GSM8K, and, on HumanEval pass@1, "4.81% on average just from the date, and by up to 7.32% for the most affected models" ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1), Tables 1 and 2). A change that moves your score by tens of points is never in doubt.
- Your surface injects the date. Llama 3.1 and GPT-OSS "automatically insert the current date above the system prompt defined by the user" in their default chat templates ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1), Appendix B). Qwen3's template does not. Through OpenRouter, with an empty system prompt, no tools and no internet, the authors still got today's date back from Qwen3. The provider added it. That is the probe for an undocumented surface. Anthropic documents where that prompt applies: claude.ai and the mobile apps "use a system prompt to provide up-to-date information, such as the current date, to Claude at the start of every conversation", while "These system prompt updates do not apply to the Claude API" ([Claude Platform docs](https://platform.claude.com/docs/en/release-notes/system-prompts/overview)).
- Your task generates. One answer token gives the date almost nothing to act on; a long trajectory gives it a lot. Neither standard mitigation helps. Chain-of-thought amplified the date sensitivity for Llama 3.1 (8B) on MMLU rather than damping it ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1), §5.3). 5-shot prompting left the multiple-choice average at 2.27% against 2.52% zero-shot ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1), Table 4).

## Why it works

The date moves the first few generated tokens, and autoregression does the rest: "the date affects the selection of initial CoT tokens, and, due to the autoregressive nature of LLMs, these small perturbations cascade into different reasoning paths and different final answers" ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1), §4 and §5.3). That is also why the spread tracks output length.

Nothing about a date is special. On Llama 3.1 (8B) over MMLU, six versions of the same system prompt produced the date sweep's accuracy coefficient of variation, 0.78%. Both beat three confounds that teams already control for on that pairing: batch size at 0.61%, numerical precision at 0.52%, GPU model at 0.48%. Option order keeps pace, at 0.75%. The authors call it "comparable in magnitude to the date effect" ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1), Table 5). The authors' reading is that "the model is sensitive to any system-prompt change, and the date is such a change – except that it happens without the user's knowledge".

You also cannot pick a safe date. Across multiple-choice QA, Spearman correlation between date and accuracy has a median of 0.02 over 27 model-dataset pairs. A date pushes two models the same way on 51% of dates, which is chance. So "the date acts as noise specific to each model and dataset" ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1), §5.1).

## What to do instead

The remedy depends on how much of the prompt you own. The best rung is often unavailable.

1. You own the chat template. Take the date out and change nothing else, as the authors recommend: "removing the date from the chat template when possible while keeping the rest of the template unchanged, or otherwise fixing the date and reporting it alongside the results" ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1)).
2. You are on a hosted API. You cannot pin it. The GPT-5.1 check left the system prompt empty because "the date is injected server-side". It set temperature to 0, disabled reasoning, and ran each of 7 dates twice over 3 datasets. The authors obtained "identical scores in all 42 runs", which they say "strongly suggests that the model is deterministic at a fixed date". Across one week in December 2025 the model still moved up to 4% on GPQA ([arXiv:2609.36931v1](https://arxiv.org/abs/2609.36931v1), §5.2). Run both arms inside one date window, concurrently rather than on consecutive days, and record the date you got.
3. Do not bolt a mock date into your own prompt. One developer gave four models "Behave as though today's date is 2026-02-06"; three complied and gpt-5-mini reported the injected date instead. It explained "I follow the system message, so I report 2026-02-12" ([OpenAI community](https://community.openai.com/t/openai-injecting-a-date-into-the-prompt-breaks-evaluations/1374109)). A conflicting date turns part of the eval into a conflict-resolution task.

## Example

**Before** — one workflow per arm, landing on different days:

```yaml
# .github/workflows/eval-baseline.yaml
on:
  schedule:
    - cron: "0 2 * * 1"   # Monday

# .github/workflows/eval-candidate.yaml
on:
  schedule:
    - cron: "0 2 * * 2"   # Tuesday
```

**After** — one window, both arms, date recorded:

```yaml
on:
  schedule:
    - cron: "0 2 * * 1"
jobs:
  compare:
    strategy:
      matrix: { arm: [baseline, candidate] }
    steps:
      - run: mkdir -p results
      - run: echo "run_date=$(date -u +%F)" >> results/${{ matrix.arm }}.meta
```

The schedule is the whole fix. Neither job can read the date the provider injects. Both arms see the same date, and you write down which it was. Note what the `After` block does not claim. `date -u` records the runner's date, not the injected one. The two agree only if the provider agrees on the timezone.

## When this backfires

- The effect sits far below your decision threshold. Constraining when eval jobs may run has a real scheduling cost. A floor of a few percent buys nothing when the two arms are tens of points apart.
- Stripping the date makes the eval unrepresentative of production. Removing it is itself a system-prompt edit. Table 5 prices arbitrary rewording at the date's own variance on that pairing, so the eval measures a configuration no user is served. The developer in the OpenAI thread asked for an opt-out and an override, "so eval prompts will match prod exactly". Both are controls over the date. Neither is a deletion.
- A single run cannot fit inside one date. A long agent eval that straddles UTC midnight has no single date. One reply in the same thread reports that the injected date appears to carry no timezone ([OpenAI community](https://community.openai.com/t/openai-injecting-a-date-into-the-prompt-breaks-evaluations/1374109)).
- You extrapolate past what was measured. The study covers 9 models, one date format at one fixed prompt position, and dates inside 2024. The four tasks are multiple-choice QA, math reasoning, code generation, and machine translation, so the agent case is a transfer rather than a result.

## Key Takeaways

- Probe the surface before designing around it. Ask with an empty system prompt, no tools and no internet, and see whether the model reports today's date.
- A config comparison is only trustworthy to the width of the floor under it. Write the floor down as a number before you call a single-digit gap a win.
- Run the arms concurrently, not back to back. Two sequential arms can still straddle midnight UTC, which puts them back on different dates.
- Record the date beside the score. It costs one line. It lets you re-run at that date later, or discount the gap between two dates. It does not make two dates comparable.

## Related

- [Perceived Model Degradation](perceived-model-degradation.md) — recommends rerunning a golden-query suite on a schedule, the comparison this confound breaks.
- [Serving-Stack Confounds in Tool-Call Evaluation](serving-stack-confound-tool-call-evaluation.md) — the same misattribution one layer down, where the server's launch flags move and the model takes the credit.
- [Benchmark Noise-Floor Audit](../../verification/benchmark-noise-floor-audit.md) — the instrument's own spread; the date is a floor you cannot sample by rerunning.
- [Decomposing Agent Output Variability by Layer](../../verification/sampling-state-agent-variability-layers.md) — separating sampling noise from orchestration state before picking a mitigation.
- [Seed-Variance Reporting](../../verification/seed-variance-reporting.md) — what to publish when a result moves with something other than the change under test.
