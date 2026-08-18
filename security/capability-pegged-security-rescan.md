---
title: "Capability-Pegged Security Re-Scans: Reviewing Unchanged Code When the Scanner Improves"
term: "Capability-Pegged Security Re-Scan"
description: "Peg whole-codebase security review to scanner capability rather than to your own release cycle, under two conditions: the trigger is measured against your code, and every finding clears an empirical gate."
aliases:
  - release-pegged security review
  - model-triggered re-scan
  - capability-jump re-scan
tags:
  - security
  - code-review
  - tool-agnostic
last_reviewed: 2026-08-18
maturity: emerging
---

# Capability-Pegged Security Re-Scans: Reviewing Unchanged Code When the Scanner Improves

> A security review's coverage belongs to the model that ran it, so a capability jump stales the result while the code sits unchanged.

Two conditions decide whether re-scanning unchanged code is worth the money. Miss either and the measured false-discovery rates make it net-negative.

## The two conditions

- Trigger on a capability measurement against your own code, never on a vendor release announcement. Leaderboard position does not transfer to your setup. On a single benchmark of 344 validated vulnerabilities, [SEC-bench Pro](https://arxiv.org/abs/2605.26548v2) records that Claude Code with Opus 4.6 "tends to time out but solves most instances it completes", so realized coverage depends on the harness a model runs in, not the model alone.
- Gate every finding on reproduction before it reaches an engineer. The [Refute-or-Promote](https://arxiv.org/abs/2604.19049v1) campaign killed roughly 79% of 171 candidates before disclosure, and its worst case is instructive: ten dedicated reviewers unanimously endorsed a Bleichenbacher padding oracle in OpenSSL's CMS module that did not exist, and it "was killed only by a single empirical test".

Without both, the cost side dominates. A project-scale study of five LLM detectors and two static analyzers across 24 active open-source projects found that both kinds of tool "generate substantial warnings but suffer from very high false discovery rates, hindering practical use", at "hundreds of thousands to hundreds of millions of tokens and multi-hour to multi-day runtimes" ([Li et al., 2026](https://arxiv.org/abs/2601.19239v1)).

## Why it works

A security review's coverage is a property of the analyzer, not of the code, so it decays on a schedule the code has no say in. SEC-bench Pro isolates this. Across every configuration on one fixed set of 344 validated vulnerabilities, "the strongest, Codex with GPT-5.5, solves 58% of instances overall", while "GLM-5 solves only 13 of the 344 instances" ([SEC-bench Pro](https://arxiv.org/abs/2605.26548v2)). Nothing about those 344 bugs changed between the two runs. The entire difference in what was found belongs to the analyzer, which is why a clean review dates from the model that produced it rather than from the commit it ran against.

The same paper bounds the claim. That 58% ceiling is on bugs already disclosed, with triggering instructions supplied. A clean re-scan on undisclosed bugs in production code is much weaker evidence, so a capability jump raises the floor and certifies nothing.

## What counts as a trigger

Keep a regression corpus: real defects your own codebase has had, drawn from your CVE history or postmortems, with the fixes reverted on a private branch. Run each candidate model over that corpus first. If it does not beat the incumbent on bugs in your languages and your vulnerability classes, skip the full pass. Running a small corpus costs a fraction of the whole-project figures above, so an otherwise unbounded "whenever a stronger model ships" rule stays affordable as releases accelerate.

Record which model produced each clean result. Once a review has a version attached, "we scanned this last quarter" becomes a checkable statement, not a reassurance.

## How re-scan findings triage differently

Findings from a whole-codebase pass are not pull-request findings with a longer queue.

- The code already shipped and has been running. Reachability and exploitability decide priority, not diff hygiene.
- Volume arrives in one batch rather than across weeks of pull requests, so triage capacity sets the scan's practical scope.
- Reproduction is mandatory, because nothing downstream catches a plausible-but-wrong report before it consumes engineering time.

Scope the pass to surfaces where an escape is expensive. Per-diff coverage stays with the [always-on PR security reviewer](always-on-pr-security-review.md); the re-scan covers resident risk the diff path never reaches.

## Example

Vercel reports running "full deepsec reviews across mission-critical repositories every quarter and whenever a stronger model becomes available, in addition to automated security reviews on every pull request" ([Vercel, 2026](https://vercel.com/blog/everything-hackable-will-get-hacked)). Three triggers stack there: per-diff, calendar, and capability.

Vercel motivates the third trigger with its own DeepSec Bench, on which it says the open-weight Kimi K3 "ranks highest among the open-weight models we evaluated, roughly matching Sonnet 5 and outperforming Opus 4.8". That benchmark and the `deepsec` tool are Vercel's own products, and the closest independent measurement points the other way: SEC-bench Pro reports that open-weight models "struggle" on long-horizon security tasks. The cadence does not depend on open-weight parity, only on capability moving, which both sources support.

## When this backfires

- No reproduction gate. "Plausible-but-wrong reports overwhelm maintainers and degrade credibility for real findings" ([Agarwal, 2026](https://arxiv.org/abs/2604.19049v1)), so the cost lands on the next true positive rather than on the scan that produced the noise.
- Small or low-blast-radius codebases. Multi-day runtimes and hundreds of millions of tokens exceed the value of any plausible finding on an internal tool with no untrusted input.
- Triggers read off general leaderboards. A coding or reasoning benchmark says nothing about your languages, vulnerability classes, or harness.
- Accelerating releases with an unbounded trigger. At monthly release cadence, "whenever a stronger model ships" collapses into continuous scanning and the calendar leg stops meaning anything.
- Treating a clean result as certification. The benchmark ceiling is 58% on known bugs with instructions attached.
- No per-diff review yet. Chasing capability drift while new risk lands unreviewed inverts the order of operations.

## Key Takeaways

- A review's coverage is a property of the model, so it goes stale on model releases rather than on commits.
- Trigger on a measured improvement against a regression corpus of your own past defects, not on a release announcement.
- Re-scan findings need a reproduction step that pull-request findings can survive without.
- Scope capability-triggered passes to high-blast-radius surfaces and leave the rest to per-diff review.
- Attach the model and version to every clean result, so a past scan is a dated claim rather than a standing one.

## Related

- [Always-On Agentic PR Security Review](always-on-pr-security-review.md) — the per-diff and calendar legs this trigger stacks on top of
- [Three-Depth In-Session Security Review](three-depth-in-session-security-review.md) — the per-turn layer below both
- [Restricted-Access Defensive AI](restricted-access-defensive-ai.md) — gating frontier discovery models to vetted defenders, the same dual-use problem from the supply side
- [Security Budget as Token Economics](security-budget-token-economics.md) — how far inference spend scales vulnerability discovery within a single attempt
- [Cross-Repository Security Posture for Agent-Introduced Vulnerabilities](cross-repository-security-posture.md) — turning one finding into an organization-wide sweep
