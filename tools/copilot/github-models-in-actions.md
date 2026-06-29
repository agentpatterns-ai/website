---
title: "GitHub Models in Actions for AI-Driven CI Workflows"
description: "Insert AI judgment into GitHub Actions workflows using GitHub Models — no API keys, version-controlled prompts, and deterministic branching."
tags:
  - workflows
  - agent-design
  - copilot
  - github-actions
applies_to: "copilot@1.x"
last_reviewed: 2026-05-27
status: current
---
# GitHub Models in Actions

> Insert AI judgment into GitHub Actions workflows using GitHub Models — no external API keys, version-controlled prompts, and deterministic branching on probabilistic outputs.

## Architecture

GitHub Models exposes 40+ AI models (OpenAI, Mistral, xAI, and others) through a single inference endpoint. Access from Actions needs only `permissions: models: read` and authenticates with the built-in `GITHUB_TOKEN`, so you manage no external API keys ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/automate-your-project-with-github-models-in-actions/)).

You can use three integration methods:

| Method | Use case |
|--------|----------|
| `actions/ai-inference@v1` | Inline or file-based prompts in workflow steps |
| `gh models run` CLI | Piping content through models in shell steps |
| `.prompt.yml` files | Versioned, templated prompts with variable substitution |

You swap models with a single parameter (for example `model: openai/gpt-4.1` or `model: xai/grok-3-mini`), which keeps workflow logic separate from model choice ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/automate-your-project-with-github-models-in-actions/)).

## Prompt file format

`.prompt.yml` files version-control AI prompts alongside code. The format supports multi-message conversations, template variables with `{{variable}}` syntax, JSON schema response formatting, and per-prompt parameter overrides (`temperature`, `topP`, `maxCompletionTokens`) ([`actions/ai-inference` README](https://github.com/actions/ai-inference)):

```yaml
name: bug-triage
description: Assess whether an issue is a valid bug report
model: openai/gpt-4.1
messages:
  - role: system
    content: >
      Evaluate the issue. Return "pass" if it contains
      reproduction steps and expected behavior. Otherwise
      return a one-line explanation.
  - role: user
    content: "{{issue_body}}"
```

The `response-file` output handles large responses that exceed Actions output size limits ([`actions/ai-inference` README](https://github.com/actions/ai-inference)).

## Deterministic branching on AI output

The core pattern: constrain model output to fixed return values, then branch deterministically. Instruct the model to return a known string (for example `"pass"`) when criteria are met, which enables standard workflow conditionals ([GitHub Blog](https://github.blog/ai-and-ml/generative-ai/automate-your-project-with-github-models-in-actions/)):

```yaml
- id: analyze-issue
  uses: actions/ai-inference@v1
  with:
    model: openai/gpt-4.1
    prompt-file: .github/prompts/bug-triage.prompt.yml

- if: steps.analyze-issue.outputs.response != 'pass'
  uses: actions/github-script@v7
  with:
    script: |
      await github.rest.issues.addLabels({
        ...context.repo,
        issue_number: context.issue.number,
        labels: ['needs-info']
      })
```

This works because LLMs constrained to a small vocabulary of valid tokens (for example `"pass"`, `"bug"`, `"feature"`) have far fewer degrees of freedom than open-ended generation, which reduces variance enough to treat the output as an enum value. The same conditional mechanics apply to any Actions workflow.

## Pre-built actions

Two ready-made Actions implement common patterns using GitHub Models:

AI Assessment Comment Labeler ([`github/ai-assessment-comment-labeler`](https://github.com/github/ai-assessment-comment-labeler)) runs multiple prompts in parallel against issues, applies structured labels (`ai:<prompt-stem>:<assessment>`), and supports comment suppression ([GitHub Changelog](https://github.blog/changelog/2025-09-05-github-actions-ai-labeler-and-moderator-with-the-github-models-inference-api/)).

AI Moderator ([`github/ai-moderator`](https://github.com/github/ai-moderator)) detects spam, link spam, and AI-generated content on issues and comments. It auto-labels flagged content and can minimize it. It also supports custom prompt overrides ([GitHub Changelog](https://github.blog/changelog/2025-09-05-github-actions-ai-labeler-and-moderator-with-the-github-models-inference-api/)).

Both use the same `models: read` permission pattern with no separate API key management.

## MCP integration

The `actions/ai-inference` action supports GitHub MCP for read-only access to repos, issues, PRs, users, actions, and code security toolsets. MCP needs a PAT or GitHub App token — the built-in `GITHUB_TOKEN` is not enough for MCP. You select toolsets: `github-mcp-toolsets: 'repos,issues,pull_requests'` ([`actions/ai-inference` README](https://github.com/actions/ai-inference)).

## Security considerations

The main risk is prompt injection through user-controlled content (issue bodies, PR descriptions, comments) passed as model input. To reduce it ([GitHub Docs: Actions Security Hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)):

- Grant minimum permissions — avoid `issues: write` if only read is needed
- Scope `GITHUB_TOKEN` tightly per job
- Use intermediate environment variables for untrusted input rather than inline shell interpolation
- Sensitive headers are not automatically masked — use `::add-mask::` explicitly to redact secrets from logs

## When this backfires

GitHub Models in Actions is a preview feature — model availability, API surface, and rate limits can change without notice, which makes it unsuitable for workflows where reliability guarantees matter. Specific failure conditions:

- Rate limits cause silent failures: GitHub Models applies per-user and per-workflow quotas. Exceeding them causes steps to fail or return empty responses. If your workflow does not assert on response content, failures become invisible.
- Non-determinism persists at temperature:0: constrained single-word output reduces variance but does not remove it. Edge-case inputs (malformed issue bodies, unusually long content) can still produce unexpected output, which makes deterministic branching mis-route.
- Prompt injection cannot be fully mitigated: user-controlled content passed directly into prompts can override instructions regardless of system-prompt framing. Workflows that take irreversible actions (closing issues, applying restrictive labels, modifying code) should require human confirmation for high-stakes outcomes.
- Endpoint vendor lock-in: workflows built on `actions/ai-inference@v1` and the `models: read` permission are GitHub-specific. Porting to other CI platforms means replacing the inference layer.

## Key Takeaways

- `models: read` permission plus `GITHUB_TOKEN` provides zero-configuration AI access in any GitHub Actions workflow
- `.prompt.yml` files version-control prompts with template variables, enabling prompt-as-code practices
- Constrain model output to fixed strings to create deterministic branch points in CI/CD pipelines
- Pre-built labeler and moderator Actions demonstrate the pattern of AI judgment embedded in repository automation
- Treat all user-controlled content as untrusted input when passing to models — apply the same injection defenses used for shell scripts

## Example

A complete workflow that triages new issues using GitHub Models — the prompt file classifies each issue, and the workflow applies labels based on the model's response. For a full pipeline including summarization, routing, and rollout sequencing, see [Continuous Triage](../../workflows/continuous-triage.md).

```yaml
# .github/workflows/issue-triage.yml
name: AI Issue Triage
on:
  issues:
    types: [opened]

permissions:
  models: read
  issues: write

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - id: classify
        uses: actions/ai-inference@v1
        with:
          model: openai/gpt-4.1
          prompt-file: .github/prompts/issue-classifier.prompt.yml
          prompt-file-variables: |
            issue_title=${{ github.event.issue.title }}
            issue_body=${{ github.event.issue.body }}

      - if: steps.classify.outputs.response == 'bug'
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.addLabels({
              ...context.repo,
              issue_number: context.issue.number,
              labels: ['bug', 'needs-triage']
            })

      - if: steps.classify.outputs.response == 'feature'
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.addLabels({
              ...context.repo,
              issue_number: context.issue.number,
              labels: ['enhancement']
            })
```

```yaml
# .github/prompts/issue-classifier.prompt.yml
name: issue-classifier
description: Classify an issue as bug, feature, or question
model: openai/gpt-4.1
modelParameters:
  temperature: 0
messages:
  - role: system
    content: >
      Classify the GitHub issue. Return exactly one word:
      "bug", "feature", or "question". No other output.
  - role: user
    content: |
      Title: {{issue_title}}
      Body: {{issue_body}}
```

The workflow uses `temperature: 0` and single-word constrained output to maximize determinism. The `models: read` permission grants access to GitHub Models through the built-in `GITHUB_TOKEN`, so it needs no additional secrets.

## Related

- [GitHub Agentic Workflows](github-agentic-workflows.md)
- [Prompt Injection Threat Model](../../security/prompt-injection-threat-model.md)
- [Blast Radius Containment: Least Privilege for AI Agents](../../security/blast-radius-containment.md)
- [Secrets Management for Agents](../../security/secrets-management-for-agents.md)
- [MCP Integration with GitHub Copilot](mcp-integration.md)
