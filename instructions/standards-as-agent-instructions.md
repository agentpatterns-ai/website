---
title: "Standards as Agent Instructions for AI Agent Development"
description: "Project standards precise enough for human reviewers work as agent instructions verbatim — one document serves both when written without interpretive gaps."
tags:
  - instructions
  - tool-agnostic
---

# Standards as Agent Instructions

> A standards file that is actionable for humans is, verbatim, an instruction file for agents — the same document does both jobs when written precisely.

## The Dual-Audience Property

Project standards files — `STANDARDS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` — are read by two audiences: humans checking their own work, and agents producing output. When a standard is precise enough to serve as an agent instruction, it needs no translation layer. When it is vague, it fails both audiences.

The distinguishing property is actionability. Compare:

| Vague (fails both audiences) | Actionable (serves both) |
|-------------------------------|--------------------------|
| "Be concise" | "Max 500 words for pattern pages; max 750 for techniques" |
| "Follow naming conventions" | "Use kebab-case file names; no prefixes or numbering" |
| "Write good commit messages" | "Use conventional commits: `type(scope): description`" |
| "Avoid filler" | `"No phrases: 'in this guide', 'let's explore', 'as you may know'"` |

The actionable form gives the agent a verifiable rule. The vague form gives the agent interpretive latitude, which produces inconsistent output.

## Why Agents Read Standards Literally

Humans read standards with context: they know what "concise" means in their domain, they have judgment about edge cases, they apply intent rather than letter. Agents apply the rule as written. Ambiguity in a rule does not produce a reasonable interpretation — it produces the interpretation most consistent with training data, which may not match project conventions.

This is not a failure mode to work around; it is a constraint to design for. Writing standards that an agent can follow without interpretation produces instructions that are also clearer for humans.

## File Hierarchy

Standards work at multiple scopes. Claude Code reads `CLAUDE.md` in a hierarchy: managed policy → project → user ([Claude Code memory docs](https://code.claude.com/docs/en/memory)). GitHub Copilot reads `.github/copilot-instructions.md` at the repository level ([Copilot customization docs](https://docs.github.com/en/copilot/concepts/about-customizing-github-copilot-chat-responses)).

The practical consequence: a root standards file applies to all tasks; nested files add specificity for particular areas. A rule in `src/auth/CLAUDE.md` overrides or extends the root when an agent works in that directory.

Structure the hierarchy as:

- Root: project-wide conventions that apply to every task
- Area-specific: constraints that only apply in a particular directory or domain

Avoid putting area-specific rules in the root file — they add noise to every task even when irrelevant.

## Concrete Examples as Anchors

Standards with examples are more reliably followed than standards without them [unverified — consistent with observed agent behavior but not independently benchmarked]. An agent reading "no filler phrases" must infer what counts. An agent reading:

```
No filler phrases: "in this guide", "let's explore", "as you may know", "it's worth noting"
```

has a concrete reference set. The examples anchor the rule against ambiguity and provide pattern-matching targets.

Where a rule has a clear correct form and a clear incorrect form, include both. The contrast eliminates the ambiguity zone where most interpretation errors occur.

## Standards as Quality Gates

When reviewers check agent output against the standards file, they are using it as a diff target: the output either satisfies the rule or it does not. This only works if the rule is precise enough to produce a binary determination.

"Be concise" fails as a gate — any output can be argued to satisfy it. "Max 500 words" succeeds — word count is measurable. Designing standards for reviewability forces the precision that also makes them work as agent instructions.

## Example

A `STANDARDS.md` excerpt from a documentation project, written so both a human reviewer and an agent can apply every rule without interpretation:

```markdown
## Commit Messages

Format: `type(scope): lowercase description under 72 chars`
Types: feat, fix, docs, refactor, test, chore
Scope: directory name or filename stem

✅ `docs(agent-harness): add tool registration example`
❌ `Updated the agent harness docs`

## Page Structure

1. YAML frontmatter with `title`, `description` (80–160 chars), `tags` (≥1)
2. H1 matching the `title` field
3. Blockquote summary (one sentence, defines the concept — not "This page covers…")
4. Body sections using H2; never skip heading levels
5. `## Related` section with relative markdown links

## Word Limits

| Directory        | Max body words |
|------------------|---------------|
| `patterns/`      | 750           |
| `anti-patterns/` | 500           |
| `articles/`      | 5000          |

## File Naming

- kebab-case, no prefixes, no numbering
- Stem matches the concept: `agent-harness.md`, not `01-harness-overview.md`
```

A human reviewer reads these rules and checks a pull request against them. An agent reads the same file as its instruction set and produces output that satisfies every rule on the first pass. No translation layer, no separate prompt — one document serves both.

## Key Takeaways

- An actionable standards file requires no translation to serve as an agent instruction — precision serves both audiences
- Agents read standards literally; ambiguity produces training-data defaults, not project-appropriate interpretation
- Use file hierarchy to scope rules: project-wide at root, area-specific in nested files
- Include concrete examples — both correct and incorrect forms — to eliminate the ambiguity zone
- Design standards for reviewability (binary pass/fail per rule) to force the precision that makes them work for agents

## Unverified Claims

- Standards with examples are more reliably followed than standards without them `[unverified — consistent with observed agent behavior but not independently benchmarked]`

## Related

- [AGENTS.md: A README for AI Coding Agents](../standards/agents-md.md)
- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md)
- [Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md](instruction-file-ecosystem.md)
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels](hierarchical-claude-md.md)
- [Layer Agent Instructions by Specificity: Global, Project, and Directory Scopes](layered-instruction-scopes.md)
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md)
- [Convention Over Configuration for Agent Workflows](convention-over-configuration.md)
- [The Specification as Prompt: Existing Artifacts as Agent Instructions](specification-as-prompt.md)
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md)
- [Prompt Governance via PR](prompt-governance-via-pr.md)
