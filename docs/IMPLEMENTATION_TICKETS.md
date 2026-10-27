# 开发任务图（供 mattpocock to-tickets/implement-spec 转 GitHub Issues）

**请按纵向可演示切片做，不按“先写全部数据层、再写全部UI层”拆分。** 下列 ID 为文档锚点，真正开发票号由 tracker 创建后回填。用户已批准整体产品方向，此文件是默认任务拆分建议。

| ID | 前置 | 纵向可演示交付 | DoD |
|---|---|---|---|
| T01 | 无 | 仓库初始化、Matt技能 setup、测试工具、CI与开发约定 | GitHub Issues配置，静态校验与测试能运行 |
| T02 | T01 | 授权后探测 CapCut 官方接口，并做最小导入/粗剪/读回实验 | 完整能力矩阵，真实操作证据，不支持项明示 |
| T03 | T01 | Codex 一句话打开/恢复项目，读取本地素材与状态 | 可连续会话恢复，非法路径/损坏文件清楚报错 |
| T04 | T03 | 用户可选/推荐/指定自定义风格 Skill 的路由 | 显式选择不覆盖，风格列表/冲突/错误均测试 |
| T05 | T03,T04 | 素材分析 + 基于真实媒体的剪辑计划（可 Dry Run） | 源片时间不越界、目标时间线连续、证据可查 |
| T06 | T02,T05 | CapCut 最小真实编辑闭环 | 一句话创建可编辑工程，真实裁切/排序且读回 |
| T07 | T06 | 对话局部修改并保留历史 | “缩短第三镜1秒”后工程相符，前版可恢复 |
| T08 | T06 | 字幕、音乐、音效和风格组合 | 能力支持范围内全量出片，不支持明确降级 |
| T09 | T06,T08 | QA + 实际视频/工程导出 | MP4存在可播+工程实际可重开，无虚假成功 |
| T10 | T09 | 国内剪映草稿导出可选兼容路径 | 目标版本打开/可改/保存的实测；失败有明确回退 |
| T11 | T04,T07,T09 | 从优秀成片/参考视频提取经确认的 Skill | 新Skill可发现、复用、回退；无硬编码绝对路径 |
| T12 | T07,T09,T11 | 多项目恢复、全链路故障、回归审查 | 断点恢复、测试矩阵、示例Demo、真实验收记录 |
| T13 | T12,T10 | 交付封装、安装、说明、代码审查与最终验收 | Codex新会话安装运行、真实端到端、文档更新 |

## T02 关键决策规则
尽早探测官方CapCut真实能力；若某项能力未开放，用 `unsupported` 记录且对该项设置明确验收阻碍，不得将 mock/FFmpeg/剪映MCP 替代为 CapCut 成功。

## ticket 交付字段模板
- Problem / User observable result / Given-When-Then acceptance
- Dependencies / test seam / environment & permissions
- Files changed / actual evidence / known limitations
- Status: blocked | ready | in-progress | implemented | verified

## 并行原则
T02与T03可并行，T04与T05在T03基础上推进，T11可在T09完成后开始。所有集成分支执行双轴 code-review（规范与规格）。禁止因为票数多把验收挤到最后才做。
