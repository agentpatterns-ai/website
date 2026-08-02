---
title: "Dual Executable Specifications for Long-Horizon Features"
term: "Dual Executable Specifications"
description: "Compile a feature design into architecture and behavior checks that re-run after every edit, so design drift surfaces during the work instead of at review."
tags:
  - testing-verification
  - tool-agnostic
  - arxiv
aliases:
  - executable architecture and behavior specifications
  - architecture spec plus behavior spec
  - functional chain specifications
last_reviewed: 2026-08-02
maturity: emerging
---

# Dual Executable Specifications for Long-Horizon Features

> Executable design checks and a written design plan perform the same on ordinary tasks; the gap opens only past roughly 3,000-word instructions.

A dual executable specification splits a feature design into two machine-checkable halves that run against the repository after every edit: an architecture specification asserting the required components exist and stay connected, and a behavior specification asserting data flows through them correctly. The point is not a better description of the design. It is a design that fails loudly while the agent works, not at review.

## When this earns its cost

The evidence is narrow. Check your task against it before paying for the extra layer.

Reach for it when one feature spans several components and the agent will work for hundreds of turns. FeatureBench is calibrated to that shape: each problem averages 4,800 words of instruction and about 800 lines of valid code. There, compiling the design into executable checks beat the two textual approaches by 14.0 and 15.1 points past 200 agent turns. On instructions of 3,000 to 5,000 words it reached 71.8%, against 43.8% for the same design expressed as text ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)).

Skip it below that line. Under 3,000-word instructions or 120 turns, the same study found executable specifications, textual specifications, and an architecture-first textual baseline performed similarly ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)). Compiling a design you could write in a paragraph is overhead.

Then size the win honestly. Under a DeepSeek-V4-Pro backbone the method passed 70.7%, 55.0%, and 49.9% of fail-to-pass tests on FeatureBench's 30-, 100-, and 200-task splits, against 65.3%, 49.7%, and 46.1% for the strongest baseline. Fully resolved tasks moved far less — 28 against 26 on the 200-task split, with bootstrap standard deviations of ±2.8 ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)). Most of the gain is partial progress, not finished features.

## What the two specifications check

The architecture half turns each step of the intended component path into three assertions: each required unit exists, adjacent units preserve the intended call or dependency relation, and the required data state passes between them. The behavior half derives observable-output, boundary-condition, and state-transition checks at several points along that path, not only at the final output ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)).

If you build only one, build the behavior half. Removing the behavior specification dropped the pass rate from 70.7% to 64.0%; removing the architecture specification dropped it to 66.6%; removing both dropped it to 62.6% ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)). Structural connectivity alone does not guarantee correct outputs, and behavior checks alone still admit incomplete paths.

## Why it works

A plan and a check fail differently under long-horizon pressure, and that difference is the mechanism. A plan is passive context: it competes with every file the agent has since read, grows the input, and gets overlooked as interactions accumulate. A check re-runs after each edit and returns a localized violation — this unit is missing, this relation is broken, this data flow is interrupted — so the agent repairs a named defect instead of re-deriving the whole design ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)).

Neither half is new. The authors build the architecture checks on software reflexion models and static architecture conformance checking, and the behavior checks on property-based, category-partition, and model-based testing ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)). What is new is running both inside the agent's loop rather than at a review gate.

## When this backfires

- Very large repositories. On the greenfield NL2Repo-Bench, the margin over the best baseline was 8.0 points under 1.5K lines of code, 4.3 points from 1.5K to 4K, and 1.1 points above 4K — the last inside error bars of ±4.7 ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)). The advantage shrinks exactly where long-horizon pressure is highest.
- Codebases with no legible conventions. The checks are derived by pairing each requirement with existing design patterns, call relations, and dependencies; removing that grounding cost 5.9 points ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)). A repository with no consistent structure supplies little to pair against.
- Dynamic and reflective code. The architecture half asserts that named units exist and that named relations hold between them ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)). Dependency-injection wiring, runtime registries, and generated code bind at runtime, so there is no static edge for a relation check to match. The paper reports no false-positive rate for its own checks.
- Misread requirements. Both specifications are model-generated from a model-inferred component path, and the method validates neither. When a model [writes a specification from an artifact it may have misread](derived-specification-test-generation.md), 15% to 21% of those specifications carried the original defect forward ([Zhao, Zhou & Cohen, 2026](https://arxiv.org/abs/2607.22883v1)). These checks enforce consistency with a design, never correctness of it.
- Teams that will not retire them. The specifications exist to guide one implementation. Nothing in the method covers their lifecycle afterward, and left in place they fail on legitimate refactors.

## Example

The paper's case study is a distributed-tracing feature in MLflow that required preserving a span lifecycle across several modules. The textual-design agents identified the right entities and still shipped a broken feature: they dispatched spans on `is_recording()` rather than the required OpenTelemetry span type, missed a required cross-module import, and left the OTLP conversion path incomplete, for a 56.7% pass rate ([Wang et al., 2026](https://arxiv.org/abs/2607.26777v1)).

**Before** — the design as a plan the agent holds in context:

```text
"Route spans through the MLflow span factory, then convert to OTLP
 before export. Preserve the span lifecycle across modules."

  -> agent reads this once, implements across ~200 turns
  -> nothing re-reads it; the missing import is never noticed
```

**After** — the same design as checks that re-run against the repository:

```text
Architecture spec:
  CheckUnit(create_mlflow_span)                       -> exists?
  CheckRelation(tracer -> create_mlflow_span, calls)  -> connected?
  CheckDataFlow(span -> otlp_converter, span payload) -> reaches it?

Behavior spec:
  CheckOutput(exported span type)     -> OTel span, not is_recording()
  CheckBoundary(non-recording span)   -> handled, not dropped
  CheckState(span lifecycle)          -> opened and closed once

  -> each edit re-runs both; a break names the unit that broke
```

The difference is not the content of the design. It is that the second form has somewhere to fail.

## Key Takeaways

- The gain is conditional: executable and textual designs performed similarly under 3,000-word instructions or 120 agent turns, and diverged by 14.0 and 15.1 points over the two textual approaches only past 200 turns.
- Under a DeepSeek-V4-Pro backbone the method reached 70.7%, 55.0%, and 49.9% of fail-to-pass tests on FeatureBench, but fully resolved tasks moved only from 26 to 28 on the 200-task split.
- The behavior half carries more weight than the architecture half in ablation — build it first if you build only one.
- The mechanism is localized feedback: a plan is passive context that gets overlooked, a check re-runs after every edit and names what broke.
- The checks are model-generated from a model-inferred path, and nothing validates them, so they enforce consistency with a design rather than correctness of it.
- The advantage narrowed to 1.1 points on repositories above 4K lines of code, inside the reported error bars.

## Related

- [Reverse-Engineered Executable Specifications for Agentic Program Repair](../patterns/multi-agent/reverse-engineered-executable-specifications.md) — the same specification-first split applied to repair, with the spec inferred from failing tests rather than from the feature request
- [Deriving a Specification From Buggy Code Before Generating Tests](derived-specification-test-generation.md) — what to do when the artifact you would compile a spec from is itself the thing under suspicion
- [Spec-Driven Development with Spec Kit](../workflows/spec-driven-development.md) — the textual end of this spectrum: a human-authored Markdown spec as persistent context rather than an executing check
- [Symptom-Reduction-as-Root-Cause: Why Oracle Tests Alone Miss Architectural Drift](symptom-reduction-as-root-cause.md) — the failure this pattern's architecture half targets, seen from the side where only behavior is checked
- [State-Bound Evidence and Typed Revision Contracts for Repair Loops](state-bound-repair-evidence.md) — the adjacent long-loop failure, where evidence detaches from the state that produced it
