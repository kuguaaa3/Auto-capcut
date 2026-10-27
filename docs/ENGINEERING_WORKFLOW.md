# 使用 mattpocock/skills 管理整个开发

核心仓库：https://github.com/mattpocock/skills
该仓库是**开发工程管理方法**，不负责视频剪辑，不应被混入风格技能列表。

## 1. Codex 安装（上游 README 2026-10-27 版本）
```bash
codex plugin marketplace add mattpocock/skills
codex plugin add mattpocock-skills@mattpocock
```
Codex 不支持插件命令的环境可按照上游 README 的 `npx skills@latest add mattpocock/skills` 提示选择 Codex，但**只能选一种安装方式**，避免同一个 Skill 重复注册。插件与 npx 二者安装目录不同，请以实际 Codex 版本为准。

## 2. 初始化
在本仓库打开 Codex，运行 `setup-matt-pocock-skills`（在 Codex 中使用当前支持的 Skill 调用语法，例如 `$setup-matt-pocock-skills`）。
建议：issue tracker = GitHub Issues；文档 = `docs/`；术语文件 = `GLOSSARY.md`；若仓库已有配置不要重复覆盖。
该 setup 按其定义可能请求确认一次 tracker/labels/document layout，属于**开发管理**，不是产品交互；业务需求已经确定，不要重新摸底。

## 3. 用现有定稿资料实施
- 先读当前仓库的 PRD、审计、架构、交互、参考库。
- 使用 `to-spec` 将定稿规格映射到 issue tracker，不重新反复询问用户已经确认的产品方向。
- 使用 `to-tickets` 将 docs/IMPLEMENTATION_TICKETS.md 的纵向任务图发布到 tracker，并保留依赖关系。若技能规定审批任务拆分，给出已有建议与默认路径，减少反复。
- 使用 `implement-spec` 在集成分支实施整份规格，或根据实际权限用 `implement` 按票实施；每张票以 `tdd` 的外部行为为先。
- 使用 `code-review` 对比 main，做**标准审查和规格审查**；修复后运行端到端验收。
- 使用 `retro` 回顾规则改进。

参照上游：
- https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/implement-spec/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md

## 4. 开发流程约束
- 使用同一集成分支串联相互依赖的票，避免局部“绿了”却未真正接通。
- TDD 的首选测试缝：用户可观察的路由结果、持久项目状态、adapter 公开接口、Skill 复用和输出校验。
- 测试条件能模拟的都自动化，但“可编辑工程已可用”和“MP4真的剪出来”必须用真实应用验收。
- 允许少量技术原型研究 CapCut 工具参数，原型不能替代产品主路径。
- GitHub issue/PR、代码审查、功能演示及能力矩阵都是验收证据，不能靠开发日志口头宣布。
- 完成后更新 README 成熟度/兼容矩阵，明确哪些版本/系统实测通过。
