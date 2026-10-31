---
title: "Treating Co-Loaded Agent Skills as Additive Rule Sets"
term: "Skill Takeover"
description: "With two same-job skills in one context, one skill's exclusive rules are followed and the other's are dropped. The closing worked example usually decides which; Phi-4-mini mainly follows load order."
tags:
  - anti-pattern
  - instructions
  - skills
  - tool-agnostic
  - arxiv
aliases:
  - skill takeover
  - co-loaded skill conflict
  - same-job skill rule loss
last_reviewed: 2026-10-28
maturity: emerging
---

# Treating Co-Loaded Agent Skills as Additive Rule Sets

> With two same-job skills in context, 45 to 78% of outputs follow one skill's exclusive rules and drop the other's entirely.

Skill takeover is the loss of a co-loaded skill's exclusive rules when a second skill for the same job sits beside it in the same context. On a benchmark of 16 same-job skill pairs, a skill's six rules were followed 93 to 99% of the time alone and 61 to 62% with a same-job skill loaded next to it ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). The readers were five open models (Qwen3-4B, Qwen2.5-7B, Mistral-7B, Llama-3.1-8B and Phi-4-mini) and two stronger models called through an API, Qwen3-235B and GPT-4.1. Most of what is lost conflicts with nothing in the other skill ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).

The loss is close to all or nothing. "The outputs are rarely blends: in 45 to 78% of outputs, one skill's exclusive rules are all followed and the other skill's are all dropped" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). One side of a genuine contradiction has to lose, and that explains little of it: on the five rules per skill that can always hold together, the drop was still 28 to 35 points.

## When it applies

Three conditions have to hold before an audit is worth the time.

- Both skill bodies are in the context at once. Both files sat in the system prompt, so file selection played no part: "Takeover happens after both files are loaded, so better skill selection would not fix it" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). The [selection-stage failure](silent-skill-substitution.md) has its own fix.
- The two skills claim the same job. A skill for a different job changed nothing: "Adding a skill for a different job changes nothing, so a longer context is not the cause" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).
- The two rule sets govern the same part of the output. Where they constrain different parts of one artifact, the models blend them: takeover was at most 19% on every model for SQL queries ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).

## Why it works

The worked example usually decides the winner. Phi-4-mini is an exception: it follows the second-listed skill in almost every takeover. A skill file is a list of rules, often followed by one worked example of a finished output ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). Each example demonstrates one skill's format, so the model writes in that format and the other skill's rules go unwritten: "Each example shows an output that follows one skill only, and the model writes in that format" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).

Three tests isolate the example rather than the file boundary. On the five open models and Qwen3-235B, takeover ran 45 to 78% with the examples and 7 to 41% once they were removed from both files. Putting both complete files, examples included, into a single file left takeover at 34 to 73%. And when only one skill kept its example, that skill "wins 67 to 93% of the takeovers over both load orders, and moving the example to the other skill moves the winner with it" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). The source adds: "The one exception is Phi-4-mini, which follows the second-listed skill in almost every takeover." Camassa and Shiller call the related pattern-over-instruction effect induction pressure. Their study uses hardcoded conversation turns rather than skill files ([arXiv:2605.20382v3](https://arxiv.org/abs/2605.20382v3)).

Which skill wins is a property of the pair and the load order, not of the request. The first-listed skill won 74 and 77% of takeovers on Llama-3.1-8B and GPT-4.1, 24% on Qwen2.5-7B and 3% on Phi-4-mini. The authors conclude: "A user who does not control the load order cannot know which skill will be followed" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).

## What does not fix it

Naming the winner in a line of prose is the reflex, and it buys nothing. With a priority instruction, "the achievable rules followed stay at 62 to 71%, close to what following one skill alone gives, and one skill still takes over in 36 to 82% of outputs" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). Following one skill alone already scores 60% there.

Telling the model the skills are complementary works part way, and only on the stronger readers. Qwen3-235B and GPT-4.1 reached 88 to 89% of achievable rules with no takeover. Both entangled rules held in only 38 and 32% of outputs. About one output in five was fully correct ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). The five open models reached 69 to 78% and still showed takeover in up to 46% of outputs.

## What to do

1. Read the example at the end of each skill file before you read its rules. That is where an audit starts.
2. Give both files the same closing example, one that satisfies both rule sets. Two unmerged files each ending in such an example brought takeover down to 1 to 15% and achievable rules to 90 to 96% across the six models tested. It raised fully correct outputs on the two strong models from 1% to 76 and 60% against 22 and 21% for the complementary-skills instruction ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).
3. Better still, merge the pair into one file using the strongest model you have. Files merged by Claude Opus 5.5 reached 96 to 99% of achievable rules on all seven reader models with no takeover ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). The authors' own instruction: "The merged file should end with one correct worked example that follows both skills, and it should not copy the examples of the source skills" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).
4. Check the merged example against both rule sets before you save the file. A correct example added 12 to 17 points of achievable rules and an incorrect one added little or nothing; the source skills' original examples, pasted into a merged rule list, cost 0 to 14 points and brought takeover back to 32 to 55% ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).
5. Do not reach for a structured merge prompt to compensate for a weaker model. "Structure helps only when the labels are right, and only the strongest merger got them right" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).

## Example

The benchmark's commit-message pair sets `conventional-commits` against `ticket-first-commits`. Skill A wants a subject starting with a conventional-commit type such as `feat:`, a `Why:` line, a `Risk:` line, a `BREAKING CHANGE:` line, a `Tested:` line, and `Signed-off-by:` as the last line. Skill B wants a subject starting with the ticket, a body of two or more bullets, `Component:` and `Rollback:` lines, the same `Tested:` line, and a `Refs:` trailer. Only the two subject lines genuinely conflict.

With both files loaded, Qwen3-4B "follows all six rules of B and only the shared rule of A, in either load order". The `Why:`, `Risk:` and `BREAKING CHANGE:` lines are gone, although nothing in B asks for their omission. Given one merged file written by Claude Opus 5.5 with A as the primary, the same model produced an output following all ten achievable rules ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).

## When this backfires

- The dropped rules do not change your outcome. SWE-Skills-Bench found 92 of 98 public skills had no statistically significant effect. Adding skills raised the average pass ratio from 76.6% to 76.9% ([arXiv:2603.15401v2](https://arxiv.org/abs/2603.15401v2)). Task-quality gains need separate measurement from the rule fidelity measured by the takeover benchmark.
- You have no strong model to write the merge. Self-merges reached 71 to 95% of achievable rules, 5 to 25 points below the Claude Opus 5.5 files, and a step-by-step merge by a self-merger was level with or below its own plain merge ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).
- You cannot check the result. "Checking a merge on real skills also needs a judge model or hand-written checks, since real skills come without rule checkers" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).
- You expected removing the examples to be enough. The researchers also stripped out contradictory and entangled rules. Four of six models still followed both skills' exclusive rules in full 24 to 33 points less often than their single-skill runs predicted: "two skills for the same job can get in each other's way even when none of their rules conflict" ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)).
- Blocking one skill is enough for you. [Denying the rival skill's first read](silent-skill-substitution.md) switched the model to the installed skill in 96% of 179 cases ([arXiv:2610.11647v2](https://arxiv.org/abs/2610.11647v2)), needs no merge artifact, and costs only the rules of the skill you did not want.

The evidence is one v1 preprint. Its authors wrote 16 skill pairs with planted rule relations, "so that we control how their rules interact". Claude Opus 5.5 appears only as the merge author, never as a reader model ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). The real-skill check reanalyzes another study's public run summaries. Claude Code runs using both skills met first-skill-only requirements about 8 points less often than paired single-skill runs ([arXiv:2610.25064v1](https://arxiv.org/abs/2610.25064v1)). A competing pipeline reconciles co-loaded skills offline through typed, scoped constraints, with a classifier for interaction types and an adversarial verifier for uncertain judgments ([arXiv:2610.15481v1](https://arxiv.org/abs/2610.15481v1)).

## Key Takeaways

- A same-job skill cuts the share of a skill's rules that are followed by about a third; an unrelated skill changes nothing, so context length is not the cause.
- When only one skill keeps its closing example, that skill wins 67 to 93% of takeovers, except on Phi-4-mini. Phi-4-mini follows the second-listed skill in almost every takeover.
- A priority line leaves achievable rules followed at 62 to 71% against a 60% do-nothing floor, so naming a winner is not a fix.
- A file merged by the strongest model on hand, ending in one example that satisfies both rule sets, reached 96 to 99% of achievable rules on all seven reader models; a self-merge reached 71 to 95%.
- A wrong example is worth roughly nothing, so verify the merged example against both rule sets before shipping the file.

## Related

- [Silent Skill Substitution When Same-Job Skills Co-Install](silent-skill-substitution.md) — the selection-stage half, where the rival skill runs and your skill's body never loads at all
- [Example-Driven vs Rule-Driven Instructions](../../instructions/example-driven-vs-rule-driven-instructions.md) — when an example beats a rule, which is the same force that drives takeover
- [Agent Extension Conflicts: When Installed Skills and MCP Servers Fight Each Other](agent-extension-conflicts.md) — the wider composition failure across skills, servers, and context budget
- [Assuming Loaded Skills Stay Enforced in Long Contexts](assuming-loaded-skills-stay-enforced.md) — a single loaded skill shedding its own requirements as the run grows
- [Skill Over-Trust: Treating Topical Relevance as Evidence a Skill Helps](skill-over-trust.md) — attributing a regression to one skill by re-running the task with it withheld
