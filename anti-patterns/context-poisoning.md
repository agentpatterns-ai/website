---
title: "Context Poisoning: When Hallucinations Become Premises"
description: "Context poisoning: an early hallucination becomes a trusted premise, causing every subsequent step to build on a false foundation the agent never questions."
aliases:
  - hallucination propagation
  - hallucination cascade
tags:
  - context-engineering
  - agent-design
---

# Context Poisoning: When Hallucinations Become Premises

> A hallucination in step 3 becomes a trusted fact in step 4. The agent remains confident and coherent -- it is just building on a false foundation.

## The Pattern

An agent hallucinates an incorrect detail early in a session -- a wrong API signature, a misidentified file, a nonexistent function. The error is not caught. Each subsequent step treats the hallucination as ground truth, compounding the original mistake.

## How It Differs from Related Failures

| Failure Mode | What Goes Wrong |
|---|---|
| [Context rot (Infinite Context)](infinite-context.md) | Attention degrades as context grows |
| [Objective Drift](objective-drift.md) | Goal lost during summarisation |
| [Distractor Interference](distractor-interference.md) | Wrong instruction attended |
| **Context Poisoning** | Wrong content treated as fact |

## Why Detection Is Hard

Output remains coherent, confident, and internally consistent. The agent does not hedge or self-correct. Once LLMs take a wrong turn, they over-commit to the flawed premise rather than revisiting it ([Breunig, 2025](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)) `[unverified]`.

## Common Causes

| Cause | Mechanism |
|---|---|
| Model hallucination | Wrong API signature generated, then called in later steps |
| Stale code comments | Outdated comment treated as current behaviour |
| Contaminated user input | Hidden control characters or contradictory instructions in pasted text |
| Context overflow | Poisoned content gets disproportionate attention weight ([Roo Code](https://docs.roocode.com/advanced-usage/context-poisoning)) |

## The Propagation Chain

```mermaid
flowchart LR
    A["Step 1: Agent reads codebase"] --> B["Step 2: Hallucinates function signature"]
    B --> C["Step 3: Generates code using wrong signature"]
    C --> D["Step 4: Error output enters context"]
    D --> E["Step 5: Agent 'fixes' by adjusting around the hallucination"]
    E --> F["Step 6: Deeper into wrong solution space"]

    style B fill:#c0392b,color:#fff
    style C fill:#e74c3c,color:#fff
    style D fill:#e74c3c,color:#fff
    style E fill:#e74c3c,color:#fff
    style F fill:#e74c3c,color:#fff
```

Each step is locally correct. In multi-agent systems the cascade crosses agent boundaries -- one agent's hallucination becomes another's trusted input ([Lin et al., 2025](https://arxiv.org/abs/2509.18970)).

## Example

A Claude Code session is tasked with refactoring a payment module. Early in the session, the agent reads the codebase and hallucinates that `process_payment()` accepts an optional `currency` parameter. It does not. The agent proceeds to:

1. Refactor callers to pass `currency` explicitly
2. Add currency conversion logic that calls the nonexistent parameter
3. Write tests that mock the parameter
4. When tests fail, "fix" by adjusting the mock setup rather than questioning the premise

Forty tool calls deep, the developer reviews a diff full of changes built on a function signature that never existed. Every individual change is internally consistent. The root cause -- a hallucinated parameter in step 1 -- is buried in scroll-back.

## Recovery

Corrective prompts only mask the problem temporarily -- the hallucination resurfaces from poisoned context. Start a new session with clean context ([Roo Code docs](https://docs.roocode.com/advanced-usage/context-poisoning)) `[unverified]`.

## Mitigation

| Strategy | Mechanism |
|---|---|
| **Ground-truth checks** | Re-read the real file each step; do not trust context memory ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)) |
| **Evaluator-optimizer** | A second model evaluates output, breaking confirmation bias ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)) |
| **Pre-completion checklists** | Middleware enforces verification before completion ([LangChain](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)) |
| **Sub-agent isolation** | Separate context windows prevent cross-task contamination ([FlowHunt](https://www.flowhunt.io/blog/context-engineering-for-ai-agents/)) |
| **Externalise results** | Write to files; disk is ground truth, context is lossy ([FlowHunt](https://www.flowhunt.io/blog/context-engineering-for-ai-agents/)) |
| [**Poka-yoke tool design**](../tool-engineering/poka-yoke-agent-tools.md) | Require absolute paths, reject ambiguous identifiers ([Anthropic](https://www.anthropic.com/engineering/building-effective-agents)) |
| **Hard reset** | New session rather than correcting within poisoned context ([Roo Code](https://docs.roocode.com/advanced-usage/context-poisoning)) |

## Related

- [The Infinite Context](infinite-context.md)
- [Context Window Dumb Zone](../context-engineering/context-window-dumb-zone.md)
- [Objective Drift](objective-drift.md)
- [Distractor Interference](distractor-interference.md)
- [Assumption Propagation](assumption-propagation.md)
- [Session Partitioning](session-partitioning.md)
- [Evaluator-Optimizer](../agent-design/evaluator-optimizer.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Incremental Verification](../verification/incremental-verification.md)
- [Trust Without Verify](trust-without-verify.md)
