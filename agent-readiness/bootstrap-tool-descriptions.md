---
title: "Bootstrap Tool Descriptions"
description: "Enumerate undocumented or under-specified tools, generate descriptions following trigger-phrase / return-shape / self-contained / preference-signal rules, and validate against the audit runbook."
tags:
  - tool-agnostic
  - cost-performance
aliases:
  - generate tool descriptions
  - rewrite MCP descriptions
  - tool description scaffold
---

# Bootstrap Tool Descriptions

> Enumerate undocumented or under-specified tools, generate descriptions following trigger / return / self-contained / preference rules, validate against the audit.

!!! info "Harness assumption"
    The runbook covers MCP servers and harness-defined tools. Description-craft rules are tool-agnostic — the only harness-specific step is where you patch the description (MCP server source, OpenAPI spec, or harness config). See [Assumptions](index.md#assumptions).

Tool descriptions are the prompt the model reads to decide which tool to call and how. Treated as documentation they fail silently. This runbook is the paired remediation for [`audit-tool-descriptions`](audit-tool-descriptions.md). Rules from [tool description quality](../tool-engineering/tool-description-quality.md), [token-efficient tool design](../tool-engineering/token-efficient-tool-design.md), and [MCP server design](../tool-engineering/mcp-server-design.md).

## Step 1 — Enumerate Tools Needing Work

```bash
# MCP servers
find . -name "mcp.json" -o -name ".mcp.json" 2>/dev/null
test -f .claude/settings.json && jq '.mcpServers // empty' .claude/settings.json

# OpenAPI specs that compile to tools
find . -name "openapi.y*ml" -o -name "openapi.json" 2>/dev/null

# Custom tool definitions in code
grep -rEl '"name":\s*"[a-z_]+"' --include="*.json" --include="*.yaml" \
  --include="*.py" --include="*.ts" 2>/dev/null | head -20
```

Decision rules:

- **No tool surface** → halt; this runbook needs at least one tool to operate on
- **Run [`audit-tool-descriptions`](audit-tool-descriptions.md) first** if it has not been run; the audit names the tools needing work
- **Tools generated from OpenAPI** → patch the OpenAPI `description` fields, not the generated tool definitions; the latter regenerate

## Step 2 — Cluster Overlapping Tools

For each domain (e.g. `filesystem`, `git`, `linear`, `slack`), list the tools that overlap. Each cluster member must name its siblings and when to prefer each.

```python
from collections import defaultdict
clusters = defaultdict(list)
for tool in tools:
    domain = tool["name"].split(".")[0] if "." in tool["name"] else tool["name"].split("_")[0]
    clusters[domain].append(tool)
```

## Step 3 — Generate Each Description

Apply the four-block template per tool:

```
<one-sentence what>. <trigger phrase: use this when X>.
<negative trigger or preference: do not use when Y / prefer <sibling> for Z>.
Returns <return-shape: structure, key fields, exit semantics>.
<argument hints for non-trivial inputs: 1-line example string>.
```

Examples by tool category:

### Read-only filesystem tool

```
Read a file from the filesystem and return its contents as text.
Use this when you need the contents of a known path. Do not use for binary files
(use the dedicated binary tool) or when the path is unknown (use search_files first).
Returns {"content": string, "lines": int, "truncated": bool}; truncated=true when
the file exceeds 2 MB.
```

### Search tool with sibling

```
Search file contents using a regex pattern across the repository.
Use this when looking for a specific symbol, keyword, or pattern in code.
Prefer search_files for filename-pattern matches; prefer this for content matches.
Returns an array of {file, line, match}; capped at 200 results.
Pattern accepts Go-style regex; example: "func\s+New[A-Z]\w+".
```

### Write / mutation tool

```
Create a new GitHub issue in the configured repository.
Use this when the user wants to file a bug, feature, or task as an issue.
Do not use for comments on existing issues (use add_comment) or for PRs (use
create_pull_request). Returns {"number": int, "url": string} on success.
Labels accept comma-separated names; example: "bug,priority:high".
```

### MCP-domain tool (self-contained)

```
For Linear (issue tracker) — list issues matching a filter.
Use this when retrieving issues by state, assignee, or label. Prefer get_issue
for a single issue by ID. Returns an array of {id, title, state, assignee, labels};
capped at 100 results.
Filter accepts Linear's query DSL; example: "state:open AND assignee:me".
```

Generation rules:

1. **Trigger phrase first** — every description starts with what the tool does, then "use this when X"
2. **Negative trigger or sibling preference** — name the cases not to use the tool, or the sibling to prefer
3. **Return shape** — describe the structure, the key fields, and the failure semantics
4. **Domain context for MCP** — descriptions stand alone; the agent may load one without its siblings, so repeat the domain
5. **Argument hints for structured types** — filter syntax, query DSL, regex flavor → 1-line example
6. **≤500 tokens** — long descriptions crowd selection; tighten if over

## Step 4 — Apply Per Tool Surface

### MCP server

Edit the server's tool definition source. Most MCP SDKs accept `description` as a field on the tool registration:

```typescript
server.tool({
  name: "search_files",
  description: "<generated description>",
  inputSchema: { ... }
});
```

For a third-party MCP server you do not control, file a PR upstream rather than wrapping locally.

### OpenAPI

Patch the `description` field on each operation:

```yaml
paths:
  /issues:
    get:
      description: |
        For Linear (issue tracker) — list issues matching a filter.
        Use this when retrieving issues by state, assignee, or label.
        ...
```

### Custom function tools

For function-call schemas defined inline:

```python
TOOLS = [
    {
        "name": "search_files",
        "description": "<generated description>",
        "input_schema": { ... }
    },
]
```

## Step 5 — Add Argument Examples

For arguments with structured string types (filter DSL, regex, query string), add an example to the schema:

```json
{
  "type": "string",
  "description": "Linear filter expression. Example: 'state:open AND assignee:me'"
}
```

Examples in the schema travel with the tool; examples only in the description disappear when the schema is rendered separately.

## Step 6 — Validate

```bash
# Run the audit and confirm zero high-severity findings on the rewritten tools
# (See audit-tool-descriptions for the per-axis checks.)

# Trigger phrase present
for desc in $(extract_descriptions); do
  echo "$desc" | grep -qiE "use (this )?when|invoke when" \
    || echo "FAIL: missing trigger phrase: ${desc:0:60}..."
done

# Token budget per tool
for desc in $(extract_descriptions); do
  TOKENS=$(echo "$desc" | wc -c | awk '{print int($1/4)}')
  [[ $TOKENS -gt 500 ]] && echo "WARN: ${desc:0:40} is ~$TOKENS tokens"
done
```

Then run [`audit-tool-descriptions`](audit-tool-descriptions.md) end-to-end.

## Idempotency

Re-running on a tool that already has a compliant description produces no diff. The first pass writes; subsequent passes detect the existing trigger phrase and skip.

## Output Schema

```markdown
# Bootstrap Tool Descriptions — <repo>

| Surface | Tools rewritten | Avg tokens | Audit pass |
|---------|---------------:|-----------:|:----------:|
| MCP: github | <n> | <n> | ✅ |
| MCP: linear | <n> | <n> | ✅ |
| Custom | <n> | <n> | ⚠️ (<n> findings) |

Cluster preference signals added: <n> pairs
```

## Related

- [Tool Description Quality](../tool-engineering/tool-description-quality.md)
- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [MCP Server Design](../tool-engineering/mcp-server-design.md)
- [Audit Tool Descriptions](audit-tool-descriptions.md)
- [Bootstrap MCP Config](bootstrap-mcp-config.md)
