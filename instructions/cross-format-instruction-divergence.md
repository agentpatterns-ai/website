---
title: "Divergent Rules Across Coexisting Agent Instruction Files"
description: "In 386 sampled section pairs from multi-format repos, 16.1% gave divergent guidance. Consolidate first, then compare same-scope sections by topic."
term: "Cross-Format Instruction Divergence"
aliases:
  - instruction file divergence
  - AGENTS.md and CLAUDE.md drift
tags:
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-05
maturity: emerging
---

# Divergent Rules Across Coexisting Agent Instruction Files

> In a 1,000-repository study, 16.1% of sampled same-topic section pairs across coexisting agent instruction files gave divergent guidance, and none contradicted outright.

When one repository keeps both an `AGENTS.md` and a `CLAUDE.md`, or adds Copilot or Cursor rules beside them, the copies of a rule can drift apart. Consolidate to one file where every tool you use can read it. Where two files must stay, compare their sections paired by topic, not by heading, and only where both sections apply to the same scope.

## What the study measured

An empirical study of 3,387 instruction files from 1,000 GitHub repositories put numbers on the drift ([Toward an Evidence-Based Template for Agent Instruction Files, arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)). The repositories were sampled at random, 500 above and 500 below the median star count of the AIDev dataset.

"Among repositories containing at least one instruction file, 42.2% of the higher-popularity cohort and 21.6% of the lower-popularity cohort contain two or more formats" ([arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)). The most common pair was `AGENTS.md` with `CLAUDE.md`, in 231 repositories.

The authors then sampled 386 pairs of sections that covered the same category in different formats of one repository. Two annotators labeled each pair (Cohen's kappa 0.85):

| Label | Pairs | Share |
|---|---|---|
| Same guidance, different words | 126 | 32.6% |
| Compatible, complementary | 198 | 51.3% |
| Divergent | 62 | 16.1% |
| Contradictory | 0 | 0.0% |

A pair counts as divergent "if an agent following one section would behave differently from one following the other" ([arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)).

Read the 16.1% with its scope caveat. Only 186 pairs (48.2%) shared the same repository-wide or directory scope, and 193 (50.0%) belonged to different directories or components. The authors conclude that "observed divergence may reflect legitimate component-specific requirements rather than inconsistent instructions" ([arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)).

## Why it works

When tools load different files, a rule changed in one file changes one agent's behavior. Claude Code makes this concrete: by default, with an `AGENTS.md` and a `CLAUDE.md` both present, it reads "Your `CLAUDE.md` files only" ([Claude Code memory docs](https://code.claude.com/docs/en/memory)). Under that default, a command fixed in `AGENTS.md` never reaches Claude Code.

The stale copy goes unnoticed because the sections do not share names. For coexisting `AGENTS.md` and `CLAUDE.md` files, the median category-level Jaccard similarity was 0.929 and the median heading-level Jaccard was 0.273 ([arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)). The files cover the same topics under different headings, so "there is no obvious heading-level signal that a differently-named section in a sibling file covers the same topic and may need the same update." Pairing by topic closes that gap, and filtering by scope keeps the differences that are correct.

## How to run the check

1. Consolidate where you can. Claude Code documents an `@AGENTS.md` import in `CLAUDE.md` that keeps `AGENTS.md` "the one file every tool shares" ([Claude Code memory docs](https://code.claude.com/docs/en/memory)).
2. For the files that remain, map each section to a topic: build, test, code style, Git conventions, and so on. Do not match on heading text.
3. Drop pairs whose sections apply to different directories or components.
4. For each remaining pair, ask the paper's question: would an agent following one section act differently from an agent following the other? Fix those pairs.
5. Repeat when a build, test, or convention changes. The paper proposes this trigger and labels it one of its "practical recommendations informed by our observations rather than experimentally validated interventions" ([arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)).

## When this backfires

- Files scoped to different components. Half the sampled pairs differed in scope, and a check that ignores scope flags correct differences as drift.
- Repositories that can use one file. An import or symlink removes the second copy. On Windows, use the import: a committed symlink needs Administrator privileges or Developer Mode, and otherwise Git checks it out as a plain text file ([Claude Code memory docs](https://code.claude.com/docs/en/memory)).
- Treating text differences as conflicts. Most pairs (51.3%) were compatible but carried different information. The authors note that "consolidating instruction files requires attention to complementary information" ([arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)), so a careless merge deletes detail one tool needed.
- Expecting a measured payoff. The paper does not test whether divergence changes outcomes. It lists "evaluating how instruction quality affects downstream coding-agent performance" as future work ([arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)). Gloaguen et al. report that "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v2)), so fixing divergence may not move results ([Evaluating AGENTS.md](evaluating-agents-md-context-files.md)).

## Example

The paper's motivating case is Dawarich, a Ruby on Rails app with both files at its root ([arXiv:2611.02383v1](https://arxiv.org/abs/2611.02383v1)). The live files still disagree.

[`AGENTS.md`](https://github.com/Freika/dawarich/blob/master/AGENTS.md) sends JavaScript to Prettier:

```markdown
- `bundle exec rubocop` / `npx prettier --check app/javascript` — enforce formatting before commits.
```

[`CLAUDE.md`](https://github.com/Freika/dawarich/blob/master/CLAUDE.md) sends it to Biome:

```markdown
- **Always run Biome** on modified JS/CSS files before committing: `npx @biomejs/biome check --write <files>`
```

Both sections are repository-wide and share the code style topic, so the pair passes steps 2 and 3. An agent following one runs a different tool from an agent following the other, so it fails step 4. With default settings, Claude Code reads only `CLAUDE.md` here and runs Biome. A tool that reads only `AGENTS.md` runs Prettier.

## Key Takeaways

- Pair sections by topic. In the median `AGENTS.md` and `CLAUDE.md` pair, fewer than one in three section headings used the same wording.
- Filter by scope before you call a difference drift; half the sampled pairs applied to different components.
- An `@AGENTS.md` import in `CLAUDE.md` leaves one shared copy, so only the Claude-specific lines below the import remain to check.
- The 16.1% figure is annotator-judged divergence, with zero contradictions and no measured effect on agent outcomes.

## Related

- [Project Instruction File Ecosystem](instruction-file-ecosystem.md) — which tool reads which file, and the convergence strategies
- [Frontmatter and Body Rule Drift in Agentic Workflows](frontmatter-body-rule-drift.md) — the same two-copy drift inside one workflow file
- [@import Composition Pattern for Agent Instruction Files](import-composition-pattern.md) — composing one instruction file from shared parts
- [Agent Context File Evolution](agent-context-file-evolution.md) — instruction files as maintained configuration code
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — the evidence on whether instruction files help at all
