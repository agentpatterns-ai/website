---
title: "Bounding an Embedded Copilot SDK Agent's Tool Set"
description: "Two independent controls decide what an embedded Copilot agent can call, and a handoff framework supplies tools at invocation that the session config never named."
tags:
  - agent-design
  - copilot
applies_to: "copilot@1.x"
last_reviewed: 2026-09-16
status: current
---

# Bounding an Embedded Copilot SDK Agent's Tool Set

> Two independent controls decide what an embedded Copilot agent can reach, and a handoff framework adds tools to that set at invocation.

An application that embeds the Copilot SDK for non-coding work has to take tools away from the runtime as well as add them. `SessionConfig.AvailableTools` decides which tool names exist for a session. `OnPermissionRequest` decides whether a call proceeds. Setting one does nothing to the other, and the Interview Coach sample sets them in opposite directions: it narrows `AvailableTools` to host-supplied tools while handing the permission hook `PermissionHandler.ApproveAll` ([AgentDelegateFactory.cs](https://github.com/Azure-Samples/interview-coach-agent-framework/blob/main/src/InterviewCoach.Agent/AgentDelegateFactory.cs)).

## When this applies

Two conditions, and dropping either one changes the answer.

The application's job is not editing code. An interview coach reads a resume and saves a record; it "has no reason to run shell commands or edit the application's source files" ([Build an interview coach app with the GitHub Copilot SDK](https://devblogs.microsoft.com/blog/build-an-interview-coach-app-with-the-github-copilot-sdk/)). Embed the SDK for coding work and there is nothing to subtract.

An orchestration framework sits above the SDK and encodes control flow as tool calls. Handoff orchestration in Microsoft Agent Framework "only supports `Agent` and the agents must support local tools execution" ([handoff orchestration](https://learn.microsoft.com/agent-framework/workflows/orchestrations/handoff)). Without that layer the tool set is fixed at configuration time and the merge below is ceremony.

## Subtracting the built-in tools

The sample starts the client in `CopilotClientMode.Empty` and lists every allowed tool with a `custom:` prefix, which "selects those supplied tools rather than Copilot CLI's built-in tools" ([devblogs.microsoft.com](https://devblogs.microsoft.com/blog/build-an-interview-coach-app-with-the-github-copilot-sdk/)).

The permission hook does not do this job. GitHub's Agent Framework provider documents the default: "By default, the agent cannot execute shell commands, read/write files, or fetch URLs. To enable these capabilities, provide a permission handler via `SessionConfig`", and `OnPermissionRequest` decides "Copilot's built-in shell/file/URL prompts" ([Agent Framework Copilot provider](https://learn.microsoft.com/agent-framework/agents/providers/github-copilot)). Approve-all opens that gate on the whole built-in set. The allowlist is what keeps the set empty.

## What the orchestrator adds at invocation

A specialist that cannot transfer is stuck. Agent Framework supplies transfer tools when it invokes an agent, not when you configure one, so a list fixed at configuration time omits them. The sample's own comment names the problem: "Handoff orchestration supplies transfer tools through `ChatClientAgentRunOptions`. The Copilot adapter currently ignores run options, so recreate its lightweight agent wrapper per invocation with the merged static and handoff tool set" ([AgentDelegateFactory.cs](https://github.com/Azure-Samples/interview-coach-agent-framework/blob/main/src/InterviewCoach.Agent/AgentDelegateFactory.cs)).

That workaround is bound to a version. The sample repository "uses floating package versions, so this describes the linked implementation rather than a limitation of every Copilot SDK release" ([devblogs.microsoft.com](https://devblogs.microsoft.com/blog/build-an-interview-coach-app-with-the-github-copilot-sdk/)). The habit generalizes past the bug: when you put a runtime under an orchestrator, check what the orchestrator hands you at call time.

## Why it works

The reachable action space is an intersection of two sets computed in different places. `AvailableTools` is a namespace filter evaluated when the session is built. `OnPermissionRequest` is an interception point evaluated per call. A host that only tightens the permission hook still leaves every built-in name callable, and a host that only narrows the allowlist still approves whatever remains. Interview Coach gets a document-and-records agent out of a coding runtime because its filter is narrow, not because its hook is careful.

The invocation-time half follows from where control flow lives. A handoff framework does not route the conversation itself. It gives the model transfer functions and lets the model call one, so control flow and application work share a namespace. Filter that namespace at configuration time and you have removed half of it.

## When this backfires

- The host installs its own `OnPreToolUse` hook through `SessionConfig.Hooks`. That hook takes precedence, the default approval hook is never installed, and the host silently owns enforcement for every `ApprovalRequiredAIFunction` it registered, with a log warning as the only signal ([Agent Framework Copilot provider](https://learn.microsoft.com/agent-framework/agents/providers/github-copilot)).
- The work genuinely needs the built-ins. Subtracting file and shell tools from an application that edits files means writing custom tools that duplicate what the runtime already ships, and maintaining them against it.
- You treat the allowlist as the security boundary. "Tool selection controls exposure, but it is not a complete security boundary", and a deployed application "still needs authorization checks and an appropriate policy for the actions its tools can perform" ([devblogs.microsoft.com](https://devblogs.microsoft.com/blog/build-an-interview-coach-app-with-the-github-copilot-sdk/)).
- There is no orchestrator. A single agent with a static tool list pays for the per-invocation rebuild and gets nothing back.
- You pin to this sample's adapter workaround. Floating versions mean it may already be unnecessary, and rebuilding the wrapper on every call is not free.

## Example

Two excerpts from the sample ([AgentDelegateFactory.cs](https://github.com/Azure-Samples/interview-coach-agent-framework/blob/main/src/InterviewCoach.Agent/AgentDelegateFactory.cs)). First, what `CreateCopilotSessionConfig` returns — `Tools` carries the definitions and their handlers, `AvailableTools` names which of them the agent may call:

```csharp
return new SessionConfig
{
    AvailableTools = copilotTools.Select(tool => $"custom:{tool.Name}").ToList(),
    OnPermissionRequest = PermissionHandler.ApproveAll,
    Tools = copilotTools,
};
```

Second, the merge applied on every invocation:

```csharp
internal static IList<AITool> MergeCopilotTools(
    IList<AITool>? configuredTools, AgentRunOptions? options)
{
    var runTools = (options as ChatClientAgentRunOptions)?.ChatOptions?.Tools;

    return (configuredTools ?? [])
        .Concat(runTools ?? [])
        .DistinctBy(tool => tool.Name, StringComparer.Ordinal)
        .ToList();
}
```

The merge deduplicates by name, because the orchestrator and the host can both offer a tool called the same thing. The adapter reaches the workflow through `client.AsAIAgent(config, ownsClient: false, ...)`, where `ownsClient: false` stops the per-invocation wrapper disposing the shared client.

## Key Takeaways

- `AvailableTools` and `OnPermissionRequest` are independent. Tightening the permission hook leaves every built-in tool name callable.
- The `custom:` prefix is what excludes Copilot CLI's built-in tools from an embedded session.
- Under a handoff orchestrator the tool set is composed at invocation, so merge the framework's transfer tools with your configured ones or the agent cannot hand off.
- Neither control authorizes anything. Put the access check inside the tool, where it can see the caller.
- Check the adapter against your SDK version before copying the merge. The sample's floating dependencies date its workaround.

## Related

- [GitHub Copilot SDK](copilot-sdk.md) — what the runtime provides, the agent-in-app pattern, and its cost and lock-in trade-offs
- [Embedding the Copilot SDK in a Managed Java Runtime](copilot-sdk-managed-runtime.md) — the other integration seam, where the host supplies threads instead of tools
- [Agent as Tool vs Handoff: Who Keeps the Conversation](../../patterns/agent-design/agent-as-tool-vs-handoff.md) — why a handoff needs transfer tools at all, and when delegation is the better shape
- [MCP Integration](mcp-integration.md) — how the document and record services in this sample reach the agent
- [Tool Minimalism and High-Level Prompting](../../tool-engineering/tool-minimalism.md) — the general case for a small, non-overlapping tool set
