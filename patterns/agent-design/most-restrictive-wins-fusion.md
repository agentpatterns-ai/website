---
title: "Most-Restrictive-Wins Fusion for Parallel Agent Control Returns"
term: "Most-Restrictive-Wins Fusion"
description: "The deny > defer > ask > allow merge function that fuses parallel hook decisions, classifier verdicts, and permission rules into a single agent-control answer."
tags:
  - agent-design
  - tool-agnostic
  - security
aliases:
  - most-restrictive-wins
  - deny-overrides hook merge
  - parallel hook decision precedence
last_reviewed: 2026-08-30
maturity: established
---

# Most-Restrictive-Wins Fusion for Parallel Agent Control Returns

> Fuse parallel agent-control returns by picking the strongest restriction (`deny > defer > ask > allow`) so a single deny anywhere blocks the call.

Most-restrictive-wins is the merge function for parallel agent-control decisions. Several `PreToolUse` hooks, a permission classifier, and settings-scope rules can evaluate one tool call at once. The harness picks the strongest restriction across the set. The Claude Agent SDK documents the ordering explicitly: *"When multiple hooks or permission rules apply, **deny** takes priority over **defer**, which takes priority over **ask**, which takes priority over **allow**. If any hook returns `deny`, the operation is blocked regardless of other hooks."* ([SDK hooks reference](https://code.claude.com/docs/en/agent-sdk/hooks#outputs))

The teaching is the merge itself: it lets each input be authored independently.

## The ladder

| Decision | Meaning | Slot |
|---|---|---|
| `deny` | Block the call. No retry path. | Strongest — wins over everything |
| `defer` | Pause the session for out-of-band approval, then resume. | Beats `ask` and `allow` |
| `ask` | Surface an interactive prompt to the developer. | Beats `allow` only |
| `allow` | Proceed without modification. | Weakest — loses to every other value |

`defer` is a first-class state, distinct from `ask` and `allow`. It ends the headless query for out-of-band approval, then resumes via `--resume` (see the [deferred permission pattern](deferred-permission-pattern.md)). The merge slots it between `deny` and `ask`: pausing is stronger than prompting, but weaker than a hard block.

## How the merge composes

Three properties make the function work. Drop any one and it breaks silently.

- parallel evaluation: hooks fire concurrently: *"When an event fires, all matching hooks run in parallel. For permission decisions, the most restrictive result applies: a single `deny` blocks the tool call regardless of what the other hooks return."* ([SDK — Register multiple hooks](https://code.claude.com/docs/en/agent-sdk/hooks#register-multiple-hooks)) The same handler defined more than once runs only once; a plugin's or skill's copy stays separate ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks))
- author-time independence: completion order is non-deterministic, so each hook acts alone. An authorization check, an input validator, and an audit logger on the same event each return their own verdict
- reason-string discipline: when a deny blocks the call, finding which hook denied collapses into log archaeology unless every hook attaches `permissionDecisionReason` to its return

## The same merge beyond hooks

Most-restrictive-wins generalizes wherever an agent has several parallel decision sources for one action:

- settings-scope rules: managed-policy, project, and user rules all evaluate a tool call, and the most restrictive wins. Managed settings also win at the disable layer — `disableAllHooks` cannot turn off managed hooks ([hooks reference](https://code.claude.com/docs/en/hooks))
- classifier verdicts: a [classifier-gated auto-permission](classifier-gated-auto-permission.md) inspector is one more input to the same merge — a parallel `ask` or `deny` source
- plugin and project hooks: a plugin hook that requires approval composes with a project hook that auto-allows the same tool, and the plugin's `ask` wins

## Why it works

The merge is correct because the underlying decision is binary (proceed or don't) and the harm is asymmetric. A wrongful proceed exfiltrates a secret or runs a destructive shell; a wrongful block costs a re-prompt. Picking the strongest restriction minimizes the worst-case outcome regardless of which evaluator is wrong — the minimax-regret strategy. [XACML's `deny-overrides` combining algorithm](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html) rests on the same argument: *"if a single Rule or Policy element is encountered that evaluates to Deny, then, regardless of the evaluation result of the other Rule or Policy elements in the applicable policy, the combined result is Deny."* [AWS IAM policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html) follows the same logic: explicit deny in any policy overrides any allow.

## When this backfires

- hooks that side-effect between siblings: a downstream deny can't undo a side effect an earlier hook already committed. Keep side-effecting logic in `PostToolUse`, not `PreToolUse`
- a chronically wrong deny: one bad hook blocks the agent indefinitely. Without `permissionDecisionReason` on every hook, finding which of six denied means reading each hook's own logs
- allow-wins fits some tools better: coding agents default to `deny-overrides`, but XACML's `permit-overrides` suits resource classes with inverted harm asymmetry ([XACML 3.0 spec](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html)); the SDK exposes only `deny-overrides`
- settings-scope confusion: a project rule that should beat a managed-org rule instead loses to it, because managed settings also gate which hooks can fire
- inflexible by design: once a deny is in place, no allow elsewhere overrides it ([Datadog: least-privilege IAM](https://www.datadoghq.com/blog/iam-least-privilege/)) — the property coding agents want, but say so for new authors
- indeterminate handling is unspecified: XACML stops on `Indeterminate`; the SDK is silent on a hook that errors mid-evaluation. Treat a thrown exception as unhandled

## Example

Three independent `PreToolUse` hooks against the same event — the merge fuses them in parallel without any one knowing about the others:

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[authorization_check]),  # may return deny
            HookMatcher(hooks=[input_validator]),      # may return ask
            HookMatcher(hooks=[audit_logger]),         # always returns allow + side effect
        ]
    }
)
```

The merge resolves the three hooks' verdicts in ladder order:

- `authorization_check` returns `deny`: the call is blocked regardless of what `input_validator` and `audit_logger` say
- `authorization_check` returns `allow` and `input_validator` returns `ask`: the developer sees a prompt
- all three return `allow`: the call proceeds

The audit logger contributes a side effect every time it fires, which is safe only because nothing downstream depends on its ordering relative to siblings. ([Example adapted from the SDK docs](https://code.claude.com/docs/en/agent-sdk/hooks#register-multiple-hooks))

## Key Takeaways

- Check `permissionDecisionReason` first when a call gets blocked unexpectedly — the ladder means one hook, classifier, or settings rule can deny with no other signal in the transcript.
- Drop any of the three composing properties and the failure is silent: an audit logger that mutates state before a deny still leaves the side effect behind, and a missing reason string turns a wrongful block into a guessing game.
- The merge is the minimax-regret choice under asymmetric harm — the same argument XACML's and AWS IAM's deny-overrides logic both rest on.
- Before building a custom conflict-resolution scheme across hooks, classifiers, and settings scopes, check whether most-restrictive-wins already covers the case — it generalizes to any set of parallel decision sources for one action.
- Reach for `permit-overrides` (allow-wins) only when a resource class inverts the harm asymmetry, such as read-only retrieval from sources that self-certify as safe — not as a general substitute for deny-overrides.

## Related

- [Deferred Permission Pattern](deferred-permission-pattern.md) — The `defer` slot in the merge; explains how a headless session pauses and resumes when a hook returns the second-strongest verdict.
- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](classifier-gated-auto-permission.md) — A classifier becomes one more parallel return into the same merge function.
- [Tool Confirmation Carousel: Batched UI for Per-Call Approvals](tool-confirmation-carousel.md) — How the `ask` rung renders when multiple approvals queue up.
- [Permission Framework Over Model](../../security/permission-framework-over-model.md) — Why the framework owns the merge function rather than the model.
- [Agent Runtime Middleware: Per-Call Interception Pipeline](agent-runtime-middleware.md) — Composing cross-cutting concerns around model and tool calls — the middleware layer parallel-hook authors plug into.
- [Team-Scoped Agent Policy Delegation](../../security/team-scoped-policy-delegation.md) — A managed-settings layer that merges across a user's teams least-restrictive, inverting this ladder.
