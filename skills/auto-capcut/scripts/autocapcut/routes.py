"""Conservative control-command hints for Codex, never a replacement for understanding.

The complete original instruction is retained. Only recognizable control requests
are classified; Codex must interpret goals, named styles and compound requests.
No result here executes a tool, grants upload permission, or confirms Skill saving.
"""

from __future__ import annotations

import re

from .errors import AutoCapcutError


_RULES = (
    ('pause', r'^(?:停止|暂停|停下)(?:$|[，。！!\s]|剪辑|编辑|操作|项目)|^(?:stop|pause)\b'),
    ('explain', r'为什么|为何|why\b|explain\b'),
    ('learn', r'保存.*(?:skill|技能)|存.*(?:skill|技能)|剪法存起来|save.*skill'),
    ('research', r'(?:找|搜索|研究|寻找).*(?:skill|技能)|research.*skill|find.*skill'),
    ('reference', r'参考.*(?:节奏|风格|视频)|学.*(?:片子|视频|节奏)|learn.*(?:reference|style)'),
    ('styles', r'有什么.*(?:风格|skill|技能)|(?:列出|查看|展示|有哪些).*(?:风格|skill|技能)|list.*styles'),
    ('export', r'导出|要.*(?:mp4|草稿|工程)|export\b'),
    ('resume', r'继续|恢复.*项目|resume\b|continue\b'),
    ('mode', r'直接剪|先看计划|先.*计划.*再剪|just.*edit|plan.*first'),
    ('style', r'^(?:用|使用|采用|换成|切换).*(?:skill|技能|风格|治愈|反转|pet-healing)|use.*style'),
    ('revise', r'第[一二三四五六七八九十\d]+(?:段|镜)|缩短|音乐.*(?:小|低)|改.*字幕|修改.*(?:剪辑|上一版)|revise\b|shorten\b'),
    ('new', r'剪成|剪辑.*(?:文件夹|素材)|把.*(?:视频|素材).*剪|new.*(?:edit|project)'),
)


def route_intent(text: str, current_project: dict | str | None = None) -> dict:
    if not isinstance(text, str) or not text.strip():
        raise AutoCapcutError('E_INPUT', 'An editing request or control command is required.')
    project_id = current_project.get('project_id') if isinstance(current_project, dict) else current_project
    intent = next((name for name, pattern in _RULES if re.search(pattern, text, re.I)), 'unknown')
    requires_project = intent in {'revise', 'export', 'learn', 'pause', 'explain'}
    result = {'intent': intent, 'raw_text': text, 'project_id': project_id,
              'requires_project': requires_project,
              'needs_interpretation': True,
              'needs_project_selection': requires_project and not project_id,
              'confirmation_required': intent == 'learn',
              'execution': 'none'}
    if intent == 'export':
        result['formats'] = [name for name, pattern in (
            ('mp4', r'mp4|视频'), ('capcut', r'capcut'), ('jianying', r'剪映'))
            if re.search(pattern, text, re.I)]
    if intent == 'mode':
        result['execution_preference'] = 'plan-first' if re.search(r'先.*计划|plan.*first', text, re.I) else 'direct'
    return result
