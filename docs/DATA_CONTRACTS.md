# 数据合同和文件一致性

这些是给开发人员的稳定**逻辑数据结构**；不代表 CapCut 官方 API。开发时可选 JSON Schema/Pydantic 等实现，重点是外部行为可验证。

## project.json
- `schema_version`: 版本。
- `project_id`, `name`, `created_at`, `updated_at`, `status`。
- `goal`: 用户原文与已确认派生目标。
- `style`: 主风格 id、来源、版本、confirmed_by_user、options。
- `preferred_formats`: 用户需要视频/CapCut/剪映草稿。
- `current_revision`, `last_verified_revision`。
- `execution_preference`: `direct`（默认）或 `plan-first`，用户可随时修改并持久保存。
- `confirmed_plan_revision`: 用户明确审定的当前计划版本或 null；改计划/素材/风格后失效。
- `editor`: backend=capcut_official（常规）/jianying_compat（显式可选）、capability_snapshot_id。
- `last_error`: code、human_message、recover_action（成功时为null）。

## assets.json
素材清单: `asset_id`, `kind`(video/audio/image), `path`, `exists`, `size`, `hash`, `duration_us`, `width`, `height`, `fps_num`, `fps_den`, `audio_tracks`, `content_evidence`。原素材只读且无用户允许不上传。
来源时间轴单位建议用**整数微秒**，面向导出可独立进行帧对齐。

## plan/vXXX.json
```json
{
  "schema_version": "1.0",
  "revision": 1,
  "style_id": "pet-healing",
  "target": {"aspect_ratio": "9:16", "duration_us": 20000000},
  "shots": [
    {
      "shot_id": "s01",
      "asset_id": "video-001",
      "source_in_us": 1000000,
      "source_out_us": 5000000,
      "target_in_us": 0,
      "target_out_us": 4000000,
      "decision": "用主人寻找袜子的真实镜头建立疑问",
      "evidence": "用户标注或素材分析结果的实际区段"
    }
  ],
  "captions": [{"text": "袜子去哪儿了？", "in_us": 400000, "out_us": 2600000}],
  "music": [{"asset_id": "music-001", "target_in_us": 0, "target_out_us": 20000000, "gain_db": -18}],
  "unresolved": []
}
```
该例仅描述示意片段，非已经读取过的真实狗狗素材。实际计划必须校验每个 asset 时长、片段前后不颠倒、目标时间线可解析、字幕落在目标视频范围内。
落盘时同时固定 `style_version`；执行边界必须与 project.style 的 ID/版本一致。
正式编辑前重查源文件和 SHA-256，不能仅信任 assets.json 中的旧 exists 标记。

## operations.jsonl
一行一个操作事件（操作ID、项目版本、外部工具名、工具调用参数的可公开部分、执行前计划/后状态、成功/失败、可恢复信息、时间）。
**幂等策略**：操作ID与目标版本稳定；重试前读回是否成功落地，不能盲目对同一工程再次插入镜头。

## capability.json
`backend`, `discovered_at`, `os`, `editor_version`, `plugin_version`, `tools`, `supports`（键→supported/unsupported/unknown/blocked）、`evidence`、`notes`。更新/断线后失效重探测。

## qa/vXXX.json
`checks`: id/status/pass-or-fail/evidencePath/details；`artifact_paths`；`verified_at`；`review_status`。所有显示“已完成”必须有相应 artifact 存在且通过与类型相符的验证。

## style.json
`id`, `name`, `source`(builtin/custom/learned/external-ref), `version`, `compatibility`, `inputs`, `quality_rules`, `origin`, `license`, `approved_at`。风格只储存抽象策略，不存用户的个人视频、一次性剧情、绝对路径、私人信息。

## 文件与运行不变量
1. 源文件、可编辑工程、成片、学习生成的Skill是不同对象，不同验证。
2. plan ≠ 已落地 timeline，timeline ≠ 已导出 MP4。
3. 修改在新版本落地；失败时原项目版本可以恢复。
4. 不允许生成一个虚拟文件路径当作操作成功。
5. 新用户Skill仅在明确确认后落盘；未经测试只标 draft/proposed。
