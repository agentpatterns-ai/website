---
title: "bypassPermissions Silently Overrides allowedTools (The Restricted-Bypass Trap)"
description: "Pairing allowedTools with permissionMode bypassPermissions does not restrict the agent — the allow list is a no-op below the bypass step, so every tool runs without prompts."
tags:
  - anti-pattern
  - security
  - tool-agnostic
aliases:
  - restricted bypass trap
  - bypassPermissions plus allowedTools
  - allowedTools does not constrain bypass
last_reviewed: 2026-05-30
---

# bypassPermissions Silently Overrides allowedTools (The Restricted-Bypass Trap)

> Pairing `allowedTools` with `permissionMode: "bypassPermissions"` does not restrict the agent — the allow list is a no-op below the bypass step.

The intuitive composition — *allowlist plus bypass-prompts equals locked-down-no-prompts* — produces the most-permissive runtime instead. `allowedTools` adds *allow rules* that pre-approve listed tools; it is not a closed set. Unlisted tools fall through to the permission mode, and `bypassPermissions` approves them. Anthropic ships an explicit Warning on this exact composition in the agent SDK permissions docs: *"Setting `allowed_tools=['Read']` alongside `permission_mode='bypassPermissions'` still approves every tool, including `Bash`, `Write`, and `Edit`."* ([Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions)).

## The Anti-Pattern

A team wants the agent to read a repo and report findings, with no approval prompts in CI. They write:

```typescript
const options = {
  allowedTools: ["Read", "Grep", "Glob"],
  permissionMode: "bypassPermissions"
};
```

Their mental model: *"Read, Grep, Glob are pre-approved; bypassPermissions means no prompts; therefore the agent can only run those three tools."* The runtime behaviour: every tool — `Bash`, `Write`, `Edit`, `WebFetch`, every MCP server tool — runs without prompts. The allow list is decorative.

The same shape appears in `claude` CLI flags: `claude -p "..." --allowedTools Read --permission-mode bypassPermissions` executes `Bash` without prompting. Repro filed as [anthropics/claude-code#12232](https://github.com/anthropics/claude-code/issues/12232) and closed as not planned — the composition is intended behaviour, not a bug.

## Why It Works (the documented evaluation order)

The permission pipeline is a 5-step ordered flow ([Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions)):

1. **Hooks** — custom code can allow, deny, or pass
2. **Deny rules** — `disallowedTools` and `settings.json` deny entries; matches block in every mode, *including* `bypassPermissions`
3. **Permission mode** — `bypassPermissions` approves; `acceptEdits` approves file ops; `dontAsk` denies; others fall through
4. **Allow rules** — `allowedTools` and `settings.json` allow entries; matches approve
5. **`canUseTool` callback** — interactive approval (skipped under `dontAsk`)

`bypassPermissions` resolves the call at step 3; the allow check at step 4 never runs. `disallowedTools` works under bypass because deny rules sit at step 2, *above* the permission mode. The trap is in the intuition that allow lists are exhaustive — they are not.

## When This Backfires (the conditions that make it dangerous)

The misconfiguration is silently permissive in exactly the contexts where operators reach for it:

- **Headless CI under bypass** — a workflow that wants "don't prompt me, but limit to these tools" gives the agent every tool. If injected content reaches the agent ([External Artifacts as Data](external-artifacts-as-data.md)), every write tool is available with no consent event.
- **Sub-agent dispatch under inherited bypass** — *"When the parent uses `bypassPermissions`, `acceptEdits`, or `auto`, all subagents inherit that mode and it cannot be overridden per subagent"* ([Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions)). Sub-agents with looser system prompts (third-party agents, plugins, skills) gain full system access; the request to add a `subagentPermissionMode` override was [closed as not planned](https://github.com/anthropics/claude-code/issues/20264).
- **MCP server addition under bypass+allowlist** — a newly wired MCP server's tools fall through to bypass automatically. The operator who believed the allow list restricted to `Read` does not realise the new write tools are auto-approved.
- **Security review of `allowedTools` alone** — a reviewer reads the allow list, certifies the configuration as restrictive, and misses the `permissionMode` interaction. The composition passes review and ships permissive.
- **Cross-tool intuition transfer** — Codex CLI, Cursor, and other harnesses expose analogous allow/deny/mode tri-axes with different default precedences. An operator who internalises one tool's rule order misreads another's.

The composition is *correct* only when the environment itself is the boundary — a hermetic sandbox, ephemeral VM, or throwaway container where every tool running is acceptable by construction. In that case, the allow list is redundant rather than misleading. See [Permission Framework Choice Outweighs Model Choice](../security/permission-framework-over-model.md) for the broader framework-vs-model trade-off and [Blast Radius Containment](../security/blast-radius-containment.md) for the deterministic-allowlist alternative.

## The Two Correct Shapes

The docs name them explicitly:

| Goal | Shape | Why |
|------|-------|-----|
| Restrict to a small set, never prompt | `permissionMode: "dontAsk"` + `allowedTools: [...]` | Deny-by-default: listed tools approve at step 4; unlisted tools fall through to step 5 where `dontAsk` denies. *"For a locked-down agent, pair `allowedTools` with `permissionMode: 'dontAsk'`. Listed tools are approved; anything else is denied outright."* ([Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions)) |
| Trust broadly, block a few | `permissionMode: "bypassPermissions"` + `disallowedTools: [...]` | Allow-by-default with named denies. Bare `disallowedTools: ["Bash"]` removes `Bash` from the tool catalogue entirely; `disallowedTools: ["Bash(rm *)"]` blocks scoped patterns at step 2, above the bypass step |

Anthropic's own preference for "background safety checks without prompts" is neither of these — it is `permissionMode: "auto"`, a classifier-gated mode that approves or denies each call ([How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)). See [Classifier-Gated Auto Permission](../agent-design/classifier-gated-auto-permission.md).

## Example

**Before — restricted-bypass trap (intent: read-only CI; reality: unrestricted):**

```typescript
// Intent: "Read-only audit, no prompts in CI"
const options = {
  allowedTools: ["Read", "Grep", "Glob"],
  permissionMode: "bypassPermissions"
};
```

At evaluation step 3, `bypassPermissions` approves the call. Step 4 — where `allowedTools` would match — never runs. A `Bash(rm -rf node_modules)` call from the agent or from an injected instruction in a fetched document runs without prompts. The allow list is decorative.

**After — deny-by-default, no prompts (matches the original intent):**

```typescript
// Listed tools approve at step 4; unlisted tools deny at step 5
const options = {
  allowedTools: ["Read", "Grep", "Glob"],
  permissionMode: "dontAsk"
};
```

A `Bash` call is not pre-approved at step 4 and is denied at step 5. The agent runs read-only without prompts, matching the operator's intent. This is the shape the docs prescribe for "locked-down" agents.

**Alternative — keep bypass, block writes explicitly:**

```typescript
// Bare names remove tools from the catalogue; scoped patterns block at step 2
const options = {
  permissionMode: "bypassPermissions",
  disallowedTools: ["Bash", "Write", "Edit", "MultiEdit"]
};
```

`Bash`, `Write`, `Edit`, and `MultiEdit` are removed from the tool catalogue before evaluation begins. Bypass approves whatever remains. This shape suits "trust the agent broadly, deny a small named set" — a different intent from deny-by-default.

## Key Takeaways

- `allowedTools` is an additive pre-approval, not a closed set; unlisted tools fall through to the permission mode ([Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions)).
- The documented 5-step evaluation order places `bypassPermissions` (step 3) above allow rules (step 4); bypass resolves the call before the allow check runs.
- `disallowedTools` works under bypass because deny rules (step 2) evaluate above the mode; this is the correct shape for "bypass but block named tools."
- For "restrict to a small set + never prompt," pair `allowedTools` with `permissionMode: "dontAsk"` — the explicit shape named in the docs.
- The trap compounds at the sub-agent boundary: parent bypass is inherited and cannot be overridden per sub-agent ([Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions); [#20264](https://github.com/anthropics/claude-code/issues/20264)).

## Related

- [Permission Framework Choice Outweighs Model Choice](../security/permission-framework-over-model.md) — the broader finding that framework type drives overeager-action rates more than model choice
- [Blast Radius Containment: Least Privilege for AI Agents](../security/blast-radius-containment.md) — deterministic narrow allowlist as the structural alternative
- [Skill disallowed-tools Frontmatter](../tools/claude/skill-disallowed-tools.md) — the deny-side complement to allow-lists at the skill layer
- [Prompt-Only Tool Access Control](prompt-only-tool-access-control.md) — same shape one layer up: instructions cannot enforce a closed set either
- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — why the restricted-bypass trap is dangerous in the first place
