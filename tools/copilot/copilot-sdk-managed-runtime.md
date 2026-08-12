---
title: "Embedding the Copilot SDK in a Managed Java Runtime"
description: "The Java binding asks a host for its threads. What that costs an application with its own concurrency model, and the JDK level the design assumes."
tags:
  - agent-design
  - copilot
applies_to: "copilot@1.x"
last_reviewed: 2026-08-12
status: current
---

# Embedding the Copilot SDK in a Managed Java Runtime

> Embedding the Copilot SDK in a JVM service turns on one seam: the executor you hand the client.

The Copilot SDK's Java binding asks the host application for its threads. `CopilotClientOptions.setExecutor(...)` accepts an `Executor`, and inside a Jakarta EE container that executor has to be built from the container's `ManagedThreadFactory`, or the tool callbacks the model invokes run without CDI, JNDI, and transaction context ([Using the GitHub Copilot SDK for Java](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)). Everything else is ordinary library integration; that one choice is where a managed runtime differs from a script.

## When this applies

Three conditions carry the design, and it degrades if any is missing.

A JDK new enough for virtual threads. The binding accepts "Java 17 or later" but recommends JDK 25, and the shipped multi-release jar "automatically uses virtual threads for its default internal executor" on JDK 25 and above ([java binding README](https://github.com/github/copilot-sdk/tree/main/java)). Virtual threads arrived in Java 21 ([JEP 444](https://openjdk.org/jeps/444)), so the SDK's own floor predates the design it recommends.

A host that propagates context across threads. The post cites section 5.2 of the Jakarta Concurrency 3.1 specification: application-created threads must be obtained from a `ManagedThreadFactory` so the container can track them for lifecycle shutdown, apply concurrency policy, and propagate context automatically ([GitHub Engineering](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)). A tool callback that injects a JPA repository only works because that propagation happened.

Tolerance for a preview artifact. The published coordinate is `com.github:copilot-sdk-java:1.0.10-preview.0` ([README](https://github.com/github/copilot-sdk/tree/main/java)), and the annotation-based tool API is experimental behind a compiler opt-in (`-Acopilot.experimental.allowed=true`). The SDK as a whole [went generally available on 2026-06-02](https://github.blog/changelog/2026-06-02-copilot-sdk-is-now-generally-available); this binding has not caught up.

## The executor seam

Headless server use runs the client in `CopilotClientMode.EMPTY`: no IDE integration, the client talks directly to the Copilot CLI, and CLI 1.0.71 or later is required ([GitHub Engineering](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)). The same options object takes the executor, so the wiring is a single construction site.

Calls return `CompletableFuture<T>`, and a turn is driven by `session.sendAndWait(prompt).get()`. That one `.get()` runs the whole agentic loop, during which "the model reasons, calls your tools (potentially multiple times), and returns its final response" ([GitHub Engineering](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)). Streaming events arrive through `session.on(...)`, which fires typed events such as `AssistantMessageEvent` and `ToolExecutionStartEvent` while the loop is still running ([java binding README](https://github.com/github/copilot-sdk/tree/main/java)).

## Defining tools

The binding offers three registration shapes ([GitHub Engineering](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)): annotated methods (`@CopilotTool`, collected with `ToolDefinition.fromObject(this)`), inline lambdas (`ToolDefinition.from(name, description, params, handler)`), and scanning tools declared in separate CDI beans. Annotated tools also need an `annotationProcessorPath` entry in the compiler plugin, so they are a build change and not only a code change.

What the agent may reach is bounded by `sessionConfig.setAvailableTools(new ToolSet()...)`, which restricts it to named custom and built-in tools; the sample defaults permission handling to `PermissionHandler.APPROVE_ALL`, a development setting rather than a production one ([GitHub Engineering](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)).

## Why it works

An agent turn is dominated by waiting on inference, and the JVM has two separate problems with that. The first is cost. A virtual thread that blocks unmounts from its carrier and waits in memory, releasing the platform thread for other virtual threads ([JEP 444](https://openjdk.org/jeps/444)), and GitHub's post states the consequence for this API directly: "On a virtual thread, `.get()` is cheap. No platform thread is consumed while waiting" ([GitHub Engineering](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)). A blocking, readable call shape therefore stops being a scalability problem. The second is correctness. Tool callbacks are where the agent touches application state, and they run on SDK-owned threads, so routing those threads through the container's factory is what lets a callback resolve a repository and join a transaction. The binding exposes exactly one hook for threading, and it happens to be the seam a managed runtime needs.

## When this backfires

- Running on JDK 17 through 20. Virtual threads did not ship until Java 21 ([JEP 444](https://openjdk.org/jeps/444)), so every `.get()` parks a platform thread for a full agentic turn. The SDK accepts these versions; the design argument does not.
- Running on JDK 21 through 23 with `synchronized`-heavy libraries. A virtual thread that blocks inside a `synchronized` method or block is pinned to its carrier and cannot unmount, which [JEP 491](https://openjdk.org/jeps/491) fixed only in Java 24. Netflix hit exactly this on Java 21: four pinned virtual threads exhausted the four-thread carrier pool on a 4-vCPU instance, the service stopped serving traffic while the JVM stayed up, and sockets piled up in `closeWait`. The offending `synchronized` was inside a tracing library, not application code, and the failure is hard to see: virtual thread stacks are absent from `jstack` output and Java 21 `jcmd Thread.dump_to_file` dumps carry no lock-ownership information, so the instance presents as an idle JVM ([Netflix Technology Blog](https://netflixtechblog.com/java-21-virtual-threads-dude-wheres-my-lock-3052540e231d)).
- Passing a plain executor. A bare virtual-thread-per-task executor inside a container drops the context the callbacks depend on, and the failure surfaces inside a tool rather than at startup.
- Hosts with no container to integrate with. Context propagation is most of what this binding asks of you, so a plain `main()` pays the ceremony and collects none of the benefit.
- Teams that need a pinned API. Preview versioning and a flag-gated annotation processor suit a slow upgrade cadence badly.

Out-of-process is a real alternative, and the SDK's headless mode already shells out to the CLI. A hung agent turn behind a queue is a consumer you can kill and retry. In-process on the wrong JDK it is a pinned carrier thread.

## Example

Wiring a container-managed virtual thread factory into the client, from the Jakarta EE sample ([GitHub Engineering](https://github.blog/engineering/using-the-github-copilot-sdk-for-java/)):

```java
@Resource(lookup = "concurrent/virtualThreadFactory")
private ManagedThreadFactory virtualThreadFactory;

Executor managedVirtualExecutor = runnable ->
    virtualThreadFactory.newThread(runnable).start();

CopilotClientOptions copilotClientOptions = new CopilotClientOptions()
        .setMode(CopilotClientMode.EMPTY)
        .setCopilotHome(copilotHome)
        .setExecutor(managedVirtualExecutor);
```

That lambda is the whole integration: the container hands out the thread, the SDK runs its loop on it, and CDI, JNDI, and transaction context reach the tool callbacks. Swapping in `Executors.newVirtualThreadPerTaskExecutor()` compiles, runs, and breaks the callbacks.

## Key Takeaways

- `setExecutor` is the binding's only threading hook, and in a container it must be fed from a `ManagedThreadFactory` or tool callbacks lose their context.
- The JDK level is a design input rather than a build detail: virtual threads are absent below Java 21 and pin on `synchronized` blocks below Java 24.
- `sendAndWait(...).get()` runs an entire agentic loop in one blocking call, which is only affordable on a virtual thread.
- The Java artifact is still preview-versioned and its annotation tool API is flag-gated, so binding parity with the GA SDK is not a given.

## Related

- [GitHub Copilot SDK](copilot-sdk.md) — what the SDK provides, the agent-in-app pattern, and its cost and lock-in trade-offs
- [MCP Integration](mcp-integration.md) — connecting the agent to external tools over Model Context Protocol
- [Custom Agents, Skills & Plugins](custom-agents-skills.md) — the declarative alternative to defining tools in host code
- [Copilot CLI BYOK and Local Model Support](copilot-cli-byok-local-models.md) — pointing the same runtime at another provider
- [Cost-Aware Agent Design: Route by Complexity, Not Habit](../../token-engineering/cost-aware-agent-design.md) — budgeting the turns an embedded loop will run
