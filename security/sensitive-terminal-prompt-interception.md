---
title: "Sensitive Terminal Prompt Interception"
description: "Intercept password and verification-code prompts inside the terminal so an agent never sees the secret — confirm in default mode, cancel in auto-approve mode."
tags:
  - security
  - tool-agnostic
---

# Sensitive Terminal Prompt Interception

> Detect password, passphrase, PIN, and verification-code prompts inside an agent-driven terminal, route input to a human-controlled TTY in default mode, and cancel the command in auto-approve mode — keeping the secret out of the model's context.

Sensitive-prompt interception applies on the interactive TTY path: when an agent runs a shell command (`sudo`, `ssh`, `gh auth login`, `npm publish` with OTP) and the command writes a credential prompt to the terminal, the harness recognises the prompt string before the agent reads it, swaps in a synthetic "user is typing in terminal" message, and routes the actual keystrokes only to the human-controlled TTY. The model's transcript never contains the secret. The pattern applies only when a real TTY prompt is in the loop — it does not cover credentials read from files, returned by MCP tool calls, or pasted into chat earlier in the session.

## How It Works

Three components run in sequence:

1. **Prompt detection.** The harness watches captured terminal output for vendor patterns: `Password:`, `passphrase`, `Verification code`, `2FA`, `OTP`, and named-vendor strings (`sudo`, `ssh`, `gpg`, `gh auth`, `npm publish`). Detection is heuristic — there is no protocol-level "this prompt wants a secret" signal at the TTY layer.
2. **Mode-conditional routing.**
   - **Default mode**: the harness pauses the command, surfaces a confirmation dialog, and asks the user to focus the terminal and type the secret directly. The keystrokes never enter the harness's serialisation step. VS Code 1.121 ships exactly this behaviour: "chat shows a confirmation dialog that lets you focus the terminal to enter the secret directly there" ([VS Code 1.121 release notes](https://code.visualstudio.com/updates/v1_121#_sensitive-terminal-prompts-stay-in-the-terminal)).
   - **Auto-approve mode**: the harness cancels the command and instructs the model not to retry or request the secret. VS Code 1.121 documents this as: "In auto-approve flows, VS Code cancels the command and tells the model not to retry or request the secret" ([VS Code 1.121 release notes](https://code.visualstudio.com/updates/v1_121#_sensitive-terminal-prompts-stay-in-the-terminal)).
3. **Transcript scrub.** The agent sees a sanitised stand-in message in place of the prompt and any subsequent stdin echoes — so a downstream summariser, replay, or injected instruction cannot reconstruct what was typed.

Cancel-in-auto-approve is the only safe choice when there is no human present: a confirmation dialog with no one to confirm it would either deadlock the run or, worse, fall through to letting the agent type the secret.

## Cross-Tool Status

| Tool | Status |
|------|--------|
| VS Code Copilot Chat (1.121+) | Built in: confirm in default, cancel in auto-approve ([release notes](https://code.visualstudio.com/updates/v1_121#_sensitive-terminal-prompts-stay-in-the-terminal)) |
| Claude Code (Bash tool) | Not built in. "Password prompts" listed as unsupported; docs recommend host-side `sanitize_output` regex masking ([Bash tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool)). Community workaround: `PreToolUse`/`PostToolUse` hooks with `sed`-based redaction ([nopeek](https://scottspence.com/posts/nopeek-keep-secrets-out-of-claude-code)). Open requests: [#25053](https://github.com/anthropics/claude-code/issues/25053), [#29434](https://github.com/anthropics/claude-code/issues/29434). |
| Cursor (terminal) | Not documented. The terminal tool forwards stdout to the model; the published docs describe no prompt-interception layer ([Cursor terminal docs](https://cursor.com/docs/agent/tools/terminal)). |

Stdout regex redaction is strictly weaker than terminal-side interception: by the time output is filtered the secret has already been typed into a harness-controlled buffer, and anything bypassing the regex (custom prompt string, non-English locale, base64) leaks through.

## Why It Works

Once a secret enters the serialised terminal output the model reads, it is indistinguishable from any other token: it can be summarised, echoed into a tool argument, persisted to a transcript, or replayed in a later call. Interception adds a control layer between the PTY prompt and the model stream — detection fires before the read completes, a synthetic message is substituted, and the real stdin bytes route only to the human's TTY. The same trust-boundary logic motivates Anthropic's `sanitize_output` recommendation for tool returns ([Bash tool docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool)), and industry framing has converged on "any secret that has touched a context window should be treated as compromised" ([Cequence](https://www.cequence.ai/blog/ai/even-the-best-ai-agents-leak-secrets-prompt-injection-is-why/)).

The threat is documented. The "Comment and Control" disclosure showed Claude Code Security Review, Gemini CLI Action, and GitHub Copilot Agent exfiltrating repository secrets via a single PR-title injection — credentials had been pulled into context by tool calls, then drained back through GitHub ([VentureBeat](https://venturebeat.com/security/ai-agent-runtime-security-system-card-audit-comment-and-control-2026)). "Your AI, My Shell" reports a 68.2% credential-access attack success rate across leading agentic coding editors when an attacker can place untrusted content in scope ([arxiv 2509.22040](https://arxiv.org/html/2509.22040v1)).

## When This Backfires

- **MCP tool injection bypasses the layer.** A compromised MCP server can return a secret (or instructions to harvest one) directly in a tool result — terminal interception sees nothing. Pair it with [MCP runtime control](mcp-runtime-control-plane.md) and [tool signing](tool-signing-verification.md).
- **Non-interactive credential reads.** `cat .env`, `aws configure get aws_secret_access_key`, `gh auth token` — no prompt, just stdout. Only sensitive-path blocking ([protecting sensitive files](protecting-sensitive-files.md)) helps.
- **Heuristic miss and false positives.** A custom CLI saying `Enter unlock token:` may not match; a legitimate non-secret prompt may get cancelled and break the workflow. Cursor users hit the second failure mode when sudo stopped working in agent terminals ([Cursor forum regression](https://forum.cursor.com/t/regression-agent-terminals-no-longer-support-sudo-or-interactive-input/136719)).
- **Auto-approve deadlock.** In unattended runs (CI, overnight batches) cancellation forces the agent to give up or invent a recovery path; a poorly-written agent may retry and defeat the purpose.
- **Out-of-band exfiltration.** Interception protects the model's transcript, not the host. Screen-capture telemetry, accessibility tooling, or clipboard history still see the typed secret outside the harness.
- **Pre-existing context contamination.** If a `.env` was pasted into chat earlier or a prior tool call already read a credential, the secret is in context regardless.
- **The path may not need to exist.** When browser PKCE or OAuth device-code flows are available, the secret never reaches a terminal prompt at all ([CLI authentication methods](https://blog.logto.io/cli-authentication-methods)) — prefer credential-broker injection ([secrets management](secrets-management-for-agents.md), [scoped credentials via proxy](scoped-credentials-proxy.md)) when redesigning auth flows.

## Example

VS Code 1.121 default mode, walked through with `gh auth login`:

1. Agent runs `gh auth login --hostname github.com --git-protocol https` in a chat-spawned terminal.
2. The command prints `Enter your authentication token:` and waits on stdin.
3. The harness pattern-matches the prompt, pauses the command, and surfaces a confirmation dialog asking the user to focus the terminal.
4. The user types the token into the terminal pane. Keystrokes go to the PTY only — the harness does not capture them into the chat transcript.
5. The command completes. The agent's tool result records "command completed" without the token.

In auto-approve mode, step 3 cancels the command instead and the agent receives an explicit instruction not to retry ([VS Code 1.121 release notes](https://code.visualstudio.com/updates/v1_121#_sensitive-terminal-prompts-stay-in-the-terminal)).

## Key Takeaways

- Interception applies only to interactive TTY prompt paths — passwords, passphrases, PINs, verification codes; it does nothing for secrets read from files or returned by MCP tools.
- The two safe behaviours are confirm-in-terminal (default mode) and cancel-the-command (auto-approve) — never let the agent type the secret itself.
- Stdout regex redaction is a fallback, not a substitute: by the time output is filtered the secret has already been in an agent-controlled buffer.
- Detection is heuristic and brittle — expect false positives on legitimate interactive flows and false negatives on non-standard prompts; instrument both failure modes.
- The structurally better fix is to remove credentials from the TTY path entirely — browser PKCE, device-code, or credential-broker injection — and treat interception as defence-in-depth for the cases where the prompt cannot be designed away.

## Related

- [Secrets Management for Agent Workflows](secrets-management-for-agents.md)
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md)
- [Human-in-the-Loop Confirmation Gates for Consequential Agent Actions](human-in-the-loop-confirmation-gates.md)
