---
title: "GitHub Copilot: Customization Primitives and Stack"
description: "How to extend Copilot with instructions, prompt files, agents, skills, hooks, MCP servers, memory, Spaces, and content exclusions across all surfaces."
tags:
  - training
  - copilot
---

# GitHub Copilot: Customization Primitives

> Copilot's customization primitives — instructions, prompt files, agents, skills, hooks, MCP servers, memory, Spaces, and content exclusions — let you override default behavior at increasing levels of specificity. Each addresses a different problem: guidance, enforcement, tool access, or persistent context.

Ten primitives compose to control what the agent knows, how it behaves, and what it can do. The [Surface Map](surface-map.md) covers what each surface does — the sections below cover how to extend and constrain them.

---

## The Customization Stack

Copilot ships with capable defaults. The customization stack lets you override those defaults at increasing levels of specificity:

```
Organization instructions     ← broadest: every repo, every user (GitHub.com + coding agent only)
Repository instructions       ← per-repo conventions
Path-specific instructions    ← scoped to file patterns
Prompt files                  ← reusable prompt templates
Custom agents                 ← specialized personas
Skills                        ← structured task knowledge
Hooks                         ← lifecycle enforcement
MCP servers                   ← external tool integration
Memory                        ← persistent learned context
Spaces                        ← curated context containers
Content exclusions            ← admin-level file access control (limited scope)
```

Each layer addresses a different problem. Instructions tell the agent *what to do*. Agents tell it *who to be*. Skills tell it *how to do a specific task*. Hooks *enforce rules it can't override*. MCP servers *extend what tools it can use*. Memory *persists what it learns*. Spaces *curate what context the agent sees*.

They compose — a custom agent can reference skills, consume MCP server tools, and operate under the constraints of both instructions and hooks simultaneously.

**Chat Customizations Editor** (v1.113+ Preview): A [unified interface](https://code.visualstudio.com/updates/v1_113) organizing custom instructions, prompt files, custom agents, and agent skills into separate tabs with an embedded code editor and marketplace access. Open it from the Copilot chat panel settings.

### Surface Support Overview

| Primitive | VS Code | GitHub.com | CLI | Coding Agent |
|-----------|:-------:|:----------:|:---:|:------------:|
| Organization instructions | — | ✓ (Chat, code review) | — | ✓ |
| Repository instructions | ✓ | ✓ | ✓ | ✓ |
| Path-specific instructions | ✓ | — | ✓ | ✓ |
| Personal instructions | — | ✓ | — | — |
| Prompt files | ✓ | — | — | — |
| Custom agents | ✓ | ✓ | ✓ | ✓ |
| Skills | ✓ | ✓ | ✓ | ✓ |
| Hooks | ✓ (Preview) | — | ✓ | ✓ |
| MCP servers | ✓ | ✓ | ✓ | ✓ |
| Memory | — | ✓ (code review) | ✓ | ✓ |
| Spaces | ✓ | ✓ | — | — |

---

## Custom Instructions

### What it is

Markdown files that inject context into every Copilot interaction. Three organizational tiers, applied from broadest to most specific, plus a personal tier in VS Code.

### Used for

Encoding conventions, constraints, and context that Copilot would otherwise have to infer: stack details, build commands, test commands, coding standards, naming rules, architecture decisions, prohibited patterns.

### When to use it

Every non-trivial repository should have at least a repository-wide instructions file. If you've corrected Copilot for the same thing twice, put it in instructions.

### When NOT to use it

- Don't write an encyclopedia. Long instructions dilute important rules — Copilot's attention to any single instruction decreases as the total volume grows.
- Don't duplicate what's already in code (linter configs, type definitions, `tsconfig.json`). Copilot reads those directly.
- Don't use instructions for enforcement — use hooks for rules the agent must not be able to override.

---

### Organization Instructions

**What it is**: Instructions set by org admins, applied to every repo and every user on supported surfaces (GitHub.com and the coding agent).

**Configured in**: GitHub.com → Organization Settings → Copilot → Custom instructions.

**Used for**: Company-wide coding standards, security policies, approved patterns, compliance rules. Applied silently — individual users don't see them in their workspace.

**When to use it**: Standards that apply across all repositories — language preferences, security practices, forbidden patterns.

**When NOT to use it**: Rules specific to a single repo or codebase area. Those belong in repository or path-specific instructions.

**Surfaces**: GitHub.com (Chat, code review) and the coding agent. Not currently supported in VS Code or the CLI.

---

### Repository Instructions (`.github/copilot-instructions.md`)

**What it is**: A Markdown file at the root of `.github/` injected into every Copilot session in this repository. Applied to all requests regardless of which files are open.

**Used for**: Repo-specific conventions — stack details, build/test commands, architectural rules, do-not-do lists.

**When to use it**: Every non-trivial repository. This is the highest-leverage, lowest-effort customization. If you've ever corrected Copilot for the same thing twice, put it here.

**When NOT to use it**: Rules that only apply to a subset of files — use path-specific instructions instead. Rules that must be enforced mechanically — use hooks.

**Surfaces**: All four. The coding agent reads it from the default branch. The CLI and VS Code read it from the working directory.

**How to use it**:

```markdown
# Project: Payments API

## Stack
- Node.js 22, TypeScript 5.4, Fastify 4
- Postgres via Drizzle ORM
- Vitest for tests

## Conventions
- All handlers are async and use the `asyncWrapper` from `src/middleware/async.ts`
- Error classes live in `src/errors/` — use them, don't throw raw Error objects
- Database access only through repository classes in `src/repositories/`

## Build & Test
- `npm run build` — TypeScript compile
- `npm test` — run Vitest suite (unit + integration)
- `npm run test:db` — integration tests (requires local Postgres on port 5432)

## Do not
- Import directly from `src/db/connection.ts` — use repositories
- Use `any` types
- Write tests that mock the database (use the real test DB)
```

**What makes a good instructions file**: Actionable rules, not descriptions. Short enough that every line gets attention. Focus on things Copilot gets wrong without guidance — it already reads your code, types, and configs.

---

### Path-Specific Instructions (`.github/instructions/*.instructions.md`)

**What it is**: Instructions that apply only when Copilot works with files matching an `applyTo` glob pattern. They merge with repository-wide instructions when both match — they don't replace them.

**Used for**: Different rules for different parts of the codebase — frontend components, API routes, database migrations, infrastructure config.

**When to use it**: A rule applies to a subset of files and would dilute the global instructions file. Keeps repo-wide instructions lean and focused.

**When NOT to use it**: The rule is universal to the repo — put it in `.github/copilot-instructions.md` instead.

**Surfaces**: VS Code, CLI, coding agent. Not supported on GitHub.com.

**How to use it**:

```markdown
---
applyTo: "src/components/**/*.tsx,src/components/**/*.ts"
---

Use React functional components with hooks. Never class components.
Use Tailwind CSS utility classes — no inline styles or CSS modules.
All components must export a props interface named `{ComponentName}Props`.
```

The `applyTo` field supports standard glob patterns (`*`, `**`, comma-separated). An optional `excludeAgent` field restricts the instruction to specific surfaces (e.g., `excludeAgent: "coding-agent"` prevents these instructions from applying to the coding agent).

---

### Personal Instructions (GitHub.com)

**What it is**: Instructions configured in your GitHub personal settings that apply to all Copilot interactions on GitHub.com, regardless of what repo-level instructions exist.

**Used for**: Your personal preferences — language style, response format, coding conventions — that follow you across repos on GitHub.com.

**When to use it**: Preferences that aren't repo-specific and should apply wherever you use Copilot on GitHub.com (Chat, code review).

**When NOT to use it**: Rules the team should share — those belong in repository instructions.

**Surfaces**: GitHub.com only (Chat, code review). Not available in VS Code, CLI, or the coding agent.

**How to configure**: GitHub.com → Settings → Copilot → Personal instructions.

> **Note**: The VS Code setting `github.copilot.chat.codeGeneration.instructions` was deprecated in VS Code 1.102. Use file-based instructions (`.instructions.md` files) for IDE-level customization instead.

---

### Priority Cascade

When multiple tiers apply to the same request:

```
Personal > Repository > Organization
```

More specific instructions take precedence over more general ones. Path-specific instructions merge with repository-wide instructions when both match — they layer, not replace.

**In practice**: An organization instruction says "use camelCase." A repository instruction says "use snake_case for database columns." A path-specific instruction for `src/components/` says "prefix event handler props with `on`." All three apply simultaneously to a React component file — the agent follows all three because they address different concerns. When instructions conflict on the same concern, the more specific one wins.

### Further reading

- [Instruction File Ecosystem](../../instructions/instruction-file-ecosystem.md) — how CLAUDE.md, copilot-instructions.md, and AGENTS.md converge
- [copilot-instructions.md Convention](../../tools/copilot/copilot-instructions-md-convention.md) — Copilot-specific instructions best practices
- [CLAUDE.md Convention](../../instructions/claude-md-convention.md) — Claude Code's equivalent instruction file
- [AGENTS.md Design Patterns](../../instructions/agents-md-design-patterns.md) — executable commands, code-over-prose, tier boundaries
- [Layered Instruction Scopes](../../instructions/layered-instruction-scopes.md) — how instruction scopes stack in multi-tool environments
- [Instruction Compliance Ceiling](../../instructions/instruction-compliance-ceiling.md) — how adherence varies by specificity and format
- [Instruction Polarity](../../instructions/instruction-polarity.md) — positive vs negative framing for agent compliance
- [System Prompt Altitude](../../instructions/system-prompt-altitude.md) — positioning prompts in the instruction hierarchy
- [Prompt Layering](../../context-engineering/prompt-layering.md) — how instructions stack from system prompt through user message

---

## Prompt Files

### What it is

Markdown files in `.github/prompts/` that define reusable prompt templates. Each file becomes a selectable option in the VS Code chat input — effectively a custom command you can invoke by name.

### Used for

Standardising how the team asks Copilot for specific task types. Encodes the "how to ask" knowledge so consistent quality doesn't depend on who writes the prompt.

### When to use it

A task is repeated often by multiple team members and prompt quality matters for output quality: code reviews against a checklist, migration patterns, test generation with specific conventions, documentation templates.

### When NOT to use it

- One-off or exploratory tasks — the overhead isn't worth it.
- Tasks that need a persistent persona with tool restrictions — use a custom agent.
- Tasks with structured multi-step procedures and resource files — use a skill.

### How to use it

Create `.github/prompts/NAME.prompt.md`:

```markdown
Review the API handler in #file:../../src/routes/users.ts for:
1. Missing input validation
2. Unhandled error cases
3. N+1 query patterns
4. Missing auth checks

Suggest fixes with code snippets.
```

Reference workspace files with `#file:` relative paths. Referenced files are injected into context when the prompt is used.

Select prompt files from the attachment menu (📎) in the VS Code chat input. They appear alongside file references and other context sources.

### Surface support

| Surface | Supported | Notes |
|---------|:---------:|-------|
| VS Code | ✓ | Select from the chat attachment menu |
| Visual Studio | ✓ | Same as VS Code |
| JetBrains | Preview | |
| CLI | — | Not supported — use skills or instructions instead |
| GitHub.com | — | Not available in web chat |
| Coding agent | — | Use skills or instructions instead |

Prompt files work in IDEs (VS Code, Visual Studio, JetBrains). For surfaces without prompt file support (CLI, GitHub.com, coding agent), encode the same knowledge as a skill (if it has steps and resources) or in instructions (if it's a simple rule).

### Further reading

- [Prompt File Libraries](../../instructions/prompt-file-libraries.md) — storing reusable parameterized templates in `.github/prompts/`
- [Prompt Governance via PR](../../instructions/prompt-governance-via-pr.md) — PR-based governance for prompt file changes across teams

### Prompt files vs instructions vs agents vs skills

| You need… | Use |
|-----------|-----|
| Rules that always apply automatically | Instructions |
| A reusable prompt invoked on demand | Prompt file |
| A specialized persona with tool/model constraints | Custom agent |
| A structured procedure with steps and resource files | Skill |

---

## Custom Agents

### What it is

Markdown files in `.github/agents/` that define specialized agent profiles. Each agent has a name, description, system prompt, and optional tool/model constraints. Think of them as roles: a `docs-writer`, a `security-reviewer`, a `test-specialist`.

### Used for

Giving the agent domain-specific expertise, constraints, and a consistent persona that goes beyond what instructions provide. Instructions say "follow these rules." An agent says "you are a security reviewer — here's how you think about code."

### When to use it

The default Copilot behaviour produces consistent friction for a category of task, and you can articulate the better behaviour as a system prompt. Agents are for repeatable task types where the specialization pays off every time.

### When NOT to use it

- One-off tasks — the setup cost isn't justified.
- Simple constraints ("use Vitest, not Jest") — put that in instructions.
- Structured step-by-step procedures with resource files — use a skill.

### How to use it

Create `.github/agents/AGENT-NAME.agent.md` (`.agent.md` is the conventional extension; `.md` also works):

```markdown
---
description: Reviews pull requests for security vulnerabilities
tools:
  - read_file
  - search_code
model: claude-sonnet-4-5
---

You are a security reviewer for this TypeScript/Node.js project.

When reviewing code:
- Check for injection vulnerabilities (SQL, command, path traversal)
- Verify authentication and authorization on every endpoint
- Flag hardcoded secrets or credentials
- Check that user input is validated before use
- Verify error messages don't leak internal details

Read the full diff before commenting. Only flag real issues — no style nits.
```

### Frontmatter fields

| Field | Required | Purpose |
|-------|:--------:|---------|
| `description` | **Yes** | Shown in the VS Code dropdown and used for agent selection — be specific |
| `tools` | No | Restrict which tools the agent can use (allowlist) |
| `mcp-servers` | No | Additional MCP servers available to this agent |
| `model` | No | Override the default model |
| `target` | No | Restrict to a surface: `vscode` or `github-copilot` |
| `name` | No | Display name — defaults to filename stem |
| `user-invocable` | No | Whether the agent appears in the mode selector for manual invocation |

The body (below the frontmatter) is the system prompt.

### Surface support

| Surface | How it works |
|---------|-------------|
| **VS Code** | Appears in the agents dropdown alongside Ask, Agent, and Plan. Select it to activate the agent's persona and constraints for the session. |
| **GitHub.com** | Available for the coding agent when assigning tasks. |
| **CLI** | Available in interactive sessions. |
| **JetBrains** | Preview support. |
| **Coding agent** | Assignable when creating a task. The agent's system prompt and constraints apply in the Actions sandbox. Use `target: github-copilot` to restrict an agent to only the coding agent surface. |

### How agents compose with other primitives

Agents inherit repository and organization instructions — the agent prompt layers on top, it doesn't replace the instruction stack. An agent can also:

- **Reference MCP servers** via the `mcp-servers` frontmatter field, gaining access to tools from those servers.
- **Use skills** — if a skill matches the task, the agent's context includes the skill's `SKILL.md` and resources.
- **Operate under hooks** — hooks fire regardless of which agent is active.

### Custom agents vs built-in agents

Custom agents appear in the same agents dropdown as Ask, Agent, and Plan. The difference: built-in agents define *how* Copilot interacts with your workspace (read-only, autonomous, plan-first). Custom agents define *who* Copilot is for the session — a persona with domain expertise, tool restrictions, and a specific model. A custom agent runs in Agent mode by default (autonomous, with tool access).

### Further reading

- [Custom Agents & Skills in Copilot](../../tools/copilot/custom-agents-skills.md) — defining custom agents with specialized tools and MCP servers
- [Domain-Specific System Prompts](../../instructions/domain-specific-system-prompts.md) — building system prompts for specialized agents
- [Agent Composition Patterns](../../agent-design/agent-composition-patterns.md) — how agents compose with other primitives
- [Controlling Agent Output](../../agent-design/controlling-agent-output.md) — constraining what agents produce

---

## Skills

### What it is

Directories in `.github/skills/` containing a `SKILL.md` file plus optional resource files — templates, scripts, reference docs, example files. A skill packages the knowledge needed to perform a specific task type: not just *what* to do, but *how*, with ordered steps, tools, and supporting files.

### Used for

Encoding repeatable procedures that any agent could follow if they had the documentation: generating changelogs, running migration playbooks, scaffolding components, performing audit checklists, importing data in a specific format.

### When to use it

The task has a known, documented procedure with defined steps, and the agent needs supporting files (templates, scripts, reference material) beyond what fits in an instructions file.

### When NOT to use it

- Simple rules ("use Vitest") → instructions.
- A persona with tool/model constraints → custom agent.
- The task can be described in 3 sentences → it doesn't need a skill.

### How to use it

Create a directory under `.github/skills/` (lowercase, hyphen-separated):

```
.github/skills/generate-changelog/
  SKILL.md              ← required — description, steps, resource references
  template.md           ← changelog format template
  scripts/
    fetch-commits.sh    ← helper script
```

`SKILL.md` (uppercase, required):

```markdown
---
name: generate-changelog
description: Generates a CHANGELOG.md entry from recent commits
---

Generate a CHANGELOG.md entry for the current release.

## Steps
1. Run `scripts/fetch-commits.sh` to get commits since the last tag
2. Group commits by type: Features, Bug Fixes, Breaking Changes, Other
3. Use `template.md` as the format template
4. Prepend the entry to CHANGELOG.md — do not replace existing entries
5. Omit chore/ci/docs commits

## Resources
- template.md — changelog entry format
- CHANGELOG.md — existing changelog to prepend to
```

Skills follow the [Agent Skills open standard](https://agentskills.io). A skill written for GitHub Copilot works in Claude Code and other compatible tools without modification.

### Surface support

| Surface | How it works |
|---------|-------------|
| **VS Code** | Agent mode discovers and uses skills when the task matches the skill's description. `SKILL.md` and referenced resources are injected into context. |
| **GitHub.com** | Available for coding agent tasks initiated from the web. |
| **CLI** | Same as VS Code — the CLI agent discovers skills from the working directory. |
| **Coding agent** | Reads skills from the repo's default branch. Uses them when the task matches the skill's description. |

### Skill selection

The agent decides whether to use a skill based on the `description` field in the frontmatter. Write descriptions that clearly state what the skill does and when it applies — vague descriptions lead to the skill being missed or misapplied. The description is the skill's "trigger."

### Personal vs repository skills

| Location | Scope |
|----------|-------|
| `.github/skills/` | This repo — committed, shared with the team |
| `~/.copilot/skills/` | All repos on your machine — personal, not committed. Check CLI docs for current path. |
| `~/.claude/skills/` | Claude Code personal skills (same standard, different tool) |

### Skills vs agents

| | Agent | Skill |
|-|-------|-------|
| **Defines** | Who the agent is (persona, constraints) | How to do a task (steps, resources) |
| **Format** | Single `.agent.md` file | Directory with `SKILL.md` + resource files |
| **Composable** | An agent *uses* skills | A skill is used *by* agents |
| **Portable** | Copilot-specific | Cross-tool via Agent Skills standard |

An agent can use a skill. A skill can be used by any agent. Design them to compose.

### Further reading

- [Skill Authoring Patterns](../../tool-engineering/skill-authoring-patterns.md) — practical patterns for building, testing, and troubleshooting skills
- [Skill Frontmatter Reference](../../tool-engineering/skill-frontmatter-reference.md) — complete SKILL.md frontmatter field reference
- [Skill as Knowledge](../../tool-engineering/skill-as-knowledge.md) — how skills function as encoded domain knowledge
- [Skill Library Evolution](../../tool-engineering/skill-library-evolution.md) — managing skill libraries as projects grow
- [On-Demand Skill Hooks](../../tool-engineering/on-demand-skill-hooks.md) — lifecycle hooks for skills triggered on demand

---

## Hooks

### What it is

A `hooks.json` file that registers shell commands to execute at specific points in the agent's lifecycle. Hooks run **outside** the agent's context — the agent cannot see, skip, or reason about them. They are enforcement, not guidance.

### Used for

Security validation before tool use, audit logging, policy enforcement (block writes to protected paths), custom notifications, automated checks that must run regardless of what the agent decides.

### When to use it

When a rule must be enforced mechanically. If the agent ignoring the rule would cause real harm — security violations, data corruption, compliance failures — use a hook. The agent can misinterpret or ignore instructions. It cannot bypass a hook.

### When NOT to use it

- Guidance the agent should follow but could reasonably override in edge cases → use instructions.
- Don't replicate what linters, formatters, or CI already enforce.
- Keep hooks fast. Every `preToolUse` hook runs synchronously before every tool call. Heavy hooks add cumulative latency across an agent session.

### How to configure

Create any `.json` file under `.github/hooks/` (e.g., `.github/hooks/security.json`):

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "type": "command",
        "bash": "scripts/check-path.sh",
        "powershell": "scripts/check-path.ps1",
        "timeoutSec": 10
      }
    ],
    "sessionStart": [
      {
        "type": "command",
        "bash": "echo \"[$(date -u)] Session started\" >> .copilot-audit.log",
        "powershell": "Add-Content .copilot-audit.log \"Session started: $(Get-Date)\"",
        "timeoutSec": 5
      }
    ]
  }
}
```

Both `bash` and `powershell` fields are supported for cross-platform compatibility. The agent harness picks the right one for the current OS.

### Lifecycle events

The CLI and coding agent support six events (camelCase):

| Event | Fires when | Common use |
|-------|-----------|------------|
| `sessionStart` | Agent session begins | Audit logging, environment setup |
| `sessionEnd` | Agent session ends | Cleanup, summary logging |
| `userPromptSubmitted` | User sends a prompt | Input validation, prompt logging |
| `preToolUse` | Before any tool call | Path restrictions, security checks, policy enforcement |
| `postToolUse` | After a tool call completes | Output validation, notification |
| `errorOccurred` | An error fires in the agent | Error reporting, alerting |

VS Code supports a different set of eight events (PascalCase):

| Event | Fires when | Common use |
|-------|-----------|------------|
| `SessionStart` | Agent session begins | Environment setup |
| `UserPromptSubmit` | User sends a prompt | Input validation |
| `PreToolUse` | Before any tool call | Security checks, path restrictions |
| `PostToolUse` | After a tool call completes | Output validation |
| `PreCompact` | Before conversation context is compacted | Context preservation, logging |
| `SubagentStart` | A subagent begins execution | Subagent monitoring |
| `SubagentStop` | A subagent completes | Subagent output validation |
| `Stop` | Agent stops executing | Resource cleanup, final checks |

### Surface support

| Surface | How it works |
|---------|-------------|
| **VS Code** | Preview (v1.109+). Reads `.github/hooks/*.json` from the workspace. Uses the PascalCase event set above. |
| **GitHub.com** | Not applicable. |
| **CLI** | Reads `.github/hooks/*.json` from the current working directory. Hooks execute locally on your machine with your user permissions. Uses the camelCase event set above. |
| **Coding agent** | Reads `.github/hooks/*.json` from the repo's default branch. Hooks execute inside the GitHub Actions sandbox with the same constraints as the agent. Uses the camelCase event set above. |

### Hooks vs instructions

| | Instructions | Hooks |
|-|-------------|-------|
| **Nature** | Guidance — the agent reads and interprets them | Enforcement — the agent can't see or override them |
| **Mechanism** | Injected into context as text | Shell commands executed by the harness |
| **Failure mode** | Agent may ignore, misinterpret, or override | Hook blocks the action mechanically |
| **Performance** | No runtime cost | Synchronous execution adds latency per tool call |
| **Use for** | Conventions, preferences, architecture patterns | Security policy, audit requirements, hard constraints |

**Rule of thumb**: If the consequence of violation is "the code is inconsistent," use instructions. If the consequence is "production data is exposed," use a hook.

### Further reading

- [Hook Catalog](../../tool-engineering/hook-catalog.md) — practical reference of high-value hooks for guardrails and enforcement
- [Hooks Lifecycle Events](../../tool-engineering/hooks-lifecycle-events.md) — detailed documentation of all lifecycle events
- [Claude Code Hooks Lifecycle](../../tools/claude/hooks-lifecycle.md) — Claude Code's hook system (SessionStart, PreToolUse, PostToolUse)
- [Skill-Tool Runtime Enforcement](../../tool-engineering/skill-tool-runtime-enforcement.md) — runtime enforcement patterns for tool control

---

## MCP Servers

### What it is

[Model Context Protocol](https://modelcontextprotocol.io/) servers extend the agent's tool set with external capabilities — databases, APIs, monitoring systems, project management tools. The agent calls MCP tools the same way it calls built-in tools (file read, search, terminal).

### Used for

Connecting the agent to systems it can't reach natively: Sentry for error context, Jira or Linear for issue details, Notion for documentation, databases for schema queries, custom internal APIs.

### When to use it

The task requires data or actions from an external system, and you want the agent to access it directly rather than through manual copy-paste or shell scripts.

### When NOT to use it

- The external system has a CLI or REST API the agent can call via shell/curl — an MCP server may be unnecessary overhead.
- The **coding agent** only supports MCP **tool calls** — resources and prompts are not available. VS Code supports tools, resources, and prompts from MCP servers.
- Untrusted MCP servers are a security risk — they can inject arbitrary content into the agent's context via tool responses.

### Configuration per surface

#### VS Code

In `.vscode/mcp.json` (primary) or `.vscode/settings.json`:

```json
// .vscode/mcp.json
{
  "servers": {
    "sentry": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${env:SENTRY_AUTH_TOKEN}"
      }
    }
  }
}
```

MCP servers configured here are available in Agent mode and to custom agents that include the server in their `mcp-servers` frontmatter field. VS Code supports MCP tools, resources, and prompts.

#### CLI

The Copilot CLI reads MCP configuration from its config file. Use the `/mcp` slash command in an interactive session to list configured servers [unverified].

#### Coding Agent

In GitHub.com → Settings → Code & automation → Copilot → Coding agent, add MCP server configuration as JSON. Supports `local`, `stdio`, `http`, and `sse` transport types.

```json
{
  "sentry": {
    "type": "http",
    "url": "https://mcp.sentry.io/sse",
    "headers": {
      "Authorization": "Bearer ${secrets.SENTRY_TOKEN}"
    }
  }
}
```

The coding agent runs in a GitHub Actions sandbox — `stdio` and `local` servers must be installable in that environment. Remote (`http`/`sse`) servers are typically more practical for the coding agent.

#### GitHub.com

Not supported in the web chat interface. MCP servers for the coding agent are *configured* on GitHub.com, but web chat itself cannot call MCP tools.

### Surface support summary

| Surface | Transport types | Configuration location | MCP capabilities |
|---------|----------------|----------------------|-----------------|
| **VS Code** | `stdio` | `.vscode/mcp.json` or settings.json | Tools, resources, prompts |
| **CLI** | `stdio` | `~/.copilot/mcp-config.json` | Tools |
| **Coding agent** | `local`, `stdio`, `http`, `sse` | GitHub.com → Settings → Code & automation → Copilot → Coding agent | Tools only |

### Further reading

- [MCP Client-Server Architecture](../../tool-engineering/mcp-client-server-architecture.md) — transport, tool design, error handling, security
- [MCP Server Design](../../tool-engineering/mcp-server-design.md) — tool naming, schema design, error handling, token efficiency
- [MCP Client Design](../../tool-engineering/mcp-client-design.md) — lifecycle management, multi-server routing, observability
- [Copilot MCP Integration](../../tools/copilot/mcp-integration.md) — Copilot-specific MCP server guidance
- [Copilot Extensions to MCP Migration](../../tool-engineering/copilot-extensions-to-mcp-migration.md) — migrating from Copilot extensions to MCP
- [Tool Description Quality](../../tool-engineering/tool-description-quality.md) — writing tool descriptions that enable proper routing
- [Token-Efficient Tool Design](../../tool-engineering/token-efficient-tool-design.md) — optimizing tool definitions for token efficiency

---

## Memory

### What it is

Persistent knowledge that Copilot stores about your repository — coding conventions, patterns, preferences, project structure details — and reuses across sessions. Memory is learned through interaction, not configured through files.

### Used for

Reducing repetitive corrections. Instead of re-explaining your conventions each session, Copilot remembers them. Memory complements instructions with learned context that you haven't formalised into a file.

### When to use it

You find yourself repeatedly correcting Copilot about repo-specific details that aren't important enough to add to the instructions file — minor preferences, project quirks, one-off conventions.

### When NOT to use it

- Critical rules → use instructions. Memory is best-effort context, not guaranteed enforcement.
- Sensitive information → memory persists at the repository level and may be visible to other collaborators.
- Instructions are deterministic (always applied). Memory is probabilistic (applied when the model judges it relevant).

### Surface support

| Surface | How it works |
|---------|-------------|
| **VS Code** | Not supported. |
| **GitHub.com** | Used by Copilot code review on pull requests. |
| **CLI** | Reads and writes repository-level memories during interactive sessions. |
| **Coding agent** | Reads repository-level memories. Stores new memories during task execution. |

Memory is stored at the repository level — all collaborators with access share the same memory pool. Memories are automatically deleted after 28 days. Enabled by default for Pro and Pro+ users (public preview as of March 2026).

### Memory vs instructions

| | Instructions | Memory |
|-|-------------|--------|
| **Source** | You write them in a file | Copilot learns them through interaction |
| **Reliability** | Always applied (deterministic) | Applied when judged relevant (probabilistic) |
| **Visibility** | Readable in the repo | Managed through Copilot settings |
| **Use for** | Rules that must always apply | Context that's helpful but not critical |

**Lifecycle**: When a memory proves consistently useful, promote it to the instructions file. Memory is where conventions are discovered; instructions are where they're codified.

### Further reading

- [Agent Memory Patterns](../../agent-design/agent-memory-patterns.md) — persisting knowledge across conversations with scoped memory systems
- [Copilot Memory](../../tools/copilot/copilot-memory.md) — Copilot's autonomous memory: citation-based verification, cross-agent sharing, self-healing
- [Episodic Memory Retrieval](../../agent-design/episodic-memory-retrieval.md) — storing and retrieving problem-solving episodes for agent learning
- [Memory Synthesis from Execution Logs](../../agent-design/memory-synthesis-execution-logs.md) — synthesizing memory from logs for cross-session learning
- [Subtask-Level Memory](../../agent-design/subtask-level-memory.md) — granular memory organization at the subtask level

---

## Spaces

### What it is

Named context collections on GitHub.com that aggregate repositories, code files, pull requests, issues, notes, images, and uploads into a curated container. GA since September 2025, replacing Knowledge Bases (sunset November 2025).

### Used for

Curating the reference material that Copilot uses when answering questions. Instead of hoping Copilot finds the right files via `#codebase`, you pre-select the relevant code, documentation, issue context, and even write explanatory notes. The agent sees exactly what you intended — no more, no less.

### When to use it

- **Large, multi-team codebases** where automatic context selection misses relevant material or surfaces too much noise.
- **Cross-repo context** — a Space can pull from multiple repositories, which no instruction file or skill can do.
- **Onboarding bundles** — curate the key files, ADRs, and issues that a new team member needs to understand a system.
- **Recurring task templates** — a "telemetry event" Space with the event schema, SDK wrapper, and prior PRs, reused every time someone adds a new event.

### When NOT to use it

- Small repos where `#codebase` already surfaces the right context. The curation overhead isn't worth it.
- Rules and constraints — those belong in instructions. Spaces are for *reference material*, not *behavioural rules*.
- Sensitive data you wouldn't want accessible via Copilot Chat — Space contents are available to anyone with access to the Space.

### How it works

A Space contains **sources** (things that sync automatically) and **uploads** (things you add manually):

| Source type | Auto-syncs | Notes |
|------------|:----------:|-------|
| Repositories | ✓ | Entire repo or specific paths |
| Code files | ✓ | Individual files from any accessible repo |
| Pull requests | ✓ | PR description, diff, and comments |
| Issues | ✓ | Issue body and comments |
| Notes | — | Free-text Markdown you write directly in the Space |
| Images / uploads | — | Diagrams, screenshots, design mockups |

GitHub sources (repos, files, PRs, issues) stay current as code evolves. Notes and uploads require manual updates.

### The three-layer context stack

Spaces sit in the middle of a three-layer context model:

```
Instruction files     → behavioural rules ("always use Vitest, never mock the DB")
Copilot Spaces        → reference material (specs, schemas, ADRs, example code)
Ad-hoc chat context   → conversation-specific files and references
```

Instructions tell the agent *how to behave*. Spaces tell it *what to know about*. Ad-hoc references fill one-off gaps.

### Access control

| Ownership | Visibility options |
|----------|-------------------|
| **Organization** | Private, shared with specific teams, or org-wide. Tiered RBAC — viewers only see sources they already have GitHub permission to access. |
| **Individual** | Private, shared with collaborators, or public (view-only). |

### Surface support

| Surface | How it works |
|---------|-------------|
| **GitHub.com** | Create, edit, and chat with Spaces from github.com/copilot/spaces. |
| **VS Code** | Reference a Space in chat. Spaces appear alongside other context sources. |
| **CLI** | Not directly supported — use instruction files or skills instead. |
| **Coding agent** | Not directly referenced. For coding agent context, use instruction files, skills, or MCP servers. |

### Spaces vs instructions vs skills

| You need… | Use |
|-----------|-----|
| Rules that always apply automatically | Instructions |
| Curated reference material for Q&A | Space |
| A structured procedure with steps and resource files | Skill |
| Learned conventions that persist across sessions | Memory |

### Further reading

- [Copilot Spaces](../../tools/copilot/copilot-spaces.md) — full architecture, RBAC model, and practical composition patterns

---

## Content Exclusions

**What it is**: An admin-level control (Copilot Business/Enterprise) that prevents Copilot from accessing or suggesting content from specified files and repositories.

**Scope**: Inline completions and non-agent chat modes. **Content exclusions are not respected by Agent mode (in any IDE), the CLI, or the coding agent.** This is a significant limitation — if you rely on exclusions for compliance, be aware that agent-based workflows bypass them. See [Content Exclusion Gap](../../instructions/content-exclusion-gap.md) for a detailed analysis of this gap and mitigation strategies.

**Configured in**: Organization or enterprise settings on GitHub.com. Manageable via the REST API (added February 2026, public preview).

---

## Decision Framework: Which Primitive?

| Problem | Primitive | Why |
|---------|-----------|-----|
| Copilot keeps using the wrong test framework | Repository instructions | Universal rule, always applied |
| Frontend and backend have different conventions | Path-specific instructions | Scoped to file patterns |
| The team asks for code reviews inconsistently | Prompt file | Standardises the prompt for a repeatable task |
| Need a specialist for security reviews | Custom agent | Persona with tool/model constraints |
| Changelog generation follows a 5-step procedure | Skill | Structured steps with template files |
| The agent must never write to `/migrations/` | Hook (`preToolUse`) | Hard enforcement the agent can't override |
| The agent needs Sentry context for bug fixes | MCP server | External tool integration |
| Ground answers in specific code/docs | Copilot Spaces | Curated context containers, shareable across team |
| Copilot forgets your naming convention each session | Memory → instructions | Start with memory; promote to instructions when confirmed |

### Composition example

A repository that uses the full stack:

```
.github/
  copilot-instructions.md            ← "We use Drizzle ORM, Vitest, async handlers"
  instructions/
    frontend.instructions.md         ← "React + Tailwind for src/components/**"
    api.instructions.md              ← "Fastify conventions for src/routes/**"
  prompts/
    review-api.prompt.md             ← "Review this handler for auth + validation"
  agents/
    security-reviewer.agent.md       ← Security review persona, restricted tools
    test-writer.agent.md             ← Test generation persona, specific model
  hooks/
    hooks.json                       ← Block writes to /migrations/, audit logging
  skills/
    generate-changelog/
      SKILL.md                       ← 5-step changelog procedure with template
```

Instructions provide baseline context. Path-specific instructions refine per directory. The prompt file standardises a recurring ask. Agents specialise for task categories. The hook enforces a hard constraint. The skill packages a procedure. MCP servers (configured in settings, not in `.github/`) connect external tools. Memory fills gaps the instructions don't cover yet.

---

## Key Takeaways

- **Instructions are the highest-leverage, lowest-effort customization**. Start there. Every non-trivial repo needs `.github/copilot-instructions.md`.
- **Match the primitive to the problem**: guidance → instructions, reusable prompt → prompt file, persona → agent, procedure → skill, enforcement → hook, external tools → MCP, curated context → Spaces.
- **Surface support varies significantly**. Repository instructions work on all surfaces. Organization instructions only work on GitHub.com and the coding agent. Prompt files work in IDEs only. Hooks run in VS Code (Preview), the CLI, and the coding agent — but with different event sets. Check the support matrix before investing effort.
- **Hooks and instructions serve different purposes**. Instructions are guidance the agent interprets. Hooks are enforcement the agent cannot override. Using one when you need the other creates either false confidence or unnecessary rigidity. Note: CLI/coding agent and VS Code support different lifecycle events.
- **Skills are portable** across tools via the [Agent Skills open standard](https://agentskills.io). A skill written for Copilot works in Claude Code without modification.
- **Memory is a stepping stone**. It captures learned conventions. When a memory proves consistently useful, promote it to the instructions file where it's guaranteed to apply.
- **Content exclusions have limited scope**. They apply to inline completions and non-agent chat. Agent mode, the CLI, and the coding agent bypass them entirely.
- **The primitives compose**. An agent can use skills, consume MCP tools, and operate under hooks and instructions simultaneously. Design them to layer, not overlap.

## Related

**Training**

- [GitHub Copilot: Platform Surface Map](surface-map.md) — all surfaces in depth
- [GitHub Copilot: Context Engineering & Agent Workflows](context-and-workflows.md) — context design, task decomposition, and steering
- [GitHub Copilot: Advanced Patterns](advanced-patterns.md) — multi-agent orchestration and automation
- [GitHub Copilot: Harness Engineering](harness-engineering.md) — making codebases agent-ready with enforcement and legibility
- [GitHub Copilot: Team Adoption & Governance](team-adoption.md) — rolling out Copilot with progressive autonomy and shared configuration
- [GitHub Copilot: Model Selection & Routing](model-selection.md) — model roster, premium multipliers, and override strategies

**Context & Instructions**

- [Context Engineering](../../context-engineering/context-engineering.md) — foundational discipline of designing what enters agent context windows
- [Context Priming](../../context-engineering/context-priming.md) — pre-loading relevant files before agent tasks
- [Dynamic System Prompt Composition](../../context-engineering/dynamic-system-prompt-composition.md) — building system prompts dynamically based on state
- [Context Compression Strategies](../../context-engineering/context-compression-strategies.md) — reducing context consumption while preserving signal
- [Critical Instruction Repetition](../../instructions/critical-instruction-repetition.md) — when and how to repeat critical instructions across layers

**Tool Engineering**

- [Tool Engineering](../../tool-engineering/tool-engineering.md) — foundational principles for designing tools agents can use
- [Advanced Tool Use](../../tool-engineering/advanced-tool-use.md) — advanced patterns for agent-tool interactions
- [Poka-Yoke Agent Tools](../../tool-engineering/poka-yoke-agent-tools.md) — error-proofing tool design
- [Tool Minimalism](../../tool-engineering/tool-minimalism.md) — keeping tool surfaces small and focused

**External**

- [GitHub Copilot docs](https://docs.github.com/en/copilot)
- [Agent Skills standard](https://agentskills.io)
- [GitHub Changelog](https://github.blog/changelog/)
