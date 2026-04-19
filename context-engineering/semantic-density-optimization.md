---
title: "Semantic Density Optimization for Agent Codebases"
description: "Maximize the ratio of task-relevant tokens in your codebase — eliminate zero-information ceremony while preserving high-value naming, documentation, and commit context."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
aliases:
  - agent-readable codebase
---

# Semantic Density Optimization for Agent Codebases

> Maximize the ratio of task-relevant tokens in the codebase — eliminate structural ceremony while preserving naming, documentation, and commit context that agents cannot reconstruct without inference cost.

## The Compression Paradox

Naively compressing codebase content for agents backfires. A controlled experiment on log format ([Ustynov, 2026](https://arxiv.org/abs/2604.07502)) shows why:

| Format | Input tokens | Session tokens | Session/file ratio |
|--------|-------------|----------------|-------------------|
| Human-readable | 8,072 | 18,900 | 2.3× |
| Structured | 7,106 | 24,000 | 3.4× |
| Compressed | 6,695 | 31,600 | 4.7× |

The compressed format cut input tokens by 17% but increased total session cost by 67%. Removing semantic content shifts interpretive burden to the model's reasoning phase — it reconstructs meaning it could have read directly.

The lesson: optimize for **semantic density**, not raw token count.

## What Semantic Density Means

Semantic density is the ratio of task-relevant tokens to total tokens. Every token in a codebase is either:

- **High-density** — carries meaning the agent cannot derive without additional inference: descriptive names, type annotations, docstrings, error messages, commit reasoning
- **Zero-density** — structural overhead the agent must parse but gains nothing from: boilerplate, dependency injection wiring, framework scaffolding, ceremonial access modifiers

The goal is not to compress — it is to eliminate zero-density tokens while protecting high-density ones.

## Seven Conventions to Reconsider

[Ustynov (2026)](https://arxiv.org/abs/2604.07502) analyzes seven human-centric conventions under agent consumption:

### 1. Naming Conventions

Descriptive names are high-density tokens. `VerifyOrderByAvailableAmount` is immediately interpretable; `verifyOrd` forces the agent to infer meaning from usage context. Strengthen naming for agents — abbreviations that save keystrokes for humans cost reasoning tokens for agents.

### 2. Commit Messages

The conventional 50-character limit is agent-hostile. When agents trace history to understand why code exists, terse commit messages force multi-turn clarification. Include the reasoning, rejected alternatives, and constraints in commit messages — information the agent would otherwise reconstruct through multiple file reads.

### 3. Abstraction Depth

Deep call hierarchies force agents to traverse multiple files per task. Flat call chains with well-named functions reduce cross-file navigation. Enterprise frameworks that distribute a single request across many scaffolding layers make agents pay that read cost on every lookup.

### 4. File Splitting

Human cognitive limits drive the convention of keeping files small (under 200 lines). Agents do not share this limit but do pay a navigation cost for each additional file. Let deployment boundaries and logical cohesion drive file organization, not human screen capacity.

### 5. SOLID Principles

Single-responsibility and interface-segregation principles that split logic into micro-units increase agent traversal cost. Apply them where they serve logical boundaries, not where they serve human reading habits.

### 6. Logging Formats

Structured log entries with readable field names outperform abbreviation-heavy formats. `"Payment failed for order #4521: insufficient funds"` is immediately interpretable. `"|E|PS|pf|o=4521|rs=insuf_funds"` forces abbreviation decoding, costing reasoning tokens.

### 7. Classical Anti-Patterns

Anti-patterns like the God Object emerged to protect human cognition from overwhelm. Under agent consumption, consolidating related logic into fewer files reduces cross-file traversal. This trade-off lacks empirical validation — the paper flags it as theoretically motivated but unconfirmed. Attention degradation on very large files is a documented LLM limitation ([Liu et al., 2024](https://arxiv.org/abs/2307.03172)); the paper does not measure it in the consolidation context, so treat this recommendation as provisional.

## The Program Skeleton Artifact

The paper proposes a new artifact — a `CODEMAP.md` file — stored at the repository root:

```markdown
# CODEMAP.md

## Module Topology
- `src/payments/` — payment processing pipeline
- `src/orders/` — order lifecycle management

## Entry Points
- `payments/processor.py:process_payment(order_id)` — main payment flow
- `orders/validator.py:validate_order(order)` — pre-payment validation

## Key Call Chains
1. API → `process_payment` → `validate_order` → `charge_card` → `emit_event`

## Data Flow
Order ID → validation → payment charge → event emission → status update
```

This provides batch-oriented navigation in a single read. Unlike Language Server Protocol queries (one symbol at a time), a program skeleton gives agents the codebase topology before they begin exploring — reducing the number of file reads required to understand task context.

## Example

A logging statement illustrates semantic density directly.

**Before — compressed, low-density:**
```python
log.e(f"|PS|pf|o={oid}|rs={rs}")
```

**After — readable, high-density:**
```python
logger.error(f"Payment failed for order #{order_id}: {reason}")
```

The compressed version uses fewer input tokens per log line — the savings are real but modest. When the agent reads this log during debugging, it must decode `PS`, `pf`, and the abbreviated field names — spending reasoning tokens that exceed the original savings. The readable version is immediately parseable; the agent proceeds without an intermediate decoding step.

## When This Backfires

Semantic density optimization trades human ergonomics for agent performance. The trade-off is not always favorable:

- **Human teams dominate the workflow.** If agents touch the codebase rarely — for code review, one-off generation, or ad hoc queries — optimizing conventions for agents degrades the daily experience of the human developers who live in the code.
- **Single-study basis.** The evidence comes from one controlled experiment on log formats. Applying its conclusions to naming conventions, file structure, and SOLID principles is an extrapolation the paper acknowledges as theoretically motivated.
- **Flatter files create their own problems.** Consolidating logic into fewer large files reduces agent traversal cost but increases merge conflict frequency, complicates code ownership, and may exceed the attention range of the model on very large files.
- **Context window sizes are growing.** As models handle larger windows with better long-range attention, the navigation cost advantage of flatter structures shrinks; human-oriented organization may dominate again.

## Key Takeaways

- Compressing codebase content increases total session cost when compression removes semantic information the agent must reconstruct
- Semantic density optimization targets zero-information tokens (boilerplate, ceremony) not high-information tokens (names, docs, error messages)
- Stronger naming conventions, expanded commit messages, and flatter abstractions improve agent performance
- A `CODEMAP.md` program skeleton gives agents topology-level orientation in a single read
- File consolidation driven by deployment boundaries (not human cognitive limits) reduces agent traversal cost

## Related

- [Token-Efficient Code Generation](token-efficient-code-generation.md) — structural transforms that reduce generated-code token cost without semantic loss
- [Repository Map Pattern](repository-map-pattern.md) — parse-time symbol extraction for agent navigation, complementary to the program skeleton
- [Semantic Context Loading](semantic-context-loading.md) — LSP-based symbol navigation as an alternative to file-level reading
- [Context Budget Allocation](context-budget-allocation.md) — distributing token budget across sources
- [Prompt Compression](prompt-compression.md) — reducing instruction token count without semantic loss
- [Context Compression Strategies](context-compression-strategies.md) — broader techniques for managing context size in long-running agents
- [Agent-First Software Design](../agent-design/agent-first-software-design.md) — designing system interfaces for agent consumption; this page covers internal codebase conventions
