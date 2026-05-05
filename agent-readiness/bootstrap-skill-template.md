---
title: "Bootstrap Skill Template"
description: "Generate an opinionated SKILL.md skeleton with frontmatter, description-craft template, CLI-first body wired to a scripts/ directory, and a Gotchas section seed — paired remediation for skill-quality findings."
tags:
  - tool-agnostic
  - cost-performance
aliases:
  - scaffold SKILL.md
  - skill template generator
  - SKILL.md skeleton
---

# Bootstrap Skill Template

> Generate an opinionated `SKILL.md` skeleton with frontmatter, description-craft template, CLI-first body wired to `scripts/`, and a Gotchas seed.

!!! info "Harness assumption"
    `SKILL.md` is the Claude Code skill format and Cursor's `.cursor/skills/` mirror. Other harnesses without an on-demand skill primitive have no direct equivalent — adapt the template into a system-prompt fragment or a sub-agent definition for those tools. See [Assumptions](index.md#assumptions).

A new skill should follow the [skill authoring patterns](../tool-engineering/skill-authoring-patterns.md) from the start — retrofitting description craft and Gotchas onto a skill that grew organically is harder than starting right. This is the paired remediation for [`audit-skill-quality`](audit-skill-quality.md) when the audit returns "no skill exists yet" or "rewrite needed".

## Step 1 — Detect Current State

```bash
# Skill location varies by harness
SKILL_ROOT=""
test -d .claude/skills && SKILL_ROOT=".claude/skills"
test -d .cursor/skills && SKILL_ROOT=".cursor/skills"
test -d skills && SKILL_ROOT="skills"

echo "skill root: ${SKILL_ROOT:-<none — defaulting to .claude/skills>}"
ls "${SKILL_ROOT:-.claude/skills}" 2>/dev/null
```

Decision rules:

- **No skill root** → create `.claude/skills/` (Claude Code default); ask the user if a different harness is in use
- **Existing skill of the same name** → halt; ask whether to overwrite or pick a different name
- **Run [`audit-skill-quality`](audit-skill-quality.md) first** if rewriting; the audit drives the rewrite

## Step 2 — Probe the User

Three questions, no generation without answers (the description and Gotchas cannot be invented):

1. "What does this skill do, in one sentence?"
2. "When should the agent invoke it, and when should it skip?"
3. "What goes wrong with this kind of task — name 3 specific failure modes if you have them, otherwise mark TBD."

If the user has incident records or transcripts of the failures the skill is meant to prevent, mine them for the Gotchas list.

## Step 3 — Generate the Directory

```bash
SKILL_NAME="$1"
SKILL_DIR="${SKILL_ROOT:-.claude/skills}/$SKILL_NAME"
mkdir -p "$SKILL_DIR/scripts"
```

## Step 4 — Generate SKILL.md

```markdown
---
name: <skill-name>
description: <one sentence: what>. Use this when <trigger condition>. Skip when <negative trigger>. Key capabilities: <c1>, <c2>, <c3>.
version: "0.1.0"
---

# <Skill Title>

<one-sentence summary in plain prose, identical in spirit to the frontmatter description>.

## When to Use

- <trigger 1 — concrete user message or task type>
- <trigger 2>
- <trigger 3>

Skip when:

- <negative trigger 1>
- <negative trigger 2>

## Process

1. <Step 1 — short imperative>
2. <Step 2>
3. <Step 3>

(Steps that involve more than 3 lines of shell go in `scripts/`. Call them from here.)

## Example

<one concrete example: input → invocation → output>

## Gotchas

- <failure mode 1: a specific case where the agent does something plausible but wrong>
- <failure mode 2>
- <failure mode 3>

(Add to this section as new failures are discovered; this is the highest-signal block.)

## Related

- [<related skill>](../<related>/SKILL.md)
- [<source page on this site>](<url>)
```

Generation rules:

1. **Description in 4 blocks**: one-sentence-what + use-when + skip-when + key-capabilities
2. **Triggers must be concrete** — name the user message or task type, not a category
3. **Process steps are short imperatives** — long shell goes in `scripts/`
4. **Example is real** — drawn from a probed scenario, not invented
5. **Gotchas seeded with 3 entries minimum** — even if marked TBD, the section frame must exist
6. **Body ≤200 lines** — tighten if the user provides more material; the body's job is to wrap the script, not be the script

## Step 5 — Generate scripts/

```bash
cat > "$SKILL_DIR/scripts/main.sh" <<'EOF'
#!/usr/bin/env bash
# Main entry point for the <skill-name> skill.
# SKILL.md calls this; logic lives here so it can be tested in isolation.
set -euo pipefail

# <real implementation goes here as the user fleshes out the skill>
echo "stub: implement <skill-name>"
EOF
chmod +x "$SKILL_DIR/scripts/main.sh"
```

Add a `scripts/README.md` if the skill needs more than one script:

```bash
test "$NUM_SCRIPTS" -gt 1 && cat > "$SKILL_DIR/scripts/README.md" <<'EOF'
# Scripts for <skill-name>

| Script | Purpose |
|--------|---------|
| main.sh | <purpose> |
EOF
```

## Step 6 — Validate

```bash
# Run the per-skill audit
python3 -c "
import frontmatter, sys, re
p = frontmatter.load(sys.argv[1])
fm = p.metadata
assert fm.get('name'), 'missing name'
assert fm.get('description'), 'missing description'
assert re.search(r'\buse (this )?when\b', fm['description'], re.I), 'description missing trigger'
assert re.search(r'\bskip when\b|\bdo not use\b', fm['description'], re.I), 'description missing negative trigger'
print('OK')
" "$SKILL_DIR/SKILL.md"

# Body has Gotchas section
grep -qE '^## Gotchas' "$SKILL_DIR/SKILL.md" || echo "FAIL: no Gotchas section"
```

Then run [`audit-skill-quality`](audit-skill-quality.md) over the skill root; the new skill should pass.

## Step 7 — Document

If `AGENTS.md` lists project skills, add a one-line pointer:

```markdown
- `<skill-name>` — <one-line purpose>; see `.claude/skills/<skill-name>/SKILL.md`
```

## Idempotency

Re-running on an existing skill name halts (do not overwrite). To regenerate, the user must explicitly delete the existing directory first.

## Output Schema

```markdown
# Bootstrap Skill Template — <skill-name>

| Action | File | Notes |
|--------|------|-------|
| Created | .claude/skills/<name>/SKILL.md | <n> lines, description: <pass/fail> |
| Created | .claude/skills/<name>/scripts/main.sh | mode 0755 (stub) |
| Modified | AGENTS.md | added skill pointer |

Audit: <pass/findings>
Next: implement scripts/main.sh; expand Gotchas as failures emerge
```

## Related

- [Skill Authoring Patterns](../tool-engineering/skill-authoring-patterns.md)
- [Skill Evals](../verification/skill-evals.md)
- [Audit Skill Quality](audit-skill-quality.md)
- [Bootstrap Tool Descriptions](bootstrap-tool-descriptions.md)
