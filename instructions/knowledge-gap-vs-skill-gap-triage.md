---
title: "Knowledge Gap or Skill Gap: Triage Before Writing Context"
term: "Knowledge-Gap Triage"
description: "Classify agent near-misses as knowledge gaps or skill gaps before enlarging a context file — an ablation across two frontier agents found only the knowledge half is addressable by context."
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - knowledge gap versus skill gap
  - context file failure triage
  - implementation-skill failure triage
last_reviewed: 2026-08-02
maturity: emerging
---

# Knowledge Gap or Skill Gap: Triage Before Writing Context

> Classify agent failures as knowledge gaps or skill gaps first — a context file only closes the knowledge half, and only that half.

## When this triage applies

Run this triage when the agent is near-missing (patches that fail one to four gold tests, not outright failures) and you are weighing a bigger context file against spending the time elsewhere. It is a routing decision, not a case for deleting AGENTS.md — better-powered work finds guidance does move correctness. Across four trials on 500 SWE-bench Verified instances, a static knowledge base resolved 28.3% against a 25.5% unguided baseline, p = 0.004 ([Shepard and Albrecht, 2026](https://arxiv.org/abs/2606.20512v2)). Keep the file; the question is whether growing it pays.

## The two gap types

Khatri ablated three context-injection strategies: none, the full AGENTS.md in the system prompt every turn, and a topic-organized wiki retrievable on demand. The design spanned Claude Code and Codex, 17 tasks from three Python repositories, and 288 gold-test-evaluated runs ([Do Context Files Help Coding Agents?, 2026](https://arxiv.org/abs/2607.27250v1)). Pass rates barely moved: 53.3%, 55.6%, and 55.6% for Claude; 58.8%, 56.9%, and 52.9% for Codex. Omnibus permutation tests returned p = 1.00 and p = 0.66.

The triage behind that null is the reusable part. Each of the four near-misses the author triaged was an implementation-skill gap, not a missing fact about the repository:

| Observed failure | Gap type |
|---|---|
| A valid optimization attempted, a correctness bug introduced | skill |
| Reactive retry implemented where proactive token refresh was specified | skill |
| An argument-rejection check miswired | skill |
| A type left un-narrowed through `isinstance` plus `assert` | skill |

Read your own transcripts the same way. An agent that greps the wrong directory, runs the wrong test command, or misses an unwritten convention has a knowledge gap. One line in the context file closes it. An agent that reaches the right code and then designs the wrong thing has a skill gap, which routes to task decomposition, better tooling, and [example-driven instructions](example-driven-vs-rule-driven-instructions.md) instead.

The same study explains part of the disagreement between published results. Across the 15 tasks both agents attempted, per-task pass rates correlate at only Spearman ρ = 0.75, with roughly 40% sitting in agent-specific difficulty bands ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)). A benchmark sees an effect only where tasks are borderline for the agent under test.

## Why it works

The mechanism is a binding constraint. A context file supplies repository knowledge: where subsystems live, how to run the tests, which conventions apply. More of that input cannot relieve a constraint on a different one. The manipulation probe shows it empirically — across 36 probe cells, injecting the real AGENTS.md never converted a failing run into a passing one on either agent ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)).

The one effect that survived was process, not capability. On opshin, whose AGENTS.md carries explicit runtime warnings, Claude's blind full-suite test runs fell dose-dependently across the three strategies: 3.67, then 2.44, then 1.67 per cell. Across all three repositories, not opshin alone, selective injection cut Claude's cache-creation tokens on all 11 tasks compared (Holm-corrected p = 0.012) ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)). Knowledge changed how the agent worked, not what it could do — so measure context files on cost and latency, not pass rate.

## When this backfires

- Reading the null as "context files do not help". Descriptive equivalence bounds put every pairwise difference under 10 percentage points for Claude and 15 for Codex, and the author puts the minimum detectable effect well above 30 points at this sample size ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)). The 2.8-to-7.5-point gains measured on SWE-bench Verified sit inside that blind spot.
- Generalizing past generic files. The study tested naturalistic, style-guide-shaped context and lists the inert-manipulation concern as an open limitation ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)). Guidance tuned against the agent's observed failures beat both static guidance and no guidance at a 33.0% resolve rate, p < 0.001 ([Shepard and Albrecht, 2026](https://arxiv.org/abs/2606.20512v2)) — see [probe-and-refine tuning](probe-and-refine-guidance-tuning.md).
- Undocumented codebases. All three test repositories are public, documented Python projects, and the author names repository diversity as a limitation ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)). Where constraints are not inferable from the code, the ablation says nothing.
- Expecting the efficiency win on any agent. Every efficiency signal was Claude-only; Codex was flat on tool calls, output tokens, and duration. The two agents also received context through different channels, system prompt against user-turn prepend, which the author flags as a confound ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)).
- Treating one snapshot as durable. Results are specific to claude-sonnet-4-6 and gpt-5.5 ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)). Re-run the triage after a model upgrade rather than carrying the conclusion forward.

## Example

Applied to the opshin arm of the study, the triage runs in three steps.

Symptom: Claude ran the full test suite blind, repeatedly, before it had narrowed the problem.

Classification: knowledge gap. The agent did not know the suite was slow, and that fact is not inferable from the source tree.

Action: deliver the runtime warning the repository's AGENTS.md already carried, rather than author anything new.

**Before** — no context injected: 3.67 blind full-suite runs per cell, 2689 seconds mean duration.

**After** — selective retrieval of the same content: 1.67 blind runs per cell, 2032 seconds mean duration.

Claude's overall pass rate moved from 53.3% without context to 55.6% under selective injection, a difference the study's permutation test could not separate from noise ([Khatri, 2026](https://arxiv.org/abs/2607.27250v1)). The triage still worked: it closed the gap it could close and left the skill gaps for a different intervention.

## Key Takeaways

- Triage near-misses before enlarging a context file: knowledge gaps are addressable by context, skill gaps are not
- All four near-misses triaged in a 288-run two-agent ablation traced to implementation skill, and injecting the real AGENTS.md never flipped a failure to a pass across 36 probe cells
- The correctness null is bounded, not zero — the design cannot see effects below roughly 10 to 15 points, and a better-powered study measured gains inside that band
- Context files earned their keep on process: fewer blind test runs and lower cache-creation tokens, with pass rate unchanged
- Cross-agent task difficulty correlates at only ρ = 0.75, so a benchmark that is borderline for one agent is saturated for another, which explains much of the disagreement between published results

## Related

- [Evaluating AGENTS.md: When Context Files Hurt More Than Help](evaluating-agents-md-context-files.md) — the broader evidence review on whether context files help; this page is the triage that decides where to spend effort next
- [Probe-and-Refine Tuning of Repository Guidance for Coding Agents](probe-and-refine-guidance-tuning.md) — the method that closes the task-specific-guidance gap this study leaves open
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — one of the three destinations the author names for effort diverted from generic context
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why an enlarged context file degrades rather than improves behavior past a threshold
- [Method Map: Failure-Mode to Smallest-Artifact Triage](method-map-failure-mode-triage.md) — the same triage discipline generalized across artifact types
- [Discoverable vs Non-Discoverable Context](../context-engineering/discoverable-vs-nondiscoverable-context.md) — the test for which facts belong in a context file at all
