---
title: "Shared Agent Context Store API: When to Expose Curated Context as an Endpoint"
term: "Shared Agent Context Store API"
description: "Use an API-backed shared context store only when the writer is a system, ingestion is controlled, and the team accepts retrieval-time selection over deterministic reads."
tags:
  - agent-design
  - memory
  - copilot
last_reviewed: 2026-06-12
maturity: adopted
---

# Shared Agent Context Store API: When to Expose Curated Context as an Endpoint

> Use an API-backed shared context store only when the writer is a system, ingestion is controlled, and the team accepts retrieval-time selection over deterministic reads.

A shared agent context store API is a programmatic CRUD interface over a team-scoped, retrieval-grounded knowledge bundle that agents and humans both read from. The first shipped instance is the [Copilot Spaces REST API, GA on 2026-05-18](https://github.blog/changelog/2026-05-18-copilot-spaces-api-now-generally-available/) — it exposes the same Spaces a human curates in the GitHub UI ([reference](https://docs.github.com/en/rest/copilot-spaces/copilot-spaces)) so CI jobs, sub-agents, and orchestrators can create, update, and attach resources at runtime. The pattern generalizes to any tool shipping an API alongside a curated context surface.

## When to apply

Apply this pattern only when all of the following hold:

- The writer is a system, not a person. CI publishes release notes, a reviewer agent posts decisions, an orchestrator seeds sub-agent context. If the only writer is a human, a version-controlled repo file like AGENTS.md is simpler.
- Ingestion is controlled. Inputs are first-party artifacts — your own CI output or agent transcripts — not auto-attached untrusted content like external issue bodies or webhook payloads.
- Retrieval-time selection is acceptable. Readers take a relevant subset per query, not a deterministic full read. Copilot Chat only processes a portion of a Space per response ([Responsible use of Copilot Spaces](https://docs.github.com/en/copilot/responsible-use/copilot-spaces)).
- Vendor-hosted is acceptable. The team is on GitHub and needs neither airgapped operation nor point-in-time reproducibility — auto-syncing sources mean the same query can return a different answer tomorrow ([concept docs](https://docs.github.com/en/copilot/concepts/context/spaces)).

If any condition fails, prefer a file-based shared context surface ([AGENTS.md](../instructions/agents-md-distributed-conventions.md), pinned repo docs) and stop here.

## How it differs from file-based shared context

| Surface | Read mechanism | Write mechanism | Trifecta posture |
|---------|---------------|-----------------|------------------|
| `AGENTS.md` / `CLAUDE.md` / repo docs | Deterministic file read | Human PR | Closed by default |
| [Per-agent memory](agent-memory-patterns.md) | Auto-loaded by harness | Agent-authored, scoped | Closed within agent |
| API-backed shared context store | Retrieval-grounded (RAG) | Any authenticated principal | Open unless inputs are controlled |
| Ad-hoc chat context | Per-message | Per-message | Closed |

Files give reproducibility and offline operation; the API gives runtime mutability, multi-writer concurrency, and per-viewer RBAC. It adds a second surface to keep in sync, not a replacement.

## How it works

The API changes the producer/consumer topology of the index, not what the store does. A Space stays a curated bundle of repos, files, PRs, issues, notes, and uploads grounded through retrieval-augmented generation: sources are indexed, the top-k passages for a prompt are retrieved, and only those reach the model ([GitHub Blog: RAG](https://github.blog/ai-and-ml/generative-ai/what-is-retrieval-augmented-generation-and-what-does-it-do-for-generative-ai/), [Copilot Spaces concept](../tools/copilot/copilot-spaces.md)).

It exposes full CRUD at user and org scope — `GET/POST /orgs/{org}/copilot-spaces`, `GET/PATCH/DELETE` per space, plus a resources sub-endpoint for attaching repos, files, issues, PRs, and notes ([API ref](https://docs.github.com/en/rest/copilot-spaces/copilot-spaces), [awesome-copilot skill](https://github.com/github/awesome-copilot/blob/main/skills/copilot-spaces/SKILL.md)). Classic PATs need `read:org` to list; fine-grained tokens and Apps need grants on the owning org and *every repository referenced by Space resources*.

## Why it works

The API drops the manual sync step without changing retrieval: indexed sources still drive the prompt, but the index updates as the system runs. Anthropic's guidance for long-running agents recommends sharing state through external, addressable artifacts so agents and humans read and write the same context without re-deriving it each session ([Anthropic: harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)); Manus reports the same — a programmable context store lets sub-processes converge without thrash ([Manus: context engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)).

## When this backfires

- Single-repo teams already on `AGENTS.md`. A pinned repo file plus existing agent memory covers their shared context; the API adds a second source of truth with no offsetting model-behavior change.
- High-write workflows hit undocumented quotas. Capacity is enforced on indexed semantic content (tokens/embeddings), not file size, and GitHub has not published the limits. Community reports describe a progress bar passing 100% with ~185 small files ([community discussion #182622](https://github.com/orgs/community/discussions/182622)), after which the Space hard-errors — "You've exceeded the size limit for this space. Remove some references to continue." — and blocks further writes until a human removes references. CI that appends every release note eventually fails its write step rather than degrading silently.
- Mixed-permission audiences produce divergent answers. RBAC is enforced per viewer even on shared and public Spaces ([GitHub Changelog, Dec 2025](https://github.blog/changelog/2025-12-01-copilot-spaces-public-spaces-and-code-view-support/)). Two readers asking the same question receive different effective context — a reproducibility hazard for a decision record.
- Untrusted ingestion closes a [lethal trifecta](../security/lethal-trifecta-threat-model.md). If the API attaches external issue bodies, third-party PR descriptions, or webhook payloads, every later reader carries private repo data, untrusted content, and a write-capable token in one context — the classic prompt-injection loop ([Prompt Injection Threat Model](../security/prompt-injection-threat-model.md)).
- Airgapped or non-GitHub regimes. Spaces are GitHub-hosted ([Copilot Spaces page](../tools/copilot/copilot-spaces.md)), so the API is unavailable there; auto-syncing sources also mean the same Space returns different answers over time without a code change, disqualifying it as a compliance system of record.

## Example

A reviewer-agent workflow seeds its sub-agents from a curated Space, and a CI job appends post-release decisions back into the same Space:

```yaml
# .github/workflows/post-release-context.yml
name: post-release-context
on:
  release:
    types: [published]
jobs:
  update-space:
    runs-on: ubuntu-latest
    steps:
      - name: Append release decision to shared Space
        env:
          GH_TOKEN: ${{ secrets.SPACES_BOT_TOKEN }}   # fine-grained, scoped to one Space
        run: |
          gh api -X PATCH \
            /orgs/acme/copilot-spaces/42/resources \
            -f kind=note \
            -f title="Release ${{ github.event.release.tag_name }} — decisions" \
            -f content="$(cat .release-notes/${{ github.event.release.tag_name }}.md)"
```

The note is first-party content the team already produces — not external issue text. The token is fine-grained, scoped to one Space, and cannot read unrelated repos. Reviewer agents pick up the new release context on the next query without a human updating an `AGENTS.md`. If the Space hits its semantic budget, the `PATCH` fails with a size-limit error and the write step goes red — the escape valve is a human pruning old references, not silent degradation ([community #182622](https://github.com/orgs/community/discussions/182622)).

Contrast with the wrong shape:

```yaml
# Wrong — auto-attaches every external issue body into a shared Space
- name: Mirror inbound issues into Space
  run: |
    gh issue list --state open --json body --jq '.[].body' |
      gh api -X PATCH /orgs/acme/copilot-spaces/42/resources -f kind=note -f content=@-
```

External issue bodies are untrusted input; mirroring them gives every later reader — including agents with write access elsewhere — a prompt-injection surface no human reviewed.

## Key Takeaways

- The API changes *who can write the index*, not how retrieval works — apply only when the writer is a system whose updates a human currently makes by hand.
- File-based shared context (`AGENTS.md`, repo docs) remains the default for human-authored, version-controlled, offline-capable team context.
- Treat the write endpoint as a trifecta gate: control what gets attached, scope tokens to one Space, and never auto-ingest untrusted content.
- Accept that retrieval-grounded reads are non-deterministic, and that hitting the semantic budget hard-errors writes until a human prunes references — do not use a Space as a system of record requiring point-in-time reproducibility.

## Related

- [Copilot Spaces: Curated Context Collections for Grounding](../tools/copilot/copilot-spaces.md)
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md)
- [Externalization in LLM Agents: Memory, Skills, Protocols, and Harness](externalization-in-llm-agents.md)
- [File-Based Agent Coordination](../multi-agent/file-based-agent-coordination.md)
- [AGENTS.md as Distributed Conventions](../instructions/agents-md-distributed-conventions.md)
