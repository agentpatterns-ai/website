---
title: "Bootstrap Egress Policy"
description: "Generate a network egress allowlist, decompose lethal-trifecta principals into two-leg agents, configure URL exfiltration guards and image-load denial, and validate the trifecta is closed."
tags:
  - tool-agnostic
  - security
aliases:
  - generate egress allowlist
  - close lethal trifecta
  - network egress policy scaffold
---

# Bootstrap Egress Policy

> Generate a network egress allowlist, decompose lethal-trifecta principals, configure URL exfiltration guards, validate the trifecta is closed.

The cheapest leg to remove from the [lethal trifecta](../security/lethal-trifecta-threat-model.md) is usually egress — restrict to a known allowlist, route external operations through a separate non-private-data principal, and block silent side-effect channels (image loads, webhook fan-out). This is the paired remediation for [`audit-lethal-trifecta`](audit-lethal-trifecta.md). Sources: [agent network egress policy](../security/agent-network-egress-policy.md), [URL exfiltration guard](../security/url-exfiltration-guard.md), [action selector pattern](../security/action-selector-pattern.md).

## Step 1 — Detect Current State

```bash
# Existing egress allowlist (if any)
test -f .claude/settings.json && jq '.permissions.allow[] | select(test("curl|wget|http"))' .claude/settings.json

# Sub-agent definitions and their tool inheritance
find .claude/agents -name "*.md" 2>/dev/null

# MCP servers with network access
test -f .claude/settings.json && jq '.mcpServers // empty' .claude/settings.json

# Markdown rendering surfaces (image-load egress)
grep -rE "image_render|markdown_render|html" .claude/skills/*/SKILL.md 2>/dev/null
```

Decision rules:

- **Run [`audit-lethal-trifecta`](audit-lethal-trifecta.md) first** — the audit names which principals are at high severity
- **No high-severity trifecta** → ask whether the user wants preventive scoping anyway; the runbook produces an allowlist either way
- **Multiple high-severity principals** → process the most-privileged one first; the others may inherit from it

## Step 2 — Inventory Required Egress Targets

For each principal that legitimately needs egress, list the hosts:

```bash
# Hosts already invoked in transcripts (best signal)
find ~/.claude/projects -name "*.jsonl" 2>/dev/null \
  | xargs grep -hE '"command":"curl|wget' 2>/dev/null \
  | grep -oE 'https?://[a-zA-Z0-9.-]+' | sort -u

# Hosts referenced in code
grep -rEhoE 'https?://[a-zA-Z0-9.-]+' src/ lib/ 2>/dev/null | sort -u | head -30
```

Categorize each host:

| Category | Examples | Allowlist? |
|----------|----------|:----------:|
| API for the project's purpose | `api.linear.app`, `api.github.com` | yes |
| Webhooks the project publishes | `hooks.slack.com/services/T0...` | yes (host + path prefix) |
| Public CDNs the docs reference | `cdn.jsdelivr.net`, `unpkg.com` | yes (read-only) |
| Speculative / "in case" | <none> | **no** |
| Wildcards | `*.acme.com` | **no** unless every subdomain is trusted |

## Step 3 — Generate the Allowlist

`.claude/settings.json` egress block (merge into existing `permissions`):

```json
{
  "permissions": {
    "allow": [
      "Bash(curl:* https://api.linear.app/*)",
      "Bash(curl:* https://api.github.com/*)",
      "Bash(curl:* https://hooks.slack.com/services/T0*)"
    ],
    "deny": [
      "Bash(curl:* http://*)",
      "Bash(curl:* file://*)",
      "Bash(curl:* gopher://*)",
      "Bash(curl:* http://169.254.169.254/*)",
      "Bash(curl:* http://localhost/*)",
      "Bash(curl:* http://127.*)",
      "Bash(curl:* http://10.*)",
      "Bash(curl:* http://192.168.*)",
      "Bash(wget:*)"
    ],
    "ask": [
      "Bash(curl:*)"
    ]
  }
}
```

Generation rules:

1. **Schema deny** — `http://`, `file://`, `gopher://`, link-local `169.254/16`, RFC1918 ranges (`10/8`, `172.16/12`, `192.168/16`), localhost
2. **Wildcard ask** — any unlisted `curl` falls into ask, never silent allow
3. **wget denied** — single egress tool to allowlist (curl); wget is a parallel surface to maintain
4. **Allowlist is host + path** where possible — `hooks.slack.com/services/T0*` is tighter than `hooks.slack.com/*`

## Step 4 — Decompose Trifecta Principals

For each high-severity principal in the audit, propose decomposition rather than hardening:

```yaml
# Before: web-researcher has all three legs
---
name: web-researcher
tools: [Read, WebFetch, mcp__slack__post]   # private + untrusted + egress
---

# After: split into two two-leg principals
---
name: web-researcher        # private + untrusted, no egress
tools: [Read, WebFetch]
description: |
  Research over web sources; produces a structured handoff payload.
  Does NOT post results — hand off to `publisher` via .claude/state/handoff.json.
---

---
name: publisher              # egress + private (no untrusted content)
tools: [Read, mcp__slack__post]
description: |
  Reads .claude/state/handoff.json and posts to the configured channel.
  Does NOT fetch external URLs or read agent context.
---
```

The two-principal pattern preserves capability while breaking the trifecta. Hand off via a structured payload (`.claude/state/handoff.json`) the publisher reads — never via inline transcript.

## Step 5 — Configure URL Exfiltration Guards

For markdown-rendering channels (chat output, issue comments, PR descriptions), block remote image and link side effects:

```bash
# Pre-output filter: rewrite remote image URLs to local placeholders
# Apply via PostToolUse hook on tools that emit markdown to external sinks
cat > .claude/hooks/strip-remote-images.sh <<'EOF'
#!/usr/bin/env bash
# Strip remote image URLs from agent output that lands in external channels.
# Rationale: image-load is silent egress; an attacker-controlled URL leaks data
# the moment the channel renders the markdown.
set -euo pipefail
EVENT="$(cat)"
TOOL=$(echo "$EVENT" | jq -r '.tool_name // empty')
[[ "$TOOL" =~ ^(mcp__slack__post|mcp__github__add_comment|mcp__linear__create_comment)$ ]] || exit 0

OUTPUT=$(echo "$EVENT" | jq -r '.tool_input.body // .tool_input.text // empty')
SAFE=$(echo "$OUTPUT" | sed -E 's|!\[([^]]*)\]\(https?://[^)]+\)|[image redacted: \1]|g')
echo "$EVENT" | jq --arg s "$SAFE" '.tool_input.body = $s | .tool_input.text = $s' \
  | { read -r modified; echo "$modified"; }
EOF
chmod +x .claude/hooks/strip-remote-images.sh
```

Wire as a PreToolUse hook on the matching tools.

## Step 6 — Validate

```bash
# Egress allowlist is non-empty and host-scoped
jq '.permissions.allow[] | select(test("curl|wget"))' .claude/settings.json

# Internal IP ranges denied
for ip in "127.0.0.1" "169.254.169.254" "10.0.0.1"; do
  jq -e --arg i "$ip" '.permissions.deny[] | select(contains($i))' .claude/settings.json \
    || echo "FAIL: missing deny for $ip"
done

# wget denied
jq -e '.permissions.deny[] | select(. == "Bash(wget:*)")' .claude/settings.json \
  || echo "FAIL: wget not denied"

# Re-run trifecta audit; confirm zero (1,1,1) principals
# (See audit-lethal-trifecta for the matrix.)
```

## Step 7 — Document

```markdown
## Egress policy

Host allowlist in `.claude/settings.json`. Internal IP ranges and non-https schemes denied.
Markdown side effects (remote image loads, link follows) stripped before output via `.claude/hooks/strip-remote-images.sh`.
Trifecta principals decomposed: see `.claude/agents/<name>.md` for the per-principal capability map.
```

## Idempotency

Re-running merges new hosts into the allowlist; never widens the deny scope. Trifecta decompositions are not reversed by re-running.

## Output Schema

```markdown
# Bootstrap Egress Policy — <repo>

| Action | File | Notes |
|--------|------|-------|
| Modified | .claude/settings.json | egress allow: <n>, deny: <n>, ask: <n> |
| Created | .claude/agents/<new>.md | decomposed from <original> |
| Modified | .claude/agents/<original>.md | tools narrowed |
| Created | .claude/hooks/strip-remote-images.sh | wired to <n> tools |

Trifecta status: <CLOSED | <n> principals still at risk>
```

## Related

- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md)
- [Agent Network Egress Policy](../security/agent-network-egress-policy.md)
- [URL Exfiltration Guard](../security/url-exfiltration-guard.md)
- [Action Selector Pattern](../security/action-selector-pattern.md)
- [Audit Lethal Trifecta](audit-lethal-trifecta.md)
- [Audit Permissions and Blast Radius](audit-permissions-blast-radius.md)
- [Bootstrap Permissions Allowlist](bootstrap-permissions-allowlist.md)
