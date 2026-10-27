# 已随开发包保存的上游 Skill 原文参考

为让 Codex 开发时能够直接阅读实际的开源剪辑规则，本目录保存了 **10 个来源明确的原文只读参考快照**。每份 `UPSTREAM_SKILL_REFERENCE.md` 均保留了源地址、抓取日期、上游 blob SHA；相邻 `LICENSE` 是对应项目原始许可证。

这些文件刻意不命名为 `SKILL.md`，且不放在自动发现的 `.agents/skills` 中：**它们是研究证据，不应未经适配就作为正式运行技能加载**。

| 文件夹 | 上游仓库 | 主要用处 |
|---|---|---|
| clip-skills | appergb/ClipSkills | 软件无关剪辑知识与主路由 |
| storyline-style | FireRedTeam/FireRed-OpenStoryline | 从剪辑风格生成用户Skill |
| herk-short | nateherkai/herk-edit-kit | 专业短视频剪辑方法 |
| cut-as-code | WhiteTowerAI/cut-as-code | 工程化剪辑、时间线与QA |
| drama-edit | zenstory-ai/drama-skills | 剧情短剧剪辑 |
| vertical-video | nopefallacy/vertical-video-editing-skills | 竖屏短视频制作 |
| reverse-engineer | kevinbadi/open-edits | 参考片拆解和风格学习 |
| product-shot | Vincentwei1021/video-shotcraft | 广告/产品镜头 |
| music-director | guigulaoshi/music-video-director-skill | 音乐卡点与MV编排 |
| talkcraft | Vincentwei1021/video-talkcraft | 口播字幕、动效和逐字同步 |

完整按视频风格和能力类别的研究结果见 [RESEARCHED_SKILLS.md](../../docs/RESEARCHED_SKILLS.md)。上游文档可能描述原作者独立渲染引擎或远程脚本，**不要将其误认为本项目已接入的CapCut工具**。

### 推荐研发使用顺序
先读对应的上游参考 → 提炼可迁移判断规则 → 编写本项目 style/capability Skill → 用明确合同连接实际CapCut adapter → 真机验收。禁止原封不动复制“必须安装其他编辑软件”的指令到运行时。

### 法律范围
用户明确声明**个人非商用**，所以不以商用许可兼容为选型门槛。保留原许可证、版权声明及必要来源信息，不承诺任何源项目的模型/字体/音频资产已经获得授权。
