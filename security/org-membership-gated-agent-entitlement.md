---
title: "Org-Membership-Gated Agent Entitlement"
description: "Gate AI chat activation on directory-managed GitHub organization membership, not seat licences alone — a fail-closed device policy that ties entitlement to identity rather than installation."
aliases:
  - org-gated agent entitlement
  - approved account organizations policy
  - account-membership gating for AI chat
tags:
  - security
  - human-factors
  - copilot
last_reviewed: 2026-06-03
maturity: established
---

# Org-Membership-Gated Agent Entitlement

> Gate AI chat on directory-managed GitHub org membership, not seat licences — a fail-closed device policy tying entitlement to identity, not installation.

Seat licenses answer "who paid" but not "who is currently allowed to send code to a model." A user offboarded from the company keeps the installed VS Code on their device. They may also keep a personal GitHub account that still resolves a Copilot Pro seat. Org-membership-gated entitlement closes that gap by deciding chat activation on the device against directory-managed group membership.

## The `ChatApprovedAccountOrganizations` policy

VS Code 1.118 (April 29, 2026) introduced the `ChatApprovedAccountOrganizations` device policy ([VS Code 1.118 release notes](https://code.visualstudio.com/updates/v1_118)). Setting it to a non-empty list activates the Approved Account gate: "all AI features are disabled until the user signs into a GitHub account whose organizations intersect this list" ([VS Code Enterprise Policies](https://code.visualstudio.com/docs/enterprise/policies)).

Two conditions must hold before chat activates ([VS Code 1.118 release notes](https://code.visualstudio.com/updates/v1_118)):

1. The user is signed into a GitHub account with membership in an approved organization.
2. The account-based policy has been resolved.

Until both resolve, features stay off — a fail-closed model that mirrors the contract pattern used in [fail-closed remote settings enforcement](fail-closed-remote-settings-enforcement.md) for Claude Code's managed settings.

## Deployment

The policy value is a JSON list of org slugs deployed as a device-level managed setting ([VS Code Enterprise Policies](https://code.visualstudio.com/docs/enterprise/policies)):

| Platform | Mechanism |
|----------|-----------|
| Windows  | Registry policy value (string containing the JSON list) |
| macOS    | `.mobileconfig` profile |
| Linux    | `/etc/vscode/policy.json` |

The wildcard `'*'` accepts any signed-in GitHub or GitHub Enterprise account — a relaxation suited to GHE-only deployments where the identity provider already constrains who can authenticate ([VS Code Enterprise Policies](https://code.visualstudio.com/docs/enterprise/policies)).

## Why this is not redundant with seat licenses

Seat-based controls answer entitlement at GitHub.com. They govern license assignment but do not enforce who currently signs in on a device. Server-side org policies likewise only bind users holding [licenses granted by that organization](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-organization/manage-policies); a personal Copilot Pro account on the same device sidesteps them. A device policy moves the decision into the client, where the chat code path itself refuses to start.

The structural pattern is conditional access from identity products: entitlement = identity assertion + group membership + device posture. Org membership becomes the directory-managed group; the device policy is the local check that enforces it.

## Failure modes

- Surface coverage gap: the policy applies only to VS Code chat. Copilot CLI, Claude Code, JetBrains Copilot, and browser-based chat surfaces are not bound — the gate is one client among many. Treat it as a layer, not a perimeter.
- Account is not the person: the check authenticates a GitHub account, not the human at the keyboard. Shared machines, kiosks, or any user with a personal account in an approved org can satisfy the policy.
- Offboarding lag: removing a user from the GitHub org is a separate runbook step from HR or IdP deprovisioning. If the runbook does not list org-membership revocation, the gate stays open after corporate access ends.
- Contractor and personal-account expansion: including contractors who use personal GitHub accounts means adding them to the approved org — widening membership beyond the employees the policy was written for.

## Example

A Windows-managed enterprise blocks all Copilot chat surfaces in VS Code unless the signed-in GitHub account belongs to `acme-engineering` or `acme-platform`:

```reg
[HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\VSCode]
"ChatApprovedAccountOrganizations"="[\"acme-engineering\",\"acme-platform\"]"
```

The same policy on Linux:

```json
{
  "ChatApprovedAccountOrganizations": ["acme-engineering", "acme-platform"]
}
```

Pair the offboarding runbook with org-membership revocation as the first irreversible step. The next VS Code launch on the user's device then fails the gate, and chat refuses to activate.

## Key Takeaways

- The Approved Account gate is fail-closed: chat stays off until an approved-org GitHub account is signed in *and* policy has resolved.
- Device-side enforcement is structurally distinct from seat licences and from GitHub.com-side org policies — it gates on the account currently signed in, not the licence assigned.
- Coverage is bounded to the VS Code surface; layer it with seat licensing and IdP-based controls rather than relying on it alone.
- The offboarding contract is one membership revocation — make it a runbook step, not an afterthought.

## Related

- [Enterprise Agent Hardening: Governance, Observability, and Reproducibility](enterprise-agent-hardening.md)
- [Fail-Closed Remote Settings Enforcement](fail-closed-remote-settings-enforcement.md)
- [Copilot Cloud Agent Organization Controls](../tools/copilot/cloud-agent-org-controls.md)
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
