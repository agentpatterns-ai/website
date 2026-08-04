---
title: "Context Hub: On-Demand Versioned API Docs for Coding Agents"
term: "Context Hub"
description: "Fetch current, versioned API documentation into agent context at generation time so agents write against the live spec rather than stale training-data snapshots."
tags:
  - context-engineering
  - cost-performance
  - tool-agnostic
  - rag
aliases:
  - Retrieval-Augmented Agent Workflows
  - Semantic Context Loading
  - JIT Context
  - RAG
  - chub
last_reviewed: 2026-05-27
maturity: established
---

# Context Hub: On-Demand Versioned API Docs for Coding Agents

> Fetch current, versioned API documentation into agent context at generation time so agents write against the live spec rather than stale training-data snapshots.

Related lesson: [Mind the Version Gap](https://learn.agentpatterns.ai/context-engineering/mind-the-version-gap/) covers this concept in a hands-on lesson with quizzes.

!!! info "Also known as"
    Retrieval-Augmented Agent Workflows, Semantic Context Loading, JIT Context, RAG

## The problem: training-time API snapshots

Model weights encode API surfaces from training time. When a library ships breaking changes, adds new endpoints, or deprecates parameters after the training cutoff, agents hallucinate calls against the old spec. Andrew Ng [showed this directly](https://www.deeplearning.ai/the-batch/issue-343/): asked to call a newer model API, agents default to older completion patterns because the current interface did not exist during training.

The failure mode is subtle. Generated code compiles and looks correct, but it targets a deprecated or nonexistent surface. Static documentation in system prompts does not scale, because you cannot preload every API the agent might call.

## Context Hub (chub)

[Context Hub](https://github.com/andrewyng/context-hub) is an open-source npm CLI (`npm install -g @aisuite/chub`) that retrieves current API documentation on demand. The agent calls a shell command before generating code against a specific API. The command injects the live spec into its context window.

### Core commands

| Command | Purpose |
|---------|---------|
| `chub search [query]` | Find available docs across providers |
| `chub get <id> [--lang py\|js]` | Fetch language-specific docs for a provider/endpoint |
| `chub annotate <id> <note>` | Attach persistent local notes to a doc |
| `chub feedback <id> <up\|down>` | Rate doc quality — flows back to maintainers |

A typical agent integration adds one instruction: "Before writing code against an external API, run `chub get <provider>/<endpoint> --lang <lang>` and use the returned documentation."

### How it complements llms.txt

[llms.txt](../geo/llms-txt.md) is a passive, site-level index that tells agents where to find documentation. Context Hub does active, provider-specific retrieval that delivers the documentation content itself. The two work together: `llms.txt` for discovery, `chub get` for on-demand injection.

### Incremental fetching

Docs are stored as markdown with YAML frontmatter, split into multiple reference files per provider. The `--file` flag fetches a single reference selectively; `--full` fetches the complete doc set. This keeps token cost proportional to what the agent actually needs.

## The annotation feedback loop

Context Hub keeps local annotations across sessions. When an agent finds an undocumented quirk or workaround, `chub annotate` records it. On later fetches, annotations surface automatically, so the agent does not rediscover the same issue. As Ng describes it, [agents can "save a note so as not to have to rediscover it from scratch next time"](https://www.deeplearning.ai/the-batch/issue-343/).

Feedback ratings (`chub feedback`) flow upstream to doc maintainers. This closes an improvement loop: real agent usage identifies documentation gaps that maintainers can then fix.

## Private and internal APIs

The same on-demand retrieval pattern applies to proprietary APIs. Because docs are plain markdown with YAML frontmatter, teams can write internal chub-compatible doc sets in the same format and inject them into agent context with the same `chub get` workflow, without submitting them to the public registry.

## Relationship to JIT context loading

Context Hub implements what Anthropic calls [just-in-time context loading](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): it keeps lightweight identifiers (provider names, endpoint IDs) and resolves them to full documentation at runtime rather than preloading everything upfront. This avoids both the staleness of pre-computed embeddings and the token waste of blanket context injection.

## Example

An agent tasked with writing a Python function that calls the OpenAI Chat Completions API runs `chub get openai/chat-completions --lang py` before generating code. The command returns current parameter names, required fields, and deprecation notices as markdown, which the agent reads into its context window. It then generates code against the live spec rather than the training-time snapshot.

If the agent finds that `stream=True` needs explicit iterator handling the docs do not cover, it runs `chub annotate openai/chat-completions "stream=True returns a generator; call next() to advance"`. On the next fetch, the note reappears automatically, so the agent skips re-diagnosing the same quirk.

## When this backfires

On-demand doc retrieval adds a network round-trip before every code-generation step. In latency-sensitive pipelines or offline environments, that is a non-starter. The pattern also needs the agent to have shell tool-calling, so agents confined to pure text completion cannot invoke `chub get`. The public registry [covers roughly 68 providers as of March 2026](https://dev.to/aws/context-hub-has-68-apis-add-yours-33ma); for APIs outside the registry, the agent falls back to training data anyway and gains nothing over the baseline. Finally, teams already running a well-tuned local embeddings-based retrieval system may see only marginal gains, because chub helps most when no other retrieval layer exists.

## FAQ

**How is Context Hub different from llms.txt?**

llms.txt is a passive, site-level index that tells agents where documentation lives; Context Hub does active, provider-specific retrieval that delivers the documentation content itself. The two are complementary rather than competing: agents use llms.txt for discovery, then run `chub get <provider>/<endpoint>` to inject the actual current spec into context in place of a stale training-data snapshot.

**When does Context Hub not help?**

On-demand retrieval adds a network round-trip before every code-generation step, which rules it out for latency-sensitive or offline pipelines, and it requires shell tool-calling, so agents confined to pure text completion cannot invoke `chub get`. The public registry [covers roughly 68 providers as of March 2026](https://dev.to/aws/context-hub-has-68-apis-add-yours-33ma); outside that set, agents fall back to training data and gain nothing over the baseline.

**How does Context Hub keep token cost down when fetching docs?**

Docs are stored as markdown split into multiple reference files per provider, so the `--file` flag pulls a single reference selectively instead of the whole set, while `--full` remains available when the complete doc set is actually needed. This keeps token cost proportional to what the agent actually needs rather than injecting an entire provider's documentation for every call.

## Key Takeaways

- Agents hallucinate API calls when training data predates library changes. On-demand doc retrieval fixes this at generation time, without retraining the model
- `chub get <provider>/<endpoint>` injects current, language-specific API docs into context before code generation
- `chub annotate <id> <note>` records a workaround locally; the annotation surfaces automatically on the next `chub get`, so it never needs rediscovery
- The pattern extends to proprietary APIs: write internal doc sets in the same markdown-with-frontmatter format and fetch them with `chub get`, without submitting them to the public registry

## Related

- [llms.txt: Spec, Adoption, and Honest Limitations](../geo/llms-txt.md)
- [Context Priming](context-priming.md)
- [Retrieval-Augmented Agent Workflows](retrieval-augmented-agent-workflows.md)
- [Seeding Agent Context: Breadcrumbs in Code](seeding-agent-context.md)
- [Semantic Context Loading](semantic-context-loading.md)
- [Context Engineering](context-engineering.md)
- [Layered Context Architecture](layered-context-architecture.md)
- [Context Budget Allocation](context-budget-allocation.md)
- [Discoverable vs Non-Discoverable Context](discoverable-vs-nondiscoverable-context.md)
- [Phase-Specific Context Assembly](phase-specific-context-assembly.md)
- [Structured Domain Retrieval](structured-domain-retrieval.md)
- [Repository-Level Retrieval for Code Generation](repository-level-retrieval-code-generation.md)
- [Environment Specification as Context: Closing the Version Gap](environment-specification-as-context.md)
