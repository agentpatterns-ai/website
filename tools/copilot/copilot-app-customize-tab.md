---
title: "Copilot App Customize Tab vs Repo Configuration Files"
description: "The Copilot app's Customize tab installs MCP servers, plugins, skills, and canvases outside the repo, while the cloud agent installs plugins only from the committed settings file."
tags:
  - copilot
  - instructions
aliases:
  - Copilot app Customize tab
  - Copilot app plugin install
applies_to: "copilot@1.x"
last_reviewed: 2026-08-26
status: current
---

# Copilot App Customize Tab vs Repo Configuration Files

> The Customize tab installs customization outside the repository, and the cloud agent installs plugins only from the committed `.github/copilot/settings.json`.

The Customize tab in the GitHub Copilot app is a discovery and install surface, not an editor for `.github/copilot-instructions.md`. It "allows you to discover and manage MCP servers, plugins, skills, and canvases in one place" ([GitHub Docs — Customizing the GitHub Copilot app](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app)), and it reached general availability on 2026-08-25 ([GitHub Changelog, 2026-08-25](https://github.blog/changelog/2026-08-25-github-copilot-app-customize-tab-is-generally-available/)).

Customization does not move out of the repository into it. The flow runs the other way. "Any skills configured for your repositories or Copilot CLI are automatically available in the GitHub Copilot app," and GitHub prints the same sentence for MCP servers ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app)). Your reviewed files arrive in the app on their own. So the [file-first convention](copilot-instructions-md-convention.md) survives this release intact, and the useful question is narrower: which app-side state has no repository copy at all.

## The two surfaces with no repo copy

The first is the plugin install path, and it differs by client. In Copilot cloud agent "you install plugins declaratively by adding them to the `enabledPlugins` field of the repository's `.github/copilot/settings.json` file." In the app you "click **Customize**, then click **Plugins** to browse marketplaces and install plugins" ([GitHub Docs — About GitHub Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins)). A plugin can carry [custom agents, skills, hooks, and MCP and LSP server configurations](custom-agents-skills.md), so one click can add a hook that no commit records. The app also accepts a custom marketplace from any "GitHub repository or Git URL" ([GitHub Docs](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app)).

The second is instruction editing, which lives in app settings rather than the Customize tab. The app carries a global "App instructions" field and a per-repository "Instructions" field, and the repository one applies "to every session for the selected repository" ([GitHub Docs — Customizing the GitHub Copilot app](https://docs.github.com/en/copilot/how-tos/github-copilot-app/customize-github-copilot-app), which carries the current menu path). That is a repository-scoped instruction with no diff and no reviewer.

## Which one wins

GitHub has not published an answer for the app. The documented order runs personal instructions first, then repository instructions, then organization instructions, and it is scoped to the GitHub website ([GitHub Docs — Response customization](https://docs.github.com/en/copilot/concepts/prompting/response-customization)). The per-environment support reference covers GitHub.com, VS Code, Visual Studio, JetBrains IDEs, Eclipse, Xcode, and Copilot CLI, with no GitHub Copilot app section ([GitHub Docs — Support for different types of custom instructions](https://docs.github.com/en/copilot/reference/custom-instructions-support)).

Treat instructions as additive until GitHub says otherwise. Where precedence is documented, it does not discard the loser: "all sets of relevant instructions are provided to Copilot" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/prompting/response-customization)). A conflicting app-side instruction muddies the reviewed file rather than replacing it. That is harder to spot than an override.

## Why it works

Keeping configuration in the repository buys reach and review from one property, and GitHub's own table says so: manual repository configuration scores scope "Single repository" and versioning "Git history," against a plugin's "Any project" and "Marketplace versions" ([GitHub Docs — About GitHub Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins)). Git history is branch protection applied to configuration, and GitHub gives exactly that reason for the enterprise policy file: "Because the configuration lives in a Git repository, all changes to plugin standards are tracked, auditable, and reviewable through pull requests" ([GitHub Docs — Enterprise-managed plugin standards](https://docs.github.com/en/copilot/concepts/agents/about-enterprise-plugin-standards)).

Reach is the half people miss. "In Copilot cloud agent, you install plugins declaratively by adding them to the `enabledPlugins` field of the repository's `.github/copilot/settings.json` file" ([GitHub Docs — About GitHub Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins)), so a plugin installed through the Customize tab does not follow the work when you delegate it. Instructions are a separate matter: the cloud agent also reads organization instructions, which live in Copilot settings rather than in a file ([GitHub Docs — Custom instructions support](https://docs.github.com/en/copilot/reference/custom-instructions-support)).

## When this backfires

- Insisting on files while ignoring the tab costs you discovery. GitHub scores repository configuration as discoverable only by "Searching repositories," and a server you never find cannot be committed.
- The Installed view is the only place the effective configuration appears as one list. Reproducing a bad agent output means accounting for repo files, CLI settings, enterprise defaults, and app installs, and only the first is in your checkout.
- Central control over the app path is enterprise-tier. `managed-settings.json` defines known marketplaces and default-enabled plugins for "all users on the enterprise's Copilot plan" ([GitHub Docs — Enterprise-managed plugin standards](https://docs.github.com/en/copilot/concepts/agents/about-enterprise-plugin-standards)), so a Business or individual team gets no equivalent gate.
- A GUI customization editor is not new here. JetBrains IDEs already ship an Agent Customizations editor for workspace and personal customizations ([GitHub Docs — Support for different types of custom instructions](https://docs.github.com/en/copilot/reference/custom-instructions-support)), so treating 2026-08-25 as the moment the model changed misreads it.

## Example

The cloud-agent test tells you whether a customization exists only in your app. Delegate a task that needs it and see whether the delegated run has it.

```jsonc
// .github/copilot/settings.json - the only plugin config the cloud agent reads
{
  "enabledPlugins": ["my-org-plugin"],
  "extraKnownMarketplaces": ["my-org/copilot-marketplace"]
}
```

If a plugin works in your app session and the cloud agent behaves as though it is absent, it is absent. `extraKnownMarketplaces` in the same file is how a marketplace you added through the app reaches the agent ([GitHub Docs — About GitHub Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins)).

## Key Takeaways

- The Customize tab discovers and installs. It does not edit `.github/copilot-instructions.md`, and repository skills and MCP servers reach the app on their own.
- Browse in the app, then commit what you keep. An app-only install is invisible to reviewers and to the cloud agent.
- GitHub documents no precedence for the app's global and per-repository instruction fields. Assume they are added to the reviewed file, not substituted for it.
- The per-repository Instructions field is the sharpest edge: one developer can change every session for a repository without a commit.
- Below the enterprise plan there is no central control over which marketplaces and plugins developers install.

## Related

- [GitHub Copilot Dedicated App as Agent-First Surface](copilot-dedicated-app.md) — the desktop client the Customize tab sits in
- [GitHub Copilot App Slash Commands and What They Change](slash-commands-copilot-app.md) — the sibling app surface, and the commands that load your customization
- [copilot-instructions.md as a Repo-Level Instruction Convention](copilot-instructions-md-convention.md) — the file this tab does not replace
- [GitHub Copilot Custom Agents and Skills Extensibility Guide](custom-agents-skills.md) — what a plugin bundles, and the repo paths each part lives at
- [GitHub Copilot MCP Integration for AI Agent Development](mcp-integration.md) — the customization type the tab surfaces as trending and by category
