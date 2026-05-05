---
title: "Bootstrap Permissions Allowlist"
description: "Detect existing tool usage from transcripts and CI, generate a default-deny .claude/settings.json permissions block with sensitive-path deny rules and a tight Bash allowlist, and validate against blast-radius rules."
tags:
  - tool-agnostic
  - security
aliases:
  - generate permissions allowlist
  - scaffold settings.json permissions
  - default-deny permission block
---

# Bootstrap Permissions Allowlist

> Detect tool usage from transcripts and CI, generate a default-deny permissions block with sensitive-path deny and a tight Bash allowlist, validate against blast-radius rules.

!!! info "Harness assumption"
    Templates target Claude Code (`.claude/settings.json` allow/deny/ask schema). The default-deny posture and category-based allowlist apply to any harness — translate to Cursor's `permissions`, Copilot's tool gates, or your runtime's equivalent. See [Assumptions](index.md#assumptions).

A capable agent with no permission boundary is a production incident waiting for a prompt-injection vector. This runbook generates the runtime constraint the agent operates under — paired remediation for [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md). Rules from [blast radius containment](../security/blast-radius-containment.md), [permission-gated commands](../security/permission-gated-commands.md), and [transcript-driven permission allowlist](../security/transcript-driven-permission-allowlist.md).

## Step 1 — Detect Current State

```bash
# Existing permissions config
test -f .claude/settings.json && jq '.permissions // empty' .claude/settings.json
test -f .claude/settings.local.json && jq '.permissions // empty' .claude/settings.local.json

# Sensitive paths that exist in this repo
find . -maxdepth 6 \( \
  -name ".env" -o -name ".env.*" -o -name "*.pem" -o -name "*.key" -o \
  -name "id_rsa*" -o -name "id_ed25519*" -o -name "credentials" -o \
  -path "*/secrets/*" -o -path "*/.aws/*" -o -path "*/.ssh/*" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null

# Protected branches (from git remote / GitHub branch protection)
git for-each-ref --format='%(refname:short)' refs/remotes/origin/ 2>/dev/null | grep -E "^origin/(main|master|production|release)"
```

Decision rules:

- **No `.claude/settings.json`** → generate a fresh one with default-deny posture
- **Existing `permissions` block** → audit ([`audit-permissions-blast-radius`](audit-permissions-blast-radius.md)); merge into the existing structure rather than overwriting
- **`settings.local.json` present** → personal overrides; do not generate there — generate in `settings.json` (committed)

## Step 2 — Mine Transcripts for Observed-Safe Commands

If the project has agent transcripts available, the [transcript-driven approach](../security/transcript-driven-permission-allowlist.md) bootstraps a tight allowlist from observed safe usage:

```bash
# Claude Code transcripts (if present)
find ~/.claude/projects -name "*.jsonl" 2>/dev/null | xargs grep -hE '"name":"Bash"' 2>/dev/null \
  | jq -r 'select(.message.content[]?.input.command) | .message.content[].input.command' 2>/dev/null \
  | sort -u | head -50

# CI workflow commands (the closest available proxy when no transcripts exist)
yq '.. | select(has("run")) | .run' .github/workflows/*.y*ml 2>/dev/null | sort -u
```

Categorize each observed command:

| Category | Example | Action |
|----------|---------|--------|
| Read-only | `ls`, `find`, `cat`, `grep`, `git status`, `git diff` | always allow |
| Build/test | `pytest`, `npm test`, `cargo build` | allow with no flags requiring confirmation |
| Mutating local | `git add`, `git commit`, `npm install` | allow |
| Mutating remote | `git push`, `gh pr create`, `curl POST` | gate with approval |
| Destructive | `rm -rf`, `git push --force`, `find -delete` | deny |

If no transcripts exist, ask the user to run the agent against a representative task once and capture the commands — the resulting allowlist will fit the project shape exactly. Synthetic allowlists drift; observed allowlists do not.

## Step 3 — Generate the Permissions Block

`.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Edit",
      "MultiEdit",
      "Glob",
      "Grep",

      "Bash(ls:*)",
      "Bash(find:*)",
      "Bash(cat:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(grep:*)",
      "Bash(rg:*)",

      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(git show:*)",
      "Bash(git branch:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git checkout:*)",
      "Bash(git pull:*)",

      "Bash(<discovered test cmd>:*)",
      "Bash(<discovered lint cmd>:*)",
      "Bash(<discovered build cmd>:*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./**/secrets/**)",
      "Read(./**/*.pem)",
      "Read(./**/*.key)",
      "Read(./**/id_rsa*)",
      "Read(./**/id_ed25519*)",
      "Read(./**/.aws/credentials)",
      "Read(./**/.ssh/**)",

      "Edit(./.env)",
      "Edit(./.env.*)",
      "Write(./.env)",
      "Write(./.env.*)",

      "Bash(rm -rf:*)",
      "Bash(find:* -delete)",
      "Bash(git push --force:*)",
      "Bash(git push -f:*)",
      "Bash(git push origin main:*)",
      "Bash(git push origin master:*)",
      "Bash(git reset --hard:*)",
      "Bash(curl:* | sh)",
      "Bash(curl:* | bash)",
      "Bash(wget:* | sh)",
      "Bash(sudo:*)"
    ],
    "ask": [
      "Bash(git push:*)",
      "Bash(gh pr:*)",
      "Bash(gh release:*)",
      "Bash(npm publish:*)",
      "Bash(pip install:*)",
      "Bash(curl:*)",
      "Bash(wget:*)"
    ]
  }
}
```

Substitution rules:

- Discovered test/lint/build commands replace the placeholder lines
- Sensitive-path deny rules are filtered to patterns that actually exist in the repo (run the find from Step 1; only include matches)
- Protected branches in the deny list match what `git for-each-ref` returned
- Add `Bash(<package-manager>:*)` only for the discovered manager (one of bun/pnpm/yarn/npm/uv/poetry)

## Step 4 — Merge with Existing Config

If `settings.json` exists, merge non-destructively:

```bash
# Append to existing arrays without duplicating
jq --slurpfile new <(echo "$NEW_PERMISSIONS") '
  .permissions.allow = ((.permissions.allow // []) + $new[0].allow | unique) |
  .permissions.deny  = ((.permissions.deny  // []) + $new[0].deny  | unique) |
  .permissions.ask   = ((.permissions.ask   // []) + $new[0].ask   | unique)
' .claude/settings.json > .claude/settings.json.tmp \
  && mv .claude/settings.json.tmp .claude/settings.json
```

Never remove an existing entry the user added. Generation is additive.

## Step 5 — Wire Sub-Agent Restrictions

For each sub-agent in `.claude/agents/`, add minimal `tools` frontmatter:

```yaml
---
name: review-bot
description: <existing description>
tools: [Read, Glob, Grep]   # explicit minimal set; never `*` or omitted
---
```

The principle: a sub-agent inherits no privilege by default. If the existing definition omits `tools`, add the field. If it lists `*`, replace with the minimum the description implies.

## Step 6 — Validate

```bash
# JSON parses
jq empty .claude/settings.json || { echo "FATAL: settings.json malformed"; exit 1; }

# Default-deny posture (no bare `Bash` in allow)
jq -e '.permissions.allow[] | select(. == "Bash")' .claude/settings.json \
  && echo "FAIL: bare 'Bash' allows everything"

# Required deny rules present (for the patterns that exist)
for pattern in ".env" "secrets/" "*.pem" "*.key"; do
  if find . -maxdepth 6 -name "$pattern" 2>/dev/null | head -1 | grep -q .; then
    jq -e --arg p "$pattern" '.permissions.deny[] | select(contains($p))' .claude/settings.json \
      || echo "FAIL: missing deny for existing $pattern"
  fi
done

# Destructive shell denied
for d in "rm -rf" "git push --force" "curl:* | sh"; do
  jq -e --arg d "$d" '.permissions.deny[] | select(contains($d))' .claude/settings.json \
    || echo "FAIL: missing deny for $d"
done
```

Then run [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md). Resolve any high-severity findings before declaring success.

## Step 7 — Document in AGENTS.md

```markdown
## Permission boundaries

Runtime allowlist in `.claude/settings.json`. Sensitive paths and destructive shell are denied at the harness layer; remote git operations require approval.
```

## Idempotency

Re-running merges new entries; never removes. Safe to re-run after every new tool, sub-agent, or sensitive-path discovery.

## Output Schema

```markdown
# Bootstrap Permissions Allowlist — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created/Modified | .claude/settings.json | allow: <n>, deny: <n>, ask: <n> |
| Modified | .claude/agents/<name>.md | tools: <list> |
| Modified | AGENTS.md | added permission-boundaries pointer |

Validation: <pass/fail>
Audit: <pass/findings count>
```

## Related

- [Blast Radius Containment](../security/blast-radius-containment.md)
- [Permission-Gated Commands](../security/permission-gated-commands.md)
- [Transcript-Driven Permission Allowlist](../security/transcript-driven-permission-allowlist.md)
- [Safe Outputs Pattern](../security/safe-outputs-pattern.md)
- [Audit Permissions and Blast Radius](audit-permissions-blast-radius.md)
- [Audit Lethal Trifecta](audit-lethal-trifecta.md)
