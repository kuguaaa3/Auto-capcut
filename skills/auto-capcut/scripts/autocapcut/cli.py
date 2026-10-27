"""Local support commands. Actual editing is performed by Codex native tools."""
import argparse
import json
from pathlib import Path
import sys

from .errors import AutoCapcutError

SKILL_ROOT = Path(__file__).resolve().parents[2]


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as exc:
        raise AutoCapcutError('E_PLAN', f'Cannot read JSON: {path}', 'Check the file path and JSON encoding.') from exc


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--workspace', default='auto-capcut-workspace')
    sub = result.add_subparsers(dest='command', required=True)
    route = sub.add_parser('route', help='Conservative route hint; does not edit')
    route.add_argument('text')
    doctor = sub.add_parser('doctor', help='Read-only native plugin and connection discovery')
    doctor.add_argument('--check-connection', action='store_true')
    doctor.add_argument('--codex-cli')
    styles = sub.add_parser('styles', help='List or resolve a style')
    styles.add_argument('--query', default='')
    styles.add_argument('--id')
    styles.add_argument('--version')
    project = sub.add_parser('create', help='Create an isolated local project')
    project.add_argument('--name', required=True)
    project.add_argument('--goal', required=True)
    project.add_argument('--format', action='append', dest='formats')
    sub.add_parser('projects')
    for command in ('show', 'context', 'assets', 'select', 'plan', 'revise', 'pause', 'resume', 'capabilities', 'operation', 'set-mode', 'confirm-plan'):
        item = sub.add_parser(command)
        item.add_argument('project_id')
        if command not in ('show', 'context'):
            item.add_argument('--expected-revision', type=int, required=True)
        if command == 'assets':
            item.add_argument('paths', nargs='+')
            item.add_argument('--ffprobe')
            item.add_argument('--annotations', help='Actual user/frame/transcript evidence keyed by local source path')
        elif command == 'select':
            item.add_argument('--id', required=True)
            item.add_argument('--version')
        elif command in ('plan', 'revise'):
            item.add_argument('--file', required=True)
        elif command == 'capabilities':
            item.add_argument('--file', required=True, help='Current actual discovery snapshot')
        elif command == 'operation':
            item.add_argument('--file', required=True, help='Native-tool handoff request')
        elif command == 'set-mode':
            item.add_argument('mode', choices=['direct', 'plan-first'])
    finish = sub.add_parser('settle', help='Journal a real native-tool result; does not declare export complete')
    finish.add_argument('project_id')
    finish.add_argument('--id', required=True)
    finish.add_argument('--status', choices=['succeeded', 'failed', 'unknown'], required=True)
    finish.add_argument('--file', required=True)
    qa = sub.add_parser('qa', help='Inspect a real exported video, without editing')
    qa.add_argument('path')
    qa.add_argument('--expected')
    qa.add_argument('--ffprobe')
    qa.add_argument('--ffmpeg')
    frame = sub.add_parser('frame', help='Extract one source frame for Codex visual inspection')
    frame.add_argument('path')
    frame.add_argument('--at-us', type=int, required=True)
    frame.add_argument('--output', required=True)
    frame.add_argument('--ffprobe')
    frame.add_argument('--ffmpeg')
    learn = sub.add_parser('learn', help='Save only an explicitly approved reusable style proposal')
    learn.add_argument('--file', required=True)
    learn.add_argument('--approved', action='store_true')
    rollback = sub.add_parser('rollback-style')
    rollback.add_argument('style_id')
    rollback.add_argument('version')
    rollback.add_argument('--approved', action='store_true')
    return result


def execute(args):
    if args.command == 'route':
        from .routes import route_intent
        return route_intent(args.text)
    if args.command == 'doctor':
        from .environment import inspect_environment
        from .adapter import OfficialAdapter
        return OfficialAdapter(inspect_environment(check_connection=args.check_connection,
                              codex_cli=args.codex_cli)).discover_capabilities()
    if args.command in ('styles', 'learn', 'rollback-style'):
        from .styles import StyleRegistry
        registry = StyleRegistry(SKILL_ROOT, args.workspace)
        if args.command == 'styles':
            return registry.load(args.id, args.version) if args.id else registry.list(args.query)
        if args.command == 'learn':
            return registry.save(read_json(args.file), approved=args.approved)
        return registry.rollback(args.style_id, args.version, approved=args.approved)
    if args.command == 'qa':
        from .qa import verify_media
        return verify_media(args.path, read_json(args.expected) if args.expected else None,
                            ffprobe=args.ffprobe, ffmpeg=args.ffmpeg)
    if args.command == 'frame':
        from .media import extract_frame
        return extract_frame(args.path, args.at_us, args.output, ffprobe=args.ffprobe, ffmpeg=args.ffmpeg)
    from .store import ProjectStore
    store = ProjectStore(args.workspace)
    if args.command == 'create':
        return store.create(args.name, args.goal, preferred_formats=args.formats)
    if args.command == 'projects':
        return store.list_projects()
    project = store.load(args.project_id)
    if args.command == 'show':
        return project
    if args.command == 'context':
        return {'project': project, 'assets': store.load_assets(args.project_id),
                'capability': store.load_capabilities(args.project_id),
                'plan': store.load_plan(args.project_id) if project.get('plan_revision') else None,
                'operations': store.operations(args.project_id),
                'next_action': 'Read the saved plan and official server draft before any external edit. Reconcile unfinished operations.'}
    if args.command == 'assets':
        from .media import inspect_assets
        assets = inspect_assets(args.paths, ffprobe=args.ffprobe)
        if args.annotations:
            annotations = read_json(args.annotations)
            if not isinstance(annotations, list):
                raise AutoCapcutError('E_MEDIA', 'Annotations must be a list of path and content_evidence records.')
            by_path = {str(Path(asset['path']).resolve()): asset for asset in assets}
            for record in annotations:
                path = str(Path(record['path']).resolve())
                if path not in by_path or not isinstance(record.get('content_evidence'), list):
                    raise AutoCapcutError('E_MEDIA', 'Annotation does not match an inspected source file.')
                by_path[path]['content_evidence'] = record['content_evidence']
        return store.save_assets(args.project_id, assets, args.expected_revision)
    if args.command == 'select':
        from .styles import StyleRegistry
        style = StyleRegistry(SKILL_ROOT, args.workspace).select(explicit={'id': args.id, 'version': args.version})
        selection = {k: style[k] for k in ('id', 'name', 'version', 'source') if k in style}
        selection['confirmed_by_user'] = True
        changes = {'style': selection}
        previous = project.get('style') or {}
        if (previous.get('id'), previous.get('version')) != (selection['id'], selection['version']):
            changes.update(status='STYLE_SELECTED', plan_revision=None, confirmed_plan_revision=None)
        return store.update(args.project_id, args.expected_revision, changes)
    if args.command in ('plan', 'revise'):
        from .plan import validate_plan, revise_plan
        plan = read_json(args.file)
        if args.command == 'revise':
            plan = revise_plan(store.load_plan(args.project_id), plan)
        validate_plan(plan, store.load_assets(args.project_id))
        selected = project.get('style') or {}
        if selected.get('id') != plan.get('style_id'):
            raise AutoCapcutError('E_PLAN', 'Plan style must match the user-selected project style.')
        if not selected.get('version') or plan.get('style_version', selected['version']) != selected['version']:
            raise AutoCapcutError('E_PLAN', 'Plan style version does not match the selected version.')
        plan['style_version'] = selected['version']
        return store.save_plan(args.project_id, plan, args.expected_revision)
    if args.command == 'set-mode':
        return store.update(args.project_id, args.expected_revision, {'execution_preference': args.mode})
    if args.command == 'confirm-plan':
        from .plan import validate_plan
        report = validate_plan(store.load_plan(args.project_id), store.load_assets(args.project_id))
        if not report['ready_to_edit']:
            raise AutoCapcutError('E_PLAN', 'Resolve plan questions and evidence before confirming it.')
        return store.update(args.project_id, args.expected_revision, {'confirmed_plan_revision': project['plan_revision']})
    if args.command in ('pause', 'resume'):
        if args.command == 'resume':
            from .media import verify_sources
            verify_sources(store.load_assets(args.project_id))
        return getattr(store, args.command)(args.project_id, args.expected_revision)
    if args.command == 'capabilities':
        from .adapter import OfficialAdapter
        snapshot = read_json(args.file)
        return store.save_capabilities(args.project_id, OfficialAdapter(snapshot).discover_capabilities(), args.expected_revision)
    if args.command == 'operation':
        from .adapter import OfficialAdapter
        request = read_json(args.file)
        if request.get('requires_upload') and request.get('upload_approved') is not True:
            raise AutoCapcutError('E_AUTH', 'Uploading the selected local media requires explicit user approval.')
        if request['operation'] in ('rough_cut', 'apply_plan', 'revise', 'captions', 'audio', 'export'):
            from .plan import validate_plan
            plan = store.load_plan(args.project_id)
            style = project.get('style') or {}
            if (plan.get('style_id'), plan.get('style_version')) != (style.get('id'), style.get('version')):
                raise AutoCapcutError('E_PLAN', 'Saved plan is stale for the selected style/version.', 'Create a new plan for the current selection.')
            report = validate_plan(plan, store.load_assets(args.project_id))
            if not report.get('ready_to_edit'):
                raise AutoCapcutError('E_PLAN', 'Plan has unresolved decisions or lacks actual content evidence.',
                                      'Inspect the media or obtain user annotations before editing.')
            if project['execution_preference'] == 'plan-first' and project['confirmed_plan_revision'] != project['plan_revision']:
                raise AutoCapcutError('E_APPROVAL', 'The user chose plan-first and has not confirmed this plan revision.',
                                      'Show the current plan and record explicit confirmation; or follow the user’s request to switch to direct.')
            from .media import verify_sources
            referenced = {shot['asset_id'] for shot in plan['shots']} | {music['asset_id'] for music in plan.get('music', [])}
            verify_sources(store.load_assets(args.project_id), referenced)
        prepared = OfficialAdapter(store.load_capabilities(args.project_id)).prepare(
            request['operation'], request['arguments'], operation_id=request['operation_id'])
        action = store.begin_operation(args.project_id, prepared['operation_id'], prepared['tool'],
                                       prepared['arguments'], args.expected_revision)
        if action['action'] != 'execute':
            return {'journal': action, 'next_action': 'Reuse a confirmed result, or reconcile the official server; do not invoke again.'}
        return {'handoff': prepared, 'journal': action}
    if args.command == 'settle':
        receipt = read_json(args.file)
        return store.finish_operation(args.project_id, args.id, args.status,
                                      result=receipt if args.status == 'succeeded' else None,
                                      error=receipt if args.status != 'succeeded' else None)
    raise AutoCapcutError('E_TOOL', 'Unknown local command.')


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = execute(args)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except AutoCapcutError as exc:
        print(json.dumps({'status': 'blocked', 'error': exc.to_dict()}, ensure_ascii=False), file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'blocked', 'error': {'code': 'E_PLAN',
              'human_message': str(exc), 'recover_action': 'Check local inputs; no editing success is implied.'}}, ensure_ascii=False), file=sys.stderr)
        return 2
