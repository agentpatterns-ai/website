---
title: "Audit Rules-File Injection Surface"
description: "Enumerate every rules and instruction file an agent reads at session start, scan for embedded injection markers, classify by trust tier, and emit per-file findings with deny-rule remediations."
tags:
  - tool-agnostic
  - security
aliases:
  - rules file injection audit
  - instruction file injection scan
  - CLAUDE.md injection surface check
---

Packaged as: `.claude/skills/agent-readiness-audit-rules-files-injection/`

# Audit Rules-File Injection Surface

> Enumerate the rules and instruction files an agent reads at session start, scan for injection markers, classify by trust tier, and emit deny-rule remediations.

!!! info "Harness assumption"
    The runbook covers Claude Code, Cursor, Copilot, Windsurf, Aider, and any harness that auto-loads a project-rooted instruction file. File names differ per harness — translate the inventory step accordingly. See [Assumptions](index.md#assumptions).

Rules files are the highest-leverage prompt injection surface in any coding harness — they are read at session start, applied to every turn, and frequently sourced from cloned repositories the user did not author. The technique is documented in [Discovering Indirect Injection Vulnerabilities](../security/indirect-injection-discovery.md) §Step 4: Test rules file injection and the attack-surface taxonomy in [Designing Agents to Resist Prompt Injection](../security/prompt-injection-resistant-agent-design.md) §Coding Assistant Attack Surfaces. This runbook turns those steps into a repeatable scan.

## Step 1 — Enumerate Rules Files

```bash
# Project-rooted instruction files across harnesses
find . -maxdepth 3 -type f \( \
  -name "CLAUDE.md" -o -name "AGENTS.md" -o -name ".cursorrules" -o \
  -name ".cursor/rules" -o -name ".windsurfrules" -o -name ".aider.conf.yml" -o \
  -name "copilot-instructions.md" \
\) 2>/dev/null

# Per-directory CLAUDE.md / AGENTS.md (loaded when CWD enters that dir)
find . -type f \( -name "CLAUDE.md" -o -name "AGENTS.md" \) 2>/dev/null

# .github/copilot-instructions.md and instruction sub-files
find .github -type f \( -name "copilot-instructions.md" -o -path "*/instructions/*.md" \) 2>/dev/null

# .claude/commands and .claude/skills (rules-equivalent surfaces)
find .claude -type f \( -name "*.md" -o -name "settings*.json" \) 2>/dev/null
```

For each file, record the path, byte size, and last-modified author (`git log -1 --pretty=%an -- "$file"`).

## Step 2 — Classify by Trust Tier

Each file falls into one of three tiers. The tier determines how aggressively to scan and remediate.

| Tier | Definition | Action on suspicious content |
|------|-----------|------------------------------|
| **T1 — User-authored** | Last commit by the current user or a known org member; no third-party dependency in the file path | Scan; warn on findings |
| **T2 — Cloned / vendored** | File is in a path that originated from `git clone`, `npm install`, a submodule, or a downloaded archive | Scan; **block load** until reviewed |
| **T3 — Generated** | File is produced by a tool the agent runs (e.g., a reviewer subagent writes `REVIEW.md`) | Scan; restrict to advisory tier — never load as instruction |

```bash
# Detect dependency-imported instruction files
git submodule status 2>/dev/null | awk '{print $2}'
test -f package.json && jq -r '.dependencies // {} | keys[]' package.json | head -20
# Cross-reference against discovered rules-file paths
```

## Step 3 — Scan for Injection Markers

Parse each file for the patterns that flip rules-file content into agent instructions. Severity is assigned per pattern.

```python
import re
from pathlib import Path

PATTERNS = [
    # High: explicit instruction-injection phrasing
    (r"(?i)\b(ignore|disregard) (?:all )?(previous|prior|above) (?:instructions|rules|context)\b", "high",
     "explicit override directive"),
    (r"(?i)\bnew (?:instructions|directives)\s*[:.]", "high",
     "instruction-replacement marker"),
    (r"(?i)\b(?:system|developer)\s*[:>]\s*", "high",
     "fake role-tag injection"),
    (r"(?i)\bexecute (?:this|the following)\b.{0,40}\b(curl|wget|bash|sh|powershell)\b", "high",
     "remote-execution lure"),
    (r"(?i)\b(api[_ ]?key|secret|token|credential)s?\b.{0,40}\b(send|post|exfiltrate|share|email)\b", "high",
     "credential-exfiltration lure"),
    # Medium: tool-coercion phrasing
    (r"(?i)\bmust (?:always )?(?:use|call|run)\b.{0,40}\b(?:WebFetch|fetch|curl|http)\b", "medium",
     "forced egress tool call"),
    (r"(?i)\b(?:always|never) commit\b", "medium",
     "blanket commit directive — review polarity"),
    # Low: structural anomalies
    (r"```[a-zA-Z]*\n[^`]{800,}\n```", "low",
     "very large embedded code block (review for hidden directives)"),
    (r"(?i)<\s*system\s*>", "low",
     "HTML-style system tag (rendered as instruction by some harnesses)"),
]

def scan(path: Path):
    text = path.read_text(errors="replace")
    findings = []
    for pat, sev, msg in PATTERNS:
        for m in re.finditer(pat, text):
            line = text[: m.start()].count("\n") + 1
            findings.append({"path": str(path), "line": line, "severity": sev, "match": msg})
    return findings
```

A T2 file with **any** high-severity finding should fail the audit. T1 files with high-severity findings warn.

## Step 4 — Cross-Check Against the Lethal Trifecta

A rules file with injection markers is most dangerous when the agent it instructs holds the [lethal trifecta](../security/lethal-trifecta-threat-model.md) — private data, untrusted content, and egress. Cross-reference the per-principal matrix from [`audit-lethal-trifecta`](audit-lethal-trifecta.md):

```bash
# If the trifecta audit produced JSON, intersect
test -f .claude/agent-readiness/lethal-trifecta.json && \
  jq '.principals[] | select(.private_data and .untrusted_content and .egress) | .name' \
    .claude/agent-readiness/lethal-trifecta.json
```

Findings that overlap with a `(1,1,1)` principal escalate one severity tier — a medium becomes high.

## Step 5 — Emit Findings and Deny-Rule Remediations

```markdown
# Audit Report — Rules-File Injection Surface

## Inventory
| Path | Tier | Bytes | Last author |
|------|------|------:|-------------|

## Findings
| Severity | Path | Line | Pattern | Trifecta-amplified |
|----------|------|-----:|---------|:------------------:|

## Remediations

### For T2 cloned files with high findings
Add to `.claude/settings.json` `permissions.deny`:
```json
{"permissions": {"deny": ["Read(<path>/CLAUDE.md)", "Read(<path>/.cursorrules)"]}}
```

### For T1 high findings
Open the file at the cited line; rewrite to remove the override directive, role tag, or
exfiltration lure. Re-run the audit until clean.

### For trifecta-amplified findings
Decompose the principal: split private-data, untrusted-content, and egress capabilities
across separate sub-agents per [`bootstrap-egress-policy`](bootstrap-egress-policy.md).
```

## Step 6 — Hand Off

For each remediation that requires an instruction-file rewrite, point the user at [`audit-instruction-placement`](audit-instruction-placement.md) and [`audit-claude-md`](audit-claude-md.md) to validate the rewrite stays well-formed.

For a `(1,1,1)` overlap, halt the broader assessment and walk the user through trifecta decomposition before re-running other audits — same posture as a high finding from [`audit-secrets-in-context`](audit-secrets-in-context.md).

## Idempotency

Read-only. Re-running on a clean repo produces no findings. Re-running after a remediation produces a delta showing which rules files were rewritten.

## Output Schema

```markdown
# Audit Rules-File Injection Surface — <repo>

| Files scanned | T1 | T2 | T3 | High findings | Trifecta-amplified |
|--------------:|---:|---:|---:|--------------:|-------------------:|
| <n> | <n> | <n> | <n> | <n> | <n> |

Top fix: <one-liner — usually a T2 cloned CLAUDE.md with override directive>
```

## Related

- [Discovering Indirect Injection Vulnerabilities](../security/indirect-injection-discovery.md)
- [Designing Agents to Resist Prompt Injection](../security/prompt-injection-resistant-agent-design.md)
- [Lethal Trifecta Threat Model](../security/lethal-trifecta-threat-model.md)
- [Audit Lethal Trifecta](audit-lethal-trifecta.md)
- [Audit Secrets in Context](audit-secrets-in-context.md)
- [Audit CLAUDE.md](audit-claude-md.md)
- [Audit Instruction Placement](audit-instruction-placement.md)
