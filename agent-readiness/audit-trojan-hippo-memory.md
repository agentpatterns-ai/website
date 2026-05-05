---
title: "Audit Trojan Hippo Memory Surfaces"
description: "Enumerate long-term memory write paths, classify each by source-trust (user-authored vs tool-return), validate the trifecta-leg removal that defeats dormant-payload attacks, and flag any auto-ingest configuration that bridges untrusted input to cross-session retrieval."
tags:
  - tool-agnostic
  - security
  - memory
aliases:
  - dormant memory payload audit
  - cross-session memory poisoning audit
  - trojan hippo audit
---

Packaged as: `.claude/skills/agent-readiness-audit-trojan-hippo-memory/`

# Audit Trojan Hippo Memory Surfaces

> Enumerate long-term memory write paths, classify each by source-trust, validate the trifecta-leg removal that defeats dormant-payload attacks, and flag any auto-ingest configuration that bridges untrusted input to cross-session retrieval.

!!! info "Harness assumption"
    Memory surfaces include: file-based memory (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `~/.claude/memory/*`), explicit memory tools (Mem0, MemGPT, agent-managed lists), RAG index writes, and sliding-window summarizers that persist across sessions. The audit reads harness config, MCP server registrations, and memory-write callsites in `scripts/` and `.claude/`. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip when the agent has no persistent memory at all (session-scoped only) or has no outbound tool surface (no `send_email` / `http_post` / `webhook` / public-write file path). Run when memory persists across sessions and the agent has any egress; the [`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md) §When This Doesn't Apply enumerates closed-domain exclusions in detail.

The Trojan Hippo class plants a dormant memory payload via one untrusted tool input that activates sessions later when the user discusses sensitive topics — finance, health, identity ([Das et al., 2026](https://arxiv.org/abs/2605.01970), via [`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md)). Baseline attack-success rates run 85–100% across four memory architectures; defenses that drive ASR to 0–5% carry steep utility cost. The audit converts the four architectural defenses from [`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) §Defenses and Their Utility Costs into mechanical checks.

## Step 1 — Enumerate Memory Write Surfaces

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
RAG_WRITES=$(grep -rlE 'vector_store\.add|index\.upsert|chroma.*add|pinecone.*upsert|qdrant.*upsert' \
  scripts/ .claude/ 2>/dev/null)

# Sliding-window persistence (compaction summaries written to durable storage)
COMPACT=$(grep -rlE 'compact.*save|summary.*persist|conversation.*archive' \
  scripts/ .claude/ 2>/dev/null)
```

Capture each surface's: write path, write trigger (user message vs assistant summary vs tool return), and read scope (single-session vs cross-session). The audit treats anything reachable across sessions as in-scope.

## Step 2 — Source-Trust Classification per Write Path

Every memory write must pass a source-trust check. From [`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) §Defenses, the strongest cheap defense is **user-prompt-only writes** — assistant summaries of tool returns must not enter long-term memory.

```bash
for surface in $FILE_MEMORY $MEMORY_MCP $RAG_WRITES $COMPACT; do
  # Look for the source taxonomy near the write callsite
  CONTEXT=$(grep -B2 -A5 -E 'memory.write|memory_add|persist|upsert' "$surface" 2>/dev/null)

  # The write should be conditioned on source == user
  echo "$CONTEXT" | grep -qE 'source.*user|role.*user|user_message|user_authored' \
    || echo "high|$surface|memory write not gated on user-authored source|reject writes derived from tool returns or assistant summaries"

  # Auto-ingest of tool returns is the high-risk configuration
  echo "$CONTEXT" | grep -qiE 'auto.ingest|tool.return.*memory|email.*memory|webfetch.*memory|scrape.*memory' \
    && echo "high|$surface|auto-ingests untrusted tool returns into long-term memory|require explicit user confirmation per write"
done
```

Reference: the example memory-write policy in [`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md) §Example denies `email_body`, `web_fetch_content`, and `mcp_tool_return` as write sources.

## Step 3 — Confirmation Gate on Memory Writes

Even user-attributed writes can be rewritten by an injected instruction inside an attacker email when the agent paraphrases it back to the user. The defense is an explicit confirmation step.

```bash
for surface in $FILE_MEMORY $MEMORY_MCP $RAG_WRITES; do
  # Confirmation gate: HITL prompt, signed user approval, or explicit write tool call (not implicit)
  grep -qE 'confirmation.required|hitl.*memory|user.approval|explicit.write' "$surface" 2>/dev/null \
    || echo "medium|$surface|no confirmation gate on memory write|wire a HITL prompt; cite human-in-the-loop-confirmation-gates"
done
```

Cross-reference: [`audit-confirmation-gate-logs`](audit-confirmation-gate-logs.md). A high finding here usually surfaces missing confirmation-gate coverage on the memory write itself.

## Step 4 — Trifecta-Leg Removal Check

Trojan Hippo composes the [lethal trifecta](../security/lethal-trifecta-threat-model.md) across two sessions — Session 1 untrusted input + memory write, Session N private data + outbound tool. Removing any leg breaks the chain ([`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md) §Architectural Defenses).

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

## Step 5 — Provenance on Retrieved Memory

The dominant failure mode is provenance blindness — retrieved memory tokens enter the model with the same authority as live user input ([`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) §Why It Works). Validate that retrieved entries carry a trust-tier marker the system prompt recognises.

```bash
# Retrieval callsites should attach provenance to surfaced entries
for surface in $MEMORY_MCP $RAG_WRITES; do
  RETRIEVE=$(grep -B2 -A10 -E 'memory.retrieve|memory_get|search\(.*memory|query\(.*memory' "$surface" 2>/dev/null)
  echo "$RETRIEVE" | grep -qE 'source|provenance|trust.tier|written_by|origin' \
    || echo "medium|$surface|memory retrieval surfaces entries without provenance markers|attach origin (user_message vs tool_return) per entry; instruct the model to weight accordingly"
done

# A-MemGuard / cryptographic provenance is the strong form (not yet broadly deployed)
grep -rlE 'a.memguard|memory.provenance.signature|mem.taint' scripts/ .claude/ 2>/dev/null \
  | head -1 | awk '{ if ($0) print "info|"$1"|cryptographic memory provenance present — strongest defense" }'
```

Reference: [`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) cites [A-MemGuard (2025)](https://arxiv.org/abs/2510.02373) and the [Memory Poisoning and Secure Multi-Agent Systems (2026)](https://arxiv.org/abs/2603.20357) provenance approach.

## Step 6 — Cross-Session Lethal-Trifecta Pivot

A per-session trifecta audit passes each session and misses the pivot ([`trojan-hippo-memory-exfiltration`](../security/trojan-hippo-memory-exfiltration.md) §Cross-Session Lethal Trifecta). This step composes the union.

```bash
# Reuse the principal table from audit-lethal-trifecta if available
TRIFECTA=$(find . -name "trifecta*.md" -o -name "lethal-trifecta-matrix*" 2>/dev/null | head -1)

# A principal that has memory writes from untrusted input AND egress in the same agent
# is the cross-session (1,1,1) — flag even if no single session shows all three
for principal in $(grep -lE 'agent.*name|sub.agent' .claude/agents/*.md 2>/dev/null); do
  HAS_MEMORY=$(grep -cE 'memory|persist|long.term' "$principal")
  HAS_UNTRUSTED=$(grep -cE 'web|email|fetch|scrape|external.input' "$principal")
  HAS_EGRESS=$(grep -cE 'send_email|http_post|webhook|publish|push' "$principal")
  [[ $HAS_MEMORY -gt 0 && $HAS_UNTRUSTED -gt 0 && $HAS_EGRESS -gt 0 ]] \
    && echo "high|$principal|cross-session (1,1,1) — memory bridges untrusted input to egress|remove one leg; defaults: deny tool-return memory writes"
done
```

A `high` here is the Trojan-Hippo-specific finding `audit-lethal-trifecta` cannot see.

## Step 7 — Findings Output

```markdown
| Severity | Surface | Mode | Finding | Suggested fix |
|----------|---------|------|---------|---------------|
```

Severity rule of thumb (drawn from [`trojan-hippo-memory-attack`](../security/trojan-hippo-memory-attack.md) §When This Doesn't Apply):

- `high` — auto-ingest of tool returns into long-term memory; cross-session `(1,1,1)`; sensitive-topic agent with no PII tokenization or egress control
- `medium` — missing confirmation gate; missing provenance markers on retrieval; rapidly-evolving memory schema where the policy has not stabilised
- `low` — closed-domain agent (no untrusted input path) with auto-ingest; advisory only

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Trojan Hippo Memory — <repo>

| Memory surfaces | User-only writes | Confirmation gate | Trifecta-leg removed | Provenance |
|----------------:|:----------------:|:-----------------:|:--------------------:|:----------:|
| <n> | <n> | <n> | <legs removed> | <n> |

Top fix: <one-liner — usually deny tool-return writes; second usually default-deny egress>
```

## Remediation

- Auto-ingest detected → restrict memory writes to `source: user_message`; deny `email_body`, `web_fetch_content`, `mcp_tool_return` as sources ([example policy](../security/trojan-hippo-memory-attack.md#example))
- Missing confirmation gate → wire [`human-in-the-loop-confirmation-gates`](../security/human-in-the-loop-confirmation-gates.md) on the memory-write tool; pair with [`audit-confirmation-gate-logs`](audit-confirmation-gate-logs.md)
- No trifecta leg removed → choose by task distribution: untrusted-input write removal is cheapest, PII tokenization preserves most utility, IFC policy is strongest but loses outbound-mail in untrusted-context sessions
- Retrieval lacks provenance → attach origin per entry; tag system prompt to weight `tool_return`-origin entries lower
- Cross-session `(1,1,1)` → split memory and egress across separate principals; or remove memory writes from any agent that holds egress

## Related

- [Trojan Hippo: Dormant Memory Payloads That Wait for Sensitive Topics](../security/trojan-hippo-memory-attack.md) — three-stage attack mechanism and example policy
- [Trojan Hippo: Cross-Session Memory Poisoning for Data Exfiltration](../security/trojan-hippo-memory-exfiltration.md) — measured ASR per backend, four defenses with utility cost
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md) — single-session decomposition; this audit covers the cross-session pivot
- [PII Tokenization in Agent Context](../security/pii-tokenization-in-agent-context.md) — defense for the private-data leg
- [URL Exfiltration Guard](../security/url-exfiltration-guard.md) and [Bootstrap URL Fetch Gate](bootstrap-url-fetch-gate.md) — egress-leg removal
- [Audit Lethal Trifecta](audit-lethal-trifecta.md) — sibling audit; per-session check
- [Audit Confirmation Gate Logs](audit-confirmation-gate-logs.md) — sibling audit; gate fidelity on memory writes
