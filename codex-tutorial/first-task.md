---
title: "用 Codex 完成第一个可复查的任务"
description: "选一个能 diff、能回退的小改动。目标是走通「说明任务 → 看补丁 → 留下或丢掉」，不是炫技。"
tags:
  - codex
  - tool-agnostic
  - workflows
last_reviewed: 2026-08-28
---

# 用 Codex 完成第一个可复查的任务

> 选一个能 diff、能回退的小改动。目标是走通「说明任务 → 看补丁 → 留下或丢掉」，不是炫技。

## 动手前的五分钟

- 用一个你拥有的 git 仓库，工作区干净，当前在普通功能分支（[codexapp.cc 第三章](https://codexapp.cc/guides/codex-first-task)）
- 先能自己跑一项检查：测试、类型检查或 lint。Agent 需要一个你也看得懂的完成标准
- 官方文档建议任务前后各建一个 git checkpoint，方便回退改动（[Codex CLI 官方文档](https://learn.chatgpt.com/docs/codex/cli)）
- 仓库很大时，用练习分支或一个你自己的小项目。这一课练的是闭环，不是业务域

## 把任务说成可验收的句子

坏任务：把代码变好。好任务：在这个测试文件里补一个失败用例，再改实现让它通过，不要动无关目录（[codexapp.cc 第三章](https://codexapp.cc/guides/codex-first-task)）。

写清三件事：哪些路径能改、哪些命令能跑、什么叫完成。范围是给你自己看的，也是给 Agent 看的。一段可改写的提示词：

```text
在 tests/auth_test.py 里补一个失败用例，只改应该让它通过的实现，跑 `npm test`，
不要提交也不要推送，不要碰其他文件。
```

- 点名文件或目录
- 给出验证命令
- 写上不要提交密钥、不要推远程

## 跑起来

在仓库根目录启动文档里的 Codex 会话命令。再留一个终端跑 `git status` 和验证命令——不要让 Agent 成为唯一的成功汇报（[codexapp.cc 第三章](https://codexapp.cc/guides/codex-first-task)）。若文档有非交互调用（`codex exec`），可以用来丢一条提示，但文件仍要你自己看。

## 看 diff，而不是看自信的总结

Agent 很会说"已完成"。你要看改动的文件列表和具体 hunk；多出来的重构，默认先丢掉（[codexapp.cc 第三章](https://codexapp.cc/guides/codex-first-task)）。然后用你自己的命令再跑一遍——测试绿了但你看不懂的改动，仍然算未完成。

盯着顺手重构：重命名、新格式化工具、额外依赖。你没要的就回退。

## 第二轮怎么收

第一轮常会漏测试或改太大。第二轮只说漏了什么，不要把任务重写成史诗（[codexapp.cc 第三章](https://codexapp.cc/guides/codex-first-task)）。

连续两轮仍在扩散，停。要么你范围太大，要么仓库缺少说明书——下一章去写 AGENTS.md（[日常三件套：AGENTS.md、技能与 MCP](main-workflows.md)）。

## 第一课失败也算学过

- 登录过期、PATH 指错、仓库太大却不给范围：去 [Codex 常见故障排查](troubleshooting.md)，不要在这里加 MCP
- Agent 改了不该改的文件：回退，把 diff 留下来当反面教材，写进即将出现的 AGENTS.md
- 若客户端提供撤销，可以用，但仍然要跑 git

## 清单

- [ ] 干净的 git status，分支可以丢掉
- [ ] 提示里有路径、命令和禁区
- [ ] 你自己的验证命令，由你来跑
- [ ] 多余的改动回退
- [ ] 完成意味着你能解释每个 hunk，或者已经回退了讲不清的部分

## 相关

- [日常三件套：AGENTS.md、技能与 MCP](main-workflows.md)
- [Bounding a Headless Codex Run Without a Turn Cap](../workflows/headless-codex-bounding.md)
- [Codex CLI 官方文档](https://learn.chatgpt.com/docs/codex/cli)
