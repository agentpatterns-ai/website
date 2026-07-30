---
title: "Prompt Governance via PRs: Reviewable AI Behavior"
term: "Prompt Governance via PRs"
description: "Store agent instructions as markdown files in git and use pull requests to propose, review, and merge behavior changes — no ML expertise required."
tags:
  - instructions
  - technique
  - tool-agnostic
  - workflows
last_reviewed: 2026-07-30
maturity: established
---

# Prompt Governance via PR

> Govern agent prompt files like code: store them as markdown in git and review behavior changes through pull requests, no retraining required.

## Instruction files are already version-controlled

Instruction files (`CLAUDE.md`, `.github/copilot-instructions.md`, `AGENTS.md`) are already plain text in version control. So they fall under the same change-management tools the team already uses for code: branches, diffs, reviews, merge approvals, and revert.

Treat this as deliberate governance, not an incidental storage choice. Teams then get a structured way to own and improve AI behavior without ML infrastructure or data scientists.

The PR mechanism is one part of a larger gap. Towards Data Science argues that prompt engineering is the solved half of the problem and prompt *management* — versioning, a registry, and lifecycle handling — is the half still missing from most teams ([Towards Data Science — Prompt Engineering Is Solved. Prompt Management Isn't](https://towardsdatascience.com/prompt-engineering-is-solved-prompt-management-isnt/)). Branch-and-review covers versioning and approval; the registry and lifecycle pieces need conventions on top.

GitHub's accessibility team chose this on purpose: they stored prompt files instead of fine-tuning a model, so that any team member could update AI behavior through a pull request. When accessibility standards change, the team edits the instruction files and merges a PR. The AI adapts on the next run, not the next training cycle. ([Source](https://github.blog/ai-and-ml/github-copilot/continuous-ai-for-accessibility-how-github-transforms-feedback-into-inclusion/))

## How it works

Agents load instruction files at session start and do not cache them between runs:

- Claude Code reads `CLAUDE.md` at session start, including for subagents ([Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents))
- GitHub Copilot reads `.github/copilot-instructions.md` (repo-wide) and matching `.github/instructions/*.instructions.md` files on each request ([GitHub repository instructions docs](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions))
- AGENTS.md-compatible tools (Codex, Jules, Cursor, Aider, and others) read `AGENTS.md` from the repo root ([agents.md standard](https://agents.md))

Because agents load files at runtime, a merged PR takes effect immediately — no deployment, no retraining, no restart.

The PR review process applies unchanged:

1. Open a branch and edit the instruction file.
2. The diff shows exactly what behavior is changing, so reviewers see the change, not a black box.
3. Merge approval gates the change, the same as any code review.
4. `git revert` gives a full rollback, and git history is the audit log.

## Trade-offs

| Approach | Change velocity | Reviewability | Required expertise | Rollback |
|---|---|---|---|---|
| Prompt files via PR | Hours | Full diff | Markdown editing | `git revert` |
| Model fine-tuning | Days | None (weight update) | ML infrastructure | Retrain from prior checkpoint |
| Ad-hoc prompt iteration | Minutes | None | None | Manual reconstruction |

## When this backfires

PR-gated prompt changes are not the right default in every context:

- Fast experimental iteration. Eval-driven prompt tuning often runs dozens of variants per session. Routing each one through a review queue adds latency that swamps the experiment loop. A sandboxed prompt registry or feature-flag system fits better until you promote a winner to the reviewed file.
- Reviewers lack prompt-engineering literacy. A diff is only as useful as the reviewer's ability to predict its effect on behavior. If approvers cannot reason about how a wording change shifts model output, the review becomes a rubber stamp — what some practitioners call "liability laundering" rather than governance ([Dev.to, 2026](https://dev.to/amit_kochman/ai-code-without-governance-is-now-a-legal-liability-520p)).
- No canary stage. Instruction files load on the next agent run, so a merged PR is effectively an instant production deploy with full [blast radius](../security/blast-radius-containment.md). Teams that need staged rollouts (percentage-based, cohort-gated) must add infrastructure on top, because branching alone does not provide it.
- Secrets or sensitive context in prompts. Anything committed to git is recoverable from history. Prompts that legitimately contain customer data, credentials, or proprietary policy text need a separate secret-management path. PR review does not redact what the diff exposes.

## Example

GitHub's accessibility team runs a triage pipeline that calls the [GitHub Models API](../tools/copilot/github-models-in-actions.md). Their instruction file serves two roles: classifying issues by WCAG violation severity, and coaching engineers on accessible code. The file references internal accessibility policies and their component library — the [standards-as-agent-instructions](standards-as-agent-instructions.md) pattern.

Before (generic severity guidance):
```markdown
Classify accessibility issues as high, medium, or low severity.
```

After (domain-specific, reviewable via PR):
```markdown
Classify accessibility issues using the following severity scale:
- sev1: Critical — blocks all access for a user group (e.g., no keyboard navigation)
- sev2: High — significantly impairs access (e.g., missing alt text on informational images)
- sev3: Medium — reduces usability but workarounds exist
- sev4: Low — best-practice improvement, no functional barrier

Apply WCAG 2.2 AA criteria. Reference our component library at /docs/components
for expected accessible patterns before classifying.
```

The PR diff makes the severity definition change explicit. Reviewers can judge whether the thresholds are correct before the change affects production triage. If the classification produces wrong results, `git revert` restores the prior behavior.

## Key Takeaways

- Instruction files are already in git — treating them as governed artifacts requires only a branch and PR convention, not new tooling
- Behavior changes are diffs: reviewable, approvable, and revertible with the same process as code changes
- The audit log is git history — every behavior decision is attributed and timestamped
- Fine-tuning changes model weights and is opaque; prompt-file changes are transparent and take effect immediately on the next agent run
- Non-ML team members can own and iterate on AI behavior — the change medium is markdown, not training pipelines

## Related

- [Prompt File Libraries](prompt-file-libraries.md)
- [Project Instruction File Ecosystem: CLAUDE.md, copilot-instructions, AGENTS.md](instruction-file-ecosystem.md)
- [Continuous Agent Improvement](../workflows/continuous-agent-improvement.md)
- [Central Repo for Shared Agent Standards](../workflows/central-repo-shared-agent-standards.md)
- [Standards as Agent Instructions for AI Agent Development](standards-as-agent-instructions.md)
- [Frozen Spec File: Preserving Intent in AI Agent Sessions](frozen-spec-file.md)
- [CLAUDE.md Convention](claude-md-convention.md)
- [Prompt Transpilation: Instructions as Build Artifacts](prompt-transpilation.md)

## Sources

- [GitHub Blog — Continuous AI for Accessibility](https://github.blog/ai-and-ml/github-copilot/continuous-ai-for-accessibility-how-github-transforms-feedback-into-inclusion/) — Production case study: stored prompts + PR workflow instead of fine-tuning
- [GitHub Docs — Add Repository Instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) — Official reference for `copilot-instructions.md` file format and org/repo/personal hierarchy
- [GitHub Accessibility — Optimizing Copilot with Custom Instructions](https://accessibility.github.com/documentation/guide/copilot-instructions) — GitHub's own guide on writing accessibility-focused custom instructions
- [agents.md open standard](https://agents.md) — Cross-tool standard for `AGENTS.md` instruction files
- [Claude Code Sub-Agents Docs](https://code.claude.com/docs/en/sub-agents) — Confirms CLAUDE.md loads per session including for spawned subagents
- [Towards Data Science — Prompt Engineering Is Solved. Prompt Management Isn't](https://towardsdatascience.com/prompt-engineering-is-solved-prompt-management-isnt/) — Argues versioning, registry, and lifecycle are the unsolved half of prompt work
