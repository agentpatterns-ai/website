---
title: "Secrets Management for AI Agents: Credential Injection"
term: "Secrets Management for AI Agents"
description: "Inject credentials as environment variables or wrapper scripts so agents work without secrets appearing in context, prompts, or generated code."
aliases:
  - "Secrets & Credentials"
  - "Credential Injection Patterns"
tags:
  - agent-design
  - workflows
  - tool-agnostic
  - security
last_reviewed: 2026-06-12
maturity: established
---

# Secrets Management for AI Agents: Credential Injection

> Inject credentials as environment variables or wrapper scripts so agents can do authenticated work without secrets appearing in context, prompts, or generated code.

Learn it hands-on with [Keep the Keys Out](https://learn.agentpatterns.ai/security/keep-the-keys-out/), a guided lesson with quizzes.

!!! note "Also known as"
    Secrets & Credentials, Credential Injection Patterns. For the proxy-based approach to credential scoping, see [Scoped Credentials via Proxy](scoped-credentials-proxy.md).

## The anti-pattern

Pasting an API key into a prompt sends it to the model API and writes it into session logs. The agent can also echo it back in comments or generated files. Once a secret enters the context window, you lose control of where it goes.

## Environment variable injection

Inject secrets at the shell level before the agent process starts. Agents use environment variables without reading them as text:

```bash
# Start the agent with credentials pre-loaded in the environment
DATABASE_URL="postgres://..." OPENAI_API_KEY="sk-..." claude
```

Tools call scripts that consume `$DATABASE_URL` internally — the value never appears in a prompt or tool call.

For persistent configuration, use `direnv` to evaluate `.envrc` on `cd` into the project ([direnv.net](https://direnv.net/)).

## Wrapper scripts

Agents need results, not credentials. A wrapper script uses a secret internally and returns only the output:

```bash
#!/bin/bash
# scripts/query-db.sh
# Agent calls this script; the connection string is never visible in tool input
RESULT=$(psql "$DATABASE_URL" -t -c "$1")
echo "$RESULT"
```

The agent runs `scripts/query-db.sh "SELECT count(*) FROM users"`, and `DATABASE_URL` never appears in the tool call or context. Design wrappers to accept intent and return results.

## Never store secrets in agent-readable files

Agent-readable files include:

- Any file in the working directory not excluded by `permissions.deny`
- Files the agent explicitly requests
- Files referenced in AGENTS.md or system prompts

Do not store secrets in:

- `.env` files unless they are blocked by `permissions.deny` rules (see [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md))
- AGENTS.md, system prompts, or instruction files
- Comments in code files

Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, 1Password CLI) to retrieve secrets in a parent shell before you launch the agent. The retrieval command stays in the parent context, and the session inherits only the exported value.

## Auditing agent environment access

Before starting an agent session, audit available credentials:

```bash
# List environment variables the agent shell will inherit
env | grep -iE 'key|secret|token|password|url|dsn' | sort
```

Remove any credential the task does not need. A minimal permission set limits the damage if the agent misbehaves or a [prompt injection](prompt-injection-threat-model.md) occurs.

## CI and agentic pipelines

When agents run autonomously in CI/CD pipelines:

- Use short-lived tokens scoped to the minimum permissions needed. Most CI providers and cloud platforms support OIDC-based federated identities that remove long-lived secrets entirely
- Rotate tokens between pipeline runs rather than reuse long-lived credentials
- Store secrets in the CI platform's native secret store (GitHub Actions secrets, GitLab CI variables), not in repo files
- Mask secret values in CI logs. GitHub Actions redacts every registered secret value that appears in stdout or stderr ([GitHub Docs](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions))

This GitHub Actions example injects secrets as environment variables and never writes them to disk:

```yaml
- name: Run agent task
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    API_KEY: ${{ secrets.API_KEY }}
  run: claude --print "run the migration"
```

## Why it works

Environment variables are inherited by child processes but are not transmitted as text through tool calls. The agent sends a command string; the shell executing it inherits the env, but the context window only records the command name and arguments. Wrapper scripts extend this boundary: the script consumes the credential internally, and the agent receives only stdout — the credential traverses no channel the agent can read or log.

## When this backfires

Env var injection has specific failure modes:

- Shared container environments: in multi-tenant or sidecar-based deployments, sibling processes may be able to read `/proc/<pid>/environ` on Linux unless the container is hardened with user namespaces or seccomp restrictions.
- Sub-process env stripping: some agent frameworks spawn sandboxed sub-processes with a cleaned environment. If the agent runs tools in an isolated subprocess, env vars set in the parent shell may not be inherited. Verify the tool execution model before you rely on this pattern.
- Env var logging by the agent itself: some agents log their startup environment for debugging. Confirm the agent's own log output is not captured in session context or written to files the agent can read (see [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)).
- Secrets manager retrieval inside the session: fetching a secret with a CLI tool during an agent task, rather than before session start, risks the retrieval command and its output appearing in the context window. Retrieve all required secrets before the agent session begins.
- Env sprawl: injecting all available credentials rather than just the ones needed for the current task expands the blast radius. See [Blast Radius Containment](blast-radius-containment.md).

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

## Related

- [Credential Hygiene for Agent Skills](credential-hygiene-agent-skills.md)
- [Protecting Sensitive Files from Agent Context](protecting-sensitive-files.md)
- [Blast Radius Containment](blast-radius-containment.md)
- [Lethal Trifecta Threat Model](lethal-trifecta-threat-model.md)
- [Permission-Gated Custom Commands](permission-gated-commands.md)
- [Hook Catalog: Guardrails, Sandboxing, and CLI Enforcement](../tool-engineering/hook-catalog.md)
- [Enterprise Agent Hardening](enterprise-agent-hardening.md)
- [Sandbox-Enforced PII Tokenization in Agent Workflows](pii-tokenization-in-agent-context.md)
