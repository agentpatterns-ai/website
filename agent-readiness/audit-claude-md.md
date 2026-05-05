---
title: "Audit CLAUDE.md"
description: "Locate CLAUDE.md and equivalent project instruction files, run mechanical checks for size, polarity, embedded code, @path imports, primacy, and cache stability, and emit findings."
tags:
  - tool-agnostic
  - instructions
aliases:
  - CLAUDE.md health check
  - CLAUDE.md audit pass
  - project instruction file audit
---

# Audit CLAUDE.md

> Locate `CLAUDE.md` and equivalents, run mechanical checks for size, polarity, embedded code, `@path` imports, primacy, cache stability.

`CLAUDE.md` is the highest-leverage instruction file in the Claude Code ecosystem — it loads on every session and frames every task. The same patterns apply to `.github/copilot-instructions.md`, `.cursor/rules/`, and similar tool-specific equivalents. This runbook catches file-level failure modes that prompt-quality reviewers cannot.

## Step 1 — Locate Files

```bash
find . -maxdepth 4 \( \
  -iname "CLAUDE.md" -o -iname "CLAUDE.local.md" -o \
  -iname "copilot-instructions.md" -o \
  -path "*/.cursor/rules/*" -o -path "*/.cursor/mdc/*" -o \
  -name ".cursorrules" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*" -print
```

## Step 2 — Run Mechanical Checks

### Check 1 — Size

```bash
LINES=$(wc -l < "$FILE")
[[ $LINES -gt 200 ]] && echo "high|-|file is $LINES lines (target ≤200)|hoist sections to skills/rules loaded on demand"
```

### Check 2 — Embedded Code Blocks

```bash
awk '/^```/{n++; if(n%2==1) start=NR; else if(NR-start>20) print "high|"start"|code block "(NR-start)" lines|replace with @path import to canonical file"}' "$FILE"
```

### Check 3 — `@path` Import Resolution

Every `@path` reference must resolve to an existing file:

```bash
grep -nE '@[A-Za-z][A-Za-z0-9_./-]+' "$FILE" | while read line; do
  LINE_NO=$(echo "$line" | cut -d: -f1)
  for path in $(echo "$line" | grep -oE '@[A-Za-z][A-Za-z0-9_./-]+' | tr -d '@'); do
    test -e "$path" || echo "high|$LINE_NO|@path import does not resolve: $path|update or remove"
  done
done
```

### Check 4 — Cache-Prefix Mutation

Detect dynamic substitutions in the file that break prompt caching:

```bash
# Common substitution patterns
grep -nE '\{[a-z_]+\}|\$[A-Z_]+|\$\{[A-Z_]+\}' "$FILE" | while read line; do
  LINE_NO=$(echo "$line" | cut -d: -f1)
  echo "high|$LINE_NO|dynamic substitution in instruction prefix|remove — breaks prompt cache"
done

# Date / timestamp content
grep -nE "\b(Today|Date|Updated)[: ]" "$FILE" | while read line; do
  LINE_NO=$(echo "$line" | cut -d: -f1)
  echo "high|$LINE_NO|date/timestamp likely in prefix|remove — breaks prompt cache"
done
```

### Check 5 — Polarity

For coding-agent rules, prefer guardrails (negative + remediation). Flag pure-positive guidance for safety-critical rules:

```bash
# Heuristic: rules in a "Safety" / "Security" / "Critical" section that read as positive
awk '
  /^## (Safety|Security|Critical|Never)/ { in_safety=1; next }
  /^## / { in_safety=0 }
  in_safety && /^[ ]*-[ ]+(use|prefer|always)/ {
    print "medium|" NR "|safety rule in positive form: " $0 "|reframe as guardrail (no X / never Y) with remediation"
  }
' "$FILE"
```

### Check 6 — Primacy Positioning

The first 5–10 substantive rules must be the highest-stakes. Heuristic: extract the first ten bullet rules; flag if any are obviously cosmetic (formatting, tone) when later rules are safety/correctness:

```python
# pseudo-Python — surface, not script
rules = parse_bullets(file)
top_n = rules[:10]
remaining = rules[10:]
cosmetic_top = [r for r in top_n if matches_cosmetic_pattern(r)]
critical_below = [r for r in remaining if matches_critical_pattern(r)]
if cosmetic_top and critical_below:
    finding("high", "primacy positioning",
            f"top rules are cosmetic ({len(cosmetic_top)}); critical rules sink below line {critical_below[0].line}",
            "move safety/correctness rules to the top")
```

### Check 7 — Stale References

Every backticked file path and `@path` import must resolve (covered in Check 3); every command must be in PATH:

```bash
grep -oE '`[a-z][a-z0-9_-]+( |$)' "$FILE" | awk '{print $1}' | tr -d '`' | sort -u | while read cmd; do
  command -v "$cmd" >/dev/null || echo "medium|-|command not in PATH: $cmd|verify or update"
done
```

### Check 8 — Duplication

Same approach as in [`audit-agents-md`](audit-agents-md.md): cross-reference section headers against `STANDARDS.md`, `AGENTS.md`, and any loaded skill.

```bash
for ref in AGENTS.md STANDARDS.md docs/STANDARDS.md; do
  test -f "$ref" || continue
  grep -E "^##" "$FILE" | sed 's/^## //' | while read header; do
    grep -qE "^##.*$header" "$ref" 2>/dev/null && \
      echo "medium|-|section '$header' duplicates $ref|replace with @$ref reference"
  done
done
```

## Step 3 — Aggregate and Emit Report

```markdown
# Audit Report — CLAUDE.md (<path>)

> <n> findings: <high> high, <medium> medium, <low> low. File is <n> lines.

## Findings

| Severity | Line | Finding | Suggested fix |
|----------|------|---------|---------------|
| high | <n> | <finding> | <fix> |

## Suggested next action

<targeted fix list | full rewrite | no action>
```

## Step 4 — Hand Off

For high-severity cache-prefix or stale-reference findings, propose a one-line patch per finding for user approval. For widespread bloat (>50 lines over cap, >5 embedded code blocks), recommend hoisting sections into rules files or skills.

## Idempotency

Read-only. Re-runnable.

## Output Schema

```markdown
# Audit CLAUDE.md — <repo>

| File | Severity | Findings | Action |
|------|:--------:|---------:|--------|
| CLAUDE.md | high | <n> | targeted patches + 2 hoists |
```

## Related

- [CLAUDE.md Convention](../instructions/claude-md-convention.md)
- [Instruction Polarity](../instructions/instruction-polarity.md)
- [Guardrails Beat Guidance for Coding Agents](../instructions/guardrails-beat-guidance-coding-agents.md)
- [Hints Over Code Samples](../instructions/hints-over-code-samples.md)
- [Critical Instruction Repetition](../instructions/critical-instruction-repetition.md)
