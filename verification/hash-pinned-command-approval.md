---
title: "Hash-Pinned Command Approval for Non-Interactive Plugin Installs"
term: "Hash-Pinned Command Approval"
description: "Claude Code 2.1.271 accepts the sha256 of a command a previous --json run displayed, so an unattended install approves the string that was read instead of whatever the catalog serves next."
tags:
  - testing-verification
  - automation
  - claude
aliases:
  - hash-pinned command approval
  - digest-bound install approval
applies_to: "claude-code@2.x"
last_reviewed: 2026-09-17
status: current
maturity: emerging
---

# Hash-Pinned Command Approval for Non-Interactive Plugin Installs

> `claude plugin install` and `claude plugin update` accept a `sha256` of the command a previous `--json` run displayed, in place of `-y`.

`--accept-command` landed in Claude Code 2.1.271 on 14 September 2026, on `claude plugin install` and `claude plugin update` ([Claude Code changelog](https://code.claude.com/docs/en/changelog#2-1-271)). Four conditions decide whether it reaches your pipeline. You need v2.1.271 or later for the flag, and v2.1.268 or later for the `--json` run that produces the digest. You have to run it from your own terminal, because both `-y` and `--accept-command` have no effect inside a Claude Code session. The plugin has to declare a command. And the acceptance covers one command, one plugin, and one marketplace catalog together ([Claude Code plugins reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-install)).

Two things declare a command: a [`command` source](https://code.claude.com/docs/en/plugins/marketplace-reference#command-plugin-source), which runs a locally installed tool that prints the plugin directory's absolute path, and a [`headersHelper`](https://code.claude.com/docs/en/plugins/host-marketplace#authenticate-archive-downloads), which prints the HTTP headers that authenticate an archive download. Where an entry declares neither, no command is displayed and no `sha256` is reported, so the flag has nothing to accept.

## Where the gap sits

Between two invocations, not inside one. Under `-y`, Claude Code accepts "the displayed install command" without the prompt ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-install)). For a plugin entry's `headersHelper`, the documentation goes further: Claude Code "runs only the command it showed, for the archive URL it showed. If the entry's command or archive URL changed in between, Claude Code refuses the install or update. A change in the query string alone doesn't count" ([host a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace#how-users-accept-a-headershelper-command)). For a `command` source or a `headersHelper`, Claude Code "first prints the command and asks `Run this command now? [y/N]`" ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-install)). A script has no one to answer that prompt ([install plugins](https://code.claude.com/docs/en/plugins/install#install-from-your-shell)). Without a TTY and without `-y` or `--accept-command`, the install is refused with exit code `1` ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-install)).

Automation pulls the two halves apart. A pipeline inspects with `--json`, a person or an agent reads the command out of that output, and a later invocation approves. `-y` on that later invocation accepts whatever the catalog declares at that moment, and nothing connects it to what was read. The digest is the connection.

## What the acceptance covers

The inspect run supplies the digest. With `--json` the last line of stdout is one JSON object, and a script parses only that line because Claude Code "prints any command the marketplace declares ahead of it". When a run displays a command and does not run it, the `failed` result "also carries a `shownCommand` object. Its fields include the command as displayed, the plugin it belongs to, and the command's `sha256`" ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command)).

The approving run then applies a documented equality test: "The `sha256` counts as acceptance for exactly that command, plugin, and marketplace catalog. If any of them changed since the command was displayed, Claude Code doesn't accept the `sha256` and shows the command again. A change that the run's own marketplace refresh fetches also counts as such a change." The flag cannot be combined with `-y` ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command)).

A mismatch reports rather than retries. When `shownCommand.acceptCommandMatched` is `false`, "the `sha256` you passed doesn't match the command now displayed", and the documented next step is one sentence: "Review that command before re-running with its `sha256`" ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command)).

## What the pin does not reach

It identifies a command string, and the same documentation states that the accepted command keeps running and can produce different content each time. Claude Code re-runs a command source's command "Once per session for each enabled command-sourced plugin, in the background, shortly after the session starts", and "When the command's hashed output has changed, Claude Code installs the result as a new version and reloads it in the running interactive session" ([plugin loading reference](https://code.claude.com/docs/en/plugins/loading#when-a-command-source-re-runs)). The marketplace `version` field does not pin it either: the marketplace entry's `version` "is ignored for command sources" ([plugin loading reference](https://code.claude.com/docs/en/plugins/loading#how-claude-code-computes-the-version)).

The reviewable artifact is one command line. Claude Code "shows users the whole string for review before it runs", and the schema caps it at "printable ASCII, at most 500 characters, with no run of four or more spaces" ([marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference#command-plugin-source)). Pinning it says what will run. It says nothing about what the tool on the other end prints tomorrow.

## Why it works

The digest gets re-checked before the approval is spent, which drops the assumption `-y` makes: that the command to be run now is the command that was read earlier ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-install)).

Terraform binds an approval the same way and says why. Passing a saved plan file to `terraform apply` performs the operations in that plan "without prompting you for confirmation", and `-auto-approve` is ignored in that mode "because Terraform interprets the act of passing the plan file as the approval" ([Terraform CLI: apply](https://developer.hashicorp.com/terraform/cli/commands/apply)). One difference is load-bearing. Terraform carries the reviewed artifact itself; `--accept-command` carries only a hash of it, so the approving run has to re-derive the same command before it can recognize the digest. That is why a catalog refresh breaks the match.

## When this backfires

- Inside a Claude Code session. The documentation says to pass `--accept-command` "from your own terminal, because the flag has no effect inside a Claude Code session" ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command)). An agent working in-session gains nothing here and cannot supply the approval for the operator.
- A benign catalog change between the two runs. A change that "the run's own marketplace refresh fetches" invalidates the acceptance ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command)), so an ordinary upstream release stops an unattended run and sends it back to a person. pip records the same friction for hash-checking mode, where requirements must be pinned because that "prevents a surprising hash mismatch upon the release of a new version that matches the requirement specifier" ([pip: Secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/)).
- Fleets below the version floor. `--accept-command` needs v2.1.271 or later and `--json` needs v2.1.268 or later ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-install)). An older CLI falls back to `-y`, and a mixed-version fleet gets the weaker behavior without anything announcing it.
- Organizations that can delete the capability instead. Set to `true`, the managed setting `disableCommandPluginSources` means Claude Code "never runs the command, doesn't install or update command-sourced plugins, and stops loading the ones already installed" ([settings reference](https://code.claude.com/docs/en/settings-reference#disablecommandpluginsources)). Where policy allows that, removing the decision beats mediating it.

## Example

The inspect run prints the command, declines to run it, and leaves the digest on the last line of stdout:

```bash
claude plugin install formatter@my-marketplace --json
```

The approving run names that digest in place of `-y`:

```bash
claude plugin install formatter@my-marketplace \
  --accept-command 9f2c41b8e7d05a63c1ba84f7e2903d5c6a8be14f70d92c3ba5e6f81d4c27a09b
```

Between the two, a person reads the command string out of `shownCommand`.

## Key Takeaways

- Split your provisioning step in two and pass the digest across. Under `-y` alone, nothing ties the approving run to the command an earlier run displayed ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-install)).
- Refresh the digest whenever you refresh the catalog. The acceptance covers command, plugin, and catalog together, so the two inspect-and-approve runs have to sit close enough that nothing moves between them ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command)).
- Handle `acceptCommandMatched: false` as a review step, not a retry. The documentation asks you to review the command before re-running with its new `sha256` ([plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command)).
- Budget for the halt. A pinned approval converts a legitimate upstream change into a stopped pipeline, the cost pip records for the same class of control ([pip: Secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/)).

## Related

- [Pre-Install Plugin Transparency: Capability Inventory and Cost Projection](../standards/pre-install-plugin-transparency.md) — what a plugin will install, disclosed before the install decision
- [The Post-Authorization Execution Trust Gap in Remote MCP](../security/post-authorization-execution-trust-gap.md) — the same interval between authorization and execution, on the provider side of a protocol
- [Deferred Permission Pattern](../patterns/agent-design/deferred-permission-pattern.md) — collecting a human approval outside a headless session
- [Enterprise-Managed Plugin Governance for Agent CLIs](../security/enterprise-managed-plugin-governance.md) — the managed-settings layer that can remove plugin capabilities outright
- [Agent-Driven Deployment: What to Delegate and What to Gate](../workflows/agent-driven-deployment.md) — where an approval boundary belongs in a pipeline an agent drives
