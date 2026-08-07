---
title: "Generated Procedure Drivers: Skills That Emit a Program"
term: "Generated Procedure Driver"
description: "A skill whose output is an executable script that walks a person through a manual procedure, useful only where automation genuinely stops."
tags:
  - tool-engineering
  - skills
  - tool-agnostic
aliases:
  - wizard skills
  - agent-generated setup scripts
  - generated setup wizard
last_reviewed: 2026-08-06
maturity: emerging
---

# Generated Procedure Drivers: Skills That Emit a Program

> Where a procedure needs human hands, have the agent generate a script that drives those hands rather than instructions that scroll away.

A generated procedure driver is a skill whose output is an executable program that walks a person through a manual procedure stage by stage and holds the state as it runs. It earns its place at one line only: where automation genuinely stops, and the next step is a key the agent cannot mint or a dashboard it cannot click ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)). Above that line, write the automation. AI Hero's `/wizard` skill is the worked case. It "generates an interactive bash script that walks a human, step by step, through a manual procedure", and "the agent writes the script; it never runs it" ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)).

## When to reach for it

| Situation | Right artifact |
|---|---|
| The provider exposes an API, a CLI, or a Terraform provider | Automation. Interactive setup is the older anti-pattern ([Walter, 2015](https://stef.thewalter.net/installer-anti-pattern.html)) |
| Only a person can mint the credential, accept the terms, or upgrade the plan | A generated driver, which is the line the skill exists to sit on ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)) |
| The transition happens once and never again | A generated driver you run from a scratch path and then delete ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)) |
| The next person on the repo needs the same path | Commit the driver and link it from the README, so they run it instead of re-asking an agent ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)) |

## How the state gets carried

A skill file is static Markdown with no control flow, so it cannot itself hold a position in a procedure. The generated program holds it instead. In the `/wizard` template that means a stage index and a stage total, arrays recording which values were written to `.env`, which became GitHub secrets and which steps were skipped, plus the helpers the authored stages call: `ask`, `ask_secret`, `open_url`, `write_env`, `set_secret` ([template.sh](https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/template.sh)). Re-running is the recovery path. Values already in `.env` come back as defaults, so you press Enter through the stages you got right ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)).

## Why it works

Two causes, both structural. First, the agent has two places to put procedural state and only one of them survives. Simulating the procedure in conversation puts the ordering in a context window and the instructions in scrollback, where both age out. Emitting a program moves them into an artifact with a real runtime. Second, the model is not asked to write the whole program. Everything above the template's `STAGES` marker is fixed and never hand-edited, so generation is constrained to authoring stages against a small vocabulary ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)). Narrowing the target that way is the same mechanism that makes [DSL-constrained generation](../patterns/agent-design/dsl-constraining-harness.md) reliable where free-form generation is not.

A third property follows from the first. Because the agent authors and you execute, captured secrets are typed into a terminal the model is not connected to, so they never reach its context ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)). That holds for values the driver captures at runtime, not for a key you paste into the chat while scoping the procedure ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)).

## When this backfires

- The step is automatable. Stef Walter's case against interactive setup still applies: configuration should carry sane defaults and change through a repeatable surface, because "a theoretically perfect setup process has no interactive choices" ([Walter, 2015](https://stef.thewalter.net/installer-anti-pattern.html)).
- The knowledge is disposable. A driver teaches its own click-path, which Walter calls "useless disposable throw-away knowledge", since changing the same value later takes a different route ([Walter, 2015](https://stef.thewalter.net/installer-anti-pattern.html)).
- Nobody has run the artifact. The authoring agent verifies statically with `bash -n`, `shellcheck` where available, and a trace that each value lands where scoping said it would ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)). Those are syntax and lint checks, not behavior. For scale on how far LLM-produced setup sits from working unaided, EnvBench ran zero-shot and agentic approaches across 329 Python and 665 JVM repositories, and the best configured 6.69% and 29.47% of them ([Eliseeva et al., 2025](https://arxiv.org/abs/2503.14443v1)). Put a confirmation gate in front of anything irreversible.
- The run needs revision. Stages move forward with no back button, and arrow keys in a prompt insert escape sequences instead of moving the cursor, because the prompt uses `read -r` rather than Readline ([mattpocock/skills #741](https://github.com/mattpocock/skills/issues/741)).
- The click-path ages. A driver records the dashboard path mapped at scoping time, and the skill consults the live interface only where it does not already know it ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)). The claim made for a committed driver is that it "can't rot as quietly" as the README it replaces ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)), which is weaker than not rotting.

## Example

The `/wizard` scoping pass reads the repository before it asks anything: `.env*` files, `docker-compose*`, framework config, and every `secrets.*` or `vars.*` reference in `.github/workflows/`. Each reference is a value the driver has to produce. It then shows the ordered stage list for confirmation, and only after that maps each stage to the path a person follows through the provider's dashboard ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)).

Scoping also settles where each captured value lands ([AI Hero, 2026](https://www.aihero.dev/skills-wizard)):

| Destination | When |
|---|---|
| `.env` only | Local development needs it and CI does not |
| GitHub secret | CI reads it and it is sensitive |
| GitHub variable | CI reads it and it is public |
| Both `.env` and a secret | Local development and CI both need it |
| Nowhere | The stage is a pure action, such as flipping a switch |

## Key Takeaways

- Gate the choice on whether an API exists. If one does, write the automation and skip the driver.
- Put the procedure's state in the generated program rather than the conversation: stage position, what was written, what was skipped.
- Fix the template above the authored stages so the model writes only the variable half.
- Keep execution outside the agent, which is what keeps captured secrets out of its context.
- Treat the first run as the test, and put a confirmation gate in front of anything irreversible.

## Related

- [Skill Authoring Patterns: Description to Deployment](skill-authoring-patterns.md) — the canonical home for the skill-authoring rules this shape sits inside.
- [CLI Scripts as Agent Tools: Return Only What Matters](cli-scripts-as-agent-tools.md) — scripts written for the agent to run, the inverse of a script written for you to run.
- [Skill Program Functions](../patterns/agent-design/skill-program-functions.md) — compiles skill guidance into predicates that constrain the agent instead of driving a person.
- [Runbooks as Agent Instructions](../workflows/runbooks-as-agent-instructions.md) — rewriting human procedures so an agent can execute them, the opposite direction of travel.
- [Grill Me: Developer-Initiated Plan Interrogation](../patterns/agent-design/grill-me-technique.md) — a skill that does run multi-turn in the conversation and leaves no artifact behind.
