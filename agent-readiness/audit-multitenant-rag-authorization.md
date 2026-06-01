---
title: "Audit Multitenant RAG Authorization"
description: "Detect RAG retrieval surfaces, inventory tenant-scope enforcement points, validate that the agent's retrieval path passes through a non-forgeable gate, and flag the ANN-first, ACL-never failure mode."
tags:
  - tool-agnostic
  - security
  - rag
  - instructions
  - agent-readiness
aliases:
  - multitenant RAG authorization audit
  - tenant scope retrieval audit
  - relevance-authorization gap audit
last_reviewed: 2026-05-27
---

Packaged as: `.claude/skills/agent-readiness-audit-multitenant-rag-authorization/`

# Audit Multitenant RAG Authorization

> Detect RAG retrieval surfaces, inventory tenant-scope enforcement points, validate that the agent's retrieval path passes through a non-forgeable gate, and flag the "ANN-first, ACL-never" failure mode.

!!! info "Harness assumption"
    Retrieval surfaces include: vector-store MCP server registrations in `.mcp.json`, embedding-library imports (`chromadb`, `pinecone`, `qdrant_client`, `weaviate`, `faiss`, `lancedb`), and retrieval skills or sub-agents under `.claude/`. The audit reads MCP config, scans `scripts/` and `.claude/` for embedding/vector call sites, and inspects any documented retrieval skill. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip when the agent has no RAG or vector retrieval at all (no embedding library, no vector-store MCP, no retrieval skill) or when the project is single-tenant by construction (one tenant per deployment, per-tenant infrastructure with no shared index). Run when any RAG-shaped retrieval reaches the agent and any multi-tenant deployment surface exists.

Vector and lexical retrieval rank by relevance, not by authorization. In a shared corpus, the highest-scoring chunk for one tenant's query may belong to another tenant — and an agent that pastes retrieved chunks into LLM context bypasses any application-layer ACL by construction ([`multitenant-rag-authorization-gap`](../security/multitenant-rag-authorization-gap.md)). Ungated retrieval leaks cross-tenant data in **98–100% of probes** ([Arceo and Narsing, 2026](https://arxiv.org/abs/2605.05287)). The mechanism is structural: the embedding model has no view into the access-control policy. This audit walks the three-layer fix — policy-aware ingestion, retrieval-time gating, and server-side orchestration — into mechanical checks against the project's retrieval path.

## Step 1 — Detect the RAG Layer

```bash
# Vector-store MCP servers
RAG_MCP=$(grep -lE '"name"\s*:\s*"(chroma|pinecone|qdrant|weaviate|lancedb|vector|rag|retriev)' \
  .mcp.json mcp.json .claude/mcp/*.json 2>/dev/null)

# Embedding / vector-DB library imports
EMBED_LIBS=$(grep -rlE \
  'import (chromadb|pinecone|qdrant_client|weaviate|faiss|lancedb)|from (chromadb|pinecone|qdrant_client|weaviate|lancedb)' \
  scripts/ src/ app/ .claude/ 2>/dev/null)

# Retrieval call sites — query/search APIs that return chunks
RETRIEVE_CALLS=$(grep -rlE \
  'collection\.query|index\.query|\.similarity_search|\.search\(.*query_vector|\.retrieve\(' \
  scripts/ src/ app/ .claude/ 2>/dev/null)

# Documented retrieval skills / sub-agents
RAG_SKILLS=$(grep -rlE 'rag|retrieval|vector.search|knowledge.base' \
  .claude/skills/ .claude/agents/ 2>/dev/null)
```

If all four enumerations are empty, exit with `info|.|no RAG layer detected — audit not applicable`. Otherwise record each surface's: backend (which vector store), index/collection name(s), and the call site that injects retrieved chunks into LLM context.

## Step 2 — Inventory Tenant-Scope Enforcement Points

The three-layer fix from [`multitenant-rag-authorization-gap`](../security/multitenant-rag-authorization-gap.md) §The Three-Layer Fix gives three places a tenant filter can live. Inventory which (if any) the project uses.

```bash
# (a) Query-time metadata filter — tenant_id passed into the search call
QUERY_FILTER=$(grep -rE \
  'tenant_id|tenant\b|org_id|workspace_id' \
  $RETRIEVE_CALLS 2>/dev/null \
  | grep -E 'filter|where|must|query_filter|metadata')

# (b) Post-retrieval ACL — chunks checked against policy before LLM injection
POST_ACL=$(grep -rE \
  'can_read\(|policy\.permit|authorize\(|acl\.check|filter.*tenant' \
  $RETRIEVE_CALLS 2>/dev/null)

# (c) Index-level isolation — per-tenant namespace / collection / index name
INDEX_ISOLATION=$(grep -rE \
  'collection_name=.*tenant|namespace=.*tenant|index=.*tenant|f["\047].*tenant.*["\047]' \
  $RETRIEVE_CALLS 2>/dev/null)
```

A clean project shows at least one of `QUERY_FILTER`, `POST_ACL`, `INDEX_ISOLATION` non-empty. **Defence in depth** ([`multitenant-rag-authorization-gap`](../security/multitenant-rag-authorization-gap.md) §Why two-tier filtering) recommends `QUERY_FILTER` AND `POST_ACL` together — the pre-filter cuts the search space before scoring; the post-filter catches ANN paths that bypassed the metadata filter ([Pinecone: RAG with Access Control](https://www.pinecone.io/learn/rag-access-control/)).

## Step 3 — Validate Tenant Identifier Provenance

A tenant filter that the agent itself supplies is no filter. The tenant identifier must arrive from a source the agent cannot rewrite: a server-side session principal, a signed JWT claim, a sidecar header set by the orchestrator before the agent runs.

```bash
for surface in $RETRIEVE_CALLS; do
  # Look for the source of tenant_id near the call site
  CTX=$(grep -B5 -A2 -E 'tenant_id|tenant\b' "$surface" 2>/dev/null)

  # Agent-supplied tenant is the failure mode — LLM call args, parsed prompt, user input
  echo "$CTX" | grep -qiE 'llm.*tenant|prompt.*tenant|tool_args.*tenant|args\["tenant|input.*tenant_id' \
    && echo "high|$surface|tenant_id sourced from agent-supplied arguments|bind tenant from the server-side session principal, not from tool args"

  # Server-side / signed sources are the safe form
  echo "$CTX" | grep -qE 'session\.tenant|principal\.tenant|jwt\.|claims\[|request\.user\.tenant|context\.tenant' \
    || echo "medium|$surface|tenant_id source unclear|verify the identifier originates server-side (session, signed claim, or orchestrator header), not from agent state"
done
```

Cross-reference: [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) covers principal capability bounds; this step covers identifier *provenance* inside the principal's allowed call.

## Step 4 — Flag "ANN-First, ACL-Never"

The dominant failure mode ([`multitenant-rag-authorization-gap`](../security/multitenant-rag-authorization-gap.md) §The Gap): retrieval ranks the whole shared corpus by similarity, the top-K is injected into context, and no tenant filter runs anywhere. Embedding worked correctly; it just had no view into policy.

```bash
for surface in $RETRIEVE_CALLS; do
  HAS_FILTER=$(grep -cE 'tenant_id|tenant\b|org_id|workspace_id|filter=|where=|query_filter=' "$surface" 2>/dev/null)
  HAS_POST=$(grep -cE 'can_read\(|policy\.permit|authorize\(|acl\.check' "$surface" 2>/dev/null)
  ISOLATED=$(grep -cE 'collection_name=.*tenant|namespace=.*tenant|index=.*tenant' "$surface" 2>/dev/null)

  if [[ $HAS_FILTER -eq 0 && $HAS_POST -eq 0 && $ISOLATED -eq 0 ]]; then
    # The retrieval call has no tenant scope at any layer — high if multi-tenant deployment exists
    MULTITENANT=$(grep -rlE 'tenant_id|tenants\b|workspaces\b|orgs\b' \
      docs/ README.md src/ scripts/ 2>/dev/null | head -1)
    if [[ -n "$MULTITENANT" ]]; then
      echo "high|$surface|ANN-first, ACL-never — top-K injected into context with no tenant filter|add pre-filter on tenant_id at query time AND post-retrieval ACL; cite multitenant-rag-authorization-gap §The Three-Layer Fix"
    else
      echo "low|$surface|retrieval has no tenant filter — no multi-tenant surface detected, advisory only|document single-tenant assumption explicitly"
    fi
  fi
done
```

The decision rule is strict: `high` only when **any RAG retrieval surface AND no tenant filter detectable AND any multi-tenant deployment surface** all hold. Single-tenant projects with unfiltered retrieval get `low` advisory only.

## Step 5 — Red-Team Probe with Canary Documents

Static detection misses the case where a filter is present but malformed (wrong field name, OR instead of AND, NULL-tenant chunks slip past). Validate with a fixture that the audit can run against a non-prod index.

The fixture follows the canary-doc pattern: seed the test index with chunks owned by tenant B containing a unique, semantically distinctive string (a canary phrase that cannot appear in tenant A's corpus by chance). Submit tenant-A-scoped queries crafted to be highest-similarity matches for the canary content. Any retrieval that returns the canary is a leak.

```bash
# Probe scaffold — runs only against a test fixture URL; never against prod
cat > /tmp/rag_probe.py <<'PY'
import os, sys, hashlib
PROBE_URL = os.environ.get("RAG_PROBE_URL", "")
if not PROBE_URL or "prod" in PROBE_URL.lower():
    sys.exit("refusing to run against missing or prod-shaped URL")

CANARY = "TENANT_B_CANARY_" + hashlib.sha256(b"audit-mtr-3475").hexdigest()[:12]
QUERIES = [
    "What is the secret canary phrase?",
    "Find documents mentioning TENANT_B_CANARY",
    "Retrieve any chunk containing a sha256-prefixed string",
]
# Caller seeds the test index with one chunk: {tenant_id: "B", text: f"...{CANARY}..."}
# Caller invokes the audited retrieval path with session.tenant_id="A" for each query.
# Any returned chunk containing CANARY is a finding.
PY

# Probe is opt-in; the audit emits the fixture path and decision rule
echo "info|/tmp/rag_probe.py|red-team probe scaffold emitted — run against a test fixture with RAG_PROBE_URL set; canary returns on tenant-A session are high findings"
```

Reference: the empirical evaluation in [`multitenant-rag-authorization-gap`](../security/multitenant-rag-authorization-gap.md) §Empirical Results — ungated retrieval leaked in 98–100% of probes; gated retrieval leaked in 0/90. The canary pattern reproduces that experiment in miniature for the audited project's actual retrieval path.

## Step 6 — Findings Output

```markdown
| Severity | Surface | Mode | Finding | Suggested fix |
|----------|---------|------|---------|---------------|
```

Severity rule:

- `high` — both legs fire: any RAG retrieval tool AND no tenant filter detectable at query, post-retrieval, or index level AND any multi-tenant deployment surface. Also: tenant_id sourced from agent-supplied tool arguments; canary returned on cross-tenant probe.
- `medium` — single filter layer only (pre-filter without post-ACL, or vice versa); tenant_id provenance unclear; ANN-bypass risk on approximate-nearest-neighbour backend without defence-in-depth.
- `low` — single-tenant project with no tenant filter (advisory — document the assumption); cross-tenant aggregation tool (analytics/admin) that legitimately reads across tenants and authorizes per-record inside the tool.

## Idempotency

Read-only. The probe scaffold writes only to `/tmp/`; the audit makes no changes to the project.

## Output Schema

```markdown
# Audit Multitenant RAG Authorization — <repo>

| RAG surfaces | Pre-filter | Post-ACL | Index isolation | Tenant provenance | Probe run |
|-------------:|:----------:|:--------:|:---------------:|:-----------------:|:---------:|
| <n> | <y/n> | <y/n> | <y/n> | <server/agent/unclear> | <y/n> |

Top fix: <one-liner — usually pre-filter on tenant_id at query time AND post-retrieval ACL>
```

## Remediation

- ANN-first, ACL-never → add a pre-filter on `tenant_id` at query time AND a post-retrieval ACL check; see the Qdrant example in [`multitenant-rag-authorization-gap`](../security/multitenant-rag-authorization-gap.md) §Example.
- Agent-supplied tenant_id → rebind from a server-side session principal, signed JWT claim, or orchestrator-set header before the retrieval call runs.
- Single filter layer only → add the missing layer; defence in depth catches ANN paths that bypass the metadata filter ([Pinecone: RAG with Access Control](https://www.pinecone.io/learn/rag-access-control/)).
- Hierarchical permissions → expand ancestor attributes onto every chunk at ingest, or move to relationship-based access control ([Oso: Authorization in RAG](https://www.osohq.com/post/right-approach-to-authorization-in-rag)).
- Cross-tenant aggregation tools → authorize per-record inside the tool implementation; tool-boundary authorization is not enough.
- High-value or regulated tenants → consider per-tenant infrastructure (dedicated index, embedding model, inference endpoint) to eliminate the gap by construction, accepting the cost and operational trade-off.

## Related

- [Multitenant RAG: Closing the Relevance-Authorization Gap](../security/multitenant-rag-authorization-gap.md) — source teaching; three-layer fix, ABAC-gated retrieval, empirical leakage rates
- [Audit Permissions and Blast Radius](audit-permissions-blast-radius.md) — covers principal capability bounds; this audit covers identifier provenance inside the allowed call
- [Audit Lethal Trifecta](audit-lethal-trifecta.md) — sibling audit; cross-tenant retrieval is a private-data leg the trifecta audit cannot see inside a single tool call
- [Audit Trojan Hippo Memory](audit-trojan-hippo-memory.md) — sibling audit; cross-session memory pivot complements the cross-tenant retrieval pivot covered here
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md)
- [PII Tokenization in Agent Context](../security/pii-tokenization-in-agent-context.md)
