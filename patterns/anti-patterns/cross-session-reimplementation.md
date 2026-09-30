---
title: "Cross-Session Re-Implementation of Existing Agent Code"
term: "Cross-Session Re-Implementation"
description: "Agents that build on one workspace across fresh sessions read less repository code and rewrite their own earlier functions while tests stay green."
tags:
  - agent-design
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - cross-turn re-implementation
  - agent code reinvention
  - self-reuse decay
last_reviewed: 2026-09-30
maturity: emerging
---

# Cross-Session Re-Implementation of Existing Agent Code

> Fresh agent sessions on one workspace read less repository code and rewrite their own earlier functions, and the tests still pass.

Cross-session re-implementation is duplicated logic that builds up when a chain of separate agent sessions extends the same codebase. A later session gets a task, does not call the helper an earlier session wrote, and writes an equivalent one. Each per-turn test run checks behavior, so the copy passes.

## Conditions

The evidence comes from one preprint. It applies under these conditions:

- Each task is a chain of turns. Every turn starts a fresh agent session, and the workspace persists across turns ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1)). The finding concerns chained sessions, not context rot inside one long session.
- The benchmark is Python only. The RepoReuse setup has 75 chains of 5 turns over 5 libraries, run with 2 harnesses and 4 models, for 3,000 turns ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1)).
- The conditions are harsher than a normal repository. "Git history is deleted, since git log would expose later changes." The task text also never names the repository code to reuse ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1), Appendix A.3).
- The paper is a single version-1 preprint, and its authors say widening the repository pool and the model-harness grid is work in progress. No outside group has replicated it.

Figures below average the eight model-harness configurations unless the text names one.

## What the measurements show

Repository exploration shrinks. The agents "read 83.6% of relevant repository code at turn 1 on average, but only 35.4% at turn 5" ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1)). Here "read" means recall: the share of a turn's reuse targets where the agent opened at least one line of the source. Repository reuse falls far less than recall over the same turns. The paper says later reuse increasingly happens without reading the target, plausibly from call sites in the agent's own earlier code.

Self-reuse decays even though access is complete. Agents read their own earlier code almost every time and still skip part of it. In the paper's words, "every configuration reads at least 98.9% of its own earlier targets, yet self reuse ranges only from 67.0% to 86.4%. The gap therefore lies in the decision to build on the code that was found, not in finding it." ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1)). Self-reuse falls from 83.9% to 69.1% from turn 2 to turn 5.

Duplication follows. The share of task chains with a cross-turn re-implementation "climbs from 13.8% at turn 1 to 50.8% at turn 5, while pass rates barely move" ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1)). The paper counts a function as re-implemented when the new code does not call it but does call at least 80% of the non-builtin functions it calls, for functions that call three or more such functions. That is a call-overlap heuristic, not a clone detector.

## Why tests do not catch it

A per-turn functional test checks behavior. A rewrite that behaves the same passes it. The paper's Appendix C case shows the shape. The agent read the turn-4 source in full and rewrote the dtype coercion, group masking, categorical ordering, and mean-centering logic in 262 lines. The reference solution reaches the same behavior in 68 lines by calling the turn-4 function. The submission passes 10 of 10 tests ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1), Appendix C).

The cost is a bug fix that you must apply twice. That follows from ordinary duplication reasoning, and the paper does not measure it downstream.

"Pass rates barely move" holds within one agent setup. Across configurations, the paper reports that reuse, correctness, and redundancy move together ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1)). You cannot conclude that reuse and correctness are unrelated.

## Mitigations

### Audit across sessions, not per diff

A per-PR review and a per-turn test each see one step. Run a duplicate or clone check over the modules that agents created across several sessions, and treat its output as a prompt for a human reviewer. The per-PR scan is in the [Reviewer's Playbook for Agent-Authored PRs](../../code-review/reviewers-playbook-agent-authored-prs.md).

### Hand the next session an interface list

The paper compared three memory settings in one configuration (OpenCode with Qwen3.7-plus). "Listing the interfaces of earlier functions raises self reuse from 30.0% with no memory to 67.8%". Supplying the full source of earlier work left self reuse at 29.2%. Duplication, averaged over the five turns, was highest with full source, at 70.7% of chains against 46.7% with the interface list ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1), Section 4.4).

Three limits apply:

- The result comes from one configuration.
- The authors note that "interface memory explicitly encourages reuse while source memory does not, so the two factors cannot be fully separated."
- "Interface memory mitigates rather than removes the problem, however: self reuse still declines over turns, from 82.9% to 58.9%."

### Point the agent at existing library code

The interface list has a cost. With it, agents "rely on the note rather than exploring", and repository recall fell by 61.6 points against 30.5 without memory ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1), Section 4.4). The note lists only the agent's own functions. Add an explicit pointer to the repository internals the task touches.

## Why it happens

The paper describes two gaps. On the repository side, once the workspace holds the agent's own code, reuse decisions come increasingly from signatures and priors instead of current-turn observation. On the self side, the agent has the code in view and still writes a new version, a decision gap and not an access gap ([arXiv:2609.35357v1](https://arxiv.org/abs/2609.35357v1)). Reading more does not close it: the paper's delivery prompt already asks the agent to reuse existing modules, and the gap persisted (Appendix B.2). The paper gives no cause for that disposition.

## When this backfires

Auditing for duplication costs reviewer time and can push agents the wrong way. Skip or soften it in these cases:

- Prototype or throwaway code. The code may be deleted before a second fix lands.
- Near-fit helpers. Forcing reuse of a function with slightly different edge-case behavior turns a visible copy into a hidden bug. Sandi Metz writes that ["duplication is far cheaper than the wrong abstraction"](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction).
- A clone detector used as a merge gate. A call-overlap threshold also flags legitimate parallel code, such as per-format parsers, and an agent told to clear the gate may force a bad merge.
- A push toward more abstraction. [Abstraction Bloat](abstraction-bloat.md) records the opposite failure.
- Single-session tasks. The paper measured chained sessions and says nothing about one-shot work.

Field data points the same way but does not prove cause. GitClear reports a spike in duplicate code blocks and a continued decline of moved lines, which it uses as a sign of code reuse ([GitClear 2025](https://www.gitclear.com/ai_assistant_code_quality_2025_research)). SlopCodeBench separately finds structural erosion when agents extend their own code while checkpoints pass ([arXiv:2603.24755v2](https://arxiv.org/abs/2603.24755v2)).

## Example

The paper's Appendix C case.

Before: the agent reads the turn-4 source in full, never imports it, and writes 262 lines that repeat the coercion, masking, ordering, and centering steps. The tests pass 10 of 10. A later fix to group masking must now be made in two places.

After: the reference solution calls the turn-4 function and aggregates its output in 68 lines. A duplicate check across the chain's new modules would flag the 262-line version for a human to review.

## Key Takeaways

- The effect applies to chained fresh sessions on a shared workspace, not to one long session.
- Agents read nearly all of their own earlier code and still rewrite part of it, so the gap is in the decision, not in access.
- A per-turn test suite cannot see the duplication. That holds within one agent setup, not across models.
- A short interface list beat full source in one configuration, at the cost of less exploration of existing library code.
- Treat duplicate-check output as a review prompt. Duplication is sometimes the right call.

## Related

- [Reviewer's Playbook for Agent-Authored PRs](../../code-review/reviewers-playbook-agent-authored-prs.md)
- [Verification Capacity and the Quality Ceiling](../../verification/verification-capacity-quality-ceiling.md)
- [Abstraction Bloat](abstraction-bloat.md)
- [CodeSlop: Search-Trajectory Residue in Agent Patches](codeslop-trajectory-minimization.md)
- [Large-Codebase Coding-Agent Failure Patterns](large-codebase-agent-failure-patterns.md)
