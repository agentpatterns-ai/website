---
title: "Memory-Induced Tool-Drift in LLM Agents"
description: "Personality biases in agent memory act as implicit steering vectors on tool-call parameters in unrelated contexts; prompt defenses do not eliminate the drift."
tags:
  - agent-design
  - memory
  - anti-patterns
aliases:
  - memory induced tool drift
  - personality bias tool drift
---

# Memory-Induced Tool-Drift in LLM Agents

> Personality biases stored in long-term memory — cost-consciousness, impatience, risk tolerance — silently influence tool-call parameters in contexts where they should not apply.

Memory-induced tool-drift is a failure mode in agents that combine persistent personality memory with tool-calling: biased memory entries function as implicit steering vectors on the model's activations, redirecting tool parameters toward the bias even when the current task is unrelated ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)).

## The Pattern

A user once told the agent "I prefer low-cost options." Months later, in a security review of an authentication library, the agent calls a static-analysis tool with reduced scan depth — a parameter the user never set, on a task where cost has nothing to do with correctness.

The same shape applies across bias dimensions: an "impatient" preference shortens timeouts on resilience tests; a "risk-tolerant" preference relaxes safety thresholds on automated deployments. The pattern manifests only when three conditions all hold:

- The agent has persistent personality memory accumulated across sessions
- The tool being called has semantic slack in its parameters
- Memory retrieval is naive enough to surface the bias entry as relevant

## Why It Fails

Biased memories act as implicit steering vectors in activation space — pushing the model along the same latent directions as explicit behavioral instructions, with no in-prompt instruction triggering them ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)). A stored "I value low cost" is indistinguishable from an in-prompt "minimize cost" once attended to.

Across seven frontier models — including extended-reasoning variants — biased memories raised deflection scores by **up to +3.6 points on a 1-5 scale** versus baseline, measured across 105 MEMDRIFT scenarios spanning five bias dimensions and seven professional domains ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)). A scan of verified MCP servers identified **608 vulnerable tool parameters** — production-scale, not a benchmark artifact.

Prompt-based relevance instructions and memory filters **reduce drift but do not eliminate it** on any model class tested ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)). Telling the model to ignore irrelevant memories is not enough.

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

No instruction in the current prompt asked for these. The "fast iteration" preference, surfaced by keyword-similarity retrieval, steered four parameter choices on a task where security is the explicit goal. Each value is individually defensible — the failure is that bias from one context shaped tool calls in another.

## Remediation

The paper frames the gap as needing "specialized safeguards addressing memory management and tool-call generation" ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)). Practical mitigations:

- **Scope personality memory by task domain.** Tag preference entries with the domains they apply to; do not surface a "fast iteration" preference during security work.
- **Constrain tool parameters at the schema level.** Where a parameter has no semantic slack, make the schema enforce it. A required-reviewers field that cannot drop below policy minimum cannot be steered.
- **Audit tool-call parameters against memory entries.** A post-hoc check that flags every tool-call parameter whose value matches a memory-stored preference surfaces drift without requiring model self-correction.
- **Separate preferences from facts.** Treat "user prefers X" as a scope-bound preference with retrieval-time filtering, not a general fact. Stable, general, verified facts belong in [agent memory](../agent-design/agent-memory-patterns.md); preferences need stricter gating.

## Why It Works

The mechanism is attention competition under semantic similarity. When the current prompt activates a tool whose parameters share surface keywords with a memory entry — "configure," "deploy," "test" — the entry gets attended to even when its content has no causal bearing on the current task. The model then incorporates the memory's preference the same way it would incorporate an in-prompt instruction, because the activation patterns are equivalent ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)). "Ignore irrelevant memories" prompting reduces attention weight on biased entries but cannot zero it out, leaving residual drift that compounds across long-running sessions.

## When This Backfires

The anti-pattern framing does not apply universally:

- **Single-user single-task agents** — When the agent only does one job for one user, personality and task context are aligned by definition. The "drift" is the intended personalization.
- **Stateless agents** — Without persistent memory the failure mode is structurally impossible.
- **Fully-constrained tool surfaces** — If every parameter is dictated by the user's literal request, there is no slack for bias to influence.
- **Strict task-conditional retrieval** — Architectures that namespace preferences by domain and refuse cross-domain surfacing shrink the drift surface significantly, though they do not eliminate it ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)).

Personality memory delivers measurable benefit when retrieval is scoped correctly: [MAPLE](https://arxiv.org/abs/2602.13258) reports a 14.6% personalization-score improvement and trait incorporation rising from 45% to 75%, and [MEMENTO](https://arxiv.org/abs/2505.16348) shows episodic memory delivering both personalization and in-context learning benefits. The lesson is not "do not use personality memory" — it is "do not let personality memory leak into tool calls in unrelated domains."

## Key Takeaways

- Personality biases in persistent memory act as implicit steering vectors on tool-call parameters, even when the current task is unrelated to the stored preference.
- The drift is real, large, and present across seven frontier models — up to +3.6 deflection points on a 1-5 scale, with 608 vulnerable tool parameters identified in verified MCP servers ([Dabas et al., 2026](https://arxiv.org/abs/2605.24941)).
- Prompt-based relevance instructions and memory filters reduce but do not eliminate the drift — "just tell the model to ignore it" is not a sufficient defense.
- The failure requires three conditions: persistent personality memory, tool parameters with semantic slack, and naive retrieval. Architectures that miss any of these conditions are not vulnerable.
- Treat personality memory and stable factual memory as different classes — preferences need scoped retrieval; facts do not.

## Related

- [Agent Memory Patterns: Learning Across Conversations](../agent-design/agent-memory-patterns.md)
- [Context Poisoning: When Hallucinations Become Premises](context-poisoning.md)
- [Distractor Interference: Relevance Is Not Enough](distractor-interference.md)
- [Objective Drift: When Agents Lose the Thread](objective-drift.md)
- [The Anthropomorphized Agent](anthropomorphized-agent.md)
