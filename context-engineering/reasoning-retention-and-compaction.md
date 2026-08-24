---
title: "Reasoning Retention and Compaction as Harness Settings"
term: "Reasoning Retention"
description: "Whether a harness keeps private reasoning across tool calls and compacts instead of truncating decides how much of an agent's measured ability belongs to the model."
aliases:
  - reasoning retention across tool calls
  - compaction over truncation
tags:
  - context-engineering
  - agent-design
  - evals
  - tool-agnostic
last_reviewed: 2026-08-01
maturity: adopted
status: current
---

# Reasoning Retention and Compaction as Harness Settings

> A harness that keeps private reasoning across tool calls and compacts instead of truncating changes measured agent performance, sometimes by multiples.

Two harness settings decide how much of an agent's thinking survives between actions: whether private reasoning is passed back with each tool result, and whether old context is summarized or deleted. Both are harness configuration, independent of the model itself. When a harness discards reasoning, the agent rebuilds its understanding of the task from scratch every turn.

## How much you gain depends on what you currently discard

Read the headline numbers below as a ceiling rather than an expectation: they measure what a maximally lossy harness was giving up.

The extreme case is ARC-AGI-3, a benchmark of unfamiliar 2D puzzle games. Its harness discarded all private reasoning after every game action and used a rolling truncation window that dropped the oldest messages once the conversation passed 175,000 characters (OpenAI's reproduction used 175,000 tokens, which it reports as near-equivalent because this benchmark's text is mostly 1:1-tokenized action grids). Against that harness as the baseline, retained reasoning and compaction moved GPT-5.6 Sol from 13.3% to 38.3% on the ARC-AGI-3 public set while cutting output tokens sixfold — roughly 3x, on a metric (relative human action efficiency) whose estimated human average is 48% ([OpenAI, 2026](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores)).

Where a harness is otherwise reasonable, the same change is worth only a few points, well short of the multiples above. An independent study measured retained thinking history improving two small open models, Qwen3-4B and Qwen3-8B, by roughly 3 to 5% on the BFCL multi-turn category, and generalizes the result only as far as "reasoning models" ([Liu et al., 2026](https://arxiv.org/abs/2606.00135v2)). Two small models are not a population, but that is the closest thing to a controlled measurement of the setting on its own — where the 3x figure measures how much one benchmark harness was throwing away.

## Two independent settings

Reasoning retention governs what the model thought. Compaction governs what the model saw. You can enable either without the other, and they fail differently.

| Setting | What is lost when it is off | Where it lives |
|---|---|---|
| Reasoning retention | The plans behind past actions, so the agent re-derives them | Responses API: pass the previous response ID, which retains reasoning across tool calls and turns ([OpenAI](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores)). Claude API: pass thinking blocks back complete and unmodified with tool results ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/thinking)) |
| Compaction instead of truncation | The oldest observations, deleted rather than summarized | [Responses API compaction](https://developers.openai.com/api/docs/guides/compaction); [Claude API compaction](https://platform.claude.com/docs/en/build-with-claude/compaction) (beta) |

Retention is not always a setting you control directly. On the Claude API the default is per model: Claude Opus 4.5 and later Opus models, Claude Sonnet 4.6 and later Sonnet models, Claude Fable 5, and the Claude Mythos models keep every prior turn's thinking blocks, while earlier Opus and Sonnet models and all Haiku models through 4.5 keep only the last turn ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/thinking)). Two agents on the same code and the same provider can therefore retain different amounts of reasoning purely because of the model string.

## Why it works

The reasoning trace is where the working hypothesis lives, and a log of past actions does not reconstruct it. A harness that strips it leaves the agent able to see its past moves and short notes but not "the plans, insights, or thoughts that led to them" ([OpenAI, 2026](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores)). Re-deriving that hypothesis every turn is what the output-token count measures, which is why holding more input context produced fewer output tokens.

Anthropic states the same causal claim as an API requirement rather than a tuning option: thinking blocks "capture the step-by-step reasoning that led to the tool requests," and passing them back lets the model "continue reasoning from where it left off," because a tool-use loop is one continuous assistant turn interrupted by external calls ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/thinking)). Compaction's mechanism is separate: truncation deletes early observations, while [summarizing them](context-compression-strategies.md) carries what the agent learned into later turns.

## When this backfires

- The agent locked onto a wrong hypothesis. ARC Prize's analysis of the same benchmark saw Opus 4.7 harden a mislabeled read of a mechanic into a fixed rule, after which "the run never recovered" ([ARC Prize, 2026](https://arcprize.org/blog/arc-agi-3-gpt-5-5-opus-4-7-analysis)). That run used the standard reasoning-discarding harness, so it does not measure retention's cost — but it shows the failure retention would preserve as faithfully as an insight.
- History is already the bottleneck. On models that keep every prior turn, retained thinking counts as input like any other history and consumes the window, which is why Anthropic ships a thinking-block clearing strategy to override the default ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/thinking)).
- You switch models mid-conversation. Thinking blocks belong to the model that produced them; other models ignore them silently while still billing the input tokens ([Anthropic](https://platform.claude.com/docs/en/build-with-claude/thinking)).
- Long multi-turn work amplifies early mistakes. Across more than 200,000 simulated conversations, models dropped 39% on average from single-turn to multi-turn performance across six generation tasks, partly by relying too heavily on previous incorrect attempts ([Laban et al., 2025](https://arxiv.org/abs/2505.06120v1)).
- Compaction inherits summarization loss. Replacing a hard cut-off with a summary trades one failure mode for [objective drift and compounding error across cycles](context-compression-strategies.md).
- Benchmark comparisons need the untuned harness. ARC's generic harness exists because a simple harness makes model shortcomings visible and comparisons fair; tuning your own harness raises your score and turns the comparison into a harness comparison ([OpenAI, 2026](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores)).

## What this means for reading benchmarks

Any leaderboard row measures a model and a harness together. The paper that measured retained thinking history also found that results are "highly sensitive to seemingly minor, often undocumented implementation choices," including how prior reasoning history is carried forward, and concluded that "without rigorous standardization, leaderboard rankings are unreliable" ([Liu et al., 2026](https://arxiv.org/abs/2606.00135v2)). Before attributing a score gap to model quality, check whether both runs retained reasoning and how each handled context overflow — a caveat that generalizes past the two settings here to [everything an eval fails to observe](../verification/eval-blind-spots.md).

Apply the same caution to this page's own numbers. The ARC-AGI-3 result is a 2D puzzle-game benchmark scored on relative human action efficiency, a different domain from a coding benchmark ([OpenAI, 2026](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores)); the direction of the effect is corroborated on tool-calling tasks, but the magnitude there remains unconfirmed.

## Example

The two harnesses that produced the ARC-AGI-3 result, described as the per-action message flow.

**Before** — reasoning discarded, context truncated:

```text
turn N:   [system] + [past actions + short notes] + [current frame]
          -> model thinks from scratch -> action
          reasoning discarded after the action
overflow: conversation exceeds the 175,000-character window
          -> oldest messages deleted, early observations gone
```

**After** — reasoning retained, context compacted:

```text
turn N:   previous response ID
          -> prior reasoning and tool calls carried forward automatically
          -> model continues its existing hypothesis -> action
overflow: compaction summarizes older history in place
          -> what the agent learned early survives into later turns
```

The only differences are which prior content the harness sends back and what it does at the overflow boundary; neither changes the model, the prompt, or the tools ([OpenAI, 2026](https://openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores)).

## Key Takeaways

- Reasoning retention and compaction are separate settings: audit both when reviewing a harness config, since turning on one leaves the other at its default.
- Where a harness is already reasonable, the one controlled measurement available reports single-digit gains on small open models; expect multiples only where the harness was discarding reasoning outright.
- Retention costs context on models that keep every prior turn, so budget for it, and watch for a hypothesis that locks in early and never gets revisited.
- On the Claude API, whether prior thinking stays in context is a per-model default: check the model string before assuming two agents on the same harness retain reasoning the same way.
- Treat every benchmark score as a model-plus-harness measurement, and check both runs' context settings before reading a gap as capability.

## Related

- [Context Compression Strategies](context-compression-strategies.md) — the tiered offload-then-summarize approach that compaction belongs to
- [Manual Compaction as Dumb Zone Mitigation](manual-compaction-dumb-zone-mitigation.md) — compacting on reasoning quality rather than at a fill threshold
- [Agent-Initiated Rubric-Gated Self-Compaction](agent-initiated-self-compaction.md) — letting the agent choose the compaction moment from trajectory structure
- [Eval Blind Spots](../verification/eval-blind-spots.md) — what a benchmark cannot observe about the system it scores
- [Consistent Capability Fallacy](../fallacies/consistent-capability-fallacy.md) — why a benchmark result does not transfer unchanged to your codebase
