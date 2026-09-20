---
title: "Skill or MCP Server: Choosing a Capability's Delivery Mechanism"
term: "Capability Delivery Selection"
description: "Decide per capability whether to ship it as a skill or an MCP server, using four measurable inputs: standing token cost, credential location, enforcement strength, and revocation path."
aliases:
  - skill versus MCP server selection
  - capability delivery mechanism choice
  - choosing between a skill and an MCP server
tags:
  - tool-engineering
  - agent-design
  - tool-agnostic
  - skills
  - mcp
last_reviewed: 2026-09-19
maturity: adopted
---

# Skill or MCP Server: Choosing a Capability's Delivery Mechanism

> Choose the server when the credential or the guarantee must live outside the agent, and the skill when readable guidance is enough.

Credential location and enforcement strength settle most capabilities on their own, usually before anything is measured. Two further inputs are conditional. Standing token cost only bites above a threshold your harness may not have reached, and revocation only matters where someone has to prove a capability was switched off. Run all four per capability rather than once for the team, because one codebase normally produces different answers for different jobs.

## The four inputs

| Input | Skill | MCP server |
|---|---|---|
| Standing token cost | About 100 tokens per skill, always; under 5k when triggered ([Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)) | About 55k tokens for five common servers, before any work ([Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)) |
| Credential location | None held, so the agent's own process does the work | Held at the server, which must "only accept tokens specifically intended for themselves" ([MCP Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)) |
| Enforcement | Advisory. Trajectories covered "only 38.66–45.51% of the extracted skill behavior constraints on average" ([Tan et al., 2026](https://arxiv.org/abs/2606.20659v2)) | A call either happens or does not, and the spec tells clients to log tool usage for audit purposes ([MCP Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)) |
| Revocation | Bound to skill identity, so an edit after install "inherits the original approval" ([Li et al., 2026](https://arxiv.org/abs/2604.02837v1)) | Disable the endpoint, or revoke the grant at the provider |

Get your own numbers before the token row decides anything. Claude's docs put the line at "10 or more tools available" or "tool definitions consume more than 10k tokens" ([Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)). Below that line the context argument is noise. Whether a server's definitions sit in context at all is a separate call, covered in [MCP alwaysLoad](mcp-eager-vs-jit-loading.md), and the [cost ratio between the two shapes swings with the scaffolding](mcp-cli-cost-ratio-scaffolding-bound.md).

Reuse across clients used to sit on this list and no longer belongs there. Agent Skills is an open standard, and Copilot reads `SKILL.md` from `.github/skills/`, `.claude/skills/`, and `.agents/skills/` in [VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills) and the Copilot CLI ([GitHub changelog, 2025-12-18](https://github.blog/changelog/2025-12-18-github-copilot-now-supports-agent-skills/)). Both mechanisms are portable now, so portability decides nothing.

## Why it works

The two mechanisms put the capability's authority in different places, and that placement produces every number above. An MCP server keeps the capability in a separate process behind a typed schema, which [Li et al., 2026](https://arxiv.org/abs/2604.02837v1) describe as having "preserved a partial data-to-instruction boundary". The credential stays at that boundary, and the definitions are billed into context whether the capability gets used or not. A skill puts the capability in text the agent reads at trigger time, inside a package whose "co-location of natural language instructions and executable scripts within a single filesystem package collapses the distinction between capability specification and code execution". That is cheap to load and followed less than half the time. The general form of the second axis, advice against guarantee, is worked through in [Skill Authoring as Software Engineering](skill-authoring-software-engineering.md).

## When this backfires

- The capability needs a live credential and you reach for a skill anyway. Skills on the Claude API run with "No network access" and no runtime package installation ([Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)), so that surface cannot deliver the capability as a skill at all.
- You read the readability of Markdown as auditability. A skill's grant is persistent and, per [Li et al., 2026](https://arxiv.org/abs/2604.02837v1), "irrevocable by content change", because trust binds to the skill's identity rather than to "a cryptographically committed version of its content". An operator asked to prove the capability is off has more to show with a server.
- The library is already large. The ~100 tokens are charged per skill, so sixty skills stand at roughly 6k tokens of description text competing for the same match, and one that never wins costs its share and returns nothing.
- You are below the threshold. With fewer than ten tools, moving a capability into a skill to save context saves an amount nobody can measure.
- You standardize instead of deciding. Carrying both mechanisms costs two review paths and two revocation paths. Where every capability in the codebase wraps an authenticated API, skip the per-capability procedure and run the servers.

## Example

Two capabilities from one team, decided with the table above.

Filling a PDF form ships as a skill. There is no credential and no remote state, and the bundled `fill_form.py` runs through bash, where "the script's code never loads into the context window" ([Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)). The agent carries about 100 tokens of description until a request matches it.

Reading GitHub issues ships as a server. The capability needs an OAuth grant that must not enter the model's context, and the client can log every call. GitHub is one of the five servers in the ~55k-token measurement ([Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)), so the team defers its definitions behind tool search rather than paying that on every request.

The hybrid falls out of the same reading. A capability that needs the credential and also needs house conventions applied to it puts the call in the server and the procedure in a skill. Treat that as the answer two inputs produced, not as a way to avoid choosing.

## Key Takeaways

- Ask the credential question and the enforcement question first. If either has a hard answer, stop there; the token arithmetic will not overturn it.
- A skill instruction is advice, and the measured follow-through is 38.66–45.51% of constraints. Anything that must happen every time needs a call site.
- A skill's approval survives edits to its content, so "it is Markdown, so we can review it" is a claim about the first read rather than about the version running today.
- Cross-client reuse stopped being a discriminator once Copilot and VS Code began reading `SKILL.md`.
- Below ten tools or 10k tokens of definitions, the context argument decides nothing.

## Related

- [Auth-Isolation as the MCP-vs-CLI Selection Heuristic](mcp-auth-isolation-vs-cli-selection.md) — the same credential question, decided against a CLI rather than a skill
- [MCP alwaysLoad: Classifying Servers as Eager or Just-in-Time](mcp-eager-vs-jit-loading.md) — whether a server's definitions sit in context, once you have chosen the server
- [Skill Authoring as Software Engineering: What Transfers](skill-authoring-software-engineering.md) — the advice-against-guarantee axis in its general form
- [Skill as Knowledge Pattern](skill-as-knowledge.md) — what belongs inside a skill once you have chosen one
- [Separation of Knowledge and Execution](../patterns/agent-design/separation-of-knowledge-and-execution.md) — the layered framing this decision sits inside
