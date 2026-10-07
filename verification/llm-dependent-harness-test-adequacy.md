---
title: "Test Adequacy of LLM-Dependent Harness Code"
term: "LLM-Dependent Harness"
description: "When the harness is more than a thin provider wrapper, scope a coverage and mutation report to the harness statements that depend on model output, and build reusable contract-faithful fixtures before writing the cases."
tags:
  - testing-verification
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - LLM-dependent harness coverage
  - agent harness test adequacy
  - contract-faithful test setups
last_reviewed: 2026-10-06
maturity: emerging
---

# Test Adequacy of LLM-Dependent Harness Code

> LLM-dependent harness code concentrates an agent's decision logic, and averaged under half line and branch coverage across ten studied agent codebases.

Measure coverage separately over the harness code that depends on model output, when that slice is more than a thin wrapper over a provider SDK. A study of 10 open-source agentic systems found that slice averaged 44.27% line and 41.18% branch coverage under the projects' own test suites, with an average mutation score of 33.60% ([Xiong et al., arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)). The authors name the slice LLM-dependent harness code: harness statements carrying a data or control dependency on the output of an LLM invocation.

## Where a separate coverage target pays

LDH is not uniformly the worst-covered part of an agent codebase, so the separate target needs a reason. "LDH line coverage is lower than project-level line coverage in eight of the ten agents", but average LDH branch coverage of 41.18% ran above average project branch coverage of 36.84% ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)). Four conditions decide whether reporting it earns the effort.

- The harness is more than a wrapper over a provider SDK. SWE-agent's LDH slice was 8.78% of executable lines and 12.63% of branches ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)), small enough that project coverage already describes it.
- Model output crosses several components before the decision that consumes it. The paper's account: "Model outputs often flow through multiple harness components before reaching deeper LDH logic, where each component may expect specific input structures, runtime states, and interaction sequences" ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)).
- You have no reusable builders for mocked responses and accumulated state yet. The study's inspection found that "Kimi Code provides systematic test support for satisfying these requirements", and Kimi Code reached 92.83% LDH line coverage against 71.98% project line coverage ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)).
- You score the slice by mutation. Average LDH mutation score across the ten systems was 33.60%, from 3.58% on RD-Agent to 70.94% on Kimi Code ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)).

## What the tests reach and miss

Two annotators hand-coded 700 LDH branch predicates sampled from the ten systems, reaching Cohen's kappa of 0.96 before a third reviewer resolved disagreements. Of those predicates, "only 25.57% are fully covered, 24.57% are partially covered, and 49.86% remain entirely uncovered" ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)). The gap is not spread evenly across what the predicates do.

| Predicate group | Fully covered |
|---|---|
| Tool action handling | 38.18% (63/165) |
| Observation feedback handling | 18.39% (16/87) |
| Error recovery handling | 17.65% (9/51) |
| Agent orchestration control | 14.29% (14/98) |

Orchestration control also had the lowest coverage of any group, with 63.27% (62/98) of its predicates uncovered. The same split appears on the other two coding dimensions. Policy guards were 50.00% (15/30) fully covered against 22.12% of presence-or-shape checks, and predicates over tool action payloads were 43.42% fully covered against 17.71% for predicates over generated content.

The covered half is the half with a schema. Tool actions and policy interfaces give a test an explicit shape to build and a bounded set of values to vary. Orchestration, feedback handling, and free-text content do not.

## Why it works

Model output lands in decision logic, and the decisions outnumber the lines that carry them. LDH averaged 22.35% of executable lines but 31.71% of branches, and "across all studied agents, the LDH branch share is 1.10-1.75 times its line share" ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)). In the 700-predicate sample, 47.14% of those decisions were presence or shape checks over model-derived values.

One mocked response drives one path through that logic. The other outcomes need a differently shaped model-derived input while the rest of the execution context stays valid, which an end-to-end run cannot supply because it gets whatever the model emits. Mocking alone does not close this. All ten studied systems mock the LLM, and the paper's reading is that "simply using mocks does not necessarily make deeper harness behavior easy to reach".

What separated the best-covered system from the worst was reusable test infrastructure. Kimi Code carried helpers that build mocked responses with the fields each scenario needs, fake LLMs for valid interaction sequences, and local HTTP and SSE servers for provider communication. OpenClaw's mocks and fixtures were "organized in a relatively ad hoc manner". The study's own summary is that high LDH adequacy "calls for contract-faithful test setups that satisfy the expected data structures, runtime states, and interaction protocols across harness components".

The bug-detection result follows the same line. Across 250 historical harness bugs from the ten systems, with every technique handed the buggy location as its generation target, a generator carrying explicit contract guidance revealed 43 of them (17.20%) against 2 (0.80%) for the strongest general-purpose baseline ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)). Removing the contract support dropped it to 15 (6.00%).

## When this backfires

- You read the coverage percentage as the goal. Coverage's "effect, and specifically the advisable dose, are disputed in both the research and engineering communities", and the existing evidence base is correlational ([Schulte et al., arXiv:2602.03585v1](https://arxiv.org/abs/2602.03585v1)). The discriminating instrument in the harness study was the mutation score, as it is in [mutation testing as a quality gate](mutation-testing-quality-gate.md).
- Your fixtures diverge from the production contract. Seven of the 50 differential outcomes the contract-aware generator retained were false positives, rising to 5 of 20 without contract support. The cases came from "fixtures that violated production-side agent-harness contracts or assertions that assumed unsupported behavior" ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)). Each one costs triage time and names no bug.
- You have no way to compute the slice. Off-the-shelf analysis does not identify it: existing frameworks "do not directly capture the LLM-specific semantics required by LDH extraction", so the authors built an interprocedural tool that treats LLM invocations as taint sources and propagates to a fixed point ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)). Without that, the number you report is the project's.
- You generalize past the sample. The authors scope it themselves: "The generality of our findings can be scoped to our studied agents" ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)). Those agents were open-source, written in Python or TypeScript, and carried at least 10,000 GitHub stars with a reproducible test suite.

## Example

A generated test exposed a confirmed sensitive-data leak in Browser Use. The agent records model-selected tool calls as typed actions in its execution history. On the save path, `redact_dict` hands list-valued fields to `redact_list`, which masks strings and recurses into dictionaries but returns nested lists unchanged, so a secret held in a `list[list[str]]` action parameter survived into the saved history file ([arXiv:2610.04921v1](https://arxiv.org/abs/2610.04921v1)).

Reaching that line took a complete valid chain. The test had to build a schema-valid action, wrap it in a model-output object, place that inside a history object carrying browser state, supply the sensitive-data mapping, and then read the written file. Neither the strongest Python baseline nor the contract-agnostic variant revealed the bug.

## Key Takeaways

- When that slice is more than a thin wrapper, report coverage over the statements with a data or control dependency on model output, not only over the project; in the ten-system sample those averaged 44.27% line coverage against 49.48% project-wide
- Score that slice by mutation rather than by percentage covered; the sample's best-covered system reached 92.83% LDH line coverage and still killed only 70.94% of its LDH mutants
- Aim the fixture budget at orchestration control, error recovery, and generated-content predicates; tool-call payloads and policy guards are already the covered half
- Build reusable response, state, and transport fakes before writing cases, because every studied system already mocked the model and that did not reach the deep logic
- Check a new failing harness test against the production contract before filing it; a quarter of the contract-agnostic generator's differential outcomes were false positives

## Related

- [Mutation Testing as a Quality Gate for AI-Generated Test Suites](mutation-testing-quality-gate.md) — the instrument that separates a covered harness line from a tested one
- [Structural Coverage Criteria for Agent Workflows](structural-coverage-agent-workflows.md) — the behavioral counterpart, deriving obligations from a declared coordination graph instead of from source statements
- [LLM API Fault Injection at the HTTP Layer (AgentChaos)](llm-api-fault-injection-http-layer.md) — varying provider responses at the transport, where this page varies them at the fixture
- [Spec-Driven Test Generation: Contract Coverage Is the Lever](spec-driven-test-generation-contract-coverage.md) — the same contract-first move applied to general software rather than harness code
- [Cut-Point Replay: Test a Fix Against a Recorded Agent Run](cut-point-replay-agent-regression-tests.md) — the alternative when fixture fidelity is the hard part, since a recorded run satisfies the contract by construction
