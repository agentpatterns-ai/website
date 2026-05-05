---
title: "Audit Instruction Placement"
description: "Locate every instruction surface, classify rules by criticality, validate that critical rules sit in primacy or recency positions, flag mid-file critical rules and contradictory restatements, emit per-file findings."
tags:
  - tool-agnostic
  - instructions
  - context-engineering
aliases:
  - critical instruction placement audit
  - primacy recency audit
  - lost-in-the-middle audit
---

Packaged as: `.claude/skills/agent-readiness-audit-instruction-placement/`

# Audit Instruction Placement

> Classify rules by criticality, check that critical rules occupy primacy (top) or recency (bottom) positions, flag mid-file criticals and contradictory restatements, emit per-file findings.

!!! info "Harness assumption"
    Instruction surfaces are `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/*.mdc`, `.github/copilot-instructions.md`, and any `SKILL.md` or sub-agent file with substantive prose. The runbook is harness-agnostic — it parses markdown, not config.

Transformer attention is U-shaped: tokens at the start (primacy) and end (recency) receive disproportionate attention; tokens in the middle decay 30%+ in retrieval accuracy ([Liu et al. 2023](https://arxiv.org/abs/2307.03172)). A critical rule placed in the middle of a long instruction file sits in the weakest-attention trough. Rules from [`critical-instruction-repetition`](../instructions/critical-instruction-repetition.md), [`lost-in-the-middle`](../context-engineering/lost-in-the-middle.md), [`attention-sinks`](../context-engineering/attention-sinks.md), [`instruction-compliance-ceiling`](../instructions/instruction-compliance-ceiling.md).

## Step 1 — Locate Instruction Surfaces

```bash
find . -maxdepth 4 \( \
  -name "AGENTS.md" -o -name "CLAUDE.md" -o -name "GEMINI.md" \
  -o -name "copilot-instructions.md" \
  -o -path "*/.cursor/rules/*.mdc" \
\) ! -path "*/node_modules/*" ! -path "*/.claude/worktrees/*"
```

Skip files smaller than 30 lines — primacy/recency analysis assumes a meaningful middle. Short files are entirely high-attention.

## Step 2 — Tokenize Lines and Mark Position

For each file, split body lines into thirds:

```bash
for f in $FILES; do
  BODY=$(awk 'BEGIN{c=0} /^---$/{c++; next} c>=2 || c==0' "$f")  # strip frontmatter if present
  TOTAL=$(echo "$BODY" | wc -l)
  TOP_END=$(( TOTAL / 3 ))
  BOT_START=$(( TOTAL * 2 / 3 ))
  # Lines 1..TOP_END = primacy, TOP_END+1..BOT_START-1 = middle, BOT_START..TOTAL = recency
done
```

The middle third is the lost-in-the-middle zone for files long enough to have one.

## Step 3 — Classify Rules by Criticality

A critical rule is anything where non-compliance has a security, safety, or correctness cost. Heuristic detection:

```bash
CRITICAL_RE='(?i)\b(never|must not|do not|forbidden|critical|secret|credential|password|token|sandbox|destructive|delete|drop|force[- ]push|rm -rf|exfiltrat)'
ADVISORY_RE='(?i)\b(prefer|consider|avoid (when)?|try to|ideally|where possible)'
```

For each line, classify:

| Class | Pattern | Treatment |
|-------|---------|-----------|
| critical | matches `CRITICAL_RE` and reads as imperative | must be in primacy or recency |
| advisory | matches `ADVISORY_RE` or is a soft preference | placement irrelevant |
| informational | descriptive prose, not a rule | placement irrelevant |

```bash
echo "$BODY" | nl -ba | while IFS= read -r line; do
  num=$(echo "$line" | awk '{print $1}')
  text=$(echo "$line" | cut -f2-)
  if echo "$text" | grep -qiP "$CRITICAL_RE"; then
    pos=$(( num <= TOP_END ? 1 : (num >= BOT_START ? 3 : 2) ))
    echo "$num|$pos|$text"
  fi
done
```

## Step 4 — Flag Mid-File Critical Rules

Any critical rule with position `2` (middle third) is a finding:

```bash
MID_CRITICAL=$(grep -E "^[0-9]+\|2\|" classified.txt)
echo "$MID_CRITICAL" | while IFS='|' read -r num pos text; do
  echo "high|$f:$num|critical rule in middle third|move to top of file or restate at end"
done
```

## Step 5 — Detect Missing Recency Restatement on Long Files

For files over 200 lines, the most critical rule should appear at both top and bottom (per [`critical-instruction-repetition`](../instructions/critical-instruction-repetition.md)):

```bash
if [[ $TOTAL -gt 200 ]]; then
  TOP_CRITICALS=$(awk -v end=$TOP_END 'NR<=end' "$f" | grep -ciP "$CRITICAL_RE")
  BOT_CRITICALS=$(awk -v start=$BOT_START 'NR>=start' "$f" | grep -ciP "$CRITICAL_RE")
  if [[ $TOP_CRITICALS -gt 0 && $BOT_CRITICALS -eq 0 ]]; then
    echo "medium|$f|long file ($TOTAL lines) with criticals at top but no recency restatement|restate the most critical rule near end"
  fi
fi
```

## Step 6 — Detect Contradictory Restatements

If a critical rule is restated, the wording at top and bottom must be consistent. Different wording for the same rule reads as two conflicting constraints, not reinforcement.

```bash
# Extract the noun/verb signature of each critical rule and compare top vs bottom occurrences
python3 - "$f" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
lines = text.splitlines()
total = len(lines)
top, bot = lines[:total//3], lines[2*total//3:]

def signatures(block):
    out = []
    for ln in block:
        m = re.search(r'\b(never|do not|must not)\b\s+(\w+\s+\w+)', ln, re.I)
        if m:
            out.append(m.group(2).lower())
    return out

t_sigs = set(signatures(top))
b_sigs = set(signatures(bot))
common_themes = {s.split()[0] for s in t_sigs} & {s.split()[0] for s in b_sigs}
for theme in common_themes:
    t_match = [s for s in t_sigs if s.startswith(theme)]
    b_match = [s for s in b_sigs if s.startswith(theme)]
    if t_match and b_match and set(t_match) != set(b_match):
        print(f'medium|{sys.argv[1]}|critical rule "{theme}" restated with different wording|align wording so reinforcement reads as one rule, not two')
PY
```

## Step 7 — Polarity Spot-Check

The placement audit is incomplete without a polarity check ([`instruction-polarity`](../instructions/instruction-polarity.md)). Negative-only rules ("do not X") in primacy positions without a positive corollary ("instead, do Y") underperform on compliance:

```bash
awk -v end=$TOP_END 'NR<=end' "$f" | grep -iP "\b(never|do not|must not)\b" | while read -r line; do
  if ! echo "$line" | grep -qiE "instead|use|prefer|do "; then
    echo "low|$f|negative-only rule in primacy without positive corollary|append 'instead, do X' to make compliance actionable"
  fi
done
```

## Step 8 — Per-File Scorecard

```markdown
# Audit Report — Instruction Placement

## Per-file scorecard

| File | Total lines | Mid-file criticals | Top criticals | Recency restated | Top issue |
|------|------------:|-------------------:|--------------:|:----------------:|-----------|
| AGENTS.md | <n> | <n> | <n> | ✅ | <one-line> |

## Findings

| Severity | File:Line | Finding | Suggested fix |
|----------|-----------|---------|---------------|
| high | AGENTS.md:142 | critical rule in middle third | move to top or restate at end |
```

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Instruction Placement — <repo>

| Files | Pass | Warn | Fail | Mid-file criticals total |
|------:|-----:|-----:|-----:|-------------------------:|
| <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner>
```

## Remediation

- For mid-file criticals: move to top of file (primacy) — see [`critical-instruction-repetition`](../instructions/critical-instruction-repetition.md)
- For long files without recency restatement: restate the most critical rule in the closing section
- For contradictory restatements: align wording so the rule reads as one constraint, not two
- For total instruction count over budget: run [`audit-instruction-rule-budget`](audit-instruction-rule-budget.md) to identify rules to drop before re-arranging

## Related

- [Critical Instruction Repetition](../instructions/critical-instruction-repetition.md)
- [Lost in the Middle](../context-engineering/lost-in-the-middle.md)
- [Attention Sinks](../context-engineering/attention-sinks.md)
- [Instruction Compliance Ceiling](../instructions/instruction-compliance-ceiling.md)
- [Instruction Polarity](../instructions/instruction-polarity.md)
- [Audit Instruction Rule Budget](audit-instruction-rule-budget.md)
- [Audit AGENTS.md](audit-agents-md.md)
- [Audit CLAUDE.md](audit-claude-md.md)
