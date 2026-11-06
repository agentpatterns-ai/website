---
title: "Treating Rule Retention After Compaction as Compliance"
term: "Retained-Rule Violation"
description: "A rule that survives compaction can still be broken: in one benchmark, compacted runs that kept the rule violated it 2.6 times as often as full-history runs."
aliases:
  - the rule survives compaction and the agent breaks it anyway
  - post-compaction rule violation
  - rule retention as a compliance proxy
tags:
  - anti-pattern
  - context-engineering
  - instructions
  - tool-agnostic
  - arxiv
last_reviewed: 2026-11-05
maturity: emerging
---

# Treating Rule Retention After Compaction as Compliance

> A rule still present in the compacted summary can still be broken; grade the agent's tool calls after compaction, not the summary text.

This applies to rules the agent received in conversation or in a tool result, and it is worst for rules the user gave. In ARCBench, a benchmark built on the pi agent harness, compacted runs that kept the rule broke it more often than full-history runs ([arXiv:2611.03223v1 §4.2](https://arxiv.org/abs/2611.03223v1)). The study used 17 English cases ([arXiv:2611.03223v1 §Limitations](https://arxiv.org/abs/2611.03223v1)), four models that each compacted and acted, and canned tool results ([arXiv:2611.03223v1 Appendix C](https://arxiv.org/abs/2611.03223v1)).

## What the benchmark found

With the Hermes compactor, "violation@3 rises from 9.6% with the full history to 37.8% after compaction". Violation@3 counts a case once if any of its three runs breaks the rule. Compaction rarely deleted the rule: "Most compacted runs still retain the rule (70.1%); 26.9% retain it partially, and only 3.0% lose it" ([arXiv:2611.03223v1 §4.2](https://arxiv.org/abs/2611.03223v1)).

Keeping the rule did not keep the agent compliant. With the full history, "8.1% of runs violate". Of the compacted runs that kept the rule, 21.1% still violated it, 2.6 times the full-history rate ([arXiv:2611.03223v1 §4.2](https://arxiv.org/abs/2611.03223v1)). The authors conclude: "Rule retention is thus not a sufficient proxy for compliance" ([arXiv:2611.03223v1 §5](https://arxiv.org/abs/2611.03223v1)).

The delivery channel sets the size of the gap. A retained rule was violated in 36.6% of runs when the user stated it, against 11.7% when the agent fetched it with a policy tool ([arXiv:2611.03223v1 §4.3](https://arxiv.org/abs/2611.03223v1)).

## Why it works

The failure happens in the action, so a check that reads the summary cannot see it. A judge panel read the agent's reasoning on each violating call. The commonest reason, with or without compaction, was that "the agent treats the user's later request as permission to break the rule". Compaction also made the agent more likely to say the rule applied and go ahead anyway. That reason covered 21.6% of retained-rule violations that appeared only after compaction, against 3.4% with the full history ([arXiv:2611.03223v1 §4.2, Table 4](https://arxiv.org/abs/2611.03223v1)). The authors explain the channel effect: "A personal rule comes from the user, so the user's later request can be read as lifting it, whereas an organizational rule comes from the organization, which the user cannot override" ([arXiv:2611.03223v1 §4.3](https://arxiv.org/abs/2611.03223v1)).

## What to do instead

- Grade compliance the way ARCBench does: "ARCBench grades what the agent does, not what it says: only its tool calls count" ([arXiv:2611.03223v1 Appendix B](https://arxiv.org/abs/2611.03223v1)). Force a compaction, send the request the rule forbids, and run each case more than once.
- Keep a retention check for the failures it does catch. A tight budget or a selective compactor deletes the rule outright ([arXiv:2611.03223v1 §4.3](https://arxiv.org/abs/2611.03223v1)).
- Put a rule that must hold where the harness reloads it. Claude Code re-reads project-root CLAUDE.md from disk after `/compact` ([Claude Code memory docs](https://code.claude.com/docs/en/memory)). ARCBench's four delivery channels are all inside the history, so it did not test that route ([arXiv:2611.03223v1 Appendix E.4](https://arxiv.org/abs/2611.03223v1)).
- Block the forbidden call outside the model. A `PreToolUse` hook runs before a tool call executes and can block it ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)).

## When this backfires

- A study that grades only whether the constraint survived. Governance Decay, with constraints delivered in context, found a 0% violation rate when an LLM judge ruled the constraint survived (n=90), against 38% when it was dropped (n=315) ([arXiv:2606.22528v2](https://arxiv.org/abs/2606.22528v2)). ARCBench's organizational channels still saw retained runs violate in 16.9% (document-embedded) and 11.7% (policy-tool fetching) of runs ([arXiv:2611.03223v1 Appendix M](https://arxiv.org/abs/2611.03223v1)).
- A compactor told to preserve rules, with no attack. Pi with a rule-preservation prompt was the only strategy below the full-context baseline, at 9.0% against 11.9% ([arXiv:2611.03223v1 §4.3](https://arxiv.org/abs/2611.03223v1)).
- A rule a hook already enforces. Test the hook, because the agent's choice no longer decides the outcome.
- A rule with no tool-call footprint, such as tone. ARCBench dropped cases whose violation cannot be seen in a tool call ([arXiv:2611.03223v1 §3.1](https://arxiv.org/abs/2611.03223v1)).

## Key Takeaways

- A summary that still states the rule is not evidence the agent will follow it.
- User-given rules carry the largest gap, because a later user request reads as permission.
- Score a case as failed if any of several runs breaks the rule; an average over runs hides the one that does ([arXiv:2611.03223v1 §3.2](https://arxiv.org/abs/2611.03223v1)).
- Rules that must hold belong in a reloaded file or a tool-call gate.

## Related

- [Reading Benchmark Compaction Tolerance as Policy Evidence](compaction-tolerant-benchmarks-as-policy-evidence.md) — measures whether constraints survive the summary; this page covers what happens when they do.
- [Scoring Constraint Loss and Tool Reach as Separate Risks](constraint-loss-and-tool-reach-scored-separately.md) — a dropped constraint costs most when the unsafe action stays reachable.
- [Assuming Loaded Skills Stay Enforced in Long Contexts](assuming-loaded-skills-stay-enforced.md) — the same presence-versus-enforcement gap for skill requirements.
- [Treating Compaction Prompt Rules as a Provenance Defense](compaction-prompt-rules-as-provenance-defense.md) — a compactor prompt rule that failed to stop forged approvals.
- [Post-Compaction Re-read Protocol for Agent Continuity](../../instructions/post-compaction-reread-protocol.md) — restores instruction files after compaction.
