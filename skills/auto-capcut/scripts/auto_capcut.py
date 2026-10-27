#!/usr/bin/env python3
"""One-shot local command entry for the Codex Auto-capcut Skill."""
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from autocapcut.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
