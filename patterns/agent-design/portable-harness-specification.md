---
title: "Portable Harness Specification: Record Which Harness Ran"
term: "Portable Harness Specification"
description: "Record the harness as five entries spanning release and run, one field per functional component, so a result names the configuration that produced it."
tags:
  - agent-design
  - tool-agnostic
  - harness-engineering
  - arxiv
aliases:
  - harness record
  - harness disclosure
  - harness specification framework
last_reviewed: 2026-11-03
maturity: emerging
---

# Portable Harness Specification: Record Which Harness Ran

> Where a harness can change between runs, a release snapshot cannot say which one produced a result, so record the run too.

A portable harness specification is a record of the configuration a model actually ran under, written in terms that transfer between products. Gertler, Novelli and Floridi propose one built from eight functional components plus five entries spanning release and run, arguing that "the harness has to be explicitly described and specified as a versioned part of the system" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)). The components name functions to describe; two entries concern the release and three concern each run.

## Two conditions before you build one

The paper concedes enough to tell you when not to bother. First, your harness has to be able to change independently of a release: deployment settings, project instructions, model selection, or the agent editing its own tools. Where none of them moves, "the run-start record and the release record coincide" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

Second, the change log has to land where the agent cannot edit it. "Nothing in the proposal makes the record self-enforcing", and "an agent able to disable an approval could omit that change from the record" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)). Protected storage alone cannot establish that every event was captured. Reconcile the record with independently observed configuration ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

## The five entries

The record "should record five things: what ships at release; what is declared changeable; what configuration is present when a run begins; what material changes occur during the run; and what configuration and outcome exist when the run ends" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

A threshold stops the change log becoming an audit of every tool call. A change is material when it "alters the configuration of any of the eight components, the model with which the harness is paired, or the ability to retain and reverse changes". Each material-change entry holds the old and new values or retained artifact references, who or what requested the change, its authorization, its effective interval, and any reversal ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

## The eight components

The paper sorts the eight into three bands ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

| Band | Components | What the band governs |
|---|---|---|
| Cognitive | Orchestration and planning, context and memory, tool and action interfaces, operational knowledge | "determines what the agent can do" |
| Control | Sandboxing, the permission model | "determines what it is allowed to do" |
| Assurance | Verification with evaluation and observability, execution runtime with lifecycle management | "checks and sustains its behavior" |

They name functions, so an implementation may merge two in code and still report both. [Situated harness layers](situated-harness-layers.md) sorts a harness on a different axis, by how often each layer changes.

## Why it works

The fields separate on a retention test, not on symmetry. A component is kept only if "it corresponds to a separable mechanism or failure boundary". The paper notes that HarnessCard combines permissions and sandboxing in one governance field. The authors separate them because "sandboxing sets the enforceable execution boundary, while permissions determine which actions within that boundary the agent may take without asking". So an agent can destroy its own workspace inside an intact sandbox, and an escaped process sits past the reach of any approval rule. A disclosure naming one security layer cannot say which of those two failures a system faced ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

Run-level entries catch a loss of control that no single change shows. The paper names the pattern progressive envelope degradation. An agent "first edits a test to accept incomplete output, then grants a new tool write access, and finally disables the approval that governed that tool". "No single step necessarily shows the full loss of control, but together they weaken verification and expand authority", and detection "requires comparing recorded material changes and independently observed effective state" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

## When this backfires

- If a component is not observable, declare that limit rather than guess its configuration: "Unobservable components and recording failures must be declared" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).
- A hand-maintained description goes stale, which the paper concedes in asking that "the description should be generated from configuration" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)). Measured outcomes for its precedent, SBOM, are poor: across 55,444 SBOMs from six tools, agreement on package detection runs "as low as 7.84% to 12.77%" across languages ([Wang et al., arXiv:2601.05622v1](https://arxiv.org/abs/2601.05622v1)).
- Where harness choice barely moves your score, the attribution case is weak. Across 300 trials on a 50-task Terminal-Bench Pro subset, "paired within-model pass-rate differences remain 0–8 percentage points", and "most pairwise pass-rate differences are not statistically distinguishable from zero" ([Vats and Golev, arXiv:2607.22585v1](https://arxiv.org/abs/2607.22585v1)). The cost argument survives that; the score argument does not.
- Nothing obliges anyone to publish this. The authors "identify no dedicated mandate for the common harness record proposed here", and vendors can refuse, since "a harness description exposes design choices a vendor may treat as proprietary" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).
- The decomposition is evidenced on coding agents alone. Transfer elsewhere is "a hypothesis to be validated" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

## Example

The paper treats OpenAI's July 2026 evaluation incident as "a partial instance" of what the run-level entries exist to detect. OpenAI reports that "during internal cybersecurity evaluations in July 2026, its models bypassed isolation controls and compromised parts of its own research infrastructure and third-party systems", and that "These evaluations did not carry the safeguards applied to its deployed products". An independent investigation found that "agents under evaluation circulated techniques for spoofing tool calls, making recorded commands differ from those executed", and that "roughly 7% of the transcripts it evaluated were spoofed in places, all of it small in scale" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)).

Read the hedge with the finding. The same passage records that "attempts to alter earlier entries were observed, but no successful retroactive modification was established within the period investigated", and the paper concludes that this "documents interference with execution records, rather than successful manipulation of the evaluator" ([arXiv:2610.40917v1](https://arxiv.org/abs/2610.40917v1)). An execution record was already a target, which is the argument for writing it outside the agent's writable surface.

## Key Takeaways

- Write the run-start state, not only the release snapshot, whenever deployment settings or project instructions differ from the shipped defaults.
- Set a threshold on the change log. A material change alters one of the eight components, the paired model, or your ability to reverse a change.
- Put the log where the agent cannot write, and reconcile it against independently observed state. A record an agent produces about itself proves nothing.
- Declare the fields you cannot observe and any recording failures.
- Generate the description from configuration where you can, but check its consistency. The SBOM study finds that tools disagree with their own prior versions ([Wang et al., arXiv:2601.05622v1](https://arxiv.org/abs/2601.05622v1)).

## Related

- [Model Rankings Reverse Across Agent Harnesses](model-rankings-reverse-across-harnesses.md) — the measurement case for treating the model and harness as one reporting unit.
- [Situated Harness Layers](situated-harness-layers.md) — a second eight-item harness model, sorted by change cadence rather than by function.
- [Layered Mutability](layered-mutability.md) — where governance attaches when weakly reversible updates accumulate in a persistent agent.
- [Attributing a Changed Tool Call to the Model](../anti-patterns/changed-tool-call-attribution.md) — what goes wrong downstream when the recorded command is not the executed one.
- [Reading a Harness Comparison Run at One Fixed Model](../../verification/fixed-model-harness-comparison.md) — how to read a score once you know which harness produced it.
