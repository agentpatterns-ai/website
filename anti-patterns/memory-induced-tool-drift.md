---
title: "Memory-Induced Tool-Drift in LLM Agents"
term: "Memory-Induced Tool-Drift"
description: "Personality biases in agent memory act as implicit steering vectors on tool-call parameters in unrelated contexts; prompt defenses do not eliminate the drift."
tags:
  - agent-design
  - memory
  - anti-pattern
  - tool-agnostic
  - arxiv
aliases:
  - memory induced tool drift
  - personality bias tool drift
last_reviewed: 2026-06-12
maturity: emerging
---

# Memory-Induced Tool-Drift in LLM Agents

> Memory-induced tool-drift is when personality biases in an agent's long-term memory silently steer tool-call parameters in contexts where those preferences should not apply.

It is a failure mode of agents that combine persistent personality memory with tool-calling: biased memory entries act as implicit steering vectors on the model's activations, redirecting tool parameters toward the bias even when the current task is unrelated ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)).

## The Pattern

A "fast iteration" preference shortens timeouts on resilience tests; a "low-cost" preference reduces scan depth on a security review; a "risk-tolerant" preference relaxes safety thresholds on deployments — each a parameter the user never set on the current task. The pattern manifests only when three conditions all hold:

- Persistent personality memory accumulated across sessions
- A tool whose parameters have semantic slack
- Retrieval naive enough to surface the bias entry as relevant

## Why It Fails

A stored "I value low cost" is indistinguishable from an in-prompt "minimize cost" once attended to. The mechanism is attention competition under semantic similarity: when a tool's parameters share surface keywords with a memory entry — "configure," "deploy," "test" — that entry gets attended to despite no causal bearing on the task, and the model incorporates its preference exactly as it would an in-prompt instruction ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)).

The effect is large and broad. Across seven frontier models, biased memories raised deflection scores by **up to +3.6 points on a 1-5 scale**, across 105 MEMDRIFT scenarios spanning five bias dimensions and seven domains; a scan of verified MCP servers identified **608 vulnerable tool parameters** ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)). Prompt-based relevance instructions and memory filters **reduce drift but do not eliminate it** on any model class tested.

## Example

An agent has a memory entry written months ago: *"User prefers fast iteration over thorough review."* The user now asks the agent to configure a CI pipeline for a security-critical library.

**Drift surface — the agent's tool call:**

```yaml
# tool: configure_ci_pipeline
test_timeout_seconds: 30        # default: 120
parallel_workers: 16            # default: 4
fail_fast: true                 # default: false
required_reviewers: 0           # default: 1
```

No instruction in the current prompt asked for these. The "fast iteration" preference, surfaced by keyword-similarity retrieval, steered four parameter choices on a task where security is the explicit goal — the same attention-competition mechanism as [distractor interference](distractor-interference.md). Each value is individually defensible — the failure is that bias from one context shaped tool calls in another.

## Remediation

The paper frames the gap as needing "specialized safeguards addressing memory management and tool-call generation" ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)). Practical mitigations:

- **Scope personality memory by task domain.** Tag preference entries with the domains they apply to; do not surface "fast iteration" during security work.
- **Constrain tool parameters at the schema level.** A required-reviewers field that cannot drop below the policy minimum cannot be steered.
- **Audit tool-call parameters against memory.** A post-hoc check flagging every parameter whose value matches a stored preference surfaces drift without relying on model self-correction.
- **Separate preferences from facts.** Stable, verified facts belong in [agent memory](../agent-design/agent-memory-patterns.md); preferences need scope-bound, retrieval-time filtering.

## When This Backfires

The anti-pattern framing vanishes when any of the three conditions is removed:

- **Single-user single-task agents** — personality and task context align, so the "drift" is intended personalization.
- **Stateless agents** — without persistent memory the failure is structurally impossible.
- **Fully-constrained tool surfaces** — if every parameter is dictated by the user's literal request, bias has no slack to exploit.
- **Strict task-conditional retrieval** — namespacing preferences by domain shrinks the drift surface, though it does not eliminate it ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)).

Scoped correctly, personality memory pays off: [MAPLE](https://arxiv.org/abs/2602.13258) reports a 14.6% personalization-score gain, and [MEMENTO](https://arxiv.org/abs/2505.16348) shows episodic memory delivering both personalization and in-context learning. The lesson is not "avoid personality memory" — it is "do not let it leak into tool calls in unrelated domains."

## Key Takeaways

- Personality biases in persistent memory act as implicit steering vectors on tool-call parameters, even when the current task is unrelated to the stored preference.
- The drift is real, large, and present across seven frontier models — up to +3.6 deflection points on a 1-5 scale, with 608 vulnerable tool parameters identified in verified MCP servers ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)).
- Prompt-based relevance instructions and memory filters reduce but do not eliminate the drift — "just tell the model to ignore it" is not a sufficient defense.
- The failure requires three conditions: persistent personality memory, tool parameters with semantic slack, and naive retrieval. Miss any one and the agent is not vulnerable.
- Treat personality memory and stable factual memory as different classes — preferences need scoped retrieval; facts do not.

## Related

- [Agent Memory Patterns: Learning Across Conversations](../agent-design/agent-memory-patterns.md)
- [Context Poisoning: When Hallucinations Become Premises](context-poisoning.md)
- [Distractor Interference: Relevance Is Not Enough](distractor-interference.md)
- [Objective Drift: When Agents Lose the Thread](objective-drift.md)
- [The Anthropomorphized Agent](anthropomorphized-agent.md)
