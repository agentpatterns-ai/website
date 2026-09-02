---
title: "Capturing Dismissal Reasons for Agent Review Findings"
term: "Dismissal Reason Capture"
description: "Record why a human rejected an agent review finding, in a closed vocabulary read back per rule — the two conditions that separate a precision measurement from an extra click."
tags:
  - code-review
  - human-factors
  - copilot
aliases:
  - resolution reasons
  - why a review comment was dismissed
  - structured dismiss reasons
last_reviewed: 2026-08-28
maturity: emerging
---

# Capturing Dismissal Reasons for Agent Review Findings

> A dismissal reason pays only where you can read it back per rule and the vocabulary separates "the finding is wrong" from "right, not here".

An agent reviewer's precision is invisible in the PR timeline, because a comment someone fixed and a comment someone rejected both end up resolved. Recording which one it was turns that into data, at the cost of one dropdown on an action people already take. Two things have to be true before the record is worth the click. You must be able to read the reason back through an API, grouped by the rule that fired. And the vocabulary must distinguish an incorrect finding from a correct one the team declined.

## What GitHub shipped, and where it goes

Copilot code review added a dropdown next to the resolve button on 2026-08-27. A reviewer picks "Addressed", "Won't fix", or "Incorrect." The changelog names the destination: "Selecting one of these options provides valuable feedback to the product team and helps improve the product" ([GitHub Changelog](https://github.blog/changelog/2026-08-27-copilot-code-review-resolution-reasons-and-expanded-capabilities)). It flows to GitHub. No repository field carries it, and the Copilot documentation already states that the loop does not close locally: "Copilot may repeat the same comments again, even if they have been dismissed" or downvoted ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review)).

The dropdown is a vote. Both conditions fail today.

## The shape that does work

GitHub ships a version that meets both conditions, on the security side of the same product. Dismissing a code scanning alert requires a reason from a closed set: `dismissed_reason` is "Required when the state is dismissed" and takes `false positive`, `won't fix`, `used in tests`, or `mitigated`. Free text lives separately in `dismissed_comment`, and both come back on every alert from `GET /repos/{owner}/{repo}/code-scanning/alerts` ([GitHub REST API](https://docs.github.com/en/rest/code-scanning/code-scanning)). `mitigated` arrived on 2026-08-20 because "won't fix" was hiding a distinct decision, where the code is still vulnerable but a firewall or network policy contains it ([GitHub Changelog](https://github.blog/changelog/2026-08-20-code-scanning-adds-a-mitigated-alert-dismissal-reason/)).

SARIF encodes the same split at the standard level. A suppression object's `kind` and `status` are enumerated, while `justification` is "a user-supplied string that explains why the result was suppressed" ([OASIS SARIF 2.1.0 §3.35](https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html)). A reviewer that emits SARIF has a standard place to record the decision, though the spec leaves the reason itself as free text.

With the field in place, group dismissals by rule id and count the distribution. A rule whose findings come back "Incorrect" two thirds of the time is a retirement candidate. A rule dismissed as "Won't fix" is correct and unwanted, which is a scope question rather than a precision one. That per-rule split is what [the review-feedback-to-rule loop](review-feedback-to-rule-loop.md) needs to decide what to narrow, and the signal [learned review rules](learned-review-rules.md) names as missing.

## Why it works

The record is countable because the vocabulary is closed at the moment of decision. An enum groups and sums; prose needs a parsing pass before it counts at all, which is why both SARIF and the code scanning API keep the enum and the free text in separate fields. Cursor built a product on the accept-and-dismiss signal: "More than 110,000 repos have enabled learning, generating more than 44,000 learned rules" ([Cursor](https://cursor.com/blog/bugbot-learning)). What the post does not report is an effect. Bugbot's resolution rate went from 52% at its July 2025 launch to "nearing 80%" in April 2026, and Cursor credits that arc to something else entirely: "Up until now, improvements have been propelled exclusively by offline experiments." Learned rules are the new mechanism in that post, with no resolution-rate figure attached. Take the 44,000 as evidence that teams will supply the signal, not that it works.

## When this backfires

- The reason is write-only. Copilot's dropdown is the current example. It sends feedback to GitHub's product team and returns nothing you can query.
- Bulk dismissal. GitHub supports dismissing many alerts "for the same reason" from a filtered list ([GitHub Docs](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/resolve-alerts)). One selection describes fifty findings, and the distribution tracks whoever wrote the filter.
- The recorded reason is not the real one. Across 1,425 Java projects using FindBugs or SpotBugs, "false positives account for a minor proportion of suppressions. A significant number of suppressions introduce technical debt" ([arXiv:2311.07482v1](https://arxiv.org/abs/2311.07482v1)). A menu built around "Incorrect" has no box for deliberately accepted debt.
- Nobody reads the pile. Across 7,357 suppressions in 46 Python projects, the count "tends to continuously increase over time" and "50.8% of all suppressions do not affect any warning and hence are practically useless" ([Hu, Wang, Rubin et al., FSE 2025](https://doi.org/10.1145/3715729)). Collection with no scheduled read produces the same inert record.
- Too few comments. Splitting a small monthly comment count across three or four buckets leaves each one too sparse to read, the same volume floor that makes [comment acceptance measurement](agentic-review-comment-acceptance.md) noisy per repository and per comment type.
- The field is audited. SARIF's suppression object exists for compliance, showing "an auditor that they have looked at all results that corporate policy requires" ([OASIS SARIF §3.35](https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html)). A field serving an audit and a field serving your own precision measurement are answering different questions, and the audit wins.

The honesty check is one query. If a rule's dismissals are never "Incorrect", that is not a precise reviewer. It is a field nobody takes seriously, and the fix is to hand-adjudicate thirty comments before trusting the self-reported ones.

## Key Takeaways

- Do not enable a reason field you cannot query. Copilot's resolution dropdown fails that test today; code scanning's `dismissed_reason` passes it.
- Keep the enum and the free text in separate fields, the way `dismissed_reason` and `dismissed_comment` are split. A merged field counts as neither.
- Group by rule id, not by repository. The aggregate dismissal rate says nothing about which rule to narrow.
- Set the read cadence when you turn collection on. Suppression records tend to grow continuously, and in the FSE sample half of them affected no warning at all.
- Validate the taxonomy against a hand-adjudicated sample before acting on its distribution. One that never records disagreement is measuring compliance with itself.

## Related

- [Learned Review Rules](learned-review-rules.md) — the consumer: rule extraction that conflates signals without a structured dismiss reason
- [Review-Feedback-to-Rule Loop](review-feedback-to-rule-loop.md) — where a per-rule dismissal distribution feeds the retire-or-narrow decision
- [Agentic Review Comment Acceptance](agentic-review-comment-acceptance.md) — the accept/reject baseline this reason field decomposes
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — the design goal the measurement serves
- [Reviewer Theme Distribution Audit](reviewer-theme-distribution-audit.md) — the adjacent audit, by comment theme rather than by resolution

## Sources

- [OASIS SARIF v2.1.0 Errata 01 §3.35](https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html) — suppression object: `kind`, `status`, `justification`.
- [Hu, Wang, Rubin et al. (FSE 2025)](https://doi.org/10.1145/3715729) — "An Empirical Study of Suppressed Static Analysis Warnings".
- [arXiv:2311.07482v1](https://arxiv.org/abs/2311.07482v1) — Liargkovas, Panourgia, Spinellis (2023): "Quieting the Static".
