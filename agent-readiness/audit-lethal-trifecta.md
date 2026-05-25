---
title: "Audit Lethal Trifecta"
description: "Enumerate every principal, classify each tool as private-data, untrusted-content, or egress, build the per-principal trifecta matrix, flag any (1,1,1), and recommend the cheapest leg to remove."
tags:
  - tool-agnostic
  - security
aliases:
  - lethal trifecta audit
  - trifecta exfiltration check
  - prompt injection trifecta map
---

Packaged as: `.claude/skills/agent-readiness-audit-lethal-trifecta/`

# Audit Lethal Trifecta

> Enumerate every principal, classify each tool, build the per-principal three-leg matrix, flag any complete trifecta, recommend the cheapest leg to remove.

!!! info "Harness assumption"
    Principal discovery uses Claude Code paths (`.claude/settings.json`, `.claude/agents/`) and CI workflow files. The trifecta model itself (private data + untrusted content + egress) is harness-agnostic — translate principal enumeration to your harness's sub-agent and automation surfaces. See [Assumptions](index.md#assumptions).

The [lethal trifecta](../security/lethal-trifecta-threat-model.md) is the smallest configuration that turns prompt injection from curiosity to exfiltration. An agent that reads private data, processes untrusted content, and can communicate externally is a complete attack surface — adding any defense to that combination is harder than removing one of the three legs.

## Step 1 — Enumerate Principals

```bash
# Main agent + sub-agents (covered in audit-permissions-blast-radius)
test -f .claude/settings.json && echo "principal: main"
find .claude/agents -name "*.md" -exec basename {} .md \; 2>/dev/null | sed 's/^/principal: /'

# Automations
find .github/workflows -name "*.y*ml" -exec basename {} \; 2>/dev/null | sed 's/^/principal: ci:/'

# MCP-mediated principals
find . -name "mcp.json" -o -name ".mcp.json" 2>/dev/null | while read f; do
  jq -r 'keys[]' "$f" 2>/dev/null | sed 's/^/principal: mcp:/'
done
```

## Step 2 — Classify Tools by Leg

For each principal's tool list, classify every tool against the three legs. A single tool can grant multiple legs (e.g., a `Bash` allowlist that includes `curl` grants both shell power and egress).

| Leg | What grants it | Examples |
|-----|----------------|----------|
| **Private data** | tool reads private/internal data | `Read` over project source, DB tools, secrets store, internal docs MCP |
| **Untrusted content** | tool returns content the operator does not author | `WebFetch`, RSS readers, GitHub issue body fetchers, email readers, search-result tools |
| **External egress** | tool reaches outside the trust boundary | `Bash` with `curl`/`wget`, webhook tools, email send tools, image rendering of remote URLs in markdown |

Classification table for common tools (extend per project):

```python
LEG_MAP = {
    "Read":               {"private_data"},
    "Edit":               set(),
    "Write":              set(),
    "Bash":               set(),  # depends on allowlist
    "WebFetch":           {"untrusted_content", "external_egress"},
    "WebSearch":          {"untrusted_content"},
    "mcp__github__issue_read":   {"untrusted_content"},
    "mcp__github__issue_write":  {"external_egress"},
    "mcp__slack__post":          {"external_egress"},
    "mcp__email__send":          {"external_egress"},
    "mcp__http__*":              {"external_egress"},
}

def legs_for_bash(allowlist):
    legs = set()
    if any(re.search(r"\b(curl|wget|http|fetch)\b", a) for a in allowlist):
        legs |= {"untrusted_content", "external_egress"}
    if any(re.search(r"\bgit (push|pull)\b", a) for a in allowlist):
        legs |= {"external_egress"}
    return legs
```

## Step 3 — Identify Indirect Egress

These count as egress even when the tool is not explicitly named "fetch":

- Markdown rendering with remote image loads (silent GET on the image URL)
- Webhook side effects (issue post that triggers downstream automation)
- Logging to a remote sink (errors that include sensitive content)
- Any tool whose output is rendered to a downstream channel the operator does not control

Detect heuristically:

```bash
# Markdown emitters with image-rendering UIs
grep -rE "image|markdown_render|html_render" .claude/skills/*/SKILL.md 2>/dev/null
# Webhook-class tools
grep -rE "webhook|notify|post_to" .claude/agents/*.md 2>/dev/null
```

## Step 4 — Build the Trifecta Matrix

```python
matrix = []
for principal in principals:
    legs = set()
    for tool in principal["tools"]:
        legs |= LEG_MAP.get(tool, set())
    legs |= legs_for_bash(principal.get("bash_allow", []))
    legs |= indirect_egress(principal)
    matrix.append({
        "principal": principal["name"],
        "private_data": "private_data" in legs,
        "untrusted_content": "untrusted_content" in legs,
        "external_egress": "external_egress" in legs,
        "legs_count": sum([
            "private_data" in legs,
            "untrusted_content" in legs,
            "external_egress" in legs,
        ]),
    })
```

## Step 5 — Score Severity

```python
for row in matrix:
    if row["legs_count"] == 3:
        row["severity"] = "high"
        row["verdict"] = "TRIFECTA — direct exfiltration path"
    elif row["legs_count"] == 2 and row.get("indirect_third"):
        row["severity"] = "high"
        row["verdict"] = "indirect trifecta — image-load or webhook side effect closes the loop"
    elif row["legs_count"] == 2:
        row["severity"] = "medium"
        row["verdict"] = "two legs — third may emerge from a future tool addition"
    else:
        row["severity"] = "none"
        row["verdict"] = "safe"
```

## Step 6 — Recommend Leg Removal

For each high-severity row, propose the cheapest leg to remove. Heuristic:

1. **External egress is usually cheapest to drop** — restrict to a specific allowlist or route through a non-trifecta principal
2. **Untrusted content** can be moved behind a sanitization layer (LLM-as-filter, schema validation) — but the agent still receives the content, so this is not a true removal; prefer egress restriction first
3. **Private data** scope is hardest to shrink without breaking the principal's purpose — last resort

For each row, name the proposed action and the remaining configuration:

```python
def recommend(row):
    if row["external_egress"]:
        return ("remove egress", "route external operations through a separate, non-private-data principal")
    if row["untrusted_content"]:
        return ("remove untrusted content",
                "drop WebFetch/issue-reading tools; pass content through a sanitizing pre-step")
    return ("decompose principal",
            "split into two principals each holding only two legs")
```

## Step 7 — Emit Report

```markdown
# Audit Report — Lethal Trifecta

## Trifecta matrix

| Principal | Private data | Untrusted content | External egress | Verdict |
|-----------|:------------:|:-----------------:|:---------------:|:-------:|
| Main agent | ✅ | ✅ | ❌ | safe |
| sub: web-research | ✅ | ✅ | ✅ | **HIGH — TRIFECTA** |
| sub: publisher | ✅ | ❌ | ✅ | safe |
| ci: pr-bot | ✅ | ✅ | ❌ | safe |

## Findings

| Severity | Principal | Verdict | Recommended remediation |
|----------|-----------|---------|--------------------------|
| high | sub: web-research | reads source + fetches URLs + posts to Slack | remove egress: route Slack via `publisher` with a structured handoff |
| medium | sub: publisher | two legs (private + egress); no untrusted content today | watch for future additions of WebFetch / issue-read |
```

## Step 8 — Hand Off

For each high-severity row, propose the configuration change in `.claude/agents/<name>.md` or `.claude/settings.json`. Decompose principals before adding defenses — two two-legged agents are safer than one three-legged agent with hardening.

## Step 9 — Per Sub-Agent Decomposition

The matrix above treats each sub-agent file as a single principal. When a sub-agent's `tools:` list is missing or wildcarded, it inherits the parent's full toolset and acquires every leg the parent holds — silently. Run [`audit-subagent-definitions`](audit-subagent-definitions.md) Step 4 first; any sub-agent flagged as a "local trifecta" there appears as a (1,1,1) row here, regardless of whether the parent itself is safe. Do not consider this trifecta audit complete until the sub-agent definition audit has run and its findings have been merged into the matrix above. Sub-agent decomposition rules from [`subagent-schema-level-tool-filtering`](../multi-agent/subagent-schema-level-tool-filtering.md).

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Lethal Trifecta — <repo>

| Principals | (1,1,1) | Indirect | Two-leg | Safe |
|-----------:|--------:|---------:|--------:|-----:|
| <n> | <n> | <n> | <n> | <n> |

Status: <SAFE | TRIFECTA — N principals at risk>
```

## Remediation

- [Bootstrap Egress Policy](bootstrap-egress-policy.md) — host allowlist + principal decomposition; the cheapest leg to remove
- [Bootstrap Permissions Allowlist](bootstrap-permissions-allowlist.md) — when the trifecta is closed by tighter Bash + sub-agent tools

## Related

- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md)
- [Action Selector Pattern](../security/action-selector-pattern.md)
- [URL Exfiltration Guard](../security/url-exfiltration-guard.md)
- [Defense in Depth for Agent Safety](../security/defense-in-depth-agent-safety.md)
- [Audit Permissions and Blast Radius](audit-permissions-blast-radius.md)
- [Audit Sub-Agent Definitions](audit-subagent-definitions.md)
- [Subagent Schema-Level Tool Filtering](../multi-agent/subagent-schema-level-tool-filtering.md)
