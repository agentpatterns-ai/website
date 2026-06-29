---
title: "AST-Grounded Critic Loop for Documentation Maintenance"
term: "AST-Grounded Critic Loop"
description: "A documentation-update technique that combines AST-anchored retrieval with a critic-guided Reflexion loop, treating doc-vs-code consistency as a structural verification problem."
tags:
  - agent-design
  - workflows
  - arxiv
  - tool-agnostic
aliases:
  - critic-guided documentation refinement
  - AST-grounded doc maintenance
last_reviewed: 2026-06-12
maturity: emerging
---

# AST-Grounded Critic Loop for Documentation Maintenance

> Constrain doc generation to the code's Abstract Syntax Tree, retrieve only the dependency neighbourhood, and loop a separate critic over the structural diff until convergence.

## The composition

The technique stacks three components that each work as standalone patterns. The novelty is the wiring, not any single piece:

1. AST grounding — parse the source, then extract the symbols, signatures, and dependency edges the doc must describe. This restricts the generator's hypothesis space to nodes in the tree
2. Dependency-aware retrieval — RAG fetches only the AST neighborhood (callers, callees, referenced type definitions), not the whole file or repo
3. Critic-guided Reflexion — a separate model compares the proposed doc against the AST diff between current and previous code, returns a structured rejection when they disagree, and stores that rejection as a verbal lesson for the next attempt

```mermaid
graph TD
    A[Code change] --> B[Parse to AST]
    B --> C[Retrieve dependency neighbourhood]
    C --> D[Generator drafts doc update]
    D --> E[Critic compares doc<br/>against AST diff]
    E -->|Disagree| F[Store verbal lesson]
    F --> D
    E -->|Agree| G[Open PR]
```

This is the architecture proposed in DocSync ([Badrinarayan & Parthasarathy, arXiv:2605.02163](https://arxiv.org/abs/2605.02163)), which reports 3.44/5.0 on an automated judge against 1.91 for a CodeT5-base baseline using a LoRA-adapted small language model. Treat the number as a single-paper claim; no independent replication exists yet.

## Why each layer carries weight

AST grounding addresses factual incorrectness in generated docs. That is one of three failure dimensions (Completeness, Helpfulness, Truthfulness) DocAgent identifies in prior LLM doc generators ([DocAgent, ACL 2025 — arXiv:2504.08725](https://arxiv.org/abs/2504.08725)). A symbol absent from the AST cannot legitimately appear in a doc that claims to describe the file — the same property that motivates [Code-Native Memory Substrates](code-native-memory-substrates.md).

Dependency-aware retrieval (the RAG layer) fills the context window with exactly the code that constrains the doc. Loading the whole module pollutes context; loading nothing forces invention. The AST answers precisely: load the transitively-referenced nodes.

Critic-guided Reflexion is the separation lever. A single model reflecting on its own output rationalizes rather than critiques — the [self-correction blind spot](https://arxiv.org/abs/2507.02778) measures a 64.5% average blind-spot rate across 14 tested LLMs. A critic working on the AST diff (a different artifact than the generator's text) breaks that shared blind spot. The Reflexion layer ([Shinn et al. 2023 — arXiv:2303.11366](https://arxiv.org/abs/2303.11366)) carries the rejected attempt's lesson into the next iteration as a verbal note.

## When to apply

Apply when:

- The codebase has reliable AST tooling for the target language — polyglot stacks need a parser per language
- Documentation drift is frequent and high-cost — API references, function docstrings, README API tables, OpenAPI summaries
- The critic and generator can be different models, or the same model in distinct prompts with non-overlapping context

Avoid when:

- The doc is narrative or conceptual (architectural overviews, tutorials) — there is no AST diff to compare against
- The codebase relies on metaprogramming, code generation, or DSLs the parser sees only partially — structural ground truth is incomplete
- The documentation surface is small or rarely-changes — manual edits beat the infrastructure cost
- The model lacks pre-training exposure to the codebase's proprietary patterns — RAG helps but does not eliminate hallucination the critic cannot judge

## Where it slots into a pipeline

This is a technique, not a workflow. The orchestration layer — schedule triggers, push triggers, safe outputs, PR labeling — belongs to [Continuous Documentation](../workflows/continuous-documentation.md). The technique replaces that workflow's generation step with a critic-guided loop instead of a single-shot LLM call.

The critic role mirrors [Critic Agent Pattern](critic-agent-plan-review.md), specialized for doc-vs-AST-diff comparison. The Reflexion-style memory carries forward like [Self-Rewriting Meta-Prompt Loop](self-rewriting-meta-prompt-loop.md), applied per-file rather than per-prompt.

## Failure modes specific to this composition

Drift-loop churn — stylistic rejection criteria make the generator oscillate between equivalent phrasings without converging. Cap the iteration depth and escalate non-convergence (see [Convergence Detection](../loop-engineering/convergence-detection.md)).

AST coverage gaps that masquerade as agreement — symbols generated by macros, decorators, or runtime metaclasses appear partial or absent in the AST. The critic sees no diff to disagree with, so the loop ends with a doc that misses actual runtime behavior. Track which doc symbols map to AST nodes ([Code-Native Memory Substrates](code-native-memory-substrates.md) mapping), and flag the unresolved ones.

Shared blind spot when critic and generator share a model and prompt — separation needs either a different model or a critic prompt that works on a different artifact (the AST diff, not the doc text). A "review your work" instruction with the same context reproduces the blind-spot rate ([arXiv:2507.02778](https://arxiv.org/abs/2507.02778)).

Reported gains came from a LoRA-adapted small model — the same loop around a generic frontier model without domain adaptation may not reproduce DocSync's headline numbers. The architecture is separable from the parameter-count savings.

## Example

The minimum viable form for a Python codebase:

```python
import ast

def doc_critic_loop(source_file, code_diff, max_iterations=3):
    tree = ast.parse(source_file.read())
    target = locate_changed_function(tree, code_diff)
    neighbourhood = collect_dependencies(tree, target)  # callers, callees, types

    lesson = ""
    for _ in range(max_iterations):
        proposed_doc = generator.draft(
            target=target,
            context=neighbourhood,
            prior_lesson=lesson,
        )
        verdict = critic.evaluate(
            doc=proposed_doc,
            ast_diff=diff_target_against_prior(target),
        )
        if verdict.agrees:
            return proposed_doc
        lesson = verdict.structured_rejection  # verbal note, Reflexion-style

    return None  # escalate to human reviewer
```

The `critic.evaluate` call is the lever — it consumes the AST diff, not the source code, so its judgment is structural rather than textual. The loop ends on agreement or on the iteration cap, never on the generator's self-assessment.

## Key Takeaways

- AST grounding restricts the generator's hypothesis space to symbols that actually exist; RAG limits context to the dependency neighbourhood; the critic operating on AST diffs breaks the same-model blind spot — three separable levers, each with prior evidence
- The Reflexion layer ([Shinn et al. 2023](https://arxiv.org/abs/2303.11366)) carries the rejected attempt's lesson forward; it is the persistence mechanism, not the reasoning mechanism
- DocSync's headline judge score is from a single just-published paper ([arXiv:2605.02163](https://arxiv.org/abs/2605.02163)); no independent replication, no production reports
- The technique is a generation-step replacement inside [Continuous Documentation](../workflows/continuous-documentation.md), not a workflow on its own
- Failure modes — AST coverage gaps, drift-loop churn, shared blind spot when critic and generator share a model and prompt — are addressable but not eliminated by the architecture

## Related

- [Continuous Documentation](../workflows/continuous-documentation.md)
- [Critic Agent Pattern](critic-agent-plan-review.md)
- [Code-Native Memory Substrates](code-native-memory-substrates.md)
- [Evaluator-Optimizer Pattern](evaluator-optimizer.md)
- [Self-Rewriting Meta-Prompt Loop](self-rewriting-meta-prompt-loop.md)
- [Inference-Time Tool-Call Reviewer](inference-time-tool-call-reviewer.md)
