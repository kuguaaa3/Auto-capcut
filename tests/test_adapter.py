"""Local native-tool handoff contracts, never real CapCut acceptance."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'skills/auto-capcut/scripts'))
from autocapcut.errors import AutoCapcutError
from autocapcut.adapter import OfficialAdapter


class AdapterContractTests(unittest.TestCase):
    def test_missing_account_cannot_prepare_an_edit(self):
        adapter = OfficialAdapter({'backend': 'capcut_official', 'tools': [], 'connection': 'login_required'})
        with self.assertRaises(AutoCapcutError) as caught:
            adapter.prepare('create_project', {}, operation_id='op-1')
        self.assertEqual(caught.exception.code, 'E_AUTH')
        self.assertEqual(adapter.discover_capabilities()['supports']['project_create'], 'blocked')

    def test_tool_visibility_alone_does_not_prove_editing_support(self):
        adapter = OfficialAdapter({'backend': 'capcut_official', 'connection': 'connected',
            'tools': [{'name': 'fixture_native_edit', 'inputSchema': {'type': 'object'}}],
            'bindings': {'create_project': 'fixture_native_edit'}})
        handoff = adapter.prepare('create_project', {'request': 'user goal'}, operation_id='op-2')
        self.assertEqual(handoff['status'], 'prepared')
        self.assertEqual(handoff['tool'], 'fixture_native_edit')
        self.assertEqual(adapter.discover_capabilities()['supports']['project_create'], 'unknown')

    def test_binding_must_refer_to_a_discovered_tool(self):
        adapter = OfficialAdapter({'backend': 'capcut_official', 'connection': 'connected',
                                    'tools': [], 'bindings': {'export': 'imagined_tool'}})
        with self.assertRaises(AutoCapcutError) as caught:
            adapter.prepare('export', {}, operation_id='op-3')
        self.assertEqual(caught.exception.code, 'E_TOOL')

    def test_simulated_or_failed_results_never_establish_support(self):
        adapter = OfficialAdapter({'backend': 'capcut_official', 'connection': 'connected', 'tools': []})
        with self.assertRaises(AutoCapcutError):
            adapter.record_verification('mp4_export', {'simulation': True, 'status': 'succeeded'})
        self.assertEqual(adapter.discover_capabilities()['supports']['mp4_export'], 'unknown')


if __name__ == '__main__':
    unittest.main()
