---
name: explainer-documentary
description: "有可核对事实、旁白和资料出处的解说；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 解说纪录

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
有可核对事实、旁白和资料出处的解说。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：无来源的引述或无法核对事实的素材。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 先建立事实与资料来源，再按信息层次安排论证。
- 证据镜头与旁白逐段对应，无法证明的内容标缺而不补造。
- 字幕、文字与声音同步，复杂信息保留足够理解时间。

## 必要能力
material-analysis、speech、narrative、captions、qa。实际能力由官方工具探测决定。

## 质量门禁
- 事实准确、出处清楚、信息层次可理解
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 编造引述和来源
- 无关素材被当作事实证据

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- talkcraft: https://github.com/Vincentwei1021/video-talkcraft/blob/main/SKILL.md；blob 70170e660731f78c3af34c34c8432ed734cc4ea6；PolyForm-Noncommercial-1.0.0；许可见 ../../references/licenses/talkcraft.txt。
- cut-as-code: https://github.com/WhiteTowerAI/cut-as-code/blob/main/skills/cut-as-code/SKILL.md；blob bea91c5df055546b0a02d6038296bb327cc054b4；MIT；许可见 ../../references/licenses/cut-as-code.txt。
