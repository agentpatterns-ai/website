---
title: "Non-Retirable Approval Rules for Agent Operations"
term: "Non-Retirable Approval Rule"
description: "An admin-set ask rule re-prompts on every occurrence and no bypass mode, auto-approval, hook, or saved grant satisfies it. The permission state local agent config cannot express, and what it costs."
tags:
  - security
  - agent-design
  - copilot
aliases:
  - managed ask rule
  - permissions.ask
  - un-retirable approval
last_reviewed: 2026-09-10
maturity: emerging
---

# Non-Retirable Approval Rules for Agent Operations

> A managed ask rule accepts no bypass mode, auto-approval, hook, or saved grant, so the same operation prompts for approval every time.

A non-retirable approval rule is an administrator-set permission that demands fresh human approval each time an operation is requested and that no accumulated local grant satisfies. GitHub shipped one for Copilot on 9 September 2026 as the `permissions.ask` key in enterprise managed settings. Managed permissions there "cover shell commands, file reads and edits, and network domains" ([GitHub Changelog](https://github.blog/changelog/2026-09-09-enterprise-managed-permissions-for-github-copilot-agent-operations)). A local permission system treats an approval as a fact it can store, the assumption an [allowlist mined from past sessions](transcript-driven-permission-allowlist.md) runs on. This state makes the store non-authoritative.

## When it is worth pinning an operation to ask

The control converts an authorization problem into an attention budget, and earns its place under three conditions.

- The operation fires rarely. A prompt on something a developer does dozens of times a day produces reflex approvals, not decisions.
- An interactive approver is present. Headless, scheduled, and cloud-agent runs have nobody to prompt, so the prompt is a hang.
- Someone has audited the blast radius of the first rule, which changes the default for everything you did not name.

Where a condition fails, pin the operation to `deny` or leave it alone. Nobody habituates to a denial.

## Three states and one precedence order

The keys "use deny > ask > allow precedence" ([GitHub Docs](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)).

| Key | What it does | How it composes across sources |
|---|---|---|
| `deny` | Blocks the operation whatever else matches it | Union. A deny from any source "blocks the operation for all users" |
| `ask` | Demands fresh, one-time approval "even if the operation would otherwise be allowed" | Not satisfiable by bypass mode, auto-approval, a hook, or an earlier grant |
| `allow` | Lets the operation run with no prompt | Intersection, "not the union" |

Read the `allow` row twice. A central allow list narrows a developer's rather than extending it, so it is a ceiling. Rules select operations with `Shell(...)`, `Read(...)`, `Edit(...)`, and `Domain(...)`, where `Bash(...)` aliases `Shell(...)` and `Write(...)` aliases `Edit(...)`.

The trap is the default. "If an MDM-managed, server-managed, or file-based source defines any permission rule ... an unmatched supported operation defaults to requiring approval" ([GitHub Docs](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)). A short deny list therefore gates the whole supported tool surface. The prompts a policy generates come mostly from the operations nobody wrote down.

## Why it works

A stored approval outlives the reasoning that produced it. The judgement was made once, against one command, in one context, and every later reuse inherits a decision nobody re-made. A managed ask rule takes that state out of the trust chain by name: it "can't be satisfied by bypass mode (also known as allow-all or YOLO mode), an auto-approval setting, a hook or other approval shortcut, or a grant persisted from an earlier approval", and "the same operation prompts again the next time it's requested" ([GitHub Docs](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)). Authorization re-binds to the occurrence instead of to a remembered rule, so the check runs in the context where the effect lands. Enumerating the escape hatches by name is what makes it [an enforced control](enforced-versus-advisory-controls.md) rather than a default.

## When this backfires

The dominant failure is not a bypassed policy. It is a habituated one. Across 400 repeat reviewers and 11,429 reviews of agent-authored code, approval rates rose "from 30.1% to 36.8%" while "inline comment volume decreases (-22%)", a pattern the authors read as "most consistent with reflexive habituation under growing workload rather than rational trust calibration alone" ([arXiv:2606.22721v1](https://arxiv.org/abs/2606.22721v1)). A gate designed never to retire is the gate most exposed to that decay, and no approver corrects it by trying harder ([reviewer habituation](../code-review/reviewer-habituation-decay.md)).

Enforcement also costs throughput on work with no security relevance. Across 12 coding agents on Terminal-Bench 2.1, "under the strictest policy, success losses reach 18.3 points and cost inflation 167.3%", and runs "grind into timeouts or wrong solutions rather than stopping early" ([arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)). A stalled run does not announce that policy stalled it, so the cost is hard to attribute.

A selector matches text, not intent. `Shell(git push *)` prompts identically for a docs typo and a force-push to a release branch, so the approver sees no signal the policy author had. Client coverage is also worth checking before you rely on a rule. The controls are "generally available in the GitHub Copilot app, GitHub Copilot CLI, and Visual Studio Code sessions that use Agent Host" ([GitHub Changelog](https://github.blog/changelog/2026-09-09-enterprise-managed-permissions-for-github-copilot-agent-operations)), and in VS Code they "apply to Copilot sessions that use Agent Host" ([GitHub Docs](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)).

## Example

The `permissions` block from GitHub's own `managed-settings.json` reference ([GitHub Docs](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)):

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "deny": [
      "Shell(rm -rf *)",
      "Read(~/.ssh/**)",
      "Edit(//etc/**)",
      "Domain(*.unapproved.example)"
    ],
    "ask": [
      "Shell(git push *)",
      "Edit(/src/**)",
      "Domain(api.github.com)"
    ],
    "allow": [
      "Shell(npm test *)",
      "Read(/src/**)",
      "Domain(registry.npmjs.org)"
    ]
  }
}
```

Three `ask` entries, and `Edit(/src/**)` is the one to argue about. It prompts on every write to the source tree, which is most of what the agent does. `Shell(git push *)` is the shape that fits the conditions above: rare, consequential, and answered by someone who knows what the branch is.

## Key Takeaways

- A managed ask is a permission state local config cannot express, because local approval is built to be storable and this one is not.
- Budget asks by how often the operation fires, not by how risky it looks. Repetition is what degrades the gate.
- Audit the unmatched set before shipping the first rule. Defining any rule makes every unnamed supported operation prompt.
- Treat a central `allow` list as a ceiling. It intersects with the developer's list, while `deny` unions.
- Give headless and scheduled runs a `deny` or an `allow`, never an `ask`. There is nobody there to answer.

## Related

- [Working Inside an Enterprise-Managed Agent Sandbox Policy](enterprise-managed-agent-sandbox.md) — the sibling `sandbox` key, and the most-restrictive-wins merge these permission keys sit alongside.
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — where a control gets evaluated, and why naming the escape hatches is the difference.
- [Transcript-Driven Permission Allowlist](transcript-driven-permission-allowlist.md) — the accreted-grant workflow a managed ask deliberately invalidates.
- [Team-Scoped Agent Policy Delegation](team-scoped-policy-delegation.md) — how these subkeys are marked overridable so a team can vary them inside the enterprise boundary.
- [Reviewer Habituation in Agent PR Review](../code-review/reviewer-habituation-decay.md) — the measured decay that bounds what any repeated approval gate buys.
