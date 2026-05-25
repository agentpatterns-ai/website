---
title: "Audit AGENTS.md"
description: "Locate every AGENTS.md and equivalent in a repository, run mechanical checks against the pointer-map rules, validate links and commands, and emit a structured findings report with suggested rewrites."
tags:
  - tool-agnostic
  - instructions
aliases:
  - AGENTS.md health check
  - AGENTS.md audit pass
  - review AGENTS.md for bloat
---

Packaged as: `.claude/skills/agent-readiness-audit-agents-md/`

# Audit AGENTS.md

> Locate every `AGENTS.md` and equivalent, run mechanical checks against pointer-map rules, validate links and commands, emit findings.

!!! info "Harness assumption"
    `AGENTS.md` is the open standard; the same checks apply to `CLAUDE.md`, `.cursor/rules/`, `copilot-instructions.md`, and `GEMINI.md`. Audit any instruction file that loads on session start. See [Assumptions](index.md#assumptions).

`AGENTS.md` files drift. A file written correctly six months ago now misleads agents into deprecated commands, embeds knowledge that should have linked out, and exceeds the budget that makes it useful. This runbook produces a structured findings report against the published rules from the [table-of-contents pattern](../instructions/agents-md-as-table-of-contents.md) and [design patterns](../instructions/agents-md-design-patterns.md).

## Step 1 — Locate Files

```bash
find . -maxdepth 8 \( \
  -iname "AGENTS.md" -o -iname "CLAUDE.md" -o \
  -iname "copilot-instructions.md" -o -name ".cursorrules" -o \
  -iname "GEMINI.md" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/.claude/worktrees/*" -print
```

For each file, classify: root vs subdirectory. Root has the strictest rules (≤100 lines); subdir has ≤30.

## Step 2 — Run Mechanical Checks

For each file, run all checks and capture findings as `(severity, line, finding, fix)` tuples.

### Check 1 — Size

```bash
LINES=$(wc -l < "$FILE")
LIMIT=100; [[ "$FILE" =~ /[^/]+/AGENTS\.md$ ]] && LIMIT=30
[[ $LINES -gt $LIMIT ]] && echo "high|-|file is $LINES lines (target ≤$LIMIT)|hoist sections to docs/ and link"
```

### Check 2 — Executable Commands

A "command" is any backticked CLI string in a list item. Each must include flags or a target — bare names fail.

```bash
grep -nE '^[ ]*-' "$FILE" | grep -oE '`[^`]+`' | tr -d '`' | while read cmd; do
  # Bare command (no args, no flags) is a fail
  if [[ "$cmd" =~ ^[a-z][a-z0-9_-]*$ ]]; then
    LINE=$(grep -n "\`$cmd\`" "$FILE" | head -1 | cut -d: -f1)
    echo "high|$LINE|bare command \`$cmd\` is not executable|add flags and target, e.g. \`$cmd -v tests/\`"
  fi
done
```

### Check 3 — Three-Tier Boundaries

The permission section must use ✅ / ⚠️ / 🚫 tiers, not a flat prohibition list.

```bash
# Detect a "do not" / "never" list with no positive tier
if grep -qE "^[ ]*-[ ]+(do not|never|don't|avoid)" "$FILE"; then
  if ! grep -qE "✅|always|allowed" "$FILE"; then
    LINE=$(grep -nE "^[ ]*-[ ]+(do not|never)" "$FILE" | head -1 | cut -d: -f1)
    echo "medium|$LINE|permission section is a flat prohibition list|restructure as ✅ Always / ⚠️ Ask / 🚫 Never"
  fi
fi
```

### Check 4 — Embedded Code Blocks

The principle is [hints over code samples](../instructions/hints-over-code-samples.md): point at canonical files (`see scripts/run-tests.sh`) instead of pasting them inline. Embedded code drifts from the real source and burns context budget on every session load. The 20-line cap below is the hard floor; shorter blocks are still a smell — review each one and ask whether a path reference would do.

```bash
awk '
  /^```/ { if (!in_block) { in_block=1; start=NR } else { in_block=0; if (NR-start>20) print "high|" start "|code block " (NR-start) " lines|replace with hint to canonical file" } }
' "$FILE"
```

### Check 5 — Discoverable Content

Heuristic patterns that suggest the file lists what an agent could discover:

```bash
# Lists every file under a directory
grep -nE "^[ ]*-[ ]+\`[a-z]+/[a-z][^\`]*\`$" "$FILE" \
  | awk -F: '{print "high|" $1 "|likely directory listing|remove — agents can ls"}'

# Restates package.json scripts the agent can run jq on
if test -f package.json; then
  jq -r '.scripts | keys[]' package.json | while read script; do
    grep -qE "\b$script\b" "$FILE" 2>/dev/null && \
      echo "low|-|mentions package.json script '$script'|prefer a single 'run scripts via package.json' pointer"
  done
fi
```

### Check 6 — Stale References

Every relative link and file reference must resolve; every command must be runnable.

```bash
# Markdown relative links
grep -oE '\[[^]]+\]\([^)h][^)]*\)' "$FILE" | grep -oE '\([^)]+\)' | tr -d '()' | while read link; do
  TARGET="$(dirname "$FILE")/$link"
  test -e "${TARGET%#*}" || echo "high|-|broken link: $link|update or remove"
done

# Backticked file paths
grep -oE '`[^`]+\.[a-z]+`' "$FILE" | tr -d '`' | while read path; do
  test -e "$path" || echo "high|-|file does not exist: $path|update or remove"
done

# Commands resolve in PATH
grep -oE '`[a-z][a-z0-9_-]+( |$)' "$FILE" | awk '{print $1}' | tr -d '`' | sort -u | while read cmd; do
  command -v "$cmd" >/dev/null || echo "medium|-|command not in PATH: $cmd|verify discovered tooling matches"
done
```

### Check 7 — Duplication

Cross-reference section headers against `STANDARDS.md`, `CONTRIBUTING.md`, `README.md`:

```bash
for ref in STANDARDS.md CONTRIBUTING.md README.md docs/STANDARDS.md; do
  test -f "$ref" || continue
  grep -E "^##" "$FILE" | sed 's/^## //' | while read header; do
    grep -qE "^##.*$header" "$ref" 2>/dev/null && \
      echo "medium|-|section '$header' duplicates $ref|replace with: see $ref §$header"
  done
done
```

### Check 8 — Scope Discipline (Subdirectory Files)

A subdirectory `AGENTS.md` must not speak to project-level concerns.

```bash
[[ "$FILE" =~ /[^/]+/AGENTS\.md$ ]] || return
grep -qE "^# (Project|Repository)" "$FILE" && \
  echo "medium|-|subdirectory AGENTS.md uses project-level title|scope to the directory only"
```

## Step 3 — Aggregate Findings

Collect all findings into a list, deduplicate, sort by severity:

```bash
findings | sort -t '|' -k1,1r | column -t -s '|'
```

Severity ordering: `high > medium > low`.

## Step 4 — Emit the Report

```markdown
# Audit Report — AGENTS.md (<path>)

> <n> findings: <high> high, <medium> medium, <low> low. File is <n> lines.

## Findings

| Severity | Line | Finding | Suggested fix |
|----------|------|---------|---------------|
| high | <n> | <one-line finding> | <one-line fix> |
| ... |

## Suggested next action

<one of: rewrite via `bootstrap-agents-md`, targeted fixes inline, no action>
```

## Step 5 — Hand Off

If the report contains any high-severity finding, recommend either:

- Targeted fixes inline (≤3 high findings) — present a diff for user approval
- Full rewrite via [`bootstrap-agents-md`](bootstrap-agents-md.md) (>3 high findings or >50% over the line cap) — confirm before overwriting

If only low/medium findings, present the report and let the user decide.

## Idempotency

Read-only. Safe to re-run any time. Output is deterministic given the same input.

## Output Schema

```markdown
# Audit AGENTS.md — <repo>

| File | Severity | Findings | Action |
|------|:--------:|---------:|--------|
| AGENTS.md | high | <n> | rewrite via bootstrap-agents-md |
| packages/api/AGENTS.md | low | <n> | targeted fixes |
```

## Related

- [AGENTS.md as Table of Contents](../instructions/agents-md-as-table-of-contents.md)
- [AGENTS.md Design Patterns](../instructions/agents-md-design-patterns.md)
- [AGENTS.md Standard](../standards/agents-md.md)
- [Hints Over Code Samples](../instructions/hints-over-code-samples.md)
- [Bootstrap AGENTS.md](bootstrap-agents-md.md)
