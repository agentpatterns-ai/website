---
title: "Verifier-Driven Parallel Coding Agents (Glite ARF)"
term: "Verifier-Driven Parallel Coding Agents"
aliases:
  - Glite ARF
  - verifier-driven research framework
  - rules-as-failing-code multi-agent contract
description: "Encode the multi-agent research-process rules — task isolation, immutability of completed work, corrections overlay — as deterministic verifier scripts that fail loudly, so per-agent instruction lapses do not compound across parallel coding agents."
tags:
  - multi-agent
  - agent-design
  - testing-verification
  - tool-agnostic
  - arxiv
last_reviewed: 2026-06-29
maturity: emerging
---

# Verifier-Driven Parallel Coding Agents (Glite ARF)

> Encode the multi-agent coordination contract as deterministic verifier scripts that fail loudly, so per-agent lapses do not compound across parallel coding agents.

This pattern applies when three conditions hold: genuine parallelism (many coding agents working concurrently on the same repository), deterministic completion criteria (verifier scripts can check "done" against repository state), and an engineering owner who treats the verifier set as a first-class artifact. Without all three, a simpler single-agent harness with a [pre-completion checklist](../../verification/pre-completion-checklists.md) earns the same correctness at lower cost.

## The inter-agent contract as code

Glite ARF is an open-source Python framework that runs many LLM coding agents (Claude Code, Codex CLI) in parallel on a research repository under a fixed structure, with deterministic Python verifier scripts enforcing the coordination rules ([Philippov et al., 2026](https://arxiv.org/abs/2606.27416)). The framework defines a three-role stack: a human researcher chooses which hypotheses to test, coding agents implement individual tasks, and verifier scripts enforce four invariants ([Philippov et al., 2026](https://arxiv.org/abs/2606.27416)):

- Task isolation — each agent's work is scoped to a defined unit that does not bleed into another agent's territory.
- Immutability of completed work — once a task is closed, agents cannot silently modify it. This is the multi-agent extension of the single-agent [frozen spec](../../instructions/frozen-spec-file.md) discipline, raised to the level of repository state.
- Corrections overlay — fixes to completed work are layered on top of (not into) the original artifact, so the audit trail survives.
- Materialised project overview — a generated read-only view of repository state that any agent can consult without conflicting with concurrent edits.

Each invariant lives in a Python script that fails loudly when an agent violates it. The agents cannot reason around a `sys.exit(1)`.

## Why it works

Per-agent instruction lapses are rare, but in a parallel system they compound. The probability that some agent violates some rule on some step approaches 1 as agents times steps grows, so prose coordination degrades quadratically with scale; verifier scripts short-circuit that scaling because they cost a process exec, not a context-window check ([Philippov et al., 2026](https://arxiv.org/abs/2606.27416)). The mechanism is the same one [deterministic guardrails](../../verification/deterministic-guardrails.md) use inside a single agent — telling an agent "don't break the build" is a prompt, running the build is a guardrail — extended outward to the contract between agents. Reported overhead is roughly 1% of wall-clock across three research campaigns; the verifier checks run fast against repository state and short-circuit before expensive agent work commits, so caught violations amortise the cost ([Philippov et al., 2026](https://arxiv.org/abs/2606.27416)). [Pre-completion checklists](../../verification/pre-completion-checklists.md) supply the same evidence at the per-agent layer; verifier-driven parallel agents apply the same logic at the inter-agent layer.

## How it differs from adjacent patterns

Three nearby patterns overlap in mechanism but not in scope.

| Pattern | Scope | What it gates |
|---|---|---|
| [Deterministic Guardrails](../../verification/deterministic-guardrails.md) | Inside one agent | Output of one agent against rules |
| [Pre-Completion Checklists](../../verification/pre-completion-checklists.md) | Inside one agent | An agent's completion signal |
| [Verify-Gated Completion as Admission Control](verify-gated-completion-admission-control.md) | Between agents | Each individual "done" claim |
| Verifier-driven parallel agents | Between agents | The contract (isolation, immutability, overlay) across all agents |

Admission control is completion-shaped — it admits or rejects one claim. Verifier-driven parallel agents are rule-shaped — they hold the cross-agent invariants regardless of which completion is happening, much like a database holds ACID properties regardless of which transaction is running.

## When this backfires

The verifier layer earns its overhead under specific conditions. Skip it or treat the rules as prompt-level guidance when:

- One agent, not many. Task isolation and immutability of completed work are vacuous with a single worker. A [pre-completion checklist](../../verification/pre-completion-checklists.md) plus a [frozen spec](../../instructions/frozen-spec-file.md) hits the same correctness target without the inter-agent contract.
- "Done" is a judgement call, not observable state. Verifier scripts must pass or fail on git diffs, file contents, or test exit codes. For literature review, hypothesis ranking, or design critique the verifier collapses into a stamp and the same warning [admission-control verifiers](verify-gated-completion-admission-control.md) raise about advisory-verifier promotion applies.
- Research scope churns faster than completion edges. Immutability of completed work assumes the completion boundary is stable. If the question itself keeps mutating, the corrections overlay grows faster than the materialised overview can absorb and the framework becomes a write-shaped object behind read-only semantics.
- No engineering owner for the verifier set. Each new process rule needs a verifier script that survives agent attempts to route around it. Without an owner who treats the scripts as a first-class artifact (test coverage, versioning, regression checks), the verifier layer rots into a placebo — the same risk [deterministic guardrails](../../verification/deterministic-guardrails.md) flags at the single-agent layer.
- Verifier-rule precision is unmeasured. The cited deployment does not report blocked-precision on rule violations. An enforcing rule whose precision is low mostly blocks valid work; deployed admission-control verifiers have reported 0.39% blocked precision in adjacent settings ([Nguyen & Tran, 2026](https://arxiv.org/abs/2605.17998)). Measure before promoting an advisory rule to enforcing.
- Multi-agent overhead exceeds single-agent gain. The general multi-agent caveat applies. The [Multi-Agent System Failure Taxonomy (MAST)](https://arxiv.org/abs/2503.13657) finds that across surveyed benchmarks, multi-agent performance gains are often minimal and inter-agent misalignment is a leading failure category. Verifier-driven coordination addresses misalignment within rules; it does not address the prior question of whether parallel agents beat one capable agent on this workload.

## Example

In the cited deployment, the framework coordinated up to twelve parallel agents across 273 tracked tasks in 129 feature sets for roughly $450 in API costs, with verifier scripts adding about 1% wall-clock overhead ([Philippov et al., 2026](https://arxiv.org/abs/2606.27416)). Applied to the BEA 2026 vocabulary-difficulty shared task, the system finished first on the closed track and second on the open track across three languages, reducing the official baseline RMSE by 29.9% (closed) and 35.9% (open) ([Philippov et al., 2026](https://arxiv.org/abs/2606.27416)).

The reported wall-clock figure is the load-bearing number for adoption: a 1% overhead is cheap, so the question is not "is the verifier layer too expensive?" but "do my conditions support it?" — the parallelism, deterministic criteria, and maintainer ownership called out above.

## Key Takeaways

- The pattern moves the multi-agent coordination contract from prose instructions into Python scripts that fail loudly on violation — the inter-agent extension of [deterministic guardrails](../../verification/deterministic-guardrails.md).
- Four invariants carry the contract: task isolation, immutability of completed work, corrections overlay, materialised project overview.
- Reported overhead is ~1% of wall-clock; the cost gate is engineering ownership of the verifier set, not runtime.
- Verifier-driven parallel agents are rule-shaped, not completion-shaped — unlike [admission control](verify-gated-completion-admission-control.md), the invariants hold across all agents regardless of which claim is in flight.
- Skip the pattern when work is single-agent, completion is a judgement call, scope churns, no owner exists, or rule precision is unmeasured — a [pre-completion checklist](../../verification/pre-completion-checklists.md) plus a [frozen spec](../../instructions/frozen-spec-file.md) covers the single-agent case at lower cost.

## Related

- [Verify-Gated Completion as Admission Control](verify-gated-completion-admission-control.md) — the per-completion external-verifier sibling; this page is the rule-set generalisation across all agents
- [Deterministic Guardrails Around Probabilistic Agents](../../verification/deterministic-guardrails.md) — the single-agent precedent; verifier-driven parallel agents extend the mechanism to the inter-agent contract
- [Pre-Completion Checklists for AI Agent Development](../../verification/pre-completion-checklists.md) — the single-agent verification gate; covers the case where one agent suffices
- [Frozen Spec File](../../instructions/frozen-spec-file.md) — single-agent immutability; this page raises immutability to completed work across many agents
- [Multi-Agent Topology Taxonomy: Centralised, Decentralised, and Hybrid](multi-agent-topology-taxonomy.md) — choosing the right coordination structure; verifier-driven contracts are an architectural choice within decentralised topologies
- [File-Based Agent Coordination](file-based-agent-coordination.md) — a complementary low-mechanism coordination layer using git locks; verifier scripts can sit on top
