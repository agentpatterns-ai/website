---
title: "日常三件套：AGENTS.md、技能与 MCP"
description: "AGENTS.md 是始终生效的仓库说明书，技能是按任务加载的可复用剧本，MCP 是仓库外的手。先写说明书，再抽技能，最后才接线。"
tags:
  - codex
  - instructions
  - standards
  - mcp
  - skills
  - tool-agnostic
last_reviewed: 2026-08-28
---

# 日常三件套：AGENTS.md、技能与 MCP

> AGENTS.md 是始终生效的说明书，技能是按任务加载的剧本，MCP 是仓库外的手。先写说明书，再抽技能，最后才接线。

## AGENTS.md：仓库级说明书

Codex 在开始任何工作之前读取 AGENTS.md（[官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)）。发现顺序：

1. 先读 Codex 主目录（默认 `~/.codex`）里的全局文件：`AGENTS.override.md` 优先，否则 `AGENTS.md`
2. 从项目根（通常是 git 根）往下走到当前目录，逐层读取，每层最多一个文件
3. 拼接时根目录在前，靠近当前目录的文件排在后面、覆盖更早的指引

拼接总量有上限：`project_doc_max_bytes`，默认 32 KiB（同上）。所以说明书要短：把最硬的三条禁区写在第一屏，长流程不要塞进来。仓库根放团队硬约束，子目录放该包自己的测试命令，用户级放个人口味（[codexapp.cc 第四章](https://codexapp.cc/guides/codex-agents-md)）。

一份可以借的起手结构（示例，以你自己的仓库事实为准）：

```md
# AGENTS.md

- 这是什么项目：一句话
- 验证命令：npm test
- 禁止提交：任何 .env 或密钥文件
- 生成文件放：docs/generated/
```

跨工具视角：本仓库的 [AGENTS.md 标准页](../standards/agents-md.md) 讲这个文件作为开放标准的来龙去脉，[Getting Started: Setting Up Your Instruction File](../instructions/getting-started-instruction-files.md) 从零教你怎么搭。

## 技能：可复用剧本

技能是"带指令、资源和可选脚本的目录"，核心文件是 `SKILL.md`，必须包含 `name` 和 `description`（[官方 Build skills 文档](https://learn.chatgpt.com/docs/build-skills)）。关键机制：

- **渐进式披露**：ChatGPT 和 Codex 先看到技能的名字和描述，决定使用时才加载完整的 `SKILL.md`（同上）
- **两种调用方式**：显式调用——CLI 或 IDE 扩展里用 `/skills` 或 `$` 提及；隐式匹配——任务和 `description` 对上时自动选择（同上）
- 技能构建在开放技能标准之上（[agentskills.io](https://agentskills.io)，同上）
- 独立技能在 ChatGPT 桌面应用、Codex CLI 和 IDE 扩展里都可用（同上）

什么时候写：第三次打同一套步骤，就该写进 `SKILL.md`，而不是更长的聊天（[codexapp.cc 第五章](https://codexapp.cc/guides/codex-skills)）。描述要写得像触发器，名称要能打出来。

跨工具视角：[Agent Skills: A Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)。

## MCP：仓库外的手

MCP 把模型接到工具和上下文。本地 Codex 客户端——ChatGPT 桌面应用、Codex CLI、IDE 扩展——共享同一份 MCP 配置（[官方 MCP 文档](https://learn.chatgpt.com/docs/extend/mcp)）：

- 配置位置：默认 `~/.codex/config.toml`；可信项目也可以用 `.codex/config.toml` 做项目级配置（同上）
- 支持的服务器：STDIO（本地进程）和 Streamable HTTP（远程地址，支持 Bearer / OAuth 认证）（同上）
- 桌面应用里的入口：Settings → MCP servers → Add server（同上）

什么时候接：只有仓库里没有的能力才接线，先做只读调用，再谈写权限。一行 git 或测试就够的事，留在命令里（[codexapp.cc 第六章](https://codexapp.cc/guides/codex-mcp)）。密钥放环境变量或系统钥匙串，配置里只留占位符；进过聊天或截图的密钥一律当作泄漏。每条 MCP 工具的 schema 一开始就占上下文，任务结束关掉刚加的。

跨工具视角：[MCP: The Open Protocol Connecting Agents to External Tools](../standards/mcp-protocol.md)。

## 顺序与最小化

官方把定制化分成互补的几层：AGENTS.md（持久指引）、记忆、技能（可复用工作流）、MCP（外部系统）、子代理（[官方 Customization 总览](https://learn.chatgpt.com/docs/customization/overview)）。推荐顺序（[codexapp.cc 教程总览](https://codexapp.cc/guides/codex)）：

1. 先写一页以内的 AGENTS.md
2. 同一任务重复第三次时抽成技能
3. 最后才接一条只读 MCP

反过来会先得到一个会乱调外部系统、却不懂你仓库的 Agent。

## 无头运行

CI 和脚本场景用 `codex exec`。它没有 `--max-turns` 之类的轮次上限，边界要由调用方（墙钟、预算）和沙箱策略提供；沙箱策略分 read-only / workspace-write / full access 三档（[Bounding a Headless Codex Run Without a Turn Cap](../workflows/headless-codex-bounding.md)）。

## 清单

- [ ] 一页以内的 AGENTS.md，禁区在第一屏
- [ ] 第三遍重复的步骤已经写成了技能
- [ ] MCP 只接了任务需要的一条，先只读
- [ ] 密钥在环境变量，不在 git

## 相关

- [AGENTS.md: Project-Level README for AI Coding Agents](../standards/agents-md.md)
- [Getting Started: Setting Up Your Instruction File](../instructions/getting-started-instruction-files.md)
- [MCP: The Open Protocol Connecting Agents to External Tools](../standards/mcp-protocol.md)
- [Agent Skills: A Cross-Tool Task Knowledge Standard](../standards/agent-skills-standard.md)
- [Bounding a Headless Codex Run Without a Turn Cap](../workflows/headless-codex-bounding.md)
