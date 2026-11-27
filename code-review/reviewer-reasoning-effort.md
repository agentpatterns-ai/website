---
title: "Reasoning Effort for an AI Code Review Gate"
term: "Review Gate Reasoning Effort"
description: "In one Claude 5.5 study on Django patches, medium effort was shown non-inferior to high only for Opus. Every setting accepted at least 45% of wrong patches."
aliases:
  - reviewer reasoning effort
  - AI reviewer effort setting
tags:
  - code-review
  - testing-verification
  - cost-performance
  - claude
  - arxiv
last_reviewed: 2026-11-27
maturity: emerging
---

# Reasoning Effort for an AI Code Review Gate

> On 90 Django patches, Claude 5.5 reviewers accepted fewer wrong ones at high effort than low, and at least 45% in every setting.

Reasoning effort controls how much work a reviewer model does before it returns a verdict. A preprint measured what that buys against plausible-but-wrong patches. Claude Opus 5.5, Sonnet 5.5, and Haiku 5.5 each reviewed the same 90 agent-written patches from SWE-bench Verified at low, medium, and high effort ([Shen et al., arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)). A patch first counted as wrong if it passed the benchmark's tests and failed stronger SWE-ABS tests. A label check after the runs left 55 wrong and 35 correct.

## What the study ran

These conditions bound the study's numbers ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)):

- Claude Code 2.1.311 in non-interactive mode, with no plugins or saved settings, and effort set by `--effort`.
- The reviewer saw the issue text and the Django repository with the patch as one commit. It could read and write files and run shell commands. It had no internet beyond the model API, and no scoring tests or official fix.
- One generic prompt failed a patch only for an unmet requirement or a functional defect that matters.
- The Opus study was preregistered. The Sonnet and Haiku studies are exploratory.
- The first author develops Trust My Bot, the agent harness whose review gate motivated the study.

## Results by effort

False success is the share of wrong patches accepted. False alarm is the share of correct patches rejected. Cost is the mean list price per review ([Table 3, arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)).

| Model | Effort | False success | False alarm | Cost |
|-------|--------|---------------|-------------|------|
| Opus 5.5 | low | .67 | .06 | $0.044 |
| Opus 5.5 | medium | .47 | .06 | $0.095 |
| Opus 5.5 | high | .45 | .06 | $0.120 |
| Sonnet 5.5 | low | .65 | .06 | $0.023 |
| Sonnet 5.5 | medium | .60 | .09 | $0.027 |
| Sonnet 5.5 | high | .49 | .09 | $0.047 |
| Haiku 5.5 | low | .78 | .06 | $0.0023 |
| Haiku 5.5 | medium | .64 | .20 | $0.0037 |
| Haiku 5.5 | high | .51 | .11 | $0.0078 |

The drop in false success from low to high passed the study's test for Opus and Haiku. Sonnet's missed its multiple-comparison threshold.

## Where medium is enough

For Opus, medium stayed within the preregistered 15-point margin of high (difference .018, 95% CI −.065 to .108). It cost 20% less than high by geometric mean, short of the 30% the authors had set as a material saving ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)).

For Sonnet and Haiku, medium cost 39% and 51% less than high but was not shown to be as good. The upper ends of the intervals reached .234 and .269, past the same margin ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)).

The authors call medium a sound default for an Opus 5.5 gate under similar conditions, and say that default does not carry over to the smaller models: with Sonnet and Haiku, high caught clearly more wrong patches than medium. For Haiku, they say their data point to high ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)). Anthropic's general advice differs for Haiku 5.5: [start with `medium`](https://platform.claude.com/docs/en/build-with-claude/effort) for most work, including agentic coding, and use `high` for longer agent tasks, among other cases.

Haiku at high cost about 8% as much per review as Opus at medium and rejected 27 of the 55 wrong patches against 29. The authors could not call it as good as Opus at medium, or worse. It also raised 4 false alarms against 2, returned 2 malformed verdicts, and ran three days later on a newer test harness. The authors say this motivates a confirmatory test rather than a switch ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)).

## What effort does not buy

All four points come from [arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1):

- A strong gate. Every setting accepted at least 45% of wrong patches, and the authors say such a gate complements tests rather than replacing them.
- A much cleaner merge stream. Assume 16.7% of incoming patches are wrong, the authors' count of passing Django patches that SWE-ABS tests reject. Then 83.3% are correct with no reviewer. Among patches Opus accepts, the authors compute 87.5% correct at low, 90.9% at medium, and 91.2% at high.
- A verdict that follows the feedback. Across the nine settings, 290 reviews accepted a wrong patch, and 111 of them named the tested defect anyway, per exploratory model coding with no human check. A gate that reads only pass or fail never sees that text.
- A usable verdict every time. In 270 reviews each, Sonnet returned 10 malformed verdicts and Haiku 5, so a gate on either needs a fallback.

## Why higher effort catches more

The study shows what came with more effort, not what caused the better verdicts. High produced more output tokens than medium on over 90% of patches in every model. Every review that used no thinking tokens returned a pass. In exploratory coding, the share of wrong patches rejected for the tested defect rose from low to high: .22 to .40 for Opus, .24 to .40 for Sonnet, and .16 to .31 for Haiku ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)). Anthropic documents that at lower levels Claude [can skip thinking entirely](https://platform.claude.com/docs/en/build-with-claude/effort) for simpler problems.

## When the numbers do not transfer

- The tests may be stricter than the issue. For 32 of the 55 wrong patches, a post hoc model coder judged that the issue does not require what the failing test checks. Without them, no model shows high beating low at the study's .025 level, or medium matching high ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)).
- Labels changed after data collection. The original labels give the same hypothesis decisions, but on them Opus agreed more with the labels at medium than at high, and Sonnet agreed most at low ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)).
- The sample is one repository, one prompt, public agent patches, one model family, and three of five effort levels. The authors say richer context, such as project review rules, may change the effect ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)).
- Opus often remembered the official fix. It accepted wrong patches more often on fully recalled issues than on partly recalled ones (.57 against .31 at high), an association only. The authors expect absolute rates may differ on new private code ([arXiv:2611.33639v1](https://arxiv.org/abs/2611.33639v1)).

## Example

In Claude Code, Opus 5.5, Sonnet 5.5, and Haiku 5.5 [default to `medium`](https://code.claude.com/docs/en/model-config#adjust-effort-level), so a Haiku gate left at its default runs below the level the study's data favor. Name the level in the gate command:

```bash
claude -p --model claude-haiku-5-5 --effort high "$REVIEW_PROMPT"
```

The same page documents settings that beat the flag. The `CLAUDE_CODE_EFFORT_LEVEL` environment variable takes precedence over `--effort`, and an effort cap lowers a higher request to the cap. Check both on the CI runner. The Claude API default differs: Sonnet 5.5 [defaults to `high`](https://platform.claude.com/docs/en/build-with-claude/effort) there.

## Key Takeaways

- For an Opus 5.5 gate in similar conditions, start at medium. High caught 1 more of 55 wrong patches than medium did.
- For Sonnet 5.5 or Haiku 5.5, set high explicitly, then confirm it on your own patches. The evidence is exploratory.
- Keep your tests behind the gate at any effort level.
- Log the feedback on passing reviews, and treat a malformed verdict as something other than a pass.
- Do not quote these rates as your gate's expected miss rate. They move with the tests that define a wrong patch.

## Related

- [Tunable Effort Levels for Code Review Agents](tunable-review-effort.md) — exposing review depth as a per-PR dial, once you know what each level buys
- [Effort as a Verification Dial: What a Higher Level Buys](../patterns/agent-design/effort-as-verification-dial.md) — the same setting on the producing side of the work
- [Treating a Resolved Task as a Defect-Free Change](../patterns/anti-patterns/resolved-task-as-defect-free.md) — why passing the task's tests leaves defects for review to find
- [Defect Visibility as the Unsupervised Review Boundary](../verification/defect-visibility-review-autonomy.md) — which changes to leave to agent review at all
- [Reproduce-Before-Report Verification Gate](reproduce-before-report-verification-gate.md) — checking a reviewer's findings, the false-alarm side of the gate
