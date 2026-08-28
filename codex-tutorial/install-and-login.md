---
title: "安装、登录与首次自检"
description: "先选一扇门（CLI、IDE 扩展或 ChatGPT 里的 Codex）装通并登录，再做一次无害的只读自检。不要同一天配三个客户端。"
tags:
  - codex
  - tool-agnostic
  - instructions
last_reviewed: 2026-08-28
---

# 安装、登录与首次自检

> 先选一个入口装通并登录，再做一次无害的只读自检。不要同一天配三个客户端。

## 先选哪一扇门

- 整天在终端里看日志和测试 → 装 Codex CLI
- 主要在编辑器里点文件 → 装官方扩展
- 人已经在连着仓库的 ChatGPT 工作区 → 从那里开始

两扇门看起来差不多时选 CLI：你能对它要帮助、有日志目录、PATH 也能检查，这比沉默的侧栏好查（[codexapp.cc 安装章](https://codexapp.cc/guides/codex-install)）。三个入口常常共享登录和本地配置，先打通一个，排错才有对照物。

## 安装 Codex CLI

官方文档给出的安装方式（[Codex CLI 官方文档](https://learn.chatgpt.com/docs/codex/cli)）：

- macOS / Linux 独立安装脚本：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

- Windows（PowerShell）：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

- npm：`npm install -g @openai/codex`
- Homebrew：`brew install --cask codex`

可执行文件名和参数曾经改过，从你今天打开的官方页面抄，不要从旧 gist 抄（[codexapp.cc 教程总览](https://codexapp.cc/guides/codex)）。装完**新开一个终端**再检查 PATH。

## 安装 IDE 扩展

VS Code 及兼容编辑器通过扩展市场安装官方扩展，官方文档列出的安装入口是 VS Code 市场里的 `openai.chatgpt`，并给出 Cursor、Windsurf、VS Code Insiders 的安装链接；Xcode 和 JetBrains IDE 有各自的集成（[Codex IDE 扩展官方文档](https://learn.chatgpt.com/docs/codex/ide)）。

装扩展不等于已经登录：打开侧栏里的 Codex 面板，按提示登录。市场里若出现多个名字相近的扩展，先看发布者，只装官方发布者（[codexapp.cc 安装章](https://codexapp.cc/guides/codex-install)）。

## 从 ChatGPT 里打开 Codex

- ChatGPT 桌面应用支持 macOS、Windows 和 Linux（[官方桌面应用文档](https://learn.chatgpt.com/docs/app)）
- 打开应用，用 ChatGPT 账号登录；做软件开发时，从模型下拉里选 Codex（[官方快速入门](https://learn.chatgpt.com/docs/quickstart)）
- 也可以用 API 密钥使用 Codex，但部分功能可能不可用（[官方快速入门](https://learn.chatgpt.com/docs/quickstart)）。密钥只放环境变量或系统钥匙串，不要写进仓库
- 网页 / 桌面应用适合已经连上仓库的长任务。本机文件权限和 CLI 不完全一样，不要假设云端任务能看见你笔记本上未上传的文件（[codexapp.cc 安装章](https://codexapp.cc/guides/codex-install)）

## 登录与本地配置

- CLI 和扩展通常走 ChatGPT 登录（[官方认证文档](https://learn.chatgpt.com/docs/auth)）
- 本地状态常见位置是用户目录下的 Codex 主目录，默认 `~/.codex`，可用环境变量改位置，但目录必须先存在（[官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)）。里面会有配置、登录态、日志和技能缓存。把那目录当邮箱：不要打包装进 git
- Agent 的稳定设置写在 `config.toml`；环境变量适合一次性覆盖和密钥（[codexapp.cc 安装章](https://codexapp.cc/guides/codex-install)）
- 换机器时重新登录，不要复制会话文件

## 无害自检

在一个不重要的临时目录问一个只读问题——例如让它描述当前目录或列出顶层文件——不要一上来就对生产仓库开写（[codexapp.cc 安装章](https://codexapp.cc/guides/codex-install)）。官方 CLI 快速入门的第一句示例也是让 Codex 描述项目（"Tell me about this project"，[Codex CLI 官方文档](https://learn.chatgpt.com/docs/codex/cli)）。

能回答目录问题，说明登录和可执行文件都通了。若 shell 说找不到命令，那是安装或 PATH，不是模型——回到安装步骤，不要从随机博客再发明第二种安装器。

## 安装清单

- [ ] 只用官方包或官方扩展
- [ ] 装完新开终端，PATH 里有你刚装的可执行文件
- [ ] 登录完成，没有把密钥贴进仓库
- [ ] 在临时目录里做了一次只读自检
- [ ] 记下日志位置（默认 `~/.codex`）

## 下一步

- [用 Codex 完成第一个可复查的任务](first-task.md)
- 自检失败 → [Codex 常见故障排查](troubleshooting.md)

## 相关

- [Codex 现在指什么](what-is-codex.md)
- [Codex CLI 官方文档](https://learn.chatgpt.com/docs/codex/cli)
- [Codex IDE 扩展官方文档](https://learn.chatgpt.com/docs/codex/ide)
- [ChatGPT 桌面应用官方文档](https://learn.chatgpt.com/docs/app)
