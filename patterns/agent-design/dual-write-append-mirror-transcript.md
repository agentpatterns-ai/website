---
title: "Dual-Write Append-Mirror for Agent Transcript Externalization"
term: "Dual-Write Append-Mirror"
description: "Write the agent transcript to local disk first and forward each batch to a remote store as a best-effort mirror — so a store outage degrades the externalization, not the agent."
tags:
  - agent-design
  - observability
  - tool-agnostic
aliases:
  - dual-write transcript mirror
  - local-first agent session store
  - append-mirror session externalization
last_reviewed: 2026-05-30
maturity: adopted
---

# Dual-Write Append-Mirror for Agent Transcript Externalization

> Write the agent transcript to local disk first; forward each batch to a remote store as a best-effort mirror that the agent never blocks on.

Dual-write append-mirror is the externalization shape the Claude Agent SDK ships: the `claude` subprocess "always writes to local disk first; the SDK then forwards each batch to `append()`" on an attached `SessionStore`, with the store positioned as "a mirror, not a replacement" ([Claude Agent SDK: Persist sessions to external storage](https://code.claude.com/docs/en/agent-sdk/session-storage)). It applies to self-hosted agents that need local execution context (project filesystem, locally-running MCP servers) and off-host durability for at least one of: multi-host resume on shared-nothing replicas, container reclamation on restart or scale-down, or compliance retention in operator-governed storage ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage); [Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)). When none of those hold — a single developer laptop, sessions that never migrate — the local JSONL alone is the source of truth; when local execution context is not load-bearing, Anthropic's [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) treats the session log as the only durable substrate and removes the dual-write surface entirely ([Anthropic: Managed Agents](https://www.anthropic.com/engineering/managed-agents)).

## The adapter surface

A `SessionStore` is "an object with two required methods, `append` and `load`, and three optional methods" ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)):

| Method | Required | Called when |
|--------|----------|-------------|
| `append` | Yes | After each batch of transcript entries is written locally |
| `load` | Yes | Once before the subprocess spawns, when `resume` is set; returns `null` for unknown sessions |
| `listSessions` | No | By `listSessions()` and by `continue: true`; SDK throws if called and not implemented |
| `delete` | No | By `deleteSession()`; deleting the main key "must cascade to all subkeys for that session"; if undefined, deletion is a no-op, "which suits append-only backends" |
| `listSubkeys` | No | During resume, to discover subagent transcripts; without it, "only the main transcript is restored" |

The minimum surface is intentionally narrow — two methods make adapter authorship cheap, and a 13-contract conformance suite ships with the SDK to validate behavior ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage); [examples/session-stores](https://github.com/anthropics/claude-agent-sdk-typescript/tree/main/examples/session-stores)). Reference adapters exist for S3 (one JSONL part file per `append()`), Redis (`RPUSH`/`LRANGE` per transcript), and Postgres (one row per entry in a `jsonb` table) ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)).

## Mirror-failure semantics

When the remote store fails, the agent does not. "If `append()` rejects or times out, the error is logged, a `{ type: "system", subtype: "mirror_error" }` message is emitted into the iterator, and the query continues. The local transcript is already durable on disk, so a store outage does not interrupt the agent or lose data locally. Batches that fail are not retried, so monitor for `mirror_error` if you need to detect store data loss" ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)).

Three operational consequences follow from the no-retry policy:

- Alerting on `mirror_error` is the only signal that the remote copy has drifted from local truth.
- The adapter is responsible for any retry semantics it wants — the SDK will not call `append()` again on the same batch.
- An adapter that silently swallows duplicate-key errors (for example, a Postgres adapter that deduplicates at insert time) can drop data while emitting `mirror_error` an operator may ignore.

## Compaction versus raw: two reads, two consumers

The dual-write shape forces a clean split between what the agent sees on resume and what the audit trail holds. "`getSessionMessages({ sessionStore })` returns the linked message chain the agent would see on resume. After auto-compaction, earlier turns are replaced by a summary, so a session whose store holds 503 raw entries may return 18 messages from `getSessionMessages`. For the full raw history, including pre-compaction turns and metadata entries, call `store.load(key)` directly" ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)).

Two consumers, two reads:

- Resume engine → `getSessionMessages()` → post-compaction chain.
- Audit trail, compliance review, debugging → `store.load(key)` → raw history.

A team that conflates the two will misread incidents — the documentation makes the distinction explicit, but the surface is non-obvious until something goes wrong.

## Fork is not byte-copy

`forkSession` reads source entries, "rewrites every `sessionId` field and remaps message UUIDs, then appends the transformed entries under a new key. An adapter-level copy or `CopyObject` shortcut would produce a transcript that still references the old session ID, so the SDK does not use one" ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)). Custom adapters that try to optimize forks with backend-native copy primitives (S3 `CopyObject`, Postgres `INSERT INTO ... SELECT`) break the transcript silently. The conformance suite catches this — running it is part of adapter ownership.

## Flush mode and retention

The default `session_store_flush: "batched"` mode waits for end-of-turn before delivering frames; v0.1.73 added an `"eager"` mode that "delivers frames to `SessionStore.append()` in near-real-time instead of waiting for the end-of-turn flush, enabling live-tailing UIs, cross-process resume, and crash-durability use cases" ([claude-agent-sdk-python CHANGELOG](https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md)). Eager trades remote-write volume for live observability — on per-request-priced backends (S3 PUT, DynamoDB write capacity) the bill scales with agent verbosity.

Retention sits on the adapter, not the SDK: "The SDK never deletes from your store on its own. Retention is the adapter's responsibility: implement TTLs, S3 lifecycle policies, or scheduled cleanup according to your compliance requirements. Local transcripts under `CLAUDE_CONFIG_DIR` are swept independently by the `cleanupPeriodDays` setting" ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)).

## Why it works

Dual-write append-mirror works because it inverts the dependency between the agent's liveness and the durability layer's liveness. The authoritative write lands on a single substrate (local JSONL) before any secondary copy is attempted, so a remote-store outage degrades replication but not the primary write — the standard write-ahead-log replication shape ([Architecture Weekly: The Write-Ahead Log](https://www.architecture-weekly.com/p/the-write-ahead-log-a-foundation)). The agent's loop sees the local write succeed and continues; the remote write happens asynchronously, and its failure is surfaced as data (a `mirror_error` system message) rather than as a control-flow interruption. Hosting docs name this directly as one of three things to know about `SessionStore`: "Mirror, not replacement: the subprocess writes to local disk first, and the store receives a copy of each batch. Local writes remain authoritative" ([Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)). The naive alternative — store-as-replacement, where the agent blocks on the remote round-trip — couples agent liveness to store liveness; a slow store stalls the loop and a flaky store kills sessions. The dual-write inversion preserves the unconditional fast-path and pushes the consistency burden onto the operator's monitoring.

## When this backfires

- Atomic-coupling expectations. The general "dual-write is an anti-pattern" critique targets designs that need atomicity across two stores ([Confluent: The Dual-Write Problem](https://www.confluent.io/blog/dual-write-problem/)). This pattern is not symmetric — local is authoritative, mirror is best-effort. Treating the two as needing to agree on every write recreates the anti-pattern; transactional outbox or CDC is the right shape if you genuinely need atomicity.
- Append idempotency violations in the adapter. The SDK does not retry failed batches. An adapter that swallows duplicate-key errors at insert time loses data while logging `mirror_error` an operator may ignore.
- `CLAUDE.md` and working-directory artifacts are not mirrored. Resuming on a different host with the transcript intact but no `CLAUDE.md` yields a behaviorally different agent ([Hosting the Agent SDK](https://code.claude.com/docs/en/agent-sdk/hosting)). Mount a shared volume or sync those separately — the pattern delivers transcript portability, not full agent portability.
- Compaction divergence between resume and audit consumers. Anyone assuming `getSessionMessages()` and `store.load()` return the same data will misread incidents; the 503-vs-18 gap is a documented surface that bites teams who do not internalize it.
- Single-tenant, single-host deployments. When the host is a developer laptop and the session never migrates, the local JSONL is already the source of truth — the mirror adds a failure surface (`mirror_error`) with no resume benefit. The pattern pays for itself only when at least one of {multi-host resume, container reclamation, compliance retention} is real.
- Incompatible options. "Because the mirror depends on local writes, `sessionStore` cannot be combined with `persistSession: false`; the SDK throws if you set both. It also throws if combined with `enableFileCheckpointing`, since file-history backup blobs are written directly to local disk and are not mirrored to the store" ([Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)).
- Managed-Agents-style centralized durability fits better. When local execution context is not load-bearing — no project filesystem, no local MCP servers — Anthropic's [Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) architecture treats the session log as the single durable substrate and removes the two-system reconciliation surface entirely ([Anthropic: Managed Agents](https://www.anthropic.com/engineering/managed-agents)). Use that path when build-vs-buy points to buy.

## Example

A team operating self-hosted Agent SDK workers in a Kubernetes hybrid-session pattern wants threads to survive pod reclamation without losing in-flight reasoning.

Before — naive externalization (store-as-replacement):

```text
Agent loop --[blocking write]--> Remote store
       \--[on store error]--> session fails, user sees error
```

A slow store stalls the loop; a flaky store kills sessions.

After — dual-write append-mirror with `SessionStore`:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { S3Client } from "@aws-sdk/client-s3";
import { S3SessionStore } from "./S3SessionStore"; // copied from examples/session-stores/s3

const store = new S3SessionStore({
  bucket: "my-claude-sessions",
  prefix: "transcripts",
  client: new S3Client({ region: "us-east-1" }),
});

for await (const message of query({
  prompt: "Continue investigation",
  options: { sessionStore: store, resume: previousSessionId },
})) {
  if (message.type === "system" && message.subtype === "mirror_error") {
    metrics.increment("session_store.mirror_error"); // operator alert path
  }
}
```

The local JSONL under `CLAUDE_CONFIG_DIR` is authoritative; S3 receives a best-effort copy of each batch; a regional S3 outage emits `mirror_error` into the message stream and the agent keeps stepping. On pod loss, a new pod loads the transcript from S3 via `resume`, hydrates the agent, and continues ([Hosting the Agent SDK: Hybrid sessions](https://code.claude.com/docs/en/agent-sdk/hosting); [Session storage](https://code.claude.com/docs/en/agent-sdk/session-storage)).

## Key Takeaways

- The Claude Agent SDK ships dual-write append-mirror as the externalization shape — local-first with the remote store as a best-effort mirror, not a replacement
- Mirror failures emit a `{ type: "system", subtype: "mirror_error" }` message and the query continues; the SDK does not retry, so operator alerting on this event is the only data-loss signal
- The adapter surface is two required methods (`append`, `load`) plus three optional (`listSessions`, `delete`, `listSubkeys`); a 13-contract conformance suite ships with the SDK to validate it
- `getSessionMessages()` returns the post-compaction chain the agent sees on resume; `store.load(key)` returns the raw history — two reads for two consumers (resume engine vs audit trail)
- `forkSession` rewrites session IDs and remaps message UUIDs at the SDK layer; adapter-level `CopyObject` shortcuts produce silently-broken forks that the conformance suite catches
- Retention is the adapter's responsibility — the SDK never deletes from your store; TTLs, S3 lifecycle, scheduled cleanup live on the storage side
- The pattern is Qualified: apply it when local execution context is load-bearing and at least one of {multi-host resume, container reclamation, compliance retention} is real; otherwise the local JSONL alone suffices or Managed Agents is the better path

## Related

- [Remote Agent Host Sessions over SSH and Dev Tunnels](remote-agent-host-sessions.md) — where the host is the durability boundary instead of an attached store; complementary externalization shape for editor-attached topologies
- [Cloud-Agent Three-Layer State Decoupling](cloud-agent-state-layer-decoupling.md) — the higher-level state-split this pattern sits inside; conversation state is the layer the mirror externalizes
- [Session Harness Sandbox Separation for Long-Running Agents](session-harness-sandbox-separation.md) — the three-primitive architecture under which the session log is the durable substrate
- [Long-Running Agents: Durability and Resumability Across Sessions](long-running-agents.md) — the operational shape that makes off-host transcript durability worth running
- [Delta Channels: Bounded Checkpoint Storage for Append-Only Agent State](delta-channels-checkpoint-storage.md) — keeps the append-only mirror linear in storage cost over long sessions
