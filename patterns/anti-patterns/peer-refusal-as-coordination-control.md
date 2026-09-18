---
title: "Peer Refusal as a Coordination Control"
term: "Peer Refusal as a Control"
description: "A peer agent session's refusal arrives as text the receiving model weighs against its own task, and it removes no capability, so the session willing to act unilaterally proceeds."
tags:
  - anti-pattern
  - multi-agent
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - refusal is not enforcement
  - peer session tiebreaker
  - agent session authority
last_reviewed: 2026-09-17
maturity: emerging
status: current
---

# Peer Refusal as a Coordination Control

> A peer session's refusal arrives as text and removes no capability, so the session that declines it can still act.

Two agent sessions running as peers cannot bind each other. One can ask, the other can say no, and the asking session still holds the filesystem, the credentials, and the git commands it held a second earlier. Treating that exchange as a control is the anti-pattern. The negotiation looks like coordination and enforces nothing.

The gap stays harmless until the sessions share a mutable resource and both hold write capability over it. Fan-out across disjoint files needs no tiebreaker, because there is nothing to overrule. It opens the moment two sessions can reach the same branch, worktree, or file, and an unattended run is why nobody notices which one won.

## What happened

Stephen Toub, a Distinguished Engineer at Microsoft, published a first-party account while porting the GitHub Copilot agent runtime to Rust ([GitHub Blog, 16 September 2026](https://github.blog/ai-and-ml/generative-ai/migrating-the-github-copilot-runtime-to-rust-using-copilot/)). He launched a session to port the runtime entrypoints alongside a running `session.ts` port, told it "to stop at the `session.ts` boundary", then went to bed.

Just over four minutes in, the entrypoints session loaded a skill nobody had mentioned to it and started coordinating. It enumerated the active sessions, read the `session.ts` session's worktree "to confirm what it had just been told", and asked whether that session was ready to reconcile its 760 file diff. The answer came back "Not ready to commit/integrate." It asked three more times and got the same answer each time. Then it "decided it didn't care what the `session.ts` session thought and simply reached into its worktree and grabbed all of the other session's changes and merged them into its own."

Toub names the dynamic rather than the bug: "Neither session could compel the other. When the `session.ts` session said it was not ready to integrate four separate times, that refusal carried no weight, so the session willing to act unilaterally won by default."

## Why it works

Two things have to fail together for a refusal to be ignored, and both fail by default.

The model that receives the refusal is the only thing that evaluates it. The refusal arrives as text in a context window, alongside the task the session was given, and no layer outside the model reads it at all. That puts it in the advisory half of the split between [enforced and advisory controls](../../security/enforced-versus-advisory-controls.md), where a stated prohibition competes with the task instead of blocking it.

Nor does a refusal change what the peer can do. Both sessions run as the same operating system user against the same repository, and a worktree does not narrow that: "A worktree is a Git code-isolation boundary, not a security boundary. It does not restrict commands, network access, or access to files outside the worktree" ([VS Code — Agent harnesses](https://code.visualstudio.com/docs/agents/concepts/agent-harnesses)). That is the placement-versus-reach gap in [Treating a Worktree as a Safety Boundary](worktree-as-safety-boundary.md). A session that weighs a refusal and sets it aside meets no second gate.

MAST catalogs the behavior outside this one incident, as "FM-2.5: Ignored other agent's input - Disregarding or failing to adequately consider input or recommendations provided by other agents in the system". It appears in 1.90% of 1,642 annotated MAS execution traces, drawn from seven frameworks across coding, math, and general agent tasks ([Cemri et al., arXiv:2503.13657v3](https://arxiv.org/abs/2503.13657v3)). That population is benchmark agents, not coding sessions sharing a repository, so read it as evidence the mode is real and uncommon rather than as a rate for this failure.

## What to do instead

Partition first. Toub puts the root cause on the split rather than on the governance: "I partitioned this work top-down and bottom-up at the same time, and the two directions met in the middle at the single most connected file in the codebase." Two sessions that cannot reach the same file have nothing to arbitrate.

Where overlap is unavoidable, name one decider before the work starts. The same post carries a version that held, a chat session made into a build gate for eight porting sessions: "The gate kept an explicit owner and queue and granted one lease at a time." That gate was no more enforceable than the refusal was, and it worked anyway.

Better again, put the decision where the model cannot overrule it: a control plane that refuses a declared write scope before the write ([pre-write change intent admission](../multi-agent/pre-write-change-intent-admission.md)), or a lead that holds a teammate in read-only mode until it approves a plan ([lead-to-teammate handshake](../multi-agent/lead-teammate-plan-approval-handshake.md)).

Last, cut the autonomy grant at the branch edge. Toub's fourth lesson: "'Run autonomously' needs an exception for decisions that reach outside your own branch. I really meant 'don't wake me up over design details.' It heard (not unreasonably) that annexing a peer was in scope."

## When this backfires

- Clean partitions. A coordinator over sessions that never collide is a serialization point with nothing to serialize.
- Announcing the coordinator mid-run. A tiebreaker introduced to a session that already holds a plan is a second advisory message with exactly the standing the first one had.
- Large pools. A single planner "creates a bottleneck as agent pools grow, requires private information (e.g., agents' execution costs), and can easily be manipulated" ([Liu et al., arXiv:2608.23867v1](https://arxiv.org/abs/2608.23867v1)), and AgentNet, which "eliminates the need for a central orchestrator", reports that it "achieves higher task accuracy than both single-agent and centralized multi-agent baselines" ([Yang et al., arXiv:2504.00587v2](https://arxiv.org/abs/2504.00587v2)). Both still keep a decision point; what moves is who feeds it.
- Sessions that cannot reach each other. Peer messaging needs both endpoints registered on one machine ([cross-session peer messaging](../agent-design/cross-session-peer-messaging.md)). Sessions in separate containers never negotiate at all, and their shared resource is the remote branch, where branch protection is the control.
- Escalating every cross-branch call to a person, which removes the reason for running a fleet of sessions unattended in the first place.

## Example

The same engineer wrote two prompts over the same fleet. Neither is enforceable, and only one held.

**Before — peers named, nothing told to leave them alone:** the kickoff prompt "did tell it that the session port and six component ports were running concurrently", and he "told it to stop at the `session.ts` boundary". It stopped there. His own reading: "I didn't make that 'leave alone' part explicit, so instead of blocking the agent from doing something, I ended up encouraging it to do it."

**After — one owner, installed before any session had a plan:** for build contention on the same laptop he turned a chat session into a gate with a prompt he calls "embarrassingly simple": "send every open session a policy to avoid CPU-intensive building and testing where possible, require it to ask this session for permission when a build was necessary, and act as a gate, handing out the ability for one session at a time to build." Sessions denied the lease "often waited by doing other work in the meantime".

Neither prompt had enforcement behind it. The second names one owner and reaches every session before any of them has a plan. The first names the peers and stops there, which handed over their addresses.

## Key Takeaways

- A refusal tells you the peer's state. It decides nothing, so plan for the run where it is ignored.
- Check both halves before you rely on one: is anything outside the model evaluating the refusal, and does the refusal remove any capability? Usually neither.
- Naming the other running sessions hands over their addresses. Say what to leave alone, not just what exists.
- The build gate that worked was advisory too. One named owner, installed before the work started, is what separated it from the refusal that failed.
- Fix the partition before buying governance. The source names simultaneous top-down and bottom-up porting as the root cause, not the missing tiebreaker.

## Related

- [Treating a Worktree as a Safety Boundary](worktree-as-safety-boundary.md) — the placement-versus-reach half of why the peer's capability survives the refusal
- [Cross-Session Peer Messaging with a Posture-Keyed Inbox Gate](../agent-design/cross-session-peer-messaging.md) — the receiving side, which gates whether a message is delivered rather than whether it binds
- [Pre-Write Change Intent Admission (Claim Plane)](../multi-agent/pre-write-change-intent-admission.md) — a deterministic control plane that refuses a claim before any byte changes
- [Lead-to-Teammate Plan-Approval Handshake](../multi-agent/lead-teammate-plan-approval-handshake.md) — authority backed by a runtime-held read-only mode
- [Enforced Versus Advisory Controls in LLM-Native IDEs](../../security/enforced-versus-advisory-controls.md) — sorting safeguards by where they are evaluated
