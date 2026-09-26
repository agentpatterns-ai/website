---
title: "Agent-Operable Interface Design (Affora)"
term: "Agent-Operable Interface Design"
description: "Make a screen's controls, choices, state, and outcomes recoverable from its machine-readable structure so a computer-use agent can operate it, and learn which deficits are worth fixing."
aliases:
  - shared human-agent interface
  - agent-friendly interface design
  - agent-readable interface structure
tags:
  - agent-design
  - human-factors
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-19
maturity: emerging
---

# Agent-Operable Interface Design (Affora)

> Agent success on an interface tracks whether its controls, choices, state, and outcomes stay recoverable from the machine-readable structure the agent reads.

Rework a screen for a computer-use agent only where a specific deficit already exists. Across four independently authored applications the gain sat in one task class: targets behind a label that does not predict its contents. There, shadcn-admin moved from 16/71 (23%) to 46/72 (64%) and Ant Design Pro from 12/18 (67%) to 18/18 (100%). Already-visible targets barely moved, 93% to 90% for shadcn-admin and 100% to 100% for Ant Design Pro, and two of the four applications barely moved: 79% to 81%, and 72% to 71% ([Gao, *Affora*, §6.3](https://arxiv.org/abs/2609.19125v1)).

## Which deficits are worth fixing

Three shapes account for most of the loss, and each is a property of what the page declares rather than how it looks ([§4.1](https://arxiv.org/abs/2609.19125v1)):

- A styled element that reads as a control to a person but is not represented as a named, operable control.
- A set of choices that exists only after an interaction, such as a hover, an expansion, or an opened menu.
- An outcome delivered as transient feedback instead of persistent state.

Accessibility semantics overlap with these shapes without covering them. Adding ARIA and structured data to the primary comparison set moved completion from 46/60 to 45/60 ([§3, §6.2](https://arxiv.org/abs/2609.19125v1)).

A controlled repair sequence separates the two halves. Correcting semantics raised success from 43% to 67%; exposing the relevant choices and state raised it to 90% ([§4.1](https://arxiv.org/abs/2609.19125v1)). Valid markup is only the floor.

Sixty interactive components were built nine ways with task content held constant. Plain semantic HTML reached 91%; the eight libraries ran from 86.7% down to 68.3% on the mid-tier model ([§4.1](https://arxiv.org/abs/2609.19125v1)).

## What can vary freely

Visual identity is close to free once the declared structure holds. Across sixteen themes and six layout archetypes, DOM-channel completion stayed at 99.5%, and the marked-pixel channel reached 92% against 94% for native controls ([§4.2](https://arxiv.org/abs/2609.19125v1)). Stronger visual cues did not help either. A sweep from convention-contradicting to convention-reinforcing treatments ranged 98.7% to 99.8% with no trend.

That result is bounded. The marked-pixel reader receives enumerated targets, so the author states the result should not be generalized to agents that locate actions from raw pixels alone ([§4.2](https://arxiv.org/abs/2609.19125v1)).

## The human canon does not carry over intact

Gao re-tested seven established interaction-design principles with an agent as the reader. Added confirmation raised interaction cost. Splitting a form into steps added cost with no demonstrated completion benefit. Explaining disabled states showed no consistent gain. Explicit recovery information did help. The reason is the reader's memory model. An agent may re-observe the interface at each step and lose task state across context boundaries. A step bought to reassure a person is then charged to the agent ([§4.3](https://arxiv.org/abs/2609.19125v1)).

## Why it works

An agent never reads the rendered screen. It acts on a projection: a serialized list of interactive elements with roles and names, an accessibility tree, a marked screenshot, or pixels. Those projections expose different portions of the interface and different action spaces ([§3](https://arxiv.org/abs/2609.19125v1)). The author, drawing on Norman, puts the gap directly: "visual appearance can provide a strong signifier to a person while providing little or no corresponding signifier in the representation available to an agent" ([§3](https://arxiv.org/abs/2609.19125v1)). So success turns on whether controls, names, state, choices, and outcomes survive into the projection, which is independent of styling. Both halves are measured. Hold the declared layer fixed and sixteen themes cost nothing; repair the declared layer and success moves from 43% to 90% ([§4.1, §4.2](https://arxiv.org/abs/2609.19125v1)).

## When this backfires

- The deficit is absent. Rewriting already-sound Magento components left completion at 7/40 either way ([§6.3](https://arxiv.org/abs/2609.19125v1)).
- The failing idiom sits outside your rule set. See the example below.
- A cheaper intervention already clears the task set. An `agent.md` instruction file, with no interface work, matched the full rewrite at 60/60 on the primary set. It reached 32/33 on the harder set ([§6.2](https://arxiv.org/abs/2609.19125v1)).
- The right answer is a tool layer. A WebMCP-style arm reached 55/55 on its applicable action set ([§6.2](https://arxiv.org/abs/2609.19125v1)). One position paper argues the human-interface mismatch is deep enough to warrant a purpose-built agent interface instead ([Lù and others, arXiv:2506.10953v1](https://arxiv.org/abs/2506.10953v1)).
- Your surface is not a web DOM. Windows UI Automation, AT-SPI, and macOS accessibility are named as possible carriers, and transfer is not evaluated ([§7.4](https://arxiv.org/abs/2609.19125v1)).
- You want a human-side benefit. The work evaluates machine readers only, and the supervisability argument is a design implication with no human study ([§7.1, §7.5](https://arxiv.org/abs/2609.19125v1)).

## Example

WebShop shows the coverage limit. Its native interface uses a hidden-radio idiom for product options. Applying the published rule set changed nothing there: 9/117 (8%) full-reward completion before, and 9/117 after. Writing one further rule covering that specific idiom raised it to 80/117 (68%) ([§6.3](https://arxiv.org/abs/2609.19125v1)).

The author records this as a response to a newly encountered pattern, not as evidence that the rules generalized. That is the shape of the work: run agents against your own stack, read the failures, write the rule. A conformance check tells you a required property is present, and the author calls that a conformance floor rather than a guarantee of task success ([§5.3](https://arxiv.org/abs/2609.19125v1)).

## Key Takeaways

- Audit for the deficit before rewriting anything. Targets behind labels that do not predict their contents are where the measured gain sits, and already-visible targets do not move.
- Budget for two passes. Correcting semantics carried the repair sequence 24 points and exposing choices and state carried the next 23, so stopping at semantics buys about half.
- Restyling costs nothing and buys nothing while the declared structure holds, so a visual refresh is not an agent-reliability project.
- Try a project instruction file first. It matched a full interface rewrite on one comparison set for a fraction of the work.
- Re-check confirmation steps and multi-step forms. Confirmation raised interaction cost in the tested tasks; splitting a form into steps added cost with no demonstrated completion benefit.
- Rule coverage is discovered per stack. Budget for finding your own failing idioms rather than assuming a published rule set reaches them.

## Related

- [Agent-First Software Design](agent-first-software-design.md) — the opposing position, where machine-readable APIs replace the visual interface rather than sharing it
- [Browser as Agent Action Space](browser-as-agent-action-space.md) — the same problem from the agent's side, covering how a harness drives a page it does not own
- [WebMCP: Browser-Hosted Tool Contracts for In-Page AI Agents](../../standards/webmcp.md) — the separate tool layer measured against a shared interface here
- [Designing for Agent Consumers (Agent Experience)](../../tool-engineering/designing-for-agent-consumers.md) — the equivalent discipline for an SDK, CLI, or API rather than a screen
- [AX Evals: Measure the Agent-Facing Surface, Not the Model](../../verification/ax-evals-agent-facing-surface.md) — how to run the with-and-without contrast that tells you whether an interface change paid
