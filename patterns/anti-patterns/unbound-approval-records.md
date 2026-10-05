---
title: "Approval Records That Bind No Identity and No Session"
term: "Unbound Approval Record"
description: "A stored allow rule names a command, not who may run it. On Claude Code a subagent exercised the main session's grant in 18 of 19 runs, a seeded rule in 20 of 20."
tags:
  - anti-pattern
  - security
  - tool-agnostic
  - arxiv
aliases:
  - unbound approval record
  - delegation laundering
  - temporal laundering
last_reviewed: 2026-10-01
maturity: emerging
---

# Approval Records That Bind No Identity and No Session

> A stored allow rule fixes the command text and records nothing about who may run it or for how long.

An unbound approval record is a persisted permission entry that pins a command pattern while leaving the acting agent and the session unrecorded, so any principal in any later run satisfies it. One study instrumented Claude Code's `PreToolUse` mediation point and measured each class separately.

A subagent exercised the main session's grant in 18 of 19 valid runs. A rule pre-written into `settings.json` to stand in for an earlier session's decision drew no fresh confirmation in all 20 ([arXiv 2609.38983v1, Table III](https://arxiv.org/abs/2609.38983v1)). Replaying those same runs through a credential that also binds the agent and the session took both figures to zero.

## Bind the two fields when three things hold

The repair is a field comparison at the mediation point, and it earns its cost under three conditions.

- A per-call checkpoint exists. On Codex CLI the author registered a documented `preToolUse` hook, confirmed the harness parsed it, and the subprocess never ran: `codex exec` "appears to expose no observable per-call approval checkpoint at all" ([arXiv 2609.38983v1, §IX](https://arxiv.org/abs/2609.38983v1)). With no checkpoint there is no field to compare.
- Fan-out is small enough to absorb hard denials. The bound credential denied every laundered cross-agent and cross-session call in the study ([arXiv 2609.38983v1, Table V](https://arxiv.org/abs/2609.38983v1)), and the author did not test whether it can admit a legitimate one ([arXiv 2609.38983v1, §IX](https://arxiv.org/abs/2609.38983v1)). Every delegation and every new session meets that denial until you build an admission path.
- What worries you is an unapproved principal rather than an approved command's side effects. The same credential left scope laundering at 1.000 and moved argument laundering from 0.450 to 0.400, with p=1 for both ([arXiv 2609.38983v1, Table V](https://arxiv.org/abs/2609.38983v1)).

## Why it works

A permission rule is a predicate over the command text and the declared tool name, and neither input separates a subagent from the main thread or one session from the next. The paper puts it as a property of the credential itself: one lacking agent and session fields "is recomputed identically whether the call is dispatched by the main session or by a subagent acting under a different identity, since none of its fields distinguish them" ([arXiv 2609.38983v1, §III-A](https://arxiv.org/abs/2609.38983v1)). A persisted grant has no stale value to catch either, because Claude Code's "always allow" rules carry no session identifier of their own ([arXiv 2609.38983v1, §III-B](https://arxiv.org/abs/2609.38983v1)).

The fields are present where the check would run. Claude Code hands a `PreToolUse` hook an `agent_id`, documented as "Present only when the hook fires inside a subagent call. Use this to distinguish subagent hook calls from main-thread calls" ([Claude Code hooks](https://code.claude.com/docs/en/hooks)). Comparing them worked. In paired replay of the recorded runs, delegation fell from 0.947 to 0.000 (p = 7.6e-6) and the seeded session mismatch from 1.000 to 0.000 (p = 1.9e-6) ([arXiv 2609.38983v1, Table V](https://arxiv.org/abs/2609.38983v1)).

The guard also denied three live runs of each class. In every live delegation run it gave the same reason: no "matching unexpired Approval Token exists for this exact principal/agent/session/tool/scope combination" ([arXiv 2609.38983v1, §VII](https://arxiv.org/abs/2609.38983v1)).

## When this backfires

- Nobody tested the call that should pass. "None of the six sessions went on to complete its stated task after the denial", and whether the field set admits a legitimate cross-session or cross-delegation call while refusing a laundered one is something the author says "we did not test" ([arXiv 2609.38983v1, §IX](https://arxiv.org/abs/2609.38983v1)). A control measured only against the attack is half measured.
- Prompt volume returns. Standing grants exist because repeated prompts stop being read: "Manual prompts sit in the middle, and in practice users accept 93% of them anyway" ([Anthropic: Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)). A session-bound grant is also denied in every new session, so the work that standing grants were meant to unblock stops instead.
- The session result is seeded rather than captured. The baseline writes the rule into `settings.json` to simulate a persisted decision, and no grant made in one real session was replayed in a second real one ([arXiv 2609.38983v1, §V-A](https://arxiv.org/abs/2609.38983v1)).
- Command-text gaps need a lower layer, not a richer credential. Claude Code's documentation says a Bash rule "doesn't match the same program invoked in a different form, so a deny or ask rule covers the invocation Claude usually produces and isn't a security boundary around the program", and prescribes sandboxing for enforcement that "doesn't depend on the command text" ([Claude Code permissions](https://code.claude.com/docs/en/permissions)). That axis belongs to [parser-versus-shell evasion](../../security/parser-versus-shell-permission-evasion.md).
- The evidence base is thin: "All results in this section are for a single harness (Claude Code) under a single, fixed model" ([arXiv 2609.38983v1, §V-B](https://arxiv.org/abs/2609.38983v1)), in a v1 preprint with one author.

## Example

**Before — a grant any agent in any session satisfies:**

```json
{ "permissions": { "allow": ["Bash(npm run test *)"] } }
```

The fields a `PreToolUse` hook sees on the same call:

```json
{
  "session_id": "abc123",
  "tool_name": "Bash",
  "tool_input": { "command": "npm run test" },
  "agent_id": "agent_01..."
}
```

The hook receives that object on stdin, so it can refuse a call whose `session_id` or `agent_id` differs from the one the grant was issued under ([Claude Code hooks](https://code.claude.com/docs/en/hooks)).

## Key Takeaways

- Check which fields your approval store actually holds. A rule with no agent and no session reports no mismatch because it has no field to mismatch.
- The two identity fields are the cheap half of this problem, and the only half a check at the tool-call boundary can reach.
- Decide how a valid call gets admitted before you add the comparison. The study never tested a bound credential admitting a call it should admit.
- A session-bound grant denies a call from any other session by design, so plan for the denial.

## Related

- [Agent Approval Laundering: Effects Beyond the Named Command](../../security/approval-laundering-transitive-effects.md) — the other half of the same gap, where the record names the right command and misses what its workflow reaches
- [Parser-Versus-Shell Evasion in Command Permission Checks](../../security/parser-versus-shell-permission-evasion.md) — the command-text axis, where the checker and the shell disagree about what a string means
- [Per-Agent Capability Stores Beat One Task-Wide Allowlist](../../security/per-agent-capability-scoping.md) — the containment answer to subagent authority, measured against prompt injection rather than approval reuse
- [Scoped-Looking Permission Grants](scoped-looking-permission-grants.md) — a rule that names one runner and permits every command, the same credential read too generously
- [Non-Retirable Approval Rules for Agent Operations](../../security/non-retirable-approval-rules.md) — the administrator-side control that refuses to let any saved grant satisfy an operation
