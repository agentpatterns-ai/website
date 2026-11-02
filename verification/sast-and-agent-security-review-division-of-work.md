---
title: "Dividing Security Review Between a Static Analyzer and an Agent"
term: "SAST-Agent Division of Work"
description: "On one 108-vulnerability benchmark, Snyk Code and an agent security review each missed vulnerabilities the other found, and the tested built-in review policy excluded or restricted reporting in three vulnerability classes."
tags:
  - testing-verification
  - security
  - tool-agnostic
  - arxiv
aliases:
  - SAST plus agent security review
  - static analysis and AI security agents division of work
  - VulnBench 2.0 coverage split
last_reviewed: 2026-10-31
maturity: emerging
---

# Dividing Security Review Between a Static Analyzer and an Agent

> A static analyzer and an agent security review each missed vulnerabilities the other found; together they reached 101 of 108 in one benchmark.

Run both. The evidence for that is one benchmark from one vendor, and it also shows why the agent half needs a check on its own prompt.

## What the benchmark measured

Tal and colleagues scored nine configurations on Snyk VulnBench 2.0: 108 reference vulnerabilities in 20 open-source web applications. A finding earns credit only when its class matches and it locates the attacker-controlled source and the dangerous sink, each within two lines. Section 2.5 relaxes this for flows with fewer than three locations. A one-location flow matches on that location. A two-location flow matches on either endpoint. Both endpoints are required for flows with three or more locations. Detection is blind, and each configuration ran once per application ([arXiv:2610.38617v1](https://arxiv.org/abs/2610.38617v1)).

| Configuration | Matched of 108 | Macro recall |
|---|---|---|
| Snyk Code CLI 1.1305.1 | 89 | 82.4% |
| Claude Code `/security-review`, Opus 5, xhigh | 85 | 79.3% |
| Claude Code `/security-review` plus Snyk MCP, Opus 5, medium | 80 | 75.2% |
| Claude Code `/security-review`, Sonnet 5, xhigh | 73 | 67.0% |
| Codex Security 0.1.24, GPT-5.6 Luna, xhigh | 45 | 41.2% |
| Codex Security 0.1.24, GPT-5.6 Terra, xhigh | 35 | 30.1% |
| Codex Security 0.1.24, GPT-5.6 Sol, xhigh | 34 | 29.2% |

DeepSec 2.3.7 scored 37.5% with Opus 5 and 2.5% with GPT-5.6 Sol, and the paper does not rank it. DeepSec "does not label which location is the source and which the sink", so those rows measure localized recall and are not comparable with the table above ([arXiv:2610.38617v1](https://arxiv.org/abs/2610.38617v1)).

## How the work divides

Snyk Code and Opus 5 at xhigh together reached 101 of 108 on the frozen reference set, "the ceiling of all seven comparable configurations combined". Section 7.2 discloses one reference entry that no finding can match; correcting it changes the union to 102. They disagree on 28 vulnerabilities, split 16 to 12. The paper says the corpus "is too small to tell apart from chance" ([arXiv:2610.38617v1](https://arxiv.org/abs/2610.38617v1)). The study cannot distinguish the two recalls, and section 3.1 warns against reading that as equality. Do not use them as a ranking.

The split by kind is clearer than the recall gap:

- Opus 5 at xhigh added 12 vulnerabilities that Snyk Code missed. Seven were cross-file, including authorization classes.
- Snyk Code found 10 that none of the six endpoint-aware AI configurations matched, across six classes that include open redirect, prototype pollution and path traversal.
- Cross-file cross-site scripting defeated every configuration. None matched more than 4 of its 7 vulnerabilities.

The cost of combining is triage. Snyk Code's pooled precision is 20.9% (89 of 425 findings) against 74.6% (85 of 114) for Opus 5 at xhigh. The paper treats both as lower bounds, because the reference set may omit real vulnerabilities. The agent reports also included at least seven real vulnerabilities outside the reference set ([arXiv:2610.38617v1](https://arxiv.org/abs/2610.38617v1)).

Cost tracked coverage loosely. Snyk Code scanned all 20 applications in about 8 minutes, and every AI configuration took hours. Known model spend was $1,594.08. GPT-5.6 Sol cost 35.0 times as much as Luna and matched 11 fewer vulnerabilities ([arXiv:2610.38617v1](https://arxiv.org/abs/2610.38617v1), sections 5.1 to 5.3).

## The review policy is a second variable

The tested Claude Code 2.1.251 review policy excludes ReDoS. It asks for prototype pollution and open redirect only at "extremely high confidence". In a control run with the policy removed, the same model at the same effort matched 16 of the 20 reference vulnerabilities in those classes. With `/security-review` it matched 9. On the 78 vulnerabilities outside React and Angular XSS, the control run matched 71 and the tested policy 69 ([arXiv:2610.38617v1](https://arxiv.org/abs/2610.38617v1)).

If you wrote your own review prompt, audit it for class exclusions before you read its recall as the model's ceiling. See [Prompt as Security Knob](../patterns/anti-patterns/prompt-as-security-knob.md) for the wider case.

## When the evidence does not carry

- All authors work for Snyk, which sells Snyk Code. Five of the 20 applications had appeared in Snyk product demonstrations, and Snyk Code informed the curation format ([arXiv:2610.38617v1](https://arxiv.org/abs/2610.38617v1)).
- Every cell ran once, so run-to-run variation of the AI configurations is unmeasured.
- The policy control is one run per arm on 19 of 20 applications, run about a month after the main runs. The paper says model provider changes "cannot be excluded".
- The paper does not record which model seeded which vulnerability.

## Key Takeaways

- Neither engine alone reached 101 of 108. Use both and plan for a larger triage queue.
- The 16-to-12 disagreement split does not separate the two tools in this study. Do not pick a winner from 82.4% against 79.3%.
- Expect the agent to add cross-file findings and the static tool to add class coverage the agent skipped.
- Read your agent's review prompt for excluded classes. Removing the policy lifted one run from 9 to 16 of 20.
- Treat the numbers as a vendor study: single runs, 20 applications, Snyk authors.

## Related

- [Always-On Agentic PR Security Review](../security/always-on-pr-security-review.md) — the PR-time reviewer and scheduled scanner pairing this split informs.
- [Three-Depth In-Session Security Review](../security/three-depth-in-session-security-review.md) — layering a deterministic check under agentic review.
- [Treating a Clean Static Scan as Security Evidence](../patterns/anti-patterns/static-clean-as-security-evidence.md) — the reverse failure, where a clean static run is read as proof.
- [Model Confidence as Security Verification](../patterns/anti-patterns/model-confidence-as-security-verification.md) — why the agent half needs its own check.
- [Prompt as Security Knob](../patterns/anti-patterns/prompt-as-security-knob.md) — how prompt wording changes security outcomes.
- [Deterministic Guardrails Around Probabilistic Agents](deterministic-guardrails.md) — what the deterministic layer buys.
- [When a Second Model Helps in LLM Review](cross-model-review-independence.md) — the same different-not-better finding for model pairs.
