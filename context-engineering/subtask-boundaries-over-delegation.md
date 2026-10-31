---
title: "Subtask Boundaries Over Delegation"
term: "Subtask Boundary Declaration"
description: "Declare where a subtask ends in the agent's own context instead of spawning a child agent at every boundary. On SWE-Milestone, inline scopes matched recursive delegation's score at 73.7% lower total cost."
aliases:
  - work scopes
  - inline subtask scopes
  - subtask boundary declaration
tags:
  - context-engineering
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-29
maturity: emerging
---

# Subtask Boundaries Over Delegation

> Declare where a subtask ends without spawning an agent to run it. On SWE-Milestone, inline scopes matched delegation's score at 73.7% lower cost.

Three conditions decide whether declaring subtask boundaries beats delegating them. The work has to nest more than one level, the markers have to reach the model's input rather than sit only in the harness, and child-agent turns have to be what your bill is made of. Where all three hold, the saving is large. On SWE-Milestone with GPT-5.6 Sol, SpineCodex scored 42.6% against Recursive Subagent's 42.4% and spent $460.77 against $1,749.73 ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)). Where they do not, you are buying a tie and maintaining a runtime for it.

## The two decisions in one call

A subagent call answers two questions at once: where this subtask ends, and who executes it. Recursive delegation answers them together by routing every boundary through a child agent, which "conflates subtask granularity with executing agent choice, adding execution and coordination overhead" ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)). Each boundary you want on the record costs a session.

Spine separates them with four commands. Open enters a child scope the current agent runs itself, Close completes that scope with a result, and Next closes one scope and opens its sibling. Only Spawn hands work out, reserved for "independent subtasks to other agents in parallel". The unit declared is a work scope: "an agent-declared subtask with an explicit entry, a parent task, and a result submitted on completion" ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)).

Five approaches on the same benchmark, harness, model, and budget. SWE-Milestone with GPT-5.6 Sol, 98 milestones:

| Approach | Score (%) | Resolved | Avg. input tokens/req. | Cost |
|---|---|---|---|---|
| Codex, native compaction | 38.1 | 14/98 | 131.2K | $681.22 |
| Context Folding, untrained | 37.1 | 13/98 | 87.3K | $596.25 |
| AgentDiet, trajectory reduction | 36.5 | 12/98 | 92.8K | $1,057.08 plus $41.44 overhead |
| Recursive Subagent | 42.4 | 17/98 | 65.3K | $1,749.73 |
| SpineCodex, inline scopes | 42.6 | 19/98 | 72.3K | $460.77 |

Figures from Table 5 ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)). Read the Context Folding row with care: that baseline reimplements the folding mechanism "without FoldGRPO training", and FoldGRPO is how the published method learns the behavior in the first place ([Sun et al., arXiv:2510.11967v1](https://arxiv.org/abs/2510.11967v1)).

Delegation's bill is where its boundaries went. Child agents accounted for 75.5% of Recursive Subagent's 32,650 model requests, against 8,792 for SpineCodex ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)).

## What has to be in the prompt

The active ingredient is the cue the model can see, not the tree the runtime keeps. One ablation separates the two. It removes "explicit boundary markers and node states from model inputs while retaining runtime state compilation" across three SWE-Milestone projects, with GPT-5.6 Sol at high effort and three runs per configuration. Average input per request climbed to 118.1K-128.6K tokens, a rise of 64-97%, and cost rose 30-42%. Score fell in all three: 36.4% to 29.0% on Navidrome, 72.4% to 67.2% on ripgrep, 33.7% to 27.5% on Element ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)).

A second ablation caps scopes at one level below the root, the shape a single plan-branch-return workflow gives you. Average input per request rose from 59.8K-78.1K to 82.8K-99.5K. Agents in the unrestricted runs did work deeper than one level: counting the runtime root as depth zero, "72.6% of requests with recorded scope depth occur at depths greater than one" ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)). The full configuration beat both ablations on Score by 7.7-27.3% across the three projects, so neither nesting nor visible boundaries carries the result alone.

## Why it works

Closing a scope rewrites only the tail of the context. The completed branch's projection, task description included, is replaced by the returned result, which leaves every token before the scope's entry marker untouched. The paper writes that substitution as `Q·B -> Q·μ`. The prefix therefore stays byte-identical and remains eligible for KV-cache reuse, with the caveat the authors attach: "actual reuse depends on cache availability" ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)).

The second half is what a boundary tells a trimmer. A flat history gives a compaction pass no way to separate a finished investigation from a pending one, so it cuts both. AgentDiet cut source-inspection history from 11.7k to 1.6k tokens while the implementation was still pending. The agent went back and re-read the source, and that run resolved 12 milestones against native Codex's 14 at $1,098.52 against $681.22 ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)). Declaring the boundary makes the same call mechanical: a closed scope keeps only its result, and everything belonging to unfinished scopes stays.

The returns bear that out, and they do it while the input also gains the returned result and other new messages. Input was still shorter after 223 of 224 accepted Close calls and 77 of 80 accepted Next calls, with median decreases across all calls of 23,045 and 35,627 tokens. One recorded outer return in the Nushell migration took model input from 65,815 to 19,207 tokens while the pending subtasks stayed in context ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)).

## When this backfires

- The model does not open scopes. Boundaries are agent-issued, and the behavior is not free. The Context-Folding authors built "an end-to-end reinforcement learning framework FoldGRPO with specific process rewards to encourage effective task decomposition and context management" to make the equivalent branch-and-fold behavior learnable ([Sun et al., arXiv:2510.11967v1](https://arxiv.org/abs/2510.11967v1)). An agent that never calls Open leaves you a flat history plus a runtime to maintain.
- The work does not nest. Capping scopes at one level raised average input per request on its own, because shallow scopes "fail to isolate intermediate interactions within nested subtasks" ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)). Single-layer work pays the bookkeeping and collects little.
- Cost is not guaranteed to fall. SpineCodex cost less than Codex in five of the six benchmark-model settings. The exception was ProgramBench with GPT-5.6 Sol, at a 5.4% increase. On the Pi integration, Qwen 3.8 27B used more total tokens on SWE-Milestone, 2,252.80M against 1,996.97M ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)).
- What you return is all the parent keeps. A closed branch "contributes solely its returned result" while its body stays in the tree ([Xiang et al., arXiv:2610.37224v1](https://arxiv.org/abs/2610.37224v1)), and none of the four commands reads a closed body back. A result that omits a detail needed later puts it out of reach.
- The subtask needs isolation rather than a marker. Inline scopes share one context and one agent, so work that must not see the parent's history, or that should run on a different model, still wants a child.

## Key Takeaways

- Check what your bill is made of first. If child-agent turns are not the bulk of it, the 73.7% gap is not your gap.
- Reserve delegation for parallel work and for subtasks that must not see the parent's context. Other boundaries can be markers.
- Put the markers where the model reads them. Dropping the cues while keeping the tree raised input 64-97% and cost 30-42%.
- Budget for the declaration behavior. The nearest published predecessor used reinforcement learning to make that behavior learnable.
- Expect the gain as cost, not capability. Delegation tied on score, 42.4% against 42.6%, on one benchmark with one model.

## Related

- [Observation Masking: Filter Tool Outputs from Context](observation-masking.md) — the same substitution, one tool result at a time
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md) — phases named up front rather than declared as the agent goes
- [Stage Elision Before Summarization](stage-elision-before-summarization.md) — what to do when a threshold has to decide instead of a boundary
- [The Delegation Decision: When to Use an Agent vs Do It Yourself](../patterns/agent-design/delegation-decision.md) — the overhead case against delegating by default
- [Subtask-Level Memory for Software Engineering Agents](../patterns/agent-design/subtask-level-memory.md) — the retrieval-side counterpart, matching memory to subtask
