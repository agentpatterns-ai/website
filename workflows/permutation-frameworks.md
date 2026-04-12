---
title: "Permutation Frameworks for Batch Code Generation"
description: "Define constrained code templates with shared signatures, then use agents to generate reliable variations at scale — shifting the developer to reviewer."
tags:
  - instructions
---
# Permutation Frameworks for Batch Code Generation

> Define constrained code templates with shared signatures, then use agents to generate reliable variations at scale — shifting the developer role from implementer to reviewer.

## The Pattern

Many codebases contain families of similar features: API endpoints with the same middleware chain, UI components with shared props interfaces, test suites following identical setup/teardown patterns. Implementing each by hand is linear work. A permutation framework defines the shared structure once, then instructs the agent to generate each variation within strict constraints ([Source: ClaudeLog](https://claudelog.com/mechanics/permutation-frameworks/)).

The technique requires investing in constraint definition upfront. Without explicit boundaries, the agent produces inconsistent output across variations — what the ClaudeLog source calls "permutations of slop."

## Building the Framework

A permutation framework has three components:

**1. Reference implementations.** Build several features manually with matching function signatures, file structures, and naming conventions. These serve as concrete examples the agent can pattern-match against. More reference implementations reduce the ambiguity the agent resolves at generation time — each additional example narrows the space of plausible outputs.

**2. Constraint specification.** Define explicitly in your instruction file (CLAUDE.md, copilot-instructions.md, or equivalent):

- The shared function signature or interface each variation must implement
- Which files to create or edit — and which to leave untouched
- Step-by-step implementation sequence
- Naming conventions derived from the variation's parameters

```markdown
## Feature Generation Constraints

Each new filter must:
1. Create `src/filters/{filter-name}.ts` implementing the `Filter` interface
2. Add the filter to the registry in `src/filters/index.ts`
3. Create `src/filters/__tests__/{filter-name}.test.ts` following the pattern in `date-range.test.ts`
4. Do NOT modify any existing filter files
5. Use the filter name as the display label, title-cased
```

**3. Variation parameters.** Provide the list of variations to generate, with any per-variation data the agent needs:

```markdown
Generate filters for:
- `currency` — filters transactions by ISO 4217 currency code
- `merchant-category` — filters by MCC code ranges
- `amount-threshold` — filters transactions above/below a specified amount
```

## Variance as a Diagnostic

Variance across generated permutations is a direct measure of constraint quality. If three generated variations follow different file structures or use different error handling patterns, the constraints are underspecified.

Systematic variance tracking: generate several variations, diff them against each other, and identify where they diverge unnecessarily. Each divergence point maps to a constraint gap. Tighten the constraint, regenerate, and measure again. This iterative loop — generate, measure variance, refine constraints — is the practical refinement process for converging on a stable framework.

## The Role Shift

With a well-defined framework, the developer's work changes:

| Without framework | With framework |
|---|---|
| Write each implementation | Define constraints once |
| Debug each variation individually | Review generated variations for constraint adherence |
| Linear scaling with feature count | Review-limited scaling |

The bottleneck moves from implementation speed to review throughput. This pairs well with [parallel agent sessions](../workflows/parallel-agent-sessions.md) — multiple agents can generate different variations simultaneously, each working from the same constraint specification.

## Why It Works

Explicit constraints narrow the token-level sampling space the model draws from when generating each variation. Without constraints, the model resolves structural ambiguity at generation time — choosing file layout, error handling style, naming patterns — and those choices vary across runs. Constraints pre-resolve those decisions: the model can see from the instruction file and reference implementations which choices are fixed, so it no longer samples freely over them. The result is that structural variance collapses to near zero, leaving only variation-specific logic to differ ([constrained generation research](https://arxiv.org/html/2403.06988v1) shows this mechanism operates at the token-probability level).

## When It Works and When It Breaks

The technique works when:

- Features share a genuine structural pattern (same interface, same file layout, same test shape)
- The variation points are well-defined (a name, a config value, a data type)
- Reference implementations exist and are consistent with each other

It breaks when:

- Variations require fundamentally different logic, not just parameter substitution
- The shared interface is not stable — changing it invalidates all generated variations
- Reference implementations are inconsistent, giving the agent conflicting patterns to follow

## Example

A payments team needs 12 transaction filters, each implementing the same `Filter` interface. They build three by hand — `date-range`, `status`, and `amount` — ensuring identical file structures, test patterns, and registry integration.

Their `CLAUDE.md` constraint specification:

```markdown
## Filter Generation

Reference: src/filters/date-range.ts, src/filters/status.ts, src/filters/amount.ts

Each new filter must:
1. Create `src/filters/{name}.ts` exporting a class implementing `Filter`
2. Constructor accepts `FilterConfig` — no additional constructor params
3. `apply(transactions: Transaction[]): Transaction[]` is the only public method
4. Register in `src/filters/index.ts` — append to the `FILTER_REGISTRY` map
5. Create `src/filters/__tests__/{name}.test.ts` mirroring date-range.test.ts structure
6. Do NOT modify existing filter files
```

Agent prompt for batch generation:

```
Generate filters for the following, using the constraints in CLAUDE.md:
- currency — filters by ISO 4217 code on transaction.currency
- merchant-category — filters by MCC code ranges on transaction.mcc
- card-type — filters by transaction.cardType enum (debit, credit, prepaid)
```

After generating all three, the team diffs them against each other:

```bash
diff src/filters/currency.ts src/filters/merchant-category.ts
diff src/filters/currency.ts src/filters/card-type.ts
```

The diffs show only variation-specific logic differs — file structure, error handling, and test shape are identical. Any unexpected divergence maps to a constraint gap to tighten before the next batch.

## Key Takeaways

- Permutation frameworks trade upfront constraint investment for reliable batch generation — define the template once, generate N variations
- Explicit examples, step definitions, and file-to-edit lists directly reduce output variance across generated permutations
- Measure variance across generated outputs as a diagnostic for constraint quality — divergence points map to constraint gaps
- The developer role shifts from writing implementations to reviewing generated variations and refining constraints
- Pairs with parallel agent sessions for simultaneous variation generation

## Related

- [Example-Driven vs Rule-Driven Instructions](../instructions/example-driven-vs-rule-driven-instructions.md)
- [The Specification as Prompt](../instructions/specification-as-prompt.md)
- [Parallel Agent Sessions](../workflows/parallel-agent-sessions.md)
- [Oracle-Based Task Decomposition](../multi-agent/oracle-task-decomposition.md)
- [Skeleton Projects as Scaffolding](../workflows/skeleton-projects-as-scaffolding.md)
- [Spec-Driven Development](../workflows/spec-driven-development.md)
- [Lay the Architectural Foundation by Hand Before Delegating](../workflows/architectural-foundation-first.md)
