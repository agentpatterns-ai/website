---
title: "Audit Hooks Coverage"
description: "Inventory wired hook events, build a coverage matrix against required-by-level events, audit each hook for severity gates, idempotency, performance, and matcher correctness, and emit a gap report."
tags:
  - tool-agnostic
  - testing-verification
aliases:
  - lifecycle hook coverage
  - hook inventory audit
  - agent hook coverage check
---

Packaged as: `.claude/skills/agent-readiness-audit-hooks-coverage/`

# Audit Hooks Coverage

> Inventory wired hook events, build a coverage matrix against required-by-level events, audit each hook for severity, idempotency, performance, and matcher correctness.

!!! info "Harness assumption"
    The event names (`PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`) come from Claude Code's lifecycle. Cursor and other harnesses expose parallel events with different names — map your harness's event taxonomy onto the coverage matrix. See [Assumptions](index.md#assumptions).

A repository can have hooks without having coverage. The default failure mode is a `PostToolUse` formatter on every edit alongside zero `Stop`-event verification — high-noise, low-protection. This runbook maps the hook inventory against the events that move the readiness needle. Rules from [hooks vs prompts](../verification/hooks-vs-prompts.md) and [hooks lifecycle](../tools/claude/hooks-lifecycle.md).

## Step 1 — Locate Hook Configuration

```bash
# Claude Code
test -f .claude/settings.json && jq '.hooks' .claude/settings.json
test -d .claude/hooks && ls -la .claude/hooks/

# Cursor
test -d .cursor/hooks && ls -la .cursor/hooks/
test -f .cursor/config.json && jq '.hooks // empty' .cursor/config.json

# Copilot extensions
test -d .github/copilot-extension && ls -la .github/copilot-extension/

# Pre-commit (commonly co-located)
test -f .pre-commit-config.yaml && yq '.repos[].hooks[]' .pre-commit-config.yaml
```

## Step 2 — Build the Coverage Matrix

For Claude Code, parse the registered hooks:

```bash
jq -r '
  .hooks | to_entries[] | .key as $event | .value[] |
  "\($event)|\(.matcher // "*")|\(.hooks[].command)"
' .claude/settings.json
```

Cross-reference against the required-by-level event table:

| Event | Matcher | Required at | Severity if missing |
|-------|---------|-------------|---------------------|
| PreToolUse | `Edit\|Write\|Bash` | L2+ | high |
| PostToolUse | `Edit\|Write` | L2+ | medium |
| Stop | `*` | L3+ | **high** (the highest-leverage gate) |
| PostToolUse loop detector | `Edit\|Write\|MultiEdit` | L3+ | medium |
| SessionStart | `*` | L4+ | low |
| PreCompact / PostCompact | `*` | L4+ | low |

Output a coverage matrix:

```python
required = [
    ("PreToolUse",   r"Edit|Write|Bash",         "L2+", "high"),
    ("PostToolUse",  r"Edit|Write",              "L2+", "medium"),
    ("Stop",         r".*",                      "L3+", "high"),
    ("PostToolUse",  r"loop-?detect",            "L3+", "medium"),
    ("SessionStart", r".*",                      "L4+", "low"),
]
findings = []
for event, matcher, level, sev in required:
    if not any(h.event == event and re.search(matcher, h.matcher or h.command, re.I) for h in registered):
        findings.append((sev, event, f"required at {level}; not wired",
                         f"run bootstrap-precompletion-hook" if event == "Stop" else
                         f"run bootstrap-loop-detector-hook" if "loop" in matcher else
                         f"add a {event} hook with matcher {matcher}"))
```

## Step 3 — Audit Each Wired Hook

For every hook that is registered, run quality checks:

### Existence and Executability

The single highest-severity failure mode: a hook is registered but the script does not exist or is not executable. The harness invokes the script for every matching event; missing or non-executable scripts exit non-zero, which Claude Code reads as `block` — every subsequent matching tool call is then blocked, including the one that would write the missing file.

```bash
jq -r '
  .hooks // {} | to_entries[] |
  .key as $event |
  .value[]?.hooks[]? | select(.type == "command") |
  "\($event)\t\(.command)"
' .claude/settings.json 2>/dev/null | while IFS=$'\t' read -r event cmd; do
  # Strip leading ./ and any trailing arguments
  PATH_ONLY=$(echo "$cmd" | awk '{print $1}' | sed 's|^\./||')
  if [[ ! -e "$PATH_ONLY" ]]; then
    echo "high|settings.json|$event hook script does not exist on disk: $cmd|create the script and chmod +x, or remove the registration; risk: every $event call blocked"
  elif [[ ! -x "$PATH_ONLY" ]]; then
    echo "high|settings.json|$event hook not executable: $cmd|chmod +x $PATH_ONLY"
  fi
done
```

If any high finding fires here, treat it as a deadlock-in-waiting and fix before any other audit work.

### Severity gates

```bash
# Hook must use exit codes 0 (allow), 1 (warn), 2 (block) — or the harness's equivalent
for hook in .claude/hooks/*.sh; do
  if ! grep -qE "exit (0|1|2)" "$hook"; then
    echo "medium|$hook|hook does not use explicit exit codes|return 0/1/2 to signal allow/warn/block"
  fi
done
```

### Idempotency

Heuristic: hook scripts that mutate persistent state (write files, send network requests) need to be safe to re-run. Detect mutations and confirm guards:

```bash
for hook in .claude/hooks/*.sh; do
  if grep -qE ">\s*[^&]|curl |wget |gh " "$hook"; then
    grep -qE "test -f|already|idempotent|>>" "$hook" || \
      echo "low|$hook|hook mutates state without an idempotency guard|read-and-compare before write"
  fi
done
```

### Performance

```bash
# Time each hook against a synthetic event payload
for hook in .claude/hooks/*.sh; do
  T=$( { time -p echo '{"tool_name":"Edit","tool_input":{"file_path":"/tmp/x"}}' | "$hook" >/dev/null 2>&1; } 2>&1 | awk '/real/{print $2}')
  awk -v t="$T" -v h="$hook" 'BEGIN{ if(t>2.0) print "medium|"h"|hook took "t"s (target <2s)|profile and reduce work" }'
done
```

### Matcher Correctness

A `PostToolUse` hook should not fire on `Read`, `Grep`, or other read-only tools:

```bash
jq -r '.hooks.PostToolUse[]? | .matcher' .claude/settings.json | while read matcher; do
  if echo "$matcher" | grep -qE "Read|Grep|Glob"; then
    echo "medium|settings.json|PostToolUse matcher includes read-only tools|exclude Read/Grep/Glob — wastes cycles"
  fi
done
```

### Failure Observability

```bash
for hook in .claude/hooks/*.sh; do
  grep -qE "tee|>>.*log|jsonl" "$hook" || \
    echo "low|$hook|hook does not log structured failures|append to .claude/state/hook-log.jsonl"
done
```

## Step 4 — Emit Coverage Report

```markdown
# Audit Report — Hooks Coverage

## Coverage matrix

| Event | Matcher | Wired? | Required at | Severity |
|-------|---------|:------:|:-----------:|:--------:|
| PreToolUse | Edit\|Write\|Bash | ✅ | L2 | block |
| PostToolUse | Edit\|Write | ✅ | L2 | warn |
| Stop | * | ❌ | L3 | **MISSING** |
| PostToolUse | loop-detect | ❌ | L3 | missing |
| SessionStart | * | ❌ | L4 | defer |

## Per-hook quality

| Hook | Severity | Idempotent | Time | Matcher | Logs |
|------|:--------:|:----------:|:----:|:-------:|:----:|
| pre-commit-format.sh | warn | ✅ | 3.4s | OK | ❌ |

## Top findings

| Severity | Finding | Action |
|----------|---------|--------|
| high | No Stop hook → no pre-completion gate | Run `bootstrap-precompletion-hook` |
| medium | No loop detection on PostToolUse | Run `bootstrap-loop-detector-hook` |
| medium | pre-commit-format.sh takes 3.4s avg | move to staged-only mode or async |
```

## Step 5 — Hand Off

For each missing required-at-level event, name the bootstrap runbook to invoke. For each existing-but-poor-quality hook, propose a targeted patch (matcher fix, exit-code addition, log redirection).

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Hooks Coverage — <repo>

| Required | Wired | Missing | Quality |
|---------:|------:|--------:|--------:|
| <n> | <n> | <n> | <n>/<n> pass |

Next: <bootstrap-precompletion-hook | bootstrap-loop-detector-hook | targeted fixes>
```

## Remediation

- [Bootstrap Hooks Scaffold](bootstrap-hooks-scaffold.md) — lay down stubs for every event so enforcement has a place to land
- [Bootstrap Pre-Completion Hook](bootstrap-precompletion-hook.md) — the single highest-leverage event; close the L2→L3 gap
- [Bootstrap Loop Detector Hook](bootstrap-loop-detector-hook.md) — edit-count loop detection on PostToolUse

## Related

- [Hooks Lifecycle](../tools/claude/hooks-lifecycle.md)
- [Hooks vs Prompts](../verification/hooks-vs-prompts.md)
- [Pre-Completion Checklists](../verification/pre-completion-checklists.md)
- [Loop Detection](../observability/loop-detection.md)
