---
name: narrative-drama
description: "有完整人物或物体动作链的剧情片段；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 剧情叙事

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
有完整人物或物体动作链的剧情片段。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：缺少关键情节而要求无缝完整故事。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 先确认每镜的叙事动因，再按动作与视线建立镜头关系。
- 相邻镜头核对人物位置、道具状态与运动方向。
- 台词切点保留完整字音和必要停顿；缺失情节明确标缺。

## 必要能力
material-analysis、narrative、captions、qa。实际能力由官方工具探测决定。

## 质量门禁
- 核心情节完整，动作和空间连续
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 切镜破坏人物位置关系
- 所有镜头机械等长

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- drama-edit: https://github.com/zenstory-ai/drama-skills/blob/main/skills/short-drama-edit/SKILL.md；blob a87f0dfebe813ae5af0beae67595eb6958bd62b1；MIT；许可见 ../../references/licenses/drama-edit.txt。
- clip-skills: https://github.com/appergb/ClipSkills/blob/main/clip-skills/SKILL.md；blob 329c50d23783bbb5b4aa39dc7d2ec855cc00738c；MIT；许可见 ../../references/licenses/clip-skills.txt。
