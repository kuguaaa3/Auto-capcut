# Auto-capcut 开发代理指令

## 目标与单一事实源
这是给 Codex 开发的 **原生 Skill 项目**，不是 GUI 应用。产品决策以 docs/PRODUCT_SPEC.md、docs/INTERACTION_ROUTES.md、docs/CAPCUT_ADAPTER.md 为准；本文件负责导航和不可突破的边界。完成前先阅读 docs/DEVELOPMENT_AUDIT.md、docs/ACCEPTANCE.md 和 GLOSSARY.md。

## 强制架构
- Codex 是唯一聊天和工作流入口；用户直接说想法并引用本地素材。
- 用户可以接受推荐、显式选择已有风格、自定义或从视频学习风格。**风格选择不允许被工具静默覆盖**。
- 主视频编辑后端是 **CapCut × Codex 官方能力**；必须先实际发现授权的工具和支持的操作，不可捏造工具名、输入字段或成功状态。
- 剪映 MCP、pyJianYingDraft、FFmpeg 是 C 方案参考与必要时的受控兼容适配，不可悄悄替换主后端。
- 不开发前端、Web 服务、桌面壳、数据库、额外登录、长期驻留服务。以项目目录内 JSON/Markdown/媒体与编辑工程保存状态。
- 存在用户素材时不允许仅生成剪辑建议就报告“剪好”；不得将 MP4 伪装为可编辑剪映草稿或将一份计划 JSON 伪装为 CapCut 工程。
- 外部项目是研究资料，引用须有来源与许可证记录，禁止在用户未批准时自动运行陌生远程脚本、上传本地素材或调用付费接口。
- 所有修改必须保留先前可用版本和源素材，不原地破坏用户文件，操作失败要可恢复、可重试。
- 不作出与已连通能力不符的功能宣称。对不支持的操作报告 blocked/unsupported，不得伪造完成。

## 开发工作方式
- **必须使用 https://github.com/mattpocock/skills 管理开发**。按 docs/ENGINEERING_WORKFLOW.md 安装、运行 setup、采用 to-spec/to-tickets/implement-spec、TDD 与 code-review。该工程技能只用于开发，不是视频剪辑风格库。
- 面向最终交付实施，不以几个 mock 测试或 README 截图代替真实 CapCut E2E。
- 高价值测试缝（seams）：公开的对话命令/路由、工程状态与产物、CapCut adapter 边界、Skill 加载与质量验收。
- 开发与测试文档中记录软件版本、平台、插件实际工具列表、成功/失败的操作及截图或产物证据。
- 每个 ticket 必须有纵向可演示结果，依赖及 DoD 见 docs/IMPLEMENTATION_TICKETS.md。
- 凡需要用户作决定，优先给一条简短建议以及明确选项。只有真正不可推断的关键事项才问，不做无止境澄清。
- 开发中遇到官方插件能力缺失：先报告与记录，开放能力适配方案，不得为了显得完成暗中引入全套第二剪辑引擎。

## 首次操作
1. 阅读 README + AGENTS + docs/ 规格，确认本仓库目前只是开发包。
2. 检查本机 Codex/CapCut 能力，记录兼容性矩阵，不能在无授权环境宣称“接入成功”。
3. 使用 Matt Pocock 工程 Skill 建立规格任务图与可测试接口；已有文档作为已确认需求，不要推翻重问。
4. 实现、测试、复核后再更新本文件与 README 的状态。

## Agent skills

### Issue tracker
GitHub Issues in kuguaaa3/Auto-capcut; see docs/agents/issue-tracker.md.

### Triage labels
Upstream default roles; see docs/agents/triage-labels.md.

### Domain docs
Single-context GLOSSARY.md and docs/adr/; see docs/agents/domain.md.
