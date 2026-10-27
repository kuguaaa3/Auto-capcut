---
name: product-ad
description: "有可验证卖点、产品画面与许可资料的展示；按用户选定风格和真实素材证据剪辑。"
metadata:
  version: 1.0.0
---

# 产品展示

状态：本地规则已适配，CapCut 真机效果尚未验证。只由 auto-capcut 路由按需读取。

## 适用与输入
有可验证卖点、产品画面与许可资料的展示。输入：可读取且允许使用的素材、实际内容证据或用户明确标注、目标时长与画幅。

不适用：必须捏造功能或功效才能成立的广告。

## 默认行为
用户显式要求优先；按素材证据调整节奏，不机械套用固定镜头秒数。

## 决策规则
- 按用户确认的卖点顺序组织画面，每项声明绑定资料或实拍证据。
- 保持产品主体可辨认，镜头运动服务于展示细节。
- 文字与 CTA 在目标画幅下可读，并给产品和主体留出空间。

## 必要能力
material-analysis、narrative、visuals、captions、qa。实际能力由官方工具探测决定。

## 质量门禁
- 卖点有证据，产品清晰，CTA 可读
- 计划边界正确；导出媒体与可编辑工程分别验收。

## 错误样本
- 展示素材未证明的功能
- 文字完全遮挡产品

## 失败退化
素材证据不足则标缺；官方能力未验证则 blocked，不切换编辑引擎。

## 来源与版本
本项目 1.0.0，个人非商用。选择性改写可迁移的剪辑决策；不采用上游渲染器、安装或联网指令。
- product-shot: https://github.com/Vincentwei1021/video-shotcraft/blob/main/SKILL.md；blob 695faad1d7441597a89dea4bd1b44b835005af7c；Apache-2.0；许可见 ../../references/licenses/product-shot.txt。
- clip-skills: https://github.com/appergb/ClipSkills/blob/main/clip-skills/SKILL.md；blob 329c50d23783bbb5b4aa39dc7d2ec855cc00738c；MIT；许可见 ../../references/licenses/clip-skills.txt。
