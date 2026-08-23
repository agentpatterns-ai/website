---
title: "Minimality Prompts as a Patch-Size Control"
term: "Minimality Prompt"
description: "Across 28 SWE-bench Verified repair systems, explicitly instructing minimality was associated with patches as large as instructing nothing; patch size tracked how the repair ran."
tags:
  - anti-pattern
  - code-review
  - tool-agnostic
  - arxiv
aliases:
  - minimality instruction
  - explicit minimality prompt
  - keep the diff minimal instruction
last_reviewed: 2026-08-17
maturity: emerging
status: current
---

# Minimality Prompts as a Patch-Size Control

> Across 28 SWE-bench repair systems, explicitly instructing minimality was associated with patches as large as instructing nothing; patch size tracked how the repair ran.

Two conditions bound this finding: it was measured on repository-level agentic repair against SWE-bench Verified, and the authors classify the design-factor analysis as "*association* rather than *causation*" ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)). Inside those bounds, the line you would write into `AGENTS.md` or a system prompt predicts nothing about the diff that comes back.

## What the measurement shows

Luo et al. compared each successful patch from 28 leaderboard approaches against the developer patch for the same instance. All 28 were larger. The median approach produced "121.78% more total changes, 80.91% more net changes, and 43.99% higher cyclomatic complexity" ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)).

Grouping those systems by how they handle minimality gives the anti-pattern. Systems stating the rule explicitly sit at +208.83% total and +168.05% net changes; systems stating nothing sit at +191.39% and +194.09%. The two metrics disagree on which group is worse: "explicitly instructing minimality… yields patches as large as no instruction" ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)).

One column complicates the headline. Implicit guidance, where size pressure comes from task framing rather than a stated rule, is associated with the study's smallest patches at +49.65% total and +9.56% net, and the explicit-against-implicit contrast carries the table's largest effect size (p<0.001, |δ|=0.28) ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)). Prompt-level design is not inert. The stated rule is the part that tracks nothing.

## Why it works

Patch size is settled by the search that produced the patch, so the instruction arrives after the volume is fixed. The factors that do move it govern how much code the agent touched. Iterative refinement is associated with +406.46% total changes against +95.60% without it, and context scope runs from +72.93% for structured context to +300.34% for a fixed window, both at p<0.001. Output format shows a negligible effect (|δ|=0.03) ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)). Each refinement round leaves more edits behind, and wider context exposes more code to edit. The authors name the tension: "The mechanisms that raise resolution also inflate the patch, a tension prompting cannot resolve."

Markus Eisele reaches the same conclusion from practice: a scope limit written into a system prompt or `AGENTS.md` "is still guidance", and a budget that is "another paragraph in the prompt" can be ignored, reinterpreted, or violated and then reported as done ([The Main Thread, 16 June 2026](https://www.the-main-thread.com/p/coding-agents-change-budget)).

## When this backfires

- Deleting the instruction is not the lesson. It costs nothing, and the framing-level variant correlates with the smallest patches in the study. Stop counting it as the control.
- Systems at the small end have little headroom. Measured separately, systems without iterative refinement sit at +95.60% total changes and structured-context systems at +72.93% ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)), so a size gate there adds latency against a thin margin.
- Every shrinking method tested bought size with correctness. Prompting a stronger model to refine a finished patch cut SWE-agent's total changes from +690.91% to +41.70%. Across the four host systems that prompting baseline "sacrifices 29 to 44 resolved instances per host", and untangling and minimality-aware baselines "lose 49 to 217" ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)).
- Raw diff size is the wrong threshold. The four approaches above +1000% total changes are the four most auxiliary-heavy, editing tests and reproduction scripts, and for them "raw patch size overstates the production change a reviewer must reason about" ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)).
- Without a trustworthy suite, shrinking is unverifiable. The paper scopes its conclusions to settings "where candidate patches and validation outcomes are observable" ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)), the same limit that governs [trajectory minimization](codeslop-trajectory-minimization.md).

The paper's own remedy, a post-generation refiner trained with supervised fine-tuning and direct preference optimization ([Luo et al., 2026](https://arxiv.org/abs/2608.13292v1)), is not adoptable without training a model.

## Example

**Before — patch size delegated to an instruction.** The sentences Eisele reports teams adding to a system prompt, repository rules, or an `AGENTS.md` ([The Main Thread, 16 June 2026](https://www.the-main-thread.com/p/coding-agents-change-budget)):

```markdown
- touch as few files as possible
- do not change public APIs
- ask before making broader architectural changes
```

**After — the limit decided before the run and checked outside the model.** Eisele's published change-budget items, quoted:

```markdown
- Which paths the agent may touch
- How many production files it may change
- Whether it may add dependencies
- Whether it may change public APIs
- Which areas are protected outright
- Which checks must pass before a human even reads the diff
- Which conditions force escalation
```

The "before" block is guidance the generator may satisfy or not, and nothing downstream can tell which happened. The "after" list changes the question from whether the agent finished to "whether it stayed inside the agreed budget while completing the task" ([The Main Thread, 16 June 2026](https://www.the-main-thread.com/p/coding-agents-change-budget)).

## Key Takeaways

- Do not report a minimality instruction as your patch-size control. Nothing downstream can distinguish an agent that obeyed it from one that ignored it.
- If you need smaller patches, change the generator's context scope or its refinement rounds, and expect to resolve fewer issues when you do.
- Price the correctness loss before wiring any size-reduction step into CI. Every method tested cost resolved instances.
- Gate on production change, not raw diff size. Auxiliary test and reproduction-script edits dominate the most verbose systems.
- Treat the evidence as association across 28 heterogeneous systems classified from public artifacts, which is how the authors label it.

## Related

- [CodeSlop: Search-Trajectory Residue in Agent Patches](codeslop-trajectory-minimization.md) — what the removable residue is, and a search-based way to strip it
- [Prompt as Security Knob](prompt-as-security-knob.md) — the same false-control shape in the security domain
- [Deletion Avoidance: Agents That Guard Code Instead of Removing It](deletion-avoidance.md) — another way agent patches grow past the developer patch
- [PR Scope Creep as a Human Review Bottleneck](pr-scope-creep-review-bottleneck.md) — what oversized changesets do to review throughput
- [Reviewer's Playbook for Agent-Authored Pull Requests](../../code-review/reviewers-playbook-agent-authored-prs.md) — where to spend attention once the diff is already large
