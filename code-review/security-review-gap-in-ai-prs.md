---
title: "The Security Review Gap in AI-Authored PRs"
term: "Security Review Gap"
description: "Agent-authored security PRs cluster around six CWE categories, yet 52% merge. Reviewer heuristics calibrated for human PRs systematically miss AI-specific failure modes."
tags:
  - code-review
  - security
  - arxiv
  - tool-agnostic
aliases:
  - AI PR security review gap
  - agentic PR security weaknesses
last_reviewed: 2026-06-13
maturity: emerging
---

# The Security Review Gap in AI-Authored PRs

> AI-authored security PRs cluster around six CWEs; 52.4% merge despite flaws, and commit-message quality carries no predictive value for security outcomes.

## The finding

Rabbi et al. (EASE 2026) filtered 33,000+ agent-authored PRs from GitHub Copilot, Codex, Devin, Cursor, and Claude Code to 675 security-related submissions, combining static analysis with manual classification ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)). Two assumptions break: AI weaknesses are not diverse, and human-PR heuristics do not transfer.

## Six CWEs account for 80% of weaknesses

Across 853 vulnerability findings in 104 PRs, six categories dominate ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)):

| CWE | Description | Share |
|---|---|---|
| CWE-1333 | Inefficient regular expression complexity (ReDoS) | 36.2% |
| CWE-78 | OS command injection | 13.0% |
| CWE-22 | Path traversal | 10.3% |
| CWE-134 | Externally-controlled format string | 8.2% |
| CWE-79 | Cross-site scripting | 7.1% |
| CWE-798 | Hard-coded credentials | 5.7% |

LLM-generated regexes reproduce polynomial-backtracking patterns from their training corpus ([Siddiq et al., ICPC 2024](https://s2e-lab.github.io/preprints/icpc24-preprint.pdf)). OWASP catalogs ReDoS as a standard denial-of-service vector ([OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)). SAST rules aimed at these six CWEs cover most of the agent-PR security surface.

## Flawed patches still merge

Of 675 security-related PRs, 52.4% merged, 32.4% closed unmerged, 15.1% remained open. 15.4% contained detected CWEs. Review does not filter them out ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)). Of 219 rejections, only 1.8% cited distrust in AI-written code. Most were procedural:

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

Reviewers reject on inactivity, test gaps, and style, not on SAST-detectable CWEs. The authors call this an imbalance where "serious flaws pass review while minor issues cause rejection" ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)).

## Commit message quality stops predicting acceptance

Commit-message quality correlates with acceptance and speed for human PRs. For agent PRs, the relationship disappears ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)):

- High-quality messages: 45.6% acceptance
- Low-quality messages: 58.0% acceptance
- Mean time-to-close: 4.31 days (high) and 4.46 days (low)

Pseudo-R² of 0.23 on the logistic regression confirms limited predictive power. Reviewers rely on different signals for agent PRs (project-level trust, CI pass, surface correctness), none of which track security behavior.

## Why review heuristics fail on agent PRs

Reviewer proxies (message care, test scaffolding, change size, contributor history) assume a careful author produces careful code. Agent PRs break the link: a CI-passing patch with a detailed message still ships a polynomial regex. A regression on 33,596 agent-authored PRs shows reviewer engagement as the strongest single merge predictor ([arXiv:2602.19441](https://arxiv.org/abs/2602.19441); see [Agent-Authored PR Integration](agent-authored-pr-integration.md)), a social signal that under-weights security analysis.

## What to change

- Target SAST at the six dominant CWEs. ReDoS analyzers, shell-command taint tracking, path-traversal linters, format-string checkers, XSS sinks, and secret scanners cover the empirical majority. Run them as blocking CI gates on agent-authored PRs.
- Decouple agent-PR review from human-PR heuristics. Treat commit-message quality and CI pass as non-signals for security. Require an adversarial pass for agent PRs touching regex compilation, `exec`/`subprocess`, path construction, format-string primitives, HTML output, or credentials.
- Close the procedural-rejection hatch. 38.8% "unknown" plus 12.3% "inactive" rejections are process failures. A flawed patch timing out is not protection. The same CWE recurs on the next agent run.
- Require closure-rationale tags. Structured tags like "risk," "test," or "design" ([arXiv:2604.19965](https://arxiv.org/abs/2604.19965)) force reviewers to state whether security properties were verified rather than closing silently.

## When this backfires

- Agent populations that rarely touch security surface: gates add friction without protection when agent PRs are dominated by docs and refactors.
- Teams without security triage capacity: SAST rules need a responder, or they generate noise and dull attention.
- Bounded internal attack surface: sandboxed CLIs with no untrusted input have little exposure to ReDoS or injection.
- Single-agent populations: the CWE distribution aggregates 5 agents, so measure your own before wiring to the six-category pattern.

## Example

An agent PR adds an email validator:

```python
EMAIL_RE = re.compile(r"^([a-zA-Z0-9_\.\-])+@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$")
```

A human-PR heuristic approves on a detailed commit message, passing tests, and clean CI. The nested quantifiers `(...)+` over classes that overlap on `-` produce exponential backtracking on crafted input, a textbook CWE-1333 ([OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)). Correct review puts a ReDoS analyzer as a blocking CI gate on any PR touching `re.compile`, which surfaces the finding. The reviewer rewrites without nested quantifiers, or switches to a linear-time engine like `google/re2`. The commit message and test suite would have missed it.

## Key Takeaways

- Six CWE categories cover 80%+ of weaknesses in agent-authored security PRs: target SAST rules at this set rather than the full CWE Top 25
- 52.4% of security-related AI PRs merge, and only 1.8% of rejections cite distrust in AI code: do not treat a merge, or the absence of a distrust-based rejection, as evidence a PR is secure
- Commit message quality, a strong human-PR signal, has no predictive value for agent PR acceptance or security outcomes: do not use message quality or CI status as a review-priority signal for agent-authored PRs
- Procedural rejections (unknown, inactive) account for more than half of rejected PRs: closure is not security confirmation
- Treat agent PRs touching regex, shell, paths, format strings, HTML output, or credentials as high-risk paths that require adversarial review and a blocking SAST gate, regardless of surface quality

## Related

- [Agent-Authored PR Integration](agent-authored-pr-integration.md) — collaboration signals that predict merge success
- [CRA-Only Review and the Merge Rate Gap](cra-merge-rate-gap.md) — reviewer composition and merge outcomes
- [Agent PR Volume vs. Value](agent-pr-volume-vs-value.md) — merge rate as a productivity metric
- [Tiered Code Review](tiered-code-review.md) — risk-based routing for high-risk agent PR paths
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — high-signal review feedback design
- [Security Constitution for AI Code Generation](../security/security-constitution-ai-code-gen.md) — proactive specification-layer defense against the same CWE classes
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — structural precondition for CWE-78 and CWE-22 at runtime
- [Supply-Chain Security Debt in Agent Pull Requests](../security/supply-chain-security-debt-agent-prs.md) — the complementary supply-chain view: where agent-PR security debt concentrates outside code-level CWEs

## Sources

- [arXiv:2604.19965](https://arxiv.org/abs/2604.19965) — Rabbi et al. (EASE 2026): primary study
- [Siddiq et al., ICPC 2024](https://s2e-lab.github.io/preprints/icpc24-preprint.pdf) — mechanism behind CWE-1333 dominance
- [OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [arXiv:2507.15003](https://arxiv.org/abs/2507.15003) — AIDev dataset corroboration
- [arXiv:2602.19441](https://arxiv.org/abs/2602.19441) — reviewer engagement as the strongest single merge predictor (regression on 33,596 agent-authored PRs)
