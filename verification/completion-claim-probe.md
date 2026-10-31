---
title: "Probing an Agent's Completion Claim in a Disposable Fork"
term: "Completion-Claim Probe"
description: "Call the critic when the agent claims it is done, give it execute access to a fork of that state and of the initial state, and resume after a rejection."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - completion-claim probe
  - probe-and-resume search policy
  - probing critic in a forked state
last_reviewed: 2026-10-18
maturity: emerging
---

# Probing an Agent's Completion Claim in a Disposable Fork

> A critic given only the transcript rejected 60% of passing candidate states; one that could run commands in a fork rejected 22%.

A completion-claim probe calls the critic at the moment the actor says it has finished, and hands it execute access to a throwaway fork of that state plus a fork of the initial environment. The critic lists the task's requirements, runs whatever programs it needs to check each one, then either submits the state or sends the actor "the failures, the rationale for why they failed, and how the critic checked", and the actor resumes from the state it claimed ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).

## Four conditions before you build this

1. The environment can snapshot, restore, and fork a running container. Without a fork there is nowhere safe to run a destructive check.
2. Your actor's first claim fails often enough to leave room. GPT-5.6 Luna passed 63.4% of first claims and the loop worked on the rest; on a 15-task subset with stronger actors and critics, "None of the three combinations gains significantly" ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).
3. A program can settle the requirement. On the 19 tasks whose verifier holds a reference value unrecoverable from the environment, the probing critic accepted 31% of failing states. Where the verifier runs the artifact or probes a service it accepted 19%. With nothing to test against, it "tends to agree with the actor's interpretation of the task completion" ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).
4. The probe's time comes from a budget you sized for it. The actor and the critic shared one clock. Swapping in Claude Sonnet 5 as the critic took the median probe from 33 seconds to 138, and that cost trials outright: "Because the clock is shared, 59 loops run out of time during a probe, against 13 with Luna" ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).

## When the critic is called changes what it can see

Measured on 89 Terminal-Bench 2.1 tasks with GPT-5.6 Luna on both sides, the same access is worth very different amounts at the two positions. The final-state row covers 406 candidate states, where a false reject is a passing state the critic rejected ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).

| Where the critic is called | What the critic delivers |
|---|---|
| 25% through the trajectory | Pairwise ranking accuracy of 49%-56% against a 50% chance baseline: "we do not detect a statistically significant selection gain over random choice" |
| 75% through | Ranking accuracy of 64%-69%, with execute access worth +4.4 points [-0.9, +9.9] pooled over the intermediate depths |
| At the candidate final state | False rejects fall from 60% of passing states to 22%. Misclassification falls from 36%-39% to 22%, and "Most of the gap is in false rejects" |

End to end over those tasks and five trials each, the loop raised pass@1 from 63.4% to 72.4%, a gain of 9.0 points with a 95% interval of +5.6 to +12.6, at 2.2 times the baseline's model cost, rising on 30 tasks and falling on 1 ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)). The configuration it replaces, Monte Carlo tree search with a transcript-only critic, reached 64.0% at 3.81 times the cost.

## Why it works

The trajectory is not the state. The actor records its reasoning, its tool calls, and the outputs it saw, while the state of the computer also holds files, processes, memory, packages, and databases that changed as side effects it never observed. The paper's one-line explanation is that "evaluating a terminal task is itself a terminal task": the evidence has to be produced by running something, not recalled from a transcript. A disposable fork makes producing it safe, because the critic can delete files, install interpreters, and kill processes on a copy nobody resumes from.

Hand it a second fork of the initial environment and the requirements about preservation become checkable too. Across 404 candidate states "the fork raises accuracy from 76% to 80%", false rejects fall from 24% to 17%, and the critic's disagreement with its own second verdict on the same state drops from 18% to 9% ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)). The authors read that as more evidence rather than more severity: "its verdicts become more accurate and consistent, not stricter".

Mid-run evaluation fails for a different reason, which is why better observation does not rescue it: a half-finished state carries limited evidence about whether the trajectory ends well.

## Resume, and cap the rounds

After a rejection, put the actor back where it was. Restarting from the initial state with the same feedback submitted a passing state in 66.3% of trials against 72.4% for resuming, -6.1 points [-10.1, -2.2], at 1.6 times the cost and 9.3 minutes per trial instead of 7.8 ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).

The paper's loop allows up to six critic rounds, but its analysis finds a cap of three claims would lose nothing. That lands where [bounded repair-loop iterations](bounded-repair-loop-iterations.md) puts the cap from other evidence. 64% of claiming trials end after one round, a second claim lifted the submitted pass rate from 63% to 70% and a third to 73%, and "further rounds add nothing measurable".

## When this backfires

- Both sides are already strong. On the 15-task subset the loop showed no statistically significant gain with GPT-6 Astra or Claude Opus 5.5 as the actor, where "Critics help when actors can repair mistakes they fail to identify themselves". Eight Opus trials were refused by a content classifier and counted as zero, weakening that subset further ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).
- Shared state defeats the fork. "Forks do not isolate writes to external databases or shared services, so destructive checks require isolating those dependencies or restricting critic actions" ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).
- You are using the critic to pick among many samples instead of to judge one. On grade-school and competition math with two 7B models, verifier-guided search lost its advantage over plain resampling as the sample budget grew, because imperfect verifiers "misrank candidates and erroneously prune all valid paths" ([Yu et al., arXiv:2502.00271v1](https://arxiv.org/abs/2502.00271v1)).
- The finding is about prompted LLM critics, not step-level evaluation in general. In long-horizon software-engineering runs, FLARE distills a generative reward model that intercepts high-risk steps as they happen, reporting a single rollout that beats a five-rollout baseline with five times fewer tokens ([arXiv:2609.23808v1](https://arxiv.org/abs/2609.23808v1)). The primary study states the limit itself: "These measurements do not rule out search with a stronger value estimator or another search policy, and do not show that completion is the optimal time to intervene."
- The evidence is one paper and one actor model for the headline number. On SWE-bench Pro the loop moved the pass rate from 80% to 88% over 227 graded tasks, but "the gain comes from the medium tasks, and on the hard tasks it cannot be told apart from zero" ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)).

## Example

In the `modernize-scientific-stack` task, the critic with execute access to a fork of the final state rejected the actor's work because it could not tell whether a legacy file had been preserved. Given a fork of the initial state as well, it compared the file's hash in both and accepted ([arXiv:2610.21088v1](https://arxiv.org/abs/2610.21088v1)). Nothing about the actor's work differed between those two runs. The reference state was the missing evidence, and 15 of that critic's 56 false rejects came from requirements of this shape.

The read-only version of the same critic shows why inspection is not enough. Even on tasks whose verifier only reads files and compares them against a stored value, it rejected 42% of passing states against 9% for the critic that could execute, and in 93% of those rejections it reported insufficient evidence rather than a broken requirement.

## Key Takeaways

- Spend the critic budget at the completion claim. Partial-state ranking sat at 49%-56% a quarter of the way through, where chance is 50%, and execute access was worth +4.4 points [-0.9, +9.9] pooled across the three intermediate depths, an interval spanning zero.
- Read-only inspection is the configuration that looks careful and rejects correct work: 42% false rejects against 9%, on tasks whose own verifier only reads files.
- Give the critic a second fork of the initial state whenever any requirement says something must be preserved, recovered, or left unchanged.
- A critic that rejected 21% of passing first claims in the end-to-end loop was still worth running, because the actor rescued 57 of those 60 proposals.
- Measure the loop on your own actor before budgeting for it. The published +9.0 points came from a model that failed over a third of its own completion claims.

## Related

- [Grade Agent Outcomes, Not Execution Paths](grade-agent-outcomes.md) — the prior decision to judge the final state rather than the path, which this extends by letting the judge run programs against that state
- [Premature Completion: Agents That Declare Success Too Early](../patterns/anti-patterns/premature-completion.md) — the failure the completion claim is a trigger for, and the reason the claim cannot be taken at face value
- [Sandbox Forking: Branch Agent Runs From a Warm Snapshot](../patterns/agent-design/sandbox-forking.md) — the same fork primitive used for parallel runs instead of for verification
- [Bounded Repair-Loop Iterations](bounded-repair-loop-iterations.md) — the independent case for the round cap this loop converges at
- [Learned Prefix Monitors for Agent Traces](learned-prefix-monitors-agent-traces.md) — what mid-run trajectory reading can and cannot deliver, which is the position this page argues against
- [A Separate Critic Over Completion-Time Self-Checking](separate-critic-over-self-recheck.md) — the layer comparison behind calling a separate critic at all, where the agent's own completion-time recheck is the one layer of four its authors recommend against
