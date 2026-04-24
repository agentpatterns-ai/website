---
title: "Google ADK Skills: Portable SKILL.md Across ADK Agents"
description: "Google ADK implements the Agent Skills standard via the SkillToolset — SKILL.md directories load through list_skills, load_skill, and load_skill_resource tools at L1, L2, and L3."
tags:
  - tool-engineering
  - instructions
  - tool-agnostic
aliases:
  - ADK SkillToolset
  - Google ADK agent skills
---

# Google ADK Skills

> Google ADK implements the Agent Skills standard through the `SkillToolset` class, loading `SKILL.md` directories via three auto-generated tools mapped to the L1/L2/L3 progressive disclosure levels.

!!! note "Also known as"
    ADK SkillToolset, Google ADK agent skills. For the portable format, see [Agent Skills Standard](../standards/agent-skills-standard.md); for authoring rules, see [Skill Authoring Patterns](skill-authoring-patterns.md).

ADK Skills is marked **Experimental** in ADK Python v1.25.0+ ([ADK Skills docs](https://google.github.io/adk-docs/skills/)).

## How ADK Maps the Spec

ADK conforms to the [agentskills.io specification](https://agentskills.io/specification) directory format: a `SKILL.md` entrypoint with YAML frontmatter and body, plus optional `references/`, `assets/`, and `scripts/` subdirectories ([ADK Skills docs](https://google.github.io/adk-docs/skills/)). A directory authored for Claude Code, Cursor, or Gemini CLI loads in ADK unchanged via `load_skill_from_dir(...)` ([Google Developers Blog](https://developers.googleblog.com/developers-guide-to-building-adk-agents-with-skills/)).

The [`SkillToolset`](https://google.github.io/adk-docs/skills/) auto-generates three tools that map to progressive disclosure levels:

| Tool | Level | Payload | Loaded |
|------|-------|---------|--------|
| `list_skills` | L1 | Frontmatter `name` + `description` | Every turn |
| `load_skill` | L2 | `SKILL.md` body | When agent selects the skill |
| `load_skill_resource` | L3 | One file from `references/`, `assets/`, or `scripts/` | When L2 instructions reference it |

Google reports ~90% baseline context reduction for an agent with 10 skills: ~1k tokens of L1 metadata instead of ~10k tokens of monolithic instructions ([Google Developers Blog](https://developers.googleblog.com/developers-guide-to-building-adk-agents-with-skills/)).

## Inline Skills — ADK-Specific

ADK adds a second authoring mode beyond file-based `SKILL.md`: inline skills defined in Python via `models.Skill(frontmatter=..., instructions=..., resources=...)` ([ADK Skills docs](https://google.github.io/adk-docs/skills/)). Inline skills embed references as in-memory strings rather than files, enabling runtime skill mutation — including agents that generate new skills at runtime ([Google Developers Blog](https://developers.googleblog.com/developers-guide-to-building-adk-agents-with-skills/)). Portable `SKILL.md` directories remain the only format that travels to non-ADK tools.

## Skills vs. A2A Multi-Agent Composition

Skills scope to the agent that owns the `SkillToolset`. In an ADK multi-agent team using the [A2A protocol](https://adk.dev/a2a/intro/), each agent carries its own skill registry; A2A routes tasks between agents but does not share skills across them. Sharing happens at the filesystem layer — multiple agents can `load_skill_from_dir` the same directory independently.

## When Skills Earn Their Cost

Skills add overhead: L1 metadata injects into every turn, and `load_skill` costs an extra LLM round-trip before the agent acts. For a single-purpose agent that activates the same skill every turn, a plain `instruction=` block on the agent is strictly faster — skills are designed for agents with many capabilities that activate one or two per conversation ([MindStudio: progressive disclosure tradeoffs](https://www.mindstudio.ai/blog/progressive-disclosure-ai-agents-context-management)).

Cross-language status: skill support is documented for **ADK Python**; parity with [ADK Go](https://developers.googleblog.com/adk-go-10-arrives/) and ADK Java is not confirmed in the skills documentation — verify against the target SDK's release notes before authoring skills for a non-Python runtime.

## Example

A file-based skill loaded into an ADK agent ([ADK Skills docs](https://google.github.io/adk-docs/skills/)):

```python
import pathlib
from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather_skill"
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="skill_user_agent",
    tools=[skill_toolset.SkillToolset(skills=[weather_skill])],
)
```

The `weather_skill/` directory follows the agentskills.io layout — `SKILL.md` at root, optional `references/`, `assets/`, `scripts/` — and loads in Claude Code or Gemini CLI without changes.

## Key Takeaways

- ADK conforms to the agentskills.io directory spec; file-based skills are portable across Claude Code, Cursor, Gemini CLI, and ADK
- `SkillToolset` exposes three tools — `list_skills` (L1), `load_skill` (L2), `load_skill_resource` (L3) — mirroring progressive disclosure levels
- Inline `models.Skill` is ADK-specific and enables runtime skill generation; only `SKILL.md` directories travel to other tools
- Skills scope to a single agent in A2A teams; share via filesystem, not the A2A protocol
- Skip Skills for single-purpose agents where `instruction=` is equivalent and faster

## Related

- [Agent Skills: Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)
- [Skill Authoring Patterns](skill-authoring-patterns.md)
- [SKILL.md Frontmatter Reference](skill-frontmatter-reference.md)
- [A2A Protocol](../standards/a2a-protocol.md)
