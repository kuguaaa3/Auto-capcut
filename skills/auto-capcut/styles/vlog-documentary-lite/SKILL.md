---
name: vlog-documentary-lite
description: "旅行、日常与真实场景记录；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 生活轻纪录

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
旅行、日常与真实场景记录。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：必须重编事实顺序才成立的叙事。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 用实拍时间与空间线索串联场景，必要时用环境镜头交代位置。
- 保留有辨识度的现场声音，音乐只辅助情绪。
- B-roll 补充当前场景事实，不以无关镜头假装现场。

## 必要能力
material-analysis、narrative、audio、qa。实际能力由官方工具探测决定。

## 质量门禁
- 时空连贯自然，环境声音可感知
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 转场破坏真实时间流
- 无关素材冒充现场记录

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- storyline-style: https://github.com/FireRedTeam/FireRed-OpenStoryline/blob/main/.storyline/skills/create_profile_style_skill/SKILL.md；blob c098c0691a8e2f5780b4d724b63e8abc76a6925c；Apache-2.0；许可见 ../../references/licenses/storyline-style.txt。
- clip-skills: https://github.com/appergb/ClipSkills/blob/main/clip-skills/SKILL.md；blob 329c50d23783bbb5b4aa39dc7d2ec855cc00738c；MIT；许可见 ../../references/licenses/clip-skills.txt。
