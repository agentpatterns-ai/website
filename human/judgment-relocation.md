---
title: "Judgment Relocation: Where Human Decisions Land in an Agent Factory"
term: "Judgment Relocation"
description: "Automating code production moves human decisions to a new position rather than deleting them, but only when capacity, comprehension, trustworthy signals, and a return path move with the accountability."
aliases:
  - judgment placement
  - relocated judgment
  - nominal oversight
tags:
  - human-factors
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-23
maturity: emerging
---

# Judgment Relocation: Where Human Decisions Land in an Agent Factory

> Judgment relocation is real only when the capacity to exercise a decision moves with accountability for it; otherwise the owner signs work they cannot judge.

Judgment relocation is the claim that automating code production moves human decisions to a new position in the pipeline instead of deleting them. It holds under four conditions: attention budget to exercise the decision, comprehension of the artifact, verification signals worth trusting, and a route back into the pipeline. Miss one and the position survives on the org chart while the judgment it was meant to hold has quietly gone.

## Which decisions relocate

Addy Osmani names five that keep a human owner in a software factory: "Someone still chooses the problem. Someone still chooses the architecture. Someone still sets the quality bar. Someone decides which verification signals deserve trust. Someone decides when the evidence is sufficient to ship" ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)). The first three are the upstream move that the [software factory model](../workflows/software-factory-model.md) already describes. The last two differ in kind, because they are judgments about the gate instead of judgments made at it.

The destination is wider than a final approval. Osmani reports that in a good factory "the human isn't limited to just reviewing and approving the final diff at the very end," listing four live positions: shaping the work early, steering it during implementation, carrying it through a handoff, and stopping it before production ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)). A factory offering only the last of those has relocated less judgment than it claims.

## The four conditions

| Condition | What fails without it | Test |
|---|---|---|
| Capacity | The owner approves at the rate work arrives | Does one person's attention cover the queue at current agent count? |
| Comprehension | Approval becomes signature | Could the owner explain the change a week later? |
| Trustworthy signals | The gate reports green on work that is wrong | Has anyone checked the checks against a known-bad change? |
| Return path | A stopped run has nowhere to resume from | When the factory asks a question, where does the answer go? |

Osmani hit the fourth directly. His sample factory correctly halted an issue and labeled it for more information, and he "didn't know where to put my answer." A manual run finishes when the human knows what to do next, not when the machine stops ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)).

## Why it works

Human judgment does not scale with compute, so its value concentrates wherever machine signals are weakest. Osmani states the prescription directly: "We should remove people from the parts of the loop where machines can produce stronger, faster, more deterministic signals," and "concentrate people around the places where context, taste, risk, and long-term ownership matter most" ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)). Baum and Laux supply the causal precision behind that prescription. A human contribution changes an output only when it is constitutive, meaning "a necessary ingredient without which the process cannot proceed," or when it is a corrective position someone actually exercises, where "the human is not a 'gate' but a 'switch': present, capable of redirecting the process, but not necessary for it to run" ([Baum and Laux, arXiv:2603.19213v2](https://arxiv.org/abs/2603.19213v2)). A position nobody has the capacity to exercise is causally inert, which is why the four conditions are the pattern itself.

The mitigation that follows is structural. Layered oversight distributes real-time review of individual decisions, systemic review of aggregate patterns, and compliance review "across different roles and organizational levels," so no single compromised position carries the whole load ([Baum and Laux, arXiv:2603.19213v2](https://arxiv.org/abs/2603.19213v2)).

## When this backfires

- Volume outruns attention. Agent count scales and reviewer bandwidth does not ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)). A human who clicks approve on every decision "but rubberstamps without genuine judgment does not thereby become an overseer" ([Baum and Laux, arXiv:2603.19213v2](https://arxiv.org/abs/2603.19213v2)).
- Accountability moves and control does not. Elish calls the result a moral crumple zone, in which responsibility "may be misattributed to a human actor who had limited control over the behavior of an automated or autonomous system" ([Elish, 2019](https://estsjournal.org/index.php/ests/article/view/260)). Naming an owner for a decision nobody can make manufactures a scapegoat.
- The signals lie. Asked to make a test pass, an agent "can change the unit test to satisfy that condition" ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)). Judgment relocated onto a gate inherits whatever that gate actually measures.
- Comprehension lags approval. Osmani approved a feature in his own repository, returned days later, and "couldn't explain to you how the feature worked" ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)). See [comprehension debt](../patterns/anti-patterns/comprehension-debt.md) for how that gap compounds.
- The scale does not warrant it. "You can get surprisingly far with your stock coding harness" ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)). At one or two sessions you still read everything, and formal placement is ceremony.

## Example

Osmani measured two tasks inside the same sample factory. A quick finder with no rejections took 7 minutes. A favorites feature, carrying two rejections and one human decision in the middle, took 56 ([Osmani, 2026](https://addyo.substack.com/p/human-judgment-doesnt-leave-the-software)). The difference is where judgment sat, which is why he pairs a run-outcome taxonomy with per-stage timing: otherwise a team learns that a run came back flawed without learning what finding out cost them.

## Key Takeaways

- The discriminator is exercise rather than assignment: ask what the named owner would have had to do to catch the last defect that shipped.
- Two of the five relocated decisions concern the gate itself: which verification signals deserve trust, and when evidence is sufficient to ship.
- The available positions include shaping, steering, and handoff, so a factory offering only final-diff approval has relocated less than it claims.
- A position nobody can exercise is causally inert, which makes layered oversight across roles the structural answer to a single overloaded owner.
- Relocating accountability without relocating control produces a moral crumple zone, where blame lands on the operator with the least ability to have prevented the failure.

## Related

- [The Software Factory Model: Industrializing Agent Loops](../workflows/software-factory-model.md) — the light/dark pipeline whose review gate this page assigns an owner to
- [Rigor Relocation: Engineering Discipline with AI Agents](rigor-relocation.md) — the sibling relocation, covering engineering discipline moving into scaffolding rather than judgment moving position
- [The Bottleneck Migration](bottleneck-migration.md) — why the review stage becomes the binding constraint that these conditions have to hold under
- [Author-to-Reviewer Role Inversion in AI-Assisted Teams](author-to-reviewer-role-inversion.md) — the staffing and measurement half of giving the relocated position real capacity
- [Reviewer Habituation in Agent PR Review](../code-review/reviewer-habituation-decay.md) — the measured decay that turns an exercised position into a nominal one over months
