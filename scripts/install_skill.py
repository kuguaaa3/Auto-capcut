"""Install this reviewed local Skill without altering an existing installation."""
import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import time
import uuid


def install(destination):
    source = Path(__file__).resolve().parents[1] / 'skills' / 'auto-capcut'
    destination = Path(destination).expanduser().resolve()
    target = destination / 'auto-capcut'
    if target.exists() or target.is_symlink():
        raise ValueError(f'Existing installation preserved: {target}. Choose an empty destination or review an upgrade explicitly.')
    if destination.is_relative_to(source):
        raise ValueError('The installation destination cannot be inside its source bundle.')
    for path in source.rglob('*'):
        attributes = getattr(path.lstat(), 'st_file_attributes', 0)
        if path.is_symlink() or attributes & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0):
            raise ValueError('Skill source must contain regular files and directories, not links.')
    destination.mkdir(parents=True, exist_ok=True)
    staging = destination / ('.auto-capcut-stage-' + uuid.uuid4().hex)
    shutil.copytree(source, staging, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    try:
        # Rename within one filesystem; an existing target is never overwritten.
        if target.exists() or target.is_symlink():
            raise ValueError('Another installation appeared during staging; it was preserved.')
        for attempt in range(3):
            try:
                if target.exists() or target.is_symlink():
                    raise ValueError('Another installation appeared during staging; it was preserved.')
                staging.rename(target)
                break
            except PermissionError as exc:
                if os.name != 'nt' or getattr(exc, 'winerror', None) not in (5, 32, 33) or attempt == 2:
                    raise
                time.sleep(0.1 * (attempt + 1))
    except (OSError, ValueError) as exc:
        raise ValueError(f'Installation incomplete: {exc}. Prior installation is unchanged; staged files retained at {staging}.') from exc
    return {'status': 'installed', 'path': str(target), 'version': '0.1.0',
            'activation': 'Available to Codex on its next skill discovery; official CapCut authorization is separate.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills'
    parser.add_argument('--dest', default=str(default_root))
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    try:
        print(json.dumps(install(args.dest), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
