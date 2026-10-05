---
title: "Prompt Replay as a Skill Safety Test: What It Misses"
term: "Prompt-Replay Skill Testing"
description: "Pasting a suspect SKILL.md body into the chat reproduced under a third of the harm the installed skill caused, because the delivery path changes the route."
aliases:
  - direct-prompt skill screening
  - skill body prompt replay
  - pasting a skill body instead of installing it
tags:
  - anti-pattern
  - security
  - agent-design
  - skills
  - tool-agnostic
  - arxiv
last_reviewed: 2026-10-02
maturity: emerging
status: current
---

# Prompt Replay as a Skill Safety Test: What It Misses

> Across 11 agents, prompt replay reproduced under a third of an installed skill's verified harm, so a clean replay screens only your agent's message path.

Screening a third-party skill by pasting its body into the chat measures the ordinary message path, which is not the path the skill travels once installed. TrustProbe verified 104 taint-style vulnerabilities across 11 open-source agents, then replayed each one by stripping the frontmatter and placing the body "verbatim in a neutral user message, with no SKILL.md installed". Thirty-three survived. "Direct-prompt delivery fails to reproduce 68.3% of the verified vulnerabilities" ([Wang et al., 2026](https://arxiv.org/abs/2609.39065v1)).

## The conditions that decide whether the gap matters

The gap tracks how much work the framework does on a skill's behalf. Replay reproduction ranged from 0.0% to 100.0% across the 11 agents (Table 2 in Wang et al.). Three designs add steps an ordinary message cannot trigger:

- A catalog with a read-and-follow instruction. OpenClaw lists installed skills in a mandatory system-prompt section and tells the agent to read the matching file, which is why "only 1 of 24 vulnerabilities" came back under replay.
- A typed activation event. Kimi Code CLI resolves a slash invocation through a registry and records a `skill_activation` origin before the turn begins; 1 of 12 reproduced.
- A bound prompt. DB-GPT adopts the parsed skill's template as the agent's own prompt during construction, which the authors read from its code as "a qualitative boundary" rather than a measured one, since it contributed a single vulnerability.

Where the plain message path already reaches the same tools, replay comes close to the real thing. Pochi reproduced 9 of 13. Its "activation protocol strengthens routing without being necessary for most of the observed cases", the authors write. Pi Coding Agent reproduced 2 of 3, on a skill path they read as one that "adds a useful routing cue without forming a strong execution boundary". So read your own framework's loading code first. If it builds none of the three, replay is a defensible proxy.

## Why it works

The skill path changes which code the content travels through, as well as how the content is worded. The study traces the effect to "routing fields and resources through code that a plain message never traverses" ([Wang et al., 2026](https://arxiv.org/abs/2609.39065v1), Appendix G). The lost cases come from mechanics, and the paper puts it this way: "Paired traces link these losses to changed execution routes or sink arguments rather than explicit refusals." The agent builds a different tool call from the replayed body.

A reviewer cannot see that difference in the runtime. The authors' sanitizer audit reports that "no runtime mechanism distinguishes skill-originated tool-call arguments from user-originated ones". Three of the agents apply command-string checks, and these "are origin-blind in that they evaluate the command text without knowing whether it was suggested by skill content or by the user". Where a framework does read skill provenance, it widens the grant: "Where agent frameworks consult skill provenance at all, the signal is used to grant rather than deny."

## When this backfires

Installing is the more faithful test and the more dangerous one. It puts an unvetted skill into an agent that holds credentials. It needs a throwaway profile and a monitored sink. A team without those should not run it on a working machine.

Two further limits:

- A crude payload fails in both channels. SkillJect finds that "naive skill poisoning is often brittle: explicit harmful intent may be blocked by safety mechanisms, while malicious instructions that are weakly integrated with the original skill workflow or current task may fail to influence" downstream behavior ([Jia et al., 2026](https://arxiv.org/abs/2602.14211v3)). A clean install-based result on an obviously hostile body is as uninformative as a clean replay.
- Small per-framework counts carry little weight. Agent Zero's 100% reproduction rate rests on a single vulnerability. The authors say "with one case this result establishes route equivalence for that case rather than a general absence of skill-specific trust."

Neither test is the control. Removing automatic approval still left 31 of 89 covered vulnerabilities (34.8%) exploitable. The study splits those 31 into two causes ([Wang et al., 2026](https://arxiv.org/abs/2609.39065v1), section 5.5). In nine cases, "the configured policy covers the attempted action, but the execution path never checks it". In 22 cases there is "a policy-scope gap", where "the control works as designed but its threat model does not cover the operation". The authors conclude that "a configured control provides no security when its enforcement hook is absent from the active execution path". The fix differs by cause: move the check onto the active path, or widen the policy to cover the operation.

The study's own invariant puts the check at the operation. Skill content may reach an operation that exercises the agent's authority "only when the content is validated for that operation, the user has consented to this class of use, or its provenance remains available at the enforcement point". Hold one of those three and the delivery path stops deciding the outcome.

## Example

The two procedures differ by one step. Substitute your own agent's binary and skill directory; the shape is what matters.

**Before — skill cleared by replaying its body as a prompt:**

```bash
# strip the YAML frontmatter, send the rest as one user message
agent -p "$(sed '1,/^---$/d' suspect/SKILL.md)"
# nothing hostile fires, so the skill is approved
```

**After — skill cleared through the delivery path it will ship on:**

```bash
# install into a throwaway profile holding no real credentials
cp -r suspect "$SKILLS_DIR/suspect"
agent -p "please use this skill and follow its instructions"
# watch the sinks: spawned shells, file reads, outbound hosts
```

The driving instruction is the one the study's OpenClaw walkthrough used, and nothing more elaborate was needed. Real skills reach these paths untampered: "Of 2,963 skill-agent test runs, 743 (25.1%) trigger an audited vulnerable path", though "this rate measures exposure through skill execution; it does not classify the original skills as malicious".

## Key Takeaways

- A clean prompt replay is evidence about your agent's message path, and 68.3% of verified harm did not survive the move to that path
- Read your framework's skill-loading code before picking a screen. A catalog with a mandatory read-and-follow instruction, a typed activation event, or a bound prompt each put the skill somewhere a pasted message cannot reach
- Replays lose cases to changed routing, so a clean replay says nothing about how the framework treats the same text once it presents it as a selected capability
- The install-based test needs a throwaway profile. Without one, screening is not worth converting into an incident
- Keep the approval layer and the sandbox as the enforcement. A third of covered vulnerabilities survived the strictest non-interactive approval configuration these frameworks offered. A screen is the cheaper filter and does not replace the boundary

## Related

- [Trusting a Skill Scanner's Verdict as a Security Judgment (Green-Check Fallacy)](skill-scanner-verdict-not-security-judgment.md) — the other clean-result trap, where a static scan's green check gets read as safety
- [Skill Over-Trust: Treating Topical Relevance as Evidence a Skill Helps](skill-over-trust.md) — the withheld-skill re-run, which attributes a skill's quality cost rather than its security cost
- [Direct Prompt Injection via Collaboration (User as Attack Vector)](direct-prompt-injection-collaboration.md) — the same channel in the opposite direction, with the user pasting an attacker's text
- [Skill Supply-Chain Poisoning](../../security/skill-supply-chain-poisoning.md) — how a hostile skill reaches a registry in the first place
- [Recover the Six Measurement Choices Behind an Attack Success Rate](../../verification/asr-comparability-audit.md) — delivery channel as one more measurement choice that moves an attack success rate
