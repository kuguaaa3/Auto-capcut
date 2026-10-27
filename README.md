# Auto-capcut

**Codex 原生 AI 剪辑 Skill | 开发交接包（不是已完成的软件）**

> 截至 2026-10-27，仓库首先保存经过开发审计的需求、架构、交互路由、开源 Skill 调研、实施计划与验收标准。CapCut 官方连接、真实草稿及视频导出必须在目标电脑实测，不能仅凭文档宣称完成。

## 一句话产品定义

用户在 **Codex 对话**中提出想法、提供本地素材、选择或自定义剪辑风格 Skill；Codex 分析素材并按所选 Skill 使用 **CapCut × Codex** 编辑、预览、迭代，最后导出视频和可编辑工程。优秀剪辑方案经用户明确确认可沉淀为本地 Skill。

**不开发独立前端、桌面壳、Web 服务或第二个聊天界面。** 本地文件是持久状态，Codex 是唯一交互入口。

## 从这里开始

1. 阅读 [AGENTS.md](AGENTS.md)（开发代理的强制边界）。
2. 阅读 [产品规格](docs/PRODUCT_SPEC.md)、[开发审计](docs/DEVELOPMENT_AUDIT.md)、[架构](docs/ARCHITECTURE.md)、[用户路由](docs/INTERACTION_ROUTES.md)。
3. 阅读 [优秀开源 Skill 清单](docs/RESEARCHED_SKILLS.md)、[Skill 生命周期](docs/SKILL_GOVERNANCE.md)、[CapCut 适配验收](docs/CAPCUT_ADAPTER.md)。
4. 按 [Matt Pocock 工程流程](docs/ENGINEERING_WORKFLOW.md) 和 [任务图](docs/IMPLEMENTATION_TICKETS.md) 开发。
5. 按 [验收清单](docs/ACCEPTANCE.md) 实测；未通过不可以宣称完成。
6. [Codex Skill 入口草案](skills/auto-capcut/SKILL.md) 目前仅是**待实现合同**，不是已工作的自动剪辑工具。

## 开发环境管理

按照 [mattpocock/skills](https://github.com/mattpocock/skills) 当前官方 README，为 Codex 安装其工程技能：

```bash
codex plugin marketplace add mattpocock/skills
codex plugin add mattpocock-skills@mattpocock
```

只选一种安装方式，不要再用 `npx skills` 安装同一套重复技能。首次针对本仓库运行 `setup-matt-pocock-skills`，推荐 GitHub Issues 和 `docs/` 文档目录。若本机 Codex 的插件命令不可用，按该仓库最新官方说明调整并记录差异。

CapCut 官方入口：[CapCut × Codex](https://www.capcut.com/tools/capcut-x-codex)。只按官方安装与授权指引连接；先验证工具能力，再实现适配器。

## 不商用限定

本项目定位为**个人非商用使用**。保留第三方项目的原始链接、许可证与必要署名，不把外部仓库未经审查的脚本自动执行。开发包中的清单是调研参考，**不等于第三方代码已合并或可在 CapCut 内直接运行**。

## 完成标准

实现 `用户一句话 → 选择 Skill → 素材分析 → 剪辑 → 局部修改 → 成片QA → 导出视频与支持的工程格式 → 经同意沉淀 Skill` 的真实闭环。若目标环境无法导出国内剪映草稿，应明确提示不支持，记录兼容性实测，而不是用 JSON/MP4 冒充。

[开发入口 Prompt](docs/START_PROMPT.md)
