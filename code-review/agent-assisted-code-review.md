---
title: "Agent-Assisted Code Review: Agents as PR First Pass"
description: "Use agents to handle mechanical review checks before human review, freeing humans for architecture and design judgment. Human reviewers are better at judgment"
tags:
  - testing-verification
  - code-review
aliases:
  - AI Code Review
  - Automated PR Review
---

# Agent-Assisted Code Review: Agents as PR First Pass

> Agent-assisted code review routes the mechanical first pass — style, types, security patterns, test coverage — to an agent, reserving human reviewers for the design and architecture judgment that agents cannot reliably provide.

## The Technique

Human reviewers excel at judgment; agents excel at checklists. The agent handles the first pass — style consistency, type correctness, test coverage gaps, security patterns, naming conventions — while humans focus on design, architecture fit, and scalability.

The mechanism is attention allocation: eliminating repetitive pattern-matching from the human review queue directs reviewer attention to architectural concerns. An interview study of 20 engineers reports that engagement with AI-assisted review is distinct from peer review along cognitive, emotional, and behavioral dimensions ([arXiv:2501.02092](https://arxiv.org/abs/2501.02092)).

## How It Works

### GitHub Copilot Code Review

Copilot [always leaves a 'Comment' review](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review), never 'Approve' or 'Request changes' — findings are advisory and do not count toward required approvals. Reviews typically complete in under 30 seconds ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/)). Customize focus via `.github/copilot-instructions.md` or `.github/instructions/**/*.instructions.md`.

### Claude Code Subagents

Claude Code's [subagents documentation](https://code.claude.com/docs/en/sub-agents) includes a `code-reviewer` example — read-only, runs `git diff`, returns findings by priority.

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
---
```

Excluding `Edit` and `Write` is structural: review agents suggest fixes, they do not apply them. For specialized domains, deploy multiple focused reviewers — security, performance, style — rather than one general-purpose agent.

## Structuring Review Output

Free-form comments are hard to triage. Structure findings by severity:

- **Critical** — correctness, security, data integrity
- **High** — test coverage gaps, API contract violations
- **Medium** — style, naming, missing documentation
- **Low** — suggestions, minor improvements

## Calibrating False Positives

Agents over-flag — surfacing style issues in generated code and flagging intentional patterns. False positive rates run 5–15% for well-configured tools, higher when poorly tuned ([Graphite](https://graphite.com/guides/ai-code-review-false-positives)). Tune prompts to specify what to ignore, and apply severity thresholds so low-severity findings are optional.

## When This Backfires

**CRA-only configurations.** An empirical study of 3,109 PRs found CRA-only review achieves a 45% merge rate versus 68% for human-involved review, and 12 of 13 CRAs studied averaged signal ratios below 60% ([arXiv:2604.03196](https://arxiv.org/abs/2604.03196)). Always require at least one human approval.

**PRs exceeding context limits.** Large diffs produce generic, low-signal comments across truncated context. Keep PRs small.

**Agent reviewing its own output.** A reviewer in the same session validates the same assumptions the generating agent made. Route to a fresh-context reviewer ([Loop Strategy Spectrum](../agent-design/loop-strategy-spectrum.md)).

**Skipping human review after agent approval.** The pattern only works if humans remain accountable for design. Treating agent approval as sufficient accumulates architectural debt the agent cannot see.

**Uncalibrated false positive rates.** AI suggestions are adopted at 16.6% versus 56.5% for human suggestions ([arXiv:2603.15911](https://arxiv.org/abs/2603.15911)) — untuned prompts reduce adoption even for correct findings.

## Example

A team configures two review agents for their Python backend repository:

```yaml
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Reviews PRs for security issues — injection, exposed secrets, auth gaps.
tools: Read, Grep, Glob, Bash
model: inherit
---

Check the diff for:
- SQL injection: raw string interpolation in queries
- Exposed secrets: API keys, tokens, passwords in code or config
- Auth gaps: endpoints missing authentication decorators
- Path traversal: unsanitized user input in file operations

Return findings as:
- **Critical**: exploitable vulnerabilities
- **High**: security best-practice violations
- **Medium**: hardening opportunities
```

```yaml
# .claude/agents/style-reviewer.md
---
name: style-reviewer
description: Reviews PRs for style and convention compliance.
tools: Read, Grep, Glob, Bash
model: inherit
---

Check the diff for:
- Naming conventions: snake_case functions, PascalCase classes
- Missing type hints on public function signatures
- Docstrings missing on public functions
- Import ordering violations

Return findings as:
- **High**: public API missing type hints
- **Medium**: naming or docstring violations
- **Low**: import ordering
```

Both agents run on every PR. The security reviewer catches an exposed database URL in a config file and flags it as critical. The style reviewer notes two functions missing type hints as high-severity. Human reviewers skip the mechanical checks entirely and focus on whether the new caching layer belongs at the service level or the repository level.

## Key Takeaways

- Agents handle mechanical checks (style, types, security patterns); humans handle design and architecture judgment
- GitHub Copilot code review leaves non-binding comments and does not block merges — findings are advisory
- [Claude Code Review](../tools/claude/code-review.md) subagents should be read-only — `Edit` and `Write` tools excluded by design
- Structure agent findings by severity; calibrate false positive handling before trusting outputs
- Never have an agent review its own output — independence is structural, not behavioral

## Related

- [Trust Without Verify](../anti-patterns/trust-without-verify.md)
- [Test-Driven Agent Development: Tests as Spec and Guardrail](../verification/tdd-agent-development.md)
- [Incremental Verification: Check at Each Step, Not at the End](../verification/incremental-verification.md)
- [Agentic Code Review Architecture](agentic-code-review-architecture.md)
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md)
- [Self-Improving Code Review Agents — Learned Rules](learned-review-rules.md)
- [Tiered Code Review](tiered-code-review.md)
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md)
- [Review-Then-Implement Loop](review-then-implement-loop.md)
- [Diff-Based Review Over Output Review](diff-based-review.md)
- [Agent-Authored PR Integration: Collaboration Signals That Determine Merge Success](agent-authored-pr-integration.md)
- [Committee Review Pattern](committee-review-pattern.md)
- [Predicting Reviewable Code: Pre-Flagging Functions Reviewers Will Delete](predicting-reviewable-code.md)
- [PR Description Style Lever](pr-description-style-lever.md)
- [Human-AI Review Synergy](human-ai-review-synergy.md)
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md)
