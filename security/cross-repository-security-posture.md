---
title: "Cross-Repository Security Posture for Agent-Introduced Vulnerabilities"
term: "Cross-Repository Security Posture"
description: "Treat one agent-introduced vulnerability as a class to enumerate and fix across every repository, not a per-repo point-in-time finding."
aliases:
  - cross-repo vulnerability posture
  - organization-wide variant remediation
tags:
  - security
  - tool-agnostic
  - automation
last_reviewed: 2026-07-23
maturity: adopted
---

# Cross-Repository Security Posture for Agent-Introduced Vulnerabilities

> One agent-introduced vulnerability is rarely confined to one repository, so a real security posture enumerates and fixes the whole class everywhere.

When AI coding agents write a growing share of your code, an insecure pattern a scanner flags in one repository is rarely confined to it. The agent that emitted it there tends to emit it wherever it is prompted, so point-in-time, single-repo detection understates the real blast radius — it tells you a fact, not a posture.

## A finding is not a posture

Sourcegraph frames the gap directly: "A finding in one repo is a fact. A security posture means knowing whether that same problem exists everywhere else, and fixing it before it spreads." ([Sourcegraph](https://sourcegraph.com/blog/detection-in-one-repo-isnt-a-security-posture)) The operational test is whether you can answer "which of our repositories carry this same class of issue, directly or transitively?" — and most organizations cannot answer that within the window an attacker needs.

This is the organization-wide layer above two narrower controls. [Blast Radius Containment](blast-radius-containment.md) scopes what one agent can do. [Always-On Agentic PR Security Review](always-on-pr-security-review.md) gates each PR and scans one codebase on a cadence. Neither asks the cross-repo question a single finding should trigger.

## The detect, enumerate, remediate loop

Turn a single detection into a closed loop across the fleet:

- Detect — a scanner, reviewer, or advisory surfaces one instance of an insecure class.
- Enumerate — express the class as a query and run it across every repository to find every variant, including ones whose surface syntax differs.
- Remediate at the scale you detected — open coordinated fixes across all affected repositories, each validated in its own context rather than force-pushed blind.
- Prevent — feed the class back into pre-merge checks so the next instance is caught before it lands. ([Sourcegraph](https://sourcegraph.com/blog/detection-in-one-repo-isnt-a-security-posture))

Remediation is the leg that breaks down at scale: Sourcegraph describes fixing a class across roughly 10,000 repositories, where AI-generated fixes miss surrounding context, detection coverage leaves gaps, and individual repairs stretch into weeks ([Sourcegraph](https://sourcegraph.com/blog/vulnerability-remediation-at-codebase-scale)). Enumerating a class is cheap once modeled as a query; remediating every variant with per-repo validation is where the cost and the timeline actually land.

## Why it works

The posture rests on two mechanisms. First, an AI coding agent samples from a fixed training distribution, so given similar prompts it reproduces the same idiom — an insecure pattern is a repeatable output, not a one-off. An empirical study of Copilot-generated code found security weaknesses in 29.5% of Python and 24.2% of JavaScript snippets, spanning 43 CWEs with eight in the 2023 CWE Top 25 ([arxiv 2310.02059](https://arxiv.org/abs/2310.02059v4)). That makes cross-repo recurrence structural, so enumerating a class is a rational default once you see it once.

Second, variant analysis makes "does this exist elsewhere?" a mechanizable query. Because CodeQL treats code as data, one query "can also pick up logical variants of the problem, helping to identify entire classes of vulnerabilities in one go," and multi-repository variant analysis runs that query "against a list of up to 1,000 repositories" at once ([GitHub](https://github.blog/security/vulnerability-research/multi-repository-variant-analysis-a-powerful-new-way-to-perform-security-research-across-github/)). Detection and remediation scale to the same breadth as the defect.

## When this backfires

The posture adds cost that outweighs its value in several conditions:

- Few repositories. For a handful of services, fleet-enumeration infrastructure costs more than per-repo scanning already covers.
- False-positive economics. An idiom that is unsafe in one repo can be safe in another, so a class query surfaces context-dependent non-issues. When most alerts are false positives, security becomes a bottleneck rather than a safety net ([Invicti](https://www.invicti.com/white-papers/false-positives-in-application-security-whitepaper)). Without an AppSec triage owner, cross-repo findings become noise — the same failure mode that undermines [PR-time security review](always-on-pr-security-review.md).
- Heterogeneous stacks or missing metadata. Enumeration relies on a consistent queryable representation, and polyglot fleets or repos without accurate dependency data cannot be enumerated reliably.
- Blind mass remediation. Pushing one fix across many repositories without per-repo validation can break builds and introduce regressions at scale, so the remediation inherits the vulnerability's blast radius. Validate each fix in context.

## Example

A reviewer flags an unsafe deserialization idiom in one service. Rather than close the ticket, an engineer models the sink as a CodeQL query and runs it through multi-repository variant analysis across the organization's repositories:

```bash
# Model the class once, then enumerate every variant across the fleet.
codeql database create db --language=python
# Run the query across up to 1,000 repositories via MRVA (VS Code CodeQL extension),
# not just the repo where the finding surfaced.
```

GitHub's Security Lab used this approach to detect Android advisories affecting more than 10 million applications from a single modeled query ([GitHub](https://github.blog/security/vulnerability-research/multi-repository-variant-analysis-a-powerful-new-way-to-perform-security-research-across-github/)). The finding becomes a posture: every variant is found, each fix is scoped to its repository, and the query is added to pre-merge checks so the class cannot re-enter.

## Key Takeaways

- One agent-introduced finding is a leading indicator of a class, not an isolated bug — ask "does this exist elsewhere?" before closing it.
- Agent-authored code recurs across repositories because the model reproduces the same idiom wherever prompted.
- Variant analysis turns enumeration into a query that scales to the same breadth as the defect.
- The posture pays off at fleet scale with a triage owner; below that, per-repo scanning and per-PR gating are cheaper.
- Validate remediations per repository — a blind mass fix is itself a distributed defect.

## Related

- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — the per-PR and single-codebase layer this posture sits above
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — per-agent permission scoping, the containment layer below org-wide posture
- [Distributed Cross-PR Attacks in Persistent-State AI Control](distributed-cross-pr-attacks.md) — the offensive mirror: an attacker spreading a payload across many PRs
- [LLM-Pinned Library Versions Carry Systemic CVE Exposure](llm-pinned-vulnerable-versions.md) — another class of agent-introduced risk that recurs across repositories
- [Scanner-as-MCP-Server: Secret and Dependency Scans as Typed Agent Tools](scanner-as-mcp-server.md) — the detection primitive that seeds the enumerate-and-remediate loop
