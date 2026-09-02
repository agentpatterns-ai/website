---
title: "Team-Scoped Agent Policy Delegation"
term: "Team-Scoped Policy Delegation"
description: "Mark selected agent-config keys overridable so teams can vary them within an admin-owned boundary, safe only when the key allowlist is explicit, the deployment is server-managed, and team membership is itself governed."
aliases:
  - enterprise team specialization
  - overridable managed settings
  - delegated agent configuration
tags:
  - security
  - instructions
  - copilot
last_reviewed: 2026-08-08
maturity: emerging
---

# Team-Scoped Agent Policy Delegation

> Team-scoped policy delegation marks selected agent-config keys overridable, so teams vary those keys inside a boundary the administrator still owns.

Team-scoped policy delegation splits one agent configuration into keys a team may vary and keys only the enterprise may set. GitHub shipped it for Copilot managed settings on 3 August 2026, with the stated goal that "large enterprises can scale governance without bottlenecking every configuration change through central administrators or one-size-fits-all policies" ([GitHub Changelog](https://github.blog/changelog/2026-08-03-enterprise-team-specialization-for-managed-settings)). Three conditions decide whether the boundary holds. Where any one fails, per-team config is a set of standing exceptions rather than a delegation.

## Condition 1: the delegable keys are an explicit allowlist

A key becomes eligible only when the enterprise marks it with the `{ "overridable": <VALUE> }` syntax in `copilot/managed-settings.json`. Everything else is closed by default: "Keys not marked overridable remain an enterprise-level decision that teams can't modify" ([GitHub Docs: Enterprise managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)).

The allowlist is narrow today. The syntax "applies to the governance keys `permissions.model` and `permissions.disableBypassPermissionsMode`", and two further keys compose additively instead: `enabledPlugins` and `extraKnownMarketplaces` let a team file add to the enterprise baseline rather than replace it ([Enterprise managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)). GitHub extended the marking to MCP servers on 6 August 2026, so the new MCP allowlist keys can carry `overridable` too. That release also makes MCP access fail closed, and a server must pass every configuration layer before it loads ([GitHub Changelog](https://github.blog/changelog/2026-08-06-mcp-allowlists-in-enterprise-managed-settings)).

Teams select among enterprise-authored values and do not write new ones. "The enterprise defines all settings—team membership only determines which users receive a given set of values" ([Enterprise managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)). A team file releases a key by setting it to `"unmanaged"`. It does not invent one.

## Condition 2: team membership is governed

The merge across a user's teams runs in the opposite direction to every neighboring policy layer. "If a user belongs to multiple teams, their team files are combined using the least restrictive value for each key, then applied beneath the enterprise settings, where platform decisions always win" ([GitHub Docs: Configuring enterprise-managed settings](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-agents/configure-enterprise-managed-settings)).

That makes team membership a capability grant. Adding an engineer to one permissive team relaxes their agent policy across every key that team releases, and the change appears in a membership list rather than in a settings diff. The same product resolves the `sandbox` key the other way, combining managed and user restrictions "in the most restrictive direction" ([Enterprise managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)). An admin reasoning by analogy from [most-restrictive-wins fusion](../patterns/agent-design/most-restrictive-wins-fusion.md) will predict the wrong result.

## Condition 3: the deployment is server-managed

Team targeting reads `copilot/team-mappings.json` and `copilot/teams/` from the `.github-private` repository, which only the server-managed path consults. Precedence runs MDM-managed, then server-managed, then file-based, then user-level ([Enterprise managed settings](https://docs.github.com/en/copilot/reference/enterprise-administrators/enterprise-managed-settings)). Fleets that deploy by MDM or by dropping a file on the device keep the ceiling and lose the specialization entirely.

## Why it works

The administrator never hands over the two things that bound the result: which keys may vary, and where team values land in the merge. A team file can only occupy space the ceiling left open, because the enterprise layer is applied on top of it ([Configuring enterprise-managed settings](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-agents/configure-enterprise-managed-settings)).

What moves to the team is authorship of a proposal. Because the configuration is a repository, "a repository-based governance approach allows users to open pull request with suggestions to improve the settings, and it allows settings changes to be restricted by codeowners and rulesets" ([GitHub Docs: Creating a .github-private repository](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-agents/create-github-private-repo)). Internal visibility on that repository is what lets a team open the pull request at all. The bottleneck the changelog names is the admin having to originate every change, so review replaces authorship as the control point.

Claude Code delegates on a different axis. Its ladder runs managed, command-line arguments, local, project, then user, and managed settings apply to all organization members or all users on a machine, with no identity dimension ([Claude Code settings](https://code.claude.com/docs/en/settings)). Depth of scope and breadth of audience are separate levers.

## When this backfires

- Users sit in several enterprise teams. The least-restrictive merge means the effective floor is the floor of a person's most permissive team. Group membership accumulates the same way elsewhere: "The role that was tight on Monday has inherited two group memberships by Friday, a break-glass exception by the end of the sprint, and a pipeline-granted privilege by the next quarter", and because grants compose additively, "every new group membership is a one-way ratchet unless something actively reverses it" ([Token Security](https://www.token.security/blog/least-privilege-policy-drift-and-runtime-risk)).
- The team needs a key outside the allowlist. Sandbox paths, telemetry routing, and marketplace lockdown are not overridable, so a team blocked on one of those gains nothing and the bottleneck remains.
- The server call fails. On Copilot CLI, "if a request for server-managed settings fails and no cached response is available, the server-managed policy is unavailable for that session" ([Configuring enterprise-managed settings](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-agents/configure-enterprise-managed-settings)). Ceiling and specialization arrive together, so a session that cannot reach the server gets neither.
- Response time matters. Server-managed changes reach clients "within about an hour" unless each user restarts or signs in again ([Configuring enterprise-managed settings](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-agents/configure-enterprise-managed-settings)). Tightening a team file is not a revocation lever.
- The organization is small. Below the size where a central admin is a real bottleneck, a mapping file plus a per-team directory adds a second merge layer for no gain.

## Example

An enterprise defers two keys, then routes an AI-trained team to a looser file. First the ceiling, in `copilot/managed-settings.json`:

```json
{
  "model": { "overridable": "auto" },
  "permissions": {
    "disableBypassPermissionsMode": { "overridable": "disable" }
  }
}
```

Then the routing, in `copilot/team-mappings.json`, where each key is a settings file and each value is the team slugs that receive it:

```json
{
  "devs.json": ["developers-all", "finops-dev"],
  "ai-users.json": ["ai-baseline-trained"],
  "frontier.json": ["ai-pioneers"]
}
```

Then the specialization, in `copilot/teams/frontier.json`, carrying only keys the ceiling marked overridable:

```json
{
  "model": "unmanaged",
  "permissions": {
    "disableBypassPermissionsMode": "unmanaged"
  }
}
```

Members of `ai-pioneers` pick their own model and can enable bypass mode. Everyone else stays on auto model selection with bypass mode disabled. The trap is an engineer who belongs to both `developers-all` and `ai-pioneers`: the least restrictive value wins per key, so that engineer gets the frontier settings, and no reviewer of `frontier.json` sees who joins that team afterwards. Treat membership changes on any team named in `team-mappings.json` as policy changes, and audit them on the same cycle as the files ([Configuring enterprise-managed settings](https://docs.github.com/en/copilot/how-tos/administer-copilot/manage-for-enterprise/manage-agents/configure-enterprise-managed-settings)).

## Key Takeaways

- The delegation boundary is an allowlist of keys, not a scope. Unmarked keys stay closed, so the review question is which keys carry `overridable`, never which teams have files.
- Read the ceiling file before any team file. A team file is unreadable on its own, because `"unmanaged"` means whatever value the enterprise deferred.
- Put team rosters on the settings-file audit cycle. The multi-team merge takes the least restrictive value per key, so a membership change edits policy without touching a config diff.
- Confirm the deployment method before promising a team its own settings. Only the server-managed path reads `team-mappings.json`; MDM and file-based fleets cannot receive a specialization.
- Plan a separate exception path for sandbox, telemetry, and marketplace policy. Those keys are not overridable, so this mechanism gives a team blocked on them nothing.

## Related

- [Most-Restrictive-Wins Fusion for Parallel Agent Control Returns](../patterns/agent-design/most-restrictive-wins-fusion.md) — the merge function this pattern feeds inputs to, and the one it inverts across teams.
- [Enterprise-Managed Plugin Governance for Agent CLIs](enterprise-managed-plugin-governance.md) — the same managed-settings file governing the plugin code-load path.
- [Tenant Model Policy: Organization-Scoped Rules for AI Model Selection](../patterns/agent-design/tenant-model-policy.md) — org-level targeting of the model key this pattern delegates to teams.
- [Agent Governance Policies for AI Agent Development](../workflows/agent-governance-policies.md) — the enterprise, organization, and user tiers the team dimension cuts across.
- [Org-Membership-Gated Agent Entitlement](org-membership-gated-agent-entitlement.md) — the other place membership decides agent capability, with a fail-closed default.
- [Agent Governance Plane: Audit Events and Message-Content Surfaces](agent-governance-plane.md) — the audit surface that records which delegated value was in force, and its coverage limits.
