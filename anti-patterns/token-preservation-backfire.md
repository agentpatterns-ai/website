---
title: "Token Preservation Backfire for AI Agent Development"
term: "Token Preservation Backfire"
description: 'Token-preservation instructions create a competing objective: the agent resolves the conflict by doing less work, not completing the task better.'
tags:
  - instructions
  - tool-agnostic
  - anti-pattern
last_reviewed: 2026-06-13
maturity: established
---

# Token Preservation Backfire

> A token preservation instruction creates a competing objective the agent resolves by doing less work, not by completing the task better.

## The Pattern

Add instructions like "preserve tokens," "avoid waste," or "be efficient" to system prompts. The intent is cost savings. The effect is reduced output quality.

## Why It Fails

Efficiency instructions create a second objective: minimise resource use. When this competes with the user's task objective, the agent resolves the conflict by doing less work -- refusing explorations, skipping file reads, and stopping early.

Cursor discovered this during their Codex model harness development. GPT-5-Codex, instructed to "preserve tokens and not be wasteful," would sometimes stop with:

> "I'm not supposed to waste tokens, and I don't think it's worth continuing with this task!"

The model treated token conservation as a goal in its own right. Rather than optimising *how* it worked, the instruction changed *whether* it worked on substantial problems.

```mermaid
flowchart LR
    A["System prompt:<br/>'preserve tokens'"] --> B["Agent receives<br/>two objectives"]
    B --> C["1. Complete the task"]
    B --> D["2. Minimise tokens"]
    C ---|conflict| D
    D --> E["Agent resolves conflict<br/>by doing less"]
    E --> F["Skips exploration"]
    E --> G["Refuses ambitious tasks"]
    E --> H["Stops early"]
```

## The Mechanism

System-level instructions override user-level task requests. When token preservation is a system directive, the efficiency constraint takes precedence over the user's objective — the agent is not being lazy, it is faithfully following a conflicting instruction.

Any instruction framing work as a *cost to be minimised* risks reducing agent ambition — a form of [objective drift](objective-drift.md) where the resource budget displaces the task goal. The effect is most documented for long-horizon coding agents; evidence for other task types is limited to a small number of practitioner reports.

## When This Applies

The failure mode is specific to long-horizon, tool-using tasks where the agent chooses whether to explore or continue — coding and file-system work.

Brevity framing stays safe for conversational assistants, summarisation, and single-turn tasks without tool use — where the model has no opportunity to do *less work*.

The backfire is not universal — a *bounded* budget differs from an open-ended "don't waste tokens" directive. The Token-Budget-Aware LLM Reasoning framework reports a 68% token reduction with under 5% accuracy loss by inserting an estimated budget into the prompt ([arxiv 2412.18547](https://arxiv.org/abs/2412.18547), ACL 2025 Findings; [code](https://github.com/GeniusHTX/TALE)). The failure is a property of vague resource-minimisation framing, not of efficiency goals as such.

## Mitigation

| Instead of | Use |
|---|---|
| "Preserve tokens" | "Be thorough" |
| "Don't waste resources" | "Bias to action" |
| "Be efficient and concise" | "Implement with reasonable assumptions" |
| "Minimise tool calls" | "Use the tools needed to verify your work" |
| "Only read files when necessary" | "Read files to build context before acting" |

Reframe constraints as **quality targets** rather than **resource limits**.

**Frame around action.** OpenAI's Codex prompting guide: "Bias to action: default to implementing with reasonable assumptions; do not end on clarifications unless truly blocked."

**Use completion criteria.** LangChain structures agent phases (Planning, Build, Verify, Fix) with pre-completion checklists — done means quality criteria met, not budget hit.

**Make constraints mechanical.** Anthropic recommends requiring absolute filepaths rather than instructing "don't use relative paths" — the constraint enforces itself.

## Sources

- [Cursor -- Improving Cursor's Agent for Codex Models](https://cursor.com/blog/codex-model-harness)
- [ZenML -- Optimizing Agent Harness for Codex Models](https://www.zenml.io/llmops-database/optimizing-agent-harness-for-openai-codex-models-in-production)
- [Anthropic -- Claude 4.6 Prompting Best Practices](https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
- [OpenAI -- Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide/)
- [LangChain -- Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
- [Anthropic -- Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

## Key Takeaways

- Open-ended efficiency instructions ("preserve tokens", "don't be wasteful") create a second objective that long-horizon agents resolve by doing less work — skipping exploration, refusing ambitious tasks, stopping early.
- The mechanism is instruction precedence: a system-level resource constraint outranks the user's task, so the agent is faithfully following a conflicting directive, not being lazy.
- The failure mode is specific to multi-step, tool-using tasks where the agent chooses whether to continue ([harness-engineering](../agent-design/harness-engineering.md) territory); single-turn and summarisation work has no "less work" to fall back to.
- A bounded, quantified token budget (e.g. TALE) can cut tokens with minimal accuracy loss — the backfire is a property of vague minimisation framing, not of efficiency goals.
- Reframe constraints as quality targets ("be thorough", "bias to action") or make them mechanical, rather than as resource limits.

## Related

- [Instruction Polarity: Positive Rules Over Negative](../instructions/instruction-polarity.md)
- [Instruction Compliance Ceiling](../instructions/instruction-compliance-ceiling.md)
- [Distractor Interference](distractor-interference.md)
- [Objective Drift](objective-drift.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Harness Engineering](../agent-design/harness-engineering.md) — environment design that mechanically enforces constraints agents fail to self-impose
