---
title: "Sensitive Terminal Prompt Interception"
description: "Intercept password and verification-code prompts inside the terminal so an agent never sees the secret — confirm in default mode, cancel in auto-approve mode."
tags:
  - security
  - tool-agnostic
last_reviewed: 2026-06-12
maturity: established
---

# Sensitive Terminal Prompt Interception

> Detect credential prompts in an agent-driven terminal and route input to a human's TTY (or cancel the command), keeping secrets out of the model's context.

Sensitive-prompt interception works on the interactive TTY path. When an agent runs a shell command (`sudo`, `ssh`, `gh auth login`, `npm publish` with OTP) and the command writes a credential prompt, the harness recognizes the prompt string. It then substitutes a synthetic "user is typing in terminal" message and routes keystrokes only to the human-controlled TTY. The model's transcript never contains the secret. The pattern covers only real TTY prompts — not credentials read from files, returned by MCP tools, or pasted into chat.

## How it works

Three components run in sequence:

1. Prompt detection. The harness watches terminal output for vendor patterns: `Password:`, `passphrase`, `Verification code`, `2FA`, `OTP`, and named-vendor strings (`sudo`, `ssh`, `gpg`, `gh auth`, `npm publish`). Detection is heuristic — no protocol-level "this prompt wants a secret" signal exists at the TTY layer.
2. Mode-conditional routing.
   - Default mode: the harness pauses the command and surfaces a confirmation dialog asking the user to focus the terminal and type the secret directly. VS Code 1.121 ships this: "chat shows a confirmation dialog that lets you focus the terminal to enter the secret directly there" ([VS Code 1.121 release notes](https://code.visualstudio.com/updates/v1_121#_sensitive-terminal-prompts-stay-in-the-terminal)).
   - Auto-approve mode: the harness cancels the command and tells the model not to retry or request the secret ([release notes](https://code.visualstudio.com/updates/v1_121#_sensitive-terminal-prompts-stay-in-the-terminal)).
3. Transcript scrub. The agent sees a sanitized stand-in for the prompt and any stdin echoes, so a downstream summarizer, replay, or injected instruction cannot reconstruct what was typed.

Cancel-in-auto-approve is the only safe choice without a human. A dialog with no one to confirm it would deadlock, or fall through to the agent typing the secret.

## Cross-tool status

| Tool | Status |
|------|--------|
| VS Code Copilot Chat (1.121+) | Built in: confirm in default, cancel in auto-approve ([release notes](https://code.visualstudio.com/updates/v1_121#_sensitive-terminal-prompts-stay-in-the-terminal)) |
| Claude Code (Bash tool) | Not built in. Docs recommend host-side `sanitize_output` regex masking ([Bash tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool)). Community workaround: hooks with `sed`-based redaction ([nopeek](https://scottspence.com/posts/nopeek-keep-secrets-out-of-claude-code)). Open requests: [#25053](https://github.com/anthropics/claude-code/issues/25053), [#29434](https://github.com/anthropics/claude-code/issues/29434). |
| Cursor (terminal) | Not documented; published docs describe no prompt-interception layer ([Cursor terminal docs](https://cursor.com/docs/agent/tools/terminal)). |

Stdout regex redaction is strictly weaker. By the time output is filtered the secret is already in a harness-controlled buffer, and anything bypassing the regex (custom prompt string, non-English locale, base64) leaks through.

## Why it works

Once a secret enters the serialized terminal output the model reads, it is indistinguishable from any other token: summarizable, echoable into a tool argument, persistable, replayable. Interception inserts a control layer between the PTY prompt and the model stream. Detection fires before the read completes, a synthetic message is substituted, and stdin bytes route only to the human's TTY. The same trust-boundary logic motivates Anthropic's `sanitize_output` recommendation ([Bash tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool)). Industry framing has converged on "any secret that has touched a context window should be treated as compromised" ([Cequence](https://www.cequence.ai/blog/ai/even-the-best-ai-agents-leak-secrets-prompt-injection-is-why/)).

The threat is documented. "Comment and Control" showed Claude Code Security Review, Gemini CLI Action, and GitHub Copilot Agent exfiltrating repository secrets via a single PR-title injection ([VentureBeat](https://venturebeat.com/security/ai-agent-runtime-security-system-card-audit-comment-and-control-2026)). "Your AI, My Shell" reports a 68.2% credential-access success rate across leading agentic coding editors ([arxiv 2509.22040](https://arxiv.org/html/2509.22040v1)).

## When this backfires

- MCP tool injection bypasses the layer. A compromised MCP server can return a secret directly in a tool result. Pair with [MCP runtime control](mcp-runtime-control-plane.md) and [tool signing](tool-signing-verification.md).
- Non-interactive credential reads. `cat .env`, `aws configure get …`, `gh auth token` — no prompt, just stdout. Only sensitive-path blocking ([protecting sensitive files](protecting-sensitive-files.md)) helps.
- Heuristic miss and false positives. A custom `Enter unlock token:` may not match, and a legitimate prompt may get canceled. Cursor users hit the second mode when sudo stopped working in agent terminals ([Cursor forum regression](https://forum.cursor.com/t/regression-agent-terminals-no-longer-support-sudo-or-interactive-input/136719)).
- Auto-approve deadlock. In unattended runs, cancellation forces the agent to give up or invent a recovery. A poorly written agent may retry and defeat the purpose.
- Out-of-band exfiltration. Interception protects the transcript, not the host. Screen capture, accessibility tooling, and clipboard history still see the typed secret.
- Pre-existing contamination. If a `.env` was pasted earlier or a prior tool call read a credential, the secret is in context regardless.
- The path may not need to exist. Browser PKCE or OAuth device-code flows keep the secret off the terminal ([CLI auth methods](https://blog.logto.io/cli-authentication-methods)). When redesigning auth, prefer credential-broker injection ([secrets management](secrets-management-for-agents.md), [scoped credentials via proxy](scoped-credentials-proxy.md)).

## Example

VS Code 1.121 default mode, walked through with `gh auth login`:

1. Agent runs `gh auth login --hostname github.com --git-protocol https` in a chat-spawned terminal.
2. The command prints `Enter your authentication token:` and waits on stdin.
3. The harness pattern-matches the prompt, pauses the command, and surfaces a confirmation dialog asking the user to focus the terminal.
4. The user types the token into the terminal pane. VS Code routes keystrokes to the PTY only — the harness does not capture them into the chat transcript.
5. The command completes. The agent's tool result records "command completed" without the token.

In auto-approve mode, step 3 cancels the command instead and the agent receives an explicit instruction not to retry ([VS Code 1.121 release notes](https://code.visualstudio.com/updates/v1_121#_sensitive-terminal-prompts-stay-in-the-terminal)).

## Key Takeaways

- Interception applies only to interactive TTY prompt paths — passwords, passphrases, PINs, verification codes; it does nothing for secrets read from files or returned by MCP tools.
- The two safe behaviours are confirm-in-terminal (default mode) and cancel-the-command (auto-approve) — never let the agent type the secret itself.
- Stdout regex redaction is a fallback, not a substitute: by the time output is filtered the secret has already been in an agent-controlled buffer.
- Detection is heuristic and brittle — expect false positives on legitimate interactive flows and false negatives on non-standard prompts; instrument both failure modes.
- The structurally better fix is to remove credentials from the TTY path entirely — browser PKCE, device-code, or [credential-broker injection via a scoped-credentials proxy](scoped-credentials-proxy.md) — and treat interception as defence-in-depth for cases where the prompt cannot be designed away.

## Related

- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md)
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
