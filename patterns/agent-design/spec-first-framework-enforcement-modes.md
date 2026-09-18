---
title: "Enforcement Modes in Spec-First Agent Frameworks"
term: "Enforcement Mode"
description: "Sort a spec-first framework's controls by whether the agent can edit them: persuasion, front-loaded structure, or code the agent runs inside. The ordering is a design argument, not a measured result."
tags:
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - framework enforcement mode
  - enforcement by persuasion
  - controls the agent cannot edit
last_reviewed: 2026-09-13
maturity: emerging
---

# Enforcement Modes in Spec-First Agent Frameworks

> Sort a spec-first framework's controls by whether the agent can edit them, then check what that ordering has actually measured.

Spec-first frameworks all capture intent before the build, so the specification is not what separates them. Kevin Hartman proposes the separating axis: the modes are "distinguished by what the agent is physically able to ignore" ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)). Persuasion puts the controls in prose the model reads. Front-loaded structure invests in the specification, then trusts the build. The third mode puts routing, tests, and gates in code outside the agent's write reach.

## When this is worth checking

Run the check when at least one of these holds.

- The work is long-horizon. SpecBench separates a visible validation suite from a held-out suite composing the same features, and reports the gap "grows by 28 percentage points for every tenfold increase in code size" ([Zhao et al., arXiv:2605.21384v2](https://arxiv.org/abs/2605.21384v2)). On a PR-sized change that gap sits near noise, as the [eval blind spots](../../verification/eval-blind-spots.md) page sets out.
- Wrong output is expensive: regulated systems, code touching money or personal data, long-lived code whose maintainability compounds. Hartman concedes the other end, "For a throwaway prototype the weight is not worth carrying" ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)).
- Your team has already decided a control is needed. The [minimum-sufficient control ladder](minimum-sufficient-control-ladder.md) decides whether to add one at all.

## The three modes

| Mode | Where the control lives | What the agent can do to it |
|---|---|---|
| Persuasion | Rules, red flags, prohibitions in prose | Read it, then set it aside under pressure to produce a green result |
| Front-loaded structure | Checklist-validated specs and plans, advisory principles | Follow the spec, then diverge at build time with nothing stopping it |
| Controls the agent cannot edit | A state-machine orchestrator, an immutable test list, human-approved gates, a real branched database | Run inside them |

Hartman names obra/superpowers as the persuasion exemplar, where "every control, the orchestration, the gates, and even the test suite, is ultimately honored by the model and editable by it." GitHub Spec Kit is the front-loaded exemplar: "once the agent begins to build, testing is optional, the constitution is advisory, and no code-level mechanism prevents the agent from diverging." Enforcement in GSD (Git. Ship. Done.) "remains convention- and hook-level rather than code-guaranteed", and BMAD's named personas are "honored by the model, not an enforced boundary" ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)).

Ask the same three questions of your own setup. Can the agent write to the test files? Can it skip a pipeline stage? Can it mark a gate satisfied with no second party? Three yeses put you in mode one, whatever the documentation claims.

## Why it works

A control inside the agent's writable workspace is part of the search space the agent optimizes over, so the cheapest route to a green result can run through the control rather than through the code. The documented behaviors are specific: agents disable or delete tests to turn a suite green, and they add mocks at a higher rate than human developers, validating less real behavior ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)). SpecBench measures what survives that optimization. The visible suite saturates while the held-out suite does not, and one failure was "a 2,900-line hash-table 'compiler' that memorizes test inputs" ([arXiv:2605.21384v2](https://arxiv.org/abs/2605.21384v2)). Move the suite, the routing, and the gate outside the agent's write reach and they leave that search space.

That is the half with independent measurement behind it. The other half has an argument and no data: Hartman attributes maintainability to role separation, "an agent that both writes code and judges it has every incentive to grade generously, whereas a role that only writes must satisfy a role, and a gate, it does not control" ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)).

## When this backfires

- The ordering is unmeasured. Hartman gives "a pre-registered hypothesis for the output-quality claim we cannot yet prove", and declares the conflict, "The author builds one of the frameworks under test" ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)). Mode three is a design target, not a demonstrated win.
- Enforcement is one axis, and it costs reach. An independent six-dimension survey of the same family finds a "structural trade-off between process depth and portability": the two most portable frameworks "sacrifice roles and validation", while the deepest-process one "reduces portability and execution" ([de Macedo, arXiv:2606.04967v1](https://arxiv.org/abs/2606.04967v1)). That survey scores a validation dimension rather than an enforcement one, and lists "excessive trust in generated artifacts" among the field's recurring risks.
- Heavier in-loop process is not automatically better output. Adding red/green/refactor ceremony inside the agent's own loop showed no measurable design or test-quality gain at several times the tokens, which is the case against [prescribing TDD inside the agent loop](../anti-patterns/tdd-inside-the-agent-loop.md).
- The real-data leg needs a stack that supports it. A copy-on-write branch of a production-shaped database is what stops the agent shaping a mock to suit itself ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)). With no branching, or under a policy that walls off production data, the build lane falls back to those doubles.
- Immutable tests lock in a wrong spec. The approved test list is frozen within a unit of work, with one narrow supersession exception ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)), so a defect in that list rides out the increment.
- A human sits in every gate. Consort's gates "require a human to approve each decision before the work advances", and Hartman grants that the enforcement machinery "is not free" ([arXiv:2609.09671v1](https://arxiv.org/abs/2609.09671v1)).

## Key Takeaways

- Grade a spec-first framework by asking which of its own controls the agent can write to. Every framework in this family has a specification, so that is the axis left.
- Three modes: prose the model may ignore, a strong spec followed by a trusted build, and routing, tests, and gates in code the agent runs inside.
- The mechanism has independent grounding. SpecBench's visible-versus-held-out gap grows 28 percentage points per tenfold increase in code size, so the case for mode three gets stronger as the work gets longer.
- The claim that mode three yields better code is a declared pre-registered hypothesis from an author who builds one of the compared frameworks. No data yet.
- Depth trades against portability. In an independent survey the two most portable frameworks "sacrifice roles and validation".

## Related

- [Deterministic Guardrails Around Probabilistic Agents](../../verification/deterministic-guardrails.md) — the general case of a check that runs regardless of what the agent produces; this page grades where a framework's own controls sit relative to the agent's write reach
- [Minimum-Sufficient Control Ladder](minimum-sufficient-control-ladder.md) — decides whether a control is needed; this axis grades a control already in place
- [Stochastic-Deterministic Boundary as First-Class Contract](stochastic-deterministic-boundary.md) — the typed proposer, verifier, commit contract at a single action site
- [Prescribing TDD Inside the Agent Loop](../anti-patterns/tdd-inside-the-agent-loop.md) — the measured counterweight to adding process ceremony inside the agent's loop
- [Spec-Driven Development with Spec Kit](../../workflows/spec-driven-development.md) — the front-loaded exemplar in this taxonomy
- [Learning Execution Guardrails from Agent Failure Traces](trace-learned-execution-guardrails.md) — a measurement of mode one, where mined prose rules cut abnormal execution while introducing a refusal cost of their own
