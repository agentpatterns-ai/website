---
title: "Agent-File Instruction Coverage Does Not Determine Cost or Necessarily Improve Correctness"
term: "Instruction-Category Coverage"
description: "Across 310 generated library variants, the number of instruction categories in an AGENTS.md did not determine its generation cost and did not necessarily improve the correctness of code written from it."
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - instruction category coverage
  - agent file category selection
  - AGENTS.md instruction categories
last_reviewed: 2026-10-18
maturity: emerging
---

# Agent-File Instruction Coverage Does Not Determine Cost or Necessarily Improve Correctness

> Instruction-category count did not determine generation cost and did not necessarily improve the correctness of generated code.

Stop budgeting an agent file by how many kinds of instruction it covers. Across 310 generated variants, category count did not determine token usage and did not necessarily improve correctness. Its per-category rankings come from one reconstruction per condition and do not establish which category to remove.

## The conditions this holds under

The measurement comes from five trivial Python libraries, two models, one agent harness (OpenCode), one task type, and "one reconstruction run per condition" ([Polandra et al., 2026](https://arxiv.org/abs/2610.21421v1)). The study built all 31 non-empty combinations of five categories (Repository Overview, Function Description, Implementation Detail, Testing, Reconstruction Steps). That produced 310 agent files, and one library reconstruction from each.

Inside that setting:

| What was measured | Result |
|---|---|
| Token cost of generating the agent file | "the number of instructions alone does not determine token usage for agent-file generation, with substantial variation across models and libraries" |
| Compilability of the generated library | "largely insensitive to the instruction categories" — 88.39% for Gemma 4, 98.06% for GPT-5.4 |
| Full test pass against the original suites | 0% of Gemma 4 variants, "12.99% successfully passed all human-written test cases" for GPT-5.4 |
| Effect of adding categories | Top scores "were achieved using only one-, two-, or three-category combinations" |

The per-model winners are the part not to act on. The authors report rates over every combination containing a category, rather than single-category files alone. On that basis Function Description led Gemma 4's partial-pass rate and Reconstruction Steps led GPT-5.4's full-pass rate, but "their advantage over the next-best category was only 1.25% for Gemma 4 and 3.75% for GPT-5.4". These are descriptive differences from one reconstruction per condition, without repeated-run estimates of ranking stability.

## What the studies establish

Polandra et al. measure compilability through Python bytecode compilation. That checks syntax and basic module-level cohesion, rather than functional correctness ([Polandra et al., 2026](https://arxiv.org/abs/2610.21421v1)).

A separate 288-run study finds that its agents fail on implementation skill rather than missing repository knowledge. Its equivalence bounds apply to its own tasks and context-injection strategies, not Polandra's category comparisons ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)). This offers a possible explanation to test, not a causal explanation of the reconstruction results.

Instructions can change behavior without improving performance. Gloaguen et al. report that "instructions in the context files are well followed by coding agents" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v3)).

## What stays actionable

Drop any instruction category that restates what the agent can discover for itself, and keep what it cannot infer. The authors' own advice: "users should include instructions that are relevant to the target reconstruction or code-generation objective rather than attempting to include every available instruction". Gloaguen et al. separately report that "repository overviews, although popular and recommended by model providers, are not helpful" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v3)). Polandra's results do not support a general low ranking for Repository Overview. It ranks second for Gemma 4 partial passes and second-lowest for GPT-5.4 full passes ([Table VI](https://arxiv.org/abs/2610.21421v1)).

## When this backfires

- Re-tuning the category mix on each model upgrade. The winners differ by model at single-digit margins from one run each, so repeated trials are needed before treating the ranking as stable.
- Cutting a category to save tokens. Token usage did not track category count, so a cut aimed at cost can delete the one non-inferable instruction and move cost in neither direction.
- Judging an agent file on whether the result builds. Compile rates reached 88.39% and 98.06% while full-pass rates were 0% and 12.99%, so compilability barely varied with category.
- Reading the category ranking as causal. The authors note that generated files "may include information associated with other instruction categories, even when agents are instructed to generate only a single category", which "can blur the isolated effect of each category".
- Generalizing past library reconstruction. The authors name bug fixing and code refactoring as tasks where the effect of a category may differ, and they tested neither, nor another harness or language ([Polandra et al., 2026](https://arxiv.org/abs/2610.21421v1)).

## Key Takeaways

- Generation cost tracked the model and the target repository, not the file: "the instruction combination is less influential on token usage than the LLM and target-library characteristics"
- The highest correctness scores came from one-, two-, and three-category files, not from the five-category file
- Repeat category comparisons on your own tasks before using a descriptive ranking to remove instructions
- Judge an agent file on tests rather than on whether the build succeeds, since compilability barely varied with category
- The transferable rule is relevance: cut what the agent can discover, keep what it cannot infer

## Related

- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — the file-level evidence on presence, absence, and cost; this page works one level down, inside the file
- [Knowledge Gap or Skill Gap: Triage Before Writing Context](knowledge-gap-vs-skill-gap-triage.md) — the failure-mode triage that supplies the mechanism here
- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md) — the structural answer to a file that grew by accumulating categories
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why faithful compliance with more instructions produces more work rather than better results
- [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md) — the test for which facts belong in an agent file at all
