# Local command contracts

All commands are one-shot Python 3.11 standard-library tools. Resolve `scripts/`
relative to this installed Skill, and choose a persistent local workspace outside
the source repository. No daemon, network editor or database is started.

| Command | Input and effect |
|---|---|
| doctor [--check-connection] | Read installed native plugin inventory; optional vendor read-only connection helper. Never logs in or reads credentials. |
| route TEXT | Nonexecuting intent hint, preserves the original text for Codex interpretation. |
| styles [--query TEXT] [--id ID --version SEMVER] | Discover builtin/custom/learned rules; an invalid explicit selection is an error. |
| create --name NAME --goal GOAL [--format FORMAT] | New independent local project; default mp4 and capcut delivery preferences. |
| projects / show ID / context ID | Read persistent state; context includes source inventory, saved plan, capability and operation history. |
| assets ID PATH... --expected-revision N [--ffprobe PATH --annotations JSON] | Probe media, hash sources, save immutable inventory. Folders expand supported local media. Optional actual evidence is keyed by matching source path. |
| frame FILE --at-us N --output PNG [--ffprobe PATH --ffmpeg PATH] | Extract a source frame for actual visual inspection. Extraction alone leaves content_reviewed=false. |
| select ID --id STYLE [--version SEMVER] --expected-revision N | Lock an explicitly user-selected style version. |
| plan ID --file PLAN --expected-revision N | Validate and save a local plan; never edits a video. |
| revise ID --file PATCH --expected-revision N | Save a changed local plan revision; never substitutes for actual editing. |
| pause ID / resume ID --expected-revision N | Change local routing state; no claim of remote cancellation. |
| set-mode ID direct/plan-first --expected-revision N | Persist the user's execution preference across sessions. |
| confirm-plan ID --expected-revision N | After explicit approval, confirm only the currently saved plan revision. Any new plan clears approval. |
| capabilities ID --file SNAPSHOT --expected-revision N | Save actual current native discovery. Names and inputSchema come from the host, never from guesses. |
| operation ID --file REQUEST --expected-revision N | Validate a native-tool handoff and journal it before execution. Only action=execute permits the actual call. |
| settle ID --id OP --status succeeded/failed/unknown --file RECEIPT | Persist a real native response. Succeeded is operation-level, never whole-project completion. |
| qa FILE [--expected JSON] [--ffprobe PATH --ffmpeg PATH] | Inspect a real exported media file; semantic and editable-project checks remain separate. |
| learn --file PROPOSAL --approved | Save explicitly approved portable style rules, versioned and initially draft. |
| rollback-style ID VERSION --approved | Select a preserved style version; existing projects keep their own locked version. |

Use actual `--help` for argument order. `--workspace` is a global option before
the command. JSON is UTF-8, including Chinese paths. Nonzero exit and structured
blocked error mean the operation did not complete. ffprobe/ffmpeg can also be
resolved through AUTO_CAPCUT_FFPROBE/AUTO_CAPCUT_FFMPEG or PATH.

## Native handoff request

The local operation name is a workflow key, not an official API name. Its binding
must refer to an actual current native tool whose inputSchema has been discovered.

```json
{
  "operation": "apply_plan",
  "operation_id": "stable-project-revision-operation-id",
  "arguments": {},
  "requires_upload": false,
  "upload_approved": false
}
```

`arguments` must be filled from the actual host tool schema; this empty object is
not an invocation example. Preserve a successful tool response before advancing.
For uncertain responses use unknown and read the official server before retrying.

## Plan and media evidence

Plans carry schema_version, revision, style_id, target aspect_ratio/duration_us,
shots with unique IDs, source/target integer-microsecond intervals, captions,
music and unresolved decisions. Shot decision/evidence and source content_evidence
must describe actual inspected content or explicit user annotations. Capture that
evidence while inspecting; never populate it from a guessed filename narrative.
The CLI pins style_version when saving. Switching the selected style/version
clears the current plan pointer while preserving history. Editor-write preflight
requires the same style ID/version, actual unchanged source hashes, and current
plan confirmation when execution_preference is plan-first. Resume also rechecks
local sources. Missing/changed files require reinspection, not cached success.

The Python public modules provide inspect_media/inspect_assets, validate_plan,
revise_plan, verify_media, ProjectStore and StyleRegistry. The JSON CLI is the
primary executable seam; Codex may use the public Python API for evidence-aware
asset inspection and style proposal/import rather than generating helper code.

Edits requiring semantic decisions or overlapping captions can return E_PLAN_REVIEW
instead of automatically altering meaning. Shortening a shot uses unique shot_id
or one-based shot_index with shorten_us. Music gain uses kind=music_gain,
one-based music_index and gain_db. Actual clip editing still follows official tools.
