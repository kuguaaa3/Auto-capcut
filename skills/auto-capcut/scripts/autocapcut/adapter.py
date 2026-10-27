"""Bridge between local contracts and tools actually discovered by Codex.

This module prepares native tool handoffs. It does not implement a second editor,
invent official API arguments, or turn a prepared request into editing success.
"""
from copy import deepcopy
from pathlib import Path

from .errors import AutoCapcutError

CAPABILITIES = (
    'connection', 'project_create', 'media_import', 'trim_reorder', 'captions',
    'audio', 'local_revision', 'capcut_project', 'mp4_export', 'jianying_draft',
)


class OfficialAdapter:
    def __init__(self, snapshot: dict):
        if snapshot.get('backend') != 'capcut_official':
            raise AutoCapcutError('E_TOOL', 'Only the official CapCut backend is enabled.')
        self.snapshot = deepcopy(snapshot)
        self.verifications = {}
        for capability, evidence in snapshot.get('verifications', {}).items():
            self.record_verification(capability, evidence)

    def discover_capabilities(self) -> dict:
        result = deepcopy(self.snapshot)
        connected = result.get('connection') == 'connected'
        result['supports'] = {key: 'unknown' if connected else 'blocked' for key in CAPABILITIES}
        if connected:
            result['supports']['connection'] = 'supported'
            for capability, evidence in self.verifications.items():
                result['supports'][capability] = evidence['status']
        result['verifications'] = deepcopy(self.verifications)
        result['notes'] = [*result.get('notes', []),
                           'Tool presence is not operation support. Prepared handoffs are not executed edits.']
        return result

    def prepare(self, operation: str, arguments: dict, *, operation_id: str) -> dict:
        if self.snapshot.get('connection') != 'connected':
            raise AutoCapcutError('E_AUTH', 'CapCut account connection has not been verified.',
                                  'Complete official in-app authorization and rediscover native tools.')
        tool_name = self.snapshot.get('bindings', {}).get(operation)
        tools = {tool['name']: tool for tool in self.snapshot.get('tools', [])}
        if not tool_name or tool_name not in tools:
            raise AutoCapcutError('E_TOOL', 'No discovered native-tool binding is available for this operation.',
                                  'Discover the current official tool schema before preparing this operation.')
        if not isinstance(tools[tool_name].get('inputSchema'), dict):
            raise AutoCapcutError('E_TOOL', 'The current native input schema has not been recorded.')
        if not isinstance(arguments, dict) or not operation_id:
            raise AutoCapcutError('E_APPLY', 'Arguments and a stable operation ID are required.')
        return {'status': 'prepared', 'backend': 'capcut_official', 'operation': operation,
                'operation_id': operation_id, 'tool': tool_name, 'arguments': deepcopy(arguments),
                'input_schema': deepcopy(tools[tool_name].get('inputSchema')),
                'next_action': 'Codex must invoke this actual native tool and preserve its result; no edit has occurred.'}

    def record_verification(self, capability: str, evidence: dict) -> dict:
        """Record explicit real-operation evidence, never infer it from a tool name.

        The trusted Codex caller owns actual tool execution and visual review.
        Merely submitting a JSON receipt does not constitute independent QA.
        """
        if capability not in CAPABILITIES or capability == 'connection':
            raise AutoCapcutError('E_QA', 'Unknown operation capability.')
        if self.snapshot.get('connection') != 'connected':
            raise AutoCapcutError('E_AUTH', 'Connection must be verified before operation evidence is accepted.')
        if not isinstance(evidence, dict) or evidence.get('simulation') is not False:
            raise AutoCapcutError('E_QA', 'Real evidence must explicitly exclude simulation.')
        status = evidence.get('status')
        if status not in ('supported', 'unsupported', 'blocked'):
            raise AutoCapcutError('E_QA', 'Evidence must state supported, unsupported or blocked.')
        for key in ('observed_at', 'details', 'evidence_path'):
            if not isinstance(evidence.get(key), str) or not evidence[key].strip():
                raise AutoCapcutError('E_QA', f'Missing real evidence: {key}.')
        path = Path(evidence['evidence_path'])
        if not path.is_file() or not path.stat().st_size:
            raise AutoCapcutError('E_QA', 'Evidence file is missing or empty.')
        if status == 'supported' and evidence.get('readback_verified') is not True:
            raise AutoCapcutError('E_QA', 'Supported operations require actual readback verification.')
        self.verifications[capability] = deepcopy(evidence)
        return self.discover_capabilities()
