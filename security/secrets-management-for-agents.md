---
title: "Secrets Management for AI Agents: Credential Injection"
description: "Inject credentials as environment variables or wrapper scripts so agents work without secrets appearing in context, prompts, or generated code."
aliases:
  - "Secrets & Credentials"
  - "Credential Injection Patterns"
tags:
  - agent-design
  - workflows
  - tool-agnostic
  - security
---

# Secrets Management for Agent Workflows

> Inject credentials as environment variables or wrapper scripts so agents can do authenticated work without secrets appearing in context, prompts, or generated code.

!!! note "Also known as"
    Secrets & Credentials, Credential Injection Patterns. For the proxy-based approach to credential scoping, see [Scoped Credentials via Proxy](scoped-credentials-proxy.md).

## The Anti-Pattern

The naive approach — pasting an API key into the prompt — sends the secret to the model API, writes it into session logs, and risks the agent echoing it back in comments or generated files. Once a secret enters the context window, you lose control of where it goes.

## Environment Variable Injection

Inject secrets at the shell level before the agent process starts. Agents consume environment variables without reading them as text:

```bash
# Start the agent with credentials pre-loaded in the environment
DATABASE_URL="postgres://..." OPENAI_API_KEY="sk-..." claude
```

The agent's tools can call scripts that consume `$DATABASE_URL` internally — the variable's value never needs to appear in a prompt or tool call.

For persistent configuration, use a tool like `direnv` to load `.envrc` into your shell automatically when you enter the project directory [unverified — third-party tool behavior not verified against official docs].

## Wrapper Scripts

Agents need results, not credentials. A wrapper script consumes a secret internally and returns only the output:

```bash
#!/bin/bash
# scripts/query-db.sh
# Agent calls this script; the connection string is never visible in tool input
RESULT=$(psql "$DATABASE_URL" -t -c "$1")
echo "$RESULT"
```

The agent invokes `scripts/query-db.sh "SELECT count(*) FROM users"` — the `DATABASE_URL` never appears in the tool call or context window. Design wrappers to accept intent and return results; keep credential consumption inside the script boundary.

## Never Store Secrets in Agent-Readable Files

Agent-readable files include:

- Any file in the working directory not excluded by `permissions.deny`
- Files the agent explicitly requests
- Files referenced in AGENTS.md or system prompts

Do not store secrets in:

- `.env` files unless they are blocked by `permissions.deny` rules (see [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md))
- AGENTS.md, system prompts, or instruction files
- Comments in code files

Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, 1Password CLI) to retrieve secrets at process start and inject them as environment variables. The agent never sees the retrieval output if secrets are injected before the session begins [unverified — depends on specific secrets manager CLI behavior].

## Auditing Agent Environment Access

Before starting an agent session, audit available credentials:

```bash
# List environment variables the agent shell will inherit
env | grep -iE 'key|secret|token|password|url|dsn' | sort
```

Remove any credential not required for the task. A minimal permission set reduces blast radius if the agent misbehaves or a [prompt injection](prompt-injection-threat-model.md) occurs.

## CI and Agentic Pipelines

In CI/CD pipelines where agents run autonomously:

- Use short-lived tokens scoped to the minimum required permissions [unverified — specific token lifetimes depend on provider]
- Rotate tokens between pipeline runs rather than using long-lived credentials
- Store secrets in the CI platform's native secret store (GitHub Actions secrets, GitLab CI variables), not in repo files
- Mask secret values in CI logs — most platforms do this automatically for registered secrets [unverified — platform-specific behavior]

GitHub Actions example — secrets injected as environment variables, never written to disk [unverified — exact Claude Code CLI invocation flag may differ]:

```yaml
- name: Run agent task
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    API_KEY: ${{ secrets.API_KEY }}
  run: claude --print "run the migration"
```

## Example

A complete secrets-injection setup for a coding agent that queries a database and calls an external API:

```bash
# .envrc (loaded automatically by direnv when entering the project)
export DATABASE_URL="postgres://app:$(vault kv get -field=password secret/db)@db.internal:5432/main"
export STRIPE_API_KEY="$(op read 'op://Engineering/Stripe/api-key')"
```

```bash
#!/bin/bash
# scripts/stripe-balance.sh — wrapper that hides the API key from the agent
curl -s -H "Authorization: Bearer $STRIPE_API_KEY" \
  https://api.stripe.com/v1/balance | jq '.available[0].amount'
```

```bash
# Audit the environment, then start the agent
env | grep -iE 'key|secret|token|password|url|dsn' | sort
# Confirm only DATABASE_URL and STRIPE_API_KEY are present, then:
claude
```

The agent calls `scripts/stripe-balance.sh` and `scripts/query-db.sh` as tools. Neither the Vault token, the 1Password service account token, nor the raw credential values ever appear in the agent's context window.

## Key Takeaways

- Inject secrets as environment variables before the agent starts — never in prompts or instruction files
- Wrapper scripts that consume credentials internally prevent secrets from appearing in tool calls
- Audit available environment variables before each session and remove unused credentials
- In CI pipelines, use short-lived scoped tokens stored in the platform's native secret store
- Blocking agent reads of credential files is a complementary control, not a replacement for this pattern

## Unverified Claims

- `direnv` loads `.envrc` into your shell automatically when you enter the project directory [unverified — third-party tool behavior not verified against official docs]
- The agent never sees the retrieval command's output if secrets are injected before the session begins [unverified — depends on specific secrets manager CLI behavior]
- Use short-lived tokens scoped to the minimum required permissions [unverified — specific token lifetimes depend on provider]
- Most platforms mask secret values in CI logs automatically for registered secrets [unverified — platform-specific behavior]
- Exact Claude Code CLI invocation flag may differ [unverified — exact Claude Code CLI invocation flag may differ]

## Related

- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Blast Radius Containment](blast-radius-containment.md)
- [Dual-Boundary Sandboxing](dual-boundary-sandboxing.md)
- [Enterprise Agent Hardening](enterprise-agent-hardening.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md)
- [Permission-Gated Custom Commands](permission-gated-commands.md)
- [Safe Outputs Pattern](safe-outputs-pattern.md)
- [Designing Agents to Resist Prompt Injection](prompt-injection-resistant-agent-design.md)
- [Treat Task Scope as a Security Boundary](task-scope-security-boundary.md)
- [Sandbox-Enforced PII Tokenization in Agent Workflows](pii-tokenization-in-agent-context.md)
