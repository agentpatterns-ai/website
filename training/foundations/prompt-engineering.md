---
title: "Prompt Engineering for Agent Instructions and Systems"
description: "Agent instructions form a system of interacting constraints — altitude, polarity, scope, and volume — that determine compliance and reliability."
tags:
  - training
  - instructions
  - tool-agnostic
---
# Prompt Engineering for Agent Instructions

> Effective agent instructions form a system of interacting constraints — altitude, polarity, scope, and volume — not a list of rules appended over time.

Prompt engineering for agents is the structural discipline of designing instructions that survive attention pressure, scale across contexts, and degrade gracefully at their edges. The concepts are tool-agnostic: they apply to system prompts, `AGENTS.md` files, `CLAUDE.md` files, and any instruction surface that feeds text into an agent's context window.

---

## Altitude: Principles vs Lookup Tables

Every instruction sits at an altitude — from high-level principle to low-level case enumeration. The two failure modes are symmetric: too vague ("be helpful and accurate") gives no real constraint, and too brittle ("if the file is over 500 lines, read the first 100 and last 100") breaks on every case the author did not anticipate.

The productive altitude tells the agent *how to reason*, not *what to decide*. "Treat authentication code as high-risk; understand downstream session and token impact before editing" generalizes across cases. "Never edit files in `/src/auth/`" does not.

The test: introduce an edge case the prompt did not anticipate. A well-calibrated instruction degrades gracefully — the agent applies the nearest heuristic. A too-brittle instruction falls through to default behavior with no constraint at all.

Different sections of a prompt operate at different altitudes. Background context sits high (principles and scope). Tool guidance sits low (precise constraints on when and how). Mixing altitudes within a single section produces inconsistency.

See [System Prompt Altitude](../../instructions/system-prompt-altitude.md) for the full framework and section-by-section guidance.

---

## Polarity: Positive vs Negative Framing

Instructions come in two polarities. Positive instructions state what to do: "Use `const` and `let` only." Negative instructions state what to avoid: "Do not use `var`." The distinction is not stylistic — it affects compliance rates, and the effect compounds as instruction count grows.

Positive instructions require execution: the agent identifies the target behavior and performs it. Negative instructions require suppression: the agent holds the prohibited action in mind while choosing not to take it. Execution is a cheaper operation than suppression [unverified — model-architecture dependent], which produces higher compliance for positive forms across equivalent rule sets. As [instruction polarity research](../../instructions/instruction-polarity.md) documents, negative rules are among the first to fail when attention is under pressure from a large instruction set [unverified].

The reframing is mechanical. "Avoid long functions" becomes "Keep functions under 30 lines." "Don't write vague commit messages" becomes "Use conventional commits: `type(scope): description`." The positive form makes the correct behavior explicit rather than leaving it implied.

Negative phrasing is justified when the space of acceptable alternatives is too large to enumerate ("Do not modify infrastructure files") or when naming a specific banned item ("No `console.log` in production code"). For these cases, position them early in the instruction set — [primacy bias](../../instructions/critical-instruction-repetition.md) favors earlier instructions.

If a prohibition is critical enough that failure is unacceptable, it should not be an instruction at all — it should be a pre-commit hook or CI gate. Instructions are probabilistic; hooks are deterministic.

See [Instruction Polarity](../../instructions/instruction-polarity.md) for the full trade-off analysis.

---

## Negative Space: Constraints That Close Off Wrong Paths

[Negative space instructions](../../instructions/negative-space-instructions.md) are a distinct technique from negative *polarity*. Where polarity asks "how do I frame this rule?", negative space asks "should I define the goal or the boundary?"

Negative constraints eliminate known failure modes with precision. "No filler phrases: no 'in this guide', no 'let's explore', no 'as you may know'" is binary and verifiable — a grep confirms compliance. The equivalent positive guidance ("write in a direct, information-dense style") requires judgment to evaluate [unverified].

The design criterion is greppability: if a constraint can be expressed as a deterministic check, negative space is the right form. Banned phrases, scope exclusions ("Do not modify files outside `docs/`"), tool restrictions, and format exclusions all fit this pattern.

Negative constraints are most effective when paired with a positive directive. The positive rule gives direction; the negative constraint closes off the most common wrong interpretations. Relying entirely on either form leaves gaps.

---

## Rules vs Examples: Choosing the Right Vehicle

Rules generalize. Examples anchor. The choice between them depends on [what kind of failure you are preventing](../../instructions/example-driven-vs-rule-driven-instructions.md).

Use rules when the constraint is binary and acceptable variation is fine: "Never commit directly to main." Use examples when format or structure matters precisely and misinterpretation would produce wrong output: showing the exact commit message format with a correct instance and three incorrect instances eliminates ambiguity that a rule alone cannot.

The most reliable pattern combines both: state the rule, show one example. "File names must be kebab-case and match the concept name. Example: `progressive-disclosure.md` (not `ProgressiveDisclosure.md`, not `prog-disc.md`)." One example is usually sufficient. Multiple examples risk teaching the agent to interpolate between them rather than follow the rule [unverified].

For format and style constraints in a codebase, pointing at existing code outperforms inline examples. "Follow the repository pattern in `src/repos/UserRepo.ts`" stays current as the code evolves. A 30-line inline example freezes at the moment it was written and drifts as the codebase changes. [Hints over code samples](../../instructions/hints-over-code-samples.md) are cheaper in tokens and require no maintenance.

---

## Domain-Specific Prompts: Generic Instructions Fail

Generic instructions ("reason carefully before acting") give the model no information about what good reasoning looks like in your specific context. [Anthropic's think tool research](https://www.anthropic.com/engineering/claude-think-tool) (see also [The Think Tool](../../agent-design/think-tool.md)) measured a 54% relative improvement on the tau-Bench airline domain when switching from a generic prompt to one with domain-specific guidance and worked examples — same model, same tools, only the prompt changed.

A [domain-specific system prompt](../../instructions/domain-specific-system-prompts.md) includes domain vocabulary, worked examples of reasoning chains for real edge cases, explicit guidance for ambiguous inputs, and success/failure definitions specific enough for the agent to self-check.

The examples must come from observed failures, not imagined scenarios. Instrument the agent in production, identify where reasoning quality is low, write examples that demonstrate correct reasoning for those cases, and measure improvement. This is iterative maintenance, not a one-time authoring task.

Complex guidance belongs in the system prompt, not in tool descriptions. [Anthropic's research](https://www.anthropic.com/engineering/claude-think-tool) found that the same content in tool descriptions was fragmented and inconsistently applied; in the system prompt, it integrated across all reasoning steps.

---

## The Compliance Ceiling: Why More Rules Produce Worse Behavior

Instruction sets have a [compliance ceiling](../../instructions/instruction-compliance-ceiling.md). Below it, agents follow rules with reasonable precision. Above it, compliance degrades in a predictable sequence: modification errors first (the rule is followed imprecisely), then omission errors (the rule is skipped entirely).

The agent does not choose which rules to ignore — attention distribution determines it, and attention is finite [unverified]. Adding more rules past the ceiling does not improve behavior; it degrades it. A 200-rule monolithic instruction file is the canonical anti-pattern (the "mega-prompt"). Every incident adds another rule. The file grows; compliance shrinks.

Position within the instruction set affects compliance independent of importance. [Primacy bias](../../instructions/critical-instruction-repetition.md) means instructions near the top receive more reliable attention than those toward the end [unverified]. A poorly ordered file effectively makes low-position rules optional.

The architectural response is structural, not editorial:

- **Modularize.** Move task-specific rules into skills or on-demand files loaded only when relevant.
- **Layer by scope.** Project-wide instructions contain only conventions that apply to every task.
- **Move enforcement to hooks.** Rules that must never fail belong in linters, pre-commit hooks, or CI gates.
- **Audit total rule count.** If all loaded instructions total hundreds of rules, cut.

For critical constraints that must remain as instructions, [repeating them at both the start and end](../../instructions/critical-instruction-repetition.md) of the prompt exploits both primacy and recency bias. Reserve this for hard constraints only — repeating everything negates the priority signal.

---

## Layered Scopes: Instructions That Scale

A single instruction file at the repository root works for small codebases. As projects grow — multiple services, distinct conventions per directory, mixed toolchains — a flat file either becomes an unmanageable conditional list or fails to cover the cases that matter.

[Layered instruction scopes](../../instructions/layered-instruction-scopes.md) solve this by structuring instructions in concentric layers: global defaults, project-level conventions, and directory-level overrides. The most specific instruction wins. [OpenAI's Codex harness](https://openai.com/index/unlocking-the-codex-harness/) implements this as a three-scope hierarchy that concatenates `AGENTS.md` files from global config through the git root to the current working directory, with later (more specific) instructions taking priority.

This pattern applies independent of tooling. Any harness that reads instruction files from the filesystem can implement it: collect files from global to local, concatenate in order of increasing specificity, enforce a total size cap.

Layering interacts directly with the compliance ceiling. Each layer should be small (50-100 lines per file). The assembled total should stay well under the ceiling. Prefer pointers to documentation over embedded content. If the assembled context for a deeply nested directory exceeds the budget, the outermost layers are the first to lose attention.

---

## How These Interact as a System

These concepts are not independent techniques to apply in isolation. They form an interacting system:

- **Altitude** determines what kind of instruction you write: principle, heuristic, or precise constraint.
- **Polarity** determines how you frame it: as a target behavior or a prohibition.
- **Rules vs examples** determines the vehicle: abstract constraint or concrete anchor.
- **Negative space** closes off known failure modes that survive positive guidance.
- **Domain specificity** grounds the instructions in real reasoning patterns from your context.
- **The compliance ceiling** limits the total volume — every instruction added displaces attention from existing ones.
- **Layered scopes** distribute instructions across the right granularity so each layer stays small.
- **Repetition and position** determine which instructions survive attention pressure.

An instruction set designed with all these constraints in mind is small, layered, positively framed where possible, at the right altitude for each section, anchored by examples where format precision matters, and backed by hooks for anything that must never fail.

---

## Key Takeaways

- Write instructions at the altitude that generalizes — principles and heuristics, not case-by-case lookup tables.
- Frame rules positively ("use X") rather than negatively ("avoid Y") — reserve negative phrasing for absolute prohibitions and scope exclusions.
- Combine rules with one example when format precision matters; point at existing code rather than reproducing it inline.
- Ground system prompts in domain-specific worked examples drawn from observed failures, not imagined scenarios.
- Respect the compliance ceiling: fewer, well-positioned rules outperform comprehensive lists that exceed attention capacity.
- Layer instructions by scope (global, project, directory) so each file stays small and the most specific rule wins.
- Move must-never-fail constraints to hooks — instructions are probabilistic, hooks are deterministic.

## Related

**Source patterns**

- [System Prompt Altitude](../../instructions/system-prompt-altitude.md)
- [Instruction Polarity](../../instructions/instruction-polarity.md)
- [Example-Driven vs Rule-Driven Instructions](../../instructions/example-driven-vs-rule-driven-instructions.md)
- [The Instruction Compliance Ceiling](../../instructions/instruction-compliance-ceiling.md)
- [Domain-Specific System Prompts](../../instructions/domain-specific-system-prompts.md)
- [Negative Space Instructions](../../instructions/negative-space-instructions.md)
- [Critical Instruction Repetition](../../instructions/critical-instruction-repetition.md)
- [Layered Instruction Scopes](../../instructions/layered-instruction-scopes.md)

**Training modules**

- [Context Engineering](context-engineering.md)
- [Harness Engineering](harness-engineering.md)
- [Tool Engineering](tool-engineering.md)
- [How the Four Disciplines Compound](prompt-context-harness-capstone.md)
- [GitHub Copilot: Context Engineering and Agent Workflows](../copilot/context-and-workflows.md)
