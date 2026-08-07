---
title: "Agent-Assisted Code Review: Agents as PR First Pass"
term: "Agent-Assisted Code Review"
description: "Use agents to handle mechanical review checks before human review, freeing humans for architecture and design judgment. Human reviewers are better at judgment"
tags:
  - testing-verification
  - code-review
  - tool-agnostic
aliases:
  - AI Code Review
  - Automated PR Review
last_reviewed: 2026-06-13
maturity: established
---

# Agent-Assisted Code Review: Agents as PR First Pass

> Agent-assisted code review routes the mechanical first pass — style, types, security patterns, test coverage — to an agent, reserving human reviewers for the design and architecture judgment that agents cannot reliably provide.

## The technique

Human reviewers excel at judgment. Agents excel at checklists. The agent handles the first pass — style consistency, type correctness, test coverage gaps, security patterns, naming conventions — while humans focus on design, architecture fit, and scalability.

This works by reallocating attention. Take repetitive pattern-matching off the human review queue, and reviewers can focus on architecture. An interview study of 20 engineers reports that engagement with AI-assisted review is distinct from peer review along cognitive, emotional, and behavioral dimensions ([arXiv:2501.02092](https://arxiv.org/abs/2501.02092)).

## How it works

### GitHub Copilot code review

Copilot [always leaves a 'Comment' review](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review), never 'Approve' or 'Request changes' — findings are advisory and do not count toward required approvals. Reviews typically complete in under 30 seconds ([GitHub Blog](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/)). Customize focus via `.github/copilot-instructions.md` or `.github/instructions/**/*.instructions.md`.

### Claude Code subagents

Claude Code's [subagents documentation](https://code.claude.com/docs/en/sub-agents) includes a `code-reviewer` example — read-only, runs `git diff`, returns findings by priority.

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
---
```

Excluding `Edit` and `Write` is structural: review agents suggest fixes, they do not apply them. For specialized domains, run several focused reviewers — security, performance, style — rather than one general-purpose agent.

## Structuring review output

Free-form comments are hard to triage. Structure findings by severity:

- Critical — correctness, security, data integrity
- High — test coverage gaps, API contract violations
- Medium — style, naming, missing documentation
- Low — suggestions, minor improvements

## Calibrating false positives

Agents over-flag — surfacing style issues in generated code and flagging intentional patterns. False positive rates run 5–15% for well-configured tools, higher when poorly tuned ([Graphite](https://graphite.com/guides/ai-code-review-false-positives)). Tune prompts to specify what to ignore, and apply severity thresholds so low-severity findings are optional.

## When this backfires

Dropping the human is the failure with the hardest number attached. An empirical study of 3,109 PRs found CRA-only review achieves a 45% merge rate against 68% for human-involved review, and 12 of 13 CRAs studied averaged signal ratios below 60% ([arXiv:2604.03196](https://arxiv.org/abs/2604.03196)). Require at least one human approval.

Size breaks it differently. A diff past the context limit gets truncated, and what comes back is generic comment spread thinly over the fragments the agent did see. Keep PRs small — see [agent-driven PR slicing](agent-driven-pr-slicing.md).

Self-review is subtler. A reviewer running in the same session validates the assumptions that produced the code, so route to a fresh-context reviewer instead ([Loop Strategy Spectrum](../loop-engineering/loop-strategy-spectrum.md)).

Accountability decays without a failing signal. Treat agent approval as sufficient and architectural debt accumulates exactly where the agent cannot see it, because nobody is answerable for design any more.

Calibration decides whether any of this gets used at all. AI suggestions are adopted at 16.6% against 56.5% for human suggestions ([arXiv:2603.15911](https://arxiv.org/abs/2603.15911)), and an untuned prompt depresses adoption even for findings that are correct.

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

## FAQ

**Why do agent reviews get vaguer on large pull requests?**

Diffs that exceed the model's context limit force truncation, and the agent produces generic, low-signal comments spread across the fragments it did see. That is why PR size matters here: keep each PR small enough that the whole diff fits, so findings stay specific to the changed lines instead of restating generalities.

**Should I run one review agent or several focused ones?**

Run several. For specialized domains, separate security, performance, and style reviewers beat one general-purpose agent, because each carries a narrower checklist and its own severity scheme. The example on this page runs a security reviewer and a style reviewer on every PR: the security agent flags an exposed database URL as critical while the style agent reports missing type hints.

**What false-positive rate should I expect, and how does it affect adoption?**

False positives run 5–15% for well-configured tools and higher when poorly tuned ([Graphite](https://graphite.com/guides/ai-code-review-false-positives)). Adoption tracks that calibration: AI suggestions are taken up at 16.6% against 56.5% for human suggestions ([arXiv:2603.15911](https://arxiv.org/abs/2603.15911)), and untuned prompts depress adoption even for correct findings. Specify what to ignore, and set severity thresholds so low-severity output stays optional.

## Key Takeaways

- Split the queue by what each reviewer is good at, then hold the line: the moment humans stop owning design, the agent's clean pass starts reading as approval it was never scoped to give
- Advisory by construction is a feature, not a limitation. Because [Claude Code Review](../tools/claude/code-review.md) subagents and Copilot both comment without approving, neither can be mistaken for the required review
- Withholding `Edit` and `Write` from a reviewer is what keeps its findings falsifiable — an agent that can apply its own fix has no incentive to be right about it
- Calibrate before you trust, not after. At a 16.6% adoption rate the failure is invisible: correct findings and false positives are both simply ignored
- Independence has to be structural. An agent asked to review itself will agree, because it is re-deriving the same assumptions rather than testing them

## Related

- [Trust Without Verify](../patterns/anti-patterns/trust-without-verify.md)
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
