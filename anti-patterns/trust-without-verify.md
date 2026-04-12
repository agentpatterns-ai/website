---
title: "Trust Without Verify: Skipping Agent Output Checks"
description: "Accepting agent output as correct because it looks polished, without independent verification. Polished output does not correlate with accuracy."
tags:
  - testing-verification
---

# Trust Without Verify

> Accepting agent output as correct because it looks polished — without independent verification.

## The Pattern

Agent output is seductively plausible. Well-formatted prose with inline citations looks authoritative. Code that compiles looks correct. None of these surface signals correlate reliably with correctness.

The mistake is using output quality as a proxy for accuracy. An agent can produce hallucinated URLs, fabricated statistics, and plausible-but-wrong claims — all in grammatically perfect prose.

## Symptoms

- Citing a source without fetching it to confirm the claim
- Running code that "looks right" without executing tests
- Accepting a technical explanation because it sounds authoritative
- Skipping diff review because the agent's summary is clear

## Why It Happens

Fluency, formatting, and confidence are mistaken for correctness. Agents are trained to produce coherent responses — a separate objective from accuracy. The correlation between surface polish and correctness is weak — fluent explanations systematically increase user confidence without reliably improving accuracy ([Bhatt et al., 2025](https://arxiv.org/abs/2604.03237)).

Agents are most dangerous when almost right. A fully wrong answer is easy to catch; a mostly correct answer with one subtle error propagates undetected.

## Fix

Verify independently — not by re-reading the output, but by checking against external ground truth:

- **Fetch cited URLs.** Confirm the source exists and says what the agent claims.
- **Run the code.** Compile, execute tests, check edge cases. "Compiles" and "correct" are different properties.
- **Cross-reference claims.** Look up assertions in official documentation, not in the agent's summary of it.
- **Review the diff.** Diffs are easier to verify than full artifacts.

If something can be checked programmatically, check it automatically. Linters, type checkers, and test suites are verification, not overhead.

## When This Backfires

Constant verification has a cost. Over-verifying introduces its own failure modes:

- **Verification theater**: Running tests that don't cover the actual change, then treating a passing test suite as ground truth. The motion of verification without the substance.
- **Alert fatigue**: Automated checks that fire too often train reviewers to dismiss failures. When every warning is noise, real errors get approved.
- **Bottleneck on low-stakes output**: Applying the same scrutiny to a one-off throwaway script as to production auth code destroys the productivity benefit of AI assistance. Reserve manual verification for high-stakes, irreversible, or security-critical outputs.

The fix is calibrated verification, not universal paranoia.

## Progressive Trust

Verify all output from new configurations. Spot-check proven ones. Always verify high-stakes outputs (security, production config, financial data) regardless of track record.

## Example

### Before — merged without testing

A developer asks the agent to add email validation. The agent produces a clean function with a comment citing "RFC 5322 compliance":

```python
def is_valid_email(email: str) -> bool:
    """Validate email address (RFC 5322 compliant)."""
    pattern = r"^[a-zA-Z0-9._%\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
```

The developer merges it. The regex silently rejects valid `+` tagged addresses like `user+tag@example.com` — a subtle bug hidden behind authoritative presentation.

### After — tested before merging

The developer runs the function against edge-case emails before merging:

```python
assert is_valid_email("user+tag@example.com")  # FAILS
```

The test catches the missing `+` in the character class. The developer asks the agent to fix it, and the corrected regex is verified before merge.

## Key Takeaways

- "Looks right" is not a verification method
- Output fluency is independent of correctness; agents are most dangerous when almost right
- Automate verification; make it the default, not the exception

## Related

- [Incremental Verification](../verification/incremental-verification.md)
- [Test-Driven Agent Development](../verification/tdd-agent-development.md)
- [Agent-Assisted Code Review](../code-review/agent-assisted-code-review.md)
- [Assumption Propagation](assumption-propagation.md)
- [The Anthropomorphized Agent](anthropomorphized-agent.md)
- [Happy Path Bias](happy-path-bias.md) — agents skip error handling, producing code that compiles but fails in production
- [Context Poisoning](context-poisoning.md) — unchecked hallucinations propagate as trusted premises
- [Comprehension Debt](comprehension-debt.md) — merging agent output without understanding it compounds into unverifiable code
- [The Yes-Man Agent](yes-man-agent.md) — agents that execute without pushback ship the same unverified errors at machine speed
