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

Human reviewers excel at judgment; agents excel at checklists. Agent-assisted code review assigns each to the work it does well.

The agent handles the first pass: style consistency, type correctness, test coverage gaps, security patterns, naming conventions. Humans then focus on design, architecture fit, and scalability — questions that require judgment agents do not reliably provide.

## How It Works

### GitHub Copilot Code Review

GitHub Copilot reviews PRs directly in the pull request interface. [Per the documentation](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review), Copilot "always leaves a 'Comment' review, not an 'Approve' review or a 'Request changes' review" — findings are non-binding and do not count toward required approvals. Reviews typically complete in under 30 seconds [unverified].

Customize focus areas through instruction files at `.github/copilot-instructions.md` or `.github/instructions/**/*.instructions.md` to target security checklists, readability standards, or domain-specific conventions.

### Claude Code Subagents

Claude Code's [subagents documentation](https://code.claude.com/docs/en/sub-agents) includes a `code-reviewer` example. A review subagent is read-only (no `Edit` or `Write` tools), runs `git diff` to see changes, and returns findings by priority.

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
---
```

The `tools` field excludes `Edit` and `Write` — review agents suggest fixes, they do not apply them. This is a structural constraint, not a behavioral one.

For specialized domains, deploy multiple focused review agents — security, performance, style — rather than one general-purpose reviewer.

## Structuring Review Output

Unstructured free-form comments from agents are hard to triage. Structure findings by severity:

- **Critical** — correctness issues, security vulnerabilities, data integrity risks
- **High** — test coverage gaps on changed code paths, API contract violations
- **Medium** — style inconsistencies, naming issues, documentation missing
- **Low** — suggestions, minor improvements

## Calibrating False Positives

Agents over-flag — surfacing style issues in generated code and flagging intentional patterns as problems [unverified]. Mitigations:

1. **Tune the prompt** — specify what to check and what to ignore so intentional patterns are not flagged.
2. **Severity thresholds** — treat low-severity findings as optional. Focus human attention on critical and high findings.

## Constraints

**Context limits constrain PR size.** Large PRs exceed context limits and produce lower-quality reviews — a structural argument for keeping PRs small.

**Agents should not review their own output.** A review agent in the same session validates the same assumptions the generating agent made. Route to a fresh-context reviewer instead. See [Loop Strategy Spectrum](../agent-design/loop-strategy-spectrum.md) for when fresh-context vs accumulated-context loops apply.

**Agents are not sufficient alone.** Agent review reduces mechanical overhead but does not replace human review.

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

## Unverified Claims

- False positive rates from review agents are high initially [unverified]
- Reviews typically complete in under 30 seconds [unverified]

## Related

- [Trust Without Verify](../anti-patterns/trust-without-verify.md)
- [Test-Driven Agent Development: Tests as Spec and Guardrail](../verification/tdd-agent-development.md)
- [Incremental Verification: Check at Each Step, Not at the End](../verification/incremental-verification.md)
- [Agentic Code Review Architecture](agentic-code-review-architecture.md)
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
