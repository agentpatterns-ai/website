---
title: "Credential-Free Subprocesses: Strip Tokens From Agent Tools"
term: "Credential-Free Subprocesses"
description: "Claude Code 2.1.323 runs its own ripgrep and most internal git commands without most sign-in tokens. Allowlist your own wrappers too, and know where it fails."
aliases:
  - stripping credentials from subprocess environments
  - least-privilege subprocess environment
tags:
  - security
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-11-19
maturity: adopted
---

# Credential-Free Subprocesses: Strip Tokens From Agent Tools

> Credential-free subprocesses start each agent tool without the harness's tokens, so a helper or hook under it cannot find them in its own environment.

A credential-free subprocess is a child process started with the harness's tokens and API keys removed from its environment. It protects you only under three conditions. The child must not need the token. The code you fear must read its own environment rather than the parent's. And the secret must be one the filter recognizes. Outside those conditions, it breaks tools or does nothing.

## What Claude Code strips by default

Claude Code 2.1.323 changed "Claude Code's own ripgrep and most internal git commands to run without most of its sign-in tokens and API keys, so a credential helper or hook under such a git command no longer finds them" ([changelog 2.1.323](https://code.claude.com/docs/en/changelog#2-1-323)). The entry says "most" twice and lists no exceptions, so check a specific command before you rely on it.

A day later, 2.1.325 extended the rule. The programs the sandbox "starts for its own use, such as its network bridge" now run without sign-in tokens and API keys. Ripgrep, local git commands and the sandbox's helper programs also lose the mTLS client key's passphrase ([changelog 2.1.325](https://code.claude.com/docs/en/changelog#2-1-325)).

These defaults cover programs the harness starts for itself. The commands Claude runs for you fall under two opt-in controls:

| Control | Covers | How it picks variables |
|---|---|---|
| Default (2.1.323, 2.1.325) | Claude Code's own ripgrep, most internal git, sandbox helpers | Fixed by Claude Code |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` | Bash commands, hooks, stdio MCP servers | Variable name or value shape; keeps GitHub tokens and proxy settings ([env-vars docs](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)) |
| `sandbox.credentials` `deny` | Sandboxed Bash only | Only the variables you list; "There is no built-in credential deny list" ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#protect-credentials)) |

## Why git is the case that matters

Git runs programs that configuration chooses. A credential helper string that "begins with "!", it is considered a shell snippet" ([gitcredentials](https://git-scm.com/docs/gitcredentials)). `core.fsmonitor` can hold "the pathname of the "fsmonitor" hook command" ([git-config](https://git-scm.com/docs/git-config#Documentation/git-config.txt-corefsmonitor)). By default git "will refuse to even parse a Git config of a repository owned by someone else, let alone run its hooks" ([git-config](https://git-scm.com/docs/git-config#Documentation/git-config.txt-safedirectory)).

So a git command from the harness can start programs the harness never named. Before 2.1.323, those programs could find Claude Code's sign-in tokens and API keys in their environment.

## Apply the rule to your own wrappers

In your own tool wrappers, pass an explicit environment in place of the inherited one. Python's `subprocess` takes an `env` mapping that is "used instead of the default behavior of inheriting the current process' environment" ([Python subprocess docs](https://docs.python.org/3/library/subprocess.html)).

Build that mapping from an allowlist. A denylist misses what it does not recognize, and Claude Code's own scrub "Leaves it in place" for "A secret whose variable name and value don't look like a credential" ([env-vars docs](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)). OpenAI Codex offers the allowlist form: start empty with `inherit = "none"` or a trimmed set with `inherit = "core"` ([Codex advanced config](https://developers.openai.com/codex/config-advanced#shell-environment-policy)). Its name-based exclusion of `KEY`, `SECRET` and `TOKEN` is off by default, because `ignore_default_excludes` defaults to `true`.

Give the token back only to the call that needs it, such as one `git push`.

## Why it works

A child gets "a copy of its parent's environment" when it is created ([environ(7)](https://man7.org/linux/man-pages/man7/environ.7.html)). Each program it starts gets a copy in turn. Removing a variable at the first child removes it from the whole subtree, so a helper three levels down sees only what the harness passed.

The Codecov compromise shows the cost of the default. A modified uploader script could export "Any credentials, tokens, or keys that our customers were passing through their CI runner that would be accessible when the Bash Uploader script was executed" ([Codecov security update](https://about.codecov.io/security-update/)).

## When this backfires

- The child needs the token. A credential helper that reads a token from an environment variable fails. Claude's guidance for the scrub is "Leave the scrub unset if a subprocess needs one of the removed variables" ([env-vars docs](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)).
- Partial stripping leaves a mismatched set. Claude Code 2.1.327 fixed a nested `claude` with its own token being refused. The fix: commands that do not get the session's token "no longer get its `CLAUDE_CODE_OAUTH_SCOPES`" ([changelog 2.1.327](https://code.claude.com/docs/en/changelog#2-1-327)).
- The reader runs as the same user. Access to `/proc/<pid>/environ` "is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check" ([proc_pid_environ(5)](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html)). A report against GitHub's agentic workflows firewall found "A same-UID process can read inherited environment variables of sibling workflow processes" ([gh-aw-firewall #1753](https://github.com/github/gh-aw-firewall/issues/1753)). Claude's scrub adds a Linux PID namespace for this reason. The 2.1.323 default does not claim one.
- The token you worry about is kept. The scrub leaves `GITHUB_TOKEN` and `GH_TOKEN` in place "so that `gh` and scripts that call the GitHub API keep working" ([env-vars docs](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)). Narrow the token's scope, or add a `sandbox.credentials` `deny` entry.

## Example

A Python wrapper that runs ripgrep with four variables, and gives a token to a git call only when the caller asks for it:

```python
import os
import subprocess

BASE = ("PATH", "HOME", "LANG", "TMPDIR")

def run_tool(argv, extra=()):
    env = {k: os.environ[k] for k in (*BASE, *extra) if k in os.environ}
    return subprocess.run(argv, env=env, capture_output=True, text=True)

run_tool(["rg", "--json", "TODO", "src/"])
run_tool(["git", "push"], extra=("GH_TOKEN",))
```

The Codex documentation shows the same allowlist set from the command line:

```bash
codex --config 'shell_environment_policy.include_only=["PATH","HOME"]'
```

## Key Takeaways

- Claude Code 2.1.323 and 2.1.325 strip tokens from programs the harness starts for itself. Bash commands, hooks and MCP servers need `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` or `sandbox.credentials`.
- Give git the strictest environment of any helper, because config decides which programs it runs.
- Write wrappers with an allowlist and add a token per call. A name-based filter misses ordinary-looking secrets.
- Where same-user processes can read `/proc`, pair stripping with a PID namespace ([env-vars docs](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)), `hidepid=2`, or `PR_SET_DUMPABLE=0` ([gh-aw-firewall #1753](https://github.com/github/gh-aw-firewall/issues/1753)).

## Related

- [Subprocess PID Namespace Sandboxing in Claude Code](subprocess-pid-namespace-sandboxing.md) — the opt-in scrub plus PID namespace for Bash subprocesses
- [Per-Server MCP Environment Scoping for Credential Isolation](mcp-server-credential-isolation.md) — the same rule applied to each MCP server's environment
- [System Prompt Delivery Channels on Shared Runners](system-prompt-delivery-channel.md) — why a same-UID neighbor reads the environment block anyway
- [Sandbox Credential Masking](sandbox-credential-masking.md) — the option when a tool must read the credential
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — how credentials reach the agent process in the first place
