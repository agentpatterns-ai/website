---
title: "Skill as Instruction Surface and Callable API (Interpreter Skills)"
term: "Skill as Instruction Surface and Callable API"
description: "Ship a SKILL.md plus an importable module so the model decides when the behavior fires while the runtime executes a reviewed, testable function — the named, versionable unit on top of an embedded code interpreter."
tags:
  - tool-engineering
  - agent-design
  - instructions
  - tool-agnostic
aliases:
  - skill module importable interpreter
  - skill with importable module
last_reviewed: 2026-06-03
status: current
---

# Skill as Instruction Surface and Callable API (Interpreter Skills)

> A skill that ships both a SKILL.md and an importable module the interpreter can call — the model picks when, the runtime picks how.

Interpreter skills bundle the instruction surface of a regular skill with a code module the agent's embedded interpreter can `import` and execute. The model still decides *when* the behavior applies and *what inputs* to pass; the procedure itself lives in reviewable, testable code rather than in instructions the model has to read and carry out correctly ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)). This pattern only applies inside a harness that exposes an interpreter to the model — see [When the Conditions Hold](#when-the-conditions-hold).

## When the Conditions Hold

Four conditions must all hold; outside them, a regular instruction skill, a `scripts/`-bearing skill under the Agent Skills standard, or plain [programmatic tool calling](code-interpreter-as-agent-tool.md) dominate.

| Condition | Why it matters |
|----------|----------------|
| The harness exposes an in-loop interpreter | The `module:` field is dead syntax in a harness with no `await import("@/skills/...")` path. LangChain Deep Agents ships one; Claude Code, Copilot, and Cursor today do not ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)). |
| The procedure should be fixed across calls | The packaged module is the deterministic anchor. If the agent should adapt the join order, skip steps, or pick a different strategy per input, pinning the procedure blocks the adaptation. "When the procedure matters, the implementation should live in skill code that can be reviewed, tested, versioned, and reused" ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)). |
| There is an OS-level sandbox for any untrusted input | The interpreter's narrow default surface is a context discipline, not a security boundary. LangChain is explicit it does not replace process or VM isolation ([LangChain, 2026-05-20](https://www.langchain.com/blog/give-your-agents-an-interpreter)). |
| The procedure is heavy enough to warrant a module | A one-line normalization is overhead as a module; inline instructions plus a regular tool call serve better below a few hundred lines of helper code. |

## The Two Surfaces

A regular Agent Skill is a directory with a `SKILL.md` whose frontmatter and body the agent reads progressively — metadata first, body on activation, supporting files on demand ([Agent Skills Specification](https://agentskills.io/specification)). The standard defines `name`, `description`, optional `allowed-tools`, and optional `metadata`, plus `scripts/`, `references/`, and `assets/` subdirectories. It does not define a `module:` frontmatter field.

LangChain's Deep Agents adds the `module:` key. The value is a JavaScript or TypeScript file path relative to the skill directory ([LangChain Skills docs](https://docs.langchain.com/oss/python/deepagents/skills)). The agent imports the module from inside interpreter code:

```typescript
const { triage } = await import("@/skills/github-triage");
```

`SKILL.md` is how the agent discovers the behavior; `index.ts` is what the interpreter executes. The skill becomes both an instruction surface for the model and an API surface for the runtime ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)).

## Why It Works

Interpreter skills relocate the procedural part of a skill from model-mediated execution — instructions the model reads and tries to follow correctly — to runtime-mediated execution: an imported function the interpreter calls. The *trigger* (when to invoke the procedure) stays with the model; the *body* (how the procedure runs) moves to code that can be reviewed, tested, and versioned ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)).

That relocation defeats two known failure modes of instruction-only skills: instruction fade-out across long-context trajectories ([Bui, 2025 §3.2](https://arxiv.org/abs/2603.05344)) and the compliance ceiling at high instruction counts — frontier models reach only 68% accuracy at 500 instructions ([IFScale, 2025](https://arxiv.org/abs/2507.11538)). Neither applies to a function call. The model's only correctness obligation is the `import` and its arguments, which a fixture corpus can check exactly.

The same intermediate-state argument that powers [filter-and-aggregate-in-execution-environment](../context-engineering/filter-aggregate-execution-env.md) and [Code Interpreter as a Primary Agent Tool](code-interpreter-as-agent-tool.md) applies here — keep working values in the runtime, not in model context. LangChain's early measurement on the OOLONG `trec-coarse` task showed ~35% fewer tokens when programmatic calls go through the interpreter ([LangChain, 2026-05-20](https://www.langchain.com/blog/give-your-agents-an-interpreter)); Anthropic's Programmatic Tool Calling measures ~37% reduction on multi-step research benchmarks ([Anthropic, advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)). Interpreter skills inherit the saving because the module's intermediate values never become model input. The packaging adds discovery (progressive disclosure of the description), an audit trail (one path, one diff), and a documented import surface on top of that runtime base.

## What an Interpreter Skill Can Do That a Script-Bearing Skill Cannot

The Agent Skills standard's `scripts/` directory already supports executable code — Claude Code, for example, reads `SKILL.md` over bash, then invokes scripts under `scripts/` via bash subprocess without loading either the script source or its input into context ([Anthropic Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)). Three things the module-bearing skill can do that a script-bearing skill cannot, given an in-loop interpreter:

- **Spawn subagents from inside the skill code.** The module calls an allowlisted `tools.task(...)` bridge to fan out work, drop responses into a queue, and consume the queue. LangChain's repo-triage example uses this shape to spawn a subagent per GitHub item, condense each, then cluster — one reviewed workflow rather than a model-mediated chain ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)).
- **Maintain typed values across interpreter turns.** Arrays stay arrays, objects stay objects, helper functions stay defined. The agent does not have to round-trip every intermediate value through stdout, a file, or a message back to the model ([LangChain, 2026-05-20](https://www.langchain.com/blog/give-your-agents-an-interpreter)).
- **Run on a deterministic test corpus.** "Did the agent follow instructions?" becomes "did the agent call the expected function with the expected arguments?" — a check against a fixture, not a rubric ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)).

## Trade-offs

- **The `module:` field is not portable.** It is a LangChain Deep Agents extension, not part of the Agent Skills standard ([Agent Skills Specification](https://agentskills.io/specification)). A skill written for Claude Code, Copilot, or Cursor today must use `scripts/` for executable content; the module slot is dead syntax outside Deep Agents. The portability case [Skill as Knowledge](skill-as-knowledge.md) builds collapses if the module is load-bearing. Author interpreter skills for the harness you ship to, not the cross-tool skill library.
- **A fixed module blocks adaptation.** If the right answer is "the agent should sometimes do A and sometimes do B based on inputs," pinning A in the module removes the agent's ability to pick B. Interpreter skills suit *the routine the procedure shouldn't vary on*; for adaptive procedures, instruction-only skills keep model judgement in the loop.
- **Untrusted-input workloads still need OS-level isolation.** The interpreter's narrow default is not a sandbox. The [CIBER benchmark](https://arxiv.org/abs/2602.19547) finds execution-first interpreters fail catastrophically against natural-language-disguised attacks, and *higher* model capability increases susceptibility because stronger instruction adherence is exploitable. Pair the interpreter (and any module it can import) with [Dual-Boundary Sandboxing](../security/dual-boundary-sandboxing.md) for any workload that ingests web pages, emails, or user files.
- **The same outcome is reachable without the named surface.** Anthropic's Programmatic Tool Calling and Cloudflare Code Mode let the model write code that calls allowlisted tools without packaging it as a skill ([Anthropic, advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)). The added value of the interpreter-skill *packaging* is discovery, versioning, and a documented import path — not token savings, which the underlying interpreter already provides. If only the token savings matter, bare PTC is enough.
- **Below the module-worthy complexity threshold.** A skill whose procedure fits in one or two lines is better as inline instructions plus a regular tool call. The module is overhead for the trivial case.

## Example

A `github-triage` skill that bundles a discovery surface and a workflow module ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)):

````markdown
---
name: github-triage
description: Use this skill to triage GitHub issues, pull requests, and discussions.
module: ./index.ts
---

Use this skill when a user asks for repository triage.

Import the module using the interpreter and call `triage(repo, options)`.

Usage:

```ts
const { triage } = await import("@/skills/github-triage");

const result = await triage("langchain-ai/deepagents", {
  issues: true,
  prs: true,
});

result.toMarkdown();
```
````

The model decides the behavior is relevant (the user asked about repository triage), picks the inputs (which repo, which item kinds), and presents the result. The module — reviewed code in `index.ts` — runs the actual procedure: fetch open items, spawn a subagent per item to condense, drop responses into a queue, consume the queue and cluster. The procedure is fixed across calls; only the inputs change.

The eval implication shows up in the test corpus. Instead of grading whether the model "generally followed the triage instructions," the fixture checks `triage("langchain-ai/deepagents", {issues: true, prs: true, discussions: false})` against the expected return value — a function-call assertion, not a prose rubric.

## Key Takeaways

- Interpreter skills are skills that ship both `SKILL.md` (instruction surface) and a `module:`-referenced TypeScript or JavaScript file (API surface). The model picks when to fire; the runtime picks how to run.
- The `module:` field is a LangChain Deep Agents extension, not part of the cross-tool [Agent Skills standard](https://agentskills.io/specification). Author interpreter skills for the harness you ship to.
- The pattern fits when the procedure should be fixed, an interpreter is in the harness, untrusted-input workloads have a separate OS-level sandbox, and the procedure is heavy enough to warrant a module.
- The eval payoff is sharper: "did the agent call the expected function with the expected arguments?" replaces "did the agent generally follow instructions?" ([LangChain, 2026-05-29](https://blog.langchain.com/interpreter-skills)).
- A module-bearing skill can spawn subagents from inside the skill code, maintain typed values across turns, and compose with the harness loop — things a `scripts/`-only skill cannot do under the same standard.

## Related

- [Code Interpreter as a Primary Agent Tool](code-interpreter-as-agent-tool.md) — the runtime layer interpreter skills sit on top of; sets the interpreter's bridges, capability allowlist, and threat-model boundaries.
- [Skill as Knowledge Pattern](skill-as-knowledge.md) — the portable, instruction-only counterpart; the right answer when the procedure should adapt or the harness has no interpreter.
- [Skill Program Functions](../agent-design/skill-program-functions.md) — the orthogonal runtime-invoked skill direction (runtime predicates fire on detected state); interpreter skills are the model-invoked direction.
- [Filter and Aggregate in the Execution Environment](../context-engineering/filter-aggregate-execution-env.md) — the broader pattern of keeping intermediate state out of model context that the interpreter implements at the platform level.
- [SKILL.md Frontmatter Reference](skill-frontmatter-reference.md) — full inventory of standard and vendor-specific frontmatter fields.
- [Dual-Boundary Sandboxing](../security/dual-boundary-sandboxing.md) — the OS-level enclosure interpreter skills need for untrusted-input workloads.
