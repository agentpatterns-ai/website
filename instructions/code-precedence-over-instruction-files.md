---
title: "Code Precedence Over Stale Instruction Files"
term: "Code Precedence Rule"
description: "One sentence in the user-level instruction file, giving existing code precedence over documentation, moved agent convention choices from 4.2% code-matching to 91.4% across 320 runs."
tags:
  - instructions
  - technique
  - tool-agnostic
  - arxiv
aliases:
  - code over documentation precedence
  - stale instruction file override
  - code-wins precedence sentence
last_reviewed: 2026-10-26
maturity: emerging
status: current
---

# Code Precedence Over Stale Instruction Files

> A sentence in your user-level instruction file giving existing code precedence moved agent convention choices from 4.2% to 91.4% code-matching.

A user-level precedence sentence reduced how often two tested agents followed stale project instructions when those instructions contradicted existing code. Across 40 Python projects and 320 runs, the share of convention choices matching the existing code rose "from 7.5% to 94.4% for Claude Code and from 0.8% to 88.3% for Codex CLI" ([Xu & Wu, 2026, arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). Nobody has to find the stale line first.

## The condition that decides whether this helps

The rule assumes the file is the out-of-date half, which is the only case the study measured ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). Check your repositories against that shape first. A file recording conventions the code abandoned fits. A file recording the convention a migration is moving toward does not.

## The sentence

It goes in the user-level file, not the project file: `~/.claude/CLAUDE.md` for Claude Code, `~/.codex/AGENTS.md` for Codex CLI ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). From there it covers every project you open, with no commit to any repository.

> When a repository's documentation and its existing code disagree, follow the conventions used in the existing code, and in your final reply point out each inconsistency you found between the documentation and the code.

Keep the second clause. With the sentence in place, both agents "reported the conflicts they found in all 160 runs", which turns each session into a list of lines worth correcting ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)).

## Why it works

The two sources arrive on channels with different trained authority. "The agent software places the instruction file in the model's context as an instruction, while the code reaches the model only as the output of a file-reading tool. Models are trained to give instructions priority over tool output, so that text hidden in web pages or files cannot redirect the agent" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). That ordering is the instruction hierarchy ([Wallace et al., 2024](https://arxiv.org/abs/2404.13208)). A line keeps an instruction's rank after the code it described has moved on, while the code that superseded it arrives as information.

Reading the code was not sufficient in these runs. Claude Code "named the conflict in its final reply in 79 of 80 runs, and in those runs 86.2% of its choices still matched the file" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). It saw the difference and treated the code as the part that was wrong.

The sentence uses that ordering instead of fighting it. It also reaches the model as an instruction, so the decision becomes one instruction against another, and the sentence is the one written for this conflict. Agents still act on tool output where no instruction covers the matter ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)).

None of this is specific to one vendor's prompt wording. "The emphatic preamble in Claude Code is not needed for this: Codex CLI adds no such text and followed the file in 93.9% of its choices" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). An independent study found the same direction in 39 trials across two harnesses: "where standard and code disagree, agents follow the standard even when it prescribes the worse code, so a stale convention file costs more than no file" ([Mohammadi et al., 2026, arXiv:2608.16630v1](https://arxiv.org/abs/2608.16630v1)).

## When this backfires

- A repository mid-migration has it backwards: the file documents the target and the code holds the convention being retired. The sentence reads the same either way, so it points the agent at the convention you are retiring. [Pattern Replication Risk](../patterns/anti-patterns/pattern-replication-risk.md) is the failure it pushes toward.
- Prescriptive lines get demoted along with descriptive ones. "Instruction files mix rules for the agent with descriptions of the code (Figure 8). Current training treats both as instructions" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). The sentence does not separate them either, so a rule written for new code reads like a description the code contradicts.
- Where the code holds no single convention, the sentence names nothing. Each study project was built so "the existing code uses one convention consistently and the instruction file asks for the other" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)).
- 91.4% is a share, not a guarantee, and Codex CLI reached 88.3%. A convention whose violation breaks correctness still needs a hook or a linter, which is the case [Guardrails Beat Guidance](guardrails-beat-guidance-coding-agents.md) makes for instruction compliance generally.
- The wrong line stays in place for every human reader until someone edits it. The paper treats the two remedies as complementary: "A checker helps when someone runs it, while the sentence takes effect in every task" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). [Stale AI Configuration Artifacts](../patterns/anti-patterns/stale-ai-configuration-artifacts.md) covers that half.
- The evidence is one paper, and it bounds itself: "40 Python projects in which the instruction file is the outdated source, with 16 kinds of convention, feature tasks completed in a single unattended run, and two agents" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). Nothing outside that envelope is measured.

## Example

The paper's Figure 1 shows one study task run with Claude Code, where "The file asks for print and the code uses logging. Without the sentence, the agent reports the conflict and writes print; with the sentence, it writes logging and lists the conflicts it found" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). Same model, same file, same code. The sentence is the only difference.

Codex CLI went further on the same class of conflict. "In 20 of its 80 runs without the sentence, Codex CLI rewrote the existing code to match AGENTS.md. These runs removed a median of 198 lines from 9 files that existed before the run, across 12 of the 40 projects. When the project's original tests were restored after the run, they failed in 17 of the 20 runs." With the sentence, "no Codex CLI run rewrote existing code" ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)). Claude Code rewrote existing code in neither condition, so this cost is agent-dependent while the convention-choice effect was not.

## Key Takeaways

- In this study, the user-level edit raised code-matching convention choices by 87.2 percentage points. The 95% interval was 83.6 to 90.9 ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)).
- Decide which half of your repositories is stale before adopting it. The measured effect holds only where the instruction file is the outdated source.
- Reading the code alone did not correct the conflict. Claude Code named it in 79 of 80 runs while mostly following the file ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)).
- The full sentence improved conflict reporting on Codex CLI, which "named the conflict in 2 of 80 replies" without it ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)).
- Test-breaking rewrites are agent-dependent. Codex CLI deleted working code in a quarter of its runs without the sentence; Claude Code never did ([arXiv:2610.30571v1](https://arxiv.org/abs/2610.30571v1)).

## Related

- [Stale AI Configuration Artifacts (Context Rot)](../patterns/anti-patterns/stale-ai-configuration-artifacts.md) — the drift this sentence works around, and the CI consistency check that corrects it at source
- [Coding-Agent Working-Set Coverage (Coherence Debt)](../context-engineering/coherence-debt-working-set.md) — the same conflict measured as fact availability, where a stale convention file scored below code alone
- [Pattern Replication Risk](../patterns/anti-patterns/pattern-replication-risk.md) — the failure mode a code-wins rule amplifies when the code is the half you meant to retire
- [Layer Agent Instructions by Specificity Across Scopes](layered-instruction-scopes.md) — the scope ordering this sentence exploits, between the user-level file and the project file
- [Guardrails Beat Guidance for Coding Agents](guardrails-beat-guidance-coding-agents.md) — why a convention that must hold needs enforcement rather than a precedence rule
