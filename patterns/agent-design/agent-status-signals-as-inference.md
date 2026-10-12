---
title: "Agent Status Signals as Inference"
term: "Agent Status Signal"
description: "A status signal in an agent surface is generated off the run it describes, so it may claim only what its own inputs settle: the inbound message, or the clock."
tags:
  - agent-design
  - human-factors
  - tool-agnostic
aliases:
  - agent loading state
  - agent status indicator
  - chat agent status signal
last_reviewed: 2026-10-11
maturity: adopted
---

# Agent Status Signals as Inference

> A status signal generated off the run it describes may honestly claim only what its own inputs can settle.

A reaction chosen when the message arrives can say how the agent read the request, because that reading is true or false the moment it is emitted. It cannot say the run is going well. A phrase rotated on a timer says nothing about the run at all, since elapsed time is its only input. The generating input sets the ceiling on what either one may claim, and the copy cannot raise it.

## The two signal shapes that ship today

| Surface | Generating input | Settles | Does not settle |
|---|---|---|---|
| Classifier-chosen reaction | the inbound message text | how the agent read the request | progress, cost, or outcome |
| Timer-rotated loading phrases | elapsed time | that the app is still attached | anything about the work |

LangChain's Managed Deep Agents added the first shape in v0.9, which "includes a new API for managing reactions for your distributed agents, and a system to dynamically assign emoji responses with your instrument of choice" ([Drezner, October 2026](https://www.langchain.com/blog/slack-sdk-managed-deep-agents)). A decision model scores the inbound text against a declared vocabulary and returns one emoji.

Slack ships the second shape as a documented parameter on its own platform. `loading_messages` is "The list of messages to rotate through as a loading indicator. Maximum of 10 messages." ([Slack docs](https://docs.slack.dev/reference/methods/assistant.threads.setStatus)). Slack's docs describe them as strings that Slack "will rotate through showing to serve as a loading indicator", and record that `agents.sessions.setStatus` now replaces the method.

The design work sits in the vocabulary, not the glyph. LangChain's guidance is that "the `criteria` descriptions do more work than the emoji names. The model matches on your description of the situation, so the same glyph carries whatever meaning your workspace already gives it" ([Drezner](https://www.langchain.com/blog/slack-sdk-managed-deep-agents)). A confidence floor backs it. In the post's worked example, a top pick under 25% confidence falls back to a generic reaction rather than a specific one.

## Why it works

Trust in an indicator tracks whether the reader can catch it being wrong, and the generating input decides that. Receipt settles a claim about how the request was read, so waiting produces no evidence against it. The run settles a claim about elapsed state, which hands the reader the whole duration to collect a contradiction. A signal streamed from the run itself escapes the bound, which is why a live tool-call feed carries claims a reaction cannot ([Pan, 2026](https://tianpan.co/blog/2026-07-02-why-you-cant-put-a-progress-bar-on-an-agent)). Pan puts arithmetic on the gap: when a task runs eight minutes and the bar reached 92% at minute two, "the user has six full minutes to study the lie", and after two such catches readers "stop believing your indicators entirely — including the honest ones" ([Pan, 2026](https://tianpan.co/blog/2026-07-02-why-you-cant-put-a-progress-bar-on-an-agent)).

Slack's documented purpose for the primitive stays inside that bound: "This method helps apps set expectations for potentially slow responses; e.g. \"app is thinking...\"" ([Slack docs](https://docs.slack.dev/reference/methods/assistant.threads.setStatus)). LangChain concedes the gap on its own path. "You could argue that there is dishonesty to this design: Because a different model is scoring the reaction response from the model responding, there may be subtle differences in interpretation" ([Drezner](https://www.langchain.com/blog/slack-sdk-managed-deep-agents)). Human-computer interaction research names the class without resolving it. Adar, Tan and Teevan present "the notion of benevolent deception, deception aimed at benefitting the user as well as the developer" ([CHI 2013](https://www.microsoft.com/en-us/research/publication/benevolent-deception-in-human-computer-interaction/)).

## When this backfires

- Long runs behind a timer-driven signal. A rotating status line is "cycling through canned phrases uncorrelated with what the system is doing" ([Pan, 2026](https://tianpan.co/blog/2026-07-02-why-you-cant-put-a-progress-bar-on-an-agent)). Over minutes the reader notices, and accurate indicators lose credibility alongside decorative ones.
- Over-generic vocabulary criteria. "A scoring model will over-index on certain reaction responses if their description is overly generic" ([Drezner](https://www.langchain.com/blog/slack-sdk-managed-deep-agents)). One reaction swallows the vocabulary while the signal still looks deliberate.
- One vocabulary shared across agents in different domains. LangChain's illustration is a fire emoji that "could mean production is burning and you should wake up" from an on-call agent, and that the campaign is working from a growth agent ([Drezner](https://www.langchain.com/blog/slack-sdk-managed-deep-agents)).
- Agents that conceal their own failures. Guo et al. define "agentic upward deception, a phenomenon in which an agent facing environmental constraints conceals its failure and performs actions that were not requested without reporting", observe action-based deception across 11 evaluated models, and report that prompt-based mitigation gave "only limited reductions" ([Guo et al., 2025](https://arxiv.org/abs/2512.04864v1)). A signal drawn from the agent's account of itself reports the concealment rather than the failure.
- Unusual requests. The confidence floor is correct and still costs you: the signal degrades to a generic default on exactly the messages where a specific one would carry the most information.

## Example

The vocabulary from LangChain's worked example, passed to the decision model that picks the reaction:

```python
VOCABULARY = Choice(
    instructions="Which emoji best acknowledges this message?",
    criteria={
        "bug": "A defect or incorrect behaviour.",
        "rotating_light": "A declared incident or outage.",
        "mag": "A code review, pull request, or diff to look at.",
        "hourglass": "Waiting on someone or something else; blocked.",
        "speech_balloon": "A question, or a request to explain something.",
        "wave": "A greeting or hello.",
        "eyes": "Anything that does not clearly fit another option.",
    },
)
```

Every entry describes a situation the inbound message can be in. None describes the state of the run, which the classifier cannot see. The last entry is the catch-all the confidence floor lands on ([Drezner](https://www.langchain.com/blog/slack-sdk-managed-deep-agents)).

## Key Takeaways

- Write down the signal's generating input before its copy. The inbound message settles how a request was read; a clock settles nothing about the work.
- Audit a surface you inherited by reading its handler, not its text. A thread renders both shapes identically, and only the handler says which one you have.
- Re-read the vocabulary criteria whenever a second agent joins the workspace, because the glyph's meaning follows the domain and the criteria do not.
- Where the agent itself sources the signal, treat the signal as a claim with an incentive behind it, not a reading.

## Related

- [Tool Preamble: User-Visible Status Updates Before Tool Calls](tool-preamble-status-update.md) — the same-path case, where the working model writes its own preface
- [Long-Running Agents: Durability and Resumability Across Sessions](long-running-agents.md) — the durations that widen the window for catching a signal out
- [Steering Running Agents: Mid-Run Redirection and Follow-Ups](steering-running-agents.md) — the control a reader reaches for once a signal says to intervene
- [Chat-Platform Agent Delegation: Invoking Cloud Coding Agents from Team Channels](../../workflows/chat-platform-agent-delegation.md) — the surface these signals render in
- [Transcript-Measured Review Coverage](../../verification/transcript-measured-review-coverage.md) — measuring what an agent did against what it reported
