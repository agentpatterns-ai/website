---
title: "Codex 常见故障排查"
description: "按登录、可执行文件、MCP、技能、乱改文件的顺序排查。不要一上来重装编辑器。"
tags:
  - codex
  - tool-agnostic
  - security
last_reviewed: 2026-08-28
---

# Codex 常见故障排查

> 按登录、可执行文件、MCP、技能、乱改文件的顺序查。不要一上来重装编辑器。

## 登录和权限

命令能跑但任务立刻失败，先看是否掉登录、账号是否仍能使用 Codex（[codexapp.cc 排错章](https://codexapp.cc/guides/codex-troubleshooting)）。网页能用、CLI 不能，多半是本机登录态而不是模型本身。公司网络会挡 OAuth 或 WebSocket，先换网络验证。权限模式过严时，Agent 会像坏了一样拒绝改文件——重装之前先问一个只读问题。

## 命令找不到或立刻退出

用 `which`（Windows 上 `where`）看 PATH。装在用户目录的二进制，图形终端常常看不见（[codexapp.cc 排错章](https://codexapp.cc/guides/codex-troubleshooting)）。版本命令能跑、任务立刻崩：看 Codex 主目录里的日志，而不是先卸扩展。先新开终端、核对可执行文件路径，再证明登录和一次只读调用。

## MCP 连上了但调用失败

先分清未连接和已连接但工具报错。未连接就查命令、参数、工作目录和 PATH；已连接就看服务器日志（[codexapp.cc 排错章](https://codexapp.cc/guides/codex-troubleshooting)）。stdio 服务器若在等待交互，客户端只会显示超时——把配置里的同一条命令在普通终端手动跑一遍。收窄到只读工具，检查允许目录和过期登录。

## 技能不出现或不遵守

确认文件夹里真有 `SKILL.md`，且在客户端会扫描的位置；改完重启（[codexapp.cc 排错章](https://codexapp.cc/guides/codex-troubleshooting)）。能看见却不遵守，通常是描述不像触发器，或说明书里的禁区和技能打架——先点名调用（CLI 或扩展里 `/skills` 或 `$`，[官方 Build skills 文档](https://learn.chatgpt.com/docs/build-skills)）。两个同名技能通常不能同时选，改掉一个名字。

## 改了不该改的文件

先回退，再把路径禁区写进 AGENTS.md 顶部，不要靠下一句提示词补救（[codexapp.cc 排错章](https://codexapp.cc/guides/codex-troubleshooting)）。范围太大时拆任务，下一轮只给一个目录。官方排错文档另有一条容易误判的：评审面板会显示基于 git 状态的改动，包括 Codex 没改过的文件；只想看上一轮改动，把 diff 面板切到 **Last turn** 视图（[官方 Troubleshooting](https://learn.chatgpt.com/docs/reference/troubleshooting)）。

## 重装之前先看哪

日志通常在 Codex 主目录，默认 `~/.codex`，环境变量可以改位置（[官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)）。求助时只贴去敏后的片段，不要整个主目录。最后手段才是删掉整个主目录重来——要重新登录，本地缓存也会掉。

## Windows 和 WSL

仓库在哪边，Agent 就跑在哪边；穿越边界会像文件丢了（[codexapp.cc 排错章](https://codexapp.cc/guides/codex-troubleshooting)）。官方扩展常常有是否走 WSL 的开关；装在 Windows 上的 CLI 不会神奇看见 Linux 路径。

## 排错清单

- [ ] 只读问题上登录能用
- [ ] 新终端里能找到二进制
- [ ] MCP 进程能手动拉起
- [ ] 乱改已回退并写进禁区

还是不行：减到没有 MCP、没有技能的只读问题。若这也不行，回到[安装、登录与首次自检](install-and-login.md)重做自检。

## 相关

- [安装、登录与首次自检](install-and-login.md)
- [日常三件套：AGENTS.md、技能与 MCP](main-workflows.md)
- [官方 Troubleshooting](https://learn.chatgpt.com/docs/reference/troubleshooting)
- [Bounding a Headless Codex Run Without a Turn Cap](../workflows/headless-codex-bounding.md)
