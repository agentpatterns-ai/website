---
title: "Sandbox Credential Masking: Authenticate Without Seeing the Secret"
term: "Sandbox Credential Masking"
description: "The sandbox shows the agent a sentinel and the proxy swaps in the real credential on egress, so credential-reading tools keep working while the secret stays out of context."
aliases:
  - credential masking at the sandbox boundary
  - sentinel credential substitution
  - sandbox proxy credential injection
tags:
  - security
  - agent-design
  - claude
applies_to: "claude-code@2.x"
last_reviewed: 2026-08-08
maturity: emerging
---

# Sandbox Credential Masking: Authenticate Without Seeing the Secret

> A sandbox proxy swaps a per-session sentinel for the real credential on egress, so the agent authenticates without the secret entering its context.

Credential masking closes the gap that authoring-layer hygiene leaves open. Keeping secrets out of prompts, skill files, and the repo does nothing about the moment the agent calls an authenticated API, because the value still has to exist somewhere the tool can read it. Masking moves it to the network boundary: the sandboxed command sees a placeholder, and the proxy substitutes the real credential on requests to hosts you name.

## When masking is the right control

Use masking when a tool must read a credential and you cannot rewrite it. The AWS CLI, `gh`, and `npm` each expect a token in an environment variable or a config file, and a `deny` entry "removes the variable entirely, which also breaks tools that need it" ([Claude Code sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)). Four conditions have to hold first:

- The proxy can read the traffic. Substitution rewrites request contents, so the experimental `network.tlsTerminate` setting is mandatory ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#network-isolation)).
- The platform supports your credential type. Environment-variable masking behaves the same everywhere; file masking is Linux and WSL2 behavior ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-credential-files)).
- The configuration lives somewhere the agent cannot write. Masking is honored only from user settings, managed settings, and the `--settings` flag, never from a repository's `.claude/settings.json` ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)).
- You have hardened the no-match defaults. `onExtractNoMatch` ships as `warn`, which passes the value through unmasked ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)).

Where you own the calling code, a wrapper script or a [scoped credentials proxy](scoped-credentials-proxy.md) reaches the same end state without a regular expression, a JWT verifier, or TLS termination.

## How the substitution works

The placeholder is a per-session sentinel, and each masked entry can list `injectHosts`. The proxy replaces the sentinel in the headers or body of requests bound for one of those hosts, so "the command and anything it logs never hold the real credential, but its requests still authenticate" ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)). Misconfiguration fails safe: without `tlsTerminate` the sentinel reaches the server unchanged, authentication fails, and Claude Code reports the problem at startup.

## Structured values and JWT claims

Whole-value replacement suits a bare token. Two options added in Claude Code 2.1.224 handle values a tool parses ([changelog](https://code.claude.com/docs/en/changelog)):

- `extract` takes a regular expression and replaces "only the text captured by group 1 of each match", so a `DATABASE_URL` connection string still parses inside the sandbox ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)).
- `decode: "jwt"` verifies the value is a JSON Web Token and replaces it with "a structurally valid fake token, so code inside the sandbox that decodes the token keeps working". Adding `maskClaims` masks named top-level payload claims and leaves the rest readable. It cannot be combined with `extract` ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)).

That distinction matters when sandboxed code branches on the token, since the claims a reader does not name stay readable while the rest is replaced.

## Signed requests are the hard case

A proxy cannot fix an AWS request by swapping a header value. "AWS requests carry SigV4 signatures over the request contents, so mask `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` together"; the proxy detects the request by the access key's sentinel and re-signs it after substituting the real values ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#re-sign-aws-requests)). Masking the secret alone leaves a placeholder-signed request the proxy cannot detect, and it fails at AWS. Three forms carry signatures the proxy cannot recompute at all: aws-chunked streaming uploads, presigned URLs, and SigV4A. Those fail with a proxy error rather than a broken signature on the wire, and `credentials.sigv4` relaxes that per form ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#re-sign-aws-requests)).

## Why it works

The sentinel-to-value mapping lives in a process the agent cannot address. Every channel the agent can read or exfiltrate through carries the placeholder, while the proxy outside the sandbox holds the only copy of the real value and injects it on egress ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)). Anthropic's earlier sandbox design took the same line: "sensitive credentials (such as git credentials or signing keys) are never inside the sandbox with Claude Code", with a proxy that validates the request and attaches the token ([Anthropic: Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)).

Settings provenance is the second half. A `mask` entry authorizes the proxy to release a real secret to named hosts, so honoring one from a repo file would let anything with write access, including the agent, nominate its own `injectHosts`. Restricting the options to user, managed, and `--settings` sources makes the boundary non-self-modifiable, which turns it into an [enforced rather than advisory control](enforced-versus-advisory-controls.md).

## When this backfires

- The no-match defaults are fail-open. `onExtractNoMatch` defaults to `warn`, which "warns and passes the variable through unmasked", and a value failing JWT verification is passed through the same way ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)). A rotated credential format silently disables the mask. Set `deny` or `error` where the secret should be present.
- macOS file masking is not masking. There, "sandboxed commands can't read the listed file at all", the same effect as `deny`, so the tool breaks instead of working with a placeholder ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-credential-files)).
- Masking stops disclosure, not misuse. Sandboxed execution "does not prevent legitimate-looking API calls with malicious parameters within the sandbox's permitted scope" ([Uchibeke, 2026](https://arxiv.org/abs/2603.20953v1)). A prompt-injected agent can still spend the credential's full authority against an allowed host, which is a job for an authorization layer.
- TLS termination is a trust decision of its own, giving the proxy operator plaintext view of `git push`, `npm install`, and `aws sts` traffic. Some regulated regimes forbid it, as the [hostname-allowlist blind spot](hostname-allowlist-tls-blind-spot.md) page covers.
- Some targets cannot be masked at all: directory paths, glob patterns, files over 8 MiB, and non-UTF-8 files fall back to `deny`, and `maskDuplicates` matches raw substrings, so a short value is replaced wherever it appears ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-credential-files)).

## Example

Masking the GitHub token in `~/.config/gh/hosts.yml` so `gh` keeps working while the agent reads a placeholder. The `extract` pattern names the secret span, and the rest of the YAML stays parseable ([sandboxing docs](https://code.claude.com/docs/en/sandboxing#mask-credential-files)):

```json
{
  "sandbox": {
    "enabled": true,
    "network": {
      "tlsTerminate": {},
      "allowedDomains": ["*.github.com"]
    },
    "credentials": {
      "files": [
        {
          "path": "~/.config/gh/hosts.yml",
          "mode": "mask",
          "extract": "oauth_token:\\s*(\\S+)",
          "injectHosts": ["api.github.com"]
        }
      ]
    }
  }
}
```

On Linux and WSL2, a sandboxed `cat ~/.config/gh/hosts.yml` shows a sentinel where the token was, and the proxy substitutes the real token on requests to `api.github.com`. On macOS the read fails instead. Put this in user or managed settings, since the repository's own settings file is ignored for masking.

## FAQ

**Why does masking need TLS termination?**

The proxy substitutes the credential inside request headers and bodies, which it can only do if it can read them. A proxy forwarding opaque encrypted bytes has nothing to rewrite. Without `network.tlsTerminate` the sentinel reaches the server unchanged and authentication fails, so the failure is safe rather than a silent exposure, and Claude Code reports the misconfiguration at startup.

**Does masking protect against a prompt-injected agent?**

Only against disclosure of the secret. The agent holds a placeholder, so it cannot exfiltrate the credential itself or leak it through logs. It can still direct the proxy to make authenticated requests within the credential's scope to an allowed host. Pair masking with an authorization layer that judges the action rather than the identity behind it.

**When should I use a scoped credentials proxy instead?**

When you control the code that calls the API. A proxy that attaches tokens to unauthenticated requests has no regular expression to drift, no JWT verifier to fall back from, and no TLS termination requirement. Masking earns its extra machinery only when an unmodifiable tool insists on reading a credential from an environment variable or a config file.

## Key Takeaways

- Masking is for credential-consuming tools you cannot rewrite; wrap the call instead when you own it
- Check `onExtractNoMatch` before trusting a mask, because the default passes the value through unmasked
- File masking is Linux and WSL2 only; macOS applies mask entries as `deny`
- SigV4 needs re-signing rather than substitution, and three request forms cannot be re-signed at all
- The settings-provenance restriction is what makes this enforcement, since the agent cannot grant itself an `injectHosts` entry
- A masked credential retains its full scope, so authorization stays a separate layer

## Related

- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md)
- [Secrets Management for AI Agents: Credential Injection](secrets-management-for-agents.md)
- [Hostname-Allowlist Proxy: The TLS-Inspection Blind Spot](hostname-allowlist-tls-blind-spot.md)
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md)
- [Sandbox-Enforced PII Tokenization in Agent Workflows](pii-tokenization-in-agent-context.md)
- [Sensitive Terminal Prompt Interception](sensitive-terminal-prompt-interception.md)
