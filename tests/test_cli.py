"""The executable Skill's local public command boundary."""
import json
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


if __name__ == '__main__':
    unittest.main()
