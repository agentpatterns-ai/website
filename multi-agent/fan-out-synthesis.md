---
title: "Fan-Out Synthesis Pattern for AI Agent Development"
description: "Spawn N agents in parallel on the same task, then merge the strongest elements from each attempt into a single output using a dedicated synthesis agent."
aliases:
  - Fan-Out Pattern
  - Parallel Dispatch
  - Scatter-Gather
tags:
  - agent-design
  - cost-performance
  - workflows
  - multi-agent
---

# Fan-Out Synthesis Pattern

> Spawn N independent agents to solve the same problem in parallel, then use a synthesis agent to merge the strongest elements from each attempt into a single output.

!!! note "Also known as"
    Fan-Out Pattern, Parallel Dispatch, Scatter-Gather. The fan-out-then-synthesize variant adds a dedicated merge step after parallel execution. For the broader pattern survey, see [Agent Composition Patterns](../agent-design/agent-composition-patterns.md). For the delegation variant, see [Orchestrator-Worker](orchestrator-worker.md). For implementation guidance, see [Sub-Agents Fan-Out](sub-agents-fan-out.md).

## Structure

The pattern has three stages:

1. **Fan-out** — spawn N agents with identical instructions but independent contexts; each produces a distinct solution
2. **Synthesis** — a synthesis agent critiques all N outputs, scores them against defined criteria, and assembles a merged solution from the strongest parts
3. **Validation** — pass the merged output through a committee review loop before accepting

```mermaid
graph TD
    A[Task] --> B[Agent 1]
    A --> C[Agent 2]
    A --> D[Agent N]
    B & C & D --> E[Synthesis Agent]
    E --> F[Merged Output]
    F --> G[Committee Review]
    G -->|PASS| H[Accept]
    G -->|FAIL| F
```

## Why Parallel Diversity Helps

A single agent makes one set of decisions and commits to them. Parallel agents, given identical instructions but independent contexts, make different decisions — they explore different trade-offs, surface different edge cases, and identify different risks. The synthesis pass converts this diversity into value: rather than picking a winner, it extracts the strongest element from each attempt and assembles a composite solution no single agent would have reached alone.

This is distinct from a simple majority vote. A vote picks the most popular answer. Synthesis identifies complementary strengths across outputs and combines them deliberately.

## Why It Works

The mechanism is ensemble variance reduction applied to generative outputs. A single LLM call samples from the model's output distribution once; N independent calls sample N times with different starting conditions, producing a broader coverage of the solution space. The synthesis agent then selects the highest-quality elements from each sample — exploiting variance rather than averaging it away. This is analogous to ensemble methods in classical ML, where combining diverse weak learners outperforms any individual learner ([Dietterich, 2000 — Ensemble Methods in Machine Learning](https://link.springer.com/chapter/10.1007/3-540-45014-9_1)). The key condition is genuine output diversity: if agents converge on the same approach, there is nothing for synthesis to exploit.

## Diversity Mechanisms

Identical instructions do not guarantee identical outputs. To maximize output spread:

- Vary **model temperature** between agent instances
- Vary **seed context** — provide each agent a different starting reference or example
- Vary **system prompt emphasis** — one agent optimizes for brevity, another for robustness, a third for edge-case coverage

The goal is enough diversity for the synthesis agent to find genuinely different approaches, not just surface-level rephrasing.

## Synthesis Agent Responsibilities

The synthesis agent receives all N outputs and must:

- Score each on the defined evaluation criteria
- Identify which elements from each output are strongest
- Produce a merged output that draws on those elements explicitly
- Document which source output contributed each major decision (for auditability)

The synthesis step is deliberate assembly, not summarization. The synthesizer should justify its choices.

## Cost Trade-Off

N parallel attempts costs N× compute compared to a single attempt. This is worthwhile when:

- The task is high-stakes and errors are expensive to fix downstream
- Diversity of approach is genuinely valuable (design decisions, architecture choices, creative output)
- Reducing total iteration rounds justifies the upfront parallel cost

For routine, well-defined tasks with strong baseline performance, a single attempt is usually sufficient. [Anthropic's Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) describes voting — running the same task multiple times to get diverse outputs — and the orchestrator-workers pattern as core parallelization strategies. Research on best-of-N sampling confirms diminishing returns at high N — compute cost grows linearly while quality gains compress, so the pattern is most efficient in the N=3–5 range for most tasks ([CarBoN: Calibrated Best-of-N Sampling](https://arxiv.org/abs/2510.15674)).

## When This Backfires

Fan-out synthesis adds cost and coordination overhead that makes it counterproductive in several conditions:

- **Output homogeneity**: When the task domain constrains outputs to a narrow solution space, N runs produce near-identical results. Diversity mechanisms (temperature, seed variation) only amplify differences when the space is large; for constrained tasks the fan-out produces noise rather than signal.
- **Weak synthesis agent**: If the synthesizer cannot reliably identify which elements are strongest — due to underdefined evaluation criteria or an insufficiently capable model — it will produce a merged output worse than the best individual attempt. The synthesis step is the highest-risk component.
- **Diminishing returns at high N**: Best-of-N sampling research confirms that quality gains compress as N increases while compute cost grows linearly ([CarBoN, 2025](https://arxiv.org/abs/2510.15674)). Running N=10 rarely justifies 10× cost over N=3.
- **Cascading context loss**: Passing all N outputs to a single synthesis agent can exceed context limits and degrade synthesis quality. For large outputs, aggregation must be staged or summarized first.

## When This Backfires

Three conditions reliably degrade fan-out synthesis below single-agent performance:

1. **Conformity bias collapses diversity** — agents presented with the same problem and similar prompts converge on the same confident-sounding approach rather than genuinely independent solutions. Research on multi-agent LLM failures identifies this as the dominant failure mode in parallel synthesis architectures: agents reward linguistic confidence over factual accuracy, producing a single high-confidence answer that can be wrong ([Cemri et al., 2025 — Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657)).
2. **Weak synthesis agent becomes a bottleneck** — the synthesis step requires the synthesizer to accurately judge quality across N outputs. If the synthesis model is weaker than the worker models, or lacks the domain knowledge to distinguish strong from weak contributions, the merge step introduces errors rather than removing them.
3. **Cascading errors in downstream pipelines** — when the merged output feeds a subsequent agent that treats it as authoritative, any synthesis error compounds rather than self-corrects. A receiving agent builds on a flawed premise, and the error amplifies at each stage.

## Integration with Committee Review

After synthesis, the merged output goes through committee review before acceptance. This catches synthesis errors — cases where the synthesizer incorrectly combined elements that conflict or misidentified the strongest approach. The two patterns are complementary: fan-out generates solution diversity, committee review validates the merged result.

## Key Takeaways

- Fan-out generates solution diversity by running N agents independently on the same task
- Synthesis is deliberate assembly of the strongest parts, not a vote or a summary
- Maximize diversity by varying temperature, seed context, or system prompt emphasis between agents
- N× compute cost is justified for high-stakes or creative tasks; not warranted for routine well-defined tasks
- Chain into committee review to validate the merged output before accepting

## Example

A team needs a high-stakes API design for a payment service. Rather than iterating on a single draft, they fan out to three agents:

- **Agent 1** — temperature 0.3, instructed to optimise for simplicity and minimal surface area
- **Agent 2** — temperature 0.7, instructed to optimise for extensibility and future-proofing
- **Agent 3** — temperature 0.9, instructed to maximise edge-case coverage and error handling

Each agent produces an independent API specification. A synthesis agent then:

1. Scores all three on the team's evaluation criteria (simplicity, extensibility, robustness)
2. Selects Agent 1's endpoint naming conventions (simplest), Agent 2's versioning strategy (most extensible), and Agent 3's error codes (most comprehensive)
3. Assembles a merged specification documenting which source contributed each decision
4. Passes the merged spec to a committee review loop before the team accepts it

The result is a specification no single agent would have produced — combining simplicity, extensibility, and robustness — validated by committee review before acceptance.

## Related

- [Agent Composition Patterns](../agent-design/agent-composition-patterns.md)
- [Committee Review Pattern](../code-review/committee-review-pattern.md)
- [Task-Specific vs Role-Based Agents](../agent-design/task-specific-vs-role-based-agents.md)
- [Orchestrator-Worker Pattern](orchestrator-worker.md)
- [Sub-Agents Fan-Out](sub-agents-fan-out.md)
- [Voting Ensemble Pattern](voting-ensemble-pattern.md)
- [LLM Map-Reduce](llm-map-reduce.md)
- [Multi-Model Plan Synthesis](multi-model-plan-synthesis.md)
- [Multi-Agent Topology Taxonomy](multi-agent-topology-taxonomy.md)
- [Oracle Task Decomposition](oracle-task-decomposition.md)
- [Adversarial Multi-Model Pipeline](adversarial-multi-model-pipeline.md)
- [Bounded Batch Dispatch](bounded-batch-dispatch.md)
- [Multi-Agent SE Design Patterns](multi-agent-se-design-patterns.md)
- [Staggered Agent Launch](staggered-agent-launch.md)
- [Observation-Driven Coordination](crdt-observation-driven-coordination.md)
- [Developer Attention Management with Parallel Agents](../human/attention-management-parallel-agents.md)
- [Adaptive Sandbox Fan-Out Controller](adaptive-sandbox-fanout-controller.md)
- [Recursive Best-of-N Delegation](recursive-best-of-n-delegation.md)
- [Independent Test Generation in Multi-Agent Systems](independent-test-generation-multi-agent.md)
