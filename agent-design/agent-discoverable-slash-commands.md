---
title: "Agent-Discoverable Slash Commands"
description: "Slash commands promoted to model-callable primitives — the agent's planner can discover and invoke user-authored workflows mid-loop, collapsing the wall between human-invoked and agent-invoked capabilities."
tags:
  - agent-design
  - tool-engineering
  - tool-agnostic
aliases:
  - Model-invocable slash commands
  - Agent-invokable commands
---

# Agent-Discoverable Slash Commands

> Slash commands become model-callable primitives when the agent's planner can read their descriptions and invoke them mid-loop — collapsing the boundary between user-invoked shortcuts and agent-invoked tools.

## The Shift

Slash commands were a human surface — typed in the prompt bar, invisible to the planner. Treating them as model-discoverable turns `/review`, `/refresh-context`, or `/commit` into callable nodes in the planner's tool graph.

Claude Code 2.1.108 (April 14, 2026) shipped the shift: the model can now discover and invoke built-in slash commands like `/init`, `/review`, and `/security-review` via the Skill tool ([Claude Code changelog](https://code.claude.com/docs/en/changelog)). Cursor 2.4 (January 2026) added the same — Agent Skills are detected automatically after a name-and-description pre-scan ([Cursor 2.4 changelog](https://cursor.com/changelog/2-4)).

When the planner invokes a command directly, user-authored workflows become reusable tool-graph nodes — `/research-topic` becomes a planning step a supervisor agent selects. This extends the split in [Agents vs Commands](agents-vs-commands.md): commands gain the "who" dimension previously owned by agents, without erasing what-vs-how.

## The Control Matrix

Claude Code exposes two frontmatter fields that gate the user/agent axis ([Skills reference](https://code.claude.com/docs/en/skills)):

| Frontmatter | User can invoke | Agent can invoke | When loaded into context |
|---|---|---|---|
| (default) | Yes | Yes | Description always in context; body loads on invocation |
| `disable-model-invocation: true` | Yes | No | Description not in context; body loads when user invokes |
| `user-invocable: false` | No | Yes | Description always in context; body loads on invocation |

Side-effectful commands (`/deploy`, `/commit`, `/send-slack-message`) should set `disable-model-invocation: true` — Anthropic: "you don't want Claude deciding to deploy because your code looks ready" ([Skills reference](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill)). Background-knowledge skills set `user-invocable: false` — `/legacy-system-context` is not an action users would type.

## Descriptions Become Tool Descriptions

The `description` sits in the system prompt at all times ([Skills reference](https://code.claude.com/docs/en/skills#skill-content-lifecycle)) and drives agent invocation. Four rules from tool-description craft ([Anthropic best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions)):

1. **Third person** — "Processes Excel files", not "I can help you…" — point-of-view shift causes discovery misses.
2. **Both what and when** — "Extract text from PDFs. Use when the user mentions PDFs, forms, or document extraction." Trigger phrases anchor selection.
3. **Specific over vague** — "Fills PDF forms and merges documents" selects when those verbs appear; "Helps with documents" selects nothing reliably.
4. **Front-load the use case** — combined `description` and `when_to_use` is truncated at 1,536 characters in the skill listing ([Skills reference](https://code.claude.com/docs/en/skills)).

Negative triggers constrain over-firing: `Do NOT use for Jira or GitHub Issues workflows`.

## The Idempotency Contract

User invocation is an explicit authorisation signal; agent invocation is not. Commands written for humans assume the user read the conversation and will catch mistakes — the planner gives neither guarantee. Model-invokable commands need:

- **Up-front input validation** — reject obviously wrong arguments rather than acting on them
- **Read-only first** — a `/review` that only reads is safer to promote than a `/commit` that writes
- **Two-step destructive ops** — plan/execute split lets the planner stage changes without committing

When a command cannot be [idempotent](idempotent-agent-operations.md), default to `disable-model-invocation: true`.

## Permission Controls

Claude Code exposes allow/deny rules — `Skill(name)` for exact match, `Skill(name *)` for any arguments ([Skills reference](https://code.claude.com/docs/en/skills#restrict-claudes-skill-access)):

```text
Skill(commit)        # allow
Skill(review-pr *)   # allow with any args
Skill(deploy *)      # deny
```

The `allowed-tools` frontmatter pre-approves tools while the skill runs — a `/commit` skill can include `Bash(git add *) Bash(git commit *)` without per-use approval. That pre-approval surface expands with every model-invocable command.

## When This Backfires

1. **Destructive side effects without `disable-model-invocation`** — the agent infers authorisation from context that looked "ready" and runs a command the user would have reviewed. The failure is silent.
2. **Large skill libraries** — descriptions are shortened to fit a character budget (default 8,000 characters, scaling at 1% of the context window), stripping trigger keywords ([Skills reference](https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short)). 40+ skills degrades triggering across the board.
3. **Prompt injection surface** — a tool output or README naming a skill can cause the planner to invoke it with attacker-controlled arguments. Every model-invocable command wrapping a side-effectful tool expands this surface.
4. **Commands authored pre-shift** — existing commands often reference "the user's last message" or emit prose confirmations instead of structured results. Agent invocation breaks those assumptions.

## Counterpoint: MCP Keeps the Boundary

The [Model Context Protocol](../standards/mcp-protocol.md) takes the opposite stance: MCP `prompts` are user-controlled — exposed as slash commands or menu options — while `tools` are model-controlled ([MCP Prompts spec](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts)). Erasing that boundary is a choice, not inevitable convergence: typing `/deploy` is itself the authorisation. Claude Code and Cursor accept that trade-off for planner composability; MCP does not.

## Example

A `/review-pr` command written in Claude Code's skill format. The description names the trigger phrases the planner matches against, the negative trigger prevents over-firing on unrelated requests, and the absence of `disable-model-invocation` makes it model-callable because the operation is read-only.

```yaml
---
name: review-pr
description: Reviews a pull request for correctness, style, and security issues.
  Use when the user asks for a PR review, mentions a PR number, or asks to check
  diff quality before merge. Do NOT use for general code review outside a PR
  (use the code-review skill instead).
argument-hint: "[pr-number]"
allowed-tools: Bash(gh pr *)
---

Review PR $ARGUMENTS:

1. Fetch the diff with `gh pr diff $ARGUMENTS`
2. Scan for: missing tests, unhandled errors, suspicious secrets
3. Return findings as a structured list
```

Contrast with a `/deploy` command, where `disable-model-invocation: true` is non-negotiable because the operation is destructive and the agent inferring "ready to ship" from context is not equivalent to the user explicitly authorising release:

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
allowed-tools: Bash(./scripts/deploy.sh *)
---

Deploy $ARGUMENTS to production:
1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

The matrix pattern scales: every new command is a three-state decision — default (both), `disable-model-invocation` (user-only), or `user-invocable: false` (agent-only).

## Key Takeaways

- Promoting commands to model-invokable turns them into reusable planner primitives, not just keyboard shortcuts
- Command descriptions now carry the craft previously reserved for tool descriptions: trigger phrases, third person, negative triggers, front-loaded use case
- The three-state matrix (default, `disable-model-invocation: true`, `user-invocable: false`) is a per-command decision — destructive side effects default to user-only
- Permission rules (`Skill(name)`, `Skill(name *)`) and `allowed-tools` pre-approvals make the trust surface explicit
- MCP's user-controlled `prompts` vs model-controlled `tools` is the opposite design choice — the boundary is deliberate, not inevitable

## Related

- [Agents vs Commands: Separation of Role and Workflow](agents-vs-commands.md)
- [Skill Authoring Patterns: Description to Deployment](../tool-engineering/skill-authoring-patterns.md)
- [SKILL.md Frontmatter Reference](../tool-engineering/skill-frontmatter-reference.md)
- [Prompt File Libraries for Reusable Agent Instructions](../instructions/prompt-file-libraries.md)
- [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)
- [Permission-Gated Commands](../security/permission-gated-commands.md)
- [Progressive Disclosure for Agent Definitions](progressive-disclosure-agents.md)
- [Controlling Agent Output](controlling-agent-output.md)
