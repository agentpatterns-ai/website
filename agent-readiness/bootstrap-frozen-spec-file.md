---
title: "Bootstrap Frozen Spec File"
description: "Generate a SPEC.json with goals, non-goals, hard constraints, deliverables, and done-when criteria; install a PreToolUse hook that blocks writes to the spec path; and emit a system-prompt re-read directive that survives compaction."
tags:
  - tool-agnostic
  - instructions
aliases:
  - frozen spec scaffold
  - SPEC.json bootstrap
  - immutable spec setup
---

Packaged as: `.claude/skills/agent-readiness-bootstrap-frozen-spec-file/`

# Bootstrap Frozen Spec File

> Generate a SPEC.json with goals, non-goals, hard constraints, deliverables, and done-when criteria; block writes via a PreToolUse hook; emit a system-prompt re-read directive that survives compaction.

!!! info "Harness assumption"
    The PreToolUse hook targets Claude Code's `.claude/settings.json` schema and matcher syntax. Cursor, Aider, and Copilot expose pre-tool gates differently — translate the matcher and command for those harnesses. The system-prompt directive is harness-agnostic. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip this runbook for short tasks (under one session) and exploration work where the goal is intentionally fluid. The frozen spec adds overhead that only pays off when the task spans compactions or sessions and when scope creep is the dominant failure mode. See [Frozen Spec File](../instructions/frozen-spec-file.md) §When This Backfires.

The [Frozen Spec File](../instructions/frozen-spec-file.md) pattern is structural protection of intent: a file the agent re-reads after every compaction, with hard enforcement against the agent rewriting it. This runbook turns the pattern into a generator that ships the file, the hook, and the directive together — and validates each layer before declaring done.

## Step 1 — Detect Existing Spec State

```bash
# Existing spec file (any of the conventional names)
find . -maxdepth 2 -type f \( \
  -name "SPEC.json" -o -name "SPEC.md" -o -name "Prompt.md" -o -name "frozen-spec.json" \
\) 2>/dev/null

# Existing PreToolUse hook scoped to spec
test -f .claude/settings.json && \
  jq '.hooks.PreToolUse[]? | select((.hooks[]?.command // "") | test("SPEC|frozen-spec"))' \
    .claude/settings.json

# Existing system-prompt re-read directive
grep -lE "re-?read.*SPEC|never modify SPEC" CLAUDE.md AGENTS.md 2>/dev/null
```

Decision rules:

- **Spec file exists and hook present** → audit each layer (Step 5 below) instead of regenerating.
- **Spec file exists but hook missing** → skip Step 2; continue from Step 3 to wire enforcement.
- **No spec file** → run all steps.

## Step 2 — Generate the Spec

Choose JSON over Markdown by default — Anthropic's harness research found agents are less likely to mutate JSON files than Markdown files, per [Frozen Spec File](../instructions/frozen-spec-file.md) §Why Immutability Matters.

Prompt the user (or pull from issue body, project README, or kickoff doc) for the five sections:

```bash
cat > SPEC.json <<'EOF'
{
  "goals": [
    ""
  ],
  "non_goals": [
    ""
  ],
  "hard_constraints": [
    ""
  ],
  "deliverables": [
    ""
  ],
  "done_when": [
    ""
  ]
}
EOF
```

Validation rules — the bootstrap fails closed if any section is empty:

```bash
jq -e '
  (.goals | length > 0) and
  (.non_goals | length > 0) and
  (.hard_constraints | length > 0) and
  (.deliverables | length > 0) and
  (.done_when | length > 0)
' SPEC.json >/dev/null || { echo "FAIL: every section must be populated"; exit 1; }
```

Non-goals must be populated — they are first-class and the section that prevents scope creep, per [Frozen Spec File](../instructions/frozen-spec-file.md) §Anatomy of a Frozen Spec.

## Step 2b — Spec Quality Properties

Beyond presence-of-section, validate the spec against four properties that make it usable as a regenerable source-of-truth ([`bootstrapping-coding-agents`](../emerging/bootstrapping-coding-agents.md)):

- **Auditable** — under ~1,500 words, readable in 15 minutes. A reviewer must hold the full spec in working memory.
- **Behaviorally complete** — every behavior, error condition, and edge case the deliverable must satisfy is documented. Gaps produce divergent regenerations.
- **Convergence-testable** — two independent regenerations from the same spec produce identical external behavior. If they diverge, treat divergence as a spec-ambiguity signal, not an implementation bug.
- **Abstraction-focused** — describes *what* the deliverable does, not *how*. Implementation detail in the spec constrains regeneration without adding correctness.

```bash
# Word count gate
WC=$(jq -r '[.. | strings] | join(" ") | length / 6 | floor' SPEC.json)
[ "$WC" -gt 1500 ] && echo "WARN: spec is $WC words; trim toward auditable cap of 1500"

# Heuristic for implementation leakage in the constraints/done_when fields
jq -r '(.hard_constraints + .done_when)[]' SPEC.json \
  | grep -iE '\b(class |function |import |def |const |let |var )\b' \
  && echo "WARN: implementation-level tokens in spec; rephrase as behavior"
```

If the spec exceeds the auditable cap, split the deliverable rather than expanding the spec — multi-deliverable tasks need one SPEC.json per deliverable. Implementation-level tokens (class/function/import) signal a how-not-what failure.

## Step 3 — Write the PreToolUse Hook (Before Wiring)

Per [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) §Safety: write before wire, create the hook script and smoke-test it before adding the entry to `settings.json`. A registered-but-broken hook blocks every tool call.

`.claude/hooks/block-spec-edits.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
EVENT="$(cat)"
PATH_EDITED="$(echo "$EVENT" | jq -r '.tool_input.file_path // .tool_input.path // ""')"
case "$PATH_EDITED" in
  *SPEC.json|*SPEC.md|*frozen-spec.json|*Prompt.md)
    echo '{"decision":"block","reason":"SPEC is frozen — open an issue to amend the spec, do not edit in-session"}'
    exit 2
    ;;
esac
echo '{"decision":"approve"}'
exit 0
```

```bash
chmod +x .claude/hooks/block-spec-edits.sh
```

## Step 4 — Smoke Test the Hook

```bash
# Approve case
echo '{"tool_input":{"file_path":"src/foo.ts"}}' | .claude/hooks/block-spec-edits.sh
# Expect: {"decision":"approve"} exit 0

# Block case
echo '{"tool_input":{"file_path":"SPEC.json"}}' | .claude/hooks/block-spec-edits.sh
# Expect: {"decision":"block",...} exit 2
```

Both must produce structured JSON. If either fails, fix the script before Step 5.

## Step 5 — Wire the Hook

Only after Step 4 passes. Merge into `.claude/settings.json` with `jq` — never overwrite:

```bash
jq '.hooks.PreToolUse = ((.hooks.PreToolUse // []) + [{
  matcher: "Edit|Write|MultiEdit",
  hooks: [{type: "command", command: ".claude/hooks/block-spec-edits.sh"}]
}])' .claude/settings.json > .claude/settings.json.tmp \
  && mv .claude/settings.json.tmp .claude/settings.json
```

If `settings.json` does not exist, create it with the structure above wrapped in `{}`. Recovery from a wired-but-broken hook follows [`bootstrap-precompletion-hook`](bootstrap-precompletion-hook.md) §Recovery — open the file outside the agent, remove the entry, fix, re-wire.

## Step 6 — Emit the Re-Read Directive

The hook prevents rewrites. The directive prevents the agent forgetting the spec exists after compaction. Append to `CLAUDE.md` (Claude Code) or `AGENTS.md` (per [`bootstrap-agents-md`](bootstrap-agents-md.md)):

```markdown
## Frozen spec

`SPEC.json` is the immutable source of truth for this task. Read it at session start and after every compaction event. Verify each action against goals, non-goals, hard-constraints. Never edit SPEC.json — if a constraint blocks progress, stop and surface the conflict.
```

The placement matters — per [`audit-instruction-placement`](audit-instruction-placement.md), this is a critical rule and must sit in the primacy or recency band of the instruction file. Append to the end (recency) unless the file's structure dictates otherwise.

## Step 7 — Validate the Triple Layer

The spec is only as strong as the weakest of the three layers. Confirm each:

```bash
# Layer 1 — file present and well-formed
test -f SPEC.json && jq -e '.goals and .non_goals and .hard_constraints' SPEC.json >/dev/null

# Layer 2 — hook wired and matcher correct
jq -e '.hooks.PreToolUse[]?.hooks[]?.command | select(. | contains("block-spec-edits.sh"))' \
  .claude/settings.json >/dev/null

# Layer 3 — directive present in instruction file
grep -lE "SPEC\.json|frozen spec" CLAUDE.md AGENTS.md 2>/dev/null
```

All three must pass before declaring complete.

## Idempotency

Re-running with the same SPEC.json content produces no diff. Re-running after a manual spec amend leaves the file in place and only reapplies the hook and directive if either is missing.

## Output Schema

```markdown
# Bootstrap Frozen Spec File — <repo>

| Action | File | Notes |
|--------|------|-------|
| Created | SPEC.json | <n> goals, <n> non-goals, <n> constraints |
| Created | .claude/hooks/block-spec-edits.sh | mode 0755, smoke-tested |
| Modified | .claude/settings.json | added PreToolUse hook on Edit/Write/MultiEdit |
| Modified | CLAUDE.md | appended re-read directive |

Validation: layer-1 ✅ layer-2 ✅ layer-3 ✅
```

## Related

- [Frozen Spec File](../instructions/frozen-spec-file.md)
- [Bootstrapping Coding Agents](../emerging/bootstrapping-coding-agents.md)
- [Spec-Driven Development](../workflows/spec-driven-development.md)
- [Bootstrap AGENTS.md](bootstrap-agents-md.md)
- [Bootstrap Pre-Completion Hook](bootstrap-precompletion-hook.md)
- [Audit Instruction Placement](audit-instruction-placement.md)
- [Audit CLAUDE.md](audit-claude-md.md)
