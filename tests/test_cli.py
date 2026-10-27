"""The executable Skill's local public command boundary."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ENTRY = Path(__file__).resolve().parents[1] / 'skills/auto-capcut/scripts/auto_capcut.py'


class CliTests(unittest.TestCase):
    def test_route_is_machine_readable_and_does_not_start_editing(self):
        result = subprocess.run([sys.executable, str(ENTRY), 'route', '有哪些剪辑风格'],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['intent'], 'styles')

    def test_project_reopens_in_a_new_process_and_stale_edit_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='capcut-cli-') as workspace:
            def run(*args):
                return subprocess.run([sys.executable, str(ENTRY), '--workspace', workspace, *args],
                                      capture_output=True, text=True, encoding='utf-8')
            created = run('create', '--name', '狗狗 项目', '--goal', '保留真实动作')
            self.assertEqual(created.returncode, 0, created.stderr)
            project = json.loads(created.stdout)
            resumed = run('context', project['project_id'])
            self.assertEqual(json.loads(resumed.stdout)['project']['name'], '狗狗 项目')
            paused = run('pause', project['project_id'], '--expected-revision', '0')
            self.assertEqual(json.loads(paused.stdout)['status'], 'PAUSED')
            stale = run('resume', project['project_id'], '--expected-revision', '0')
            self.assertEqual(stale.returncode, 2)
            self.assertEqual(json.loads(stale.stderr)['error']['code'], 'E_CONFLICT')


@unittest.skipUnless((os.environ.get('AUTO_CAPCUT_FFPROBE') or shutil.which('ffprobe')) and
                     (os.environ.get('AUTO_CAPCUT_FFMPEG') or shutil.which('ffmpeg')), 'Inspection binaries required')
class EditPreflightTests(unittest.TestCase):
    """Real technical source inspection + local handoff only, never CapCut editing."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='capcut-preflight-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.mp4'
        ffmpeg = os.environ.get('AUTO_CAPCUT_FFMPEG') or shutil.which('ffmpeg')
        subprocess.run([ffmpeg, '-v', 'error', '-nostdin', '-f', 'lavfi', '-i',
                        'color=c=red:s=160x90:r=25:d=2', '-c:v', 'mpeg4', str(self.source)],
                       check=True, capture_output=True, timeout=30)
        self.pid = self.call('create', '--name', '技术样本', '--goal', '仅验证本地执行门禁')['project_id']
        self.call('assets', self.pid, str(self.source), '--expected-revision', '0')
        context = self.call('context', self.pid)
        asset = context['assets'][0]
        annotations = [{'path': str(self.source), 'content_evidence': [{'kind': 'user_annotation',
                       'description': 'Technical red frame fixture, not user footage.',
                       'source_in_us': 0, 'source_out_us': 2_000_000}]}]
        self.call('assets', self.pid, str(self.source), '--annotations', self.json_file('annotations', annotations),
                  '--expected-revision', str(self.revision()))
        self.call('select', self.pid, '--id', 'pet-healing', '--expected-revision', str(self.revision()))
        self.plan = {'schema_version': '1.0', 'revision': 1, 'style_id': 'pet-healing',
                     'target': {'aspect_ratio': '16:9', 'duration_us': 2_000_000},
                     'shots': [{'shot_id': 's1', 'asset_id': asset['asset_id'], 'source_in_us': 0,
                                'source_out_us': 2_000_000, 'target_in_us': 0, 'target_out_us': 2_000_000,
                                'decision': 'Keep technical fixture.', 'evidence': 'Explicit technical range.'}],
                     'captions': [], 'music': [], 'unresolved': []}
        self.call('plan', self.pid, '--file', self.json_file('plan', self.plan), '--expected-revision', str(self.revision()))
        catalogue = {'backend': 'capcut_official', 'connection': 'connected',
                     'tools': [{'name': 'fixture_edit', 'inputSchema': {'type': 'object'}}],
                     'bindings': {'apply_plan': 'fixture_edit'}}
        self.call('capabilities', self.pid, '--file', self.json_file('catalogue', catalogue),
                  '--expected-revision', str(self.revision()))
        self.request = self.json_file('request', {'operation': 'apply_plan', 'operation_id': 'fixture-op', 'arguments': {}})

    def json_file(self, name, value):
        path = self.root / (name + '.json')
        path.write_text(json.dumps(value), encoding='utf-8')
        return str(path)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ENTRY), '--workspace', str(self.root / 'workspace'), *args],
                              capture_output=True, text=True, encoding='utf-8')

    def call(self, *args):
        response = self.run_cli(*args)
        self.assertEqual(response.returncode, 0, response.stderr)
        return json.loads(response.stdout)

    def revision(self):
        return self.call('show', self.pid)['current_revision']

    def operation(self):
        return self.run_cli('operation', self.pid, '--file', self.request, '--expected-revision', str(self.revision()))

    def test_style_switch_preserves_history_and_blocks_the_old_plan(self):
        old = self.call('context', self.pid)['plan']
        self.call('select', self.pid, '--id', 'talking-head', '--expected-revision', str(self.revision()))
        response = self.operation()
        self.assertEqual(response.returncode, 2)
        context = self.call('context', self.pid)
        self.assertIsNone(context['plan'])
        self.assertTrue((self.root / 'workspace/projects' / self.pid / 'plan' / f"v{old['revision']:03d}.json").is_file())

    def test_missing_or_changed_source_blocks_execution_before_journaling(self):
        original = self.source.read_bytes()
        self.source.write_bytes(original + b'changed')
        changed = self.operation()
        self.assertEqual(changed.returncode, 2)
        self.assertEqual(json.loads(changed.stderr)['error']['code'], 'E_MEDIA_CHANGED')
        self.source.unlink()
        missing = self.operation()
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(json.loads(missing.stderr)['error']['code'], 'E_MEDIA_MISSING')
        self.assertEqual(self.call('context', self.pid)['operations'], [])

    def test_plan_first_preference_survives_restart_and_requires_current_plan_consent(self):
        self.call('set-mode', self.pid, 'plan-first', '--expected-revision', str(self.revision()))
        self.assertEqual(self.call('context', self.pid)['project']['execution_preference'], 'plan-first')
        self.assertEqual(self.operation().returncode, 2)
        self.call('confirm-plan', self.pid, '--expected-revision', str(self.revision()))
        self.assertEqual(self.operation().returncode, 0)
        self.call('plan', self.pid, '--file', self.json_file('new-plan', self.plan), '--expected-revision', str(self.revision()))
        self.assertEqual(self.operation().returncode, 2)
        self.call('set-mode', self.pid, 'direct', '--expected-revision', str(self.revision()))
        result = self.operation()
        self.assertEqual(result.returncode, 0, result.stderr)
        # The same pending external operation is reconciled, never reissued.
        self.assertEqual(json.loads(result.stdout)['journal']['action'], 'reconcile')


if __name__ == '__main__':
    unittest.main()
