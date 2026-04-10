---
title: "Credential Hygiene for Agent Skill Authorship"
description: "Skills are shareable files — credentials embedded in examples or invocations travel with them. Keep credentials out of skill definitions at authoring time."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - credential leakage in agent skills
  - secrets in skill files
---

# Credential Hygiene for Agent Skill Authorship

> Credentials embedded in skill definitions leak when skills are shared, committed, or reproduced verbatim in agent outputs — a distinct risk from runtime injection that existing secrets management patterns do not cover.

## Why Skills Are a Different Surface

Runtime secrets management — environment variable injection, wrapper scripts, proxy-based credential isolation — addresses how credentials enter a running agent session. It does not address credentials baked into the skill files themselves.

Skills are reusable Markdown artifacts that encode API usage patterns, tool invocations, and workflow steps. A skill that demonstrates an authenticated API call often includes a working example from the author's environment. That example may contain a live token, an API key, or a hardcoded endpoint with embedded credentials.

Three propagation paths expose embedded credentials:

1. **Sharing and publication** — Skills intended for one environment are published to community corpora ([awesome-copilot](https://github.com/github/awesome-copilot), agent registries) or committed to repositories. The credential travels with the file.
2. **Version control history** — A credential removed from a skill in a later commit remains in git history. Shallow mitigation (`git filter-repo`) is rarely applied to skill directories.
3. **Verbatim LLM reproduction** — Agents instructed to follow a skill may echo credential-containing examples into generated code, CI configs, or conversation history. The model treats the skill text as authoritative and reproduces it.

Empirical research on real-world agent skill corpora documents credential leakage in publicly available skills at scale. ([Source: arxiv:2604.03070](https://arxiv.org/abs/2604.03070))

## Leakage Forms

| Form | Example | Risk |
|------|---------|------|
| Inline token in example invocation | `curl -H "Authorization: Bearer ghp_abc123..."` | Committed to repo; published with skill |
| Hardcoded API key in config snippet | `api_key: sk-live-xyz...` | Reproduced verbatim by agent in generated files |
| Env var with default value | `API_KEY=${API_KEY:-sk-live-xyz}` | Default used when env var is unset in new environments |
| Endpoint with embedded credential | `https://user:pass@api.example.com/v1/` | Logged in request traces and agent outputs |

## Mitigations

### Use Placeholder Syntax in All Examples

Replace live credentials with unambiguous placeholders in every skill example:

```bash
# In skill file — placeholder, never a live value
curl -H "Authorization: Bearer $MY_SERVICE_API_KEY" \
  https://api.example.com/v1/endpoint
```

Use shell variable syntax (`$VAR_NAME`) or angle-bracket placeholders (`<token>`) — both signal to readers that substitution is required and prevent the model from reproducing a working credential.

Never use a real credential as an example even temporarily. Pre-commit hooks do not catch credentials that existed only in a draft; git history does.

### Scan Skill Files at Pre-commit Time

Extend secret-scanning to cover skill directories. Standard tools (`gitleaks`, `trufflehog`, `detect-secrets`) support custom path patterns:

```yaml
# .gitleaks.toml — extend scanning to skill directories
[[rules]]
description = "API key in skill file"
regex = '''(?i)(api[_-]?key|token|secret)\s*[:=]\s*['"]?[A-Za-z0-9_\-]{20,}['"]?'''
paths = [".claude/skills/**", "skills/**", ".github/copilot-skills/**"]
```

Run the same scanner in CI to catch leaks from contributors who bypass local hooks.

### Decouple Skill Invocation from Credential Holding

Structure skills so they invoke wrapper scripts or environment-provided commands rather than calling authenticated endpoints directly. The skill encodes *what* to call; the credential remains outside the skill file:

```markdown
<!-- skill: query-analytics -->
To fetch the latest report, run:
  scripts/analytics-fetch.sh <report-id>

The script handles authentication internally. Do not pass credentials as arguments.
```

The `scripts/analytics-fetch.sh` wrapper reads `$ANALYTICS_API_KEY` from the environment. The skill text contains no credential. Even if the skill file is published, the credential is not exposed.

This pattern is the authoring-time complement to [Secrets Management for Agent Workflows](secrets-management-for-agents.md), which covers runtime injection, and [Scoped Credentials via Proxy](scoped-credentials-proxy.md), which covers runtime isolation.

### Audit Before Publishing

Before publishing or sharing a skill file, run a credential audit against the file:

```bash
# Quick scan before publishing a skill
trufflehog filesystem .claude/skills/ --only-verified
detect-secrets scan .claude/skills/ --all-files
```

Community skill corpora rely on contributor inspection because automated scanning at the registry level is not universal. The [awesome-copilot](https://github.com/github/awesome-copilot) security notice — "inspect any agent and its documentation before installing" — places this burden on consumers; scanning before publishing shifts it to the safer authoring stage.

## Example

A skill that demonstrates Stripe API access before and after applying hygiene:

**Before — live credential embedded in skill:**

```markdown
<!-- skill: check-stripe-balance -->
To check the account balance, run:
  curl -s -H "Authorization: Bearer sk_live_abc123xyz..." \
    https://api.stripe.com/v1/balance | jq '.available[0].amount'
```

**After — placeholder and wrapper script:**

```markdown
<!-- skill: check-stripe-balance -->
To check the account balance, run:
  scripts/stripe-balance.sh

The script reads $STRIPE_API_KEY from the environment.
Inject the key before the agent starts — see Secrets Management for Agent Workflows.
```

The skill now encodes the intent and the interface; no credential is present.

## Key Takeaways

- Skills are authoring artifacts that persist in version control and travel with publication — credentials embedded at authoring time are not bounded by runtime controls
- Use shell variable placeholders or angle-bracket tokens in all skill examples; never use live credentials even as temporary examples
- Extend pre-commit secret scanning to skill directories explicitly — scanners do not cover them by default
- Structure skill invocations to call wrapper scripts rather than authenticated endpoints directly
- Audit skill files before publishing to any shared corpus or registry

## Unverified Claims

- LLM verbatim reproduction of skill content into agent outputs is reported by practitioners but not formally documented in a primary source [unverified]
- Secret-scanning tools do not cover skill directories by default — behavior depends on tool configuration and path glob defaults [unverified]

## Related

- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — runtime injection: keeping credentials out of agent context during execution
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — runtime isolation: proxy-held credentials that the agent never touches
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md) — permission rules to block agent reads of credential files
- [Tool-Invocation Attack Surface](tool-invocation-attack-surface.md) — how malicious tools exploit credential-containing arguments
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — limiting the impact when a credential is exposed
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — layered controls that catch leaks at multiple stages
