---
title: "Hidden AI-Directed Text in GitHub Issues and Pull Requests"
description: "A census of 142.7 million GitHub items found hidden AI-directed text at about 16 per million. Attacks were 2% of it, so filter hidden text by author."
term: "Hidden AI-Directed Text"
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - AI-directed hidden text
  - hidden prompt injection on GitHub
  - hidden agent markers
last_reviewed: 2026-11-24
maturity: emerging
status: current
---

# Hidden AI-Directed Text in GitHub Issues and Pull Requests

> Hidden AI-directed text in GitHub issues is real but mostly not an attack; filter it by author, and grant permission through labels or checks.

Hidden AI-directed text is text in an issue, pull request, or comment that GitHub does not render for people but that an agent reading the raw Markdown receives in full. A scan of 142.7 million issues, pull requests and comments found 2,281 validated items in 435 repositories, about 16 per million ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). Only 43 of them, 2%, were attacks.

The risk applies under three conditions. An outsider can trigger the agent by opening an issue or posting a comment. The agent holds secrets, a shell, or write scopes. Or your own automation acts on hidden markers without checking who wrote them. If none of these hold, the measured attack rate of one in 3.3 million items gives little reason to build more.

## What the census found

All 2,281 findings in issues, pull requests and comments sat in HTML comments, because the detector extracted only that construct there ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). The authors sorted them by victim:

| Category | Findings | What it does |
|---|---|---|
| First-party orchestration | 1,519 (67%) | A project coordinates its own agents through hidden markers: claims, hand-offs, state, instructions |
| Content override | 374 (16%) | Steers what an agent writes; about 40% configure a team's AI reviewer |
| Defensive | 345 (15%) | Mostly keeps agents off human-only sections or makes them identify themselves |
| Attack | 43 (2%) | Tries to make another party's agent act against that party's interests |

The attacks were rare and aimed ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). 24 of 43 addressed a specific agent the project runs, 17 of them an issue triage agent. Nine named the victim agent's real tools or output fields, which appear only in the project's workflow definitions. The most common goal was stealing secrets (19 attacks), then hijacking the agent for a side job (16) and forging its verdict (8). One gemini-cli issue read as an ordinary bug report, while a hidden comment told the deduplication agent to copy the workflow token into the workflow's environment.

Hidden text also stays put. On re-fetch, 34 of the 43 attacks were intact, "including issues that maintainers had closed: closing an issue does not remove its text" ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)).

## Why it works

GitHub renders Markdown for people, and agents read the source. The paper states the asymmetry: "the maintainer who reads an issue on github.com sees one document, and the maintainer's agent sees another" ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). Anyone can write an issue, and the maintainers' own agents read it. Those agents frequently hold elevated privileges, so the triage bot becomes a confused deputy.

First-party markers carry the same flaw from the other side. They are plain text in a public thread, and anyone who can comment can post the same marker ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). The paper found 47 markers in 10 projects that record an approval, a merge-ready state or a bypassed check. It did not audit whether the code reading them checks the author, and it saw no attack that copied a real project marker. The orchestration rate grew fivefold in four months, from 1.9 to 10.1 per million new issues and pull requests.

## What to do

- Filter hidden text by author. The paper's advice: "Filtering should be by author, not by format: strip what outsiders write, keep what the project's own members and bots write" ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). Check the author association or an allowlist of your own bots.
- Never let model output open a gate alone. "A model's verdict, such as allow_triage=true, is text an attacker can influence and should never open a security gate alone" ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). Route the verdict through [safe outputs](safe-outputs-pattern.md) that a deterministic job applies.
- Grant permission through maintainer-only signals. For anything that grants permission, the paper prefers a label or check status that only maintainers can set over a hidden comment ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)).
- Strip secrets and write scopes from issue-triggered jobs. An agent that labels or deduplicates issues needs to read issues and add labels ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). That removes legs of the [lethal trifecta](lethal-trifecta-threat-model.md) on the path an outsider controls.

## When this backfires

- Blanket stripping breaks your own automation. Removing HTML comments ended compliance in the paper's offline replay, and "it also removes every legitimate hidden instruction" ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)). The authors list projects' own workflows, defensive notices and reviewer settings among what breaks.
- Format filters miss other constructs. GitHub states that "text entered as an HTML comment in an issue or pull request comment is not passed to Copilot cloud agent" ([GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations)). Trail of Bits wrote "Some of these, such as HTML comments, are stripped before the issue text is passed to Copilot." and hid its payload in a `<picture>` tag instead ([Trail of Bits, 2025](https://blog.trailofbits.com/2025/08/06/prompt-injection-engineering-for-attackers-exploiting-github-copilot/)). The census left visible-text injection and other surfaces out, and its authors call every count a lower bound.
- Model resistance varies. Replayed against five models with mock tools, four never complied, and the smallest, fastest one complied with 8 of 43 attacks (19%). Two models often returned no answer at all (16 and 22 of 43 raw runs), which blocks the legitimate task too. The authors say the results show the attacks "are not merely theoretical, rather than predict how often they succeed in practice" ([Nakibly and Babo, 2026](https://arxiv.org/abs/2611.28763v1)).

## Key Takeaways

- Hidden AI-directed text appears at about 16 per million GitHub items. Attacks are 2% of it. Most aim at maintainers' own agents, and 44% hit repositories of major AI and cloud vendors.
- Two thirds of it is projects coordinating their own agents, a channel anyone who can comment can imitate.
- Filter by author, not format. Blanket stripping kills legitimate markers and still misses constructs other than comments.
- Keep secrets and write scopes out of any job an outsider's issue can trigger, and use labels or check status for permission.

## Related

- [Comment-Triggered Agent Dispatch on Issues and PRs](../workflows/comment-triggered-agent-dispatch.md) — The comment box as a dispatch surface, and the demonstrated attacks on it
- [Prompt Injection: A First-Class Threat to Agentic Systems](prompt-injection-threat-model.md) — The general threat model this census measures in the wild
- [Non-Human Event Provenance Markers to Block Fabricated Approvals](non-human-event-provenance-markers.md) — Marking injected events so a forged approval carries no authority
- [Safe Outputs Pattern for Trustworthy Agent Responses](safe-outputs-pattern.md) — Turning an agent's verdict into a request a deterministic job applies
- [Lethal Trifecta Threat Model for AI Agent Development](lethal-trifecta-threat-model.md) — Removing a leg from the outsider-triggered path
