---
name: short-form-hook
description: "目标与真实兑现点清楚的短视频；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 短视频钩子

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
目标与真实兑现点清楚的短视频。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：仅能用无证据夸张承诺吸引注意的素材。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 开头用可见价值或真实疑问建立关注，后文必须兑现。
- 根据信息密度与情绪变化安排长短镜头，避免节拍器式跳切。
- 字幕与主体保持安全距离，在实际画幅下检查开头与结尾。

## 必要能力
material-analysis、pacing、captions、reframe、qa。实际能力由官方工具探测决定。

## 质量门禁
- 开头主题清楚且后续有真实兑现
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 标题承诺在素材中没有兑现
- 过度跳切导致无法理解

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- vertical-video: https://github.com/nopefallacy/vertical-video-editing-skills/blob/main/skills/video-editing/SKILL.md；blob 667dc663a427e546e8d6e6752e84997bb2822efb；MIT；许可见 ../../references/licenses/vertical-video.txt。
- herk-short: https://github.com/nateherkai/herk-edit-kit/blob/main/.agents/skills/short-form-edit/SKILL.md；blob 412e58e3fd8939fe261b568024b0b6572f718463；MIT；许可见 ../../references/licenses/herk-short.txt。
