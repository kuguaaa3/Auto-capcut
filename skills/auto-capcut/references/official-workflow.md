# Official CapCut bridge

This file routes Codex to the installed vendor Skills. It is not an API schema.
The verified vendor bundle at development time is CapCut 0.2.6. Always discover
the current native tools and read their actual schemas before invocation.

## Preflight

1. Run `doctor --check-connection`; distinguish installed from authorized. For
   login-required or missing native tools read the installed vendor `mcp-auth`
   Skill and follow its in-app authorization workflow. No credentials in files.
2. Read the installed vendor `video-editing/SKILL.md`. For initial assembly read
   its `references/ai-rough-cut.md`; for captions-only use its captions workflow.
3. Discover the exact tools requested by that vendor workflow, including native
   preview/plan cards. Discovery failure after a connected account requires its
   documented task-loading recovery. Do not emulate cards or build a new UI.
4. Preserve a current actual tool catalogue (name, description, inputSchema) in
   capability.json with OS/plugin/editor versions and discovery time. A native
   tool being present establishes no editing capability on its own. Binding
   names in the local adapter are local operation keys, never invented APIs.

## Initial assembly

- Resolve the user-selected style and analyze actual source frames/speech or
  user-provided segment annotations. Write integer-microsecond plan with reasons.
  Validate it; `ready_to_edit` must be true, not just `valid`.
- Obtain explicit approval identifying the clips and CapCut before any upload.
  Read the vendor `capcut-upload` Skill and use its documented local uploader.
  Preserve real returned resource IDs, file hashes and user approval scope.
- Journal a stable operation ID before any non-idempotent external write.
  Invoke the discovered native rough-cut tool via Codex, with the actual schema.
  Retain actual AI session and event cursor, handle events in order, and display
  native cards exactly as required by the installed vendor Skill.
- A preview, plan or uploaded media is not a multitrack editable draft. Inspect
  the returned draft and distinguish real separate source clips from a flattened
  rendered-video seed. A flattened seed cannot pass the third-shot edit check.

## Incremental edits

Read vendor `web-collaborative-editing` and `capcut-stdraft-builder` Skills. Keep
AI Lab session IDs, cloud-draft sessions, versions, resource IDs and segment IDs
separate. Before every editing round read/check the current server baseline.
Save the previous complete server snapshot and tool receipts locally before edits.

Prepare captions/music/material resources first, use only the vendor's available
atomic functions, validate locally, then save once with the actual base version.
Server readback and the editor's visual state determine what was saved. A version
conflict stops the round; follow vendor recovery, never overwrite newer user edits.

For “第三镜缩短1秒”, map the user's third shot to an actual distinct source
segment. Preserve the previous server version and all unaffected clips. If no
discovered supported operation expresses this change, report blocked/unsupported;
do not append a duplicate clip, rebuild with another editor or alter only plan.json.

## Export and evidence

Discover actual video export and project-delivery capabilities independently.
Cloud save is not MP4 export. Deliver only the actual tool-returned editor link
or real file path; do not construct URLs. Download only when the actual result
provides a supported download workflow. Verify the local file with `qa`, play it,
inspect captions/audio/aspect ratio and reopen the editable project. A local QA
report never proves the remote project can be edited.

Domestic Jianying is a separate matrix. Until the exact installed target version
can open, modify, save and reopen the real draft, report unknown/unsupported and
offer only genuinely verified output formats. No compatibility engine is enabled.

## Interruptions

Persist stable session/cursor/version immediately after each successful native
response. On uncertain writes, leave journal pending/unknown and read the server
before any retry. Pause prevents subsequent work but cannot claim cancellation
of a remote operation. Resume from the previous confirmed state and recheck
source hashes, tool availability and server version.

Source: https://www.capcut.com/tools/capcut-x-codex and the vendor-installed Skills.
Vendor implementation and authentication scripts are not redistributed here.
