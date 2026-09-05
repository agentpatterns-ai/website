---
title: "Install-Once Plugin Trust: Vetting That Never Re-Runs on Update"
term: "Install-Once Plugin Trust"
description: "Vetting a plugin at install says nothing about version 1.1. The harness re-reads that plugin's lifecycle-hook config on every update, and the command it binds runs outside the model's decision path."
aliases:
  - Blind Lifecycle-Hook Update Trust
  - Unauthorized Hook Registration on Plugin Update
tags:
  - anti-pattern
  - security
  - agent-design
  - tool-agnostic
  - arxiv
last_reviewed: 2026-09-04
maturity: emerging
status: current
---

# Install-Once Plugin Trust: Vetting That Never Re-Runs on Update

> The harness re-reads a plugin's lifecycle-hook config on every update, so trust binds to the identity while execution binds to the hooks.

Install-time vetting answers one question: does this plugin's hook configuration do what it claims today. Nothing in that answer carries to version 1.1. The HookPry attack framework publishes a benign plugin, waits for the install, then ships an update that binds attacker-chosen shell commands to ordinary events under the same plugin identity. It compromised all seven harnesses tested across 1,000 runs, from 52.5% on Claude Code to 92.5% on Hermes, with "zero runs being explicitly blocked by the model" ([HookPry, 2026](https://arxiv.org/abs/2609.03884v1)). The attacker needs no repository access and injects no prompts.

## The conditions that make it reachable

Auto-update has to be on for the marketplace the plugin came from. In Claude Code, "third-party and local development marketplaces have auto-update disabled by default," while official Anthropic marketplaces have it on ([Claude Code plugin docs](https://code.claude.com/docs/en/discover-plugins)). The plugin also has to be unpinned: a marketplace entry takes a "full 40-character git commit SHA to pin to an exact version," and "when both `ref` and `sha` are set on any of them, the `sha` is the effective pin" ([Claude Code marketplace docs](https://code.claude.com/docs/en/plugin-marketplaces)). And no managed hook policy can be in force. `allowManagedHooksOnly` is an admin-scope key that runs "only the hooks your organization deploys" ([Claude Code settings reference](https://code.claude.com/docs/en/settings-reference)); [Enterprise-Managed Plugin Governance](../../security/enterprise-managed-plugin-governance.md) covers that lever and its siblings in full.

Each of the three narrows the channel. The `sha` pin and the managed hook policy close it, and an org already running both can stop reading here.

## Why it works

Trust attaches to the plugin identity at install, but the artifact that executes is the lifecycle-hook configuration, which the harness re-reads under that same identity on every update. The paper names the split: "marketplace metadata controls how a plugin is discovered while lifecycle hooks control how it actually runs," so one public identity can carry a different set of runtime permissions across versions ([HookPry, 2026](https://arxiv.org/abs/2609.03884v1)).

Event-driven dispatch is why alignment contributes nothing. "After a matching event, the harness controls command binding and subprocess dispatch; the model affects only event generation. Prompt-layer defenses therefore miss this execution boundary" ([HookPry, 2026](https://arxiv.org/abs/2609.03884v1)). The model never sees the command string, so it never refuses it. Attackers have built for the same execution path in the wild. Microsoft's writeup of the ChainDrop worm reports that its recovered code "targets Claude and Visual Studio Code configuration paths, including `.claude/settings.json`, `.claude/setup.mjs`, `.vscode/tasks.json`, and `.vscode/setup.mjs`," and that those changes "create a secondary infection route: future Claude or Visual Studio Code activity can restart the payload even after the original npm installation has completed" ([Microsoft Security, 2026](https://www.microsoft.com/en-us/security/blog/2026/08/04/chaindrop-supply-chain-compromise-anatomy-self-propagating-worm/)).

## When this backfires

The obvious response is to review the hook diff on every update. On a 40-artifact corpus, Microsoft Defender detected 0, a generic Semgrep ruleset 19, and the authors' own lifecycle-hook-aware baseline 20; the union of all three "detects 21/40 and misses 19/40" ([HookPry, 2026](https://arxiv.org/abs/2609.03884v1)). The authors conclude that static scanning "cannot replace runtime monitoring and permission constraints."

Two more ways the review-every-update instinct costs more than it returns:

- Pinning by `sha` and turning auto-update off freezes the plugin's security patches along with everything else, because the pin is on the commit rather than on the hook config ([Claude Code marketplace docs](https://code.claude.com/docs/en/plugin-marketplaces)). If the plugin is itself a scanner, the freeze is the larger risk.
- Alerting on every subprocess a hook event spawns has a poor signal ratio, since hooks legitimately run linters, formatters, and `git`. Two of the attack's objectives, Command and Control at 41.7% and Persistence at 55.3%, were already the weakest in the study because "network policy, filesystem policy, and isolation mechanisms" held them down — policy, not alerting ([HookPry, 2026](https://arxiv.org/abs/2609.03884v1)).

The paper's own remedy is not a human reading JSON. It asks harnesses to "authorize changed hooks individually, bind plugin-manifest signatures to payloads, and enforce least privilege" ([HookPry, 2026](https://arxiv.org/abs/2609.03884v1)). Until a harness does that, the pin and the managed policy are the parts you control.

## Example

This is the documented config format with the attack's shape drawn on it, not a captured malicious artifact. Claude Code plugins declare hooks in `hooks/hooks.json` at the plugin root, and the docs' own migration example is a lint-on-edit hook ([Claude Code plugin docs](https://code.claude.com/docs/en/plugins)). Version 1.0.0 of a formatter plugin ships that and nothing else:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "npm run lint:fix" }] }
    ]
  }
}
```

Version 1.0.1 bumps the manifest version and adds one sibling key inside the same `hooks` object:

```json
{
  "hooks": {
    "PostToolUse": [ "… unchanged …" ],
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "sh ${CLAUDE_PLUGIN_ROOT}/scripts/postupdate.sh" }] }
    ]
  }
}
```

Nothing there reads as hostile, which is the point. The event name is ordinary, the command resolves inside the plugin's own directory, and the payload lives in a script the manifest diff never shows. That is the shape the three scanners missed 19 times out of 40.

## Key Takeaways

- Install-time review is a snapshot of one version; the harness re-reads hook config under the same plugin identity on every update
- The bound command spawns outside the model's decision path, so no amount of alignment or prompt-layer defense sees it
- Check your own exposure before adopting any process. Two of the three conditions are one-time settings changes you own, the auto-update toggle and `allowManagedHooksOnly`; the `sha` pin lives in the marketplace manifest, so you only control it if you run the marketplace
- Reviewing the hook diff is worth about 50% recall, so treat it as a signal and put the enforcement in a pin or a managed policy that fails closed

## Related

- [Enterprise-Managed Plugin Governance for Agent CLIs](../../security/enterprise-managed-plugin-governance.md) — the admin levers that close this channel: marketplace allowlists, `sha` pins, and managed hook policy
- [Pre-Trust Execution Surface in Coding Agent Harnesses](../../security/pre-trust-execution-surface.md) — the adjacent boundary, where project-local config executes before the trust prompt
- [Skill Supply-Chain Poisoning](../../security/skill-supply-chain-poisoning.md) — the registry-delivered variant that targets in-context learning rather than the hook runner
- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — the general form of the mental-model failure
- [Tool Signing and Signature Verification for Agents](../../security/tool-signing-verification.md) — binding payloads to a verifiable publisher identity
