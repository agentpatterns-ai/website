---
title: "Per-Language Merge Gate Coverage for Code Scanning"
term: "Per-Language Gate Coverage"
description: "GitHub's AI Scan runs only on languages CodeQL does not cover, and its findings cannot be required in a ruleset. Audit, per file type, which code scanning findings can actually fail a check."
tags:
  - security
  - code-review
  - copilot
aliases:
  - advisory versus required code scanning
  - AI Scan merge blocking
  - which code scanning findings block a merge
last_reviewed: 2026-10-18
maturity: emerging
status: current
---

# Per-Language Merge Gate Coverage for Code Scanning

> Your code scanning coverage now reaches further than your merge gate does, so audit per file type which finding can fail a check.

Do this audit only if your pull requests actually change files CodeQL does not analyze. List those file types, and for each one write down which code scanning finding can fail a required check. On a repository whose diffs are mostly Java and Python the answer is already known. For Terraform, Dockerfiles, PHP, or shell scripts, AI Scan adds advisory findings. Also record any separate scanner whose required check covers those files.

Two sentences from GitHub's own documentation produce the gap. The last of AI Scan's three trigger conditions is this: "A pull request that is not from a fork or created by Dependabot contains changes in a supported language or framework that CodeQL does not cover" ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)). Its output is then barred from the gate: "AI Scan findings are advisory. They do not fail the code scanning check and cannot block pull request merges through ruleset requirements" ([GitHub Changelog, 2026-10-15](https://github.blog/changelog/2026-10-15-ai-scan-for-pull-requests-generally-available)). Read together, these rules show that AI Scan adds no blocking finding for those file types. Other configured checks can still block them. The named examples are "PHP, Shell/Bash, Terraform configuration (HCL), Dockerfiles, JSP for Java, and Blazor for C#" ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)).

Date this coverage audit. GitHub files the restriction under Limitations, worded "AI Scan findings cannot yet be used in rulesets to enforce merge requirements" ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)). The documentation describes the current behavior; it does not promise when that behavior will change.

The organization security overview reports AI Scan findings over time ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)).

## Why it works

Repeated runs can expose scanner variability. This is a separate question from accuracy and from whether GitHub lets a finding block a merge. A 300-run benchmark over identical JavaScript shows where the two scanner types part. The deterministic comparator "sits at that corner with 100.0% Snyk-reference F1 and 0.0 percentage-point standard deviation because it reproduced its reference set deterministically", while the model's output splits in two ([Tal et al., 2026](https://arxiv.org/abs/2606.15762v1)). Findings that matched the reference held up, 134 of 158 recurring in all five repetitions. The extra findings did not: "Across 250 model runs, 80 of 161 unique unmatched findings appeared in only one of five identical repetitions, while only 22 appeared in all five." So "a developer could get a materially different review queue depending on which run happened to execute". Snyk defines that benchmark's reference set. The 100% therefore measures reproduction of that set.

That benchmark did not test AI Scan. It cannot establish AI Scan's variability, precision, or the reason GitHub made its findings advisory.

Deterministic output can still contain false positives. In a project-scale study, "CodeQL reports 6,345 warnings on gpac for CWE-476 with an SFDR of 76.00%", and across the Java projects "CodeQL has a lower overall SFDR of 77.00%" than Semgrep's 92.71% ([Li et al., 2026](https://arxiv.org/abs/2601.19239v2)). Those rates come from Codex labeling up to 300 sampled warnings per tool per project, validated against manual annotation. A required status check establishes enforcement; its presence alone establishes no accuracy rate.

Untrusted pull requests raise a separate model-review risk. GitHub's cited documentation does not give this risk as the reason for its fork exclusion. The diff is the substance under review, but a model reads the pull request description too. An iterative metadata-framing attack succeeded "in 32/33 (97%) cases, exploiting a fundamental asymmetry: attackers can iteratively refine attacks against a local clone of the review pipeline, while defenders have only one chance to detect them" ([Alexopoulos et al., 2026](https://arxiv.org/abs/2603.18740v5)). That experiment tested Claude Code and CodeRabbit over 33 CVEs. It supplies no attack-success estimate for AI Scan.

## When this backfires

- Your diffs rarely touch an uncovered language. AI Scan then produces nothing most of the time, and the partition is accurate and useless.
- Your repository is mostly PHP, HCL, or shell. The audit returns an empty blocking column and does not fill it. One way to close the gap is to add a separate required check from a scanner that covers the missing languages. That is this page's suggestion, not a GitHub-documented procedure.
- You accept fork pull requests. AI Scan skips them, so the advisory column is blank for those pull requests.
- A hard credit budget is in force. "If a hard budget leaves no Code Security AI credits available, AI Scan cannot produce findings" ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)). An empty findings list alone does not establish that a scan ran. Check execution and credit availability separately.
- Review capacity is already the constraint. Across LLM review comments at Atlassian, "many of the LLM-generated comments are not resolved by developers (60%-70%)", with readability highest at 43.3% (586/1,354) and bugs at 41.9% (399/952) ([Goldman et al., 2025](https://arxiv.org/abs/2510.05450v1)). Those were general review comments classified by an LLM judge at moderate agreement with annotators. They do not estimate the resolution rate of AI Scan findings.
- The org already turned it on. Enablement is immediate across eligible repositories, and "qualifying pull requests can consume Code Security AI Credits before" a repository admin opts out ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)).

The audit identifies missing enforcement but does not supply it. GitHub describes the scan trigger: "Scans run when a pull request is created and after each new commit, as they do for CodeQL" ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)). This trigger does not establish that repeated scans produce identical findings.

## Example

The audit is one row per file type in your diff, and the only column that matters is the last one. Filling it from GitHub's own documentation gives this, for the languages the docs name as AI Scan's:

| File type in the diff | Scanner that reports | Can a finding fail the check? |
|---|---|---|
| PHP | AI Scan | No |
| Shell/Bash | AI Scan | No |
| Terraform (HCL) | AI Scan | No |
| Dockerfile | AI Scan | No |
| JSP (Java) | AI Scan | No |
| Blazor (C#) | AI Scan | No |
| Any language CodeQL analyzes | CodeQL | Yes, via the code scanning check |

The last row is the only one that can be made required. Everything above it is advice: AI Scan "runs automatically on pull requests when code scanning and the repository's effective AI Scan setting are enabled", and its findings "do not fail the code scanning check" ([GitHub Changelog, 2026-10-15](https://github.blog/changelog/2026-10-15-ai-scan-for-pull-requests-generally-available)). Check your own language list against [Code scanning with CodeQL](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning) to find the complete supported set. GitHub's own limitations list says so: "Detection categories and supported languages may change as the feature evolves" ([GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/ai-powered-security-detections)).

## Key Takeaways

- AI Scan's trigger and its gate exclusion are two separate sentences in GitHub's documentation and changelog, and the gap only appears when you read them together.
- Record the audit per file type. Keep the scanner and required-check configuration beside each entry.
- Enforcement and precision need separate checks. CodeQL's own sampled false-discovery rate runs 76-77% in a project-scale study ([Li et al., 2026](https://arxiv.org/abs/2601.19239v2)).
- Date the audit and schedule a recheck of GitHub's current ruleset limitation.
- Track execution separately from findings. An exhausted credit budget prevents findings.

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — the other sense of advisory, where a control fails because the model resolves it alongside the task rather than because a platform withheld the gate
- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — the coverage question split by time instead of by language
- [Capability-Pegged Security Re-Scans](capability-pegged-security-rescan.md) — when to re-run a scanner over code that has not changed, and the false-discovery rates that decide it
- [Out-of-Query Evidence for Agent-Fixed Code Scanning Alerts](../verification/out-of-query-evidence-code-scanning-alerts.md) — the adjacent question on the same alerts, whether a re-run query is evidence the fix worked
- [Enforcing Who and What Can Trigger an Agent's CI Run](workflow-execution-protections.md) — fork pull requests as a trust boundary in the Actions half of the same pipeline
