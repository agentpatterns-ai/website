---
title: "Audit Tool Idempotency"
description: "Inventory MCP tools and project-exposed tool definitions, validate `idempotentHint` / `destructiveHint` / `readOnlyHint` annotations against MCP spec defaults, classify each tool's retry-safety, and emit per-tool findings."
tags:
  - tool-agnostic
  - tool-engineering
  - mcp
aliases:
  - tool annotation audit
  - MCP idempotentHint audit
  - retry-safety audit
---

Packaged as: `.claude/skills/agent-readiness-audit-tool-idempotency/`

# Audit Tool Idempotency

> Inventory tool definitions, validate idempotency / destructive / read-only annotations against MCP spec defaults, classify retry-safety, emit per-tool findings.

!!! info "Harness assumption"
    Tools surface through MCP server `.mcp.json` definitions or project-defined tool schemas (e.g., `tools/*.json`, FastAPI router decorators, function-tool registries). Annotations in the audit's scope are MCP's `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip when the project exposes no MCP servers and defines no agent-callable tools — there is nothing to annotate. Run when MCP tools are wired or when the agent calls custom function-tools.

Per the MCP spec, tool annotations have specific defaults: `destructiveHint: true`, `openWorldHint: true`, `readOnlyHint: false`, `idempotentHint: false` ([`mcp-client-server-architecture`](../tool-engineering/mcp-client-server-architecture.md)). A server that omits annotations is treated as destructive and non-idempotent — clients gate behind confirmation, retries are unsafe, and the agent's recovery surface shrinks. Annotations are advisory; paired with idempotent server-side implementations they reduce confirmation friction without weakening safety. Rules from [`mcp-server-design`](../tool-engineering/mcp-server-design.md) and [`idempotent-agent-operations`](../agent-design/idempotent-agent-operations.md).

## Step 1 — Locate Tool Definitions

```bash
# MCP server registrations
test -f .mcp.json && jq '.servers // .mcpServers | to_entries[] | {name:.key, command:.value.command}' .mcp.json

# Project-defined tool schemas
find . -path "*/tools/*.json" -o -name "tool-schema*.json" \
  ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null

# Function-tool decorators
grep -rE "@tool|@function_tool|tool_definition\s*=|inputSchema:\s*{" \
  src/ tools/ packages/ 2>/dev/null | head -20
```

If neither MCP servers nor tool schemas are defined, abort with a single-line "no tools to audit" report.

## Step 2 — Probe MCP Servers for `tools/list`

For each MCP server, retrieve the tool catalog and capture the annotations object per tool:

```bash
probe_mcp_tools() {
  local server="$1"
  jq -nc --arg id "list-1" '{jsonrpc:"2.0", id:$id, method:"tools/list", params:{}}' \
    | $server  # adapt to actual transport (stdio/http)
}

# Or from a captured catalog file
jq '.result.tools[] | {name, annotations: (.annotations // {})}' tools-list.json
```

Capture for each tool: `name`, `annotations.readOnlyHint`, `annotations.destructiveHint`, `annotations.idempotentHint`, `annotations.openWorldHint`.

## Step 3 — Classify Each Tool

Match each tool name to one of four behavior classes. Names alone are weak evidence — confirm by reading the tool's `description` field and the inputSchema mutation surface.

| Class | Heuristic | Expected annotations |
|-------|-----------|---------------------|
| Pure read | description contains `read`, `get`, `list`, `search`, `query`; no inputSchema fields named `value`, `data`, `body`, `payload` | `readOnlyHint: true`, `idempotentHint: true`, `destructiveHint: false` |
| Idempotent write | description contains `set`, `upsert`, `put`, `update`, `replace`; behavior re-runs to same state | `idempotentHint: true`, `destructiveHint: true`, `readOnlyHint: false` |
| Non-idempotent destructive | description contains `delete`, `drop`, `remove`, `cancel`, `revoke`, or external side effects (`send`, `email`, `notify`, `pay`, `charge`) | `destructiveHint: true`, `idempotentHint: false`, `readOnlyHint: false` |
| Append / create | description contains `create`, `append`, `add`, `post`, `submit`; each call produces new resource | `destructiveHint: true`, `idempotentHint: false` (unless server enforces an idempotency key) |

```bash
classify() {
  local name="$1" desc="$2"
  echo "$desc" | grep -qiE "read|get|list|search|query|describe" && echo "pure_read" && return
  echo "$desc" | grep -qiE "delete|drop|remove|cancel|revoke|send|email|notify|pay|charge" && echo "destructive" && return
  echo "$desc" | grep -qiE "create|append|add|post|submit" && echo "append" && return
  echo "$desc" | grep -qiE "set|upsert|put|update|replace" && echo "idempotent_write" && return
  echo "unknown"
}
```

## Step 4 — Compare Against Annotations

For each tool, check the captured annotations against the expected pattern from Step 3.

```bash
expect() {
  local class="$1" anno="$2"
  case "$class" in
    pure_read)
      [[ "$(echo "$anno" | jq -r '.readOnlyHint // false')" == "true" ]] \
        || echo "high|<tool>|pure-read tool missing readOnlyHint:true|set readOnlyHint:true to skip confirmation prompts"
      [[ "$(echo "$anno" | jq -r '.idempotentHint // false')" == "true" ]] \
        || echo "medium|<tool>|pure-read tool missing idempotentHint:true|reads are idempotent by definition"
      ;;
    idempotent_write)
      [[ "$(echo "$anno" | jq -r '.idempotentHint // false')" == "true" ]] \
        || echo "medium|<tool>|idempotent-write tool defaults to idempotentHint:false|set idempotentHint:true so retry on transient error is safe"
      ;;
    destructive)
      [[ "$(echo "$anno" | jq -r '.destructiveHint // true')" == "false" ]] \
        && echo "high|<tool>|destructive tool annotated destructiveHint:false|misleads confirmation gate; correct to true"
      [[ "$(echo "$anno" | jq -r '.idempotentHint // false')" == "true" ]] \
        && echo "high|<tool>|destructive tool annotated idempotentHint:true|verify server-side idempotency key; otherwise retries duplicate side effects"
      ;;
    append)
      [[ "$(echo "$anno" | jq -r '.idempotentHint // false')" == "true" ]] \
        && ! echo "$anno" | jq -e '.idempotency_key // empty' >/dev/null \
        && echo "high|<tool>|append tool claims idempotent without idempotency_key|require an idempotency_key parameter or remove the hint"
      ;;
  esac
}
```

## Step 5 — Server-Side Verification for Idempotent Claims

A tool annotated `idempotentHint: true` must actually produce the same end state on repeat calls. Spot-check by invoking the tool twice with the same arguments and diffing results.

```bash
# Pseudo-protocol — adapt to harness
INV1=$(invoke_tool "$tool" "$args")
INV2=$(invoke_tool "$tool" "$args")
diff <(echo "$INV1" | jq -S .) <(echo "$INV2" | jq -S .) >/dev/null \
  || echo "high|$tool|idempotentHint:true but second invocation differs|either remove the hint or fix the tool"
```

For tools with side effects (delete/create/send), do not run twice in production. Inspect the implementation source for one of: pre-existence check, server-issued idempotency key support (per [AWS Builders' Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)), or explicit upsert semantics. Cite the source line in the finding.

## Step 6 — Open-World Hint Audit

`openWorldHint: true` (the spec default) signals the tool's effects extend beyond the local system — relevant for retry budgets and confirmation policy.

```bash
for tool in $TOOLS; do
  OW=$(echo "$ANNO" | jq -r '.openWorldHint // true')
  DESC=$(echo "$TOOL_DEF" | jq -r '.description')
  IS_LOCAL=$(echo "$DESC" | grep -qiE "filesystem|local file|in-memory|cache" && echo true || echo false)
  if [[ "$OW" == "true" && "$IS_LOCAL" == "true" ]]; then
    echo "low|$tool|local-only tool inherits openWorldHint:true default|set openWorldHint:false to reduce unnecessary confirmation"
  fi
done
```

## Step 7 — Per-Tool Scorecard

```markdown
# Audit Report — Tool Idempotency

## Per-tool scorecard

| Tool | Class | readOnly | destructive | idempotent | openWorld | Verified | Top issue |
|------|-------|:--------:|:-----------:|:----------:|:---------:|:--------:|-----------|
| <name> | pure_read | ✅ | ✅ | ✅ | n/a | n/a | <one-line> |

## Findings

| Severity | Tool | Finding | Suggested fix |
|----------|------|---------|---------------|
```

## Idempotency

Read-only against tool catalogs. Step 5's invocation probe sends real requests — coordinate with the operator before running against production tools that incur cost or side effects.

## Output Schema

```markdown
# Audit Tool Idempotency — <repo>

| Tools | Pass | Warn | Fail | Misclaims |
|------:|-----:|-----:|-----:|----------:|
| <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually missing idempotentHint on idempotent writes>
```

## Remediation

For each finding, the fix is a server-side annotation update plus, where applicable, a server-side idempotency-key implementation. The fix template:

```python
# Example: MCP tool registration with explicit annotations
@server.tool(
    name="upsert_record",
    description="Create or update a record by id; safe to retry.",
    annotations={
        "destructiveHint": True,
        "idempotentHint": True,    # implementation enforces upsert semantics
        "readOnlyHint": False,
        "openWorldHint": False,
    },
)
def upsert_record(record_id: str, payload: dict) -> dict: ...
```

Pair with [`audit-tool-descriptions`](audit-tool-descriptions.md) for the description-craft fixes the same tools usually need.

## Related

- [MCP Server Design](../tool-engineering/mcp-server-design.md)
- [MCP Client-Server Architecture](../tool-engineering/mcp-client-server-architecture.md)
- [Idempotent Agent Operations](../agent-design/idempotent-agent-operations.md)
- [Audit Tool Descriptions](audit-tool-descriptions.md)
- [Audit Tool Error Format](audit-tool-error-format.md)
- [Bootstrap MCP Config](bootstrap-mcp-config.md)
