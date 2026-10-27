---
name: talking-head
description: "含清晰讲话与可核对语义的口播；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 口播精剪

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
含清晰讲话与可核对语义的口播。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：无法核对原意或音频缺失的素材。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 先核对语音或用户提供的原稿，保留否定词、限定词与完整论证。
- 按句界与气口精简卡顿，不删除改变原意的停顿或语句。
- 字幕按真实发声同步，相关证据画面只在支撑语义时加入。

## 必要能力
material-analysis、speech、captions、audio、qa。实际能力由官方工具探测决定。

## 质量门禁
- 原意未变、字音完整、字幕可读同步
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 删除否定词改变原意
- 无关 B-roll 打断解释

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- cut-as-code: https://github.com/WhiteTowerAI/cut-as-code/blob/main/skills/cut-as-code/SKILL.md；blob bea91c5df055546b0a02d6038296bb327cc054b4；MIT；许可见 ../../references/licenses/cut-as-code.txt。
- talkcraft: https://github.com/Vincentwei1021/video-talkcraft/blob/main/SKILL.md；blob 70170e660731f78c3af34c34c8432ed734cc4ea6；PolyForm-Noncommercial-1.0.0；许可见 ../../references/licenses/talkcraft.txt。
