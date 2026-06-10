---
title: "Shared Agent Context Store API: When to Expose Curated Context as an Endpoint"
term: "Shared Agent Context Store API"
description: "Use an API-backed shared context store only when the writer is a system, ingestion is controlled, and the team accepts retrieval-time selection over deterministic reads."
tags:
  - agent-design
  - memory
  - copilot
last_reviewed: 2026-06-02
---

# Shared Agent Context Store API: When to Expose Curated Context as an Endpoint

> Use an API-backed shared context store only when the writer is a system, ingestion is controlled, and the team accepts retrieval-time selection over deterministic reads.

A shared agent context store API is a programmatic CRUD interface over a team-scoped, retrieval-grounded knowledge bundle that agents and humans both read from. The first major shipped instance is the [Copilot Spaces REST API, GA on 2026-05-18](https://github.blog/changelog/2026-05-18-copilot-spaces-api-now-generally-available/) — it exposes the same Spaces a human curates in the GitHub UI ([reference](https://docs.github.com/en/rest/copilot-spaces/copilot-spaces)) so CI jobs, sub-agents, and orchestrators can create, update, and attach resources at runtime. The pattern generalises to any tool that ships an API alongside a curated context surface.

## When to Apply

Apply this pattern only when **all** of the following hold:

- **The writer is a system, not a person.** CI publishes release notes, a reviewer agent posts decisions, an orchestrator seeds sub-agent context. If the only writer is a human, a version-controlled repo file is simpler and reviewable.
- **Ingestion is controlled.** Inputs are first-party artifacts — your own CI output, your own agent transcripts — not auto-attached untrusted content like external issue bodies or webhook payloads.
- **Retrieval-time selection is acceptable.** Readers will take a relevant *subset* per query, not a deterministic full read. Copilot Chat only processes a portion of a Space per response ([Responsible use of Copilot Spaces](https://docs.github.com/en/copilot/responsible-use/copilot-spaces)).
- **Vendor-hosted is acceptable.** The team is on GitHub and needs neither airgapped operation nor point-in-time reproducibility — auto-syncing sources mean the same query can return a different answer tomorrow ([concept docs](https://docs.github.com/en/copilot/concepts/context/spaces)).

If any condition fails, prefer a file-based shared context surface ([AGENTS.md](../instructions/agents-md-distributed-conventions.md), pinned repo docs) and stop here.

## How It Differs From File-Based Shared Context

| Surface | Read mechanism | Write mechanism | Trifecta posture |
|---------|---------------|-----------------|------------------|
| `AGENTS.md` / `CLAUDE.md` / repo docs | Deterministic file read | Human PR | Closed by default |
| [Per-agent memory](agent-memory-patterns.md) | Auto-loaded by harness | Agent-authored, scoped | Closed within agent |
| **API-backed shared context store** | **Retrieval-grounded (RAG)** | **Any authenticated principal** | **Open unless inputs are controlled** |
| Ad-hoc chat context | Per-message | Per-message | Closed |

Files give reproducibility and offline operation; the API gives runtime mutability, multi-writer concurrency, and per-viewer RBAC. It does not replace the file — it adds a second surface the team keeps in sync.

## How It Works

The API does not change *what* the context store does — it changes the producer/consumer topology of the underlying index. A Space remains a curated bundle of repos, files, PRs, issues, notes, and uploads that grounds responses through retrieval-augmented generation: sources are indexed, the top-k most relevant passages for a prompt are retrieved, and only those passages reach the model's context window ([GitHub Blog: RAG](https://github.blog/ai-and-ml/generative-ai/what-is-retrieval-augmented-generation-and-what-does-it-do-for-generative-ai/), [Copilot Spaces concept](../tools/copilot/copilot-spaces.md)).

The API exposes full CRUD at user and org scope — `GET/POST /orgs/{org}/copilot-spaces`, `GET/PATCH/DELETE` per space, plus a resources sub-endpoint for attaching repos, files, issues, PRs, and notes ([API ref](https://docs.github.com/en/rest/copilot-spaces/copilot-spaces), [awesome-copilot skill](https://github.com/github/awesome-copilot/blob/main/skills/copilot-spaces/SKILL.md)). Classic PATs need `read:org` to list; fine-grained tokens and GitHub Apps must hold grants on the owning org and *every repository referenced by Space resources*.

## Why It Works

When the writer is a system whose output a human maintains by hand, the API drops the manual sync step without changing retrieval: indexed sources still drive what reaches the prompt, but the index updates as the system runs. Anthropic's guidance for long-running agents recommends sharing state through external, addressable artifacts so agents and humans read and write the same context without re-deriving it each session ([Anthropic: harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)); Manus reports the same — exposing the context store as a programmable artifact lets sub-processes converge on shared state without thrash ([Manus: context engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)). The API generalises that mechanism from in-process file systems to a vendor-hosted, RBAC-enforced surface.

## When This Backfires

- **Single-repo teams already on `AGENTS.md`.** A pinned repo file plus existing agent memory covers their shared context; the API adds a second source of truth to keep in sync with no offsetting model-behaviour change.
- **High-write workflows hit undocumented quotas.** Capacity is enforced on indexed semantic content (tokens/embeddings), not file size, and GitHub has not published the limits. Community reports describe a progress bar passing 100% with ~185 small files ([community discussion #182622](https://github.com/orgs/community/discussions/182622)) and Spaces silently dropping low-priority content once over-budget — CI that appends every release note eventually evicts older entries without warning.
- **Mixed-permission audiences produce divergent answers.** RBAC is enforced per viewer even on shared and public Spaces ([GitHub Changelog, Dec 2025](https://github.blog/changelog/2025-12-01-copilot-spaces-public-spaces-and-code-view-support/)). Two readers asking the same question receive different effective context — a reproducibility hazard for anything resembling a decision record.
- **Untrusted ingestion closes a [lethal trifecta](../security/lethal-trifecta-threat-model.md).** If the API attaches external issue bodies, third-party PR descriptions, or webhook payloads, every later reader carries private repo data, untrusted content, and a write-capable token in one context — the classic prompt-injection loop ([Prompt Injection Threat Model](../security/prompt-injection-threat-model.md)).
- **Airgapped, non-GitHub, or point-in-time-reproducibility regimes.** Spaces are GitHub-hosted ([Copilot Spaces page](../tools/copilot/copilot-spaces.md)), so the API is unavailable there; and auto-syncing sources mean the same Space returns different answers over time without a code change, disqualifying it as a compliance system of record.

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

The note is first-party content the team already produces — not external issue text. The token is fine-grained, scoped to one Space, and cannot read unrelated repos. Reviewer agents reading the Space pick up the new release context on the next query without a human having to update an `AGENTS.md`. If the Space approaches its semantic budget, the workflow keeps appending — and the team accepts that older release notes silently fall out of retrieval rather than being flagged ([community #182622](https://github.com/orgs/community/discussions/182622)).

Contrast with the wrong shape:

```yaml
# Wrong — auto-attaches every external issue body into a shared Space
- name: Mirror inbound issues into Space
  run: |
    gh issue list --state open --json body --jq '.[].body' |
      gh api -X PATCH /orgs/acme/copilot-spaces/42/resources -f kind=note -f content=@-
```

External issue bodies are untrusted input; mirroring them into the Space gives every later reader — including agents with write access elsewhere — a prompt-injection surface no human reviewed.

## Key Takeaways

- The API changes *who can write the index*, not how retrieval works — apply only when the writer is a system whose updates a human currently makes by hand.
- File-based shared context (`AGENTS.md`, repo docs) remains the default for human-authored, version-controlled, offline-capable team context.
- Treat the write endpoint as a trifecta gate: control what gets attached, scope tokens to one Space, and never auto-ingest untrusted content.
- Accept that retrieval-grounded reads are non-deterministic and quota-evicted — do not use a Space as the system of record for anything requiring point-in-time reproducibility.

## Related

- [Copilot Spaces: Curated Context Collections for Grounding](../tools/copilot/copilot-spaces.md)
- [Agent Memory Patterns: Learning Across Conversations](agent-memory-patterns.md)
- [Externalization in LLM Agents: Memory, Skills, Protocols, and Harness](externalization-in-llm-agents.md)
- [File-Based Agent Coordination](../multi-agent/file-based-agent-coordination.md)
- [AGENTS.md as Distributed Conventions](../instructions/agents-md-distributed-conventions.md)
