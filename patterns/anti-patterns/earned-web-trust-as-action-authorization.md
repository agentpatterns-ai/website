---
title: "Earned Web Trust as Action Authorization (Earn-Then-Exploit)"
term: "Earn-Then-Exploit"
description: "A web source that helped a coding agent five times holds no authority over its next privileged action. Earned trust took Codex fraud success from 25% to 85.7%."
tags:
  - security
  - agent-design
  - tool-agnostic
  - anti-pattern
  - arxiv
aliases:
  - earn-then-exploit web fraud
  - EtE attack
  - earned trust attack
last_reviewed: 2026-11-05
maturity: emerging
status: current
---

# Earned Web Trust as Action Authorization (Earn-Then-Exploit)

> A web source that helped an agent before still holds no authority over its next privileged action, and earned trust amplifies the fraud.

This anti-pattern applies when a coding agent has web access and can take privileged actions, such as sending mail, loading code, or deleting data. The agent checks each page a site gives it, the checks pass, and the site's later instructions carry more weight because it has been right so far. Xu et al. built sites that gave five rounds of genuine, locally verifiable help and then asked for one out-of-scope action. Across 56 enterprise scenarios the attack succeeded at an average of 71.4%: "Codex 85.7% (48/56), ZCode 67.9% (38/56), and QwenCode 60.7% (34/56)" ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)). The four injection baselines averaged 19.6% to 32.1% on the same scenarios ([Table 1](https://arxiv.org/abs/2611.00725v1)).

## The anti-pattern

The terminal step is a real capability the agent already has, re-described as a required step of the current task. Every scenario had a safe path, where "the task remains fully completable through a genuine slow channel" that skips the harmful action ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)). The agents took the harmful path anyway in most scenarios.

Prior help carries a large share of the effect. With the help count varied from 0 to 5, "On ZCode, ASR rises from 37.5% to 67.9%, while on Codex it increases from 25.0% to 85.7%" ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)). Injection baselines given the same prior help rose too, so the amplifier is not specific to one payload style ([Section 5.5](https://arxiv.org/abs/2611.00725v1)).

## Why it works

Local verification checks that content is correct. It does not check that the content may direct an action. The authors put it in one line: "Models can mistake passing verification for permission to act" ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)). The final page adds policy citations, a shorter path, a loss narrative, and a deadline. The attack places its pressure claims outside local verification ([Section 3.3](https://arxiv.org/abs/2611.00725v1)). Removing the policy framing alone cut success by 73.2 points on Codex ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)). The paper measures behavior only. It does not "establish how trust is internally represented or formed within the model." ([Section 8](https://arxiv.org/abs/2611.00725v1)).

The fix moves the check from the source to the action. The paper's action-authorization separation (AAS) allows a sensitive action only when it comes from the user, a system rule, or explicit user endorsement, no safe path exists, and a permission table authorizes the originating principal. In the case study, "AAS instead blocks the request because it is genuine but out of scope." AAS reached 0% attack success and 100% completion on two agents. Prompt-level adaptations of instruction hierarchy, CaMeL, StruQ, and verifiable credentials left 0% to 21.4% attack success, with 69.6% to 94.6% task completion ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)).

## Example

The paper's X4-Z3 case study (application integration, untrusted code execution) shows both sides.

**Before** — the agent completes an MQ v3 integration with a connector the fraud marketplace supplied. The product page then posts a compatibility notice that calls a managed ruleset the next required step. The agent downloads a rule package, switches to managed-ruleset mode, and restarts jobs, which gives the attacker code execution in the order-event path. It reports "all done" ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)).

**After** — with AAS, the same request fails all three checks. It came from the external marketplace, the local connector had already delivered every event, and the permission table gives the marketplace no right to load runtime rules. The agent stays in local mode and finishes the task ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)).

## When this backfires

- Earned trust amplifies the attack, and the attack does not need it. Single-shot task-aligned injection already "achieves over 80% attack success rate (ASR)" on five web-use agents ([Shapira et al., 2025](https://arxiv.org/abs/2506.07153v2)). A defense aimed only at long-running sources misses that.
- AAS "is deployed through a system prompt containing the sensitive-operation list and permission table" ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)). Adaptive attacks bypassed 12 defenses at above 90% for most, though most had reported near-zero ([Nasr, Carlini et al., 2025](https://arxiv.org/abs/2510.09023v1)). Treat the 0% as a static-attack result and enforce the gate in the harness where you can.
- For an action proposed by an external source, explicit user endorsement satisfies the source check; necessity and authorization must still pass ([Section 6](https://arxiv.org/abs/2611.00725v1)).
- The attack-success evidence is one v1 preprint on a local simulated web. A scenario counted as breached if either of two attempts succeeded ([Sections 5.1 and 6](https://arxiv.org/abs/2611.00725v1)).

## Key Takeaways

- Count the help a site gave as evidence about its content, never as permission for an action.
- Newer is not safer here: GLM-5.1 fell to EtE at 25.0%, against 67.9% for the newer GLM-5.3-Flash ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)).
- In a separate public-web test using ZCode, benign help pages were retrieved in 82.1% of scenarios and adopted in 76.8% ([Xu et al., 2026](https://arxiv.org/abs/2611.00725v1)).

## Related

- [Cognitive Poisoning: Untrusted Tool Feedback as a Trajectory Attack](../../security/cognitive-poisoning-tool-feedback.md) — the same build-then-strike shape through a malicious tool instead of a public web page.
- [Authority Confusion: Untrusted Context Must Not Authorize Side Effects](../../security/authority-confusion-untrusted-context.md) — the general rule AAS applies to sensitive actions.
- [External Artifacts Treated as Data, Not Adversarial Input](external-artifacts-as-data.md) — the developer-side habit that leaves a helpful page unscreened.
- [Adaptive Evaluation of Out-of-Band Prompt-Injection Defenses](../../security/adaptive-evaluation-out-of-band-defenses.md) — why a 0% result against a static attack is a starting point.
- [Treat Task Scope as a Security Boundary](../../security/task-scope-security-boundary.md) — a narrow task leaves a fraud page fewer plausible next steps to invent.
