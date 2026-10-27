"""Atomic local project state; this module never invokes an editor or uploads media."""

from __future__ import annotations

import json
import os
import re
import tempfile
import uuid
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from .errors import AutoCapcutError


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value) -> None:
    """Replace one JSON document only after the new bytes have been flushed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.pending-', suffix='.json', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except (OSError, ValueError, TypeError) as exc:
        raise AutoCapcutError('E_STATE', 'Local state could not be written atomically.',
                              'Check disk access and JSON values; the prior committed state is retained.') from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _public_data(value) -> None:
    """Reject accidental credential fields before they enter durable history."""
    if isinstance(value, dict):
        for key, item in value.items():
            if re.search(r'token|password|cookie|authorization|secret|credential', str(key), re.I):
                raise AutoCapcutError('E_SECURITY', 'Credential fields cannot be saved in project history.')
            _public_data(item)
    elif isinstance(value, list):
        for item in value:
            _public_data(item)


class ProjectStore:
    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).expanduser().resolve()
        self.projects = self.workspace / 'projects'
        self.projects.mkdir(parents=True, exist_ok=True)

    def project_path(self, project_id: str) -> Path:
        if not isinstance(project_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}', project_id):
            raise AutoCapcutError('E_PROJECT', 'Invalid project identifier.', 'Use a project_id returned by create or list_projects.')
        if re.fullmatch(r'CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]', project_id, re.I):
            raise AutoCapcutError('E_PROJECT', 'Reserved Windows project identifier.')
        path = self.projects / project_id
        if not path.resolve().is_relative_to(self.projects.resolve()):
            raise AutoCapcutError('E_PROJECT', 'Project path escapes the workspace.')
        return path

    def create(self, name: str, goal: str, *, preferred_formats=None, project_id=None) -> dict:
        if not isinstance(name, str) or not name.strip() or not isinstance(goal, str) or not goal.strip():
            raise AutoCapcutError('E_PROJECT', 'Project name and editing goal are required.')
        project_id = project_id or uuid.uuid4().hex
        path = self.project_path(project_id)
        try:
            path.mkdir()
        except FileExistsError as exc:
            raise AutoCapcutError('E_CONFLICT', 'Project already exists; no files were overwritten.') from exc
        timestamp = _now()
        project = {'schema_version': '1.0', 'project_id': project_id, 'name': name,
                   'created_at': timestamp, 'updated_at': timestamp, 'status': 'NEW',
                   'goal': goal, 'style': None, 'preferred_formats': preferred_formats or ['mp4', 'capcut'],
                   'current_revision': 0, 'last_verified_revision': None,
                   'editor': {'backend': 'capcut_official', 'capability_snapshot_id': None},
                   'last_error': None, 'last_confirmed_operation': None, 'plan_revision': None,
                   'assets_revision': None}
        project['resume_status'] = None
        atomic_json(path / 'snapshots' / 'v000.json', project)
        atomic_json(path / 'project.json', project)
        return deepcopy(project)

    def load(self, project_id: str) -> dict:
        path = self.project_path(project_id) / 'project.json'
        try:
            project = json.loads(path.read_text(encoding='utf-8'))
            if project.get('project_id') != project_id or not isinstance(project.get('current_revision'), int):
                raise ValueError('Project identity or revision is invalid')
            return project
        except FileNotFoundError as exc:
            raise AutoCapcutError('E_PROJECT', 'Project was not found.', 'List projects and select an existing project_id.') from exc
        except (ValueError, TypeError, AttributeError) as exc:
            raise AutoCapcutError('E_STATE', 'Project state is damaged.', 'Preserve the file and recover from a verified snapshot.') from exc

    def list_projects(self) -> list[dict]:
        return [self.load(path.parent.name) for path in sorted(self.projects.glob('*/project.json'))]

    @contextmanager
    def _locked(self, project_id: str):
        path = self.project_path(project_id)
        if not (path / 'project.json').is_file():
            self.load(project_id)
        lock = path / '.write.lock'
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise AutoCapcutError('E_BUSY', 'Another writer or an interrupted write holds this project.',
                                  'Check the owning process before removing the stale project lock.') from exc
        try:
            with os.fdopen(descriptor, 'w', encoding='ascii') as stream:
                stream.write(str(os.getpid()))
            yield path
        finally:
            lock.unlink(missing_ok=True)

    def _check_revision(self, project: dict, expected_revision: int) -> None:
        if type(expected_revision) is not int or project['current_revision'] != expected_revision:
            raise AutoCapcutError('E_CONFLICT', 'Project changed since it was read.',
                                  'Reload the project and recompute the change; do not replay external edits.')

    def _commit(self, path: Path, project: dict, changes: dict) -> dict:
        protected = {'project_id', 'schema_version', 'created_at', 'current_revision', 'updated_at'}
        allowed = set(project) - protected
        if not isinstance(changes, dict) or set(changes) - allowed:
            raise AutoCapcutError('E_STATE', 'Update includes unknown or protected project fields.')
        changed = deepcopy(project)
        changed.update(deepcopy(changes))
        if changed['status'] not in {'NEW', 'INPUT_READY', 'STYLE_SELECTED', 'PLANNED', 'EDITING',
                                     'DRAFT_READY', 'REVIEWED', 'EXPORTED', 'BLOCKED', 'PAUSED'}:
            raise AutoCapcutError('E_STATE', 'Unknown project status.')
        # A crash can leave an uncommitted snapshot ahead of project.json. Preserve it
        # and allocate the next unused revision rather than overwriting history.
        revision = project['current_revision'] + 1
        while (path / 'snapshots' / f'v{revision:03d}.json').exists():
            revision += 1
        changed['current_revision'] = revision
        changed['updated_at'] = _now()
        atomic_json(path / 'snapshots' / f'v{revision:03d}.json', changed)
        atomic_json(path / 'project.json', changed)
        return changed

    def update(self, project_id: str, expected_revision: int, changes: dict) -> dict:
        with self._locked(project_id) as path:
            project = self.load(project_id)
            self._check_revision(project, expected_revision)
            return self._commit(path, project, changes)

    def pause(self, project_id: str, expected_revision: int) -> dict:
        with self._locked(project_id) as path:
            project = self.load(project_id)
            self._check_revision(project, expected_revision)
            if project['status'] == 'PAUSED':
                return project
            prior = project.get('resume_status') if project['status'] == 'BLOCKED' else project['status']
            return self._commit(path, project, {'status': 'PAUSED', 'resume_status': prior})

    def block(self, project_id: str, expected_revision: int, error: AutoCapcutError | dict) -> dict:
        error = error.to_dict() if isinstance(error, AutoCapcutError) else error
        if not isinstance(error, dict) or not {'code', 'human_message', 'recover_action'} <= set(error):
            raise AutoCapcutError('E_STATE', 'A blocker needs code, human_message and recover_action.')
        _public_data(error)
        with self._locked(project_id) as path:
            project = self.load(project_id)
            self._check_revision(project, expected_revision)
            prior = project.get('resume_status') if project['status'] in {'BLOCKED', 'PAUSED'} else project['status']
            return self._commit(path, project, {'status': 'BLOCKED', 'resume_status': prior,
                                               'last_error': error})

    def resume(self, project_id: str, expected_revision: int) -> dict:
        """Resume local routing only. Pending external work still needs read-back."""
        with self._locked(project_id) as path:
            project = self.load(project_id)
            self._check_revision(project, expected_revision)
            if project['status'] not in {'PAUSED', 'BLOCKED'}:
                return project
            prior = project.get('resume_status')
            if not prior or prior in {'PAUSED', 'BLOCKED'}:
                raise AutoCapcutError('E_STATE', 'Last valid project status is unavailable.',
                                      'Inspect snapshots before continuing.')
            return self._commit(path, project, {'status': prior, 'resume_status': None, 'last_error': None})

    def save_plan(self, project_id: str, plan: dict, expected_revision: int) -> dict:
        """Persist a proposed plan, never evidence that an editor applied it."""
        if not isinstance(plan, dict):
            raise AutoCapcutError('E_PLAN', 'Plan must be a JSON object.')
        with self._locked(project_id) as path:
            project = self.load(project_id)
            self._check_revision(project, expected_revision)
            revision = project['current_revision'] + 1
            while ((path / 'plan' / f'v{revision:03d}.json').exists()
                   or (path / 'snapshots' / f'v{revision:03d}.json').exists()):
                revision += 1
            proposed = deepcopy(plan)
            proposed['revision'] = revision
            atomic_json(path / 'plan' / f'v{revision:03d}.json', proposed)
            # Reserve the same revision as the plan even after a prior crash left
            # an orphan plan. _commit allocates from snapshots, so skip the gap.
            project['current_revision'] = revision - 1
            return self._commit(path, project, {'status': 'PLANNED', 'plan_revision': revision, 'last_error': None})

    def load_plan(self, project_id: str, revision: int | None = None) -> dict:
        project = self.load(project_id)
        revision = project.get('plan_revision') if revision is None else revision
        if type(revision) is not int or revision < 1:
            raise AutoCapcutError('E_PLAN', 'No saved plan at the requested revision.')
        try:
            return json.loads((self.project_path(project_id) / 'plan' / f'v{revision:03d}.json').read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            raise AutoCapcutError('E_PLAN', 'Saved plan is missing or damaged.', 'Preserve existing artifacts and select an intact plan revision.') from exc

    def save_assets(self, project_id: str, assets: list[dict], expected_revision: int) -> dict:
        if not isinstance(assets, list) or any(not isinstance(a, dict) for a in assets):
            raise AutoCapcutError('E_MEDIA', 'Assets must be a list of media records.')
        _public_data(assets)
        with self._locked(project_id) as path:
            project = self.load(project_id)
            self._check_revision(project, expected_revision)
            # Preserve older inventories as well as plans. project.json is committed
            # after the versioned inventory; assets.json is a convenience mirror.
            revision = project['current_revision'] + 1
            while ((path / 'snapshots' / f'v{revision:03d}.json').exists()
                   or (path / 'snapshots' / f'assets-v{revision:03d}.json').exists()):
                revision += 1
            atomic_json(path / 'snapshots' / f'assets-v{revision:03d}.json', assets)
            project['current_revision'] = revision - 1
            result = self._commit(path, project, {'status': 'INPUT_READY', 'last_error': None,
                                                 'assets_revision': revision})
            atomic_json(path / 'assets.json', assets)
            return result

    def load_assets(self, project_id: str) -> list[dict]:
        project = self.load(project_id)
        revision = project.get('assets_revision')
        if revision is None:
            return []
        path = self.project_path(project_id) / 'snapshots' / f'assets-v{revision:03d}.json'
        try:
            result = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(result, list):
                raise ValueError('Asset inventory must be a list')
            return result
        except (OSError, ValueError) as exc:
            raise AutoCapcutError('E_MEDIA', 'Saved asset inventory is missing or damaged.',
                                  'Re-inspect the source files; never infer missing media.') from exc

    def save_capabilities(self, project_id: str, capabilities: dict, expected_revision: int | None = None) -> dict:
        if not isinstance(capabilities, dict):
            raise AutoCapcutError('E_TOOL', 'Capability snapshot must be an object.')
        _public_data(capabilities)
        with self._locked(project_id) as path:
            if expected_revision is not None:
                self._check_revision(self.load(project_id), expected_revision)
            atomic_json(path / 'capability.json', capabilities)
        return deepcopy(capabilities)

    def load_capabilities(self, project_id: str) -> dict:
        self.load(project_id)
        path = self.project_path(project_id) / 'capability.json'
        if not path.exists():
            return {'backend': 'capcut_official', 'connection': 'unknown', 'supports': {}, 'tools': [],
                    'notes': ['No capability discovery has been recorded.']}
        try:
            result = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(result, dict):
                raise ValueError('Capability snapshot must be an object')
            return result
        except (OSError, ValueError) as exc:
            raise AutoCapcutError('E_TOOL', 'Saved capability snapshot is damaged.',
                                  'Rediscover the authorized official tools.') from exc

    def operations(self, project_id: str) -> list[dict]:
        self.load(project_id)
        journal = self.project_path(project_id) / 'history' / 'operations.jsonl'
        if not journal.exists():
            return []
        try:
            return [json.loads(line) for line in journal.read_text(encoding='utf-8').splitlines() if line.strip()]
        except (OSError, ValueError) as exc:
            raise AutoCapcutError('E_STATE', 'Operation journal is damaged; external outcome is unknown.',
                                  'Preserve the journal and read back the official editor before any retry.') from exc

    def _journal(self, path: Path, event: dict, events: list[dict]) -> None:
        """Atomically replace the append-only event sequence (no torn final line)."""
        journal = path / 'history' / 'operations.jsonl'
        journal.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=journal.parent,
                                             prefix='.pending-', delete=False) as stream:
                temporary = Path(stream.name)
                for item in [*events, event]:
                    stream.write(json.dumps(item, ensure_ascii=False, allow_nan=False) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, journal)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def begin_operation(self, project_id: str, operation_id: str, tool: str,
                        parameters: dict, expected_revision: int) -> dict:
        if not isinstance(operation_id, str) or not operation_id.strip() or not isinstance(tool, str) or not tool.strip():
            raise AutoCapcutError('E_APPLY', 'A stable operation ID and discovered tool name are required.')
        _public_data(parameters)
        with self._locked(project_id) as path:
            project = self.load(project_id)
            self._check_revision(project, expected_revision)
            if project['status'] in {'PAUSED', 'BLOCKED'}:
                raise AutoCapcutError('E_STATE', 'Project is paused or blocked; no new editor operation may start.',
                                      'Resolve the blocker or resume the project first.')
            events = self.operations(project_id)
            prior = [e for e in events if e.get('operation_id') == operation_id]
            if prior:
                operation = prior[-1]
                if operation['tool'] != tool or operation['parameters'] != parameters:
                    raise AutoCapcutError('E_CONFLICT', 'Operation ID was reused with different parameters.')
                return {'action': 'reuse' if operation['status'] == 'succeeded' else 'reconcile',
                        'operation': operation}
            operation = {'operation_id': operation_id, 'project_id': project_id,
                         'revision': project['current_revision'], 'tool': tool,
                         'parameters': deepcopy(parameters), 'status': 'pending', 'timestamp': _now(),
                         'result': None, 'error': None}
            self._journal(path, operation, events)
            return {'action': 'execute', 'operation': operation}

    def finish_operation(self, project_id: str, operation_id: str, status: str,
                         result=None, error=None) -> dict:
        if status not in {'succeeded', 'failed', 'unknown'}:
            raise AutoCapcutError('E_APPLY', 'Operation outcome must be succeeded, failed or unknown.')
        _public_data(result)
        _public_data(error)
        with self._locked(project_id) as path:
            project = self.load(project_id)
            events = self.operations(project_id)
            prior = [e for e in events if e.get('operation_id') == operation_id]
            if not prior:
                raise AutoCapcutError('E_APPLY', 'Operation must be recorded before an external call.')
            previous = prior[-1]
            if previous['status'] == 'succeeded':
                if status == 'succeeded' and previous['result'] == result:
                    return previous
                raise AutoCapcutError('E_CONFLICT', 'A confirmed successful operation cannot be rewritten.')
            event = {**previous, 'status': status, 'result': deepcopy(result),
                     'error': deepcopy(error), 'timestamp': _now()}
            self._journal(path, event, events)
            if status == 'succeeded':
                self._commit(path, project, {'last_confirmed_operation': operation_id})
            return event
