---
name: beat-montage
description: "已有获准音乐与可匹配动作的混剪；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 音乐卡点

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
已有获准音乐与可匹配动作的混剪。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：无可确认节拍或音乐未获许可的素材。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 先标注音乐段落、重拍与情绪变化，再安排镜头能量曲线。
- 用可见动作的起落呼应音乐节点，保留弱拍与呼吸。
- 高潮前建立层次，不在每一拍强制硬切。

## 必要能力
material-analysis、beats、pacing、audio、qa。实际能力由官方工具探测决定。

## 质量门禁
- 音画同步，有重弱层次和段落变化
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 每拍硬切导致单调
- 高潮之前没有能量铺垫

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- music-director: https://github.com/guigulaoshi/music-video-director-skill/blob/main/skill.md；blob ca2ece314d0c3ef808f3f37a7cb644c25dad73bc；MIT；许可见 ../../references/licenses/music-director.txt。
- clip-skills: https://github.com/appergb/ClipSkills/blob/main/clip-skills/SKILL.md；blob 329c50d23783bbb5b4aa39dc7d2ec855cc00738c；MIT；许可见 ../../references/licenses/clip-skills.txt。
