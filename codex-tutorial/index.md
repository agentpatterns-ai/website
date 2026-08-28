---
title: "Codex 教程：ChatGPT Codex、Codex CLI 与 IDE 扩展"
description: "面向开发者的 Codex 上手教程：先分清 ChatGPT Codex、Codex CLI 与 IDE 扩展三个入口，再装通一扇门、完成第一个可复查的任务，然后写 AGENTS.md、技能和 MCP。"
tags:
  - codex
  - tool-agnostic
  - instructions
  - index
last_reviewed: 2026-08-28
---

# Codex 教程

> 给已经会用 git 和终端的开发者的一套 Codex 上手路径：分清入口、装通一扇门、完成第一个可复查的任务，再写 AGENTS.md、技能与 MCP。

## 这套教程是什么

本栏目是一套用简体中文写的 Codex 上手教程，正文是本站原创概述，不是官方文档的粘贴。Codex 指 OpenAI 面向写代码的一套 Agent 产品：ChatGPT 里的 Codex、Codex CLI 和 IDE 扩展。参考来源：[codexapp.cc](https://codexapp.cc/)（在线工具与资源发现站）的 [Codex 教程系列](https://codexapp.cc/guides/codex)，以及官方文档入口 [developers.openai.com/codex](https://developers.openai.com/codex)——本次核对时该地址重定向到 [learn.chatgpt.com 的 ChatGPT/Codex 文档](https://learn.chatgpt.com/docs)。

只写当天能核对的公开用法。订阅档位、地区可用性、精确版本号会变，文中遇到时以官方页面为准，不编造价格、模型名或截图。命令、包名、文件名与 URL 保持原文不翻译。

## 阅读对象

已经会 git、会开终端、想让 Agent 在自己仓库里干活的开发者。不要求先背完提示词工程。只想在网页里问一句语法，用普通 ChatGPT 就够，不需要本教程。

## 学习顺序

按依赖排，别跳：

1. [Codex 现在指什么](what-is-codex.md)——分清三个入口，不装软件
2. [安装、登录与首次自检](install-and-login.md)——先选一扇门装通并登录
3. [用 Codex 完成第一个可复查的任务](first-task.md)——小改动、看 diff、回退
4. [日常三件套：AGENTS.md、技能与 MCP](main-workflows.md)——说明书、技能、外部工具
5. [Codex 常见故障排查](troubleshooting.md)——卡住时按顺序查

一个专注的下午通常够装通、做一件小事、写一页 AGENTS.md；技能和 MCP 更适合第二次坐下来，那时你已经有一份信得过的 diff（[codexapp.cc 教程总览](https://codexapp.cc/guides/codex)）。

## 页面列表

| 页面 | 内容 |
|------|------|
| [Codex 现在指什么](what-is-codex.md) | ChatGPT Codex、Codex CLI、IDE 扩展三个入口；和旧 Codex 补全模型的区别 |
| [安装、登录与首次自检](install-and-login.md) | 选一扇门、官方安装方式、登录、临时目录只读自检 |
| [用 Codex 完成第一个可复查的任务](first-task.md) | 把任务说成可验收的句子，看 diff 而不是看总结 |
| [日常三件套：AGENTS.md、技能与 MCP](main-workflows.md) | 仓库说明书、可复用技能、仓库外工具，只接需要的 |
| [Codex 常见故障排查](troubleshooting.md) | 登录、PATH、MCP、技能、乱改文件的排查顺序 |

## 相关

- [Bounding a Headless Codex Run Without a Turn Cap](../workflows/headless-codex-bounding.md)——`codex exec` 无头运行的边界控制（无 `--max-turns`，靠沙箱策略和调用方超时）
- [Codex CLI 官方文档](https://learn.chatgpt.com/docs/codex/cli)
- [Codex IDE 扩展官方文档](https://learn.chatgpt.com/docs/codex/ide)
- [ChatGPT 桌面应用官方文档](https://learn.chatgpt.com/docs/app)
