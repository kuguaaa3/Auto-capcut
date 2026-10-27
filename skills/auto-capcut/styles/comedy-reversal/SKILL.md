---
name: comedy-reversal
description: "有真实动作因果的喜剧、默剧与反应镜头；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 搞笑反转

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
有真实动作因果的喜剧、默剧与反应镜头。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：缺少铺垫或反转证据的素材。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 先用素材中可见的原因建立预期，再展示动作与反应。
- 根据表演停顿决定笑点切点，反转揭示之前不抢先曝光结果。
- 结尾如转温柔，保留能支撑情绪变化的真实互动。

## 必要能力
material-analysis、narrative、pacing、audio。实际能力由官方工具探测决定。

## 质量门禁
- 反转有依据且观众能理解前因后果
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 乱序导致笑点提前曝光
- 每秒插入特效掩盖动作

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- drama-edit: https://github.com/zenstory-ai/drama-skills/blob/main/skills/short-drama-edit/SKILL.md；blob a87f0dfebe813ae5af0beae67595eb6958bd62b1；MIT；许可见 ../../references/licenses/drama-edit.txt。
- herk-short: https://github.com/nateherkai/herk-edit-kit/blob/main/.agents/skills/short-form-edit/SKILL.md；blob 412e58e3fd8939fe261b568024b0b6572f718463；MIT；许可见 ../../references/licenses/herk-short.txt。
