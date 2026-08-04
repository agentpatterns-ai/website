---
title: "Skill Loadout Curation for Coding Agents"
term: "Skill Loadout Curation"
description: "Curate the skills and MCP servers an agent loads before a session — above roughly 30, the gain comes from removing colliding descriptions, not from saving tokens."
aliases:
  - agent skill loadout
  - tool loadout pattern
  - skill loadout curation
tags:
  - context-engineering
  - agent-design
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-08-03
maturity: adopted
---

# Skill Loadout Curation for Coding Agents

> A loadout is the skill set an agent carries into a session; past roughly 30 skills, extras shadow the right one and selection degrades.

A loadout is everything an agent loads before you type a word. It includes the name and description of every installed skill, plus the tools of every connected MCP server ([Breunig, 2026](https://www.dbreunig.com/2026/07/24/manage-your-agent-s-loadout-with-dr-skill.html)). Curating it means choosing what to carry in, beyond what you author. Candidates come from published catalogs too, such as AI Hero's index of its engineering skills ([AI Skills for Real Engineers](https://www.aihero.dev/skills-catalog)). The practice pays above roughly 30 skills. The gain comes from removing descriptions that collide, not from saving tokens.

## When curation pays

The discipline is conditional. Four things decide whether it returns anything.

| Condition | Why it matters |
|---|---|
| The catalog exceeds about 30 skills or tools | Retrieval precision holds at low counts, breaks up across candidate positions 31–70, and collapses "beyond position ~100" ([Gan and Sun, 2025](https://arxiv.org/abs/2505.03275)). Below that range there is no measurable loss to recover. |
| Two or more descriptions overlap | Selection fails when a distractor describes itself the way the right skill does. Without overlap, catalog size alone costs little. |
| A weaker model does the routing | At a 202-skill library, Claude Haiku 4.5 loses 0.26 pass rate against Sonnet 4.6's 0.15 ([Song and Wei, 2026](https://arxiv.org/abs/2605.24050)). Small models break far earlier: Llama 3.1-8B fails a query given 46 tools and succeeds given 19, in the same 16K context ([Paramanayakam et al., 2024](https://arxiv.org/abs/2411.15399)). |
| Skills arrive by default | Drew Breunig describes an enterprise agent that silently loaded over 600 colleague-authored skills, and the Hermes agent shipping nearly 100 ([Breunig, 2026](https://www.dbreunig.com/2026/07/24/manage-your-agent-s-loadout-with-dr-skill.html)). |

## Prune for collision, not for size

The intuitive reason to prune — idle skills waste context — is the weaker one. Song and Wei split the damage from a growing library into two channels and measured each. Skill shadowing, where the agent picks a distractor whose description matches the query better than the right skill does, costs 0.14 pass rate (95% CI [0.06, 0.26]). Context overhead costs 0.07 (CI [-0.13, 0.25]), indistinguishable from zero ([arxiv:2605.24050](https://arxiv.org/abs/2605.24050)).

So deleting your largest skill usually changes nothing. Renaming or merging two skills that describe themselves the same way is what moves the number.

[Progressive disclosure](../patterns/agent-design/progressive-disclosure-agents.md) explains the weak token channel. Anthropic preloads only each skill's name and description, loading the body when the skill triggers, so the content behind a skill is "effectively unbounded" ([Anthropic, 2025](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)). Disclosure caps what an idle skill costs; it does nothing about telling two similar descriptions apart.

## Auditing a loadout

Ask three questions in order: what is loaded, what collides, and what actually gets used. The `drskill` scanner answers all three ([Breunig, 2026](https://github.com/dbreunig/drskill)).

- `drskill list --harness claude-code` prints the effective skill set for one harness with token counts.
- `drskill scan` checks 34 issue categories across skills and MCP servers; its first skill check is skills that shadow each other. The `--deep` flag uses a model to judge whether two descriptions collide or two scopes overlap.
- `drskill audit` reads your traces and reports which skills and tools were actually called, and on which queries.

The trace report is the pruning signal that matters. A skill that never appears in traces is either invisible to the router or redundant, and both diagnoses point at its description rather than its length.

## Why it works

The causal channel is selection interference, not context pressure. An agent chooses a skill by matching the request against the preloaded descriptions, so every added skill is another distractor competing for that match. When a distractor fits the request better than the intended skill, the router picks it every time — Song and Wei's worked case is a video-frame-extraction skill that beat the intended skill on a coin-counting query in every trajectory they ran ([arxiv:2605.24050](https://arxiv.org/abs/2605.24050)). Because the interference happens between descriptions, cutting the candidate set is what recovers accuracy: restricting candidates by retrieval lifts tool selection from 13.62% to 43.13% while roughly halving prompt tokens ([Gan and Sun, 2025](https://arxiv.org/abs/2505.03275)).

## When this backfires

- Small catalogs. Under about 30 skills the degradation this practice targets has not started ([Gan and Sun, 2025](https://arxiv.org/abs/2505.03275)), so curation costs attention and returns nothing.
- Pruning by token weight. Removing the heaviest skill can leave the shadowing pair intact, so the symptom survives the cleanup.
- Unpredictable task mixes. You pick a loadout before you know the task. Exploratory debugging crosses domains, and a removed skill becomes a silent capability gap rather than a visible error.
- Shared repositories. A per-developer loadout makes agent behavior irreproducible: a skill present locally and absent in CI changes outcomes with no committed code change.
- Strong routers on moderate catalogs. Sonnet 4.6 degrades roughly half as much as Haiku 4.5 at the same 202 skills ([Song and Wei, 2026](https://arxiv.org/abs/2605.24050)), so the better the model, the thinner the return.

An automated alternative competes with curation directly: retrieve skills on demand from a large corpus instead of enumerating a fixed set ([Su et al., 2026](https://arxiv.org/abs/2604.24594)). Where such a retrieval layer exists, invest in description hygiene and let it do the selecting.

## Example

Breunig's Hermes agent kept invoking the wrong note-taking skill. Inspecting the machine showed Hermes ships with nearly 100 skills. Deleting the stock note-taking skill helped but did not fully fix the behavior, because the remaining collisions were in descriptions he had not yet found. That gap is what motivated a scanner rather than more manual deletion ([Breunig, 2026](https://www.dbreunig.com/2026/07/24/manage-your-agent-s-loadout-with-dr-skill.html)).

The corrective sequence is diagnostic, not subtractive:

```bash
drskill list --harness claude-code   # what this harness actually sees
drskill scan --deep                  # which descriptions collide or overlap
drskill audit                        # which skills traces show being called
```

## Key Takeaways

- A loadout is what an agent loads before your first message: every installed skill's metadata plus every connected MCP server's tools.
- The measurable harm of a large catalog is skill shadowing, not token cost; context overhead is statistically indistinguishable from zero.
- Curation earns its keep above roughly 30 skills, and earlier on smaller or weaker models.
- Prune for colliding descriptions and for skills absent from traces, not for the biggest files.
- Where an on-demand skill retrieval layer exists, description hygiene beats hand-curating a per-task set.

## Related

- [Compositional Skill Routing](compositional-skill-routing.md) — routing among skills at invocation time, once they are already present
- [Reducing System-Prompt Token Bloat in Coding Agents](system-prompt-bloat-reduction.md) — measuring the fixed prefix that a loadout contributes to
- [Cost-Aware Skill Rewriting](../instructions/cost-aware-skill-rewriting.md) — what to keep inside a skill you decide to carry
- [Contractual Skill Files](../instructions/contractual-skill-files.md) — writing the description a router has to discriminate on
- [Skill Authoring as Software Engineering: What Transfers](../tool-engineering/skill-authoring-software-engineering.md) — the authoring-time counterpart; single responsibility is what keeps a description from shadowing its siblings
