"""Read-only local runtime discovery; never accesses credentials."""
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
from datetime import datetime, timezone


def _run_json(command, timeout=40):
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=timeout)
        if result.returncode:
            return None
        return json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None


def inspect_environment(*, check_connection=False, codex_cli=None):
    """Detect installed plugins; connection is unknown unless explicitly checked."""
    cli = codex_cli or shutil.which('codex')
    snapshot = {'backend': 'capcut_official', 'discovered_at': datetime.now(timezone.utc).isoformat(),
                'os': platform.platform(), 'plugin_version': None, 'editor_version': 'unknown',
                'connection': 'unknown', 'tools': [], 'bindings': {}, 'plugins': {},
                'notes': [], 'codex_cli': str(cli) if cli else None}
    if not cli:
        snapshot['notes'].append('Native Codex CLI not found. Use the local desktop host.')
        return snapshot
    for marketplace, key in [('CapCut', 'CapCut@CapCut'), ('mattpocock', 'mattpocock-skills@mattpocock')]:
        inventory = _run_json([str(cli), 'plugin', 'list', '--marketplace', marketplace, '--available', '--json'])
        entries = inventory.get('installed', []) if isinstance(inventory, dict) else []
        entry = next((p for p in entries if p.get('pluginId') == key), None)
        snapshot['plugins'][key] = {k: entry.get(k) for k in ('version', 'enabled', 'installed')} if entry else None
        if marketplace == 'CapCut' and entry:
            snapshot['plugin_version'] = entry.get('version')
            if check_connection and entry.get('enabled'):
                source = entry.get('source', {}).get('path')
                helper = Path(source) / 'skills/mcp-auth/scripts/check-connection.mjs' if source else None
                node = shutil.which('node')
                if helper and helper.is_file() and node:
                    result = _run_json([node, str(helper), '--codex-cli', str(cli)], timeout=60)
                    if isinstance(result, dict) and result.get('server') == 'capcut_creation':
                        snapshot['connection'] = result.get('status', 'unknown')
                else:
                    snapshot['notes'].append('Official connection helper or native Node.js is unavailable.')
    snapshot['notes'].append('Tool schemas must be discovered through the current Codex native tool catalogue.')
    return snapshot
