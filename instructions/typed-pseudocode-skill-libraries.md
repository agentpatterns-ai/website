---
title: "Typed Pseudocode for Skill Libraries (Skill-as-Pseudocode)"
term: "Skill-as-Pseudocode"
description: "Converting prose skill files into typed pseudocode helps only when a concrete invocation template ships with the type signature. The contract alone tested below the prose it replaced."
aliases:
  - skill as pseudocode
  - pseudocode skill refactoring
  - typed pseudocode skill library
tags:
  - instructions
  - context-engineering
  - tool-agnostic
  - skills
  - arxiv
last_reviewed: 2026-09-01
maturity: emerging
---

# Typed Pseudocode for Skill Libraries (Skill-as-Pseudocode)

> Converting prose skill files to typed pseudocode pays only when the invocation template ships with the contract; the schema alone tested below prose.

Skill-as-Pseudocode (SaP) converts a markdown skill library into typed pseudocode automatically. Each converted skill carries a type signature plus a concrete action template, and a deterministic verifier decides which conversions to accept. On the ALFWorld unseen split it won 82 of 402 paired games against Graph-of-Skills retrieval's 47, at 22.8% fewer input tokens and 14.5% fewer LLM calls per game ([Li et al., 2026](https://arxiv.org/abs/2605.27955v2)). That came from one library, one benchmark, one model family, and the paper's own ablation shows the type signature is not the half earning it.

## When conversion pays

Three conditions come from the paper's setup and its stated limits ([Li et al., 2026](https://arxiv.org/abs/2605.27955v2)):

- The invocation has a fixed grammar. ALFWorld actions are closed strings in a small vocabulary, so a template can supply the exact call. A skill whose invocation is a judgment call has no such string.
- Procedural passages repeat. The proposer clusters near-duplicate units by frame extraction and embedding similarity at a 0.65 cosine floor. On the `skills_500` library of 5,709 procedural units, 149 candidate clusters produced 49 verified contracts, and four child skills covered 37 parents. A library of distinct skills has nothing to cluster.
- Arguments bind at index time. The verifier tests whether `invoke(κ, args)` can syntactically replace a unit, and bindings are computed when the library is built. A value that exists only as episode runtime state cannot be bound; the authors defer a runtime-expansion tool to future work.

Anthropic's skill-authoring guidance draws the same boundary from the other side: pseudocode and parameterized scripts belong to the medium-freedom tier, used "when a preferred pattern exists", while text instructions stay right for the high-freedom case where "multiple approaches are valid" and "decisions depend on context" ([Anthropic skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

## The four deterministic checks

The transferable part of SaP is the gate, not the pseudocode. One `gpt-4o-mini` call per cluster proposes a typed contract; four mechanical checks decide whether it is safe to accept unreviewed ([Li et al., 2026](https://arxiv.org/abs/2605.27955v2)):

| Check | What it measures | Failure it catches |
|---|---|---|
| Coverage | Token recall of the contract's trigger and input/output strings against the parent unit's text | A misnamed contract that does not describe its parent |
| Binding | Fraction of (parent, input) pairs whose text overlaps the input names | A cluster drawn too wide to share one signature |
| Replacement | Fraction of parents admitting a syntactic `invoke()` substitution | Control-flow entanglement that resists factoring |
| Risk | AST scan for unsafe operations, a hard reject at weighted score 0.80 or above | Dangerous operations promoted silently |

There is no aggregate score. The verifier's output is "a structured rejection profile, not a soft classifier score", so every rejection names which check failed first, and on `skills_500` binding is that check 71% of the time. Two thresholds route each candidate to auto-promote, review, or reject; the main result uses the conservative point `(τ_auto, τ_rev) = (0.65, 0.35)`, calibrated against synthetic negative controls rather than the benchmark. Of 149 candidates, 49 were promoted, binding extraction confirmed 470 of 791 call sites, and the cleanup pass rewrote 291 of 292 touched parents ([Li et al., 2026](https://arxiv.org/abs/2605.27955v2)).

## Why it works

The cost SaP removes is re-derivation paid on every retrieval, not context length. A markdown skill body does not separate what a skill does from how it is invoked, so the agent reads a long passage, emits an action whose verb or argument is slightly off, gets uninformative feedback, and re-retrieves the same prose ([Li et al., 2026](https://arxiv.org/abs/2605.27955v2)). A concrete action template ends that loop by supplying the call string in the exact tokens the environment accepts, as in the paper's own `go to {recep}` and `heat {obj} with {appliance}`. The guess never happens. The type signature narrows which arguments are admissible.

The ablation separates the two contributions on 134 games at a single seed, and the split is lopsided ([Li et al., 2026](https://arxiv.org/abs/2605.27955v2)):

| Bundle content | Wins / 134 |
|---|---|
| Templates plus skeleton plus contracts | 30 |
| Template only, contract block removed | 25 |
| Length-matched raw prose | 18 |
| Graph-of-Skills raw prose, unbounded | 16 |
| Contract only, template block removed | 13 |

The paper states that "the action template is necessary: removing it collapses reward below even the prose baseline (13 vs. template-only's 25, paired McNemar p=0.043)". Read the middle rows together and the type signature buys five wins on top of a template that already beats prose by nine.

## When this backfires

- You adopt the schema and skip the template. It is the cheapest half to adopt and, at 13 wins against prose's 16, the one that loses ([Li et al., 2026](https://arxiv.org/abs/2605.27955v2)).
- The procedure requires judgment. Where several approaches are valid and the choice depends on context, prose with reasoning is the recommended form, because it lets the model generalize to cases the contract's author never enumerated ([Anthropic](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).
- The library is already typed. OpenAPI and MCP surfaces carry a schema already, and the paper did not run its main experiment on them ([Li et al., 2026](https://arxiv.org/abs/2605.27955v2)).
- You expect structure to be enforcement. A separate contractual-skill framework found its fields "slightly higher on six models and slightly lower on two models, with small differences" against a plain expanded skill ([Liu, 2026](https://arxiv.org/abs/2605.22634v2)). Semantic fuzzing of 402 marketplace skills found specification violations in 120 of them, 29.9%, on benign requests ([Sefz, arXiv:2605.13044](https://arxiv.org/abs/2605.13044v1)).

Where the fix belongs is still contested. An unrelated group names the same defect in markdown skills and argues the missing layer is workflow state, policy enforcement, and completion discipline rather than static syntax ([Formal Skill, arXiv:2605.19604](https://arxiv.org/abs/2605.19604)). SaP's third limitation concedes the overlap: its bindings are static, so a value the episode produces only at run time stays out of reach.

## Key Takeaways

- The measured gain belongs to the concrete invocation template. Ship the type signature with it, or skip the conversion.
- Convert only where the invocation has a fixed grammar, procedural passages repeat enough to cluster, and arguments bind at index time.
- The four checks make an automatic rewrite acceptable unreviewed, and they report which one failed rather than a score, so a rejection tells you what to fix.
- One library, one benchmark, one agent, one model family. Treat the 82-versus-47 result as a direction, not a number to plan against.
- If your skills encode judgment rather than a call, the prose is doing work a signature cannot replace.

## Related

- [Contractual Skill Files](contractual-skill-files.md) — the same typed-field idea aimed at audit and multi-author review, with no output-quality claim attached
- [Cost-Aware Skill Rewriting](cost-aware-skill-rewriting.md) — why stripping operational anchors raises total cost, and why keeping the template is the anchor that matters here
- [Example-Driven vs Rule-Driven Instructions](example-driven-vs-rule-driven-instructions.md) — the general form of the ablation's finding, that examples anchor and rules generalize
- [Skill Library Technical Debt](../tool-engineering/skill-library-technical-debt.md) — library-time detection over typed contracts, which this conversion step is one way to produce
- [The Instruction Compliance Ceiling](instruction-compliance-ceiling.md) — why adding more declared fields can worsen compliance rather than improve it
