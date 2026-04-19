---
title: "Guardrails Beat Guidance: Rule Design for Coding Agents"
description: "On SWE-bench, negative constraints are the only individually beneficial rule type for coding agents; positive directives actively hurt. Rules work through context priming, not instruction specificity."
tags:
  - instructions
  - context-engineering
aliases:
  - Guardrails Over Guidance
  - Negative Rules for Coding Agents
---

# Guardrails Beat Guidance: Rule Design for Coding Agents

> For coding-agent rule files on SWE-bench Verified, negative constraints are the only individually beneficial rule type; positive directives actively degrade task success. Rules improve performance mainly by priming context, not by transmitting specific instructions.

!!! info "Also known as"
    Guardrails Over Guidance, Negative Rules for Coding Agents

## The Evidence

The first large-scale evaluation of CLAUDE.md / `.cursorrules`-style files scraped 679 rule files (25,532 rules) from GitHub and ran 5,000+ agent runs on SWE-bench Verified ([Zhang et al., 2026](https://arxiv.org/abs/2604.11088)). Four findings matter for rule design:

- Rules improve performance by **7–14 percentage points** over no rules
- **Random rules help as much as expert-curated ones** — implying rules work through context priming, not instruction content
- **Negative constraints** ("do not refactor unrelated code") are the only individually beneficial rule type — **positive directives** ("follow code style") actively hurt performance when added individually
- Rules are "mostly harmful in isolation yet collectively helpful" — no degradation up to 50 rules in the tested range

## Why It Works

Zhang et al. analyze the asymmetry through potential-based reward shaping (PBRS): rules do not teach new behavior but reshape the agent's search landscape ([Zhang et al., 2026](https://arxiv.org/abs/2604.11088)). Negative constraints remove infeasible branches — a discrete, binary cut. Positive directives add soft preferences that compete with training-time priors, producing the objective conflict that shows up as degraded benchmark performance.

The context-priming half is independent: any domain-relevant text activates the coding-task subspace of the model's representations regardless of content, which explains why random rules match hand-written ones. Rule presence primes; rule content shapes the search. The two effects stack.

## Applying the Pattern

Three rewrites follow directly from the evidence:

| Before (positive directive) | After (negative constraint) |
|---|---|
| Follow the existing code style | Do not introduce new formatting conventions |
| Write clear commit messages | Do not squash unrelated changes into one commit |
| Keep changes focused | Do not refactor code outside the task scope |
| Write thorough tests | Do not delete or skip existing tests |

Each "after" rule defines a feasibility boundary the agent either crosses or doesn't — the property PBRS predicts will reshape search without competing with priors. Each "before" rule asks the agent to rank its existing behavior against a goal it must interpret.

For novel conventions the agent cannot discover from the codebase — an unfamiliar build command, a project-specific tool invocation — a positive directive is the only option. Keep those, and pair them with negative guardrails around the adjacent failure modes.

## Reconciling With Other Findings

This result is narrower than it looks. Three boundaries matter:

- **Coding agents on SWE-bench only.** General prompt engineering still favors positive directives; Anthropic's docs advise ["Tell Claude what to do instead of what not to do"](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) for clarity and format control. The coding-agent finding is a specialization, not a reversal.
- **Rule sets under ~50 rules.** The no-degradation window ends there. Beyond it, the compliance ceiling dominates — frontier models reach only 68% accuracy at 500 instructions ([IFScale, 2025](https://arxiv.org/abs/2507.11538)).
- **Complementary, not superseding.** [AGENTS.md](../standards/agents-md.md) benchmarks found tool-specific commands and non-inferable constraints produce the largest behavior change ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988)) — positive directives that still work where they supply information the agent cannot infer.

The synthesis: write negative constraints for failure modes the agent already knows how to avoid; write positive directives only for information the agent cannot reach any other way.

## Example

A CLAUDE.md excerpt rewritten from positive to negative for a coding-agent repo:

**Before — positive-heavy rule file:**

```markdown
## Coding Rules

- Follow the existing code style and patterns
- Write descriptive variable names
- Add tests for all new functionality
- Keep functions small and focused
- Use meaningful commit messages
```

**After — negative-first with a targeted positive directive:**

```markdown
## Coding Rules

- Do not introduce formatting styles that differ from surrounding code
- Do not use single-letter variable names outside loop counters
- Do not merge changes that remove test coverage
- Do not refactor code outside the scope of the task
- Do not squash unrelated changes into a single commit

## Project-Specific

- Run tests with `pnpm test:integration --filter $PKG` — the default `pnpm test` does not cover integration tests in this monorepo
```

The negative rules reshape the agent's search by removing known failure branches. The single positive directive stays because `pnpm test:integration --filter $PKG` is not inferable from the codebase — the information has to be supplied.

## When This Backfires

- **Non-coding tasks.** The paper measures SWE-bench success only. Extrapolating guardrails-over-guidance to chat assistants, classification, or tool-dispatch pipelines is unsupported by this evidence.
- **Prescriptive output format.** Commit-message schemas, file-naming conventions, API response structures need positive specification — a negative-only rule set cannot define required structure.
- **Above the compliance ceiling.** The 50-rule no-degradation window is narrower than many production CLAUDE.md files. At high instruction densities, compliance degrades regardless of polarity — frontier models reach only 68% accuracy at 500 instructions ([IFScale, 2025](https://arxiv.org/abs/2507.11538)).
- **Must-never-fail constraints.** Critical prohibitions belong in hooks or CI gates, not instruction text. An instruction asks; a hook requires.

## Key Takeaways

- For coding-agent rule files, negative constraints are the only individually beneficial rule type on SWE-bench — positive directives degrade performance when added in isolation
- Random rules produce gains comparable to expert-curated ones, so rule presence primes the model independent of rule content
- Reserve positive directives for information the agent genuinely cannot infer from the codebase — tool commands, non-standard build steps, project-specific invocations
- The 50-rule no-degradation window sits below the compliance ceiling; guardrails-over-guidance is a refinement of rule design, not a license to add more rules

## Related

- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md) — quality-and-greppability case for negative constraints
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md) — the opposite default for general prompting; this page is the coding-agent-specific refinement
- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — complementary empirical data on context-file design
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — the ceiling past which rule count dominates rule design
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — when examples beat rules of either polarity
- [Enforcing Agent Behavior with Hooks](enforcing-agent-behavior-with-hooks.md) — the deterministic alternative to instruction-text constraints
