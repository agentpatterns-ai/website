---
title: "Audit Permissions and Blast Radius"
description: "Enumerate every principal that can act, build a capability matrix against least-privilege rules, detect missing deny rules and over-permissioned sub-agents, and emit prioritized remediations."
tags:
  - tool-agnostic
  - security
aliases:
  - permissions audit
  - blast radius assessment
  - least privilege audit
---

Packaged as: [`.claude/skills/agent-readiness-audit-permissions-blast-radius`](../../.claude/skills/agent-readiness-audit-permissions-blast-radius/SKILL.md)

# Audit Permissions and Blast Radius

> Enumerate every principal that can act, build a capability matrix against least-privilege rules, detect missing deny rules and over-permissioned sub-agents.

!!! info "Harness assumption"
    Principal enumeration parses `.claude/settings.json` and `.claude/agents/` by default. Translate the JSON paths and sub-agent file format to your harness's equivalents — the rules (least privilege, sensitive-path deny, sub-agent isolation) are tool-agnostic. See [Assumptions](index.md#assumptions).

A capable agent with no permission boundary is a production incident waiting for a prompt-injection vector. [Blast radius containment](../security/blast-radius-containment.md) at the runtime layer is what prevents agent decisions from translating into agent damage. Rules from [permission-gated commands](../security/permission-gated-commands.md) and [safe outputs pattern](../security/safe-outputs-pattern.md).

## Step 1 — Enumerate Principals

A "principal" is anything that can take action: the main agent, each sub-agent, each automation that runs unattended.

Every JSON config file is parse-checked first; a malformed file becomes a high-severity finding rather than a silent absence (a swallowed parse error reads as "no config exists" and produces a false-clean audit):

```bash
parse_or_finding() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  if ! jq empty "$f" 2>/tmp/_jqerr; then
    echo "high|$f|-|JSON parse error: $(cat /tmp/_jqerr)|fix syntax before audit can proceed"
    return 1
  fi
  return 0
}

# Main agent settings
parse_or_finding .claude/settings.json && jq '.permissions' .claude/settings.json

# Sub-agents
find .claude/agents -name "*.md" 2>/dev/null | while read f; do
  echo "--- $f"
  python3 -c "import sys, frontmatter; p=frontmatter.load(sys.argv[1]); print(p.get('tools'), p.get('model'))" "$f"
done

# CI / automation
find .github/workflows -name "*.y*ml" | while read wf; do
  yq '.jobs[].permissions, .permissions' "$wf" 2>/dev/null
done

# MCP server access
find . -name "mcp.json" -o -name ".mcp.json" 2>/dev/null

# Bash allowlist sources
test -f .claude/settings.json && jq '.permissions.allow, .permissions.deny' .claude/settings.json
```

## Step 2 — Build the Capability Matrix

For each principal, classify against capability columns:

| Capability | Detection |
|------------|-----------|
| Read | always present unless explicitly denied |
| Write (Edit/Write tools) | tool list contains `Edit` / `Write` / `MultiEdit` |
| Bash | tool list contains `Bash` |
| Network egress | Bash allowlist permits `curl`/`wget`/`fetch`, MCP exposes HTTP, or webhook tool |
| Git push | Bash allowlist permits `git push`, or dedicated git-push tool |
| Secret read | tool can read `.env*`, secrets/, key paths |

```python
def classify(principal):
    caps = {"read": True}
    tools = principal.get("tools", [])
    bash_allow = principal.get("bash_allow", [])
    caps["write"] = any(t in tools for t in ["Edit", "Write", "MultiEdit"])
    caps["bash"] = "Bash" in tools
    caps["net"] = (
        any(re.search(r"\b(curl|wget|fetch|http)\b", a) for a in bash_allow) or
        any(t.startswith("mcp__http") for t in tools)
    )
    caps["git_push"] = any(re.search(r"\bgit push\b", a) for a in bash_allow)
    deny = principal.get("deny_paths", []) + principal.get("bash_deny", [])
    caps["secret_read"] = not any(p in str(deny) for p in [".env", "secrets/", "id_rsa", "credentials"])
    return caps
```

## Step 3 — Run Default-Deny and Sensitive-Path Checks

### Default-deny posture

```bash
# Bash allowlist exists and is not "*"
# Parse-checked above; jq errors here mean the file changed mid-audit (re-run)
ALLOW=$(jq -r '.permissions.allow[]?' .claude/settings.json)
if [[ -z "$ALLOW" ]]; then
  echo "high|settings.json|no allowlist — every tool implicitly allowed|add explicit allow list"
elif echo "$ALLOW" | grep -q "^Bash$"; then
  echo "medium|settings.json|Bash is allowed unrestricted|narrow to specific commands"
fi
```

### Sensitive-path deny rules

```bash
# Required deny patterns
REQUIRED_DENIES=(".env" ".env.production" "secrets/" "*.pem" "*.key" "id_rsa")
DENY=$(jq -r '.permissions.deny[]?' .claude/settings.json)
for pattern in "${REQUIRED_DENIES[@]}"; do
  echo "$DENY" | grep -qF "$pattern" || \
    echo "high|settings.json|missing deny for $pattern|add to deny list if pattern exists in repo"
done

# Verify the patterns match real files
for pattern in "${REQUIRED_DENIES[@]}"; do
  find . -name "$pattern" ! -path "*/node_modules/*" 2>/dev/null | head -1 | grep -q . && \
    echo "info|repo|sensitive file matching '$pattern' present — confirm deny rule covers it"
done
```

### Destructive shell allowlist

```bash
# Forbidden patterns: rm -rf, curl | sh, force push to protected refs
echo "$ALLOW" | grep -qE "rm -rf|sudo|curl.*\| *(ba)?sh" && \
  echo "high|settings.json|destructive pattern allowed: $(echo "$ALLOW" | grep -E 'rm -rf|curl.*\|.*sh')|deny these explicitly"
```

### Network egress

```bash
# If any principal has net=true, confirm there's an allowlist of hosts
if echo "$ALLOW" | grep -qE "curl|wget"; then
  if ! echo "$ALLOW" | grep -qE "https?://[a-z]"; then
    echo "high|settings.json|network egress allowed without host allowlist|restrict to known hosts"
  fi
fi
```

## Step 4 — Sub-Agent Tool Restriction Check

For each sub-agent, confirm it declares only the tools it needs:

```python
for agent_file in subagents:
    fm = frontmatter.load(agent_file).metadata
    tools = fm.get("tools")
    if not tools or tools == "*" or tools is True:
        findings.append(("medium", agent_file,
                         "sub-agent inherits all tools",
                         "declare a minimal tools list in frontmatter"))
    elif "Bash" in tools and not fm.get("description", "").lower().count("shell"):
        findings.append(("low", agent_file,
                         "Bash granted but description does not mention shell use",
                         "remove Bash if not needed"))
```

## Step 5 — Approval-Gate Verification

For each high-risk operation, confirm a runtime approval gate exists:

| Operation | Required gate |
|-----------|---------------|
| Destructive Bash (`rm -rf`, `find -delete`) | not in allowlist; require approval |
| `git push` to protected branch | hook or branch protection on remote |
| Secret read | denied at filesystem level |
| Network call to non-allowlisted host | denied or gated |

## Step 6 — Safe-Outputs Declaration (CI / Automations)

For GitHub Actions workflows that run agents:

```bash
for wf in .github/workflows/*.y*ml; do
  PERMS=$(yq '.jobs[].permissions // .permissions // empty' "$wf")
  if [[ -z "$PERMS" || "$PERMS" == "write-all" ]]; then
    echo "high|$wf|workflow has write-all or unscoped permissions|set permissions: read-all + per-step writes"
  fi
done
```

## Step 7 — Emit Capability Matrix Report

```markdown
# Audit Report — Permissions and Blast Radius

## Capability matrix

| Principal | Read | Write | Bash | Net | Git push | Secret read |
|-----------|:----:|:-----:|:----:|:---:|:--------:|:-----------:|
| Main agent | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| sub-agent: review | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| sub-agent: publish | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| ci: agent-loop | ✅ | ⚠️ | ✅ | ❌ | ❌ | ❌ |

## Findings

| Severity | Principal | Finding | Action |
|----------|-----------|---------|--------|
| high | <p> | <finding> | <action> |
```

## Step 8 — Hand Off

For each high-severity finding, propose the deny rule, allowlist edit, or workflow permissions block to apply. Default-deny gaps and sensitive-path-deny gaps must be closed before any other agent-readiness work proceeds.

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Permissions and Blast Radius — <repo>

| Principals | Cells red | Default-deny | Sensitive-path | Net allowlisted |
|-----------:|----------:|:------------:|:--------------:|:---------------:|
| <n> | <n> | <yes/no> | <yes/no> | <yes/no> |

Top fix: <one-liner — usually missing deny rule or destructive bash>
```

## Remediation

- [Bootstrap Permissions Allowlist](bootstrap-permissions-allowlist.md) — generate the default-deny `permissions` block this audit looks for
- [Bootstrap Egress Policy](bootstrap-egress-policy.md) — narrow network egress when this audit flags it

## Related

- [Blast Radius Containment](../security/blast-radius-containment.md)
- [Permission-Gated Commands](../security/permission-gated-commands.md)
- [Safe Outputs Pattern](../security/safe-outputs-pattern.md)
- [Defense in Depth for Agent Safety](../security/defense-in-depth-agent-safety.md)
- [Audit Lethal Trifecta](audit-lethal-trifecta.md)
