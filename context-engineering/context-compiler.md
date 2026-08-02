---
title: "Context Compiler: Deterministic Assembly Over Bigger Windows"
term: "Context Compiler"
description: "Compile a task-scoped payload — full target file, skeletonized dependencies, everything else excluded — instead of buying a bigger context window."
aliases:
  - context compilation
  - compiled context payload
tags:
  - context-engineering
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-02
maturity: emerging
---

# Context Compiler: Deterministic Assembly Over Bigger Windows

> A context compiler resolves what a task actually reaches, trims those dependencies to interfaces, and excludes the rest.

A context compiler is a deterministic step that runs before the model and builds the payload for one task. It takes a target file, resolves what that file reaches through the dependency graph, trims the reachable set down to interfaces, and drops everything else ([Alexander, 2026](https://towardsdatascience.com/coding-agents-dont-need-bigger-context-windows-they-need-a-context-compiler/)). The output is an artifact you can read, diff, and attach to a failed run. Window size stops being the lever; selection becomes the lever.

## Apply only under these conditions

The evidence supports compilation only where all four hold.

- The task names a target file. Reachability is computed from a seed, and exploratory questions or cross-cutting refactors supply none.
- Static structure matches runtime structure. Resolving calls by name rather than by type creates blind spots the author names directly: dispatch through `importlib` and `getattr`, event-decorator registration that fires without an explicit call, and name collisions ([Alexander, 2026](https://towardsdatascience.com/coding-agents-dont-need-bigger-context-windows-they-need-a-context-compiler/)).
- The agent can search past the compiler. Exclusion is invisible to the model, so the agent needs a live-search escape hatch for the cases the compiler gets wrong.
- You measure tasks resolved, not tokens saved. Those two numbers move independently, and only one of them is the outcome.

## The three tiers

Compilation sorts every file into one of three tiers ([Alexander, 2026](https://towardsdatascience.com/coding-agents-dont-need-bigger-context-windows-they-need-a-context-compiler/)):

| Tier | Content | Purpose |
|------|---------|---------|
| Target | Full source | The file being edited |
| Reachable | Signatures and docstrings, implementations replaced by placeholders | Enough interface to call correctly |
| Unreachable | Excluded | Never enters the window |

The author reports 69.4% token reduction across 7 files and 74.3% on a 12-file repository, compiling in under 75 milliseconds ([Alexander, 2026](https://towardsdatascience.com/coding-agents-dont-need-bigger-context-windows-they-need-a-context-compiler/)). Those figures count tokens removed. They do not report whether the agent then produced a correct edit.

## Why it works

Two causes work here, and the better-known one is the weaker. Cutting irrelevant code preserves attention: models draw on a finite [attention budget](context-budget-allocation.md) that "every new token introduced depletes", so context carries diminishing marginal returns and unrelated files compete with the target for the same scarce resource ([Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

The stronger cause is determinism. Lin et al. measured that supplying lightweight call and inheritance topology improves function localization, reduces interaction rounds, and roughly halves run-to-run variance ([Lin et al., 2026](https://arxiv.org/abs/2606.26979v2)). The agent sees the same structural facts in the same position every run, instead of letting a stochastic first search result bias the whole trajectory. What compilation reliably buys is reproducibility and attributability, not raw capability — a failed run arrives with the exact payload that produced it, which turns "the agent got confused" into a claim you can check.

## When this backfires

- Token reduction is not the outcome metric. The nearest controlled measurement cut input tokens 42% through minification and lost 12 percentage points of resolution rate on SWE-bench Verified ([Hrubec & Cito, 2026](https://arxiv.org/abs/2606.01326v1)). A compiler tuned to the token number keeps looking like a win past the point it starts costing accuracy.
- A good search loop may already beat it. Grep generally outperformed vector retrieval in a controlled comparison, and scores depended strongly on which harness and tool-calling style was used ([Sen et al., 2026](https://arxiv.org/abs/2605.15184v1)). Anthropic recommends the opposite posture — keep lightweight identifiers and load data at runtime, with "some data up front for speed" only as a hybrid ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- Exclusion is subtractive, so a silent tier-3 decision hides its own errors. A [repository map](repository-map-pattern.md) or an inline [deterministic anchor](deterministic-anchoring.md) adds facts the agent can ignore; a dropped file is one the agent never learns exists. The source's own compiler flags what it could not resolve rather than guessing, on the principle that "an incomplete map with explicit warnings is far more useful than a complete map that is secretly wrong" ([Alexander, 2026](https://towardsdatascience.com/coding-agents-dont-need-bigger-context-windows-they-need-a-context-compiler/)).
- Fast-moving repositories outrun the payload. Nothing recompiles it after the agent's own edits, so a monorepo with high commit frequency invalidates the artifact mid-session.
- Small repositories gain nothing. When the whole codebase already fits comfortably in the window, tier 3 has nothing to exclude and the compile step is pure overhead.
- Gains are not uniform. Lin et al. report diminishing returns for dense semantics and recommend pruned forward edges for large repositories rather than one fixed granularity ([Lin et al., 2026](https://arxiv.org/abs/2606.26979v2)).

## Example

Skeletonization is what tier 2 does to every reachable dependency: the signature and docstring survive, the body does not ([Alexander, 2026](https://towardsdatascience.com/coding-agents-dont-need-bigger-context-windows-they-need-a-context-compiler/)).

```python
# tier 2 — reachable dependency, compiled
class SessionStore:
    def refresh(self, token: str) -> Token:
        """Exchange a refresh token for a new access token."""
        ...
```

The agent gets what it needs to call `refresh` correctly and none of the retry logic inside it. Log which tier every file landed in, so a wrong answer can be traced to a tier-3 decision rather than blamed on the model.

## Key Takeaways

- A context compiler is a deterministic pre-model step that resolves a target file's reachable set, skeletonizes it, and excludes the rest.
- Its dependable payoff is reproducibility and attributability, not accuracy — the compiled payload is an inspectable input you can attach to a failed run.
- Measure tasks resolved, not tokens saved. The reported gains are token reductions on 7-file and 12-file samples with no task-success measurement, and a comparable cut elsewhere cost 12 percentage points of resolution rate.
- Static reachability is unsound under runtime dispatch, and tier-3 exclusion hides its own misses, so keep a live-search escape hatch.
- Where the agent already searches the live filesystem well, compilation competes with a loop that has fresher facts.

## Related

- [Repository Map Pattern](repository-map-pattern.md) — whole-repo ranked orientation fitted to a token budget, additive where compilation is subtractive
- [Deterministic Anchoring](deterministic-anchoring.md) — inject static call-graph facts inline for reproducible navigation without excluding anything
- [Source Code Minification for State-in-Context Agents](source-code-minification-trade-off.md) — the measured cost of trading tokens for accuracy
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md) — assemble a different bundle per workflow phase rather than per target file
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md) — the just-in-time alternative that pulls context at the moment of need
