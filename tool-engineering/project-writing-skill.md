---
title: "Project Writing Skill: House Style as Model-Invocable Skill"
description: "Package project writing conventions — audience, tone, banned phrases, structural rules — into a model-invocable skill loaded only when the agent is actually writing prose."
tags:
  - instructions
  - agent-design
  - tool-agnostic
  - tool-engineering
aliases:
  - writing skill for agents
last_reviewed: 2026-05-27
---

# Project Writing Skill

> A project-scoped writing skill bundles audience, tone, banned phrases, and structural rules into a model-invocable [SKILL.md](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) loaded only when the agent generates prose — not on every turn the way `AGENTS.md`/`CLAUDE.md` rules are.

A project writing skill is a [model-invocable skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) whose `description` triggers on prose tasks (docs, release notes, PR descriptions, ADRs, commit messages) and whose body carries the project's writing conventions. The contrast is with the same rules in `AGENTS.md`/`CLAUDE.md`, which enter every conversation regardless of task. Matt Pocock's [AI Hero changelog](https://www.aihero.dev/skills/skills-changelog-handoff-prototype-review-and-writing) previews a `writing` skill (fragments/beats/shape passes) — the specific application of [Skill as Knowledge](skill-as-knowledge.md) to prose rules.

## Decision Conditions

The skill is justified under specific conditions. When none hold, the rules belong in `AGENTS.md`/`CLAUDE.md` or a deterministic linter.

| Condition for the skill | Condition for AGENTS.md |
|-------------------------|-------------------------|
| Prose tasks are intermittent across the session | Prose generation happens on most turns |
| Rule set is large (≥30 rules) | Rule set is small (≤10 rules) — discovery cost exceeds savings |
| Audience-conditional rules (ADR vs release note vs PR) | One universal rule set every task respects |
| Project lives in Claude Code only | Project ships cross-tool under the [agents.md open standard](https://agents.md); Custom Skills don't sync between claude.ai, the API, or other vendors ([Anthropic Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)) |

Instruction-following decays as rule count grows; smaller models exponentially ([Liu et al. 2025](https://arxiv.org/pdf/2507.11538)). Off-loading 30 rules from `AGENTS.md` leaves only rules that pass HumanLayer's "tell a senior engineer on day one" test ([HumanLayer: Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)).

## Composition with Linters

The skill defines intent; the linter enforces letter — "never send an LLM to do a linter's job" ([HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md)). Banned phrases, length caps, required headings belong in a pre-commit hook. The skill carries what a linter cannot encode: tone-per-audience and the mental model the document should leave.

| Layer | Carries | Triggers on |
|-------|---------|-------------|
| Pre-commit linter / CI check | Deterministic checks (banned regex, length, structure) | Every commit |
| Writing skill (model-invocable) | Tone, audience routing, intent rules, examples | When the agent generates prose |
| `AGENTS.md` / `CLAUDE.md` | The small universal subset | Every turn |

## Why It Works

A writing skill works because **discoverability cost is paid only when relevant**. The Skills architecture pre-loads ~100 tokens of `name`+`description` per installed skill ([Anthropic Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)); the SKILL.md body (under 5k tokens) loads only when the description matches the task. `AGENTS.md`/`CLAUDE.md` enters every turn regardless ([HumanLayer post](https://www.humanlayer.dev/blog/writing-a-good-claude-md)). Since frontier thinking models follow ~150–200 rules reliably ([Liu et al. 2025](https://arxiv.org/pdf/2507.11538)), every writing rule in `AGENTS.md` degrades compliance on every non-writing rule.

The second mechanism is **audience-conditional branching**. SKILL.md can carry rule subsets for ADRs, release notes, and PR descriptions via reference files; `AGENTS.md` encodes the union of all audiences. Progressive disclosure lets the agent navigate to just the audience's rules at write time.

## When This Backfires

Each failure mode below has a tractable diagnosis, but expect to hit at least one.

- **Silent skill non-invocation.** The agent generates prose without invoking the skill — Anthropic calls this the "under-triggering bias" of skill descriptions ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)). The same rules in `AGENTS.md` would have been loaded unconditionally. Diagnosis: ask the agent "when would you use the writing skill?" — it quotes the description, exposing missing trigger phrases ([Skill Authoring Patterns](skill-authoring-patterns.md)).
- **SKILL.md bloat.** The skill grows past Anthropic's 500-line guidance ([best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)), dilutes the rules that matter, and competes with conversation history once loaded.
- **Contradiction with `AGENTS.md`.** Both files claim authority over tone or banned phrases; the agent has no precedence rule and behaves inconsistently — analogous to [Multi-Layer Specification Redundancy](../instructions/multi-layer-specification-redundancy.md).
- **Cross-surface penalty.** Multi-tool projects pay 4× maintenance — Claude Code skill, claude.ai upload, Cursor rule, Copilot instructions — for one writing skill. Skills do not sync between claude.ai and the API ([Anthropic Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)).
- **Rules are deterministically enforceable.** If a regex catches every violation, the pre-commit hook is the right home — the skill checks only when invoked; the linter checks every commit.

## Cross-Tool Variants

| Tool | Encoding |
|------|----------|
| Claude Code | `.claude/skills/writing/SKILL.md` with `description` trigger ([Claude Code skills docs](https://code.claude.com/docs/en/skills)) |
| GitHub Copilot | Prompt files (`.github/prompts/*.prompt.md`) invoked via slash command, or instruction files scoped by glob |
| Cursor | Project rules (`.cursor/rules/*.mdc`) with `description` and `globs` for path-conditional activation |
| Tool-agnostic | SKILL.md following the [agentskills.io open standard](https://agentskills.io) — works in any standards-compliant agent |

## Example

A project's prose conventions split across three homes:

**`AGENTS.md`** (always-on, universal subset):

```markdown
## Writing

- Neutral reference tone — no marketing language, no second-person tutorials
- Cite every technical claim inline
- See `.claude/skills/writing/SKILL.md` for audience-conditional rules
```

**`.claude/skills/writing/SKILL.md`** (on-demand, audience-conditional):

```yaml
---
name: writing
description: Project writing conventions for docs, release notes, PR descriptions, ADRs, and commit messages. Use when generating any user-facing prose, when a request mentions writing/drafting/documenting, or when editing files under docs/, CHANGELOG.md, or .github/PULL_REQUEST_TEMPLATE.md.
---
```

```markdown
# Project Writing

## Audience routing

| Output | Read first |
|--------|------------|
| Docs page (under `docs/`) | `docs.md` — answer-first lede, sourced claims, 500-word target |
| Release note | `release-notes.md` — user-facing, no internal jargon |
| ADR | `adr.md` — context, decision, consequences |
| PR description | `pr.md` — what changed, why, test plan |
| Commit message | `commits.md` — Conventional Commits, present-tense imperative |

## Universal rules

- Strip meta-framing filler from openings
- Reject hedge tags — the claim either has a source or is removed
- One idea per sentence
```

**Pre-commit hook** (deterministic enforcement):

```bash
#!/usr/bin/env bash
# Blocks banned phrases and length violations on commits touching prose files
uv run python scripts/lint-prose.py "$@"
```

The skill carries the *which-audience-needs-what* knowledge that a regex cannot encode; the linter catches the deterministic violations the skill might miss; `AGENTS.md` carries the small universal subset that has to land every turn regardless of which audience.

## Key Takeaways

- A writing skill moves house-style rules from always-on (`AGENTS.md`) to on-demand (loaded only when the description matches the prose task) — the same skill-as-knowledge mechanism that applies to any domain knowledge applied to prose specifically.
- The skill beats `AGENTS.md` when prose tasks are intermittent, the rule set is large, or rules are audience-conditional. `AGENTS.md` beats the skill when rules are universal, the rule set is small, or the project ships cross-tool under the open standard.
- Compose with a deterministic linter: skill defines intent, linter enforces letter, `AGENTS.md` carries the small universal subset.
- Expect the under-triggering failure mode (silent skill non-invocation) — verify by asking the agent when it would use the skill, and tune the description's trigger phrases until the answer is right.

## Related

- [Skill as Knowledge Pattern](skill-as-knowledge.md)
- [Skill Authoring Patterns](skill-authoring-patterns.md)
- [SKILL.md Frontmatter Reference](skill-frontmatter-reference.md)
- [CLAUDE.md Convention](../instructions/claude-md-convention.md)
- [AGENTS.md as a Table of Contents, Not an Encyclopedia](../instructions/agents-md-as-table-of-contents.md)
- [Instruction Compliance Ceiling](../instructions/instruction-compliance-ceiling.md)
