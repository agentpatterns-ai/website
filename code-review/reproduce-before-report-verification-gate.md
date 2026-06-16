---
title: "Reproduce-Before-Report Verification Gate"
description: "Place an independent verifier between reviewer findings and the user so only candidates that can be reproduced against actual code behavior are reported."
tags:
  - code-review
  - testing-verification
  - tool-agnostic
aliases:
  - reproduce-before-report gate
  - verifier-gated code review
  - finding verification gate
last_reviewed: 2026-06-13
maturity: established
---

# Reproduce-Before-Report Verification Gate

> A reproduce-before-report verification gate drops any reviewer finding the verifier cannot reproduce against actual code behavior.

The reproduce-before-report gate is a structural step in a multi-agent code review pipeline: a reviewer raises a candidate finding, then a fresh-context verifier attempts to construct a concrete reproduction against the diff before the finding ships. Non-reproducing findings are silently dropped. The gate sits at the *reporter* boundary — the reviewer flags freely; the verifier converts soft suspicion into hard evidence or discards it.

## What "Reproduce" Means at the Gate

The verifier is not a second opinion. It takes the diff plus the reviewer's claim ("function `X` will crash on empty input on line 42") and tries to construct evidence: an input that triggers the failure, a code path that demonstrates the contradiction, or a citation to the specific behavior in the source. Anthropic's managed Code Review exposes this artifact — each finding "includes a collapsible extended reasoning section you can expand to understand why Claude flagged the issue and how it verified the problem" ([Code Review docs](https://code.claude.com/docs/en/code-review)). `REVIEW.md` makes the reproduction bar a per-repo dial; the canonical example is "behavior claims need a `file:line` citation in the source, not an inference from naming" ([Code Review docs](https://code.claude.com/docs/en/code-review)).

## Why the Verifier Must Be Independent

Independence is the load-bearing property. A verifier that shares context with the reviewer inherits its reasoning errors and confirms its own false positives. Two dimensions:

- **Context freshness**: the verifier starts with the diff and the claim, not the reviewer's chain of thought.
- **Model diversity**: LLM judges exhibit documented same-family bias — systematically scoring outputs from related model families higher ([Zheng et al. 2023](https://arxiv.org/abs/2306.05685)); same-family verifiers reproduce same-family confabulations.

Claude Code's `/code-review ultra` (aliased from `/ultrareview`) names this in its comparison against single-pass `/review`: ultrareview is "multi-agent fleet with independent verification" ([ultrareview docs](https://code.claude.com/docs/en/ultrareview)).

## Why It Works

Construction is harder to fake than judgment. A reviewer can hallucinate a defect with no external grounding; a verifier that must produce a reproduction cannot — it either runs or it does not. Multi-agent verification with conditionally independent agents in [CodeX-Verify](https://arxiv.org/abs/2511.16708) improved accuracy from 32.8% to 72.4%, with measured reviewer-pair correlations of 0.05 to 0.25 confirming non-overlapping error populations. The pattern generalises: Agent-as-a-Judge frames tool-augmented verification against real-world observations as the structural fix for LLM-as-a-Judge's "shallow single-pass reasoning, and the inability to verify assessments against real-world observations" ([Agent-as-a-Judge survey, arXiv:2601.05111](https://arxiv.org/abs/2601.05111)).

## Silent Drop Is the Default

Non-reproducing findings are dropped, not appended with a low-confidence flag. The `/code-review ultra` docs state the purpose: "every reported finding is independently reproduced and verified, so the results focus on real bugs rather than style suggestions" ([ultrareview docs](https://code.claude.com/docs/en/ultrareview)). Surfacing unverified findings re-creates the noise problem the gate exists to solve.

## Implementing the Gate

| Part | Job | Anthropic implementation |
|------|-----|--------------------------|
| Reviewer | High-recall candidate generation | Per-class agents (correctness, security, regressions, edge cases) in parallel |
| Verifier | Reproduction against actual code | Fresh-context agent given diff + claim; reproduced or dropped |
| Drop policy | Discard non-reproducing findings | Silent — not surfaced to user |
| Reasoning artifact | Expose verification evidence | "How it verified the problem" collapsible ([Code Review docs](https://code.claude.com/docs/en/code-review)) |

A pipeline that fans out reviewers but reports every candidate is not running this gate — it is fan-out, which amplifies false positives.

## When This Backfires

- **Small or trivial diffs.** `/code-review ultra` runs "typically cost $5 to $20" ([ultrareview docs](https://code.claude.com/docs/en/ultrareview)); managed Code Review averages "$15-25 in cost, scaling with PR size, codebase complexity, and how many issues require verification" ([Code Review docs](https://code.claude.com/docs/en/code-review)). On a typo fix, gate cost dominates false-positive cost — use a single-pass [diff-based review](diff-based-review.md).
- **Same-family verifier with no context reset.** Without independence, the verifier reproduces reviewer confabulations — the same [overcorrection bias](../anti-patterns/llm-review-overcorrection.md) the gate exists to filter. Same model + same session = verification gate in name only.
- **Reproduction-incapable defect classes.** Race conditions, distributed-system failures, and intermittent flakes cannot be reproduced on demand against a static diff. Silent-drop becomes silent-drop of the highest-stakes findings — route those classes to a separate "suspected-but-not-reproduced" channel or accept the recall loss.
- **Air-gapped or ZDR environments.** Cloud fleet implementations are "not available when using Claude Code with Amazon Bedrock, Google Cloud Vertex AI, or Microsoft Foundry, and it is not available to organizations that have enabled Zero Data Retention" ([ultrareview docs](https://code.claude.com/docs/en/ultrareview)).
- **High-iteration PRs with push triggers.** 30 pushes × $15-25 compounds linearly. Use `@claude review once` to suppress push-triggered re-verification ([Code Review docs](https://code.claude.com/docs/en/code-review)).

## Example

A `REVIEW.md` snippet that raises the verification bar on a backend repo:

```markdown
## Verification bar

Behavior claims need a file:line citation in the source code,
not an inference from naming. If a finding says "this function
will crash on null input," cite the line where the unchecked
dereference happens; if you cannot cite it, drop the finding.

For data-flow claims (taint, leakage, scope), cite both the
source line and the sink line. Findings that name the sink
but cannot trace the source are not reproductions — drop them.

For race-condition suspicions, cite the two interleavings.
If you cannot construct both, route the finding to the
"unverified-suspicion" channel in the summary, not as an
inline Important finding.
```

This configuration makes the verifier's reproduction artifact explicit per defect class: code-path bugs need source citations, taint bugs need source-plus-sink, races need an interleaving. Findings that fail their class-specific reproduction bar are dropped from the inline review rather than posted as low-confidence noise.

## Key Takeaways

- The gate sits between reviewer and user — high-recall reviewing stays freely speculative; the user only sees what survives independent reproduction
- Independence (fresh context, ideally different model family) is the load-bearing property; same-family verifiers inherit reviewer biases
- Silent drop of non-reproducing findings is the default — surfacing them with a confidence flag re-creates the noise problem the gate exists to solve
- Multi-agent verification with conditionally independent agents lifted accuracy from 32.8% to 72.4% in CodeX-Verify — the gain is empirical, not speculative
- Cost runs $5-25 per review with verification as a named scaling factor — appropriate for substantial pre-merge changes, not for typo PRs
- The pattern is unavailable for ZDR organizations and non-Anthropic cloud hosting today; a self-hosted fleet is the only option there

## Related

- [Cloud Parallel Review Pattern](cloud-parallel-review-pattern.md) — the full fan-out + verify + aggregate architecture in which this gate is the verify step
- [LLM Code Review Overcorrection](../anti-patterns/llm-review-overcorrection.md) — the false-positive bias that motivates the gate
- [Signal Over Volume in AI Review](signal-over-volume-in-ai-review.md) — the precision principle the gate enforces at the reporter boundary
- [Adversarial Multi-Model Development Pipeline (VSDD)](../multi-agent/adversarial-multi-model-pipeline.md) — the broader fresh-context independent-adversary pattern this gate instantiates for code review
- [Evaluator-Optimizer Pattern](../agent-design/evaluator-optimizer.md) — the two-role generator/evaluator loop the gate inherits and constrains
- [Tiered Code Review](tiered-code-review.md) — risk-class routing that decides which depths apply the gate
- [Committee Review Pattern](committee-review-pattern.md) — a voting-style contrast that does not gate at the reporter boundary
- [Agentic Code Review Architecture](agentic-code-review-architecture.md) — the tool-calling reviewer shape the verifier composes with
