---
title: "Bootstrap AGENTS.md"
description: "Detect existing instruction surfaces, probe for non-discoverable knowledge, generate root and subdirectory AGENTS.md files following pointer-map rules, and validate against the audit runbook."
tags:
  - tool-agnostic
  - instructions
aliases:
  - scaffold AGENTS.md file
  - AGENTS.md generation runbook
  - create initial AGENTS.md
---

Packaged as: [`.claude/skills/agent-readiness-bootstrap-agents-md`](../../.claude/skills/agent-readiness-bootstrap-agents-md/SKILL.md)

# Bootstrap AGENTS.md

> Detect existing instruction surfaces, probe for non-discoverable knowledge, generate root and subdirectory `AGENTS.md` per pointer-map rules, then validate.

!!! info "Harness assumption"
    `AGENTS.md` is the [open standard](https://agents.md) — this runbook is harness-agnostic. Tool-specific examples (e.g., `@AGENTS.md` import in `CLAUDE.md`) are illustrative; substitute your harness's instruction file if applicable. See [Assumptions](index.md#assumptions).

`AGENTS.md` is the [open standard](https://agents.md) discovery point for any AI coding agent. This runbook generates one (or several) following the [table-of-contents pattern](../instructions/agents-md-as-table-of-contents.md) and the [design patterns](../instructions/agents-md-design-patterns.md). The output is short, executable, and scoped — never a documentation dump.

## Step 1 — Detect Current State

```bash
# Existing AGENTS.md or equivalent
find . -maxdepth 8 \( \
  -iname "AGENTS.md" -o -iname "CLAUDE.md" -o \
  -iname "copilot-instructions.md" -o -name ".cursorrules" \
\) ! -path "*/node_modules/*" ! -path "*/.git/*"

# Subdirectories with their own toolchains (candidates for subdir AGENTS.md)
find . -maxdepth 6 -name "package.json" -o -name "pyproject.toml" \
  -o -name "Cargo.toml" -o -name "go.mod" | sort
```

Decision rules:

- **No instruction file exists** → generate root `AGENTS.md`
- **`AGENTS.md` exists** → run [`audit-agents-md`](audit-agents-md.md); rewrite only if findings warrant
- **Tool-specific file exists (`CLAUDE.md`, `copilot-instructions.md`)** → generate `AGENTS.md` and add an `@AGENTS.md` import or pointer in the existing file
- **Multiple subdirectory manifests** → generate root + one subdir `AGENTS.md` per divergent subdirectory

## Step 2 — Extract Discoverable Signals

Pull these from the repository — never invent:

| Source | Signal |
|--------|--------|
| `package.json` `scripts` | test, lint, build, dev commands |
| `pyproject.toml` `[tool.*]` | test runner, formatter, linter |
| `Cargo.toml` `[dependencies]` | runtime version, key crates |
| `go.mod` | Go version |
| `.github/workflows/*.yml` | actual CI commands |
| `Makefile`, `justfile`, `Taskfile.yml` | declared targets |
| `README.md` | project identity (one or two sentences only) |
| `.tool-versions`, `.nvmrc`, `.python-version` | runtime pinning |

```bash
# Detect package manager
test -f bun.lockb && echo "bun" \
  || test -f pnpm-lock.yaml && echo "pnpm" \
  || test -f yarn.lock && echo "yarn" \
  || test -f package-lock.json && echo "npm" \
  || test -f uv.lock && echo "uv" \
  || test -f poetry.lock && echo "poetry"

# Extract scripts
test -f package.json && jq -r '.scripts | to_entries[] | "\(.key): \(.value)"' package.json
test -f pyproject.toml && grep -E "^(test|lint|format)" pyproject.toml
```

## Step 3 — Probe Non-Discoverable Knowledge

Ask the user before generating. The only useful content in `AGENTS.md` is what an agent cannot find by reading files. Frame three to five questions; do not generate without answers:

- "What is the project, in one sentence? (audience, purpose)"
- "What is the most common mistake an unfamiliar developer would make?"
- "Are there commands that look right but are wrong here? (e.g., `npm install` when the project uses `bun`)"
- "Are there directories or branches that are off-limits?"
- "What three areas would you point a new contributor to first?"

If the user is not available, mark these sections `<!-- TODO: confirm with maintainer -->` and surface them as a finding in the report.

## Step 4 — Generate Root AGENTS.md

Use this template. Substitute placeholders with the discovered signals and probed answers. Stay ≤100 lines:

```markdown
# AGENTS.md

<one or two sentences: project identity and audience>

## Runtime and tooling

- **Package manager**: `<discovered>` — never `<common alternative>`
- **Test**: `<discovered command>`
- **Lint**: `<discovered command>`
- **Build**: `<discovered command>`
- **Runtime**: `<version from .tool-versions / .nvmrc / etc.>`

## Permission boundaries

- ✅ Always: read files, run tests, run lint, edit under `<scoped path>/`
- ⚠️ Ask: <list — usually migrations, shared schemas, CI, infra config>
- 🚫 Never: commit `.env*`, push to `<protected refs>`, edit `<deploy/release branches>`

## What to read first

| Area | Read first |
|------|-----------|
| <area 1> | `<path/to/canonical/doc.md>` |
| <area 2> | `<path>` |
| <area 3> | `<path>` |

## Non-obvious constraints

- <constraint 1, from probe>
- <constraint 2, from probe>
- <constraint 3, from probe>
```

Generation rules — enforce these before writing:

1. **Length cap**: root ≤100 lines. Trim if longer.
2. **Executable commands**: every command must include flags and target (`pytest -v tests/`, not `run tests`).
3. **Three-tier boundaries**: ✅ / ⚠️ / 🚫 — not a flat "do not" list.
4. **Hints over code**: never embed code blocks ≥20 lines. Reference the canonical file.
5. **No discoverable content**: do not list every file, every script, every dependency.
6. **No duplication**: do not restate `STANDARDS.md`, `CONTRIBUTING.md`, or rules a linter already enforces.

## Step 5 — Generate Subdirectory AGENTS.md (if needed)

For each divergent subdirectory, write a ≤30-line file:

```markdown
# <Directory Purpose>

<one sentence: what this directory contains and why>

## Conventions

- <convention specific to this directory>
- <convention 2>
- <convention 3>

## Read first

- `<path>`
```

A subdirectory `AGENTS.md` speaks only to its directory. If a convention applies project-wide, it belongs in root, not subdir.

## Step 6 — Validate

Before declaring done, run these checks. Each must pass:

```bash
# Length cap
test "$(wc -l < AGENTS.md)" -le 100 || { echo "FAIL: AGENTS.md exceeds 100 lines"; exit 1; }

# Executable commands resolve
grep -oE '`[a-z][^`]+`' AGENTS.md | tr -d '`' | while read cmd; do
  command -v "$(echo $cmd | awk '{print $1}')" >/dev/null \
    || echo "WARN: command not found in PATH: $cmd"
done

# Linked files resolve
grep -oE '`[^`]+\.[a-z]+`' AGENTS.md | tr -d '`' | while read path; do
  test -e "$path" || echo "WARN: missing file: $path"
done

# No embedded code blocks ≥20 lines
awk '/^```/{n++; if(n%2==1) start=NR; else if(NR-start>20) print "FAIL: code block at line " start " is " (NR-start) " lines"}' AGENTS.md
```

Then run [`audit-agents-md`](audit-agents-md.md) over the generated file. Resolve any high-severity findings before declaring success.

## Step 7 — Wire Cross-Tool Files

If the project uses Claude Code, Copilot, or Cursor, wire the new `AGENTS.md`:

- `CLAUDE.md` → add `@AGENTS.md` at the top
- `.github/copilot-instructions.md` → if it duplicates `AGENTS.md`, replace with a one-line pointer
- `.cursorrules` → add a comment pointer

## Idempotency

Re-run is safe. If `AGENTS.md` already exists and is audit-clean, this runbook produces no diff. If it exists but is not clean, the runbook surfaces the audit findings and asks before rewriting.

## Output Schema

When complete, emit:

```markdown
# Bootstrap AGENTS.md — <repo-name>

| Action | File | Lines |
|--------|------|------:|
| Created | AGENTS.md | <n> |
| Created | packages/api/AGENTS.md | <n> |
| Modified | CLAUDE.md | added @AGENTS.md import |

Validation: <pass/fail>
Audit: <pass/findings count>
```

## Related

- [AGENTS.md Standard](../standards/agents-md.md)
- [AGENTS.md as Table of Contents](../instructions/agents-md-as-table-of-contents.md)
- [AGENTS.md Design Patterns](../instructions/agents-md-design-patterns.md)
- [Project Instruction File Ecosystem](../instructions/instruction-file-ecosystem.md)
- [Audit AGENTS.md](audit-agents-md.md)
