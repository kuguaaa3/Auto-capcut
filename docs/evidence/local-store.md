# Project store and route checks

2026-10-27, Windows, Python 3.11, integration base `cd64e51`.
Matt Pocock `tdd` applied at the agreed public project-state and route seams.

## Verified locally

`python -m unittest tests.test_store tests.test_routes -v`: 9 tests pass.
`python -m compileall -q skills/auto-capcut/scripts`: passes.
`git diff --check`: passes.

Red → green iterations were run for new-session recovery; immutable plans and
compare-and-swap revision conflicts; pending versus succeeded external operations;
pause/block/resume; asset and capability persistence; conservative route hints.
Additional checks cover concurrent writers, rejected invalid JSON updates,
credential fields, Windows-reserved identifiers and path traversal.

## Public API

Import `autocapcut.store.ProjectStore` from the Skill's scripts directory.

- `ProjectStore(workspace)` uses `workspace/projects/<project_id>`.
- `create(name, goal, *, preferred_formats=None, project_id=None)` starts revision 0.
- `load(project_id)`, `list_projects()`, `project_path(project_id)`.
- `update(project_id, expected_revision, changes)` creates a new snapshot/revision.
- `save_plan(project_id, plan, expected_revision)` creates a new immutable plan
  revision and marks PLANNED; `load_plan(project_id, revision=None)` loads the
  committed plan pointer or an explicitly selected historical version.
- `save_assets(project_id, assets, expected_revision)` creates a new asset snapshot
  and INPUT_READY revision. `load_assets(project_id)` follows the committed pointer.
- `save_capabilities(project_id, capabilities, expected_revision=None)` is
  metadata-only, optionally CAS checked; `load_capabilities(project_id)` defaults
  to unknown connection/capabilities until discovery is recorded.
- `pause(project_id, expected_revision)`,
  `block(project_id, expected_revision, error)`, and
  `resume(project_id, expected_revision)` preserve the prior valid status.
- `begin_operation(project_id, operation_id, tool, parameters, expected_revision)`
  returns `execute` for a new intent, `reuse` for an already successful same intent,
  and `reconcile` for a pending/failed/unknown same intent. Reusing the operation ID
  with different arguments raises E_CONFLICT.
- `finish_operation(project_id, operation_id, status, result=None, error=None)`
  records succeeded/failed/unknown; succeeded advances the local project revision.
  Reload before the next CAS mutation. `operations(project_id)` reads its journal.
- `autocapcut.routes.route_intent(text, current_project=None)` returns a hint using
  labels new/styles/style/research/reference/revise/export/learn/resume/explain/
  pause/mode/unknown. It preserves raw text, sets execution=none, and always leaves
  semantic interpretation to Codex. Learning requires separate confirmation.

## Recovery and limits

JSON state and operation journals use same-directory temporary files, flush/fsync
and atomic replace. A project lock excludes competing writers; an interrupted
writer leaves a lock requiring process inspection before manual recovery. Stale
locks are never guessed safe to delete. An uncertain editor operation is never
automatically replayed. Snapshots and operation records are local evidence only;
they do not prove the remote editor accepted or saved a change.

Plan validation belongs to the planner's public boundary. This persistence layer
does not interpret timelines, invoke editor tools, upload files, or manufacture
media. It does not implement remote rollback by changing local project.json.
CapCut real editing, remote read-back, QA/export and domestic Jianying acceptance
remain unverified by these tests.
