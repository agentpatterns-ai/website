---
title: "Audit Action-Audit Divergence"
description: "Walk the F1-F4 divergence taxonomy against an agent runtime — name the chokepoint, integrity mechanism, liveness probe, and target validator — and convert each unanswered question into a concrete finding mapped to existing controls."
tags:
  - tool-agnostic
  - security
  - observability
aliases:
  - F1 F2 F3 F4 audit
  - action-audit divergence audit
  - audit-record divergence audit
---

Packaged as: `.claude/skills/agent-readiness-audit-action-audit-divergence/`

# Audit Action-Audit Divergence

> Walk the F1-F4 divergence taxonomy against the runtime — name the chokepoint, integrity mechanism, liveness probe, and target validator — and convert each unanswered question into a finding mapped to existing controls.

!!! info "Harness assumption"
    Targets a runtime with declared tool calls (Claude Code `.claude/settings.json` and `.mcp.json`, equivalents for Cursor / Aider / Copilot / Gemini). Detection looks at the harness, MCP servers, hook directory, audit-log destinations, and any custom dispatch wrappers under `scripts/`. See [Assumptions](index.md#assumptions).

!!! info "Applicability"
    Skip pure-text agents (no tool actions to diverge from a record) and reversible-state systems where every action is rolled back on detection. Run when the agent has any write tool, sends messages, or is subject to compliance-driven audit retention. See [`action-audit-divergence-taxonomy`](../security/action-audit-divergence-taxonomy.md) §Where the Framing Backfires.

The runtime's load-bearing safety property is that the audit record matches what actually happened. [Metere (2026)](https://arxiv.org/abs/2605.01740) decomposes the failure space into four exhaustive divergence modes — gate-bypass (F1), audit-forgery (F2), silent host failure (F3), wrong-target (F4). The audit converts each mode into a closed question against the project's existing controls; an unanswered question is a finding ([`action-audit-divergence-taxonomy`](../security/action-audit-divergence-taxonomy.md), [`audit-record-divergence-invariant`](../security/audit-record-divergence-invariant.md)).

## Step 1 — Inventory the Action Surface

```bash
# Tool-call sites (harness + MCP)
SETTINGS=$(find . -path "*/.claude/settings.json" ! -path "*/.claude/worktrees/*")
MCP=$(find . -name ".mcp.json" -o -name "mcp.json" ! -path "*/node_modules/*")
HOOKS=$(find . -path "*/.claude/hooks/*" -type f ! -path "*/.claude/worktrees/*")

# Dispatch wrappers (subprocess shells, raw HTTP, custom routers)
WRAPPERS=$(grep -rlE "subprocess\.|requests\.|httpx\.|urllib|child_process|fetch\(|node-fetch|playwright" \
  scripts/ .claude/ 2>/dev/null)

# Audit destinations
AUDIT=$(grep -rlE "audit_log|opentelemetry|otel|datadog|loki|axiom|hash.chain|merkle" \
  scripts/ .claude/ docs/ 2>/dev/null | head -20)
```

Capture three lists: actuating sites (harness + MCP + wrappers), audit sinks, and any policy-evaluation chokepoints. The audit's quality hinges on completeness here — an undetected wrapper is an undetected F1 path.

## Step 2 — F1: Name the Chokepoint

F1 fires when an action runs without passing authorisation. Every actuating site enumerated in Step 1 must funnel through one policy-evaluation point. From [`action-audit-divergence-taxonomy`](../security/action-audit-divergence-taxonomy.md) §F1: "the LLM checks" is not a chokepoint — the LLM is what is being authorised.

```bash
# A chokepoint is concrete: a PreToolUse hook, an MCP control plane, a sidecar policy daemon
HOOK_PRETOOL=$(grep -lE '"PreToolUse"|hooks/pre.tool.use' .claude/settings.json 2>/dev/null)
CONTROL_PLANE=$(grep -rlE 'mcp.runtime.control.plane|policy.evaluator|policy_engine|opa.eval' \
  .claude/ scripts/ 2>/dev/null)

# Skipped-plane clients: subprocess shells, raw HTTP, headless browser bypass the chokepoint
for w in $WRAPPERS; do
  grep -qE "PreToolUse|policy.eval|control.plane|allowlist" "$w" \
    || echo "high|$w|actuates without passing the policy chokepoint|route through PreToolUse hook or MCP control plane"
done

[[ -z "$HOOK_PRETOOL$CONTROL_PLANE" ]] \
  && echo "high|.claude|no PreToolUse policy chokepoint|wire bootstrap-permissions-allowlist or bootstrap-mcp-config control plane"
```

Cross-reference with [`audit-permissions-blast-radius`](audit-permissions-blast-radius.md) and [`audit-mcp-control-plane-bypass`](audit-mcp-control-plane-bypass.md). If both have findings, F1 coverage is broken at the same spot.

## Step 3 — F2: Name the Integrity Mechanism

F2 fires when the audit record is mutated post-write to claim a different action ran. Append-only is not enough; the log must be tamper-evident under an attacker on the host. Hash chains, Merkle trees, or external receipt sinks close the gap ([`action-audit-divergence-taxonomy`](../security/action-audit-divergence-taxonomy.md) §F2).

```bash
# Look for chained-hash, signed-receipt, or external-sink semantics
INTEGRITY=$(grep -rlE 'hash.chain|merkle|prev_hash|sha256.*prev|ml.dsa|ed25519.*receipt|signed.audit' \
  scripts/ .claude/ docs/ 2>/dev/null)

# A bare append-only file or stdout JSONL is not tamper-evident
PLAIN_LOG=$(grep -rlE 'open\(.*audit.*[\"]a[\"]|>>.*\.log|append.*audit' scripts/ .claude/ 2>/dev/null)

[[ -z "$INTEGRITY" && -n "$PLAIN_LOG" ]] \
  && echo "high|$PLAIN_LOG|append-only log without tamper-evidence|chain hashes per entry or ship to an external receipt sink"

# Vendor-managed transcripts (Claude Code session logs) are not under the project's integrity control
grep -lE 'claude-code.*session.*log|transcript_path' .claude/settings.json 2>/dev/null \
  | awk '{print "medium|"$1"|relies on vendor-managed transcript for audit|document the retention contract or duplicate to a chained log"}'
```

Reference: [`cryptographic-governance-audit-trail`](../security/cryptographic-governance-audit-trail.md). If the project ships compliance evidence (EU AI Act, finance, healthcare), absence of integrity is `high`; for ephemeral per-PR agents it is `low`.

## Step 4 — F3: Name the Liveness Probe

F3 fires when the log records "action X ran" but the host did nothing — process crashed, swallowed error, container killed mid-call. The signal must come from outside the runtime ([`action-audit-divergence-taxonomy`](../security/action-audit-divergence-taxonomy.md) §F3).

```bash
# Detect "200 == ran" assumption: tool wrappers that log on entry but not on observed side effect
for w in $WRAPPERS; do
  ENTRY_LOG=$(grep -cE 'log.*before|audit.*request|pre.execution.log' "$w")
  EXIT_VERIFY=$(grep -cE 'verify|ack|side.effect|post.execution.probe|check.*landed' "$w")
  [[ $ENTRY_LOG -gt 0 && $EXIT_VERIFY -eq 0 ]] \
    && echo "medium|$w|logs request entry without side-effect verification|add a post-execution probe (file stat, downstream ack, telemetry confirmation)"
done

# Bootstrap seal: does the runtime fail closed on init mismatch?
SEAL=$(grep -rlE 'bootstrap.seal|fail.closed|integrity.check.*startup|module.signing' \
  scripts/ .claude/ 2>/dev/null)
[[ -z "$SEAL" ]] \
  && echo "medium|.claude|no bootstrap seal — silent partial-failure on init goes undetected|see fail-closed-remote-settings-enforcement"
```

For agents that mutate external state, F3 is the divergence with the lowest detection rate in practice — the call returned, the log says success, the side effect never landed. Reference: [`fail-closed-remote-settings-enforcement`](../security/fail-closed-remote-settings-enforcement.md), [`tool-signing-verification`](../security/tool-signing-verification.md).

## Step 5 — F4: Name the Target Validator

F4 fires when the action lands on the wrong target — log says `repo:foo`; commit pushed to `repo:bar`; log says `alice@`; mail went to `attacker@`. Validation must happen at the egress boundary, not at argument generation ([`action-audit-divergence-taxonomy`](../security/action-audit-divergence-taxonomy.md) §F4).

```bash
# Egress allowlist (host or recipient) external to LLM-generated arguments
EGRESS=$(find . -name ".claude/settings.json" -exec grep -lE 'web_fetch_allowlist|allowed_hosts|deny:' {} +)
URL_GUARD=$(grep -rlE 'url.exfiltration.guard|public.web.index|common.crawl.gate' \
  scripts/ .claude/ 2>/dev/null)

# Wrong-target risk concentrates on tools that emit to a target string
for tool in $(grep -rE 'tool.*(send_email|http_post|push|publish|write_file|webhook)' \
  .claude/ scripts/ 2>/dev/null | head -20); do
  echo "$tool" | grep -qE 'allowlist|validate.*target|recipient.check' \
    || echo "medium|$tool|target-emitting tool without target validator|add an allowlist or independent validator"
done

[[ -z "$EGRESS$URL_GUARD" ]] \
  && echo "high|.claude|no egress target validation independent of LLM arguments|wire bootstrap-egress-policy or bootstrap-url-fetch-gate"
```

Cross-reference with [`audit-lethal-trifecta`](audit-lethal-trifecta.md). A `(1,1,1)` principal with no F4 control is a top-finding regardless of other audit results.

## Step 6 — Per-Mode Scorecard

```markdown
# Audit Report — Action-Audit Divergence

| Mode | Question | Project answer | Pass/Fail | Top issue |
|------|----------|----------------|-----------|-----------|
| F1 Gate-bypass | Where does every tool call pass authorisation? | `<chokepoint>` | ✅ / ❌ | <one-line> |
| F2 Audit-forgery | What makes the log tamper-evident? | `<integrity mechanism>` | ✅ / ❌ | <one-line> |
| F3 Silent host failure | What confirms the action actually ran? | `<liveness probe>` | ✅ / ❌ | <one-line> |
| F4 Wrong-target | What validates the target independent of LLM arguments? | `<target validator>` | ✅ / ❌ | <one-line> |
```

A control may cover multiple modes (a hash-chained log with policy receipts covers F1 and F2). A mode may need multiple controls. The scorecard names the question each control answers; un-answered cells are findings.

## Step 7 — Findings Output

```markdown
| Severity | Mode | Surface | Finding | Suggested fix |
|----------|------|---------|---------|---------------|
```

Severity rule of thumb (from [`audit-record-divergence-invariant`](../security/audit-record-divergence-invariant.md) §Conditions of Applicability):

- `high` — long-running multi-user runtime, regulated environment, or `(1,1,1)` principal with the cell empty
- `medium` — vendor-managed coding agent with the cell partially answered (e.g., transcript exists but retention contract is undocumented)
- `low` — ephemeral per-PR agent without cross-run state; F2 / F3 partial misses degrade to advisory

## Idempotency

Read-only.

## Output Schema

```markdown
# Audit Action-Audit Divergence — <repo>

| Mode | Pass | Fail |
|------|:----:|:----:|
| F1 | <bool> | <bool> |
| F2 | <bool> | <bool> |
| F3 | <bool> | <bool> |
| F4 | <bool> | <bool> |

Top fix: <one-liner — usually F4 for agents with egress, F1 for agents with wrappers>
```

## Remediation

- F1 missing → [`bootstrap-permissions-allowlist`](bootstrap-permissions-allowlist.md), [`bootstrap-mcp-config`](bootstrap-mcp-config.md), [`audit-mcp-control-plane-bypass`](audit-mcp-control-plane-bypass.md)
- F2 missing → [`cryptographic-governance-audit-trail`](../security/cryptographic-governance-audit-trail.md); for vendor-managed runtimes, document retention with [`audit-debug-log-retention`](audit-debug-log-retention.md)
- F3 missing → [`tool-signing-verification`](../security/tool-signing-verification.md), [`fail-closed-remote-settings-enforcement`](../security/fail-closed-remote-settings-enforcement.md)
- F4 missing → [`bootstrap-egress-policy`](bootstrap-egress-policy.md), [`bootstrap-url-fetch-gate`](bootstrap-url-fetch-gate.md), [`audit-lethal-trifecta`](audit-lethal-trifecta.md)

## Related

- [Action-Audit Divergence Taxonomy](../security/action-audit-divergence-taxonomy.md) — the F1-F4 framing this runbook walks
- [Audit-Record Divergence as an Agent Runtime Invariant](../security/audit-record-divergence-invariant.md) — the seven detection primitives and applicability conditions
- [Cryptographic Governance Audit Trail](../security/cryptographic-governance-audit-trail.md) — F2 control implementation
- [Audit MCP Control Plane Bypass](audit-mcp-control-plane-bypass.md) — sibling audit covering off-protocol egress
- [Audit Lethal Trifecta](audit-lethal-trifecta.md) — sibling audit; F4 concentrates on `(1,1,1)` principals
- [Defense-in-Depth Agent Safety](../security/defense-in-depth-agent-safety.md)
