---
title: "The Security Review Gap in AI-Authored PRs"
description: "Agent-authored security PRs cluster around six CWE categories, yet 52% merge — reviewer heuristics calibrated for human PRs systematically miss AI-specific failure modes."
tags:
  - code-review
  - security
  - arxiv
aliases:
  - AI PR security review gap
  - agentic PR security weaknesses
---

# The Security Review Gap in AI-Authored PRs

> Agent-authored security PRs cluster around six recurring CWE categories, 52.4% are merged despite the flaw rate, and commit-message quality — the main signal reviewers use for human PRs — carries no predictive value for AI PRs.

## The Finding

Rabbi et al. (EASE 2026) filtered 33,000+ agent-authored PRs from GitHub Copilot, Codex, Devin, Cursor, and Claude Code to 675 security-related submissions, combining static analysis with manual classification ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)). Two assumptions break: AI weaknesses are not diverse, and human-PR heuristics do not transfer.

## Six CWEs Account for 80% of Weaknesses

Across 853 vulnerability findings in 104 PRs, six categories dominate ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)):

| CWE | Description | Share |
|---|---|---|
| CWE-1333 | Inefficient regular expression complexity (ReDoS) | 36.2% |
| CWE-78 | OS command injection | 13.0% |
| CWE-22 | Path traversal | 10.3% |
| CWE-134 | Externally-controlled format string | 8.2% |
| CWE-79 | Cross-site scripting | 7.1% |
| CWE-798 | Hard-coded credentials | 5.7% |

LLM-generated regexes reproduce polynomial-backtracking patterns from their training corpus ([Siddiq et al., ICPC 2024](https://s2e-lab.github.io/preprints/icpc24-preprint.pdf)); OWASP catalogues ReDoS as a standard DoS vector ([OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)). SAST rules targeted at these six CWEs cover most of the agent-PR security surface.

## Flawed Patches Still Merge

Of 675 security-related PRs, 52.4% merged, 32.4% closed unmerged, 15.1% remained open; 15.4% contained detected CWEs — review does not filter them out ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)). Of 219 rejections, only 1.8% cited distrust in AI-written code; most were procedural:

| Reason | Share |
|---|---|
| Unknown / no feedback | 38.8% |
| Inactive contributor or thread | 12.3% |
| Introduces bugs or breaks APIs | 10.5% |
| Non-optimal design | 5.9% |
| Does not add value | 5.5% |
| Test failure or missing coverage | 4.1% (new category) |
| Code style / formatting | 3.7% (new category) |
| Distrust in AI-written code | 1.8% |

Reviewers reject on inactivity, test gaps, and style — not on SAST-detectable CWEs. The authors call this an imbalance where "serious flaws pass review while minor issues cause rejection" ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)).

## Commit Message Quality Stops Predicting Acceptance

For human PRs, commit-message quality correlates with acceptance and speed. For agent PRs, the relationship disappears ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)):

- High-quality messages: 45.6% acceptance
- Low-quality messages: 58.0% acceptance
- Mean time-to-close: 4.31 days (high) vs. 4.46 days (low)

Pseudo-R² of 0.23 on the logistic regression confirms limited predictive power. Reviewers rely on different signals for agent PRs — project-level trust, CI pass, surface correctness — none of which track security behaviour.

## Why Review Heuristics Fail on Agent PRs

Reviewer proxies — message care, test scaffolding, change size, contributor history — assume a careful author produces careful code. Agent PRs break the link: a CI-passing patch with a detailed message still ships a polynomial regex. The AIDev corpus of 456K agent PRs shows reviewer engagement as the dominant merge predictor ([arXiv:2507.15003](https://arxiv.org/abs/2507.15003); see [Agent-Authored PR Integration](agent-authored-pr-integration.md)) — a social signal that under-weights security analysis.

## What to Change

- **Target SAST at the six dominant CWEs.** ReDoS analysers, shell-command taint tracking, path-traversal linters, format-string checkers, XSS sinks, and secret scanners cover the empirical majority. Run them as blocking CI gates on agent-authored PRs.
- **Decouple agent-PR review from human-PR heuristics.** Treat commit-message quality and CI pass as non-signals for security. Require an adversarial pass for agent PRs touching regex compilation, `exec`/`subprocess`, path construction, format-string primitives, HTML output, or credentials.
- **Close the procedural-rejection hatch.** 38.8% "unknown" plus 12.3% "inactive" rejections are process failures — a flawed patch timing out is not protection; the same CWE recurs on the next agent run.
- **Require closure-rationale tags.** Structured tags like "risk," "test," or "design" ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)) force reviewers to state whether security properties were verified rather than closing silently.

## When This Backfires

- **Agent populations that rarely touch security surface**: gates add friction without protection when agent PRs are dominated by docs and refactors.
- **Teams without security triage capacity**: SAST rules need a responder; otherwise they generate noise and dull attention.
- **Bounded internal attack surface**: sandboxed CLIs with no untrusted input have little exposure to ReDoS or injection.
- **Single-agent populations**: the CWE distribution aggregates five agents; measure your own before wiring to the six-category pattern.

## Example

An agent PR adds an email validator:

```python
EMAIL_RE = re.compile(r"^([a-zA-Z0-9_\.\-])+@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$")
```

Detailed commit message, passing tests, clean CI — a human-PR heuristic approves. The nested quantifiers `(...)+` over classes that overlap on `-` produce exponential backtracking on crafted input, a textbook CWE-1333 ([OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)). Correct review: a ReDoS analyser as a blocking CI gate on any PR touching `re.compile` surfaces the finding; the reviewer rewrites without nested quantifiers or switches to a linear-time engine like `google/re2`. The commit message and test suite would have missed it.

## Key Takeaways

- Six CWE categories cover 80%+ of weaknesses in agent-authored security PRs — target SAST rules at this set rather than the full CWE Top 25
- 52.4% of security-related AI PRs merge, with only 1.8% of rejections citing distrust in AI code — the review process does not systematically filter on security
- Commit message quality, a strong human-PR signal, has no predictive value for agent PR acceptance or security outcomes
- Procedural rejections (unknown, inactive) account for more than half of rejected PRs — closure is not security confirmation
- Treat agent PRs touching regex, shell, paths, format strings, HTML output, or credentials as high-risk paths requiring adversarial review, regardless of surface quality

## Related

- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — collaboration signals that predict merge success
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — reviewer composition and merge outcomes
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — merge rate as a productivity metric
- [Tiered Code Review](tiered-code-review.md) — risk-based routing for high-risk agent PR paths
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — high-signal review feedback design
- [Security Constitution for AI Code Generation](../security/security-constitution-ai-code-gen.md) — proactive specification-layer defence against the same CWE classes
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — structural precondition for CWE-78 and CWE-22 at runtime

## Sources

- [arXiv:2604.19965](https://arxiv.org/abs/2604.19965) — Rabbi et al. (EASE 2026): primary study
- [Siddiq et al., ICPC 2024](https://s2e-lab.github.io/preprints/icpc24-preprint.pdf) — mechanism behind CWE-1333 dominance
- [OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [arXiv:2507.15003](https://arxiv.org/abs/2507.15003) — AIDev dataset corroboration
