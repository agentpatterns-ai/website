---
title: "Audit Skill Quality"
description: "Locate every SKILL.md, validate frontmatter, score description craft and trigger phrases, detect missing gotchas and inline shell, and emit per-skill findings with rewrite suggestions."
tags:
  - tool-agnostic
  - cost-performance
aliases:
  - SKILL.md quality audit
  - skill description quality check
  - skill authoring audit
---

Packaged as: `.claude/skills/agent-readiness-audit-skill-quality/`

# Audit Skill Quality

> Locate every `SKILL.md`, validate frontmatter, score description craft and trigger phrases, detect missing gotchas and inline shell, emit per-skill findings.

!!! info "Harness assumption"
    `SKILL.md` lives under `.claude/skills/`, `.cursor/skills/`, or any other harness that exposes on-demand skills. Skip this runbook for harnesses with no skill primitive — there is nothing to audit. See [Assumptions](index.md#assumptions).

A skill's value lives almost entirely in its description: the field the model reads to decide whether to invoke. Bodies that read like documentation, missing gotchas sections, and inline shell that should have lived in `scripts/` are the recurring failure modes that quietly degrade trigger precision and output quality. Rules from [skill authoring patterns](../tool-engineering/skill-authoring-patterns.md).

## Step 1 — Locate Skills

```bash
find . \( \
  -path "*/.claude/skills/*/SKILL.md" \
  -o -path "*/.cursor/skills/*/SKILL.md" \
  -o -path "*/skills/*/SKILL.md" \
\) ! -path "*/node_modules/*" ! -path "*/.claude/worktrees/*"
```

For each found, capture: skill directory, frontmatter, body.

## Step 2 — Frontmatter Validation

```bash
for skill in $SKILLS; do
  python3 -c "
import sys, yaml
text = open(sys.argv[1]).read()
if not text.startswith('---'):
    print('high|-|missing frontmatter|add YAML frontmatter with name, description, version')
    sys.exit()
parts = text.split('---', 2)
fm = yaml.safe_load(parts[1])
for required in ('name', 'description'):
    if not fm.get(required):
        print(f'high|-|frontmatter missing {required}|add the field')
" "$skill"
done
```

Required: `name`, `description`. Recommended: `version`.

## Step 3 — Description Craft Scoring

For each skill, score the description on four axes:

| Axis | Test | Severity if missing |
|------|------|---------------------|
| Trigger phrase | matches `use (this )?when |invoke when |run (when|on)` | high |
| Capability listing | mentions ≥2 capabilities or outputs | medium |
| Negative trigger | matches `do not use|skip when|avoid when` | medium |
| Self-contained | no references to "as above", "see other skill" | medium |

```bash
score_description() {
  local desc="$1"
  echo "$desc" | grep -qiE "use (this )?when|invoke when|run when" \
    || echo "high|frontmatter|description lacks trigger phrase|add 'use this when X' or 'invoke when X'"
  echo "$desc" | grep -qiE "do not use|skip when|avoid when" \
    || echo "medium|frontmatter|description lacks negative trigger|add 'do not use when Y' to disambiguate from sibling skills"
}
```

## Step 4 — Body Structure Checks

### Gotchas Section

The body should have a section capturing edge cases and known failure modes:

```bash
grep -qiE "^## (Gotchas|Edge Cases|Failure Modes|Known Issues|Caveats)" "$skill" \
  || echo "medium|-|no Gotchas/Edge-Cases section|capture 3 specific failure modes from past runs"

# If present, count items
SECTION=$(awk '/^## (Gotchas|Edge Cases|Failure Modes|Known Issues)/,/^## /' "$skill" | head -n -1)
ITEMS=$(echo "$SECTION" | grep -cE "^[ ]*-[ ]+")
[[ $ITEMS -lt 3 ]] && echo "low|-|Gotchas section has only $ITEMS items|add specific failure modes from incidents"
```

### CLI-First Body

Non-trivial logic should live in `scripts/`, not inline shell in `SKILL.md`:

```bash
SHELL_LINES=$(awk '/^```bash$|^```sh$/{n++; if(n%2==1) start=NR; else total+=NR-start} END{print total+0}' "$skill")
[[ $SHELL_LINES -gt 10 ]] && [[ ! -d "$(dirname "$skill")/scripts" ]] && \
  echo "medium|-|$SHELL_LINES inline shell lines and no scripts/ dir|extract to scripts/ for testability"
```

### Body Length

```bash
BODY_LINES=$(awk '/^---$/{c++; next} c==2{print}' "$skill" | wc -l)
[[ $BODY_LINES -gt 500 ]] && echo "low|-|body is $BODY_LINES lines|trim to ≤200 narrative or ≤500 tutorial-style"
```

### Critical Rules First

The first 5 substantive lines after the H1 should contain the most important rules. Heuristic: if any safety/critical wording appears late and cosmetic wording appears at top, flag.

```bash
TOP=$(awk '/^# /{f=1; next} f && NF{count++; if(count<=5) print}' "$skill")
BOTTOM=$(awk '/^# /{f=1; next} f && NF{count++; if(count>5) print}' "$skill")
echo "$TOP" | grep -qiE "format|tone|prefer" && echo "$BOTTOM" | grep -qiE "secret|never|critical|destructive" \
  && echo "medium|-|primacy positioning: cosmetic top, critical bottom|reorder"
```

## Step 5 — Trigger Precision Smoke Test (Optional)

For each skill, synthesize a positive and a negative trigger prompt; assert the description distinguishes them. Requires running the harness:

```python
# pseudo
positive_prompt = derive_from_description(desc)  # e.g. "create a README"
negative_prompt = adversarial_neighbor(desc)     # e.g. "tell me about READMEs"

with_skill = run_agent(positive_prompt, skills=[skill])
without_skill = run_agent(negative_prompt, skills=[skill])

assert skill.name in with_skill.invoked
assert skill.name not in without_skill.invoked
```

Skip if no harness is wired.

## Step 6 — Per-Skill Scorecard

```markdown
# Audit Report — Skill Quality

## Per-skill scorecard

| Skill | Frontmatter | Description | Gotchas | CLI-first | Body lines | Top issue |
|-------|:-----------:|:-----------:|:-------:|:---------:|----------:|-----------|
| <name> | ✅ | ⚠️ | ❌ | ✅ | <n> | <one-line> |

## Findings

| Severity | Skill | Finding | Suggested fix |
|----------|-------|---------|---------------|
| high | <skill> | <finding> | <fix> |
```

## Step 7 — Hand Off

For each skill with high-severity findings, propose a description rewrite + a Gotchas section starter. For inline-shell findings, propose the `scripts/` extraction with the existing shell as the seed.

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Skill Quality — <repo>

| Skills | Pass | Warn | Fail |
|-------:|-----:|-----:|-----:|
| <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually description triggers>
```

## Remediation

- [Bootstrap Skill Template](bootstrap-skill-template.md) — opinionated `SKILL.md` skeleton for new skills or wholesale rewrites
- [Bootstrap Tool Descriptions](bootstrap-tool-descriptions.md) — when the failing axis is description craft

## Related

- [Skill Authoring Patterns](../tool-engineering/skill-authoring-patterns.md)
- [Tool Description Quality](../tool-engineering/tool-description-quality.md)
- [Skill Evals](../verification/skill-evals.md)
- [Audit Tool Descriptions](audit-tool-descriptions.md)
