# 优质剪辑 Skill 调研清单（2026-10-27）

**定位：这是研究与引入清单，不是“已经能在CapCut上跑”的安装列表。** 用户端只选择一个主风格 Skill；能力 Skill 由主路由按需加载。来源经过公开仓库与主要 README/SKILL.md 核验，效果、测试覆盖和 CapCut 兼容仍需在本工程逐项验证。具体引入须遵循 SKILL_GOVERNANCE.md。

## A. 核心知识/编排底座
| 优先 | 项目 | 原仓库 | 调研亮点 | 引入决策 |
|---|---|---|---|---|
| P0 | ClipSkills | https://github.com/appergb/ClipSkills | 12类软件无关剪辑知识，决策和软件操作分离；有CapCut适配指南；`clip-skills/SKILL.md` | **核心知识层**：选取规则，按需加载 |
| P0 | FireRed-OpenStoryline | https://github.com/FireRedTeam/FireRed-OpenStoryline | 自然语言视频编排、用户二次编辑、风格保存；`.storyline/skills/create_profile_style_skill/SKILL.md` | **路由+风格沉淀参考** |
| P0 | herk-edit-kit | https://github.com/nateherkai/herk-edit-kit | 故事节奏、短视频、字幕、音效、复核；编辑playbook | **专业工艺参考** |
| P0 | cut-as-code | https://github.com/WhiteTowerAI/cut-as-code | 素材理解、粗剪、字幕、色彩、工程版本和质量检查 | **专项能力与验收参考**，不采用其主编辑引擎 |
| P0 | drama-skills | https://github.com/zenstory-ai/drama-skills | 11个创作 Skill，角色/分镜连续性、剪辑单、成片QA | **剧情类工作流** |
| P1 | vertical-video-editing-skills | https://github.com/nopefallacy/vertical-video-editing-skills | 9:16开头、非机械节奏、字幕、音效、成片门禁 | **竖屏专项规则** |
| P1 | open-edits | https://github.com/kevinbadi/open-edits | `skills/reverse-engineer/SKILL.md` 从参考视频拆解并提炼风格 Skill | **参考片学习与风格生成** |

## B. 最终用户可选的 10 类主风格
**每一类是本项目待开发的风格接口，不等于开源项目已提供完全同名风格包。**
| 风格ID | 面向视频 | 最佳研究来源 | 具体可迁移剪辑决策 |
|---|---|---|---|
| `comedy-reversal` | 搞笑反转/无对白默剧 | drama-skills + herk-edit-kit | 预期建立→动作铺垫→停顿→意料之外却可理解的反转；动作连续与反应镜头 |
| `pet-healing` | 萌宠温暖/治愈 | drama-skills + OpenStoryline | 细节特写→情绪堆叠→温暖揭示，给表演留空间，勿强制高速切 |
| `narrative-drama` | AI剧情短片/短剧 | drama-skills + ClipSkills | 主线清晰、空间方位、对话反应、镜头动因与道具连续性 |
| `short-form-hook` | 抖音等快节奏短视频 | vertical-video-editing-skills + herk-edit-kit | 真实钩子、信息密度变化、注意力回收、字幕版式 |
| `vlog-documentary-lite` | Vlog/旅行/生活记录 | OpenStoryline + ClipSkills | 场景选择、环境声、时空线索、自然转场 |
| `talking-head` | 口播/知识解释 | cut-as-code + video-talkcraft | 口播保真、音频优先、逐字字幕、相关B-roll |
| `beat-montage` | 卡点/高燃MV | music-video-director-skill + ClipSkills | 节拍段落、高潮结构、音画对应、非机械切换 |
| `product-ad` | 产品展示/广告 | video-shotcraft + ClipSkills | 卖点先后、主体保持、镜头配方、产品和文字叠加 |
| `cinematic-brand` | 电影感/品牌宣传 | ClipSkills + video-shotcraft | 视觉连贯、景别节奏、声音层次、色彩统一 |
| `explainer-documentary` | 解说/纪录片 | video-talkcraft + cut-as-code | 内容准确、证据镜头、文字与声音同步、长叙事节奏 |

## C. 系统内部 14 类专项能力
| 能力 | 参考项目 | 应产出什么 |
|---|---|---|
| 意图与路由 | ClipSkills/OpenStoryline | 任务类型、风格候选、所需能力 |
| 素材识别与打标 | cut-as-code/OpenStoryline | 素材卡、可用范围、可信证据 |
| 镜头筛选 | herk-edit-kit/cut-as-code | 拍摄内容与选用理由、弃用理由 |
| 剧情编排 | drama-skills/herk-edit-kit | 叙事线、动作连续性、情绪节点 |
| 自动粗剪 | cut-as-code/ClipSkills | 可校验source in/out + target ranges |
| 剪辑节奏 | ClipSkills/vertical-video-editing | 镜头长短、停顿、速度变化 |
| 字幕与花字 | cut-as-code/video-talkcraft | 时间码、可读性和风格 |
| 音乐与音效 | music-video-director/herk-edit-kit | beat/grid、BGM节点、音量变化 |
| 调色与镜头匹配 | ClipSkills/cut-as-code | 同场景色调/曝光一致性 |
| 视觉包装 | video-shotcraft/video-talkcraft | 标题、叠加、动画素材 |
| 画幅重构 | vertical-video-editing/cut-as-code | 主体安全区、竖屏镜头 |
| 参考片拆解 | open-edits/reverse-engineer | 统计+语义规律，不复制原成片 |
| QA | cut-as-code/drama-skills | 黑帧/错位/内容连续性/导出检查 |
| 风格沉淀 | OpenStoryline/create_profile_style_skill + open-edits | 可迁移规则与限制、新Skill版本 |

## D. 其他需要关注的项目
- https://github.com/Vincentwei1021/video-talkcraft （PolyForm Noncommercial；个人非商用可研究/使用，遵从原许可）
- https://github.com/Vincentwei1021/video-shotcraft （Apache 2.0；有剪映草稿生成相关思路，独立引擎非官方）
- https://github.com/guigulaoshi/music-video-director-skill （MIT；音乐分析/EDL与卡点）
- https://github.com/prathameshp107/video-editing （Vlog/素材处理；入库前逐项核对具体文件）
- https://github.com/BusyBee3333/viral-video-edit-skills （音乐卡点/音频驱动视觉；适合备选）
- https://github.com/hyt315/notebook-video （科普/解说；适合备选）
- https://github.com/Alisa0808/vox-director （解说叙事；适合备选）
- https://github.com/Mal-Suen/JianYing-AutoEdit-MCP （C方案工程/分镜JSON，GPLv3，非CapCut插件）
- https://github.com/GuanYixuan/pyJianYingDraft （C方案草稿结构，Apache 2.0）

## E. 许可证/来源标记（核实入口，源许可随上游更新）
MIT：ClipSkills、herk-edit-kit、cut-as-code、drama-skills、vertical-video-editing-skills、open-edits、music-video-director-skill。
Apache 2.0：FireRed-OpenStoryline、video-shotcraft、pyJianYingDraft。
PolyForm Noncommercial：video-talkcraft。
GPLv3：JianYing-AutoEdit-MCP。
任何集成均保留原始来源及许可；用户已明确**非商用**，这里不作商用许可选型阻碍。其余备选在拉取任何代码前再核对来源和许可。

## F. 评价方法
按每项 0-5 分给出：领域契合20%、可复用决策质量25%、有可核验资料20%、独立于渲染器15%、输出可测10%、维护与依赖风险10%。先人工/只读分析再引入，若涉及代码执行须额外用户授权。不同视频风格不要硬套统一“每秒一刀”。
