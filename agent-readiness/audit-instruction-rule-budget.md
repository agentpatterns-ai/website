---
title: "Audit Instruction Rule Budget"
description: "Enumerate every instruction surface in a repository, tokenize rules by class, count against the ~150-rule compliance ceiling, detect duplication and dead rules, and emit a remediation plan."
tags:
  - tool-agnostic
  - instructions
aliases:
  - instruction rule budget
  - compliance ceiling audit
  - rule count audit
---

Packaged as: `.claude/skills/agent-readiness-audit-instruction-rule-budget/`

# Audit Instruction Rule Budget

> Enumerate every instruction surface, tokenize rules by class, count against the ~150-rule [compliance ceiling](../instructions/instruction-compliance-ceiling.md), detect duplication and dead rules.

!!! info "Harness assumption"
    Surface enumeration covers Claude Code, Cursor, Copilot, and Gemini paths by default. Add any harness-specific instruction files your project uses; the budget itself is per-agent, not per-tool. See [Assumptions](index.md#assumptions).

Instructions don't fail one rule at a time — they fail at the budget. Adherence stays high through roughly 150 rules, then degrades from full compliance to selective compliance to outright omission. Single-file audits miss this; the ceiling is across all surfaces an agent loads.

## Step 1 — Enumerate Surfaces

```bash
# Every file an agent loads on session start
SURFACES=$(find . -maxdepth 8 \( \
  -iname "AGENTS.md" -o -iname "CLAUDE.md" -o -iname "CLAUDE.local.md" -o \
  -iname "copilot-instructions.md" -o -name ".cursorrules" -o \
  -path "*/.cursor/rules/*" -o -path "*/.cursor/mdc/*" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/.claude/worktrees/*")

# Skill and sub-agent files (loaded on demand but counted toward the budget when active)
SKILLS=$(find . -path "*/.claude/skills/*/SKILL.md")
SUBAGENTS=$(find . -path "*/.claude/agents/*.md")

# Tool descriptions (MCP)
MCP=$(find . -name "mcp.json" -o -name ".mcp.json")
```

## Step 2 — Tokenize Rules

A "rule" is a single imperative clause: a numbered or bulleted statement that tells the agent to do or not do something. Heuristic regex:

```bash
count_rules() {
  local file="$1"
  # Match bullets and numbered items that begin with an imperative verb or "do not" / "never"
  grep -cE '^[ ]*([-*]|[0-9]+\.)[ ]+(do not|never|always|use|prefer|avoid|run|write|read|edit|skip|add|remove|check|verify|return|emit|reject|accept|require|assume)' "$file"
}
```

Per surface, count and bucket by class:

| Class | Heuristic markers |
|-------|-------------------|
| safety | "never", "do not", "secret", "credential", "production", section under `## Safety / Security / Critical` |
| correctness | "must", "always", "verify", "test", section under `## Conventions / Standards` |
| style | "prefer", "format", "tone", "voice", section under `## Style / Tone / Format` |

Classify each rule with another regex pass:

```bash
classify_rule() {
  local rule="$1"
  if echo "$rule" | grep -qiE "secret|credential|never|production|destructive"; then
    echo "safety"
  elif echo "$rule" | grep -qiE "format|prefer|tone|voice|style"; then
    echo "style"
  else
    echo "correctness"
  fi
}
```

## Step 3 — Detect Duplication

Cross-surface duplication: the same rule expressed in multiple files counts twice toward the budget but pays once.

```python
# Pseudocode
all_rules = []  # (surface, line, text, class)
for file in surfaces:
    for rule in extract_rules(file):
        all_rules.append((file, rule.line, normalize(rule.text), classify(rule.text)))

# Semantic match: same normalized text or high cosine similarity
seen = {}
duplicates = []
for surface, line, text, cls in all_rules:
    key = stem_normalize(text)
    if key in seen:
        duplicates.append((seen[key], (surface, line, text)))
    else:
        seen[key] = (surface, line, text)
```

`normalize` strips formatting; `stem_normalize` strips stop words and stems. For higher fidelity, use embedding similarity ≥0.9 instead of stem match.

## Step 4 — Detect Dead Rules

A rule is "dead" if its violation is already mechanically prevented by hooks, linters, or CI gates:

```bash
# Rules covered by lint config — parse explicitly so malformed configs become findings
parse_or_finding() {
  local f="$1" expr="${2:-empty}"
  [[ -f "$f" ]] || return 1
  if ! jq empty "$f" 2>/tmp/_jqerr; then
    echo "FINDING: $f malformed JSON: $(cat /tmp/_jqerr)"; return 1
  fi
  jq -r "$expr" "$f"
}

[[ -f .eslintrc.json ]] && parse_or_finding .eslintrc.json '.rules | keys[]'
[[ -f biome.json ]]     && parse_or_finding biome.json     '.linter.rules | keys[]'
[[ -f pyproject.toml ]] && grep -A 50 "\[tool.ruff" pyproject.toml | grep -E "select|extend-select"
[[ -f .pre-commit-config.yaml ]] && yq '.repos[].hooks[].id' .pre-commit-config.yaml

# Rules covered by hooks
[[ -f .claude/settings.json ]] && parse_or_finding .claude/settings.json '.hooks'
```

For each rule in instruction surfaces, search the lint/hook coverage. A match flags the rule as dead.

Examples of common dead rules:

- "use single quotes" — covered by Prettier / Biome
- "no unused imports" — covered by ESLint / Ruff
- "imports must be sorted" — covered by isort / Ruff
- "use conventional commits" — covered by commitlint hook (if present)

## Step 5 — Score Primacy

Extract the first 10 rules across all surfaces (in load order — typically AGENTS.md → CLAUDE.md → loaded skills). Confirm the top 5–10 are the highest-stakes (safety/correctness with high consequence). Cosmetic rules in primacy positions are findings.

## Step 6 — Emit the Report

```markdown
# Audit Report — Instruction Rule Budget

## Totals

| Surface | Rules | safety | correct | style |
|---------|------:|-------:|--------:|------:|
| AGENTS.md | <n> | <n> | <n> | <n> |
| CLAUDE.md | <n> | <n> | <n> | <n> |
| <skill>/SKILL.md | <n> | <n> | <n> | <n> |
| <agent>.md | <n> | <n> | <n> | <n> |
| Tool descriptions | <n> | - | <n> | <n> |
| **Total** | **<n>** | <n> | <n> | <n> |

Status: <under | warning | over> the ~150 ceiling

## Findings

| Severity | Finding | Action |
|----------|---------|--------|
| <sev> | <one-liner> | <action> |

## Cut list (in order)

1. **<n> dead style rules** in <surface> already enforced by <linter> — remove
2. **<n> duplicates** of "<rule>" in <surfaces> — keep in <preferred surface> only
3. **<n> cosmetic rules** in primacy position (<surface> top 10) — move down or remove
4. **<n> rules covered by hooks** — remove from prose

After cuts: projected total <n> (under ceiling: <yes/no>)
```

## Step 7 — Hand Off

Recommend the cut list in priority order. Each cut is a small, reversible change; apply them with user approval one batch at a time. Re-run the audit after each batch to confirm the projected total.

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Instruction Rule Budget — <repo>

| Total | Ceiling | Status |
|------:|--------:|--------|
| <n> | 150 | <under | warning | over> |

Cuts to apply: <n> (style: <n>, dups: <n>, dead: <n>, primacy: <n>)
```

## Related

- [Instruction Compliance Ceiling](../instructions/instruction-compliance-ceiling.md)
- [Critical Instruction Repetition](../instructions/critical-instruction-repetition.md)
- [Project Instruction File Ecosystem](../instructions/instruction-file-ecosystem.md)
- [Audit CLAUDE.md](audit-claude-md.md)
- [Audit AGENTS.md](audit-agents-md.md)
