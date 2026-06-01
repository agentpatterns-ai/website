---
title: "Most-Restrictive-Wins Fusion for Parallel Agent Control Returns"
description: "The deny > defer > ask > allow merge function that fuses parallel hook decisions, classifier verdicts, and permission rules into a single agent-control answer."
tags:
  - agent-design
  - tool-agnostic
aliases:
  - most-restrictive-wins
  - deny-overrides hook merge
  - parallel hook decision precedence
last_reviewed: 2026-05-30
---

# Most-Restrictive-Wins Fusion for Parallel Agent Control Returns

> Fuse parallel agent-control returns by picking the strongest restriction (`deny > defer > ask > allow`) so a single deny anywhere blocks the call.

Most-restrictive-wins is the merge function for parallel agent-control decisions. When several `PreToolUse` hooks, a permission classifier, and rules from multiple settings scopes evaluate the same tool call concurrently, the harness fuses their answers by picking the strongest restriction across the set. The Claude Agent SDK documents the ordering explicitly: *"When multiple hooks or permission rules apply, **deny** takes priority over **defer**, which takes priority over **ask**, which takes priority over **allow**. If any hook returns `deny`, the operation is blocked regardless of other hooks."* ([SDK hooks reference](https://code.claude.com/docs/en/agent-sdk/hooks#outputs))

The teaching here is the merge — not the hooks, the classifiers, or the settings layers that produce the inputs to it. The merge is what lets each input be authored independently.

## The Ladder

| Decision | Meaning | Slot |
|---|---|---|
| `deny` | Block the call. No retry path. | Strongest — wins over everything |
| `defer` | Pause the session for out-of-band approval, then resume. | Beats `ask` and `allow` |
| `ask` | Surface an interactive prompt to the developer. | Beats `allow` only |
| `allow` | Proceed without modification. | Weakest — loses to every other value |

`defer` is a first-class state distinct from `ask` and `allow` — it ends the headless query so the caller can collect approval through its own UI, then resumes via `--resume` (see [Deferred Permission Pattern](deferred-permission-pattern.md) for the headless-pause mechanics). The merge slots it between `deny` and `ask` because pausing is a stronger restriction than prompting, but not as strong as a hard block.

## How the Merge Composes

Three properties make the function work, and dropping any one of them silently breaks it.

**Parallel evaluation.** The SDK fires every matching hook concurrently: *"When an event fires, all matching hooks run in parallel. For permission decisions, the most restrictive result wins: a single `deny` blocks the tool call regardless of what the other hooks return."* ([SDK — Register multiple hooks](https://code.claude.com/docs/en/agent-sdk/hooks#register-multiple-hooks)) Hooks are deduplicated by command string or URL before dispatch ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)) so identical handlers fire once.

**Author-time independence.** Because completion order is non-deterministic, the SDK requires each hook to act independently rather than rely on another hook running first. An authorization check, an input validator, and an audit logger registered against the same `PreToolUse` event each return their own verdict; the harness merges them. No hook needs to know its siblings exist.

**Reason-string discipline.** When a single deny in a parallel set blocks the call, debugging which hook denied collapses into log archaeology unless every hook attaches `permissionDecisionReason` to its return. The SDK surfaces the field for exactly this purpose — populate it on every non-`allow` return.

## The Same Merge Beyond Hooks

The function generalises wherever an agent has multiple parallel decision sources for one action:

- **Settings-scope rules.** Managed-policy, project, and user rules all evaluate against a tool call. The most restrictive wins, and managed settings additionally win at the disable-layer — `disableAllHooks` set in user or project settings cannot turn off managed hooks ([hooks reference](https://code.claude.com/docs/en/hooks)).
- **Classifier verdicts.** When a [classifier-gated auto-permission](classifier-gated-auto-permission.md) inspector returns alongside PreToolUse hooks, its verdict is one more input to the same merge. The classifier becomes a parallel `ask` or `deny` source; the merge picks the strongest.
- **Plugin and project hooks.** A vetted plugin hook that requires approval composes with a project hook that auto-allows the same tool — the plugin's `ask` wins over the project's `allow` without either side knowing about the other.

## Why It Works

The merge is correct because the underlying decision is binary (proceed or don't) and the harm is asymmetric — a wrongful proceed exfiltrates a secret or runs a destructive shell; a wrongful block costs a re-prompt. Under asymmetric harm, picking the strongest restriction across parallel evaluators is the minimax-regret strategy: it minimises the worst-case outcome regardless of which evaluator is wrong. This is the same argument [XACML's `deny-overrides` combining algorithm](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html) rests on — *"if a single Rule or Policy element is encountered that evaluates to Deny, then, regardless of the evaluation result of the other Rule or Policy elements in the applicable policy, the combined result is Deny"* — and the same one [AWS IAM policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html) follows: explicit deny in any policy overrides any allow. The pattern is decades-validated outside agent harnesses, and the SDK adopts it for the same reason those engines did.

The independence property the SDK requires flows directly from this: because the merge does not depend on evaluation order, each hook author can reason locally. The merge function is what permits the parallel execution model in the first place.

## When This Backfires

**Hooks that side-effect between siblings.** Most-restrictive-wins only composes when each evaluator is pure with respect to ordering. If an audit logger mutates state on every call and a downstream deny fires, the side effect already happened even though the operation was blocked. Hooks that need to commit state belong in `PostToolUse`, not `PreToolUse`.

**Buggy or chronically wrong deny.** One rogue deny in a parallel set blocks the agent indefinitely. Without per-hook `permissionDecisionReason` strings, identifying which of six hooks denied turns into log archaeology. The merge tolerates one bad evaluator only when reason attribution is disciplined.

**Asymmetric tools where allow-wins is the right model.** Coding-agent harnesses default to `deny-overrides` because of harm asymmetry, but XACML defines `permit-overrides` as the alternative combining algorithm precisely because some resource classes invert the asymmetry. Read-only retrieval against several curated sources, where each source independently certifies "this content is safe", may model better as allow-wins. Forcing most-restrictive across the board ignores that the combining algorithm is a choice per resource class. The fact that the Claude SDK exposes only `deny-overrides` is a design decision, not a logical necessity ([XACML 3.0 spec](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html)).

**Settings-scope confusion masking the merge.** Developers expect their project rule to win over a managed-org rule and get surprised when the managed deny overrides it. Most-restrictive-wins composes with the managed-overrides-everything settings hierarchy in non-obvious ways — the merge picks the strongest decision *across* scopes, and managed additionally wins on the meta-question of which hooks can fire at all.

**Inflexibility critique acknowledged.** The cost of the pattern is real: once an explicit deny is in place, no allow elsewhere overrides it ([Datadog: least-privilege IAM](https://www.datadoghq.com/blog/iam-least-privilege/)). For coding agents this is the desired property — break-glass exceptions belong on a managed-settings update path, not on a per-call allow elsewhere — but call the trade-off out explicitly when documenting the harness for new authors.

**Indeterminate handling is unspecified.** XACML deny-overrides stops on `Indeterminate`; the SDK is silent on what happens if a hook errors mid-evaluation. Treat a thrown exception inside a hook as an unhandled state until the contract is clarified — wrap each hook body in error handling that returns a deterministic value rather than letting the harness decide for you.

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

If `authorization_check` returns `deny`, the call is blocked regardless of what `input_validator` and `audit_logger` say. If `authorization_check` returns `allow` and `input_validator` returns `ask`, the developer sees a prompt. If all three return `allow`, the call proceeds. The audit logger contributes a side effect every time the hook fires, which is safe only because nothing downstream depends on the side effect's ordering relative to siblings. ([Example adapted from the SDK docs](https://code.claude.com/docs/en/agent-sdk/hooks#register-multiple-hooks))

## Key Takeaways

- The ladder is `deny > defer > ask > allow`. A single deny anywhere in a parallel set blocks the call.
- Parallel execution plus author-time independence plus reason-string discipline are the three properties that make the merge compose; dropping any one breaks it silently.
- The merge is the minimax-regret choice under asymmetric harm — the same argument XACML, AWS IAM, Azure Policy, and Istio all settle on.
- The function generalises beyond `PreToolUse` hooks: settings-scope rules, classifier verdicts, plugin hooks, and managed-policy decisions all feed the same merge.
- `permit-overrides` (allow-wins) is a legitimate alternative for resource classes with inverted harm asymmetry — coding agents default to deny-overrides because the asymmetry runs the other way.

## Related

- [Deferred Permission Pattern](deferred-permission-pattern.md) — The `defer` slot in the merge; explains how a headless session pauses and resumes when a hook returns the second-strongest verdict.
- [Classifier-Gated Auto-Permission for Cloud-IDE Coding Agents](classifier-gated-auto-permission.md) — A classifier becomes one more parallel return into the same merge function.
- [Tool Confirmation Carousel: Batched UI for Per-Call Approvals](tool-confirmation-carousel.md) — How the `ask` rung renders when multiple approvals queue up.
- [Permission Framework Over Model](../security/permission-framework-over-model.md) — Why the framework owns the merge function rather than the model.
- [Agent Runtime Middleware: Per-Call Interception Pipeline](agent-runtime-middleware.md) — Composing cross-cutting concerns around model and tool calls — the middleware layer parallel-hook authors plug into.
