---
title: "Audit Slash Command Catalog"
description: "Enumerate every model-invocable slash command and prompt file, validate description craft, detect missing user-invocable / disable-model-invocation gates on side-effectful commands, and emit per-command findings."
tags:
  - tool-agnostic
  - tool-engineering
  - security
aliases:
  - slash command surface audit
  - prompt file catalog audit
  - agent-discoverable command quality check
---

Packaged as: `.claude/skills/agent-readiness-audit-slash-command-catalog/`

# Audit Slash Command Catalog

> Enumerate every slash command and prompt file the planner can invoke, validate description craft and idempotency contract, flag side-effectful commands without `disable-model-invocation`, emit per-command findings.

!!! info "Harness assumption"
    Slash commands live under `.claude/commands/`, `.claude/skills/<name>/SKILL.md`, `.github/prompts/*.prompt.md` (Copilot), or `.cursor/commands/`. Each carries YAML frontmatter and a body. Skip this runbook for harnesses without a slash-command primitive.

Once the planner can discover and invoke slash commands ([`agent-discoverable-slash-commands`](../agent-design/agent-discoverable-slash-commands.md)), every slash command becomes part of the agent's tool graph. A command without a trigger phrase fails to fire. A side-effectful command without `disable-model-invocation: true` lets the planner deploy, commit, or send messages without a human typing the slash. Rules from [`agent-discoverable-slash-commands`](../agent-design/agent-discoverable-slash-commands.md) and [`prompt-file-libraries`](../instructions/prompt-file-libraries.md).

## Step 1 — Locate Commands

```bash
find . \( \
  -path "*/.claude/commands/*.md" \
  -o -path "*/.claude/skills/*/SKILL.md" \
  -o -path "*/.cursor/commands/*.md" \
  -o -path "*/.github/prompts/*.prompt.md" \
\) ! -path "*/node_modules/*"
```

Capture for each: file path, frontmatter, body length, command name.

## Step 2 — Frontmatter and Naming

Every command file must parse as YAML frontmatter + body. Required: `name` (kebab-case), `description`. Slash command name should match the filename stem.

```bash
for cmd in $COMMANDS; do
  python3 - "$cmd" <<'PY'
import sys, yaml, os
text = open(sys.argv[1]).read()
if not text.startswith('---'):
    print(f'high|{sys.argv[1]}|missing frontmatter|add YAML with name and description')
    sys.exit()
fm = yaml.safe_load(text.split('---', 2)[1]) or {}
stem = os.path.splitext(os.path.basename(sys.argv[1]))[0]
if stem == 'SKILL':
    stem = os.path.basename(os.path.dirname(sys.argv[1]))
if not fm.get('name'):
    print(f'high|{sys.argv[1]}|frontmatter missing name|add name: {stem}')
elif fm.get('name') != stem and fm.get('name') != f'/{stem}':
    print(f'medium|{sys.argv[1]}|name "{fm.get("name")}" does not match filename stem "{stem}"|rename or align')
if not fm.get('description'):
    print(f'high|{sys.argv[1]}|frontmatter missing description|description is what the planner reads to decide invocation')
PY
done
```

## Step 3 — Description Craft

The description sits in the system prompt at all times for model-invocable commands. Score on four axes (same as [`audit-skill-quality`](audit-skill-quality.md) Step 3):

| Axis | Test | Severity if missing |
|------|------|---------------------|
| Trigger phrase | matches `use when |invoke when |run when` | high |
| Negative trigger | matches `do not use|skip when|avoid` | medium |
| Third-person voice | no `I can`, `I'll`, `let me` | medium |
| Front-loaded use case | use case in first 80 chars | low |

```bash
DESC=$(yq '.description // ""' "$cmd")
echo "$DESC" | grep -qiE "use when|invoke when|run when" \
  || echo "high|$cmd|description lacks trigger phrase|add 'use when X'"
echo "$DESC" | grep -qiE "do not use|skip when|avoid when" \
  || echo "medium|$cmd|no negative trigger|add 'do not use when Y'"
echo "$DESC" | grep -qiE "^I |I'll|let me" \
  && echo "medium|$cmd|first-person voice|rewrite in third person ('Processes X', not 'I help with X')"
```

## Step 4 — Side-Effect Detection and Invocation Gates

The danger surface is side-effectful commands that the planner can fire without explicit user confirmation. Detect side effects from the body and from the `allowed-tools` frontmatter.

```bash
SIDE_EFFECT_VERBS='deploy|commit|push|merge|send|email|publish|delete|drop|rm '
SIDE_EFFECT_TOOLS='Bash\(.*git (commit|push)|Bash\(.*deploy|Bash\(.*rm |Bash\(.*curl.*-X (POST|PUT|DELETE)'

NAME=$(yq '.name // ""' "$cmd")
BODY=$(awk '/^---$/{c++; next} c==2{print}' "$cmd")
ALLOWED=$(yq '."allowed-tools" // [] | join(",")' "$cmd")
DMI=$(yq '."disable-model-invocation" // false' "$cmd")

is_side_effect=0
echo "$NAME$BODY" | grep -qiE "$SIDE_EFFECT_VERBS" && is_side_effect=1
echo "$ALLOWED" | grep -qiE "$SIDE_EFFECT_TOOLS" && is_side_effect=1

if [[ $is_side_effect -eq 1 && "$DMI" != "true" ]]; then
  echo "high|$cmd|side-effectful command without disable-model-invocation|set disable-model-invocation: true so only the user can invoke"
fi
```

Reference: [`agent-discoverable-slash-commands` §The Control Matrix](../agent-design/agent-discoverable-slash-commands.md). Anthropic guidance: "you don't want Claude deciding to deploy because your code looks ready."

## Step 5 — Description Length Budget

Skill listings are truncated at ~1,536 characters per command and the listing as a whole at ~8,000 characters (scaling at 1% of context window). Long descriptions in the front of the catalog crowd later commands out of context.

```bash
DESC_LEN=$(echo -n "$(yq '.description // ""' "$cmd")" | wc -c)
[[ $DESC_LEN -gt 800 ]] && echo "medium|$cmd|description is $DESC_LEN chars|trim to ≤500; long descriptions crowd siblings out at the listing budget"
```

Total catalog budget:

```bash
TOTAL=$(yq -s 'map(.description // "" | length) | add' $COMMANDS_AS_LIST)
[[ $TOTAL -gt 8000 ]] && echo "high|catalog|total description bytes ($TOTAL) exceed 8000-char listing budget|consolidate or split commands"
```

## Step 6 — Allowed-Tools Tightness

`allowed-tools` pre-approves tools while the command runs. Audit for:

- Wildcards in `allowed-tools` (`Bash(*)`, `Edit(*)`)
- `allowed-tools` listing tools the body never invokes
- Side-effectful tools pre-approved on a model-invocable command

```bash
yq '."allowed-tools" // []' "$cmd" | grep -qE 'Bash\(\*\)|Edit\(\*\)|Write\(\*\)' \
  && echo "high|$cmd|wildcard in allowed-tools|enumerate the exact tool calls the body needs"
```

## Step 7 — Per-Command Scorecard

```markdown
# Audit Report — Slash Command Catalog

## Per-command scorecard

| Command | FM | Trigger | Side-effect gate | Allowed-tools tight | Desc len | Top issue |
|---------|:--:|:-------:|:----------------:|:-------------------:|---------:|-----------|
| /<name> | ✅ | ⚠️ | ❌ | ✅ | <n> | <one-line> |

## Findings

| Severity | Command | Finding | Suggested fix |
|----------|---------|---------|---------------|
| high | /<cmd> | <finding> | <fix> |

## Catalog totals

- Commands: <n>
- Total description bytes: <n> / 8000 budget
- Side-effectful commands: <n> (gated: <n>, ungated: <n>)
```

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Slash Command Catalog — <repo>

| Commands | Pass | Warn | Fail | Ungated side-effect |
|---------:|-----:|-----:|-----:|-------------------:|
| <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually missing trigger or ungated side-effect>
```

## Remediation

- [Bootstrap Tool Descriptions](bootstrap-tool-descriptions.md) — when failing axis is description craft
- [Bootstrap Skill Template](bootstrap-skill-template.md) — for SKILL.md-shaped commands
- [Audit Tool Descriptions](audit-tool-descriptions.md) — overlapping description-quality coverage

## Related

- [Agent-Discoverable Slash Commands](../agent-design/agent-discoverable-slash-commands.md)
- [Prompt File Libraries](../instructions/prompt-file-libraries.md)
- [Tool Description Quality](../tool-engineering/tool-description-quality.md)
- [Audit Skill Quality](audit-skill-quality.md)
- [Audit Permissions Blast Radius](audit-permissions-blast-radius.md)
