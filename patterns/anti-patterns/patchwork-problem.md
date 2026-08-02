---
title: "The Patchwork Problem in LLM-Generated Code"
term: "The Patchwork Problem"
description: "LLM-generated code compiles, passes tests, and clears SAST yet breaks in production because each patch is locally valid but structurally incoherent across the repository."
tags:
  - anti-pattern
  - testing-verification
  - agent-design
  - arxiv
  - tool-agnostic
aliases:
  - structural coherence failures
  - structural incoherence
last_reviewed: 2026-07-13
maturity: emerging
---

# The Patchwork Problem in LLM-Generated Code

> LLM-generated code can compile, pass tests, and clear SAST yet be structurally incoherent — each patch locally valid, the whole globally broken.

The patchwork problem is single-artifact structural incoherence: an LLM emits a change that is locally correct but violates a consistency invariant the rest of the repository already holds. A generated endpoint reads a config key nobody declared. An import targets a package that exists in no registry. A new route drops the authentication guard every sibling endpoint carries. Each patch is plausible on its own, so it passes review that reads it in isolation ([Mothukuri & Parizi, arXiv:2607.08981](https://arxiv.org/abs/2607.08981)).

## What it looks like

The paper formalizes structural coherence as consistency invariants over eight graph views of a repository — import, call, dependency, configuration, schema, resource, control-flow, and routing — and names eight failure categories ([arXiv:2607.08981](https://arxiv.org/abs/2607.08981)):

| Category | The incoherence |
|---|---|
| Symbol resolution (SRF) | A referenced name resolves nowhere in the module graph |
| Phantom internal API (PIA) | A call uses a signature the real declaration does not have |
| Dependency hallucination (DHI) | An import names a package absent from registries and the manifest |
| Build/config incoherence (BCI) | Code assumes environment variables or config never declared |
| Resource coherence (RCF) | A required file, return, or schema is missing |
| Control-flow coherence (CFC) | Unreachable blocks or contradictory conditions |
| Cross-file contract (CCV) | Producer and consumer disagree on a field name or shape |
| Security structural regression (SSR) | A route omits a guard its sibling routes enforce |

## Why standard CI misses it

Type checkers, tests, and SAST reason about local correctness, not repository-scale consistency. In the paper's evaluation, type checking and linting caught 2 of 67 structural findings, test execution caught none, and SAST caught none — the vast majority evaded every baseline ([arXiv:2607.08981](https://arxiv.org/abs/2607.08981)). The risk concentrates in exactly the changes agents are asked to make: cross-cutting tasks failed at about 44.6% versus 13–16% for single-file work.

## Why it works

The mechanism is convention over ground truth. An LLM generates token by token from training-data patterns, not from a symbolic model of the target repository. When wiring a change requires consistency across configuration, middleware, and schema boundaries the model cannot see in context, it emits the plausible continuation (a config key, field name, or method signature that matches naming conventions) instead of one grounded in the repo's actual declarations ([arXiv:2607.08981](https://arxiv.org/abs/2607.08981)). Each token is locally probable, so each patch is locally valid; incoherence only appears at the scale tests and per-file linters never check. The same mechanism produces hallucinated dependencies: one 576,000-sample study found commercial models invent packages in about 5.2% of outputs and open-source models in 21.7% ([Spracklen et al., arXiv:2406.10279](https://arxiv.org/abs/2406.10279)) — names an attacker can register to poison the supply chain ([Socket](https://socket.dev/blog/slopsquatting-how-ai-hallucinations-are-fueling-a-new-class-of-supply-chain-attacks)).

This is distinct from its neighbours. [Shadow tech debt](shadow-tech-debt.md) is cumulative drift across many merged PRs; [assumption propagation](assumption-propagation.md) is a wrong interpretation that solves the wrong problem. The patchwork problem is one artifact's structural break, detectable at generation time by static graph analysis.

## Mitigation

Add repository-scale structural checks that standard CI lacks. The paper's hybrid framework delegates symbol and signature checks to mature static analysis where it already excels, then adds purpose-built detectors for the cross-cutting invariants existing tools underserve — configuration coherence, dependency validation, and cross-file contracts ([arXiv:2607.08981](https://arxiv.org/abs/2607.08981)). Practically: resolve every import against the manifest and registry before merge, diff a new route's guards against its siblings, and validate config keys against the declared schema.

## When this backfires

Repository-graph checking is not free, and the failure it targets is uneven. Skip or scope it down when:

- the codebase is greenfield or throwaway — there is no established structure to be incoherent with;
- the stack is strongly typed and well tooled — a strict TypeScript, Rust, or Java build already surfaces most SRF, PIA, and DHI as compile errors;
- the change is a small single-file diff a reviewer sees whole — the paper's own data puts simple-task failure at 13–16%, so a detector mostly adds triage cost;
- the code is dynamic or loosely typed — graph checks over-approximate on Python and JavaScript and can flood reviewers with false positives, the classic weakness of static analysis, where detectors fail through near-zero recall or overwhelming false positives ([Du et al., arXiv:2601.18844](https://arxiv.org/abs/2601.18844)).

Failure patterns also diverge between models, so a detector tuned on one model's profile under-covers another's ([arXiv:2607.08981](https://arxiv.org/abs/2607.08981)).

## Key Takeaways

- The patchwork problem is code that is locally valid but globally incoherent — undeclared config keys, phantom imports, missing auth guards — and standard CI is nearly blind to it.
- The cause is convention over ground truth: LLMs emit plausible continuations, not repository-grounded ones, so incoherence appears only at repository scale.
- Catch it with repository-scale structural checks: resolve imports against the manifest, diff route guards against siblings, validate config against schema.
- The value is highest on cross-cutting changes in large, dynamically typed repos and lowest on small diffs in strongly-typed, well-tooled stacks.

## Related

- [Shadow Tech Debt](shadow-tech-debt.md)
- [Assumption Propagation: Compounding Agent Misunderstandings](assumption-propagation.md)
- [Happy Path Bias](happy-path-bias.md)
- [Dependency Inlining Erodes SBOM and License Provenance](dependency-inlining-provenance-loss.md)
- [Pattern Replication Risk](pattern-replication-risk.md)
