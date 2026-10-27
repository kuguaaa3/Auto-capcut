---
name: pet-healing
description: "具有可观察宠物行为与互动细节的温暖记录；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 萌宠治愈

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
具有可观察宠物行为与互动细节的温暖记录。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：需要虚构情绪或不存在动作才能成立的故事。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 优先选择实际可见的宠物动作特写与互动细节。
- 留白随行为完成而定，情绪逐步建立，保留环境声音。
- 让音乐给真实动作与现场声音让位，收尾用已出现的互动兑现情绪。

## 必要能力
material-analysis、pacing、audio。实际能力由官方工具探测决定。

## 质量门禁
- 共情来自真实镜头，音乐不喧宾夺主
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 无依据编造忠诚故事
- 所有镜头强制慢动作配钢琴

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- drama-edit: https://github.com/zenstory-ai/drama-skills/blob/main/skills/short-drama-edit/SKILL.md；blob a87f0dfebe813ae5af0beae67595eb6958bd62b1；MIT；许可见 ../../references/licenses/drama-edit.txt。
- storyline-style: https://github.com/FireRedTeam/FireRed-OpenStoryline/blob/main/.storyline/skills/create_profile_style_skill/SKILL.md；blob c098c0691a8e2f5780b4d724b63e8abc76a6925c；Apache-2.0；许可见 ../../references/licenses/storyline-style.txt。
