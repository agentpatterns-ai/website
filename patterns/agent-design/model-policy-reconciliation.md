---
title: "Model Policy Reconciliation: A Copilot Model Allow List as Code"
term: "Model Policy Reconciliation"
description: "Drive a Copilot model allow list from a checked-in file through the model policy API. The live delegation mode decides where a deny can sit, removals need an explicit write, and the state you read back is a policy record rather than user access."
tags:
  - agent-design
  - copilot
  - automation
  - model-routing
aliases:
  - model allow list reconciliation
  - policy-as-code model governance
last_reviewed: 2026-10-20
maturity: emerging
---

# Model Policy Reconciliation: A Copilot Model Allow List as Code

> Model policy reconciliation drives a model allow list from a checked-in file, and only the live delegation mode decides where a deny can sit.

GitHub's Copilot model policy API turns the model allow list into a file you can diff and approve. GET and PATCH endpoints reached general availability on October 19, 2026: "You can now use the REST API to retrieve and update Copilot model policies for enterprises, enterprise teams, agent apps, and organizations" ([GitHub Changelog 2026-10-19](https://github.blog/changelog/2026-10-19-copilot-model-policy-api-for-enterprise-orgs-and-teams)). The two delegation targets are modes rather than tiers: "Enterprise policies can delegate model control to organizations in organization mode, or to teams and apps in enterprise teams mode."

## When this applies

Four conditions come from the API's shape, not from preference. Miss one and the file describes a policy the platform is not enforcing.

- The file knows which mode is live, because the modes differ in how many scopes can deny. The enterprise model's `policy_state` records its delegation target, and `delegate_to_organizations` "is only accepted for enterprises that manage Copilot through organizations" ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)).
- The enterprise default is set, not inherited. A model you never name is governed by `default_availability`, so leaving it enabled permits eligible models outside the file ([default availability documentation](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/enterprise/default-model-availability)).
- Removals are written, never implied. The team endpoint says "Use `optional` to remove the team's policy", and the apps endpoint uses the same value to remove the stored apps policy for a model ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)).
- The drift check reads a policy record. The apps PATCH and enterprise-team GET documentation state: "These states are not a final access decision for a user" ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)).

## Where a deny can sit, per mode

The two modes differ on one thing that matters to a file: how many scopes can say no.

| Mode | Scopes the file writes | Where a deny can sit | Removal below the enterprise |
|---|---|---|---|
| Organization (default) | Enterprise, organization | Enterprise, and per organization for a delegated model | Organization sets the model disabled |
| Enterprise teams (preview) | Enterprise, enterprise teams, enterprise apps | Enterprise only | Write `optional` to clear the grant |

In enterprise teams mode the lower scopes can add access but cannot override an enterprise deny. "If the enterprise has disabled a model, it cannot be enabled for a team." "If the enterprise has enabled a model, it is always enabled for teams." "A team can receive access to additional models on top of the enterprise baseline" ([Managing availability of models in your enterprise](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-availability-of-default-models)). Team membership unions rather than intersects: "If a user gets a model from any one enterprise team, that user has access to the model everywhere" ([GitHub Changelog 2026-07-31](https://github.blog/changelog/2026-07-31-enterprise-teams-model-policy-targeting-in-public-preview)).

Organization mode keeps a real second deny. Delegating a model hands over both answers, since "Organization owners can then choose whether to enable or disable the model", and switching modes deactivates that scope: "When you opt in to the preview, organization-level model settings are deactivated" ([Managing availability of models in your enterprise](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-availability-of-default-models)).

The two sources disagree at team scope. GitHub's console documentation says "There is no option to explicitly set a model to \"disabled\" for a team in the team's settings" ([Managing availability of models in your enterprise](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-availability-of-default-models)), while the team PATCH body documents a `policy_state` of `enabled`, `disabled`, or `optional` ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)). Write `optional` for removal, which both sources describe, and leave `disabled` at team scope alone until its behavior is documented.

## Reconciler discipline

Close the set at the enterprise default, because new releases arrive through the default rather than through your file: "When a new model is released, it inherits the default until you explicitly configure it" ([About default availability of Copilot features and models](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/enterprise/default-model-availability)). The enterprise PATCH body carries `default_availability.policy_state` as its own object, so that switch is itself reconcilable ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)).

Read before you write. Each team and app model in a GET response carries `editable` and `enterprise_policy_state` beside its `policy_state`, and "Locked models cannot be updated." Give the drift job a read-only credential and the apply job a separate one. The documented permissions split `read_enterprise_ai_controls` from `write_enterprise_ai_controls`, with classic token scopes `read:enterprise` and `admin:enterprise` ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)).

## Why it works

The enterprise deny is a fixed point whichever mode is live, so the file's restrictions survive every write beneath them. A model disabled there cannot be re-enabled by a team, and a model the default policy disables is "automatically disabled for all your Copilot users, and organizations or teams cannot enable it" ([About default availability of Copilot features and models](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/enterprise/default-model-availability)). A wrong write below the baseline can over-grant within the enterprise delegation but cannot breach an enterprise deny. This bounds both team owners and unattended jobs. The API also hands that boundary over as data rather than prose: `editable` and `enterprise_policy_state` tell a reconciler which fields it owns before it sends anything ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)).

## When this backfires

- The write path runs against a preview. Enterprise teams mode is opt-in, and "Any changes to enterprise-level model policies made after switching to enterprise teams mode will not be preserved after rollback" ([Managing availability of models in your enterprise](https://docs.github.com/enterprise-cloud@latest/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-availability-of-default-models)). A rollback discards the state your job has been maintaining.
- The mode switch is applied in one pass. On migration, "models that are currently delegated to organizations will be unavailable until they are enabled for specific teams" (same page). Flip the mode before every delegated model has a team grant and you take access away from everyone unmapped.
- Licenses come from more than one enterprise. In enterprise teams mode, without Enterprise Managed Users, "only the model policies from your enterprise apply to users if they are using a Copilot license assigned from your enterprise. Restrictions from any other enterprise will not apply" ([GitHub Changelog 2026-07-31](https://github.blog/changelog/2026-07-31-enterprise-teams-model-policy-targeting-in-public-preview)).

## Example

**Before** — the deny lives wherever an admin last clicked, and a new model inherits the default:

```text
Enterprise: default availability   → enabled
Enterprise: gpt-5.6-sol            → delegate_to_teams_and_apps
Data team:  gpt-5.6-sol            → enabled   (console only: no diff, no approver)
```

**After** — the baseline is closed in the repository, and the team grant is the only delegated decision:

```bash
curl -L -X PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  https://api.github.com/enterprises/ENTERPRISE/copilot/model-policies \
  -d '{"default_availability":{"policy_state":"disabled"},
       "models":[{"model_name":"gpt-5.6-sol","policy_state":"delegate_to_teams_and_apps"}]}'

curl -L -X PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  https://api.github.com/enterprises/ENTERPRISE/teams/TEAM_ID/copilot/model-policies \
  -d '{"models":[{"model_name":"gpt-5.6-sol","policy_state":"enabled"}]}'
```

Dropping that model from the file later takes a third call, sending `policy_state: "optional"` to the team endpoint. The request shapes, the version header, and the `gpt-5.6-sol` example model are GitHub's own ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)).

## Key Takeaways

- Put every deny you cannot delegate in the enterprise object, `default_availability` included. It is the one scope both modes enforce.
- Remove team grants with explicit `optional` writes; disable organization grants explicitly. The documented removal is a write, not a deleted line.
- Branch the reconciler on `delegate_to_organizations` versus `delegate_to_teams_and_apps` before it writes, because `delegate_to_organizations` "is only accepted for enterprises that manage Copilot through organizations" ([REST: enterprise AI controls](https://docs.github.com/enterprise-cloud@latest/rest/enterprise-admin/ai-controls)).
- Run drift detection on a `read:enterprise` token and keep `admin:enterprise` on the apply step, so the detector cannot change what it reports.
- Call the drift report a policy-record check in whatever your auditors read. GitHub makes no promise that it reflects user access.

## Related

- [Tenant Model Policy: Organization-Scoped Rules for AI Model Selection](tenant-model-policy.md) — the policy plane this API drives, and where it sits relative to picker and routing.
- [Agent Governance Policies](../../workflows/agent-governance-policies.md) — the wider enterprise-to-user policy hierarchy Copilot enforces around model rules.
- [Administrative Effort Ceilings for Reasoning Budget](administrative-effort-ceilings.md) — the same admin tier applied to reasoning depth, where caps compose by minimum instead of by union.
- [Model Deprecation Lifecycle](../../workflows/model-deprecation-lifecycle.md) — the calendar a reconciled allow list has to track to avoid aging into total denial.
- [Auto Model Selection](auto-model-selection.md) — harness-side routing inside the catalog this policy has already filtered.
