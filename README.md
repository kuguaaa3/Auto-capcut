# Auto-capcut

**Codex 原生 AI 剪辑 Skill | 开发中：本地工具已实现，官方真机验收未通过**

> 截至 2026-10-27，已实施本地项目状态、版本与恢复、十种风格治理、真实媒体检查、计划校验、QA 和原生工具衔接。官方 CapCut 0.2.6 已安装，账号授权等待回调超时；尚无用户批准的验收素材，未生成或验收真实 CapCut 工程/成片。整体产品尚未完成。

当前成果：[草稿 PR #12](https://github.com/kuguaaa3/Auto-capcut/pull/12)、[规格与任务](https://github.com/kuguaaa3/Auto-capcut/issues/1)、[验收状态](docs/ACCEPTANCE_STATUS.md)、[实际能力矩阵](docs/evidence/capability-matrix.md)。

用户已明确暂缓真实验收。本次继续交付本地实现、审查修复和安装验证；真机项目保留为未验证，不据此宣称自动剪辑闭环已经可用。

## 本地运行与安装

Python 3.11+，无第三方 Python 运行依赖。媒体检查需已有的原生 ffprobe 与完整视频版 FFmpeg；它们只用于检查/解码/抽帧，不作为替代剪辑引擎。可通过 PATH 或 `AUTO_CAPCUT_FFPROBE` / `AUTO_CAPCUT_FFMPEG` 指定。CI 为检查安装 FFmpeg。

```text
python skills/auto-capcut/scripts/auto_capcut.py --help
python skills/auto-capcut/scripts/auto_capcut.py styles --query 宠物
python skills/auto-capcut/scripts/auto_capcut.py doctor --check-connection
python scripts/install_skill.py
```

安装器将整个 Skill 复制到当前 Codex 数据目录的 `skills/auto-capcut`，保留已有安装且不覆盖；`--dest` 可选择空的验证目录。新会话或 Skill 重新发现后可使用 `$auto-capcut`。这不代替官方 CapCut 插件安装、账号授权和真实功能验收。

本地辅助检查：`python -m unittest discover -s tests -v`。配置原生媒体工具后，技术测试会实际创建临时媒体并执行探测/解码；这些技术样本不属于用户素材，也不满足 B/C 类真实剪辑验收。详细公共接口在 Skill 自带的 references/ 中。

## 一句话产品定义

用户在 **Codex 对话**中提出想法、提供本地素材、选择或自定义剪辑风格 Skill；Codex 分析素材并按所选 Skill 使用 **CapCut × Codex** 编辑、预览、迭代，最后导出视频和可编辑工程。优秀剪辑方案经用户明确确认可沉淀为本地 Skill。

**不开发独立前端、桌面壳、Web 服务或第二个聊天界面。** 本地文件是持久状态，Codex 是唯一交互入口。

## 从这里开始

1. 阅读 [AGENTS.md](AGENTS.md)（开发代理的强制边界）。
2. 阅读 [产品规格](docs/PRODUCT_SPEC.md)、[开发审计](docs/DEVELOPMENT_AUDIT.md)、[架构](docs/ARCHITECTURE.md)、[用户路由](docs/INTERACTION_ROUTES.md)。
3. 阅读 [优秀开源 Skill 清单](docs/RESEARCHED_SKILLS.md)、[Skill 生命周期](docs/SKILL_GOVERNANCE.md)、[CapCut 适配验收](docs/CAPCUT_ADAPTER.md)。
4. 按 [Matt Pocock 工程流程](docs/ENGINEERING_WORKFLOW.md) 和 [任务图](docs/IMPLEMENTATION_TICKETS.md) 开发。
5. 按 [验收清单](docs/ACCEPTANCE.md) 实测；未通过不可以宣称完成。
6. [Codex Skill 入口](skills/auto-capcut/SKILL.md) 及随包脚本是已实施的本地编排辅助；官方编辑路径仍受真实能力矩阵约束。

## 原始 Skill 研究资料

- [10套原文只读 Skill 快照与许可证](research/upstream/README.md)
- [10类主风格规范](docs/STYLE_PRESETS.md)
- [数据合同](docs/DATA_CONTRACTS.md)、[演示场景](docs/DEMO_SCENARIOS.md)
- [交接包审计签收](docs/AUDIT_SIGNOFF.md)、[环境待验证项目](docs/OPEN_ENVIRONMENT_QUESTIONS.md)

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
