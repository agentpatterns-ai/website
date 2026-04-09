---
title: "Context Hub: On-Demand Versioned API Docs for Coding Agents"
description: "Fetch current, versioned API documentation into agent context at generation time so agents write against the live spec rather than stale training-data"
tags:
  - context-engineering
  - cost-performance
aliases:
  - Retrieval-Augmented Agent Workflows
  - Semantic Context Loading
  - JIT Context
  - RAG
  - chub
---

# Context Hub: On-Demand Versioned API Docs for Coding Agents

> Fetch current, versioned API documentation into agent context at generation time so agents write against the live spec rather than stale training-data snapshots.

!!! info "Also known as"
    Retrieval-Augmented Agent Workflows, Semantic Context Loading, JIT Context, RAG

## The Problem: Training-Time API Snapshots

Model weights encode API surfaces from training time. When a library ships breaking changes, adds new endpoints, or deprecates parameters after the training cutoff, agents hallucinate calls against the old spec. Andrew Ng [demonstrated this directly](https://www.deeplearning.ai/the-batch/issue-343/) — when asked to call a newer model API, agents default to older completion patterns because the current interface did not exist during training.

The failure mode is subtle: generated code compiles and looks correct but targets a deprecated or nonexistent surface. Static documentation in system prompts does not scale — you cannot preload every API the agent might call.

## Context Hub (chub)

[Context Hub](https://github.com/andrewyng/context-hub) is an open-source npm CLI (`npm install -g @aisuite/chub`) that retrieves current API documentation on demand. The agent calls a shell command before generating code against a specific API, injecting the live spec into its context window.

### Core Commands

| Command | Purpose |
|---------|---------|
| `chub search [query]` | Find available docs across providers |
| `chub get <id> [--lang py\|js]` | Fetch language-specific docs for a provider/endpoint |
| `chub annotate <id> <note>` | Attach persistent local notes to a doc |
| `chub feedback <id> <up\|down>` | Rate doc quality — flows back to maintainers |

A typical agent integration adds one instruction: *"Before writing code against an external API, run `chub get <provider>/<endpoint> --lang <lang>` and use the returned documentation."*

### How It Complements llms.txt

[llms.txt](../geo/llms-txt.md) is a passive, site-level index — it tells agents where to find documentation. Context Hub is active, provider-specific retrieval — it delivers the documentation content itself. The two compose naturally: `llms.txt` for discovery, `chub get` for on-demand injection.

### Incremental Fetching

Docs are stored as markdown with YAML frontmatter, split into multiple reference files per provider. The `--file` flag fetches a single reference selectively; `--full` fetches the complete doc set. This keeps token cost proportional to what the agent actually needs.

## The Annotation Feedback Loop

Context Hub persists local annotations across sessions. When an agent discovers an undocumented quirk or workaround, `chub annotate` records it. On subsequent fetches, annotations surface automatically — the agent does not rediscover the same issue. As Ng describes it: [agents can "save a note so as not to have to rediscover it from scratch next time"](https://www.deeplearning.ai/the-batch/issue-343/).

Feedback ratings (`chub feedback`) flow upstream to doc maintainers, creating an improvement loop where real agent usage identifies gaps in documentation.

## Private and Internal APIs

The pattern generalizes beyond public providers. Teams with proprietary or fast-moving internal APIs can host a chub-compatible doc repository — the same markdown-with-frontmatter format, served from a private registry. This gives internal agents the same on-demand retrieval without exposing proprietary surfaces publicly [unverified].

## Relationship to JIT Context Loading

Context Hub implements what Anthropic calls [just-in-time context loading](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — maintaining lightweight identifiers (provider names, endpoint IDs) and resolving them to full documentation at runtime rather than preloading everything upfront. This avoids both the staleness of pre-computed embeddings and the token waste of blanket context injection.

## Example

An agent tasked with writing a Python function that calls the OpenAI Chat Completions API runs `chub get openai/chat-completions --lang py` before generating code. The command returns current parameter names, required fields, and deprecation notices as markdown, which the agent reads into its context window. It then generates code against the live spec rather than the training-time snapshot.

If the agent discovers that `stream=True` requires explicit iterator handling not covered in the docs, it runs `chub annotate openai/chat-completions "stream=True returns a generator; call next() to advance"`. On the next fetch, this annotation surfaces automatically -- no need to rediscover the quirk.

## Key Takeaways

- Agents hallucinate API calls when training data predates library changes — on-demand doc retrieval solves this at generation time rather than retraining
- `chub get <provider>/<endpoint>` injects current, language-specific API docs into context before code generation
- Annotations persist locally and surface on re-fetch, preventing agents from rediscovering known workarounds
- The pattern generalizes to private APIs via self-hosted chub-compatible doc repositories

## Unverified Claims

- Teams with proprietary APIs can host a chub-compatible doc repository for internal agents [unverified]

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
