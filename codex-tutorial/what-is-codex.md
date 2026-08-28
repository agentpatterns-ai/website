---
title: "Codex 现在指什么：ChatGPT Codex、Codex CLI 与 IDE 扩展"
description: "2025 年之后，Codex 通常指 OpenAI 面向写代码的 Agent 产品族：ChatGPT 里的 Codex、Codex CLI 和 IDE 扩展，而不是当年那个补全模型。"
tags:
  - codex
  - tool-agnostic
  - tool-engineering
aliases:
  - Codex 是什么
  - OpenAI Codex
last_reviewed: 2026-08-28
---

# Codex 现在指什么

> 2025 年后，人们说的 Codex 通常不再只是当年那个补全模型的名字，而是 OpenAI 面向写代码的一套 Agent 产品：能读仓库、跑命令、把改动建议交给你复查。

## 名字为什么容易混

早期 Codex 常被当成补全模型的名字。现在搜索结果里的 Codex，多半指 OpenAI 的编程 Agent：它能读仓库、跑命令、提交改动建议，旧文章和新产品页说的不是同一件事（[codexapp.cc 第一章](https://codexapp.cc/guides/codex-what-it-is)）。若同事说"我用 Codex"，先问他用的是 ChatGPT 里的云端任务、本机 CLI，还是编辑器扩展——三个入口任务形状不同，配置却常常共用。

## 三个入口

| 入口 | 适合 | 官方来源 |
|------|------|----------|
| ChatGPT 里的 Codex（桌面应用 / 网页） | 人已经在浏览器或桌面应用里、仓库已连接时下较长任务 | 软件开发现场从模型下拉里选 Codex（[官方快速入门](https://learn.chatgpt.com/docs/quickstart)）；ChatGPT 桌面应用支持 macOS、Windows 和 Linux（[官方桌面应用文档](https://learn.chatgpt.com/docs/app)） |
| Codex CLI | 已经住在 shell 里，想在终端里检查、改代码、跑命令 | [Codex CLI 官方文档](https://learn.chatgpt.com/docs/codex/cli) |
| IDE 扩展 | 要在编辑器侧栏看文件树和内联 diff | VS Code 及兼容编辑器用官方扩展，Xcode 与 JetBrains 有各自的集成（[Codex IDE 扩展官方文档](https://learn.chatgpt.com/docs/codex/ide)） |

官方文档另列出 Codex cloud——把任务委托到隔离的云端环境（[ChatGPT/Codex 文档索引](https://learn.chatgpt.com/llms.txt)）。本教程主线先走本地入口。

## 一份配置习惯

登录态、`config.toml`、AGENTS.md 和技能目录在三个本地入口之间常常共用（官方定制化总览把定制层分成 AGENTS.md、记忆、技能、MCP 和子代理，互补而非竞争，[Customization](https://learn.chatgpt.com/docs/customization/overview)）。换窗口通常不是换一套完全不同的 Agent。但云端任务不一定能看见你笔记本上还没同步的文件（[codexapp.cc 第一章](https://codexapp.cc/guides/codex-what-it-is)）。

实用规则：先在一扇门上完成登录，再做第一个任务。只有出现一份可复查的 diff 之后，才打开第二个界面。

## Codex 不是什么

- 不是不看 diff 就合并的机器人——你还是作者，Agent 是会跑命令的助手（[codexapp.cc 第一章](https://codexapp.cc/guides/codex-what-it-is)）
- 不是官方安全审计，也不代替你们团队的威胁模型
- 不等于 Cursor、Claude Code 或其他编辑器——配置路径和模型选择不同
- 不是把生产密钥写进仓库的借口

## 什么时候值得打开它

任务能写成"在这些文件里做这件事，用这个命令验证"就值得打开；只是问一句语法，普通对话更快（[codexapp.cc 第一章](https://codexapp.cc/guides/codex-what-it-is)）。

- 值得：补测试、修类型错误、更新清单、起草 PR 说明
- 先别：生产数据迁移、不经人看的权限变更

## 与无头运行的区分

除了交互式入口，还有 `codex exec` 无头模式，供 CI 和脚本调用。它没有 `--max-turns` 之类的轮次上限，边界要由调用方的墙钟和沙箱策略提供（[Bounding a Headless Codex Run Without a Turn Cap](../workflows/headless-codex-bounding.md)）。

## 离开这一章时你该知道

- 能用一句话点出三个入口：ChatGPT 里的 Codex、Codex CLI、IDE 扩展
- 为安装选定一扇门（下一章再装）
- 写下至少一条你这周不让 Agent 做的事（密钥、生产数据、强制推送）

## 相关

- [安装、登录与首次自检](install-and-login.md)
- [Bounding a Headless Codex Run Without a Turn Cap](../workflows/headless-codex-bounding.md)
- [Codex CLI 官方文档](https://learn.chatgpt.com/docs/codex/cli)
- [Codex IDE 扩展官方文档](https://learn.chatgpt.com/docs/codex/ide)
