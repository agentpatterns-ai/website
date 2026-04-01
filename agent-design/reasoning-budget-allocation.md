---
title: "Reasoning Budget Allocation: The Reasoning Sandwich"
description: "Allocate maximum reasoning compute to planning and verification phases, reduced compute to execution — rather than a fixed level throughout all steps."
aliases:
  - reasoning sandwich
tags:
  - agent-design
  - cost-performance
  - source:opendev-paper
---
# Reasoning Budget Allocation: The Reasoning Sandwich

> Allocate maximum reasoning compute to planning and verification phases, reduced compute to execution — rather than using a fixed level throughout.

## The Pattern

Not all steps in an agent workflow require the same depth of reasoning. Planning and verification are high-stakes; execution is largely mechanical.

[LangChain's deep agent experiments](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) tested a "reasoning sandwich" — extra-high compute at planning, high at execution, extra-high at verification (xhigh-high-xhigh). The sandwich achieved the highest completion rate (66.5% on Terminal Bench 2.0), outperforming both continuous maximum reasoning — which scored poorly (53.9%) due to agent timeouts — and uniform high reasoning (63.6%).

```mermaid
graph LR
    A[Planning<br/>Extra-high compute] --> B[Execution<br/>High compute]
    B --> C[Verification<br/>Extra-high compute]
```

## Phase Breakdown

**Planning — extra-high compute.** Map the problem space: requirements, approach, risks. Errors here propagate through every subsequent step.

**Execution — high compute.** Follow the plan: writing code, running commands. Reduced compute handles mechanical steps while lowering per-step cost.

**Verification — extra-high compute.** Check output against requirements, run tests. A missed failure produces false completion.

## Dual-Mode Operation

The OPENDEV paper implements the sandwich architecturally through two modes ([Bui, 2026 §2.2.2](https://arxiv.org/abs/2603.05344)):

- **[Plan Mode](../workflows/plan-first-loop.md)**: restricts the agent to read-only tools; planning delegated to a Planner subagent whose schema contains only read-only tools ([subagent schema-level tool filtering](../multi-agent/subagent-schema-level-tool-filtering.md)) — eliminating state machine complexity
- **Normal Mode**: full tool access for implementation

Mode switching triggers via explicit command (`/plan`) or planning-intent heuristics ([Bui, 2026 §2.2.2](https://arxiv.org/abs/2603.05344)). This maps to the sandwich: [Plan Mode](../workflows/plan-mode.md) (extra-high compute) → Normal Mode execution (high) → verification (extra-high).

An optional thinking phase adds a separate inference call using a dedicated Thinking model *before* action selection — architecturally distinct from in-generation reasoning ([Bui, 2026 §2.2.6](https://arxiv.org/abs/2603.05344)). This amplifies any phase where deeper reasoning is needed.

## Extended Thinking Budget Triggers

Extended thinking allocates a dedicated reasoning budget before the model generates its response — distinct from the think tool, which reasons mid-stream between tool calls.

In Claude Code, [including "ultrathink" in a skill's content enables extended thinking](https://code.claude.com/docs/en/skills), allocating maximum thinking tokens for that skill.

### Maximum Thinking as a Cost-Performance Tradeoff

A [community analysis](https://claudelog.com/mechanics/ultrathink) positions maximum-thinking on a balanced model as an alternative to model tier upgrades. Exhausting the thinking budget on a cheaper model costs less than switching tiers, while closing much of the capability gap for reasoning-heavy tasks [unverified].

This stacks with other techniques:

1. **Extended thinking** — maximum reasoning tokens via trigger keyword
2. **[Plan mode](../workflows/plan-mode.md)** — structured planning before execution
3. **Iterative critique** — systematic [self-review cycles](agent-self-review-loop.md) to catch edge cases

Each layer adds cost but compounds quality for structured reasoning tasks [unverified — practitioner experience, not benchmarked].

### Applying Budget Triggers

- **Claude Code skills**: include "ultrathink" in `SKILL.md` content to [enable extended thinking](https://code.claude.com/docs/en/skills)
- **Claude API**: set the `thinking` budget parameter per call — high for planning/verification, standard for execution
- **Any tool with model routing**: route planning and verification to a capable model, execution to a cheaper one

For tools without per-call configuration, approximate through prompt structure: deep reasoning guidance in planning prompts, less in execution.

## When to Apply

The sandwich pays off when:

- Tasks have discrete planning, execution, and verification phases
- Planning mistakes are costly to repair after implementation begins
- Verification failures would be falsely reported as success

Single-step tasks and independent parallel tool calls see no benefit from added reasoning overhead.

## Key Takeaways

- Planning and verification warrant extra-high reasoning compute; execution warrants high.
- The sandwich achieved the highest completion rate (66.5%) in LangChain benchmarks, outperforming continuous maximum reasoning (53.9%, penalized by timeouts) and uniform high reasoning (63.6%).
- Extended thinking triggers (e.g., "ultrathink" in Claude Code skills) front-load reasoning before generation — distinct from mid-stream think tool reasoning.
- Maximum-thinking on a balanced model is a cost-effective alternative to model tier upgrades for reasoning-heavy tasks [unverified].
- Stack extended thinking with [plan mode](../workflows/plan-mode.md) and iterative critique to compound quality gains [unverified].
- Dual-mode operation (plan/normal) enforces the sandwich architecturally by restricting tool access per phase.

## Example

A Claude API implementation routing by phase:

```python
def run_sandwich(task: str) -> str:
    # Planning — extra-high thinking budget
    plan = client.messages.create(
        model="claude-opus-4-5",
        thinking={"type": "enabled", "budget_tokens": 10000},
        messages=[{"role": "user", "content": f"Plan: {task}"}],
    )

    # Execution — standard thinking budget
    result = client.messages.create(
        model="claude-opus-4-5",
        thinking={"type": "enabled", "budget_tokens": 2000},
        messages=[{"role": "user", "content": f"Execute plan:\n{plan.content[0].text}\nTask: {task}"}],
    )

    # Verification — extra-high thinking budget
    verdict = client.messages.create(
        model="claude-opus-4-5",
        thinking={"type": "enabled", "budget_tokens": 10000},
        messages=[{"role": "user", "content": f"Verify result meets requirements:\n{result.content[1].text}"}],
    )
    return verdict.content[1].text
```

In Claude Code skills, add `ultrathink` to the skill content for planning and verification skills, and omit it for execution skills.

## Related

- [Think Tool](think-tool.md)
- [Heuristic-Based Effort Scaling](heuristic-effort-scaling.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Loop Detection](../observability/loop-detection.md)
- [Circuit Breakers for Agent Loops](../observability/circuit-breakers.md)
- [Cost-Aware Agent Design](cost-aware-agent-design.md)
- [Harness Engineering](harness-engineering.md)
- [Know When Not to Add Structured Reasoning](../anti-patterns/reasoning-overuse.md)
- [Three Reasoning Spaces: Plan, Bead, and Code](three-reasoning-spaces.md)
- [Cognitive Reasoning vs Execution: A Two-Layer Agent](cognitive-reasoning-execution-separation.md)
- [Agentic Flywheel](agentic-flywheel.md)
- [Agent Harness](agent-harness.md)
- [Agent Turn Model](agent-turn-model.md)
- [Agentic AI Architecture Evolution](agentic-ai-architecture-evolution.md)
- [Agent-First Software Design](agent-first-software-design.md)
