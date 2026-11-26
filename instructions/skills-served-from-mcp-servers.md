---
title: "Skills Served from MCP Servers in Claude Code: When to Use"
term: "MCP-Served Skills"
description: "An MCP server can ship skills to Claude Code as server:skill. The server owner then controls each version, and headless runs cannot load them at all."
aliases:
  - Skills over MCP
  - MCP skills
tags:
  - instructions
  - claude
  - skills
last_reviewed: 2026-11-25
maturity: emerging
---

# Skills Served from MCP Servers in Claude Code: When to Use

> Skills served from an MCP server change when the server owner changes them, and headless Claude Code runs such as `claude -p` cannot load them.

A skill served from an MCP server is a `SKILL.md` folder that Claude Code fetches from a connected server instead of reading it from disk. The 2.1.332 changelog added the route as a beta, and says skills from MCP servers "show as `server:skill` in the `/` menu; other skills keep their names" ([changelog](https://code.claude.com/docs/en/changelog#2-1-332)). The MCP reference gives the floor as "Claude Code v2.1.331 or later" ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#use-skills-from-mcp-servers)). Take the route when you already own the server and the skill teaches its tools. Keep a procedure you need to pin, review, or run headless somewhere else.

## When this applies

All three conditions hold, or a repo folder or a plugin is the better home:

- You own the server, and the skill describes its tools. The MCP Skills extension says serving skills this way "keeps those instructions with the service they describe" ([MCP Skills extension](https://modelcontextprotocol.io/extensions/skills/overview)).
- People run the skill interactively on a supported setup. Claude Code does not load MCP skills in "cloud sessions, `claude -p`, `claude remote-control` server mode, GitHub Actions, and the Agent SDK", nor over "cloud providers, a custom `ANTHROPIC_BASE_URL`, `apiKeyHelper`, and `ANTHROPIC_AUTH_TOKEN`" ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#where-mcp-skills-are-supported)).
- The skill needs no local frontmatter features. On an MCP skill, Claude Code ignores `allowed-tools`, `hooks`, `model`, `paths` and seven other frontmatter fields, and its `!` commands do not run ([skills docs](https://code.claude.com/docs/en/skills#skills-from-mcp-servers)).

## How it differs from a repo or plugin skill

| Property | Repo folder | Plugin | MCP server |
|---|---|---|---|
| Command name | `/name` | `/plugin-name:skill-name` | `/server:skill`, with a `claude_ai_` or `plugin_` prefix for connector and plugin servers |
| Same name elsewhere | Enterprise beats personal, personal beats project | Both load, because of the namespace | Other skills keep their names |

Names and resolution come from the [skills docs](https://code.claude.com/docs/en/skills#resolve-skills-that-share-a-name), the [MCP docs](https://code.claude.com/docs/en/mcp#run-an-mcp-skill), and the [changelog](https://code.claude.com/docs/en/changelog#2-1-332). The namespace settles the collision question. A local `pdf` skill keeps running as `/pdf`, and a server's `pdf` skill runs as `/docs:pdf`, so a server cannot take over the name of a skill you wrote. What the server does control is the text behind that name.

## The trust cost

A remote server now supplies text the agent follows. The Claude Code docs warn that "Skills can direct Claude to run code. Servers can change skills at any time. Add only servers you trust" ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#safety-of-mcp-skills)). Anthropic scans skills from some claude.ai connectors, and "doesn't scan skills from other connectors or servers, including Directory servers added with `claude mcp add`."

Your permission mode decides who approves a load. "When Claude loads an MCP skill in auto mode, the default, you don't see a prompt. The classifier decides whether the skill loads, without reading it" ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#approvals-for-mcp-skills)). Manual and `acceptEdits` mode show a prompt. Selecting **Allow this version** skips the prompt and the classifier until the server changes the skill's files.

## Why it works

The MCP Skills extension makes server-delivered text checkable, though not trusted. Each listing carries either a manifest with "each file's URI, SHA-256 digest, and byte size" or, for generated content, the value `"dynamic"`, which hosts may decline. For a manifest, "Persisted approval MUST bind to the complete set of file URIs and digests. A changed, added, or removed file revokes that approval" ([MCP Skills extension](https://modelcontextprotocol.io/extensions/skills/overview)). This page reads Claude Code's rule, an approval that holds "until the server changes the skill's files", as this binding at work. The extension states its own limit: "Digests establish consistency with the server's manifest, not trust in its content."

## When this backfires

- Unattended pipelines. A skill that a `claude -p` job or a GitHub Action depends on does not load there.
- Auto mode on a server you do not control. Noma Security's analysis notes that skills "resist rug-pull attacks because they are usually static files requiring manual updates" ([Help Net Security](https://www.helpnetsecurity.com/2026/05/05/ai-agent-security-skills-blind-spots/)). An MCP skill gives that up, and auto mode shows no prompt when it loads.
- Team and Enterprise rollouts. With `/login` on those plans, MCP skills are "off until your organization turns them on" ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#requirements-for-skills-from-mcp-servers)).
- Version checks. The feature is a public beta, and its two official sources already disagree by one release. The changelog files it under 2.1.332, and the MCP reference names 2.1.331 as the minimum.

## Example

The Claude Code docs use a server named `docs` with a `pdf` skill. Its name is `docs:pdf`, and `/docs:pdf report.pdf` runs it on a file ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#run-an-mcp-skill)). Permission rules then set how much the server can change without you seeing it ([Claude Code MCP docs](https://code.claude.com/docs/en/mcp#block-a-servers-skills-or-ask-first)):

| Goal | List | Rule |
|---|---|---|
| Prompt each time Claude loads one, even in auto mode (a typed command needs no approval) | `ask` | `Skill(mcp__docs__*)` |
| Block only the `pdf` skill | `deny` | `Skill(docs:pdf)` |
| Block every skill from the server | `deny` | `Skill(mcp__docs__*)` |

An `allow` rule for the same pattern skips the prompt, but only for servers added at user or local scope and for managed servers. It does not work for connectors, `.mcp.json` servers, or plugin servers.

## Key Takeaways

- Serve a skill from an MCP server when you own that server and the skill teaches its tools.
- Keep a repo copy of any skill that `claude -p`, GitHub Actions, or the Agent SDK must run.
- Expect `allowed-tools`, hooks, and `!` commands to be ignored on an MCP skill.
- Add an `ask` rule for any server you do not run, because in auto mode a classifier, not you, decides whether a changed version loads, and you see no prompt.

## Related

- [Skill Packs: Registry Distribution Needs Pinning Discipline](skill-pack-registry-distribution.md)
- [Workspace-Hosted Skills: Authorship Outside the Repo](workspace-hosted-skills.md)
- [Shipping a Shared Agent Toolkit as a Versioned Plugin](shared-toolkit-plugin-ownership.md)
- [Agent Config as a Managed Supply Chain](agent-config-as-managed-supply-chain.md)
- [MCP Metadata Approval View Gap](../security/mcp-metadata-approval-view-gap.md)
