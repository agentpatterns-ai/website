---
title: "Prompt Governance via PRs: Reviewable AI Behaviour"
description: "Store agent instructions as markdown files in git and use pull requests to propose, review, and merge behaviour changes — no ML expertise required."
tags:
  - instructions
  - technique
  - tool-agnostic
  - workflows
---

# Prompt Governance via PR

> Store agent instructions as plain markdown files in git. Use pull requests to propose, review, and merge behaviour changes — the same workflow as code, without retraining anything.

## Overview

Instruction files (`CLAUDE.md`, `.github/copilot-instructions.md`, `AGENTS.md`) are already plain text in version control. That makes them subject to the same change management infrastructure the team already uses for code: branches, diffs, reviews, merge approvals, and revert.

Treating this as a deliberate governance strategy — rather than an incidental storage decision — gives teams a structured way to own and iterate on AI behaviour without ML infrastructure or data science involvement.

GitHub's accessibility team adopted this explicitly: they chose stored prompt files over model fine-tuning so that any team member could update AI behaviour through a pull request. When accessibility standards evolve, the team edits the instruction files and merges a PR; the AI adapts on the next run, not the next training cycle. ([Source](https://github.blog/ai-and-ml/github-copilot/continuous-ai-for-accessibility-how-github-transforms-feedback-into-inclusion/))

## How It Works

Instruction files are loaded at agent session start and are not cached between runs:

- **Claude Code** reads `CLAUDE.md` at session start, including for subagents ([Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents))
- **GitHub Copilot** reads `.github/copilot-instructions.md` (repo-wide) and matching `.github/instructions/*.instructions.md` files on each request ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions))
- **AGENTS.md-compatible tools** (Codex, Jules, Cursor, Aider, and others) read `AGENTS.md` from the repo root ([agents.md standard](https://agents.md))

Because files are loaded at runtime, a merged PR takes effect immediately — no deployment, no retraining, no restart.

The PR review process applies unchanged:

1. Open a branch, edit the instruction file
2. The diff shows exactly what behaviour is changing — reviewers see the delta, not a black box
3. Merge approval gates the change, the same as any code review
4. `git revert` is a full rollback; git history is the audit log

## Trade-offs

| Approach | Change velocity | Reviewability | Required expertise | Rollback |
|---|---|---|---|---|
| Prompt files via PR | Hours | Full diff | Markdown editing | `git revert` |
| Model fine-tuning | Days | None (weight update) | ML infrastructure | Retrain from prior checkpoint |
| Ad-hoc prompt iteration | Minutes | None | None | Manual reconstruction |

## When This Backfires

PR-gated prompt changes are not the right default in every context:

- **Fast experimental iteration.** Eval-driven prompt tuning often involves dozens of variants per session. Routing each through a review queue adds latency that swamps the experiment loop; a sandboxed prompt registry or feature-flag system fits better until a winner is promoted to the reviewed file.
- **Reviewers lack prompt-engineering literacy.** A diff is only as useful as the reviewer's ability to predict its behavioural effect. If approvers cannot reason about how a wording change shifts model output, the review becomes a rubber stamp — what some practitioners call "liability laundering" rather than governance ([Dev.to, 2026](https://dev.to/amit_kochman/ai-code-without-governance-is-now-a-legal-liability-520p)).
- **No canary stage.** Because instruction files load on the next agent run, a merged PR is effectively an instant production deploy with full blast radius. Teams that need staged rollouts (percentage-based, cohort-gated) must layer additional infrastructure on top — branching alone does not provide it.
- **Secrets or sensitive context in prompts.** Anything committed to git is recoverable from history. Prompts that legitimately contain customer data, credentials, or proprietary policy text need a separate secret-management path; PR review does not redact what the diff exposes.

## Example

GitHub's accessibility team runs a triage pipeline that calls the [GitHub Models API](../tools/copilot/github-models-in-actions.md). Their instruction file serves two roles: classifying issues by WCAG violation severity, and coaching engineers on accessible code. The file references internal accessibility policies and their component library.

**Before** (generic severity guidance):
```markdown
Classify accessibility issues as high, medium, or low severity.
```

**After** (domain-specific, reviewable via PR):
```markdown
Classify accessibility issues using the following severity scale:
- sev1: Critical — blocks all access for a user group (e.g., no keyboard navigation)
- sev2: High — significantly impairs access (e.g., missing alt text on informational images)
- sev3: Medium — reduces usability but workarounds exist
- sev4: Low — best-practice improvement, no functional barrier

Apply WCAG 2.2 AA criteria. Reference our component library at /docs/components
for expected accessible patterns before classifying.
```

The PR diff makes the severity definition change explicit. Reviewers can assess whether the thresholds are correct before the change affects production triage. If the classification produces wrong results, `git revert` restores the prior behaviour.

## Key Takeaways

- Instruction files are already in git — treating them as governed artifacts requires only a branch and PR convention, not new tooling
- Behaviour changes are diffs: reviewable, approvable, and revertible with the same process as code changes
- The audit log is git history — every behaviour decision is attributed and timestamped
- Fine-tuning changes model weights and is opaque; prompt-file changes are transparent and take effect immediately on the next agent run
- Non-ML team members can own and iterate on AI behaviour — the change medium is markdown, not training pipelines

## Related

- [Prompt File Libraries](prompt-file-libraries.md)
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md)
- [Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md](instruction-file-ecosystem.md)
- [Central Repo for Shared Agent Standards](../workflows/central-repo-shared-agent-standards.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Hierarchical CLAUDE.md: Structuring Context Files at Multiple Levels](hierarchical-claude-md.md)
- [Convention Over Configuration for Agent Workflows](convention-over-configuration.md)
- [AGENTS.md as Table of Contents, Not Encyclopedia](agents-md-as-table-of-contents.md)
- [Content Exclusion Gap in Agent Systems](content-exclusion-gap.md)
- [Standards as Agent Instructions for AI Agent Development](standards-as-agent-instructions.md)
- [Frozen Spec File: Preserving Intent in AI Agent Sessions](frozen-spec-file.md)
- [Layer Agent Instructions by Specificity: Global, Project](layered-instruction-scopes.md)
- [AGENTS.md Design Patterns: Commands, Boundaries, Personas](agents-md-design-patterns.md)
- [@import Composition Pattern for Agent Instruction Files](import-composition-pattern.md)
- [Encode Project Conventions in Distributed AGENTS.md Files](agents-md-distributed-conventions.md)
- [Instruction Polarity: Positive Rules Over Negative](instruction-polarity.md)
- [Negative Space Instructions: What NOT to Do](negative-space-instructions.md)
- [Feature List Files](feature-list-files.md)
- [Production System Prompt Architecture](production-system-prompt-architecture.md)

## Sources

- [GitHub Blog — Continuous AI for Accessibility](https://github.blog/ai-and-ml/github-copilot/continuous-ai-for-accessibility-how-github-transforms-feedback-into-inclusion/) — Production case study: stored prompts + PR workflow instead of fine-tuning
- [GitHub Docs — Add Repository Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) — Official reference for `copilot-instructions.md` file format and org/repo/personal hierarchy
- [GitHub Accessibility — Optimizing Copilot with Custom Instructions](https://accessibility.github.com/documentation/guide/copilot-instructions) — GitHub's own guide on writing accessibility-focused custom instructions
- [agents.md open standard](https://agents.md) — Cross-tool standard for `AGENTS.md` instruction files
- [Claude Code Sub-Agents Docs](https://code.claude.com/docs/en/sub-agents) — Confirms CLAUDE.md loads per session including for spawned subagents
