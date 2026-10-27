# 实施架构（Codex 原生 Skill）

## 1. 边界
用户 ←→ Codex（自动唤起 auto-capcut Skill）←→ 决策路由与本地文件 ←→ CapCut 官方工具（唯一首选执行后端）←→ 编辑工程/视频输出。
Skill 研究/解读是 Codex 本地任务，按需联网；外部项目的脚本默认不执行。
C方案（剪映MCP/pyJianYingDraft）仅作为独立、可关闭、明确标记的兼容参考；不得自动接管 B。

## 2. 职责分层
1. **入口 Router**：用户意图解析、选择项目、选择风格/模式、生成最少交互。
2. **Skill Registry**：内置、用户、学习 Skill 的元信息、版本、冲突、出处及可信程度。
3. **Research/Style Analyzer**：在线发现开源规范；参考视频分镜、节奏、声音、构图分析；记录事实与假设。
4. **Media Inspector**：本地 ffprobe 或等价工具，时长/帧率/分辨率/音轨/路径完整性；有能力时分析镜头和语音内容。
5. **Edit Planner**：原始素材时间码映射到目标时间线，明确每个剪辑决定的依据与退化方案。
6. **Editor Adapter**：实际探测 CapCut 插件和工具能力，通过唯一受控接口运行编辑操作。不得写死尚未验证的官方工具参数。
7. **QA**：计划静态验证 + 导出媒体检测 + 编辑工程实际重开/二次修改验证。
8. **Artifact & Version Store**：本地项目状态/操作日志/草稿指针/视频/审查结果/Skill 版本。

## 3. 数据目录（默认项目根可配置）
```text
auto-capcut-workspace/
  materials/                    # 原素材；只读引用，不修改
  projects/<project-id>/
    project.json                # 目标、选定风格、版本与状态
    assets.json                 # 本地绝对/相对路径 + 媒体信息 + hash
    capability.json             # 当前环境实际工具与版本
    plan/v001.json              # 可追溯剪辑计划
    history/operations.jsonl    # 幂等操作、参数、结果和错误
    qa/v001.json                # QA结果+证据
    exports/                   # mp4/音视频/实际可编辑工程(如可用)
    snapshots/                 # 工程恢复点或可恢复定位信息
  custom-skills/<name>/SKILL.md
  learned-skills/<name>/SKILL.md
  research/                   # 来源、版本、调研结果、拒绝原因
```
目录不应强迫用户复制全部素材；采用引用或可选受控复制。禁止把个人本地素材提交到 GitHub。

## 4. 项目状态机
NEW → INPUT_READY → STYLE_SELECTED → PLANNED → EDITING → DRAFT_READY → REVIEWED → EXPORTED。
操作失败：BLOCKED（有原因与可恢复指令）；用户中断：PAUSED；恢复后走上一次有效状态，**不要重放成功且非幂等的外部写操作**。学习 Skill 是另一个侧支：REVIEWED → STYLE_PROPOSED → USER_APPROVED → SAVED。

状态必须带版本、更新时间、原子更新策略、上一次已确认操作。暂存文件 + 原子替换避免中断写坏状态。

## 5. 项目和输出的事实源
- project.json 是项目目标与路由选择的事实源；不是云端聊天消息。
- plan 是“想做什么”；外部工具返回及可回读的工程才是“做了什么”；qa + 实际视频才是“交付完成”。
- 每次局部修改以已有工程真实状态为基准，映射到新版本；不允许仅更新 JSON 就报告效果已修改。
- 如插件无时间线读取 API，则必须用可用的工程导出/GUI读回/人类打开确认方法记录证据；纯推测不判成功。
- 不能仅由源文件名推断内容，素材理解必须有真正图像/语音证据或用户明确指示。

## 6. 性能与可扩展性
- Skill 渐进式加载：入口 SKILL.md 只负责路由，引用文档按需读取。
- 不为每条视频联网搜索；本地合格风格优先，用户明确要求研究或没有合适风格才联网。
- 每个视频任务独立状态和版本，可处理多任务而不共享可变全局状态。
- 各能力以“明确输入/输出/失败模式”组织，避免万能脚本和庞大永久提示词。

## 7. 设计验证
先实现仅模拟能力可运行的 Dry Run 作为审计工具；但真正上线必须有带可编辑工程与成片的真机 E2E。模拟输出必须标记为 simulation，永不混同实际出片。
