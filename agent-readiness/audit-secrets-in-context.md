---
title: "Audit Secrets in Context"
description: "Enumerate every agent-readable surface, run pattern and entropy scans for live credentials, cross-check git history for rotation status, and emit findings with rotate-and-purge instructions."
tags:
  - tool-agnostic
  - security
aliases:
  - secrets in agent context
  - agent credential leak scan
  - instruction file secret scan
---

Packaged as: `.claude/skills/agent-readiness-audit-secrets-in-context/`

# Audit Secrets in Context

> Enumerate every agent-readable surface, run pattern and entropy scans for live credentials, cross-check git history for rotation status, emit findings with rotate-and-purge instructions.

!!! info "Harness assumption"
    Surface enumeration includes Claude Code, Cursor, and MCP config paths by default. Add any harness-specific agent-readable files your project uses — every surface a model loads is in scope. See [Assumptions](index.md#assumptions).

Secrets in code are caught by every modern scanner. Secrets in `CLAUDE.md`, in skill examples, in sub-agent system prompts are not — and they propagate further than secrets in code, because skill examples are shared across teams and registries. Rules from [secrets management for agents](../security/secrets-management-for-agents.md) and [credential hygiene for skills](../security/credential-hygiene-agent-skills.md).

This audit runs **first** in any assessment. A high finding halts other audits until rotated.

## Step 1 — Enumerate Surfaces

```bash
# Every file an agent loads
SURFACES=$(find . -maxdepth 5 \( \
  -iname "AGENTS.md" -o -iname "CLAUDE.md" -o -iname "CLAUDE.local.md" -o \
  -iname "copilot-instructions.md" -o -name ".cursorrules" -o \
  -path "*/.cursor/rules/*" -o -path "*/.cursor/mdc/*" -o \
  -path "*/.claude/skills/*/SKILL.md" -o -path "*/.claude/agents/*.md" -o \
  -path "*/.claude/commands/*.md" -o \
  -name "mcp.json" -o -name ".mcp.json" -o \
  -path "*/.claude/settings.json" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*")
```

## Step 2 — Pattern Scan

Run a credential-format regex set over every surface. Use known token formats:

```bash
PATTERNS=(
  # Slack
  'xox[abprs]-[0-9a-zA-Z-]{10,}'
  # Anthropic
  'sk-ant-[a-zA-Z0-9-_]{20,}'
  # OpenAI
  'sk-[a-zA-Z0-9]{32,}'
  # GitHub
  'gh[opsu]_[A-Za-z0-9]{36,}'
  'github_pat_[A-Za-z0-9_]{82}'
  # AWS
  'AKIA[0-9A-Z]{16}'
  'aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}'
  # Google
  'AIza[0-9A-Za-z_-]{35}'
  'ya29\.[0-9A-Za-z_-]+'
  # Generic JWT
  'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
  # Private keys
  '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'
  # Stripe
  'sk_live_[0-9a-zA-Z]{24,}'
  'rk_live_[0-9a-zA-Z]{24,}'
)

for f in $SURFACES; do
  for p in "${PATTERNS[@]}"; do
    grep -nE "$p" "$f" | while read match; do
      LINE=$(echo "$match" | cut -d: -f1)
      MATCHED=$(echo "$match" | cut -d: -f2- | head -c 80)
      echo "high|$f|$LINE|matched secret pattern: $MATCHED|rotate at issuer; remove from file; rewrite git history if pushed"
    done
  done
done
```

If `gitleaks` or `trufflehog` is available, prefer them — both ship richer rule sets and entropy heuristics. Examples:

```bash
gitleaks detect --no-git --source . --redact -v 2>&1 | grep -E "Secret:|File:|Line:"
trufflehog filesystem . --no-update --json 2>/dev/null | jq -r 'select(.Verified) | "\(.SourceMetadata.Data.Filesystem.file)|\(.SourceMetadata.Data.Filesystem.line)|\(.DetectorName)|\(.Redacted)"'
```

## Step 3 — Entropy Scan

For high-entropy strings near credential-shaped keys (catches custom token formats):

```python
import math, re, sys

def shannon_entropy(s):
    if not s: return 0
    counts = {c: s.count(c) for c in set(s)}
    return -sum((n/len(s)) * math.log2(n/len(s)) for n in counts.values())

CREDENTIAL_KEYS = re.compile(
    r'(?i)\b(api[_-]?key|secret|password|passwd|token|access[_-]?key|auth)\s*[=:]\s*["\']?([A-Za-z0-9+/=_-]{20,})',
)

for line_no, line in enumerate(open(path), 1):
    for m in CREDENTIAL_KEYS.finditer(line):
        candidate = m.group(2)
        if shannon_entropy(candidate) >= 4.0:
            print(f"high|{path}|{line_no}|high-entropy value next to credential key|rotate and remove")
```

## Step 4 — Endpoint Exposure

Internal hostnames, staging URLs, private subdomains in instruction files leak topology:

```bash
INTERNAL_PATTERNS=(
  '\.local\b'
  '\.internal\b'
  '\.corp\b'
  'staging-[a-z]+\.'
  'dev-[a-z]+\.'
  'jumpbox|bastion'
)
for f in $SURFACES; do
  for p in "${INTERNAL_PATTERNS[@]}"; do
    grep -nE "$p" "$f" | while read match; do
      LINE=$(echo "$match" | cut -d: -f1)
      echo "medium|$f|$LINE|internal hostname/endpoint pattern|generalize or remove"
    done
  done
done
```

## Step 5 — Path-to-Secret References

Detect references to credential-bearing files the agent might be told to read:

```bash
PATHS=("~/.aws/credentials" "~/.aws/config" "~/.ssh/id_" ".env.production" ".env.local" "service-account.json")
for f in $SURFACES; do
  for path in "${PATHS[@]}"; do
    grep -nF "$path" "$f" | while read match; do
      LINE=$(echo "$match" | cut -d: -f1)
      echo "medium|$f|$LINE|references credential path: $path|rephrase or remove; do not direct agents to credential files"
    done
  done
done
```

## Step 6 — Skill Example Secrets

Skill examples must use placeholders, not live values:

```bash
for skill in $(find . -path "*/skills/*/SKILL.md"); do
  # Look for tokens inside fenced code blocks (examples)
  awk '/^```/{n++} n%2==1 {print NR ":" $0}' "$skill" | while read line; do
    LINE_NO=$(echo "$line" | cut -d: -f1)
    CONTENT=$(echo "$line" | cut -d: -f2-)
    for p in "${PATTERNS[@]}"; do
      echo "$CONTENT" | grep -qE "$p" && \
        echo "high|$skill|$LINE_NO|skill example contains live-format secret|replace with placeholder (e.g. PLACEHOLDER, sk-...REDACTED)"
    done
  done
done
```

## Step 7 — Cross-Check Git History

For each finding, check whether the secret was rotated post-commit:

```bash
for finding_path in $FOUND_PATHS; do
  # When was the line last touched?
  LAST_COMMIT=$(git log -n 1 --format="%H %ai" -- "$finding_path")
  # Was the secret pattern ever pushed?
  if git log --all --oneline -p -- "$finding_path" | grep -qE "<the secret pattern>"; then
    echo "info|$finding_path|secret pushed in git history (commit: $LAST_COMMIT)|history rewrite or repo replacement may be required after rotation"
  fi
done
```

## Step 8 — Emit Report

```markdown
# Audit Report — Secrets in Context

> <n> findings: <high> high (must rotate), <medium> medium, <low> low.

## Findings

| Severity | Surface | Line | Finding | Action |
|----------|---------|-----:|---------|--------|
| high | CLAUDE.md | 47 | OpenAI key matched | rotate; remove; rewrite history (pushed 3 days ago) |
| high | skills/post-to-slack/SKILL.md | 112 | Slack token in example | rotate; replace with placeholder |
| medium | AGENTS.md | 88 | Internal hostname `*.acme.local` | generalize |

## Rotate-and-purge sequence (per high finding)

1. Revoke the credential at the issuer (the API console)
2. Replace in the secret store / env-var injection layer
3. Remove the literal value from the file
4. If the secret was pushed: rewrite git history (`git filter-repo`) or replace the repo and force re-clone
5. Notify any downstream consumers that may have cached the value
```

## Step 9 — Hand Off

If any **high** finding is present, halt the broader assessment. Surface only the rotation list to the user; the user must rotate before any other readiness work proceeds. Medium and low findings can be batched into a follow-up.

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Secrets in Context — <repo>

| Severity | Findings |
|----------|---------:|
| high | <n> |
| medium | <n> |
| low | <n> |

Status: <CLEAN | ROTATE REQUIRED — N high findings>
```

## Related

- [Secrets Management for Agents](../security/secrets-management-for-agents.md)
- [Credential Hygiene for Agent Skills](../security/credential-hygiene-agent-skills.md)
- [Skill Supply-Chain Poisoning](../security/skill-supply-chain-poisoning.md)
- [Defense in Depth for Agent Safety](../security/defense-in-depth-agent-safety.md)
