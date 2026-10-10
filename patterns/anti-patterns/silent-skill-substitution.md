---
title: "Silent Skill Substitution When Same-Job Skills Co-Install"
term: "Silent Skill Substitution"
description: "A same-job skill can take over a run so the installed skill's exclusive rules never load, the task still passes, and the reply names neither skill."
tags:
  - anti-pattern
  - agent-design
  - claude
  - arxiv
  - skills
aliases:
  - co-installed skill conflict
  - same-job skill shadowing
  - skill substitution
last_reviewed: 2026-10-09
---

# Silent Skill Substitution When Same-Job Skills Co-Install

> When two skills do the same job, the model can run the other, your skill's exclusive rules go unread, and the task still passes.

Silent skill substitution is the loss of an installed skill's rules when a similar skill from another source claims the same job and the model runs that one instead. The model picks between skills from their names and descriptions alone, and the skill body, where constraints usually live, loads only after the choice. A completion check cannot see the swap ([paper](https://arxiv.org/abs/2610.11647v1)).

## When it applies

The effect is real but small on average, so check these conditions before you spend time on an audit.

- The two skills sit in project or personal scope. With a same-job skill in a plugin, the model used the installed skill in 58.0% of runs and the plugin skill in 2.9%. The installed skill's use fell 6.2 pp, against 16.9 pp when the same pairs had the rival in the project ([paper](https://arxiv.org/abs/2610.11647v1)).
- Your skill's value is a rule only it asks for. On core functions exclusive to the installed skill, fidelity fell 5.6 pp (95% CI -7.3 to -3.8). On core functions both skills share, it did not change (+0.1 pp) ([paper](https://arxiv.org/abs/2610.11647v1)).
- Your checks look only at task completion. Completion did not drop (+1.9 pp, 95% CI -1.0 to +4.9) ([paper](https://arxiv.org/abs/2610.11647v1)).

The overall fidelity drop across all core functions was 2.6 pp. The paper reports that 37% of exclusive core functions were lost in runs that open the rival skill first, but that figure holds only for that path. Do not read it as the average loss ([paper](https://arxiv.org/abs/2610.11647v1)).

## How common it is

From snapshots of 20,947 repositories, an estimated 23.5% of installed skills (95% CI 21.2 to 25.7%) have a same-job skill in the same installation list. For 63.7% (95% CI 61.3 to 66.0%) the most similar skill by another author does the same job. The authors call both figures conservative because the pair judge sees only the most similar candidate ([paper](https://arxiv.org/abs/2610.11647v1)).

Copying a whole collection raises the rate. In 489 projects that did so, 37% of the judged skills had a same-job skill in the same list, against 19% in other lists ([paper](https://arxiv.org/abs/2610.11647v1)).

## What the failure looks like

The paper's worked example is one run with Haiku 4.5. The project skill `checkpoint` forbids any change to the git state, and with only that skill installed the model saves a handoff note without committing. A second skill added under the directory `checkpoint-2` changes the run: the model uses it, commits the work the first skill forbids, and does not say which skill it used ([paper](https://arxiv.org/abs/2610.11647v1)).

Across 113 runs where the rival skill replaced the installed one, the final reply named the skill it used in 0.9% and never said that more than one suitable skill existed ([paper](https://arxiv.org/abs/2610.11647v1)). A field report shows the same shape outside the study. Invoking a project's `self-improvement` skill silently ran a personal fork aimed at an unrelated repository, and the author found out only by reading the output ([seasonedcc/seasoned-skills#303](https://github.com/seasonedcc/seasoned-skills/issues/303)).

Most of the lost fidelity comes from runs that never use the installed skill. Substituted runs carry 36% of the loss and runs that use neither skill carry 45%, while runs that use the installed skill carry 20% ([paper](https://arxiv.org/abs/2610.11647v1)). The problem is mostly a skill that never loads, with little interference inside runs that did load it.

## Why it works

Claude Code shows the model each skill's name and description in a listing, truncated at 1,536 characters per skill, and loads the body after the model chooses ([Claude Code docs](https://code.claude.com/docs/en/skills)). The paper states the consequence: the choice between two similar skills "rests on a few hundred characters of text per skill, and the body, where the requirements of the skill usually live, is read only after the choice is made." Two skills that match the same request give the model little to tell them apart, and the skill it skips contributes no rules. Both skills can complete the task, so a pass/fail check passes either way.

The authors place the decision at the first skill read. In 97% of runs that open the rival skill first, no file changed before that read ([paper](https://arxiv.org/abs/2610.11647v1)).

Scope sets who wins before the model chooses. Claude Code resolves a name shared by a personal and a project skill in favor of the personal one, and it loads plugin skills alongside others because they are namespaced as `/plugin-name:skill-name` ([Claude Code docs](https://code.claude.com/docs/en/skills#resolve-skills-that-share-a-name)). With the rival in the personal directory, the installed skill appeared in none of 243 listings and its use fell 35.0 pp. Listing order changed use of the installed skill by only +0.6 pp ([paper](https://arxiv.org/abs/2610.11647v1)).

## What to do

1. List skills with the same name across `~/.claude/skills` and `.claude/skills`. The personal copy wins ([Claude Code docs](https://code.claude.com/docs/en/skills#resolve-skills-that-share-a-name)).
2. When you copy a whole skill collection into a project, remove skills that duplicate ones you already install ([paper](https://arxiv.org/abs/2610.11647v1)).
3. Name each skill distinctively and state its specific tasks in the description, because the listing is all the model sees before it chooses ([paper](https://arxiv.org/abs/2610.11647v1)). Put the main use case first, since the listing is truncated ([Claude Code docs](https://code.claude.com/docs/en/skills)).
4. Score exclusive rules in skill evals, not only pass/fail. The authors write that benchmarks "should therefore score exclusive core functions" ([paper](https://arxiv.org/abs/2610.11647v1)).
5. Keep hard rules out of skill bodies alone. In 38.0% of runs with the rival installed, the model used neither skill ([paper](https://arxiv.org/abs/2610.11647v1)). A rule such as "never change git state" belongs in a permission rule or hook, which does not depend on the model loading a skill.

Do not rely on description similarity to find pairs. Below 0.9 similarity, only 10% to 37% of cross-project pairs in each band were confirmed as same-job, and confirmed pairs occur even at low similarity ([paper](https://arxiv.org/abs/2610.11647v1)). You have to read the skills.

## A guard at the first read

The authors tested a pre-tool hook that denies the first read of the rival skill while the installed skill is unread, and tells the model to use the installed one. After a denied first reach, the model switched in 96% of 179 cases. Fidelity on exclusive core functions rose 9.1 pp (95% CI +6.0 to +12.1) ([paper](https://arxiv.org/abs/2610.11647v1)).

This is the authors' experiment, not a shipped tool. It also needs someone to declare the winner for each pair, which with many overlapping skills becomes a hand-kept table that drifts. A wrong entry forces the worse skill.

## When this backfires

- You have few skills with distinct names and descriptions. There is no same-job pair, so an audit finds nothing.
- The skills ask for the same behavior. Shared core functions did not change (+0.1 pp), so removing one buys nothing.
- Your duplicates live in plugins. Namespacing keeps both listed, and the rival was used in 2.9% of runs.
- You run Opus 5 and expect it to be immune. The exclusive-rule fidelity drop was significant with every model, though Opus 5 showed no first-read effect because it often reads both skills ([paper](https://arxiv.org/abs/2610.11647v1)).
- The other author's skill is the better one for you. The paper measures fidelity to the installed skill's core functions, not overall task quality, so it does not show the swap made your results worse.

The evidence is one v1 preprint with one run per model, configuration, and pair. Several LLM-judge agreement scores fall below the 0.8 threshold the authors cite as firm: 0.72 for the pair judge, 0.71 for skill types, and 0.73 for core-function identification ([paper](https://arxiv.org/abs/2610.11647v1)). The authors raised the listing cap to 20,000 characters for the experiments, so default Claude Code behavior was not measured. Codex showed a similar drop on 193 pairs (18.2 pp against 20.1 pp on Claude Code for the same pairs). The study did not test Copilot or Cursor.

## Key Takeaways

- A same-job skill in project or personal scope cut use of the installed skill by 19.9 pp while task completion held, so a passing task does not show your skill ran.
- The loss lands on rules only your skill asks for (5.6 pp), and the final reply names the skill used in 0.9% of substituted runs.
- Plugin-scoped duplicates barely compete, so audit personal and project directories first.
- Put rules that must hold in a permission rule or hook, since 38.0% of runs with a rival installed used neither skill.
- The numbers come from one preprint with tentative judge labels. Size your effort to a small average effect.

## Related

- [Agent Extension Conflicts](agent-extension-conflicts.md) — the broader composition failure, including the vocabulary collision this page measures
- [Assuming Loaded Skills Stay Enforced in Long Contexts](assuming-loaded-skills-stay-enforced.md) — a loaded skill sheds its own requirements as the run grows
- [Designing Agent Plugins to Survive Co-Installation](../agent-design/plugin-co-installation-safety.md) — the packaging side, where two plugins claim the same capability name
- [Skill Composition Risk in Agent Ecosystems](../../security/skill-composition-risk.md) — adversarial chaining between skills, a different failure from silent substitution
- [Skill Over-Trust](skill-over-trust.md) — attributing a regression to one skill by re-running without it
