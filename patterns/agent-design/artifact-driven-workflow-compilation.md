---
title: "Artifact-Driven Workflow Compilation for Agent Execution"
term: "Artifact-Driven Workflow"
description: "Rewrite a prose procedure so every step declares the artifacts it reads and writes — worth the cost when the procedure is fixed and you run it many times."
tags:
  - agent-design
  - workflows
  - tool-agnostic
  - arxiv
aliases:
  - artifact-driven workflow
  - declared-artifact workflow steps
  - workflow compilation for agents
last_reviewed: 2026-08-24
maturity: emerging
---

# Artifact-Driven Workflow Compilation for Agent Execution

> A compiled workflow makes every step declare the artifacts it reads and writes, so the executor looks up its inputs instead of inferring them.

An artifact-driven workflow names, for each step, the artifacts it reads, the artifacts it writes, and the constraints those outputs must satisfy. Xu and colleagues compile prose procedures into that shape with a tool called Artic and report that "it improves task resolve rate by 28 percentage points over the original text workflow" across 488 problem instances from 11 real-world domain workflows ([Xu et al. 2026 — arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)). The gain is conditional, and the conditions matter more than the number.

## When compilation pays back

Compile a procedure only when all four hold. Miss one and you have bought a second representation to maintain for nothing.

- The procedure is fixed and repeatable. Compilation needs steps that exist before the run starts. Exploratory debugging and design work have no procedure to compile.
- Each step's input is a named earlier output. That ambiguity is what the representation removes; if the dependencies were already obvious, the executor was never guessing.
- Branch conditions are checkable predicates over that state, not judgment calls. "If the customer is high-risk" compiles; "if the response seems evasive" does not.
- You run it often enough that repeat-run consistency is the metric you care about. That is where the effect is largest. On the Medical domain in χ-Bench, "At k=10, the compiled workflow has about 72% passing cases, while the text workflow has only 16%" ([arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)). Corpus-wide the paper reports a smaller figure, 56 percentage points more consistent in repeated-execution setups.

The underlying problem is measured independently too. SOP-Bench draws 2,000-plus tasks from expert-authored standard operating procedures across 12 business domains and finds no model-agent combination that dominates ([Nandi et al. 2026 — arXiv:2506.08119v2](https://arxiv.org/abs/2506.08119v2)).

## What a compiled step declares

Artic's target language has four statement forms: an agent step that follows a natural-language instruction, sequencing, an explicit `if p then S1 else S2` branch, and a `while p do S` loop. An artifact state maps identifiers to data plus constraints, and every control transfer is a predicate over that state ([arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)).

A language model does the translation, so checking it belongs to the pattern. Artic runs static well-formedness checks, decomposes faithfulness into local obligations matching the program structure, and dry-runs source and compiled workflows on enumerated scenarios to diff their trajectories. Dropping that layer is expensive: "in our ablation study, a compiler variant without this correctness validation performs 16 percentage points worse than the full system" ([arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)). A [critic agent reviewing the plan](critic-agent-plan-review.md) is the lighter version of the same move.

## Why it works

Declaring reads and writes removes an inference step the executor was silently performing. In the paper's healthcare case the agent "is expected to use the utilization evidence to make the complex-care decision, but because this dependency is not explicit, the executor agent may not consistently identify the correct information" ([arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)). Naming the artifact turns that guess into a lookup.

Two effects compound it. The compiler measures how much state and control logic each step carries and splits the overloaded ones, because "if a natural-language step contains too much context or too much control structure, an agent may struggle to follow it faithfully"; one decision step carrying a risk score plus two eligibility rules becomes three transformations ([arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)). Explicit predicates pin the branch semantics the prose only implied. The token figures show the same mechanism from the other side. Measured against an agent working on the text workflow, the compiled version cuts average per-agent input tokens by 63% and output tokens by 50%, at a compilation cost the paper scopes carefully: "For the studied SOP-Bench domains, the median first-package compilation time with GLM-5 is under 5 minutes, and the average compilation cost is under $3" ([arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)). Three compiler models were evaluated (GPT-5.4, Sonnet-4.6, GLM-5); only GLM-5's cost is reported.

## When this backfires

- The hard part is domain judgment. The paper concedes it: "Cases that depend more on model judgment than workflow enforcement may remain unresolved" ([arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)). Its know-your-business example needs the experience to tell a genuine typo from fabricated data, and no artifact declaration supplies that.
- The procedure changes often. The paper offers no account of recompilation or of who reviews the compiled form. Your domain expert edits the prose; the compiled version is what executes, so drift between them is the standing risk.
- You run the workflow once. A single run collects the resolve-rate gain and none of the repeat-run consistency gain, against the full compile cost.
- The rules are simple enough to code outright. "On domains such as patient intake and referral abuse, the code baseline can slightly outperform our workflow while our workflow remains near-perfect" ([arXiv:2608.21341v1](https://arxiv.org/abs/2608.21341v1)) — on patient intake, 100% for plain Python against the compiled workflow's 100/97/100 across three executors. That is a tie, and where the rules are that simple the compiler's extra cost buys nothing. Code falls behind on complex domains because such implementations "often use stable heuristics such as keyword matching".
- The task needs flexibility more than predictability. Anthropic draws the line directly: "When more complexity is warranted, workflows offer predictability and consistency for well-defined tasks, whereas agents are the better option when flexibility and model-driven decision-making are needed at scale" ([Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)).
- The compiled steps call tools you do not have. Earlier automatic generators "mainly produce LLM-centric workflows, where real tool executions are abstracted and simulated by LLM nodes, limiting the usability and stability of generated workflows" ([Hao et al. 2026 — arXiv:2608.10039v1](https://arxiv.org/abs/2608.10039v1)). A compiled procedure can read as rigorous while its tool layer stays imaginary.

## Key Takeaways

- Compile a procedure only when it is fixed, its dependencies are named outputs, its branches are checkable predicates, and you run it many times.
- The measured gain concentrates in consistency across repeats and across models, not in a single run.
- Validating the translation is load-bearing. A compiler variant without that check scores 16 percentage points below the full system, so skipping it buys the cost and little of the benefit.
- Structure does not add domain expertise. Where a step needs judgment, the compiled form fails the same way the prose did.
- Compiling leaves you two representations of one procedure. Decide who re-compiles before you adopt it.

## Related

- [Structured Task-State Ledger for Tool-Calling Agents (LedgerAgent)](ledger-agent-structured-task-state.md) — Keeps typed state outside the prompt at runtime; this pattern makes the same state explicit in the procedure itself.
- [Bounded Agent Steps Inside a Deterministic Workflow](bounded-agent-step.md) — Fences one agent stage with a typed input and output; artifact declaration is what makes those types available to declare.
- [Runbooks as Agent Instructions: Agent-Followable Ops](../../workflows/runbooks-as-agent-instructions.md) — The hand-written version of the same rewrite, with an audit instead of a compiler.
- [DSLs as a Constraining Harness for LLM Code Generation](dsl-constraining-harness.md) — Narrows the space of valid outputs with a grammar; this narrows it with declared inputs.
- [Deterministic Guardrails Around Probabilistic Agents](../../verification/deterministic-guardrails.md) — The static and dry-run checks over a compiled workflow are guardrails of exactly this kind.
