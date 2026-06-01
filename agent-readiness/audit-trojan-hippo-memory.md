---
title: "Audit Trojan Hippo Memory and Structured-Source Surfaces"
description: "Enumerate long-term memory and structured-source write paths (KG, RAG index, schema registry, named-entity resolver), classify each by source-trust, validate the trifecta-leg removal that defeats dormant-payload and oracle-poisoning attacks, and flag any auto-ingest configuration that bridges untrusted input to cross-session retrieval."
tags:
  - tool-agnostic
  - security
  - memory
  - instructions
  - agent-readiness
aliases:
  - dormant memory payload audit
  - cross-session memory poisoning audit
  - trojan hippo audit
  - oracle poisoning audit
  - KG poisoning audit
  - structured-source poisoning audit
last_reviewed: 2026-05-27
---

Packaged as: `.claude/skills/agent-readiness-audit-trojan-hippo-memory/`

# Audit Trojan Hippo Memory and Structured-Source Surfaces

> Enumerate long-term memory and structured-source store write paths (KG, RAG index, schema registry, named-entity resolver), classify each by source-trust, validate the trifecta-leg removal that defeats dormant-payload and oracle-poisoning attacks, and flag any auto-ingest configuration that bridges untrusted input to cross-session retrieval.

!!! info "Harness assumption"
    In-scope surfaces are anything the agent consults as authoritative across sessions: file-based memory (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `~/.claude/memory/*`), explicit memory tools (Mem0, MemGPT, agent-managed lists), RAG indexes and vector stores, knowledge graphs (Neo4j, rdflib, Weaviate, custom triple stores), schema registries (Confluent, JSON Schema stores), named-entity resolvers, and sliding-window summarizers that persist across sessions. The audit reads harness config, MCP server registrations, KG/RAG client wiring, and memory-write callsites in `scripts/` and `.claude/`. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip when the agent has no persistent memory at all (session-scoped only) or has no outbound tool surface (no `send_email` / `http_post` / `webhook` / public-write file path). Run when memory persists across sessions and the agent has any egress; the [`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md) §When This Doesn't Apply enumerates closed-domain exclusions in detail.

The Trojan Hippo class plants a dormant memory payload via one untrusted tool input that activates sessions later when the user discusses sensitive topics — finance, health, identity ([Das et al., 2026](https://arxiv.org/abs/2605.01970), via [`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md)). Baseline attack-success rates run 85–100% across four memory architectures; defenses that drive ASR to 0–5% carry steep utility cost. The audit converts the four architectural defenses from [`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) §Defenses and Their Utility Costs into mechanical checks.

The same trifecta math applies when the agent's source-of-truth is a knowledge graph or RAG index, not a memory MCP server. [Oracle Poisoning](../security/oracle-poisoning-knowledge-graph.md) measures 100% trust across nine production models when L2-grade poison is delivered via tool-use — structurally identical to a poisoned memory record. The audit treats memory MCPs, KGs, RAG indexes, schema registries, and named-entity resolvers as one class: any structured store the agent consults as authoritative across sessions.

## Step 1 — Enumerate Memory and Structured-Source Surfaces

```bash
# File-based memory (root + per-user)
FILE_MEMORY=$(find . \( -name "CLAUDE.md" -o -name "AGENTS.md" -o -name ".cursorrules" \
  -o -name "GEMINI.md" -o -name "copilot-instructions.md" \) \
  ! -path "*/.claude/worktrees/*" 2>/dev/null)
USER_MEMORY=$(ls "$HOME/.claude/memory" "$HOME/.claude/CLAUDE.md" 2>/dev/null)

# Memory MCP servers (Mem0, MemGPT, custom)
MEMORY_MCP=$(grep -lE '"name"\s*:\s*"(mem0|memgpt|memory|long.term)' \
  .mcp.json mcp.json .claude/mcp/*.json 2>/dev/null)

# RAG / vector-store writers
RAG_WRITES=$(grep -rlE 'vector_store\.add|index\.upsert|chroma.*add|pinecone.*upsert|qdrant.*upsert|weaviate.*data|faiss.*add' \
  scripts/ .claude/ 2>/dev/null)

# Knowledge graph clients (Neo4j, rdflib, Weaviate, generic triple stores, MCP KG servers)
KG_CLIENTS=$(grep -rlE 'neo4j|py2neo|rdflib|weaviate.client|gremlin|sparql|kuzu|nebula.graph|tigergraph' \
  scripts/ .claude/ pyproject.toml requirements*.txt package.json 2>/dev/null)
KG_MCP=$(grep -lE '"name"\s*:\s*"(neo4j|knowledge.graph|kg|graph.*memory|graphiti)' \
  .mcp.json mcp.json .claude/mcp/*.json 2>/dev/null)

# Schema registry / named-entity resolver endpoints
SCHEMA_REG=$(grep -rlE 'schema.registry|confluent.*schema|json.schema.store|ner.*resolve|entity.resolver' \
  scripts/ .claude/ 2>/dev/null)

# Sliding-window persistence (compaction summaries written to durable storage)
COMPACT=$(grep -rlE 'compact.*save|summary.*persist|conversation.*archive' \
  scripts/ .claude/ 2>/dev/null)

# All structured stores collapsed for downstream loops
ALL_STORES="$FILE_MEMORY $MEMORY_MCP $RAG_WRITES $KG_CLIENTS $KG_MCP $SCHEMA_REG $COMPACT"
```

Capture each surface's: write path, write trigger (user message vs assistant summary vs tool return vs external ingest pipeline), and read scope (single-session vs cross-session). Anything reachable across sessions and consulted as authoritative is in-scope. KG and RAG surfaces fall in even when the agent has only read access at runtime — the ingest pipeline is the relevant write surface.

## Step 2 — Source-Trust Classification per Write Path

Every write must pass a source-trust check. From [`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) §Defenses, the strongest cheap defense is **user-prompt-only writes** — assistant summaries of tool returns must not enter long-term memory. The same rule generalises to KG and RAG ingest: every record needs a per-record source tag the retrieval layer can filter on.

The taxonomy:

- **human-curated** — PR-reviewed `CLAUDE.md`, hand-edited KG nodes, ontology entries reviewed before merge
- **agent-authored** — assistant summaries, agent-written experience records, auto-generated triples
- **external-ingest** — scheduled ingestion from third-party APIs, partner data feeds, package metadata
- **scraped** — open-web scrape, user-submitted forms, untrusted feeds

```bash
for surface in $ALL_STORES; do
  # Look for the source taxonomy near the write callsite
  CONTEXT=$(grep -B2 -A5 -E 'memory.write|memory_add|persist|upsert|create_node|merge_node|add_triple|ingest' "$surface" 2>/dev/null)

  # The write should be conditioned on source == user (or human-curated for KG/RAG ingest)
  echo "$CONTEXT" | grep -qE 'source.*user|role.*user|user_message|user_authored|human.curated|reviewed_by' \
    || echo "high|$surface|write not gated on user-authored or human-curated source|reject writes derived from tool returns, assistant summaries, or scraped feeds"

  # Auto-ingest of tool returns / external feeds is the high-risk configuration
  echo "$CONTEXT" | grep -qiE 'auto.ingest|tool.return.*memory|email.*memory|webfetch.*memory|scrape.*memory|scheduled.ingest|third.party.feed' \
    && echo "high|$surface|auto-ingests untrusted tool returns or external feeds into cross-session store|require explicit user confirmation per write or quarantine until human review"

  # Per-record source tag for KG/RAG: ground for retrieval-time filtering
  echo "$CONTEXT" | grep -qE 'record.source|node.source|provenance_tier|ingest_source|source_trust' \
    || echo "medium|$surface|records written without per-record source tag|attach {human-curated|agent-authored|external-ingest|scraped} per record"
done
```

Reference: the example memory-write policy in [`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md) §Example denies `email_body`, `web_fetch_content`, and `mcp_tool_return` as write sources. For KG/RAG, [Oracle Poisoning](../security/oracle-poisoning-knowledge-graph.md) §What Actually Defends names read-only access control as the only fully effective defense — equivalent to denying every non-human-curated source at the ingest layer.

## Step 3 — Ingest-Pipeline Provenance and the Oracle Anti-Pattern

KG and RAG records that ship without per-record provenance break the audit chain. The agent treats the retrieved value as ground truth, and there is no mechanical way to ask "where did this fact come from?" at retrieval time. [Oracle Poisoning](../security/oracle-poisoning-knowledge-graph.md) measures 100% trust on tool-delivered facts across nine models; the only fully effective defense is read-only access plus per-record provenance the retrieval layer can filter on.

Required shape (per [`generative-provenance-records`](../verification/generative-provenance-records.md)): each record carries an evidence span, source identifier, and a provenance tier. Retrieval must accept a filter — e.g. `provenance_tier in {human-curated}` for high-trust workflows — and the agent's prompt must surface the tier alongside the record so the model can weight it.

```bash
# Ingest pipelines should write provenance alongside content
for surface in $RAG_WRITES $KG_CLIENTS $KG_MCP $SCHEMA_REG; do
  WRITE=$(grep -B2 -A8 -E 'add|upsert|create_node|merge_node|add_triple|ingest' "$surface" 2>/dev/null)
  echo "$WRITE" | grep -qE 'provenance|evidence_span|source_id|ingested_at|reviewed_by|provenance_tier' \
    || echo "high|$surface|ingest writes records without provenance trail|attach {source_id, evidence_span, provenance_tier, ingested_at} per record; cite generative-provenance-records"
done

# Retrieval should be filterable by provenance tier
for surface in $RAG_WRITES $KG_CLIENTS $KG_MCP; do
  READ=$(grep -B2 -A10 -E 'query|search|retrieve|get_node|match\(' "$surface" 2>/dev/null)
  echo "$READ" | grep -qE 'provenance_tier|tier.*filter|min_trust|source.*allowlist|where.*provenance' \
    || echo "high|$surface|retrieval cannot filter by provenance tier|expose a tier filter; default high-stakes workflows to human-curated only"
done

# Oracle anti-pattern: agent treats KG/RAG result as ground truth without source attribution in the prompt
ORACLE=$(grep -rlE 'kg.result|graph.result|rag.result|retrieved_fact' .claude/ scripts/ 2>/dev/null)
for o in $ORACLE; do
  grep -qE 'cite|source|provenance|attribution|according.to' "$o" \
    || echo "high|$o|oracle anti-pattern — KG/RAG result surfaced to model without source attribution|render retrieved fact with its provenance tier and source_id alongside; require the model to cite source in any claim derived from it"
done
```

Cross-reference: [`generative-provenance-records`](../verification/generative-provenance-records.md) for the per-claim record shape; [`oracle-poisoning-knowledge-graph`](../security/oracle-poisoning-knowledge-graph.md) §Six Attack Scenarios for the corruption modes a tier filter is meant to catch.

## Step 4 — Confirmation Gate on Memory and Structured-Source Writes

Even user-attributed writes can be rewritten by an injected instruction inside an attacker email when the agent paraphrases it back to the user. The defense is an explicit confirmation step.

```bash
for surface in $FILE_MEMORY $MEMORY_MCP $RAG_WRITES $KG_CLIENTS $KG_MCP; do
  # Confirmation gate: HITL prompt, signed user approval, or explicit write tool call (not implicit)
  grep -qE 'confirmation.required|hitl.*memory|user.approval|explicit.write' "$surface" 2>/dev/null \
    || echo "medium|$surface|no confirmation gate on memory or structured-source write|wire a HITL prompt; cite human-in-the-loop-confirmation-gates"
done
```

Cross-reference: [`audit-confirmation-gate-logs`](audit-confirmation-gate-logs.md). A high finding here usually surfaces missing confirmation-gate coverage on the memory write itself.

## Step 5 — Trifecta-Leg Removal Check

Trojan Hippo composes the [lethal trifecta](../security/lethal-trifecta-threat-model.md) across two sessions — Session 1 untrusted input + memory write, Session N private data + outbound tool. Removing any leg breaks the chain ([`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md) §Architectural Defenses). The same composition applies when the cross-session bridge is a poisoned KG node or RAG chunk instead of a memory record.

```bash
# Leg 1: untrusted input bridge — covered by Step 2/3 above
# Leg 2: private data — PII tokenization in context
PII_TOKENIZE=$(grep -rlE 'pii.tokenize|tokenize.*pii|redact.*pii|mask.*ssn|mask.*card' \
  scripts/ .claude/ 2>/dev/null)

# Leg 3: external communication — egress allowlist
EGRESS=$(grep -lE 'web_fetch_allowlist|allowed_hosts|deny:' .claude/settings.json 2>/dev/null)
URL_GUARD=$(grep -rlE 'url.exfiltration.guard|public.web.index' scripts/ .claude/ 2>/dev/null)

# At least ONE leg must be cleanly removed
[[ -z "$PII_TOKENIZE$EGRESS$URL_GUARD" ]] \
  && echo "high|.claude|none of three trifecta legs is architecturally removed|remove untrusted-input writes, tokenize PII, or default-deny egress"

# Cross-session private-data leg: agent that talks finance/health/identity AND has memory + egress
SENSITIVE=$(grep -rlE 'finance|health|tax|salary|ssn|medical|legal' .claude/ scripts/ 2>/dev/null | head -3)
[[ -n "$SENSITIVE" && -z "$PII_TOKENIZE" ]] \
  && echo "high|$SENSITIVE|sensitive-topic agent without PII tokenization|tokenize PII before it enters retrievable context"
```

Reference: [`pii-tokenization-in-agent-context`](../security/pii-tokenization-in-agent-context.md), [`bootstrap-egress-policy`](bootstrap-egress-policy.md), [`bootstrap-url-fetch-gate`](bootstrap-url-fetch-gate.md).

## Step 6 — Provenance on Retrieved Memory and Records

The dominant failure mode is provenance blindness — retrieved memory tokens enter the model with the same authority as live user input ([`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) §Why It Works). The same applies to KG nodes and RAG chunks. Validate that retrieved entries carry a trust-tier marker the system prompt recognises.

```bash
# Retrieval callsites should attach provenance to surfaced entries
for surface in $MEMORY_MCP $RAG_WRITES $KG_CLIENTS $KG_MCP; do
  RETRIEVE=$(grep -B2 -A10 -E 'memory.retrieve|memory_get|search\(.*memory|query\(.*memory|get_node|match\(' "$surface" 2>/dev/null)
  echo "$RETRIEVE" | grep -qE 'source|provenance|trust.tier|written_by|origin' \
    || echo "medium|$surface|retrieval surfaces entries without provenance markers|attach origin (user_message vs tool_return vs human-curated-KG vs external-ingest) per entry; instruct the model to weight accordingly"
done

# A-MemGuard / cryptographic provenance is the strong form (not yet broadly deployed)
grep -rlE 'a.memguard|memory.provenance.signature|mem.taint' scripts/ .claude/ 2>/dev/null \
  | head -1 | awk '{ if ($0) print "info|"$1"|cryptographic memory provenance present — strongest defense" }'
```

Reference: [`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) cites [A-MemGuard (2025)](https://arxiv.org/abs/2510.02373) and the [Memory Poisoning and Secure Multi-Agent Systems (2026)](https://arxiv.org/abs/2603.20357) provenance approach.

## Step 7 — Cross-Session Lethal-Trifecta Pivot

A per-session trifecta audit passes each session and misses the pivot ([`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) §Cross-Session Lethal Trifecta). This step composes the union. A poisoned KG node or RAG chunk fills the same bridge role as a poisoned memory record.

```bash
# Reuse the principal table from audit-lethal-trifecta if available
TRIFECTA=$(find . -name "trifecta*.md" -o -name "lethal-trifecta-matrix*" 2>/dev/null | head -1)

# A principal that has memory writes from untrusted input AND egress in the same agent
# is the cross-session (1,1,1) — flag even if no single session shows all three
for principal in $(grep -lE 'agent.*name|sub.agent' .claude/agents/*.md 2>/dev/null); do
  HAS_STORE=$(grep -cE 'memory|persist|long.term|knowledge.graph|vector_store|rag.|kg.' "$principal")
  HAS_UNTRUSTED=$(grep -cE 'web|email|fetch|scrape|external.input' "$principal")
  HAS_EGRESS=$(grep -cE 'send_email|http_post|webhook|publish|push' "$principal")
  [[ $HAS_STORE -gt 0 && $HAS_UNTRUSTED -gt 0 && $HAS_EGRESS -gt 0 ]] \
    && echo "high|$principal|cross-session (1,1,1) — memory/KG/RAG bridges untrusted input to egress|remove one leg; defaults: deny tool-return writes; gate retrieval on human-curated provenance tier"
done
```

A `high` here is the cross-session finding `audit-lethal-trifecta` cannot see.

## Decision Rule

A finding is **high** when **any** of the following hold:

- Agent has memory-write surfaces with auto-ingest of tool returns and any egress (classic Trojan Hippo)
- Agent has any KG/RAG retrieval tool **and** no provenance-tier filter **and** the ingest surface is not human-curated end-to-end (Oracle Poisoning trifecta)
- A principal exhibits the cross-session `(1,1,1)` from Step 7
- Sensitive-topic agent with no PII tokenization or egress control

The KG/RAG branch is the structurally identical sibling — the math from [`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) is reused with the structured-source ingest pipeline standing in for the memory-write step.

## Step 8 — Findings Output

```markdown
| Severity | Surface | Mode | Finding | Suggested fix |
|----------|---------|------|---------|---------------|
```

Severity rule of thumb (drawn from [`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md) §When This Doesn't Apply and [`oracle-poisoning-knowledge-graph`](../security/oracle-poisoning-knowledge-graph.md) §What Actually Defends):

- `high` — auto-ingest of tool returns into long-term memory; KG/RAG retrieval without provenance-tier filter and non-human-curated ingest; oracle anti-pattern (retrieved fact surfaced without source attribution); cross-session `(1,1,1)`; sensitive-topic agent with no PII tokenization or egress control
- `medium` — missing confirmation gate; missing provenance markers on retrieval; missing per-record source tag; rapidly-evolving memory or KG schema where the policy has not stabilised
- `low` — closed-domain agent (no untrusted input path) with auto-ingest; advisory only

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Trojan Hippo Memory and Structured Sources — <repo>

| Stores | User/human-curated writes | Confirmation gate | Provenance trail | Tier filter on retrieval | Trifecta-leg removed |
|------:|:-------------------------:|:-----------------:|:----------------:|:------------------------:|:--------------------:|
| <n> | <n> | <n> | <n> | <n> | <legs removed> |

Top fix: <one-liner — usually deny tool-return writes; for KG/RAG, default retrieval to human-curated tier only>
```

## Remediation

- Auto-ingest detected → restrict memory writes to `source: user_message`; deny `email_body`, `web_fetch_content`, `mcp_tool_return` as sources ([example policy](../security/trojan-hippo-memory-attack.md#example))
- KG/RAG ingest without provenance → attach `{source_id, evidence_span, provenance_tier, ingested_at}` per record; cite [`generative-provenance-records`](../verification/generative-provenance-records.md)
- Retrieval cannot filter by provenance tier → expose a tier filter; default high-stakes workflows to `human-curated` only (the only fully effective defense in [`oracle-poisoning-knowledge-graph`](../security/oracle-poisoning-knowledge-graph.md))
- Oracle anti-pattern → render retrieved fact with its provenance tier and source_id alongside; require the model to cite source in any claim derived from it
- Missing confirmation gate → wire [`human-in-the-loop-confirmation-gates`](../security/human-in-the-loop-confirmation-gates.md) on the memory- or KG-write tool; pair with [`audit-confirmation-gate-logs`](audit-confirmation-gate-logs.md)
- No trifecta leg removed → choose by task distribution: untrusted-input write removal is cheapest, PII tokenization preserves most utility, IFC policy is strongest but loses outbound-mail in untrusted-context sessions
- Retrieval lacks provenance → attach origin per entry; tag system prompt to weight `tool_return`-origin entries lower
- Cross-session `(1,1,1)` → split memory/KG/RAG and egress across separate principals; or remove memory and structured-source writes from any agent that holds egress

## Related

- [Trojan Hippo: Dormant Memory Payloads That Wait for Sensitive Topics](../security/trojan-hippo-memory-attack.md) — three-stage attack mechanism and example policy
- [Trojan Hippo: Cross-Session Memory Poisoning for Data Exfiltration](../security/trojan-hippo-memory-exfiltration.md) — measured ASR per backend, four defenses with utility cost
- [Oracle Poisoning: Knowledge Graph Corruption Against Tool-Using Agents](../security/oracle-poisoning-knowledge-graph.md) — KG/RAG sibling; 100% trust on tool-delivered facts; read-only access is the only fully effective defense
- [Generative Provenance Records for Tool-Using Agents](../verification/generative-provenance-records.md) — per-record provenance shape this audit requires
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — single-session decomposition; this audit covers the cross-session pivot
- [PII Tokenization in Agent Context](../security/pii-tokenization-in-agent-context.md) — defense for the private-data leg
- [Bootstrap URL Fetch Gate](bootstrap-url-fetch-gate.md) — egress-leg removal
- [Audit Confirmation Gate Logs](audit-confirmation-gate-logs.md) — sibling audit; gate fidelity on memory writes
