import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/auto-capcut/scripts'))

from autocapcut.store import ProjectStore
from autocapcut.errors import AutoCapcutError


class ProjectStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / '中文 工作区'
        self.store = ProjectStore(self.workspace)

    def test_new_session_reopens_project_and_keeps_projects_independent(self):
        first = self.store.create('狗狗', '剪成30秒')
        second = self.store.create('第二条', '保留原声')
        reopened = ProjectStore(self.workspace)
        self.assertEqual(reopened.load(first['project_id'])['goal'], '剪成30秒')
        self.assertEqual(reopened.load(first['project_id'])['current_revision'], 0)
        self.assertEqual(reopened.load(second['project_id'])['goal'], '保留原声')
        self.assertEqual(len(reopened.list_projects()), 2)

    def test_revision_conflict_preserves_prior_plan_and_source_version(self):
        project = self.store.create('one', 'trim')
        pid = project['project_id']
        planned = self.store.save_plan(pid, {'shots': [{'shot_id': 's1'}]}, 0)
        revised = self.store.save_plan(pid, {'shots': [{'shot_id': 's2'}]}, planned['current_revision'])
        self.assertEqual(self.store.load_plan(pid, 1)['shots'][0]['shot_id'], 's1')
        self.assertEqual(self.store.load_plan(pid)['shots'][0]['shot_id'], 's2')
        self.assertEqual(revised['current_revision'], 2)
        with self.assertRaises(AutoCapcutError) as raised:
            self.store.update(pid, 0, {'name': 'wrong stale update'})
        self.assertEqual(raised.exception.code, 'E_CONFLICT')
        self.assertEqual(self.store.load(pid)['name'], 'one')

    def test_pending_external_edit_requires_reconciliation_and_success_is_reused(self):
        pid = self.store.create('one', 'trim')['project_id']
        first = self.store.begin_operation(pid, 'trim-v1', 'official_tool', {'segment': 's3'}, 0)
        self.assertEqual(first['action'], 'execute')
        restarted = ProjectStore(self.workspace)
        uncertain = restarted.begin_operation(pid, 'trim-v1', 'official_tool', {'segment': 's3'}, 0)
        self.assertEqual(uncertain['action'], 'reconcile')
        restarted.finish_operation(pid, 'trim-v1', 'succeeded', result={'version': 'remote-v2'})
        current = restarted.load(pid)
        repeated = restarted.begin_operation(pid, 'trim-v1', 'official_tool', {'segment': 's3'}, current['current_revision'])
        self.assertEqual(repeated['action'], 'reuse')
        self.assertEqual(repeated['operation']['result']['version'], 'remote-v2')
        with self.assertRaises(AutoCapcutError):
            restarted.begin_operation(pid, 'trim-v1', 'official_tool', {'segment': 's4'}, current['current_revision'])

    def test_pause_and_block_resume_prior_valid_state_without_clearing_pending_edits(self):
        pid = self.store.create('one', 'trim')['project_id']
        self.store.begin_operation(pid, 'trim-v1', 'official_tool', {}, 0)
        paused = self.store.pause(pid, 0)
        self.assertEqual(paused['status'], 'PAUSED')
        with self.assertRaises(AutoCapcutError):
            self.store.begin_operation(pid, 'next', 'official_tool', {}, paused['current_revision'])
        resumed = self.store.resume(pid, paused['current_revision'])
        self.assertEqual(resumed['status'], 'NEW')
        self.assertEqual(self.store.begin_operation(pid, 'trim-v1', 'official_tool', {}, resumed['current_revision'])['action'], 'reconcile')
        blocked = self.store.block(pid, resumed['current_revision'], AutoCapcutError('E_AUTH', 'Reconnect', 'Authorize CapCut'))
        self.assertEqual(blocked['last_error']['code'], 'E_AUTH')
        self.assertEqual(self.store.resume(pid, blocked['current_revision'])['status'], 'NEW')

    def test_assets_and_capability_snapshot_are_reloaded_without_cross_project_writes(self):
        pid = self.store.create('one', 'trim')['project_id']
        other = self.store.create('two', 'another')['project_id']
        ready = self.store.save_assets(pid, [{'asset_id': 'a1', 'path': 'D:/素材/狗.mp4'}], 0)
        self.assertEqual(ready['status'], 'INPUT_READY')
        self.store.save_capabilities(pid, {'supports': {'export': 'unknown'}}, ready['current_revision'])
        new_session = ProjectStore(self.workspace)
        self.assertEqual(new_session.load_assets(pid)[0]['asset_id'], 'a1')
        self.assertEqual(new_session.load_capabilities(pid)['supports']['export'], 'unknown')
        self.assertEqual(new_session.load_assets(other), [])
        for unsafe in ['../other', 'a/b', 'a\\b', '.', 'CON']:
            with self.subTest(unsafe=unsafe), self.assertRaises(AutoCapcutError):
                self.store.create('unsafe', 'goal', project_id=unsafe)

    def test_invalid_update_does_not_destroy_prior_state_and_concurrent_writer_is_rejected(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier

        pid = self.store.create('one', 'trim')['project_id']
        with self.assertRaises(AutoCapcutError):
            self.store.update(pid, 0, {'style': float('nan')})
        self.assertEqual(ProjectStore(self.workspace).load(pid)['current_revision'], 0)
        barrier = Barrier(2)
        def change(name):
            barrier.wait()
            try:
                ProjectStore(self.workspace).update(pid, 0, {'name': name})
                return 'committed'
            except AutoCapcutError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(change, ['first', 'second']))
        self.assertEqual(results.count('committed'), 1)
        self.assertTrue(any(result in {'E_BUSY', 'E_CONFLICT'} for result in results))

    def test_credential_fields_never_enter_durable_operation_history(self):
        pid = self.store.create('one', 'trim')['project_id']
        with self.assertRaises(AutoCapcutError) as raised:
            self.store.begin_operation(pid, 'op1', 'official_tool', {'access_token': 'private'}, 0)
        self.assertEqual(raised.exception.code, 'E_SECURITY')
        self.assertEqual(self.store.operations(pid), [])


if __name__ == '__main__':
    unittest.main()
