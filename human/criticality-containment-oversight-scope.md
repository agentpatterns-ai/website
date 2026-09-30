---
title: "Criticality and Containment: Scoping Which Agent Code You Read"
term: "Containment-Scoped Oversight"
description: "Criticality sets how much oversight an agent-written component earns; containment decides whether reading its internals is part of that oversight, and only when the outside measures include structure."
aliases:
  - containment-scoped oversight
  - selective human oversight
  - criticality-calibrated oversight
tags:
  - human-factors
  - technique
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-29
maturity: emerging
---

# Criticality and Containment: Scoping Which Agent Code You Read

> Criticality sets how much oversight a component earns; containment decides whether reading its internals is part of that oversight.

Two conditions have to hold before you stop reading the inside of an agent-written component. The boundary has to be enforced, not assumed, and the properties you measure from outside it have to include structure, not behavior alone. Miss the second and functional correctness is all you are watching. A systematic audit of AI-generated software found that correctness does not mitigate the structural decay it measured.

## Criticality and the containment precondition

A EuroPLoP 2026 focus group of 22 industry and academic practitioners settled on criticality as "the axis along which all decisions about AI autonomy were calibrated". "The group reached strong consensus that trust in AI proposals is calibrated by the criticality of the decision or task at hand" ([van Heesch, Zimmermann and Kohls, arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)). One participant "articulated criticality as the combination of uncertainty and cost of change, a framing that was accepted by the group without dissent".

Criticality alone does not tell you what to do with a given component, because it is a property of the decision and the component is code. The second half supplies that. "If a component is well-contained and its properties are observable and measurable from the outside, an architect does not need to understand its internals" ([arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)). The participant behind that finding framed it as responsibility, not convenience: "I don't see as a loss of responsibility the fact that I don't know inside anymore, if it's contained, and I can measure and see what are the properties I have." What the paper draws from it is an attention-allocation rule. The architect's role "shifts towards deciding where to invest attention, based on the criticality of individual components as well as its interface contract/specification."

## Applying the test

Run it per component, in this order.

1. Score criticality as uncertainty combined with cost of change. A component you are confident about and can replace in an afternoon scores low whatever it does.
2. Decide whether the boundary is enforced. Shared tables, shared config, and a leaky error contract all produce a component that looks contained in the module tree and is not. This is a judgment about internals, so it is the one reading you cannot skip.
3. List the properties you can measure from outside, and check that the list covers structure as well as behavior. Complexity, coupling, and static analysis warnings belong on it.
4. Spend the internal reading you have left on the components that failed step 2 or step 3, ordered by step 1.

The measurement machinery is the machinery you already run. The focus group recorded consensus that existing validation mechanisms remain the quality backbone. One participant put it this way: "The SonarQube harness – nothing changed between when humans coded and made mistakes and now when an AI does. It's the same level of distrust" ([arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)). CI/CD pipelines, tests from unit to end-to-end, and tool-supported code quality analysis "apply equally to AI-generated code and to human-written code".

## Why it works

Reading internals is an obligation indexed to generated volume, which is the quantity agents raise fastest. Volume is also what the damage tracks. Zhu, Tsantalis and Rigby ran a "multi-scale analysis, spanning single-file algorithmic tasks and complex, agent generated systems", and report a "Volume-Quality Inverse Law, where code volume is a near perfect predictor of structural degradation" ([arXiv:2605.02741v1](https://arxiv.org/abs/2605.02741v1)). An obligation that grows with a quantity a fixed number of reviewers cannot absorb has to be converted into a bounded one.

Containment does that conversion. A component whose properties are observable from outside can be checked at its boundary instead of line by line, which turns review cost from a function of generated lines into a function of boundary count. Criticality then rations the bounded budget across those boundaries. Architecture governance already runs on the same principle. The paper describes architectural fitness functions and conformance checking tools as approaches that "share a common principle: making architectural intent explicit, machine-readable, and automatically enforceable" ([arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)). An outside-measurable component boundary is that principle applied to what you read, not to what ships. The conversion runs entirely through the measured property set, which is why step 3 decides whether the rest of the test means anything.

## When this backfires

- The outside measures are behavioral only. Zhu, Tsantalis and Rigby state it flatly: "Crucially, we demonstrate that neither functional correctness nor detailed prompting mitigates this decay" ([arXiv:2605.02741v1](https://arxiv.org/abs/2605.02741v1)). A suite that stays green tells you nothing about whether the decay is happening.
- Structure degrades and nobody watches the trend. He and colleagues ran a difference-in-differences design against a matched control group of similar projects and found "the adoption of Cursor leads to a statistically significant, large, but transient increase in project-level development velocity, along with a substantial and persistent increase in static analysis warnings and code complexity" ([arXiv:2511.04427v3](https://arxiv.org/abs/2511.04427v3)). Their panel estimation names those two increases "major factors driving long-term velocity slowdown", so the cost arrives late and as lost speed.
- The boundary was never real. The focus group supplies no test for whether a component is well-contained; it treats that as decidable. Getting it wrong redistributes attention away from the code that needed it most.
- The contract was the agent's idea. Containment checks a component against its specification and says nothing about whether a better decomposition existed. One participant named the cost: "The solution space is actually much bigger, and I'm blind to it" ([arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)).
- One accountable person, one large system. The group questioned whether the arrangement survives scale: "a single person on a huge system will not be accepted" ([arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)). Rationing attention does not help when the budget was already short.
- Your team is small enough to read everything. The focus group's own participants worked in teams that were "predominantly small: fewer than 5 (9) or 5–15 (7)" ([arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)), where formal scoping is ceremony.

Mind the shape of the evidence too. The focus group is "an experience report, not a formal study", and its authors ask that the findings "be interpreted as perspectives from an expert community rather than as representative of the profession at large" ([arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)). The two sources qualifying it are empirical; the technique is not.

## What the failure state is called

The focus group names the accumulated cost, and defines it against skill loss and does not treat it as a synonym. "Where skill degradation concerns the loss of a previously held ability, cognitive debt describes the conscious or gradual acceptance of not fully understanding parts of the system one is responsible for" ([arXiv:2609.30334v1](https://arxiv.org/abs/2609.30334v1)). Every component you decide not to read adds to that balance. The two conditions are what keep it serviceable.

## Key Takeaways

- Score criticality as uncertainty combined with cost of change, which is the definition the focus group accepted without dissent. Do not score it as severity or as lines changed.
- The boundary check is the one piece of internal reading you cannot delegate, because deciding a component is contained requires knowing how it is coupled.
- Put static analysis warnings and complexity on the outside-measure list before scoping anything out, and watch their trend rather than their level.
- Re-run the test when a component's criticality changes, because a boundary scoped out at low criticality does not re-enter review on its own.
- Weigh it as one experience report from one architecture-aware conference community against two empirical studies that qualify it, and prefer the narrower reading where they disagree.

## Related

- [Comprehension Debt](../patterns/anti-patterns/comprehension-debt.md) — the gap this technique decides where to tolerate
- [Judgment Relocation: Where Human Decisions Land in an Agent Factory](judgment-relocation.md) — comprehension as one of four conditions for an owner who can actually exercise a decision
- [Architectural Foundation First](../workflows/architectural-foundation-first.md) — building by hand the boundaries this test later depends on being real
- [Reviewer Habituation in Agent PR Review](../code-review/reviewer-habituation-decay.md) — the measured decay behind approval given without evaluation
- [Tiered Code Review](../code-review/tiered-code-review.md) — the same risk-routing idea applied to review depth per change
