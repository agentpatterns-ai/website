---
title: "Layered Policy Resolution for Multi-Group Agent Users"
term: "Layered Policy Resolution"
description: "Claude gateway layered policies combine matching roles. Deny rules accumulate, but order still controls allow lists and can combine broader permissions."
tags:
  - agent-design
  - claude
  - security
aliases:
  - layered policy resolution
  - multi-group agent policy composition
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-06
maturity: emerging
---

# Layered Policy Resolution for Multi-Group Agent Users

> Layered policy resolution applies every matching role policy; deny lists and hook arrays accumulate, while allow lists and blocks follow listing order.

Layered resolution matters when a developer matches multiple role policies. Claude apps gateway normally selects the first match and merges it with the catch-all base. Setting `managed.policy_mode: layered` includes every matching policy through the first `match: {}` entry ([gateway configuration](https://code.claude.com/docs/en/claude-apps-gateway-config#apply-every-matching-policy)).

The catch-all already supplies baseline settings in default mode. Layering changes how overlapping roles combine; it is unnecessary just to inherit an organization-wide baseline ([managed policy defaults](https://code.claude.com/docs/en/claude-apps-gateway-config#managed)).

## Selection and combination are separate decisions

Including more settings policies does not imply that every resulting value becomes more restrictive. Check each field.

The gateway merges by field type:

| Field type | Layered result |
|---|---|
| Deny lists and hook arrays | Combine across matching policies |
| Allow lists, scalar values, blocks such as `sandbox` | First-listed matching policy that sets the field wins |
| `env`, `modelOverrides`, `skillOverrides` | Merge by name, with first-listed precedence for each name |
| `desktop` keys | Follow the base `desktop` block merge rules |

Order therefore remains significant ([merge rules](https://code.claude.com/docs/en/claude-apps-gateway-config#apply-every-matching-policy)).

## Test combinations, including broader results

The vendor's example starts with `sandbox.enabled: true` in the catch-all. One group allows `Bash`; another disables the sandbox. A member of both receives both relaxations. The documented remedy lists the `Bash`-allowing policy first and copies the catch-all's whole `sandbox` block into it. Review effective settings for overlapping memberships, not just each role in isolation ([composition warning](https://code.claude.com/docs/en/claude-apps-gateway-config#apply-every-matching-policy)).

Use the distinction between selection and combination when building regression cases. A test for a single matching group cannot establish the outcome for a user matching two. Keep an explicit expected result for each relevant group combination. Include both prohibited operations and operations that should remain available.

## Deployment constraints

The mode requires gateway version 2.1.316 or later. Upgrade every replica first, and remove the key before rolling back. Rejected settings include negated Read/Edit deny or ask patterns. It also rejects `disableAllHooks`, `allowedHttpHookUrls`, and `httpHookAllowedEnvVars` outside the catch-all ([gateway constraints](https://code.claude.com/docs/en/claude-apps-gateway-config#apply-every-matching-policy)).

First-match resolution remains a simpler option when roles do not overlap. Layered resolution addresses overlapping policies, but requires reviewing their combined effects.

## Key Takeaways

- Keep baseline inheritance separate from the choice to combine role policies.
- Test policy order where allow lists or sandbox settings differ.
- Include overlapping memberships in rollout tests and plan configuration rollback with the server version.

## Related

- [Most-Restrictive-Wins Fusion](most-restrictive-wins-fusion.md) — combining per-call decisions after policies participate
- [Team-Scoped Agent Policy Delegation](../../security/team-scoped-policy-delegation.md) — which policy settings a team can change
- [Tenant Model Policy](tenant-model-policy.md) — model availability under centrally managed policy
