# Local media, plan and QA evidence

Date: 2026-10-27 (Asia/Shanghai). Scope: local contracts only.
Matt Pocock `tdd` applied at the pre-agreed media/plan/artifact public seams.
Each added behavior was first observed failing, then made green. No private media
was uploaded and no CapCut edit, export or editor reopening is claimed here.

## Implemented public interfaces

- `inspect_media(path, ffprobe=None, *, content_evidence=None)` reads local streams,
  source duration, video/display metadata, audio count and SHA-256 without editing
  the source. It never infers story content from filenames. Primary video duration
  and overall container duration are separate, preventing a longer audio track
  from extending the source shot boundary. Still images have no media duration.
- `inspect_assets(paths, ffprobe=None)` accepts files/folders, deduplicates paths,
  skips directory symlinks and reports empty input or actual probe errors.
- `extract_frame(path, at_us, output_path, *, ffprobe=None, ffmpeg=None)` produces
  an actual PNG for Codex visual inspection, with integer bounds and atomic
  non-overwrite publication. Its returned evidence has `content_reviewed=false`;
  successful extraction does not mean the frame has been understood.
- `frames_to_us` and `us_to_frame` use exact fractional arithmetic and floor the
  absolute position once. They do not accumulate rounded per-frame durations.
- `validate_plan(plan, assets, *, require_evidence=True)` returns
  `{valid, ready_to_edit, duration_us, warnings, scope}`. Invalid contracts raise
  `AutoCapcutError`. Missing content evidence or unresolved decisions leave a
  structurally valid plan **not ready to edit**, even in a local dry run.
- `revise_plan(plan, patch)` makes a deep-copied next revision. A shorten patch
  uses exactly one `shot_id` or one-based `shot_index` and integer `shorten_us`.
  Later shots retain their source ranges and shift on the target timeline. A
  caption crossing the removed interval or partially removed audio cue requires
  explicit timing review. Continuous BGM crossing the cut is shortened at its
  tail. Music gain patches use `kind=music_gain`, one-based `music_index`, and a
  finite `gain_db`. These are local proposals, never claims of actual draft edits.
- `verify_media(path, expected=None, *, ffprobe=None, ffmpeg=None)` checks an
  existing local video and fully decodes it. Requested duration, dimensions,
  aspect ratio, frame rate and audio requirements are compared when supplied.
  Black intervals, sustained silence and near-full-scale audio peaks require
  review. `passed=true` means local technical checks passed;
  `review_status=technical_pass` still leaves story/caption quality and actual
  editor reopening explicitly unverified.

Content evidence uses a list of records with `kind`, `description`,
`source_in_us` and `source_out_us`. Kinds: `user_annotation`, `user_instruction`,
`frame`, `transcript`. Frame/transcript records need an existing `evidence_path`;
frame records additionally require `content_reviewed=true`. The evidence interval
must cover the chosen source range. A sampled frame alone proves only that frame.

## Verification performed

23 tests passed with actual native inspection tools configured; no technical tests
were skipped in that run. The tests generate temporary WAV, PNG and small MPEG-4
technical fixtures for inspection checks only. They are not replacement footage,
are not committed, and do not satisfy any CapCut B/C acceptance item.

Command:

```powershell
$env:AUTO_CAPCUT_FFPROBE = '<existing native ffprobe path>'
$env:AUTO_CAPCUT_FFMPEG = '<existing native full-video FFmpeg path>'
python -m unittest tests.test_media tests.test_plan tests.test_qa -v
```

Actual tools on this machine: foobar2000's installed `ffprobe`
`N-99340-g82fdd9b67c`; Jianying's installed FFmpeg reports `21.7.0-9c087b133d`
and resides in its `11.6.0.14552` application folder. No binary was downloaded or
added as a Python dependency. The foobar FFmpeg build is audio-only and cannot
perform video decode QA, so it was not used for video checks.

Verified behaviors include Unicode/space paths, missing/corrupt media, absent
inspection tools, empty folders, PNG evidence, non-overwrite extraction, integer
time validation, out-of-source ranges, discontinuous timelines, caption overlap,
music bounds/non-finite gain rejection, content evidence gates, immutable local
shortening/gain revisions, actual decode, black/silence review flags, mismatched
output dimensions, and separate video/container duration bounds.

The bundled Jianying FFmpeg prints `invalid param` for some signal-start time
values. QA preserves these detector messages and still requests review, rather
than silently ignoring the detected black/silent interval. It does not fabricate
an exact start timestamp from this malformed output.

## Unverified and limitations

- No official CapCut editing or export was run by this module task.
- No user footage, real timeline revision, editable project or domestic Jianying
  compatibility has been accepted. Those require the parent task's actual tools,
  permitted media and application inspection.
- Source/target speed changes, arbitrary timeline rebuilding and ambiguous
  subtitle/audio timing edits are rejected rather than inferred.
- A technical pass cannot judge narrative continuity, music balance, subtitle
  meaning or editorial intent. Listening/viewing and editor checks remain needed.
- Configured binaries must support the required codecs/filters. Missing tools
  return explicit blocked status; they are never downloaded automatically.
- Without configured/PATH ffprobe and full FFmpeg, actual fixture tests are
  explicitly skipped by CI instead of reported as real-media verification.
