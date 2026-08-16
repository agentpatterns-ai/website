---
title: "Purpose-Built Eval Suites for Model and Harness Swaps"
term: "Purpose-Built Eval Suite"
description: "Build a small eval suite over your own tasks to compare models, prompts, and harnesses — but size it to the decision before you trust the ranking it produces."
tags:
  - testing-verification
  - evals
  - cost-performance
  - tool-agnostic
  - arxiv
aliases:
  - small eval suite
  - local eval suite
  - custom eval suite
last_reviewed: 2026-08-16
maturity: emerging
---

# Purpose-Built Eval Suites for Model and Harness Swaps

> A purpose-built eval suite scores your model, prompt, and harness together, answering a question no public leaderboard can answer for you.

A purpose-built eval suite is a small set of tasks taken from your own workload, run against named configurations of model, prompt, and harness, and scored by graders you wrote. Build one when you have a specific swap to decide and the closest public benchmark was measured on someone else's setup. Do not build one to have a scoreboard.

## Conditions that make it worth building

Four conditions have to hold before the output means anything:

- You have a named decision. Two or more configurations, one question, and an answer you will act on.
- You have real traces to draw tasks from. Husain and Shankar put the minimum viable setup at 30 minutes reviewing 20 to 50 outputs whenever you make a significant change, and name model switches and prompt updates as triggers to repeat it ([Husain and Shankar, 2026](https://hamel.dev/blog/posts/evals-faq/)). The failure categories that review surfaces are what your tasks should encode.
- You can afford repeat runs. Measurement reliability converges by 8 to 16 trials on structured tasks, but needs 32 or more on complex reasoning ([Mustahsan and others, 2025](https://arxiv.org/abs/2512.06710v1)).
- You can check your grader against human labels. A grader nobody has validated ranks configurations by how well they please an unmeasured judge.

Miss any of them and the suite returns a number you cannot act on.

## Why it works

A benchmark score measures a model, a prompt, and a harness jointly. It never measures the model alone. OpenAI puts it directly: "Benchmarks rarely measure AI models in isolation. They also measure less visible choices about API settings, harness design, and prompting." Turning on retained reasoning and compaction moved GPT-5.6 Sol from 13.3% to 38.3% on the ARC-AGI-3 public set, with no change of model ([OpenAI, 2026](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores)). Microsoft finds the same effect in the machine around the agent. It names the operating system and shell, absolute file paths and user identity, language server feedback, and silent tool version updates as hidden variables. "Each one introduces a few points of variance on its own, but run your eval on a different machine [...] and the cumulative effect can be large enough to swallow the signal" ([Microsoft, 2026](https://developer.microsoft.com/blog/the-hidden-variables-in-your-agent-eval/)). A published delta therefore describes someone else's configuration, and the only way to get a number about yours is to hold your setup fixed and vary one factor inside it.

The smevals tool makes that unit explicit and calls it a config: each one "specifies a model to be evaluated, but may also include other parameters to test, such as different system prompts, model parameters, or agent harnesses" ([Prime Radiant, 2026](https://primeradiant.com/blog/2026/smevals.html)). Running and grading are separate commands, so `smevals grade . --regrade` rescores runs you already paid for once you improve a checker ([Prime Radiant, 2026](https://primeradiant.com/blog/2026/smevals.html)). That separation is what keeps a suite cheap enough to keep changing as your harness changes.

## Sizing the suite to the decision

Add repeat runs before you add tasks. Paired prediction noise typically exceeds paired data noise across many evals, so averaging repeated runs raises statistical power more than sampling extra questions does ([Wang, 2026](https://arxiv.org/abs/2512.21326v2)).

Then read the output as a screen, not a verdict. Central-limit intervals "usually dramatically underestimate uncertainty" below a few hundred datapoints ([Bowyer, Aitchison and Ivanova, 2025](https://arxiv.org/abs/2503.01747v3)), so a six-task suite has no defensible error bar. Ranking is no safer. A reanalysis of a public comparison of nine models on MMLU found that "3 of the 8 adjacent leaderboard-rank gaps are not statistically significant after correcting for the 36 pairwise comparisons the ranking implies" ([Chandrahas, 2026](https://arxiv.org/abs/2607.04429v1)). Your suite has fewer items than that one and inherits the same problem. Use it to reject configurations that fail outright, and read outputs by hand when two configurations land close together.

## When this backfires

- The suite is sized below the decision. A handful of tasks run once cannot resolve the small differences you are usually choosing between ([Mustahsan and others, 2025](https://arxiv.org/abs/2512.06710v1)).
- The tasks saturate. Benchmarks saturate quickly, "making it difficult to differentiate models and diminishing their long-term value" — nearly half of 60 language model benchmarks studied showed it, at rates increasing with age ([Akhtar and others, 2026](https://arxiv.org/abs/2602.16763v3)). Retire tasks once they stop separating configurations.
- The grader goes unvalidated. A checker can call another model to judge a run ([Prime Radiant, 2026](https://primeradiant.com/blog/2026/smevals.html)), which moves the measurement problem rather than solving it.
- You tune prompts against the same fixed tasks. The suite becomes the optimization target, which is the held-out gap covered in [Eval Blind Spots](eval-blind-spots.md).
- You have no representative workload yet. Tasks you guessed at are a public benchmark with worse statistics, and the honest alternative is structured error analysis on real traces ([Husain and Shankar, 2026](https://hamel.dev/blog/posts/evals-faq/)).

## Example

The worked smevals suite is deliberately tiny: a directory of seven files with two tasks, one config, one grader, one checker, and a runner script ([Prime Radiant, 2026](https://primeradiant.com/blog/2026/smevals.html)).

```
haiku/
├── eval.yaml
├── tasks/
│   ├── pelican.yaml
│   └── otters-in-love.yaml
├── configs/
│   └── default.yaml
├── graders/
│   └── default.yaml
├── checkers/
│   └── three-lines
└── run-llm
```

Run it against several models, then grade separately:

```bash
uvx smevals run . -g -m gpt-5.5 -m gpt-5.4-nano
uvx smevals grade . --regrade
```

The first grader only checked that the output had exactly three non-empty lines. A second checker, added later, used a model to score syllable counts and subject fidelity against a 0.8 pass threshold ([Prime Radiant, 2026](https://primeradiant.com/blog/2026/smevals.html)). The regrade step applied that new checker to the runs already collected, so a better grader cost nothing to re-run the models under test.

Simon Willison covers the same tool in a practitioner write-up ([Willison, 2026](https://simonwillison.net/2026/Jul/31/smevals/)).

LangChain publishes the benchmark setup it runs against its own deep agents, with tasks in coding, conversation, and retrieval ([LangChain, 2026](https://www.langchain.com/blog/how-we-benchmark-deep-agents)). The suite gates whether a change ships.

## Key Takeaways

- Build a purpose-built suite when you have a named swap to decide and no public benchmark was measured on your setup.
- Treat the model, prompt, and harness as one configuration, because a score measures all three together.
- Separate running from grading so improving a grader does not mean re-running the tasks.
- Buy statistical power with repeat runs before extra tasks.
- Read a small suite as a screen that rejects bad configurations, never as a ranking you can defend.
- Retire tasks once every configuration passes them.

## Related

- [Benchmark-Driven Tool Selection for Code Generation](benchmark-driven-tool-selection.md) — choosing a realistic public benchmark, the decision upstream of building your own
- [Comparative Judging for Agent Configuration Ranking](comparative-judging-config-ranking.md) — how to rank configurations once your scores are noisy
- [Eval Blind Spots: Structural Gaps in Measurement Methodology](eval-blind-spots.md) — the held-out gap you create by tuning against a fixed suite
- [Decomposing Agent Output Variability by Layer](sampling-state-agent-variability-layers.md) — which layer the run-to-run noise in your suite comes from
- [Benchmark Contamination as Eval Risk](benchmark-contamination-eval-risk.md) — why public scores drift from real capability over time
- [Head-to-Head Evaluation of Competing MCP Servers](head-to-head-mcp-server-evaluation.md) — a worked instance where the configuration under test is a tool server, and the quality axis ties
- [AX Evals: Measure the Agent-Facing Surface, Not the Model](ax-evals-agent-facing-surface.md) — the inversion: hold the configuration fixed and vary your own product's agent-facing surface instead
