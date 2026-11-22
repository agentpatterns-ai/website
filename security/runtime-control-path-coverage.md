---
title: "Runtime Control Path Coverage: Map What Each Layer Checks"
description: "A gateway or hook checks only the agent actions that cross it. Map the 15 action paths to your control layers; five bypass every sub-kernel design on paper."
term: "Runtime Control Path Coverage"
tags:
  - security
  - agent-design
  - tool-agnostic
  - arxiv
aliases:
  - action path coverage map
  - enforcement point coverage
  - agent gateway coverage gap
last_reviewed: 2026-11-21
maturity: emerging
---

# Runtime Control Path Coverage: Map What Each Layer Checks

> A runtime control checks only the agent actions whose path crosses it, so map each action path to the layer that sees it.

Runtime control path coverage is the set of an agent's action paths that a control actually evaluates. The guardscope paper states the limit plainly: "a control can only evaluate the actions that cross the point where it is placed, and an agent can act through more paths than the tool-call channel" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)). It counts 15 action paths and eight topology designs for where a control sits. In its derived matrix, five of the paths cross no enforcement point below the kernel ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).

This applies when your agent can execute locally: run a shell, write files, or spawn processes. In the paper's path table, P3 is when "the harness launches a subprocess (shell, interpreter, or executable)", and a P12 process "continues running or resumes after the invocation returns" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).

## The paths and who sees them

The paper groups the 15 paths into nine families. The table below copies four columns of its derived outcome matrix: T1 is a gateway for HTTP tool servers, T3 adds forced egress and proxies local tool servers, T4 is the harness's own permission chain, and T7 is the kernel position ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).

| Path | T1 gateway | T3 gateway, all tool servers | T4 harness | T7 kernel |
|---|---|---|---|---|
| P1 in-process tool execution | no | no | yes | no |
| P2 direct-origin OS operations | no | no | no | yes |
| P3 subprocess execution | no | no | yes | yes |
| P4 direct network egress | no | prevented | no | yes |
| P5 local-intermediary routing | no | no | no | yes |
| P6 HTTP tool-server call | yes | yes | yes | yes |
| P7 stdio tool-server call | no | yes | yes | yes |
| P8 local-IPC tool-server call | no | yes | yes | yes |
| P11 daemon or scheduler submission | no | no | no | conditional |
| P12 background processes | no | no | no | yes |
| P15 reverse protocol interaction | no | no | no | yes |

The table omits P9, P10, P13, and P14, whose conditional cells depend on deployment wiring. The paper names P2, P5, P11, P12, and P15 as the five paths that "bypass every design below the kernel" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)). In its path table, P5 is agent code calling a loopback helper or Unix-socket database, P11 is a task handed to crontab, systemd, or `docker.sock`, and P15 is a tool server calling back into the harness for sampling or elicitation.

The P3 and P12 rows differ because of process lifetime. A joined subprocess falls under the invocation's check, "whereas a P12 child outlives the invocation and its later operations receive no dispatch-time check" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)). The path table gives `nohup`, `setsid`, and shell background jobs as P12 examples.

## How to build the map

1. List which of the 15 paths your agent can take. The paper's own examples for P3, P4, P11, and P12 are a shell, `curl`, crontab, and `nohup`, so one shell tool reaches all four ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).
2. For each control you run, mark the paths whose transport crosses it. Gateways check only the tool-server calls that traverse them, and harness controls check only what the dispatcher dispatches ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).
3. Mark every path with no control as accepted risk, or close it with a block outside the policy. Forced egress turns P4 from bypassed to prevented ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).
4. Before trusting the map, prove each control is live. guardscope sends one action the loaded policy must deny and starts measuring only after the deny record appears. Without that gate, the run "would silently produce false bypassed results" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).

## Why it works

A control is an interception point on one transport. Each layer sees only the actions whose transport passes through it: gateways sit on tool-server traffic, hooks sit on the dispatcher, and kernel monitoring "observes nearly every action of the agent process tree" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)). Stacking sub-kernel controls therefore does not widen coverage: "no combination of the sub-kernel designs (T1–T6) checks them. Composition therefore adds inspectable features, as the T5 runs show, but not coverage" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)). ActPlane's authors reach the same conclusion independently: "Tool-call guardrails miss system actions that bypass the tool layer" ([Zheng et al., 2026](https://arxiv.org/abs/2606.25189v2)).

The paper's recommendation is to pair layers that sit at different depths, "such as harness-native enforcement with kernel-level monitoring" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)). The harness layer inspects the tool name, arguments, and session context. At the design level the two complement each other, because "the T7 position bound is blind only to P1, which the harness-native designs (T4–T6) check" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).

## When this backfires

- The five-path result is mostly derived, not measured. The workload exercised four of the 15 paths (P2, P4, P6, P7), so "the remaining paths, including every conditional cell, rest on the design analysis alone" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)). The authors developed the path list in discussion with two AI research models.
- A kernel position is not kernel coverage. The measured ActPlane run checked seven actions and bypassed eight, including all seven tool-call actions, because "the kernel position checks a channel only if a deployed hook covers it" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).
- Kernel records are noisy on shared hosts. The sensor "cannot distinguish agent processes from unrelated processes on the host" and carries no payload content ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)). OS sandboxes also return "opaque errors that confuse the agent" ([Zheng et al., 2026](https://arxiv.org/abs/2606.25189v2)).
- Checked does not mean safe. A checked action has crossed an enforcement point, which "does not imply that the control makes a correct decision or that the policy is well configured" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).
- The T4 column models permission modes with no sandbox. The paper lists process sandboxes such as claude-sandbox and Codex sandboxes as separate T4 variants marked prevention ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)), so the T4 column does not describe a harness with its sandbox on.
- A kernel layer costs more to deploy. The paper lists higher deployment cost among T7's drawbacks, "as it must be deployed in the same system as the target agent" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).

## Example

The paper ran its T5 design on the Pi harness: Pi's permission chain plus the enforcement module of Microsoft's Agent Governance Toolkit as a gateway in front. Both tool-call classes were mediated. Even so, "the eight actions of the direct-network, process-spawn, file-write, and credential-access classes take effect without any policy evaluation in every run" ([Toyoda et al., 2026](https://arxiv.org/abs/2611.15223v1)).

## Key Takeaways

- Start from the agent's capabilities. A shell tool reaches P11 and P12 through crontab and `nohup`, and no sub-kernel layer sees either.
- In the paper's matrix, no gateway or hook design checks background processes, daemon submissions, loopback helpers, direct OS operations, or server-initiated callbacks. The kernel position checks four of them and sees daemon submissions only when the later execution crosses a monitored hook. Adding another gateway or hook does not change that.
- Verify a kernel layer hook by hook. The measured ActPlane coverage stayed below the kernel position bound.
- Run a deny-first readiness probe before you read any coverage result.

## Related

- [MCP Runtime Control Plane: Policy Evaluation Between Agent and Tool](mcp-runtime-control-plane.md) — the gateway design whose coverage this map bounds
- [Cross-Layer Evidence for Agent Attack Detection](cross-layer-detection-evidence.md) — when kernel and application telemetry together beat either alone
- [Agent Network Egress Policy](agent-network-egress-policy.md) — the out-of-policy block that turns P4 from bypassed to prevented
- [Enforced Versus Advisory Controls in LLM-Native IDEs](enforced-versus-advisory-controls.md) — sorting safeguards by where they are evaluated
- [Defense-in-Depth Agent Safety](defense-in-depth-agent-safety.md) — layering independent mechanisms
