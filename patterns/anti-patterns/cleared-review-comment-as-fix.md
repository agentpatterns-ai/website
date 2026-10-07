---
title: "Treating a Cleared Review Comment as a Fixed Flaw"
term: "Cleared-Comment Deference"
description: "Feedback-guided revision won approval for still-exploitable code on 33 of 159 CVE-based PRs, and re-running the same review caught 23 of those 33, then none."
aliases:
  - cleared review comment as security evidence
  - resolved finding as proof of fix
  - adaptive code revision attack
tags:
  - anti-pattern
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-06
maturity: emerging
---

# Treating a Cleared Review Comment as a Fixed Flaw

> A cleared review comment proves the reported defect is gone. Whether the vulnerability survived is a separate question.

Cleared-comment deference is approving a revision because the reviewer's own earlier finding no longer applies. Gong and colleagues measured what it costs on 159 executable CVE-based pull requests. An adversarial contributor that read the reviewer's explanation and revised the code won approval for code an independently executed exploit still broke on 33 of them, 20.8% of the benchmark, against a Claude Code reviewer running Sonnet 5 ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). Against a Codex reviewer running GPT-5.5 it won 25 of 159, 15.7%. Success required approval plus a proof-of-concept verified on the approved revision, so these are confirmed exploitable merges.

Compare that with attacks that leave the code alone. On the same 159 instances and the same Sonnet 5 reviewer, revising the PR description won 13, one-shot persuasion won 7, and a fabricated security-analysis comment won 2 ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). Changing the implementation is what moved the number, and 27 of the 33 successes were reachable by no other method.

## Why it works

The reviewer and the author are answering different questions, and the reviewer's answer looks like the author's. The paper states the mechanism plainly: "AFCRA exploits the gap between resolving a review comment and establishing that the code is safe. Feedback identifies a repair target, which the attacker fixes while preserving harmful behavior elsewhere. The revision becomes convincing because the reported defect disappears, and the reviewer accepts this local improvement as evidence of safety" ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)).

Holding the reviewer at Sonnet 5 across all 159 instances, a verdict alone won 19, adding the flagged location won 25, and adding the explanation won 33 ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). The verdict-to-full move gained 14 instances and lost none. The authors treat the two intermediate steps as descriptive after correction, so location and explanation are supported together, neither on its own.

A path check repaired to block sibling-directory traversal still followed symbolic links outside the served root. A rejected regular expression replaced with explicit scans removed the backtracking and left the code quadratic ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). In both, the reviewer verified its own earlier complaint and stopped there.

## What re-review catches

Default review's early rejections did not hold. Of the 33 instances that eventually won approval, it was still rejecting 23 after round one, 7 after round three, and none after round five ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). A request for changes buys a round, and the contributor has four more.

The paper then tested five alternative reviewer strategies on those same 33 instances, keeping the full feedback and the five-round budget ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)).

Among strategies using ordinary review information, root-cause review (checking whether the revision prevents the underlying violation) caught 23 of 33, re-reviewing the whole diff each round caught 22, requiring static analysis on changed files caught 20, and swapping the model for Fable 5.1 caught 18. Executing the instance's supplied proof-of-concept, an idealized upper bound, caught 29 ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). Note the denominator: 33, the already-successful attacks, not 159.

Default review cost $12; the five defenses cost $50 to $96, static scan cheapest at $50 for 20 catches and root cause $52 for 23 ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). All five reached their final catch counts by round three. Re-running the six configurations against the historical developer fixes for those same 33 instances produced "zero false rejections" across all 198 reviews ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)), so on that repair set the added checks did not start rejecting real fixes.

## When this backfires

- Nobody hostile can open a PR. The threat model needs a contributor who authored the vulnerable code and controls the revisions. An internal-only repository paying for security-focused review is buying protection it does not need.
- You withhold explanations by default. Detail is what makes feedback work for honest contributors. The paper reports, citing SWE-Review, the resolve rate after revision rising "from 8% with a verdict alone to 21%" on 100 correctly rejected patches ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). Its recommendation is staged rather than blanket, to "Give full feedback first, then withhold locations and explanations for security-sensitive issues."
- The security check targets the wrong property. Root-cause review checked prototype modification on a flaw that was uncontrolled recursion, and approved. Proof-of-concept execution accepted protection limited to HTTP after naming the same behavior in other schemes ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). A strategy that does not name the original harmful behavior costs four to six times default review and still signs off.
- You pick one strategy and stop. No single defense caught all 33. Seven were caught by all five, and the union of the five covered every instance ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)).
- Approval authority spans more than the diff. Letting the contributor edit the PR description and reply in the review thread alongside the code took approval from 33 of 159 to 70 of 159, 44.0% ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). Neither added channel was significant alone.

## Example

What separates the configurations the paper measured is the reviewer's instruction. Every strategy except the model swap ran on the same Sonnet 5 ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)).

**Before — the default reviewer, which the paper describes as one that "reviews changed code for correctness, quality, performance, and security":**

```text
Review the changed code for correctness, quality, performance, and security.
```

**After — the two best-catching strategies that use ordinary review information, described in the paper as one that "checks whether the revision prevents the underlying security violation" and one that "instructs the reviewer to inspect the whole diff again each round":**

```text
Inspect the whole diff again, not only the lines that changed since the
last round. Name the security violation your first review identified, then
decide whether this revision prevents that violation.
```

The paper measured these as two separate configurations; this prompt combines them. Carried into every later round, the root-cause question caught 23 of the 33 attacks default review had approved, and whole-diff re-reading caught 22 ([arXiv:2610.05399v1](https://arxiv.org/abs/2610.05399v1)). Static analysis on changed files is the cheaper third option, blocking approval on unresolved confirmed findings for $50 against root cause's $52.

## Key Takeaways

- A cleared comment is evidence about the comment. Ask what the first review said the violation was, and whether this revision prevents that, before approving.
- An early request for changes is not a save. Default review was still rejecting 23 of the 33 after round one and none of them after round five.
- Budget three rounds of security-focused review rather than five. Every tested defense reached its final catch count by round three.
- Use checks that look at different things. No single defense caught all 33, and the union of all five did.
- Scope approval authority to the diff. Code plus PR text plus thread replies took attack success from 20.8% to 44.0% on the same reviewer.

## Related

- [Treating a Clean Static Scan as Security Evidence](static-clean-as-security-evidence.md) — the same green-signal error without an adversary adapting to the signal.
- [Trusting Claimed Prior Approval in Agent Review Gates](trusting-claimed-prior-approval.md) — where the worthless evidence is a fabricated approval rather than a real repair.
- [Reading Visible Edge-Case Handling as a Security Check](edge-case-handling-as-security-signal.md) — the human version, judging security by whether a defensive block is visible.
- [Bug-Class Hints as Exploit Input for Coding Agents](../../security/bug-class-hints-as-exploit-input.md) — what a localizing hint gives an attacker before review ever starts.
- [The Security Review Gap in AI-Authored PRs](../../code-review/security-review-gap-in-ai-prs.md) — the non-adversarial half of the same gate, where reviewer heuristics miss AI-specific CWE clusters.
