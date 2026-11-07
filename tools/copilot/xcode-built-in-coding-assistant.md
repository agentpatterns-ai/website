---
title: "GitHub Copilot in Xcode's Built-In Coding Assistant"
description: "Use Copilot through Xcode's built-in coding assistant in public preview. Check setup requirements and distinguish this path from the separate Xcode extension."
tags:
  - copilot
  - workflows
applies_to: "xcode@27.3"
last_reviewed: 2026-11-06
status: current
---

# GitHub Copilot in Xcode's Built-In Coding Assistant

> Copilot runs in Xcode's built-in coding assistant through a public preview, alongside the existing separate Copilot extension option.

GitHub Copilot's built-in Xcode integration is a public preview starting with Xcode 27.3 beta. It supports all Copilot plans. The existing GitHub Copilot for Xcode extension remains a separate integration ([GitHub announcement](https://github.blog/changelog/2026-11-04-github-copilot-is-now-available-in-xcodes-coding-assistant/)).

## Setup and sign-in

Use a Mac running macOS Tahoe 26.6 or later. Apple lists that requirement in its [Xcode 27.3 beta release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_3-release-notes).

Open Xcode > Settings > Intelligence to set up Copilot. Apple's general agent setup uses Get, then Install, followed by the Account row's More button for sign-in. Complete the account flow shown by Xcode and the browser ([coding intelligence setup](https://developer.apple.com/documentation/xcode/setting-up-coding-intelligence)).

Enabled agents can use Xcode capabilities such as building and testing. The setup documentation also explains that an agent may access project files and other information while processing a request ([Apple setup reference](https://developer.apple.com/documentation/xcode/setting-up-coding-intelligence)). Review the integration's access in the actual project before delegating a change.

## Keep editor-specific configuration explicit

Apple documents command and tool permissions under Intelligence settings. Its customization guide also supports agent-specific configuration files and plug-ins, with configuration scoped to agents launched in Xcode ([agent customization](https://developer.apple.com/documentation/xcode/extending-and-customizing-agents)).

That general capability does not establish Copilot-specific support for every repository-instruction format or custom-agent field. The cited launch announcement and Apple pages do not provide a Copilot support matrix. Do not infer VS Code or CLI parity from the shared Copilot name.

For a mixed-editor team, record the integration used in review evidence. Check these questions in a disposable project:

- Did the expected repository instruction affect the task?
- Does the intended custom agent appear and use its declared tools?
- Can the coding assistant build and test the target scheme?
- Which permission requests reach the user?

Treat these as acceptance checks, not as features established by this page. A passing check on the separate extension does not verify the built-in assistant.

## Key Takeaways

- Name the built-in assistant or extension when reporting Xcode behavior.
- Keep the beta and macOS requirements beside setup instructions.
- Verify repository instructions and custom agents on this integration before relying on cross-editor behavior.

## Related

- [Copilot Repository Instructions](copilot-instructions-md-convention.md) — the repository-level convention to verify
- [Copilot Custom Agents and Skills](custom-agents-skills.md) — customization concepts across Copilot hosts
- [Copilot Agent Mode](agent-mode.md) — compare the editor execution loop
