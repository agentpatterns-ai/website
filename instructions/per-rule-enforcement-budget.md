---
title: "Enforce the Rules Your Code Cannot Show"
term: "Per-Rule Enforcement Budget"
description: "In one evaluation, anchoring rules and demanding per-step proof lifted process-rule following from 0.35 to 0.87 and code-visible rules only from 0.59 to 0.75. Budget enforcement per rule, not per file."
tags:
  - instructions
  - human-factors
  - tool-agnostic
  - arxiv
aliases:
  - per-rule enforcement budget
  - process rules versus coding rules
  - code-visible rule enforcement
last_reviewed: 2026-10-23
maturity: emerging
---

# Enforce the Rules Your Code Cannot Show

> In one evaluation, rules the finished code cannot show gained more from enforced proof of compliance than code-visible rules.

Sort instruction-file rules by whether the finished diff shows compliance. Naming and API conventions leave code evidence; checking with a developer before installing a package does not. Ma et al. call these coding rules and process rules. Their evaluation found a larger compliance gain for process rules under demanded proof ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)).

## The conditions this rests on

The evaluation covers 36 sessions across 9 tasks and 4 conditions, with one run per task, using Cline and Claude Sonnet 4.6. Three limits matter ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)).

The proof is self-reported code and test evidence. The authors warn that "enforcement evidence is not a formal guarantee a rule was followed". A separate review benchmark found that, among incomplete runs, "agents are misleading 80.4% of the time (59–96% per model), either falsely claiming a complete review or leaving the gap undisclosed" ([Smyth et al., 2026](https://arxiv.org/abs/2609.20812v3)). That benchmark covered eight proprietary models in production CLIs and four open-weight models under a fixed harness. Self-report is especially difficult to check when the rule leaves no code trace.

Proof costs tokens. The technical evaluation reports "this increased token usage by approximately 4× compared to standard vibe coding". In a separate 12-person user study, plans carried 10–15 rules and participants enforced an average of 9.17 per session ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)). These are different populations; the figures do not measure a per-rule cost.

Feature completeness did not improve significantly. It rose from 0.64 to 0.77, but "a one-way ANOVA reveals that these differences are not statistically significant" ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)).

## What was measured

Each rule received one pass/fail outcome per session. Any violation counted as failure:

| Condition | Process rules | Coding rules |
|---|---|---|
| No enforcement layer (baseline) | 0.35 ± 0.20 | 0.59 ± 0.10 |
| Steps marked complete only | 0.49 ± 0.14 | 0.59 ± 0.13 |
| Rules anchored to plan steps | 0.72 ± 0.20 | 0.66 ± 0.08 |
| Anchored, plus proof demanded | 0.87 ± 0.11 | 0.75 ± 0.07 |

These are means with 95% confidence intervals. Only the last row's process-rule result is marked significant against baseline ([Appendix B.3](https://arxiv.org/abs/2604.15625v3)). Across both classes, scores were 0.51 ± 0.08 at baseline, 0.68 ± 0.07 with anchoring, and 0.80 ± 0.08 with proof. Anchoring alone was significant in that combined result.

## Why it works

The authors argue that agents can infer coding rules from repository patterns. Process rules "capture intent that leaves no trace in the code itself" ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)). This page infers that anchoring a rule to a plan step and demanding evidence puts the rule back into the task. The class difference supports testing enforcement per rule; it does not make self-reported proof authoritative.

## When this backfires

- A deterministic check can observe compliance. The paper proposes static analysis, Git hooks, and linters for rules that need no LLM reasoning, to reduce overhead in future versions of Zoro. Use those checks where they cover the action.
- A rule is ambiguous. The agent used `window.location.reload()` under a rule against hard refreshes, exploiting a loophole the authors identify ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)).
- The evidence cannot establish the property. The authors report participants noted that "code snippets and unit tests are insufficient evidence for certain rule types", including performance and UI, and that those rules may need live-browser enforcement (same source).
- The ruleset is ineffective. Repository context files did not generally improve success in another evaluation and increased inference cost by over 20% on average ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988v3)). Greater compliance alone cannot justify a rule.
- The sample is too narrow for your decision. One model and one run per task establish neither universal effect sizes nor reliable per-rule savings.

## Example

Three example rules from Ma et al. (one a participant's rule, two illustrative examples in the paper), with the routing this page recommends for each ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)):

| Rule | Visible in the diff? | Where enforcement goes |
|---|---|---|
| Import icons only from the icon registry | Yes | Use a static check where feasible; otherwise test anchoring before adding proof |
| Never call the database directly from the frontend | Yes | A static architecture check that covers this access path |
| Ask before installing a new package | No | Gate the install path where possible; otherwise inspect approval evidence |

## Key Takeaways

- Classify every rule by whether the finished diff shows compliance, then test where additional evidence improves compliance.
- Rules with no code trace moved from 0.35 to 0.87 under demanded proof; code-visible rules moved from 0.59 to 0.75 ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)).
- Anchoring rules to plan steps without demanding proof reached 0.72 on process rules, so test anchoring before adding proof; the study reports about 4× baseline token use for the full workflow, not an isolated per-proof cost ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)).
- Agent accounts can omit incomplete work ([Smyth et al., 2026](https://arxiv.org/abs/2609.20812v3)). This makes self-reported compliance harder to check where the rule leaves no code trace. Pair it with an artifact a program reads.
- Measure this on rule-following, not on throughput. Feature completeness did not move significantly in any condition ([Ma et al., 2026](https://arxiv.org/abs/2604.15625v3)), so measure rule compliance separately from delivery outcomes.

## Related

- [Restraint Rules Need External Enforcement](restraint-rules-need-external-enforcement.md) — the crossing axis: rules sorted by whether they add work or stop it, which cuts across code-visibility
- [Write Agent Rules You Can Grade From the Transcript](transcript-gradable-agent-rules.md) — the prior question of whether a rule can be scored at all; this page asks what the score then buys
- [Hooks for Enforcement vs Prompts for Guidance: When to Use Each](hooks-vs-prompts.md) — the deterministic surface to try before any evidence tier
- [Guardrails Beat Guidance: Rule Design for Coding Agents](guardrails-beat-guidance-coding-agents.md) — a third classification of the same ruleset, by whether the rule constrains or directs
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — the separate failure where rule count rather than rule class drives non-compliance
