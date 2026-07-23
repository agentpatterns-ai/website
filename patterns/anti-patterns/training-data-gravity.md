---
title: "Training-Data Gravity: Agents Default to Deprecated APIs"
term: "Training-Data Gravity"
description: "LLM coding agents prefer deprecated APIs, old CLI flags, and superseded libraries because pretraining-corpus frequency outweighs current docs; current-information injection only partially overrides the prior."
aliases:
  - training-corpus gravity
  - training-data recency lag
  - deprecated-API prior
tags:
  - anti-pattern
  - agent-design
  - tool-agnostic
last_reviewed: 2026-06-28
maturity: established
---

# Training-Data Gravity: Agents Default to Deprecated APIs

> Coding agents reach for deprecated APIs because pretraining-corpus frequency outweighs current docs; injecting current information narrows the gap but never closes it.

## The pattern

Coding agents ship stale code confidently — `GenerativeModel()` instead of the current `google-genai` client, `npx create-react-app` instead of Vite, an `aws s3api` flag retired two releases ago, a Pydantic v1 `@validator` inside a v2 project. The agent is not guessing. It is sampling from a prior where the old API has years of Stack Overflow answers and the replacement has a handful of release notes ([Microsoft for Developers, 'Competing Against Yourself', 2026](https://developer.microsoft.com/blog/competing-against-yourself)).

This is distinct from three adjacent failures. It is not [Boring Technology Bias](boring-technology-bias.md), which is recommendation bias when you ask "what should I use?" — gravity fires even when the choice is implicit. It is not [Pattern Replication Risk](pattern-replication-risk.md), where the bias comes from in-repo examples. It is not [Unversioned Scaffolding Commands Pull Stale Templates](unversioned-scaffolding-stale-templates.md), a resolver fallback at scaffold time. Training-data gravity is generation-time bias on every call, with no codebase context, no scaffolder, and no recommendation question required.

## The failure surface

- Deprecated APIs. One study evaluated seven LLMs over 145 API mappings from eight popular Python libraries and 28,125 completion prompts. Every model struggled to avoid deprecated-API usage, which the authors attribute to deprecated examples in the training data and the absence of deprecation knowledge ([Wang et al., ICSE'25, arxiv 2406.09834](https://arxiv.org/abs/2406.09834)).
- Version-specific idioms. GitChameleon 2.0 (328 Python completion problems conditioned on library version) puts enterprise frontier models at only 48% to 51% baseline success ([Misra et al., arxiv 2507.12367](https://arxiv.org/abs/2507.12367)).
- Superseded libraries with generic names. Semantic collapse happens when a replacement reuses a generic label ("v2 CLI", "the new client"): the model folds it into the predecessor's concept and picks the one with more training signal. Distinctively named replacements (Vite, Bun, Deno, Astro) carve their own slot and avoid the collision ([Microsoft for Developers, 2026](https://developer.microsoft.com/blog/competing-against-yourself)).

## Why it works (the mechanism)

Each generation samples from the model's pretrained conditional distribution, which relative frequency in the pretraining corpus dominates. A decade-old API with thousands of Stack Overflow answers gets more probability mass than a one-year-old replacement, even when training-time docs named the old API deprecated ([Wang et al., 2024](https://arxiv.org/abs/2406.09834)). Prompt conditioning shifts the distribution only within the support the prior already assigns non-trivial mass, and the context-memory conflict finding measures the residual. Across 270 real-world API updates over 8 Python libraries and 11 models in 4 families, only 42.55% of generations executed without good docs in context; structured docs plus larger models raised that to 66.36% — not 100% ([Ashik et al., arxiv 2604.09515](https://arxiv.org/abs/2604.09515)). The reasoning trace shows the mechanism plainly: agents consider the new option, weigh the evidence, and still decide for the established one — "I'm wondering if a standalone CLI tool has been released, but the standard approach remains using \[established tool\]" ([Microsoft for Developers, 2026](https://developer.microsoft.com/blog/competing-against-yourself)). It is the same prior-amplification shape documented for optimization loops in [Prior Dominance Over Feedback](prior-dominance-over-feedback.md): feedback refines within the prior's support, it does not replace it. There is also a timing dimension: the agent often commits to a plan from its training priors at the moment it receives the task — *before* it reads the relevant docs — so sharpening doc clarity is the wrong lever, because the doc is consulted only after the plan already exists ([Microsoft for Developers, 'Your Agent Already Has a Plan', 2026](https://developer.microsoft.com/blog/your-agent-already-has-a-plan)).

## Counter-measures

Three controls reduce the bias. Each one shifts the conditional distribution at generation time rather than hoping the model overrides itself.

- Inject current docs at the call site. RAG against the library's current API reference improves LLM performance on less-common libraries by 83% to about 220%, and example code contributes more than descriptive text or parameter lists ([When LLMs Meet API Documentation, arxiv 2503.15231](https://arxiv.org/abs/2503.15231)). Pin docs into the harness's retrieval surface for every library the project uses; relying on the model's parametric knowledge is the failure mode.
- Encode deprecations as machine-readable steering. Add explicit "DEPRECATED: Do not use X. Use Y instead" rules to the project's [instruction file ecosystem](../../instructions/instruction-file-ecosystem.md) for every replacement the team cares about. The Microsoft writeup makes this the load-bearing control for newly released tools ([Microsoft for Developers, 2026](https://developer.microsoft.com/blog/competing-against-yourself)).
- Validate after generation. A linter, type checker, or pre-commit hook that flags known-deprecated calls catches the residual cases that retrieval and steering miss. APILOT — a system that keeps a continuously updated outdated-API dataset and gates generation against it — reduces outdated-code recommendations by 89.42% on average while improving usability by 27.54% ([Bai et al., arxiv 2409.16526](https://arxiv.org/abs/2409.16526)). The point is that the deprecated-API set has to be a live artifact, not a frozen rule pack.

## When this backfires

Counter-measures cost prompt budget, docs maintenance, and pre-commit latency. They are wasted or net-negative when:

- APIs are stable and slow-moving. POSIX, standard SQL, and BSD sockets — the popular pattern is the current pattern. Steering for an API that has not changed in a decade ages the prompt for no benefit.
- The replacement has a distinctive name and its own training mass. Bun, Deno, Vite, and Astro carved their own conceptual slot at launch; the model picks them unprompted, so explicit "prefer X over Y" steering becomes dead weight ([Microsoft for Developers, 2026](https://developer.microsoft.com/blog/competing-against-yourself)).
- The downstream verifier is fast and complete. When you run the code immediately and a failing call surfaces in a test or runtime error within one round, the gravity matters only when nothing re-checks.
- The codebase is internal or proprietary. A DSL the model has never seen has no prior to fight — example coverage matters, anti-gravity steering does not.
- Pinning the entire stack is a category error. As [Boring Technology Bias](boring-technology-bias.md) §When This Backfires notes, blanket pinning trades selection bias for lock-in and stale guidance. Steer the specific deprecation transitions the team cares about; do not pin every dependency.

## Example

Before — relying on the model's parametric knowledge:

```python
# Prompt: "Call Gemini to summarise this document."
import google.generativeai as genai

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")
response = model.generate_content(text)
```

The `google-generativeai` package was superseded by `google-genai`, but the `GenerativeModel()` pattern still dominates training-data examples ([googleapis/python-genai#1606](https://github.com/googleapis/python-genai/issues/1606), via [Boring Technology Bias](boring-technology-bias.md)). The call executes, but the project is now coupled to a deprecated client and the agent will reproduce the pattern in every new file it touches.

After — current docs injected, deprecation made explicit, validator on the path:

```markdown
# AGENTS.md (project root)

## Deprecations

- DEPRECATED: `google.generativeai` (the `google-generativeai` package). Use `google.genai` (the `google-genai` package) instead — see https://googleapis.github.io/python-genai/.
- DEPRECATED: `GenerativeModel()`. Use `genai.Client().models.generate_content(...)`.
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: no-deprecated-genai
        name: Block deprecated google-generativeai imports
        language: pygrep
        entry: 'import google\.generativeai|from google\.generativeai'
        types: [python]
```

The three controls compose: current docs in the harness's retrieval, an explicit deprecation rule the agent reads on every turn, and a deterministic gate that fails the commit when the prior leaks through anyway.

## Key Takeaways

- Pretraining-corpus frequency dominates the model's conditional distribution over APIs and tools; the bias fires on every generation, not only on recommendation prompts ([Wang et al., 2024](https://arxiv.org/abs/2406.09834); [Microsoft for Developers, 2026](https://developer.microsoft.com/blog/competing-against-yourself)).
- Current-information injection narrows the gap — RAG over API docs improves performance 83–220% — but context-memory conflict means the prior still leaks; executable rates plateau around 66% even with structured docs and larger models ([Ashik et al., arxiv 2604.09515](https://arxiv.org/abs/2604.09515); [arxiv 2503.15231](https://arxiv.org/abs/2503.15231)).
- The three load-bearing counter-measures compose: inject current docs at the call site, encode deprecations as machine-readable steering, validate after generation against a *live* outdated-API set ([APILOT, arxiv 2409.16526](https://arxiv.org/abs/2409.16526)).
- *Semantic collapse* — generic replacement names colliding with the predecessor's concept — amplifies the bias; distinctive names (Vite, Bun, Deno) avoid it at design time ([Microsoft for Developers, 2026](https://developer.microsoft.com/blog/competing-against-yourself)).

## Related

- [Boring Technology Bias](boring-technology-bias.md) — Sibling failure: bias toward *popular* tools when asked to recommend; training-data gravity covers the same prior at *generation* time, on every call.
- [Pattern Replication Risk](pattern-replication-risk.md) — In-repo examples amplify whatever pattern the codebase contains; compounds training-data gravity once a deprecated call lands.
- [Prior Dominance Over Feedback](prior-dominance-over-feedback.md) — The same prior-amplification shape inside propose-evaluate-revise loops: feedback refines within the prior's support, it does not replace it.
- [Unversioned Scaffolding Commands Pull Stale Templates](unversioned-scaffolding-stale-templates.md) — Adjacent staleness mode at *scaffold* time via the npm resolver, distinct from the always-on generation-time bias here.
- [Stale AI Configuration Artifacts (Context Rot)](stale-ai-configuration-artifacts.md) — The companion failure on the steering side: if the deprecation rules themselves drift, the counter-measure stops working.
- [Grounding Agents in Code the Model Has Never Seen](../../context-engineering/grounding-zero-prior-code.md) — Sibling at the opposite end of the prior spectrum: zero training mass at all, so the model collapses to the closest public API rather than an outdated one.
- [Emulate Agent-Experience Changes Before Shipping](../../verification/emulate-ax-changes-before-shipping.md) — The verification technique that surfaces this gravity empirically: emulate a doc change and measure whether it actually moves agent behavior before shipping it.
</content>
</invoke>
