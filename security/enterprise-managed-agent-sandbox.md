---
title: "Working Inside an Enterprise-Managed Agent Sandbox Policy"
term: "Enterprise-Managed Sandbox Policy"
description: "An org-set agent sandbox composes as a floor rather than an override, so your settings can only tighten it and the effective-policy report is the only statement of the boundary."
tags:
  - security
  - agent-design
  - copilot
aliases:
  - managed sandbox policy
  - org-set sandbox boundary
  - centrally configured agent sandbox
last_reviewed: 2026-09-09
maturity: emerging
---

# Working Inside an Enterprise-Managed Agent Sandbox Policy

> A managed sandbox is a floor your settings can only tighten, so no local edit widens it and no single file states where it sits.

An enterprise-managed sandbox policy is a set of administrator-owned restrictions that a coding agent composes into your local sandbox configuration, taking the most restrictive value at every point. GitHub shipped one for Copilot in JetBrains IDEs on 8 September 2026, in public preview. It covers "sandbox enablement, filesystem and network access, proxy settings, developer-tool access, macOS Keychain access, and more", and "Copilot locks affected controls in the IDE and identifies settings managed by your organization" ([GitHub Changelog](https://github.blog/changelog/2026-09-08-enterprise-managed-sandbox-in-copilot-for-jetbrains/)).

## Read it as a floor, not an override

The settings screen says precedence, and that is the wrong model to carry into a denial. GitHub's reference states that "managed sandbox settings impose restrictions rather than defaults": a managed `true` on a force-on setting enforces it, a managed `false` on a capability prohibits it, and any other value leaves your configuration unchanged ([enterprise managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)). You keep every tightening move you had. You lose the loosening ones.

You therefore need two things you did not need before. A way to print the boundary, since it is not in any one file. And an escalation route away from the keyboard, since the only widening act available is an administrator changing a source.

## What the org can pin

| Managed value | Effect on you |
|---|---|
| `enabled: true` | Sandboxing cannot be turned off through your configuration, `--no-sandbox`, or `/sandbox disable` |
| `allowBypass: false` | No per-command escape, and no session-wide opt-out from a bypass prompt |
| `failIfUnavailable: true` | With `enabled: true`, model and tool execution is blocked outright when no sandbox backend can enforce the policy |
| `readwritePaths` / `readonlyPaths` | Your grants survive only where the exact path string also appears in the managed list |
| `deniedPaths` | Managed denials add to yours |
| `allowDevToolAccess: false` | Package restoration, authenticated registry operations, and shared-cache builds can fail until each path is granted explicitly |

All six rows come from the `sandbox` key of the managed settings reference ([GitHub Docs](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)). Read the path rows twice. Managed grant lists "are matched against user-configured lists by exact path string, not by parent or child path coverage", so a managed grant of `/Users/octocat/projects` does not preserve your grant of `/Users/octocat/projects/app`.

## Why it works

The enforcement point moves out of a file you can write, and it stays out because the merge is an intersection rather than a lookup. Copilot composes the sandbox policy "from every source in force at once", with server-managed, MDM, and file-based sources combining "with each other, and with your own settings, in the most restrictive direction rather than one source overriding another" ([understanding local sandboxing](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/understanding-local-sandboxing)). Your settings can only narrow that result. This is the general [most-restrictive-wins merge](../patterns/agent-design/most-restrictive-wins-fusion.md) applied across policy channels instead of across hooks.

The key names above are Copilot's; the merge rule is what transfers. Where a vendor composes policy by restriction, no local edit widens the boundary and no single file states it. Where managed policy replaces your configuration instead, both consequences change, so confirm which shape you have.

The same property is why you cannot answer "am I denied or is this broken?" by reading configuration. Several sources are live at once and none of them holds the answer. In the CLI, `/sandbox policy` prints "the read/write, read-only, and denied paths that a command launched from here would actually receive... not just a copy of your saved settings" ([understanding local sandboxing](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/understanding-local-sandboxing)). The JetBrains release ships enterprise policy diagnostics for the same job, to "verify that policies are correctly detected and enforced on your device" ([GitHub Changelog](https://github.blog/changelog/2026-09-08-enterprise-managed-sandbox-in-copilot-for-jetbrains/)).

So the first move on a denial is that report. A path listed as denied gives you a policy question; a path absent from every list gives you a defect worth filing. Take the policy question to an administrator as a sub-property and an exact path string. Those are the units the merge operates on, and "my build fails" cannot be actioned against them.

## When this backfires

Mandatory sandboxing on a fleet that cannot run one stops work rather than degrading it. With `failIfUnavailable: true`, Copilot "blocks model and tool execution instead of allowing commands to fail or run unsandboxed" ([GitHub Docs](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)), and local sandboxing on Windows requires a Windows Insiders build ([configuring local sandbox settings](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/configuring-local-sandbox-settings)). A stock Windows machine under that policy runs nothing.

The network leg is weaker than the settings screen implies on two of the three platforms. "On Linux and macOS, the proxy is cooperative: it is applied through standard proxy environment variables and depends on each tool honoring them. On Windows, the sandbox enforces the proxy" ([configuring local sandbox settings](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/configuring-local-sandbox-settings)). A managed proxy URL is enforcement on Windows and [advice everywhere else](enforced-versus-advisory-controls.md).

Leaving `allowBypass` unset keeps a session-wide off switch reachable from an active bypass prompt, and that prompt arrives at the worst available moment for judgement. Set it to `false` and the hole closes, but then every blocked build becomes a ticket.

Hardening also costs throughput on tasks with no security relevance. Across 12 coding agents on Terminal-Bench 2.1, "under the strictest policy, success losses reach 18.3 points and cost inflation 167.3%", and runs "grind into timeouts or wrong solutions rather than stopping early" ([arXiv:2608.02670v1](https://arxiv.org/abs/2608.02670v1)). That failure shape is what costs the developer time, because a denied run does not look denied.

## Key Takeaways

- Managed sandbox values impose restrictions, not defaults. On a denial the question is never which setting to change, it is which source contributes the restriction.
- Run the effective-policy report before filing a bug. Server-managed, MDM, and file-based sources compose at once, so no configuration file answers the question.
- Check the exact path string when a grant disappears. Managed and user path lists intersect by string, and a parent directory in the managed list does not cover your child path.
- Ask whether `allowBypass` is set before assuming the boundary holds. Left unset, it puts a session-wide opt-out one prompt away.
- On Linux and macOS, treat a managed proxy as a request to your tools, and put egress control somewhere the tools cannot decline.

## Related

- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — where to sort each leg of an inherited policy, and why the cooperative proxy lands on the advisory side.
- [Most-Restrictive-Wins Fusion for Parallel Agent Control Returns](../patterns/agent-design/most-restrictive-wins-fusion.md) — the general merge function this policy composition is an instance of.
- [Team-Scoped Agent Policy Delegation](team-scoped-policy-delegation.md) — the administrator's side, and why sandbox keys are not among the delegable ones.
- [Policy-Graded Evaluation of Coding Agents](../verification/policy-graded-agent-evaluation.md) — what enforced tiers cost in success rate and tokens, measured per model.
- [Enterprise-Managed Plugin Governance for Agent CLIs](enterprise-managed-plugin-governance.md) — the same managed-settings channel applied to the plugin code-load path.
- [Non-Retirable Approval Rules for Agent Operations](non-retirable-approval-rules.md) — the `permissions` key beside this one, where the middle state demands a fresh approval no saved grant satisfies.
