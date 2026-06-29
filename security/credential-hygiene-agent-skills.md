---
title: "Credential Hygiene for Agent Skill Authorship"
term: "Credential Hygiene"
description: "Skills are shareable files — credentials embedded in examples or invocations travel with them. Keep credentials out of skill definitions at authoring time."
tags:
  - security
  - agent-design
  - tool-agnostic
aliases:
  - credential leakage in agent skills
  - secrets in skill files
last_reviewed: 2026-06-12
maturity: adopted
---

# Credential Hygiene for Agent Skill Authorship

> Credentials embedded in skill definitions leak when skills are shared, committed, or reproduced verbatim by agents — a risk runtime secrets management does not cover.

## Why skills are a different surface

Runtime secrets management — env var injection, wrapper scripts, proxy isolation — covers how credentials enter a running session. It does not cover credentials baked into the skill files.

Skills are reusable Markdown artifacts that encode API usage and workflow steps. A skill demonstrating an authenticated call often ships a working example from the author's environment. That example may carry a live token, key, or credential-bearing endpoint.

Three propagation paths expose them:

1. Sharing and publication — you publish skills to community corpora ([awesome-copilot](https://github.com/github/awesome-copilot), agent registries) or commit them to repos. The credential travels with the file.
2. Version control history — a credential removed in a later commit remains in git history. Teams rarely apply a fix such as `git filter-repo` to skill directories.
3. Verbatim LLM reproduction — agents may echo credential-containing examples into generated code, CI configs, or conversation history, treating the skill text as authoritative.

Empirical research documents credential leakage in publicly available skills at scale. ([Source: arxiv:2604.03070](https://arxiv.org/abs/2604.03070))

## Leakage forms

| Form | Example | Risk |
|------|---------|------|
| Inline token in example invocation | `curl -H "Authorization: Bearer ghp_abc123..."` | Committed to repo; published with skill |
| Hardcoded API key in config snippet | `api_key: sk-live-xyz...` | Reproduced verbatim by agent in generated files |
| Env var with default value | `API_KEY=${API_KEY:-sk-live-xyz}` | Default used when env var is unset in new environments |
| Endpoint with embedded credential | `https://user:pass@api.example.com/v1/` | Logged in request traces and agent outputs |

## Mitigations

### Use placeholder syntax in all examples

Replace live credentials with unambiguous placeholders in every skill example:

```bash
# In skill file — placeholder, never a live value
curl -H "Authorization: Bearer $MY_SERVICE_API_KEY" \
  https://api.example.com/v1/endpoint
```

Use shell variable syntax (`$VAR_NAME`) or angle-bracket placeholders (`<token>`). Both signal that substitution is required and stop the model reproducing a working credential.

Never use a real credential as an example, even temporarily. Pre-commit hooks miss credentials that existed only in a draft; git history does not.

### Scan skill files at pre-commit time

Extend secret-scanning to cover skill directories. `gitleaks`, `trufflehog`, and `detect-secrets` support custom path patterns:

```yaml
# .gitleaks.toml — extend scanning to skill directories
[[rules]]
description = "API key in skill file"
regex = '''(?i)(api[_-]?key|token|secret)\s*[:=]\s*['"]?[A-Za-z0-9_\-]{20,}['"]?'''
paths = [".claude/skills/**", "skills/**", ".github/copilot-skills/**"]
```

Run the same scanner in CI to catch leaks from contributors who bypass local hooks.

### Decouple skill invocation from credential holding

Structure skills to invoke wrapper scripts rather than calling authenticated endpoints directly. The skill encodes what to call; the credential stays outside the skill file:

```markdown
<!-- skill: query-analytics -->
To fetch the latest report, run:
  scripts/analytics-fetch.sh <report-id>

The script handles authentication internally. Do not pass credentials as arguments.
```

The wrapper reads `$ANALYTICS_API_KEY` from the environment. The skill text holds no credential, so publication does not expose it.

This is the authoring-time complement to [Secrets Management for Agent Workflows](secrets-management-for-agents.md) (runtime injection) and [Scoped Credentials via Proxy](scoped-credentials-proxy.md) (runtime isolation).

### Audit before publishing

Before publishing or sharing a skill, run a credential audit:

```bash
# Quick scan before publishing a skill
trufflehog filesystem .claude/skills/ --only-verified
detect-secrets scan .claude/skills/ --all-files
```

Community corpora rely on contributor inspection — registry-level scanning is not universal. The [awesome-copilot](https://github.com/github/awesome-copilot) notice — "inspect any agent and its documentation before installing" — puts this burden on consumers. Scanning before publishing shifts it to the authoring stage.

### Structural successors: treat hygiene as a holding pattern

Placeholder syntax and wrapper-script indirection reduce embedded leakage but not the deeper problem: any reusable bearer secret inside the model-steerable boundary is exposed by definition. The [Secret-Use Delegation Protocol (SUDP)](../standards/sudp-secret-use-delegation-protocol.md) frames this as the 'Agent Secret Use' problem — an untrusted requester causing an authorized operation must never hold reusable authority ([Yu, Geng, Knottenbelt 2026](https://arxiv.org/abs/2604.24920)). On the runtime side, [workload identity federation](workload-identity-federation-for-agents.md) replaces long-lived API keys with short-lived OIDC tokens minted on demand — removing the bearer secret rather than hiding it.

Apply authoring-time hygiene today, but treat it as a holding pattern: long-term, the credentials skill examples protect should not exist in their current form.

## Example

A skill that demonstrates Stripe API access before and after applying hygiene:

Before — live credential embedded in skill:

```markdown
<!-- skill: check-stripe-balance -->
To check the account balance, run:
  curl -s -H "Authorization: Bearer sk_live_abc123xyz..." \
    https://api.stripe.com/v1/balance | jq '.available[0].amount'
```

After — placeholder and wrapper script:

```markdown
<!-- skill: check-stripe-balance -->
To check the account balance, run:
  scripts/stripe-balance.sh

The script reads $STRIPE_API_KEY from the environment.
Inject the key before the agent starts — see Secrets Management for Agent Workflows.
```

The skill now encodes the intent and interface; no credential is present.

## Key Takeaways

- Skills persist in version control and travel with publication — credentials embedded at authoring time are not bounded by runtime controls
- Use shell-variable placeholders or angle-bracket tokens in every skill example; never use live credentials, even temporarily
- Extend pre-commit secret scanning to skill directories explicitly — scanners do not cover them by default
- Structure skill invocations to call wrapper scripts rather than authenticated endpoints directly
- Audit skill files before publishing to any shared corpus or registry
- Treat hygiene as a holding pattern; SUDP and workload identity federation remove the reusable secret entirely

## When this backfires

Placeholder syntax and wrapper scripts reduce leakage at authoring time but do not eliminate every vector:

- Private corpora without scanning — teams that never publish externally may skip scanner setup. Leaked credentials remain exploitable if the repo is later open-sourced or an insider extracts the history.
- Agents that resolve placeholders — an agent with both the skill file and environment secrets may substitute real values into placeholder slots such as `$STRIPE_API_KEY`, producing credential-containing outputs. Wrapper-script indirection mitigates this; placeholder-only syntax does not.
- Coverage gaps in CI — Gitleaks path rules for `.claude/skills/` only work if CI runs on all branches and PRs. Skills committed before the rule was added remain unscanned.
- Registry-level credential reuse — credentials rotated after publication remain exposed in any consumer that cached the older skill version. Pre-commit scanning prevents new leaks but does not revoke already-distributed credentials — only removing the reusable secret via [workload identity federation](workload-identity-federation-for-agents.md) closes that path.

Apply wrapper-script isolation and pre-commit scanning together; neither alone closes all paths.

## Related

- [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md) — the standard format that defines skill structure, discovery paths, and frontmatter
- [SUDP: Secret-Use Delegation Protocol](../standards/sudp-secret-use-delegation-protocol.md) — the structural alternative: a three-role protocol so the agent never holds reusable authority
- [Workload Identity Federation for Agent Runtimes](workload-identity-federation-for-agents.md) — runtime alternative: short-lived OIDC tokens that remove long-lived API keys entirely
- [Secrets Management for Agent Workflows](secrets-management-for-agents.md) — runtime injection: keeping credentials out of agent context during execution
- [Scoped Credentials via Proxy Outside the Agent Sandbox](scoped-credentials-proxy.md) — runtime isolation: proxy-held credentials that the agent never touches
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md) — permission rules to block agent reads of credential files
- [Blast Radius Containment: Least Privilege for AI Agents](blast-radius-containment.md) — limiting the impact when a credential is exposed
- [Skill Supply-Chain Poisoning](skill-supply-chain-poisoning.md) — malicious credentials and payloads embedded in published community skills
