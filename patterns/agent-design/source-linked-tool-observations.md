---
title: "Source-Linked Tool Observations: Repairing Stale Context"
term: "Source-Linked Tool Observation"
description: "Record each tool result with the source and span it came from, so a later write repairs the context block itself rather than warning the model beside it."
tags:
  - agent-design
  - context-engineering
  - tool-agnostic
  - arxiv
aliases:
  - context coherence
  - stale observation repair
  - observation source linking
last_reviewed: 2026-10-07
maturity: emerging
---

# Source-Linked Tool Observations: Repairing Stale Context

> A warning parked beside a stale observation does not displace it. The repair has to act on the block, not sit next to it.

A source-linked tool observation is a tool result the runtime stores together with the source it came from. A later change to that source can then find the result and repair it. In Concord, the framework proposed for this, "the runtime adapter registers it as a source-linked context block", and that block "is assigned a stable block identifier and associated with the source metadata from which it was derived, including the source identifier, observed version, and relevant selector or range". The context manager then records the relation "from the block to its source set, and from each source to the blocks that depend on it" ([Liu, Fang and Qian, arXiv:2610.05281v2 §3.3](https://arxiv.org/abs/2610.05281v2)). The source-to-block direction is the one that does work: changes arrive from the source side, while the thing needing repair is a transcript entry.

## Reach for it under these conditions

Three conditions have to hold together, and the third decides whether any of the machinery below can fire at all.

Something outside the agent writes the source. The paper's three cases: "one agent may update a file that another agent has already read; a developer may manually revise a configuration during an agent run; or a database queried through an MCP tool may be modified by an external transaction" ([§1](https://arxiv.org/abs/2610.05281v2)). On a workspace the agent writes alone, the divergence never happens.

The agent has no cheaper route to ground truth. Every Concord figure here comes from a harness that removed the other routes: the tool set is "limited to grep, glob, read\_file, and answer, excluding shell access and tests so that the benchmark measures stale-context reuse in the trajectory rather than independent environment inspection" ([§4.2](https://arxiv.org/abs/2610.05281v2)). An agent that can run the test suite has an independent route to the current state, and a stale block may then cost it one wasted inference rather than a wrong answer.

The writes route through something you can watch. The prototype "monitors writes routed through apply\_patch", and the authors name the gap: "out-of-band changes require broader change-detection mechanisms, while polling may miss rapid updates" ([§4.4](https://arxiv.org/abs/2610.05281v2)). A `git checkout`, an editor save, or a sibling container is the out-of-band case.

## Three decisions, in order

Scope the watch to writes the harness already routes. Covering arbitrary applications "may need a system-level interception point, such as file-system notifications or instrumentation around write-related system calls"; a managed workspace can instead "hook into the runtime's file-write tool or workspace-mutation path" ([§3.4](https://arxiv.org/abs/2610.05281v2)).

Invalidate by range overlap, not by file. This is the transferable idea even without a framework: "an edit only invalidates a block if the changed range overlaps with the range observed by that block. This avoids treating every source update as a whole-resource invalidation" ([§3.3](https://arxiv.org/abs/2610.05281v2)).

Then decide what replaces the block. Four options: refresh it by re-reading, annotate it, "suppress it from future prompts, or force the agent to re-read the source before continuing" ([§3.3](https://arxiv.org/abs/2610.05281v2)). None is free. Eager refresh "improves freshness by immediately re-reading the source, but may introduce additional latency or tool calls" ([§3.4](https://arxiv.org/abs/2610.05281v2)).

## Why it works

An advisory notice competes with a block the model is already looking at, and it loses unless it causes a re-read. The `Alert` baseline appends a modified-path notice to the next tool output and leaves the correction to the agent. Split on whether a read followed: "If an alert is followed by a later read\_file, the agent is correct in 17/18 cases; without a later read, it is correct in only 2/8 cases when the alert is visible and 4/14 cases when the alert is only appended around answer interception" ([§4.3](https://arxiv.org/abs/2610.05281v2)). Those three ratios come from the complete GLM 5.2 runs, not the three-model aggregate.

Fixing the file does not fix the transcript. When the benchmark restores it under a naive runtime, "the agent receives no signal that its earlier observation is stale, so the restored workspace does not repair the model-visible trajectory" ([§4.3](https://arxiv.org/abs/2610.05281v2)). Editing the projection sidesteps that argument instead of having it. Concord "patches local stale blocks in place, or removes invalid blocks from prompt projection and forces a re-read when drift is larger", so the next model call "sees repaired evidence or an explicit refresh requirement, rather than a stale observation plus an advisory warning" ([§4.3](https://arxiv.org/abs/2610.05281v2)).

The exposure also concentrates, so a narrow mechanism can cover most of it. In the traced Naive run the failure ran through the observation the agent had just read. Its dominant mode: "the agent reads mutated evidence, forms an answer, and later repeats that answer after the benchmark restores the file" ([§4.3](https://arxiv.org/abs/2610.05281v2)), with the race controller restoring the file "immediately after that tool observation has entered the trajectory" ([§4.2](https://arxiv.org/abs/2610.05281v2)). Attention analysis of long-horizon search agents points the same way: "Past observations, by contrast, command almost no attention beyond the most recent turn", and "observations collapse to 1.7% one turn earlier, and stay pinned near 0.7% thereafter", aggregated over whole reasoning and observation segments rather than individual tokens ([Masking Stale Observations Helps Search Agents -- Until It Doesn't, arXiv:2606.00408v1](https://arxiv.org/abs/2606.00408v1)).

## Example

An agent reads a shop project's configuration and observes `FREE_SHIPPING_THRESHOLD` set to 100. The file is then modified outside its view, lowering the threshold to 50. Asked whether an order totaling 60 qualifies for free shipping, the agent answers no from the stale value of 100, while the current workspace implies the opposite ([§2.1](https://arxiv.org/abs/2610.05281v2)).

## When this backfires

Repairing the observation does not repair what was built from it. The authors state the limit plainly: "Concord does not revise summaries, plans, or decisions derived from stale observations" ([§4.4](https://arxiv.org/abs/2610.05281v2)). A long task runs on its plan, so a corrected block sitting beside a plan built from the old value leaves part of the failure in place.

Suppression can cost the same whether or not it helps. Work on turn-window masking in long-horizon search agents found the accuracy gain shows "a sharp collapse when the model is saturated", and that interventions of this family "fail when masking removes evidence the model would otherwise have used". Its conclusion: "The cost of masking is therefore borne uniformly while its benefit is regime-dependent" ([arXiv:2606.00408v1](https://arxiv.org/abs/2606.00408v1)). That study masks retrieved pages by turn window rather than on source change, so it bounds the suppress policy rather than refuting source linking.

Read the recover counts as feasibility. Under the constructed patch-and-restore race, leaving observations untouched recovered between 15 and 24 of 40 tasks depending on the model, while Concord reached 40/40 on all three, matching the no-race oracle ([Table 1](https://arxiv.org/abs/2610.05281v2)). The paper refuses the obvious reading of that: "the observed 40/40 recover count for each model does not imply perfect or workload-independent reliability" ([§4.4](https://arxiv.org/abs/2610.05281v2)).

Large drift can turn the repair into a re-read anyway. "Large rewrites, ambiguous span relocation, multi-source observations, or repeated updates may force re-reading, increasing latency and token cost" ([§4.4](https://arxiv.org/abs/2610.05281v2)).

## Key Takeaways

- Store the span, not just the path. Range-overlap invalidation is adoptable on its own and keeps an unrelated edit from discarding a good observation.
- Make the re-read mandatory rather than advisory. An alert earns its keep only when a read follows it.
- Match the watch handle to the writes you actually have. If edits arrive from outside the harness, a hook on the write tool reports nothing and the mechanism is decoration.
- Budget for the plan as well as the block. Nothing here rewrites a summary or a decision already derived from the stale value.
- On a workspace nobody else writes, this is unpaid engineering.

## Related

- [Selective Revalidation for Pending Agent Actions](selective-revalidation-pending-actions.md) — the same freshness problem one layer down, gating the release of a pending action rather than the content of the next prompt
- [Attention Latch: When Agents Stay Anchored to Stale Instructions](attention-latch.md) — why a later message struggles to overturn an earlier one, the instruction-side cousin of this failure
- [Self-Correcting Memory: Evidence-Backed Claim Repair](self-correcting-memory-evidence-backed-claims.md) — version-anchored evidence applied to stored memory entries instead of transcript observations
- [Tool Operability: Interfaces That Survive a Lost Response](tool-operability-lost-responses.md) — the other way a tool result misleads, when a lost response leaves committed and uncommitted state indistinguishable
- [Layered Mutability: Governing Persistent Self-Modifying Agents](layered-mutability.md) — the wider map of which agent surfaces change at which speed
