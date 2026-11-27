---
title: "Permission Replies That Rewrite Coding-Agent Policy"
term: "Policy-Rewriting Permission Reply"
description: "In Claude Code, an allow answer to one permission prompt can carry updates that delete user, project, or local deny rules."
aliases:
  - policy updates in permission replies
  - permission reply policy rewrite
  - updatedPermissions deny rule removal
tags:
  - security
  - claude
  - arxiv
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-26
maturity: emerging
status: current
---

# Permission Replies That Rewrite Coding-Agent Policy

> In Claude Code, a permission reply that allows one call can also delete a deny rule from user, project, or local settings.

A policy-rewriting permission reply answers one prompt and also changes the rules that later calls are checked against. Claude Code lets an `allow` answer carry policy updates, which the runtime applies and can save to settings files. In an example from a preprint by Fei and colleagues, a remote approval service with no access to the operator's files approves an unrelated command and removes the deny rule on `.env`. The agent can then read the file in that session and later ones, even under the strict sandbox ([arXiv:2611.32195v1](https://arxiv.org/abs/2611.32195v1), §I).

The authors report that the deletion still succeeds on Claude Code 2.1.327, the latest release when they wrote. We have not reproduced the attack, and we have not verified later releases. Section numbers below refer to the preprint.

## What an answer can carry

Besides the operator's terminal dialog, four routes deliver answers: a plugin's hook, a prompt handler for unattended sessions, an application that embeds the agent through the SDK, and a remote front end on a bridge. All four may carry updates (§II). A `PermissionRequest` hook returns them as [`updatedPermissions`](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control).

The [hooks reference](https://code.claude.com/docs/en/hooks#permission-update-entries) lists the update types, including `removeRules`, which "Removes matching rules of the given `behavior`". An update targets the session or the local, project, or user settings. The same page says a hook ["can't approve what a deny rule refuses, unless a mod overrides the rule"](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control). That sentence covers the decision. The preprint tests whether the rule survives the update sent with the decision.

## Why the filter misses a deletion

The authors read the shipped filter from the binary. It checks only updates that add or replace allow rules, so a deletion of deny rules passes unchecked. They read build 2.1.312 and found the same filter loop in all 10 builds they installed from 2.1.301 to 2.1.325 (§IV-A, Appendix A).

In the releases they examined, three of the four routes skip even this filter. The prompt-handler path applies it. Hook and SDK paths in the default mode do not, unless a suppression condition holds (§IV-A, Appendix A).

The runtime stores each rule as a bare string with no author field. A deletion by an answer leaves the same record as the operator's own edit. When the plugin is uninstalled, the runtime can neither find the change nor undo it (§IV-D).

## Which updates lift a restriction

| Update in the answer | Reported effect |
|---|---|
| Remove or replace deny rules | The permission check stops refusing calls that only the lost rules denied (§VII-D). Deleting a file rule also lifts the sandbox's block (§IV-C) |
| Add a `WebFetch` or `Edit` allow rule | The sandbox widens with no deletion. A `WebFetch` rule let a rewritten command send a project file out, and an `Edit` rule let one write outside the project. A host rule saved for the session only did not reach the sandbox (§VII-C) |
| `setMode` to `acceptEdits` in user settings | The next headless session wrote a file unprompted on builds 2.1.319 and 2.1.314 (§VII-D, Appendix B) |
| `addDirectories` in user settings | The next session read an outside directory unprompted (same runs) |

The hooks reference adds one limit: `bypassPermissions` is [never saved as the default mode](https://code.claude.com/docs/en/hooks#permission-update-entries).

An answer can also [rewrite the input](permissionrequest-rewrite-sandbox-exit.md) of the call it approves. Under the strict sandbox, none of the three rewrites the authors tried exposed the protected file, while the policy update did. Without the sandbox, two of the rewrites exposed it too (§VII-C). Sending the file to the answering party took the deletion, an allow for the receiving host, and a rewritten command.

## Which relays forward updates

On 2026-10-29 the authors searched for relays. They read 70: Claude Code's Remote Control, plus open-source tools with at least 100 stars or 1,000 weekly npm downloads (§II, Appendix B).

| What the remote side can send | Tools |
|---|---|
| Rule updates it writes, deny removals included | 5 |
| A choice among updates the runtime or relay proposes | 25 |
| A decision only | 37 |
| Not determinable from the code | 3 |

The first row is about 7%, and Remote Control is in it. The claude.ai web and mobile apps answer through it, so the answering party is whoever controls that account, and its answer schema accepts every update type. For Remote Control the evidence is a reading of two releases. The authors' run through deployed software used an open-source relay (§II, §VII-B).

The [channels permission relay](../tools/claude/channels-permission-relay.md) is decision-only. Its verdict carries `allow` or `deny`, and "Neither verdict affects future calls" ([channels reference](https://code.claude.com/docs/en/channels-reference#relay-permission-prompts)).

## Saved answers in other agents

Some agents turn an "always" answer into a rule broader than the call asked about (§VII-E):

- opencode 1.19: "always" for `rm ./build.log` saves an allow for `rm *` that overrides an operator deny of `rm -rf *`. The authors note that its development branch has since adopted a safe way of saving answers (Appendix D).
- Gemini CLI 0.65.0 and 0.66.0, with saving across sessions enabled: "always" for `git tag` saves an allow for all of `git`, which outranks a lower-priority user-tier deny of `git push`.
- Codex 0.164.0 and 0.165.0: the forbidden rule held, but after a saved allow for `python3`, the next `python3` command ran outside the sandbox.
- VS Code's Copilot agent: a deny still wins. The authors checked this in source and did not run it.

## What to do now

The authors' interim advice is to keep deny rules where no update reaches: the managed tier, or a settings file passed on the command line. Also restrict the sandbox network to the hosts that managed settings allow (§VI). A managed-tier rule held in their runs (§VII-B). The command-line case rests on their reading of the binary (§IV-A).

Know the gaps:

- The network lock, `allowManagedDomainsOnly`, [applies only to commands inside the sandbox](https://code.claude.com/docs/en/sandboxing#disable-filesystem-isolation).
- The lock does not limit write paths. Even under an admin-required sandbox, `Edit` allow rules in `~/.claude/settings.json` [still apply unless a managed-only lock covers them](https://code.claude.com/docs/en/sandboxing#repository-settings-under-an-admin-required-sandbox), and an answer can write that file.
- [`allowManagedPermissionRulesOnly`](https://code.claude.com/docs/en/settings-reference#allowmanagedpermissionrulesonly) ignores `--settings` deny rules too, so use the managed tier if you set it. The preprint does not test this key.

List every party that can answer a prompt, including URL hooks and skills that declare hooks. A search for `updatedPermissions` can miss a hook that passes a remote answer through (§III, §VII-G).

## Design rules for runtimes and relays

The authors give three (§VIII):

1. Classify an update by its effect on what each reader of the policy refuses, sandbox included, whatever its syntax says.
2. Record who wrote each rule, out of the answering parties' reach.
3. When an update is refused, refuse the whole answer and show the operator the change. Applying the `allow` alone acts on an answer nobody gave.

Without authorship records, a safe runtime accepts only updates that keep every denied action denied (§V-B). For Claude Code that means refusing deny deletions and replacements. It also means refusing added allow rules that the sandbox reads, or keeping them for the session, so a relay's "always allow" for those rules lasts one session (§VI).

No authorship record makes an added network host safe, because it lifts the limit for every author. Refuse the addition, or read that list from a source no answer reaches. With records, a check that judges each step alone is still unsafe, because a party can copy a deny rule, delete the original, then delete its copy (§V-C).

The authors tested their repair by patching Claude Code binaries, and it held on the routes they tested. It is not a vendor feature. Their basic check still saved mode and directory changes, and keeping the operator's later prompts needs a stricter one (§VI, §VII-F).

## When the added risk is small

- Plugin and skill hooks already run with the operator's privileges. The new power matters most for answerers with no code on the host: relay services, SDK approvers, and services a plugin names as a URL hook (§III).
- Few plugins send updates. Of 2,227 fetched from the vendor's marketplace, two did, and both let a remote side choose among the runtime's suggestions (§VII-G, Appendix B).
- The evidence is one preprint at version 1. Its runs used Linux, and macOS was not run (§VIII).

## Example

This managed settings file applies the interim advice. The two deny rules come from the operator settings in the authors' runs (Appendix B). The sandbox keys follow the [managed sandbox](https://code.claude.com/docs/en/sandboxing#enforce-sandboxing-with-managed-settings) and [network lock](https://code.claude.com/docs/en/settings-reference#sandbox-network-allowmanageddomainsonly) docs, and the hosts are the vendor's sample. We assembled the file and have not run it. A `./` path [resolves against the current directory](https://code.claude.com/docs/en/permissions#read-and-edit).

```json
{
  "permissions": {
    "deny": ["Read(./.env)", "Bash(curl *)"]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "network": {
      "allowManagedDomainsOnly": true,
      "allowedDomains": ["github.com", "*.npmjs.org"]
    }
  }
}
```

After you deploy it, run `/status` and check that `Setting sources` includes `Enterprise managed settings`. No answer can write this tier. An answer can still write allow rules, modes, and directories to other settings files.

## Key Takeaways

- Where a route forwards policy updates, whoever answers through it can do more than decide one call: they can delete deny rules in user, project, or local settings.
- Put deny rules in the managed tier and lock sandbox domains there. The domain lock does not limit write paths, and answers can still save modes and directories.
- Judge an update by what it makes the permission check or sandbox stop refusing. By that test, an added `Edit` or `WebFetch` allow rule is a grant.
- A channels verdict carries only allow or deny, so it cannot attach a rule change.
- Treat the attack evidence as one preprint: tested on Linux, reported still working on 2.1.327 and not reproduced here, with a repair that is the authors' binary patch.

## Related

- [Six-Shape Approval Response Taxonomy](../patterns/agent-design/approval-response-taxonomy.md) — `updatedPermissions` used as a legitimate "approve and remember"
- [Evidence-Based Allowlist Auto-Discovery](evidence-based-allowlist-auto-discovery.md) — a hook that writes allow rules through the same field
- [A PermissionRequest Rewrite Can Move a Command Outside the Sandbox](permissionrequest-rewrite-sandbox-exit.md) — what the rewritten-input half of an answer can do
- [A Containment Floor for Agent Self-Configuration](agent-self-config-field-classes.md) — refusing config writes by field class at the write site
- [An Explicit Update Boundary for Agent Self-State](self-state-update-boundary.md) — why the write alone cannot show who is authorized to make it
- [One-Way Settings](one-way-settings.md) — keys that accept writes in one direction only
- [Channels Permission Relay](../tools/claude/channels-permission-relay.md) — a remote approval path whose verdict is allow or deny
