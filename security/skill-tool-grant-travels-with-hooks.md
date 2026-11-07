---
title: "A Skill's Tool Grant Travels With Its Hooks"
term: "Grant-Guard Coupling"
description: "Claude Code links some skill tool pre-approvals to hook declarations. Check the main-conversation scope, fork exception, and managed permission rules."
aliases:
  - grant-guard coupling
  - coupling a permission to its check
  - permission that outlives its constraint
tags:
  - security
  - claude
  - skills
  - hooks
  - plugins
last_reviewed: 2026-11-06
maturity: emerging
---

# A Skill's Tool Grant Travels With Its Hooks

> Claude Code's plugins-only hooks policy withdraws main-conversation tool pre-approval from personal and project skills that declare hooks, with exceptions for forked skills.

Grant-guard coupling means withdrawing a permission when its required check cannot run. Claude Code 2.1.304 introduced a narrower, declaration-based rule for skills in the main conversation. The release removes their `allowed-tools` grant when a plugins-only policy excludes their hooks ([changelog](https://code.claude.com/docs/en/changelog#2-1-304)).

The managed setting `strictPluginOnlyCustomization: ["hooks"]` blocks hooks from user, project, and local settings, plus frontmatter hooks from restricted sources. Those include skills, commands, and agents from sources that a skills or agents lock would block. Skills still load if policy permits their source. A personal or project skill declaring hooks loses its pre-approval in the main conversation. Skills using `context: fork` and skills declaring no hooks keep it ([settings reference](https://code.claude.com/docs/en/settings-reference#strictpluginonlycustomization-hooks)).

## What the grant controls

`allowed-tools` pre-approves listed tools for the invoking turn; it does not limit the available tool set. Permission settings still govern other tools ([skills reference](https://code.claude.com/docs/en/skills#pre-approve-tools-for-a-skill)). Withdrawal removes this approval route. Check the remaining rules before assuming the tool will prompt or be denied.

The design test is whether the missing hook actually restricts the granted operation. A declaration alone does not establish that dependency. Claude Code checks for declared hooks; the documented rule does not distinguish a permission gate from a logging hook ([settings reference](https://code.claude.com/docs/en/settings-reference#strictpluginonlycustomization-hooks)).

Coupling a permission to a required check applies Saltzer and Schroeder's fail-safe-default principle to policy filtering. Their principle bases access on explicit permission and favors denial when the policy is incomplete. This is a design inference, not evidence that every skill hook enforces access control ([basic protection principles](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)).

## Costs and exceptions

Restoring prompts has a cost. Anthropic warns that repeated approvals can reduce attention to individual decisions ([sandboxing article](https://www.anthropic.com/research/claude-code-sandboxing)).

Test skills that inject shell output ([injected commands](https://code.claude.com/docs/en/skills#inject-dynamic-context)). Outside auto mode, an injected command aborts invocation without prompting unless its permission check returns allow. Losing an `allowed-tools` grant can therefore abort the skill ([injected-command checks](https://code.claude.com/docs/en/skills#permission-checks-on-injected-commands)).

Removing a hook declaration restores the grant under this hooks policy alone. The vendor also documents moving the skill into a marketplace-installed plugin to retain its hooks ([managed hooks guidance](https://code.claude.com/docs/en/skills#when-managed-settings-lock-hooks-to-plugins)). These alternatives show why the rule cannot guarantee that permission always depends on an active check.

## Separate hook policy from permission policy

For organizations that also want to reject personal and project skill pre-approvals, `allowManagedPermissionRulesOnly: true` provides a separate control. From version 2.1.282, it ignores their `allowed-tools` regardless of hook declarations ([skills reference](https://code.claude.com/docs/en/skills#when-only-managed-permission-rules-apply)).

This setting also ignores permission rules from user, project, local, and `--settings` files. Review those rules before rollout: the change drops their allow, ask, and deny rules. Command-line `--disallowedTools` and current-session deny rules still apply. Managed and bundled skills retain their grants ([managed permission setting](https://code.claude.com/docs/en/settings-reference#allowmanagedpermissionrulesonly)).

## Key Takeaways

- Review the hook's actual check before treating its presence as a reason to trust a tool grant.
- Test main-conversation and forked invocations separately; the hooks policy gives them different pre-approval behavior.
- Inventory permission rules before enabling managed-only permissions, including restrictions that the setting stops reading.

## Related

- [Declaring a Per-Hook Failure Mode for Agent Policy Gates](per-hook-failure-mode.md) — what to do when a hook renders no verdict, the state a policy filter creates on purpose
- [Monotonic Capability Attenuation for Composition-Safe Tool Use](monotonic-capability-attenuation.md) — the general form of authority that may only shrink
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — which safeguards the runtime evaluates and which resolve inside the model's context
- [Skill disallowed-tools Frontmatter: Skill-Layer Tool Denial](../tools/claude/skill-disallowed-tools.md) — the deny-side field a skill can declare beside its grant
- [Restraint Rules Need External Enforcement](../instructions/restraint-rules-need-external-enforcement.md) — why a rule that asks an agent to stop belongs outside the agent
