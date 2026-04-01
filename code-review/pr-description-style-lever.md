---
title: "PR Description Style as a Lever for Agent PR Merge Rates"
description: "PR description structure is a configurable agent parameter that measurably affects reviewer engagement, merge rates, and time-to-completion."
tags:
  - workflows
  - human-factors
---

# PR Description Style as a Lever for Agent PR Merge Rates

> Treating PR description structure as a configurable agent parameter — not a cosmetic default — measurably affects reviewer engagement and merge outcomes.

## The Finding

A study of 5 AI coding agents across the AIDev dataset found statistically significant variation in PR description structure across agents. Structural differences correlate with reviewer engagement metrics and merge rates ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084)).

Merge rates by agent: OpenAI Codex 82.6%, Cursor 65.22%, Claude Code 59.0%, Devin 53.76%, GitHub Copilot 43.0%. All cross-agent differences were statistically significant at p<0.001 ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084), Table 4).

Merge rate variance is partly explained by description style differences, not code quality alone ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084)).

## Structural Differences Across Agents

The study identifies systematic per-agent patterns ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084)):

| Agent | Description Characteristics |
|---|---|
| OpenAI Codex | Frequent headers and lists; high structural clarity and understandability |
| Claude Code | High text volume; emoji use; strict adherence to conventional commits / PR conventions |
| Cursor | Politeness markers; moderate structure |
| Devin | Frequent commit splits; structured commit history |
| GitHub Copilot | Extensive reviewer discussion generated; lowest merge rate |

GitHub Copilot generated the most reviewer discussion but had the lowest merge rate — indicating review churn, not engagement volume, is the outcome to optimize ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084)).

Time-to-completion also varied sharply: OpenAI Codex at approximately 0.02 hours vs GitHub Copilot at 13.0 hours, with structured descriptions correlating with faster reviewer responses ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084), Table 4).

Effect sizes were meaningful: comments-per-PR showed a medium-to-large effect (ε²=0.280); reviewer sentiment showed V=0.128 (chi-square) ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084)).

## The Configuration Mechanism

Both primary configuration surfaces accept PR description templates directly:

**CLAUDE.md / AGENTS.md**: Add a `## Pull Requests` or `## PR Conventions` section specifying required headers. Example structure:

```markdown
## Pull Requests

Every PR description must include these sections:
- **Summary**: One sentence stating what changes and why
- **Changes**: Bullet list of concrete file-level changes
- **Testing**: How the change was verified (tests run, manual steps)
- **Breaking Changes**: Explicit note if none
```

**GitHub Copilot custom agent instructions** (`.github/agents/AGENT-NAME.md`): Inject the same template in the agent's instruction file. Neither Copilot nor Claude Code enforces structure by default ([Claude Code docs](https://code.claude.com/docs); [GitHub Blog](https://github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/)).

**AGENTS.md open standard** ([agents.md](https://agents.md)): PR and commit conventions can be embedded as project-level configuration, making them tool-agnostic and version-controlled alongside the codebase.

Note: GitHub Copilot's built-in PR summary generator ignores existing PR description content and generates from code changes alone — it has no configuration options for structure or format ([GitHub Docs](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-for-pull-requests/creating-a-pull-request-summary-with-github-copilot)).

## Why High Volume Without Structure Fails

The study's authors frame communication quality as a first-class agent capability: "accelerating the adoption of SE 3.0 requires AI coding agents to possess the capability to appropriately articulate and convey their changes" ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084)).

The counterintuitive result — more reviewer discussion, lower merge rate — points to a failure mode: descriptions that require reviewers to reconstruct intent from prose. Structured headers offload that reconstruction work from the reviewer [unverified].

The authors also note: "presentation alone does not determine acceptance — structured descriptions do not guarantee merges, and code quality remains a central factor" ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084)).

## Applying the Pattern

1. Add a PR description template to `CLAUDE.md`, `.github/agents/`, or `AGENTS.md` for every agent that opens PRs
2. Specify required sections (Summary, Changes, Testing, Breaking Changes at minimum)
3. Do not rely on model defaults — defaults differ across models and will produce variance
4. If using GitHub Copilot's PR summary generator, replace it by adding a post-PR-creation workflow step where an agent rewrites the description using your template from agent instructions, rather than relying on the diff-based summary alone
5. Treat description style as a reviewable artifact in agent eval runs — spot-check for section completeness alongside code correctness

## Example

A `CLAUDE.md` section that enforces PR description structure for an agent opening PRs against a Python backend:

    ## PR Conventions

    Every PR description must follow this template:
    - **Summary**: One sentence stating what changed and why
    - **Changes**: Bullet list of file-level changes
    - **Testing**: How the change was verified
    - **Breaking Changes**: Explicitly state "None" if there are none

    Do not include emojis, contributor shout-outs, or auto-generated diff summaries.

With this template in `CLAUDE.md`, the agent's PR descriptions consistently include the four sections reviewers need, reducing back-and-forth and aligning with the high-merge-rate structural patterns identified in the AIDev study.

## Key Takeaways

- PR description structure varies systematically by agent and correlates with reviewer engagement and merge rates per empirical study ([arXiv:2602.17084](https://arxiv.org/abs/2602.17084))
- High reviewer discussion volume does not predict merge success — review churn is the failure mode to avoid
- Description templates in `CLAUDE.md`, `AGENTS.md`, or custom agent instructions are the direct configuration mechanism
- Neither Claude Code nor GitHub Copilot enforces PR description structure by default — it must be configured
- Code quality remains the primary determinant of merge success; description style is a secondary lever with measurable but bounded effect

## Related

- [Issue-to-PR Delegation Pipeline](../workflows/issue-to-pr-delegation-pipeline.md)
- [Agent-Authored PR Integration: Collaboration Signals](agentic-code-review-architecture.md)
- [Agent-Authored PR Integration](agent-authored-pr-integration.md)
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md)
- [AGENTS.md Convention](../standards/agents-md.md)
- [Predicting Which AI-Generated Functions Will Be Deleted](predicting-reviewable-code.md)
- [Tiered Code Review: AI-First with Human Escalation](tiered-code-review.md)
- [Agent-Assisted Code Review](agent-assisted-code-review.md)
- [Diff-Based Review](diff-based-review.md)
- [Review-Then-Implement Loop](review-then-implement-loop.md)
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md)
- [Human-AI Review Synergy](human-ai-review-synergy.md)
