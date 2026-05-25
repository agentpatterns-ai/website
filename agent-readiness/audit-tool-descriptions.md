---
title: "Audit Tool Descriptions"
description: "Enumerate tool and MCP server descriptions, score each on trigger phrases, return shape, self-containment, preference signals, and token cost, and emit per-tool findings."
tags:
  - tool-agnostic
  - cost-performance
aliases:
  - tool description audit
  - MCP description quality check
  - tool prompt audit
---

Packaged as: `.claude/skills/agent-readiness-audit-tool-descriptions/`

# Audit Tool Descriptions

> Enumerate tool and MCP server descriptions, score on trigger phrases, return shape, self-containment, preference signals, and token cost.

!!! info "Harness assumption"
    The runbook covers MCP servers and harness-defined tools (Claude Code, Cursor, Copilot). The scoring rubric is tool-agnostic — it applies to any description the model reads when choosing a tool. See [Assumptions](index.md#assumptions).

Tool descriptions are the prompt the model reads to decide which tool to call and how. Treated as documentation they fail silently — the agent calls the wrong tool, hallucinates arguments, or skips a tool whose value is buried. Rules from [tool description quality](../tool-engineering/tool-description-quality.md), [token-efficient tool design](../tool-engineering/token-efficient-tool-design.md), and [MCP server design](../tool-engineering/mcp-server-design.md).

## Step 1 — Enumerate Tools

```bash
# MCP server configs
find . -name "mcp.json" -o -name ".mcp.json" 2>/dev/null
test -f .claude/settings.json && jq '.mcpServers // empty' .claude/settings.json

# Custom tool definitions (varies by harness)
find . -path "*/tools/*.json" -o -path "*/tools/*.yaml" 2>/dev/null

# OpenAPI specs that compile to tools
find . -name "openapi.y*ml" -o -name "openapi.json" 2>/dev/null
```

For each MCP server, fetch the live tool list (servers expose this via `tools/list`):

```bash
# For each configured server, query the tool inventory
# (Run via the harness or via mcp-inspector tooling.)
```

For each tool, capture: `name`, `description`, `inputSchema`.

## Step 2 — Score Each Tool

Build a per-tool scorecard. Each axis maps to a finding if it fails:

| Axis | Test | Severity if missing |
|------|------|---------------------|
| Trigger phrase | description contains "use (this )?when X" | high |
| Negative trigger | "do not use when" / contrast with sibling | medium |
| Return shape | description names what is returned (dict shape, exit code, etc.) | high |
| Self-containment (MCP) | no references to other tools' docs | high |
| Domain context | description names the domain (`for git operations…`) | medium |
| Argument hints | every non-trivial argument has an example | medium |
| Token cost | description ≤500 tokens | low |

```python
import json, re

def score_tool(tool):
    desc = tool["description"]
    findings = []
    if not re.search(r"\buse\b.*\bwhen\b", desc, re.I):
        findings.append(("high", tool["name"], "no trigger phrase",
                         "rewrite description starting with 'use this when X'"))
    if not re.search(r"\bdo not use\b|\bskip when\b|\bprefer\b.*\bover\b", desc, re.I):
        findings.append(("medium", tool["name"], "no negative trigger or preference signal",
                         "add a sibling-tool contrast"))
    if not re.search(r"return|emit|produce|output", desc, re.I):
        findings.append(("high", tool["name"], "return shape not described",
                         "describe what the tool returns and the result schema"))
    # Argument hints
    for arg, schema in (tool.get("inputSchema", {}).get("properties", {}) or {}).items():
        if schema.get("type") == "string" and "example" not in (schema.get("description") or ""):
            if re.search(r"filter|query|expression|pattern", schema.get("description") or "", re.I):
                findings.append(("medium", f"{tool['name']}.{arg}",
                                 f"argument is structured ({arg}) but lacks example",
                                 "add a one-line example string"))
    tokens = len(desc) // 4  # rough
    if tokens > 500:
        findings.append(("low", tool["name"], f"description is ~{tokens} tokens",
                         "tighten to ≤500 tokens"))
    return findings
```

## Step 2b — Poka-Yoke Parameter Constraints

Tool descriptions that under-specify parameters let the model produce calls that deterministic guards reject — wasted turns. Detect parameter docs that name a type (e.g., "string") but not the constraint that prevents whole failure classes (e.g., "absolute filepath only", "max 100 lines per page", "ISO-8601 timestamp"). Source: [`poka-yoke-agent-tools`](../tool-engineering/poka-yoke-agent-tools.md).

```python
# Heuristic: per-parameter description must name a constraint, not just a type
for tool in tools:
    schema = tool.get("input_schema", {}).get("properties", {})
    for pname, pdef in schema.items():
        pdesc = pdef.get("description", "")
        # Constraint markers: format/regex/range/enum/file-path/path-prefix/length-cap
        if not re.search(r"absolute|relative|max |min |regex|enum|^/|prefix|cap|page|chunk|line", pdesc, re.I):
            findings.append(("low", tool["name"],
                             f"parameter {pname} description names type but not constraint",
                             "add a poka-yoke constraint (e.g., 'absolute filepath only', 'max 100 lines per page')"))
```

Examples of constraints that eliminate failure classes:

- File reads: "absolute filepath only" (eliminates relative-path drift across `cwd` changes)
- Long-output tools: "max 100 lines per page; use `offset` for next page" (eliminates context-bloat from a single call)
- Timestamps: "ISO-8601 with TZ" (eliminates parse ambiguity at the receiver)

## Step 3 — Cluster Overlapping Tools

Cluster tools by capability (same domain, similar action). For each cluster ≥2:

```python
# Cluster tools by name prefix or capability keywords
from collections import defaultdict
clusters = defaultdict(list)
for tool in tools:
    key = tool["name"].split(".")[0]  # e.g. "filesystem", "git", "linear"
    clusters[key].append(tool)

# For each multi-tool cluster, confirm each tool's description names the others
for domain, members in clusters.items():
    if len(members) < 2:
        continue
    names = {t["name"] for t in members}
    for tool in members:
        siblings_named = {n for n in names if n != tool["name"] and n in tool["description"]}
        if not siblings_named:
            findings.append(("medium", tool["name"],
                             f"overlapping tools in {domain} cluster but no sibling named",
                             f"add: 'prefer <sibling> when <condition>'"))
```

## Step 4 — MCP Self-Containment Check

For MCP tools specifically, the description must stand alone — agents may load one tool description without its siblings. Detect language that assumes co-loading:

```python
SHARED_REFS = re.compile(r"see (another|adjacent|related) tool|as described above|as the other tool", re.I)
for tool in mcp_tools:
    if SHARED_REFS.search(tool["description"]):
        findings.append(("high", tool["name"], "description references adjacent tool",
                         "rewrite as self-contained — repeat domain context inline"))
```

## Step 4b — ToolLeak Argument-Signature Check

A subset of tool descriptions and `inputSchema` properties exist solely to elicit context leakage — they ask the model to populate an argument with "the system prompt", "any secrets", "the conversation so far", or similar. This is the ToolLeak class of MCP attack ([`tool-invocation-attack-surface`](../security/tool-invocation-attack-surface.md) §Attack 1: ToolLeak): a malicious server defines a benign-named tool whose schema asks the model to dump its context as an argument value.

```python
LEAK_PATTERNS = re.compile(
    r"\b(system prompt|conversation (so far|history)|"
    r"prior (messages|context)|secrets?|credentials?|api[_ ]?key|"
    r"private (data|files|context)|all available context|"
    r"any (sensitive|confidential) (data|information))\b",
    re.I,
)

for tool in tools:
    desc = tool.get("description", "")
    if LEAK_PATTERNS.search(desc):
        findings.append(("high", tool["name"],
                         "description asks for system prompt or secret-class data as argument",
                         "ToolLeak signature — refuse to wire this tool, or rewrite to avoid context-extraction phrasing"))
    schema = tool.get("inputSchema", {})
    for prop_name, prop_def in (schema.get("properties") or {}).items():
        prop_desc = (prop_def.get("description") or "")
        if LEAK_PATTERNS.search(prop_name) or LEAK_PATTERNS.search(prop_desc):
            findings.append(("high", f"{tool['name']}.{prop_name}",
                             "argument schema asks for system prompt or secret-class data",
                             "ToolLeak signature — drop the argument or wire the tool through a sanitizing proxy"))
```

A finding here means the tool itself should be rejected at install time, not just reworded. ToolLeak signatures pair with [`audit-secrets-in-context`](audit-secrets-in-context.md): if the tool runs in a session that holds private data, the description is enough to trigger leak.

## Step 4c — Tool-Search Discoverability

When the harness exposes a tool-search tool (Claude Code's `ToolSearch`, MCP-spec [advanced tool use §tool search](../tool-engineering/advanced-tool-use.md)), tool descriptions are also search documents. A tool whose description omits the trigger phrases its caller would query loses every dispatch where the model loads tools on demand instead of pre-loaded.

```python
# For each tool in a server that supports defer_loading or tool search
TRIGGER_VOCAB = {
    "github":  ["pull request", "issue", "commit", "branch", "review", "pr", "release"],
    "git":     ["commit", "branch", "merge", "rebase", "diff", "checkout", "stash"],
    "fs":      ["read", "write", "list directory", "search files", "glob"],
    "linear":  ["issue", "ticket", "cycle", "project", "team"],
    "slack":   ["message", "channel", "thread", "user", "react"],
}

def discoverability_findings(tool, server_supports_search):
    if not server_supports_search:
        return []
    desc = tool["description"].lower()
    name = tool["name"].lower()
    domain = name.split(".")[0]
    vocab = TRIGGER_VOCAB.get(domain, [])
    misses = [w for w in vocab if w not in desc]
    if vocab and len(misses) > len(vocab) // 2:
        return [("medium", tool["name"],
                 f"description omits {len(misses)} of {len(vocab)} domain trigger words ({', '.join(misses[:5])})",
                 "weave the missing trigger phrases into the description so tool search matches user intent")]
    return []
```

Also confirm that servers exposing more than ~30 tools opt into deferred loading per [Advanced Tool Use §Tool Search](../tool-engineering/advanced-tool-use.md):

```bash
test -f .mcp.json && jq -r '.mcpServers | to_entries[] |
  "\(.key)\t\(.value.tools // [] | length)\t\(.value.defer_loading // false)"' .mcp.json | \
  awk -F'\t' '$2 > 30 && $3 == "false" {print "medium|" $1 "|" $2 " tools without defer_loading|set defer_loading: true and rely on tool search"}'
```

## Step 5 — Emit the Report

```markdown
# Audit Report — Tool Descriptions

## Per-tool scorecard

| Tool | Trigger | Neg/Pref | Return | Self-cont. | Args | Tokens |
|------|:-------:|:--------:|:------:|:----------:|:----:|------:|
| <name> | ✅ | ⚠️ | ❌ | ✅ | ⚠️ | <n> |

## Cluster analysis

| Cluster | Tools | Preference signals present |
|---------|------:|:--------------------------:|
| filesystem.* | <n> | ⚠️ (only <n>/<n>) |

## Top findings

| Severity | Tool | Finding | Suggested rewrite |
|----------|------|---------|-------------------|
| high | <name> | <finding> | <one-line rewrite> |
```

## Step 6 — Hand Off

For each high-severity finding, propose a one-line description rewrite the user can accept. For overlapping clusters, propose preference-signal language for both tools simultaneously (so the contrast is mutual).

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Tool Descriptions — <repo>

| Tools | Pass | Warn | Fail |
|------:|-----:|-----:|-----:|
| <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually missing trigger phrases or return-shape>
```

## Remediation

- [Bootstrap Tool Descriptions](bootstrap-tool-descriptions.md) — rewrite descriptions following the trigger / return / self-contained / preference rules
- [Bootstrap MCP Config](bootstrap-mcp-config.md) — when missing-description findings stem from a loose MCP surface

## Related

- [Tool Description Quality](../tool-engineering/tool-description-quality.md)
- [Token-Efficient Tool Design](../tool-engineering/token-efficient-tool-design.md)
- [MCP Server Design](../tool-engineering/mcp-server-design.md)
- [Audit Skill Quality](audit-skill-quality.md)
- [Audit Tool Error Format](audit-tool-error-format.md)
- [Tool Invocation Attack Surface](../security/tool-invocation-attack-surface.md)
- [Audit Secrets in Context](audit-secrets-in-context.md)
