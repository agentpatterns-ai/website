---
title: "Plugin Component Co-Change: Scripts and Their Instructions Move Together"
term: "Plugin Component Co-Change"
description: "Inside a Claude Code plugin, a bundled script and the markdown describing it form one interface. Pair the edits where the prose carries operational detail, and strip the prose where it does not."
aliases:
  - intra-plugin co-change
  - script-markdown coupling
  - plugin component coupling
tags:
  - instructions
  - skills
  - human-factors
  - claude
  - arxiv
last_reviewed: 2026-09-02
maturity: emerging
---

# Plugin Component Co-Change: Scripts and Their Instructions Move Together

> Inside one plugin, a bundled script and the markdown describing it are two halves of one interface. Change one and the other misleads.

Pair the edit when the markdown states how the script behaves: its flags, its output shape, the conditions for reaching for it. Where the markdown names only when to invoke and never restates the implementation, there is nothing to pair, and the better move is to keep it that way.

## What the co-change data shows

Hereiz et al. mined 1,926 repositories holding 8,351 plugins across 2,018 marketplaces, covering 77,773 plugin-touching commits from the October 2025 launch through a cutoff at the end of March 2026, on repositories discovered 2 April 2026 ([arXiv:2608.28497v1](https://arxiv.org/abs/2608.28497v1)).

The headline result is a negative one, and it is why this page is scoped to a single directory: "Most component types evolve independently, but within skills directories, natural-language instruction files and implementation scripts co-evolve at above-chance rates" ([arXiv:2608.28497v1](https://arxiv.org/abs/2608.28497v1)). Skills do co-change with everything — "at least 43.2% of pull requests where the other type changes" — but the authors decline to read that as coupling, because skills change in most pull requests regardless: "every component-to-skills Lift falls below 1 (0.59–0.78) … we cannot attribute it to a coupling specific to agents and skills". The one inter-component pair beating chance is agents–commands at "Lift 1.40 (p<0.05)", with a stated mechanism: agent definitions embed command slash-names, and commands reference specific agents.

Inside `skills/` the picture inverts. "Lift here exceeds 1 for all script–Markdown pairs (1.37–1.58), confirming that scripts and Markdown files co-change more than chance alone would predict within a single skill directory". Of those co-changes, "Manual inspection of 64 sampled co-change pull requests confirms that 78% are functionally coupled, driven by interface and internal-logic changes that propagate from scripts to their paired instruction files" ([arXiv:2608.28497v1](https://arxiv.org/abs/2608.28497v1)). That figure is conditioned on a co-change having already happened. It says nothing about how often a script changed and the markdown stayed put, which is the failure this page is about.

The standard commit vocabulary also means something different here. "74% of docs commits modify instruction files Claude reads at inference time rather than human-readable documentation", and refactor commits are dominated by "rewording AI-facing instruction text without changing intended behavior" ([arXiv:2608.28497v1](https://arxiv.org/abs/2608.28497v1)). A `docs:` prefix on a plugin commit is a behavior change, so review it like one.

## Why it works

The markdown is the calling convention and the script is the implementation. Claude Code reaches a bundled script only through a path the plugin declares — `"command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format-code.sh"` in `hooks/hooks.json` — and decides whether and how to invoke it from the prose, because "Plugins contribute context through skills, agents, and hooks rather than CLAUDE.md. To ship instructions that load into Claude's context, put them in a skill" ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)). The authors name the failure directly: leaving `SKILL.md` behind after a script change "causes Claude to invoke the skill with outdated instructions, passing flags that no longer exist, use renamed identifiers, or follow an invocation pattern that the script no longer supports, with no runtime error to alert the developer" ([arXiv:2608.28497v1](https://arxiv.org/abs/2608.28497v1)).

The product does not close this gap. `claude plugin validate` checks "`plugin.json`, `hooks/hooks.json`, and the frontmatter of the skills, agents, and commands in the plugin's default directories for syntax and schema errors" ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)). Schema, not semantics. A `SKILL.md` describing a flag the script dropped last week validates clean.

## Where the paper's component map has aged

The study is a snapshot and the product moved. It treats commands and skills as two of seven component types; the current reference gives skills a location of "`skills/` or `commands/` directory in plugin root" and labels the `commands/` row "Skills as flat Markdown files. Use `skills/` for new plugins". It has also added `workflows/`, `output-styles/`, `themes/`, `monitors/monitors.json`, and `bin/` ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)). Read the co-change matrix as evidence that plugin components couple, not as a current inventory of what can couple to what.

## When this backfires

- Single-file plugins. A `SKILL.md` at the plugin root with no `skills/` subdirectory is a supported layout ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)), and has no script to fall out of sync with.
- Prose that carries no operational detail. Where the markdown names only invocation conditions, pairing manufactures churn. Strip the detail rather than police it, the remedy [Stale AI Configuration Artifacts](../patterns/anti-patterns/stale-ai-configuration-artifacts.md) reaches for.
- Private and commercial repositories. Denisov-Blanch et al. found "73.8% of artifacts are committed once and never modified" across 441 repositories ([arXiv:2608.25241v1](https://arxiv.org/abs/2608.25241v1)). The cohort here is public marketplace plugins with community traction.
- A launch surge read as a steady state. Plugin-touching commits rose "from 2,923 commits in October 2025 to 25,618 in March 2026". The authors date the evidence themselves: "The dataset was collected in April 2026 and represents a snapshot of a rapidly evolving ecosystem", and "The median repository age at collection time is only 80 days" ([arXiv:2608.28497v1](https://arxiv.org/abs/2608.28497v1)).
- A mechanical gate with no contract. Checking every value a skill document mentions produces 40% false positives against contract-bearing extraction ([Fan et al., 2026](https://arxiv.org/abs/2605.10990v1)). A rule firing on every script edit becomes a rubber stamp within weeks.

The 78% rests on a 64-pull-request human sample (two raters, Cohen's κ=0.74), extended to "the remaining 259" by a gpt-5-mini classifier validated at κ=0.62 against those 64 ([arXiv:2608.28497v1](https://arxiv.org/abs/2608.28497v1)).

## Key Takeaways

- Inside a plugin, a script and the markdown describing it are one interface. `claude plugin validate` checks schema and frontmatter, never whether the prose still matches the script ([Plugins reference](https://code.claude.com/docs/en/plugins-reference)).
- The coupling is specific to `skills/`. Across whole component types the paper finds independence, with agents–commands the single above-chance pair ([arXiv:2608.28497v1](https://arxiv.org/abs/2608.28497v1)).
- The 78% is a share of co-changes, not of script edits. Nobody has published the number you actually want: how often a script moves and its markdown does not.
- Treat a `docs:` or `refactor:` commit in a plugin as a behavior change.
- Pair the edits only where the prose carries operational detail. Where it does not, delete the detail instead; a document with no implementation references cannot drift from one.

## Related

- [Repository Skill Release Drift](../patterns/anti-patterns/repository-skill-release-drift.md) — the same decay measured against an upstream release rather than between a plugin's own components
- [Stale AI Configuration Artifacts (Context Rot)](../patterns/anti-patterns/stale-ai-configuration-artifacts.md) — drift between a config file and the codebase around it, where minimization is the rival remedy
- [Skill Library Technical Debt](../tool-engineering/skill-library-technical-debt.md) — defects across a library of skills, one level up from the coupling inside a single plugin
- [Agent Context File Evolution](agent-context-file-evolution.md) — the file-level maintenance loop for a single instruction file, where growth rather than coupling is the hazard
- [Skill File Linting: Which Three Checks to Run First](skill-file-linting.md) — the deterministic checks a `SKILL.md` can carry before any coupling question arises
