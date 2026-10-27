"""Versioned editorial style data; imported instructions are never executed."""

import hashlib
import json
import os
import re
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from .errors import AutoCapcutError


class StyleRegistry:
    def __init__(self, skill_root, workspace=None):
        self.skill_root = Path(skill_root).resolve()
        self.workspace = Path(workspace).resolve() if workspace else None

    def list(self, query=''):
        result = [self._read_json(p, self.skill_root) for p in sorted((self.skill_root / 'styles').glob('*/style.json'))]
        if self.workspace:
            for category in ('custom-skills', 'learned-skills'):
                for pointer in sorted((self.workspace / category).glob('*/active.json')):
                    self._validate_id(pointer.parent.name)
                    active = self._read_json(pointer, self.workspace).get('version')
                    self._version_key(active)
                    metadata = self._read_json(pointer.parent / 'versions' / active / 'style.json', self.workspace)
                    expected_source = 'learned' if category == 'learned-skills' else 'custom'
                    if metadata.get('id') != pointer.parent.name or metadata.get('version') != active or metadata.get('source') != expected_source:
                        raise AutoCapcutError('E_STYLE', '风格目录、版本和来源不一致。', '检查用户风格库的版本指针。')
                    result.append(metadata)
        seen = set()
        for style in result:
            self._validate(style)
            identity = style['id'].casefold()
            if identity in seen:
                raise AutoCapcutError('E_STYLE', '风格库存在同名冲突。', '为用户风格选择唯一名称。')
            seen.add(identity)
        return [s for s in result if query.casefold() in (s['id'] + ' ' + s['name'] + ' ' + s['description']).casefold()]

    def load(self, style_id, version=None):
        self._validate_id(style_id)
        if version is not None:
            self._version_key(version)
        for style in self.list():
            if style['id'] == style_id:
                directory = self.skill_root / 'styles' / style_id
                if style['source'] != 'builtin':
                    category = 'learned-skills' if style['source'] == 'learned' else 'custom-skills'
                    directory = self.workspace / category / style_id / 'versions' / (version or style['version'])
                    if not (directory / 'style.json').is_file():
                        break
                    style = self._read_json(directory / 'style.json', self.workspace)
                    if style.get('id') != style_id or style.get('version') != (version or style['version']):
                        raise AutoCapcutError('E_STYLE', '风格存储与请求版本不一致。', '检查风格版本目录。')
                    self._validate(style)
                elif version is not None and style['version'] != version:
                    break
                try:
                    text_path = directory / 'SKILL.md'
                    self._safe_file(text_path, self.skill_root if style['source'] == 'builtin' else self.workspace)
                    style['skill_text'] = text_path.read_text(encoding='utf-8')
                except (OSError, UnicodeError) as exc:
                    raise AutoCapcutError('E_STYLE', '无法读取风格 SKILL.md。', '检查风格版本是否完整。') from exc
                if style['source'] != 'builtin':
                    self._screen_text(style['skill_text'])
                return style
        raise AutoCapcutError('E_STYLE', f'风格或版本不存在: {style_id}', '列出风格，或提供有效的自定义 Skill。')

    def select(self, explicit=None, current=None, recommendation=None):
        choice = explicit if explicit is not None else current if current is not None else recommendation
        if choice is None:
            raise AutoCapcutError('E_STYLE', '尚未选择主风格。', '推荐一个与素材目标相符的主风格。')
        if isinstance(choice, dict):
            return self.load(choice['id'], choice.get('version'))
        return self.load(choice)

    def validate_review(self, style_id, observations):
        """Check recorded editorial evidence, without asserting pixels or tools."""
        style = self.load(style_id)
        checks = []
        for gate in style.get('review_gates', ['rules_followed', 'content_evidenced']):
            record = observations.get(gate) if isinstance(observations, dict) else None
            valid = isinstance(record, dict) and type(record.get('passed')) is bool and isinstance(record.get('evidence'), str) and record['evidence'].strip()
            checks.append({'id': gate, 'status': ('pass' if record['passed'] else 'fail') if valid else 'missing'})
        statuses = {check['status'] for check in checks}
        return {'style_id': style_id, 'status': 'needs_review' if 'missing' in statuses else 'fail' if 'fail' in statuses else 'pass',
                'scope': 'recorded_editorial_review', 'real_media_verified': False, 'checks': checks}

    def propose(self, style_id, name, rules, *, origin=None, quality_rules=None):
        self._validate_id(style_id)
        if not isinstance(rules, list) or not 3 <= len(rules) <= 8 or not all(isinstance(r, str) and r.strip() for r in rules):
            raise AutoCapcutError('E_STYLE', '风格提案需要 3–8 条可迁移规则。', '保留叙事、节奏、声音或字幕规律。')
        style = {
            'schema_version': '1.0', 'id': style_id, 'name': name,
            'description': name, 'source': 'learned', 'version': '1.0.0',
            'compatibility': ['capcut_official'], 'trust': 'user-approved-knowledge',
            'status': 'proposed', 'decision_rules': list(rules),
            'quality_rules': quality_rules or ['依据真实素材核验叙事、声音与字幕。'],
            'suitable_for': '符合这些规则且有真实证据的素材',
            'not_suitable_for': '缺少所需动作或声音证据的素材',
            'inputs': ['真实素材证据', '用户目标'],
            'default_behavior': '遵从用户要求，按素材证据决定节奏。',
            'required_capabilities': ['material-analysis', 'qa'],
            'fallback': '能力不足则报告 blocked，保留旧版。',
            'origin': origin or [{'type': 'user-rules'}],
            'license': 'User supplied; personal noncommercial use only',
            'approved_at': None,
        }
        self._validate(style)
        return style

    def save(self, proposal, *, approved=False):
        if approved is not True:
            raise AutoCapcutError('E_APPROVAL', '保存风格需要用户明确确认。', '先展示名称和可迁移规则，再确认入库。')
        if self.workspace is None:
            raise AutoCapcutError('E_STYLE', '未指定用户工作区。', '指定项目工作区以保存个人风格。')
        style = json.loads(json.dumps(proposal, ensure_ascii=False))
        self._validate(style)
        style['source'] = 'learned'
        style['status'] = 'draft'
        style['approved_at'] = datetime.now(timezone.utc).isoformat()
        style['version'] = '1.0.0'
        return self._persist(style)

    def rollback(self, style_id, version, *, approved=False):
        if approved is not True:
            raise AutoCapcutError('E_APPROVAL', '回退用户风格需要明确确认。', '确认要恢复的版本。')
        style = self.load(style_id, version)
        if style['source'] == 'builtin':
            raise AutoCapcutError('E_STYLE', '内置风格不可改写。', '另存为个人风格。')
        category = 'learned-skills' if style['source'] == 'learned' else 'custom-skills'
        with self._lock():
            pointer = self.workspace / category / style_id / 'active.json'
            self._safe_destination(pointer)
            self._atomic_json(pointer, {'version': version})
        return self.load(style_id)

    def import_style(self, directory, *, approved=False):
        """Import declared editorial data only; never copy or launch code."""
        if approved is not True:
            raise AutoCapcutError('E_APPROVAL', '导入风格需要用户明确确认。', '先检查来源、规则与许可。')
        if self.workspace is None:
            raise AutoCapcutError('E_STYLE', '未指定用户工作区。', '指定工作区再导入。')
        directory = Path(directory)
        metadata_path, text_path = directory / 'style.json', directory / 'SKILL.md'
        try:
            paths = [text_path] + ([metadata_path] if metadata_path.exists() else [])
            if directory.is_symlink() or any(p.is_symlink() or not p.is_file() or p.stat().st_size > 524288 for p in paths):
                raise AutoCapcutError('E_STYLE_UNTRUSTED', '导入文件必须是普通的有界文本文件。', '提供 style.json 和 SKILL.md 的本地普通副本。')
            metadata = json.loads(metadata_path.read_text(encoding='utf-8')) if metadata_path.exists() else None
            text = text_path.read_text(encoding='utf-8')
        except (OSError, ValueError) as exc:
            raise AutoCapcutError('E_STYLE', '无法读取风格合同文件。', '检查 style.json 与 SKILL.md 的 UTF-8 格式。') from exc
        self._screen_text(text)
        frontmatter = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.DOTALL)
        if frontmatter is None:
            raise AutoCapcutError('E_STYLE', 'SKILL.md 缺少前置元信息。', '添加 name 和 description。')
        declared_name = re.search(r'^name:\s*([^\r\n]+)', frontmatter[1], re.MULTILINE)
        description = re.search(r'^description:\s*([^\r\n]+)', frontmatter[1], re.MULTILINE)
        if metadata is None and declared_name is not None and description is not None:
            section = re.search(r'^##\s+(?:决策规则|Decision rules)\s*\r?\n(.*?)(?=^##\s|\Z)', text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            rules = re.findall(r'^[-*]\s+(.+)$', section[1], re.MULTILINE) if section else []
            summary = description[1].strip().strip('"\'')
            if summary in ('>', '|'):
                raise AutoCapcutError('E_STYLE', '独立 Skill 的 description 需要单行摘要。', '改成单行字符串，或提供完整 style.json 合同。')
            metadata = self.propose(declared_name[1].strip().strip('"\''), summary, rules)
            declared_version = re.search(r'^(?:  )?version:\s*([^\r\n]+)', frontmatter[1], re.MULTILINE)
            if declared_version:
                metadata['version'] = declared_version[1].strip().strip('"\'')
        if not isinstance(metadata, dict) or declared_name is None or description is None or declared_name[1].strip().strip('"\'') != metadata.get('id'):
            raise AutoCapcutError('E_STYLE', 'SKILL.md 与 style.json 标识不一致。', '修正 name、description 和 id。')
        metadata['source'], metadata['trust'], metadata['status'] = 'custom', 'untrusted-data', 'draft'
        metadata['approved_at'] = datetime.now(timezone.utc).isoformat()
        self._validate(metadata)
        metadata['origin'] = metadata['origin'] + [{'type': 'imported-data', 'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(), 'license': metadata.get('license', '')}]
        self._validate(metadata)
        return self._persist(metadata)

    def _persist(self, style):
        category = 'learned-skills' if style['source'] == 'learned' else 'custom-skills'
        with self._lock():
            for existing in self.list():
                if existing['id'] == style['id'] and existing['source'] != style['source']:
                    raise AutoCapcutError('E_STYLE', '不能覆盖其他来源的风格。', '为用户风格选择新的 ID。')
                if existing['name'].casefold() == style['name'].casefold() and existing['id'] != style['id']:
                    raise AutoCapcutError('E_STYLE', '风格显示名称与已有风格冲突。', '选择可区分的名称。')
            versions = self.workspace / category / style['id'] / 'versions'
            self._safe_destination(versions)
            prior = sorted((p.name for p in versions.iterdir()), key=self._version_key) if versions.exists() else []
            if prior:
                major, minor, patch = self._version_key(prior[-1])
                style['version'] = f'{major}.{minor}.{patch + 1}'
            target = versions / style['version']
            target.mkdir(parents=True, exist_ok=False)
            self._atomic_json(target / 'style.json', style)
            self._atomic_text(target / 'SKILL.md', self._skill_text(style))
            self._atomic_json(versions.parent / 'active.json', {'version': style['version']})
        return self.load(style['id'])

    def _safe_destination(self, path):
        if not path.resolve().is_relative_to(self.workspace):
            raise AutoCapcutError('E_STYLE_UNTRUSTED', '风格写入目标超出用户工作区。', '检查目录链接；不要改写外部文件。')

    @staticmethod
    def _version_key(version):
        if not isinstance(version, str) or re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version) is None:
            raise AutoCapcutError('E_STYLE', '版本必须是 major.minor.patch。', '使用如 1.0.0 的版本。')
        return tuple(map(int, version.split('.')))

    @staticmethod
    def _validate_id(style_id):
        reserved = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)), *(f'lpt{i}' for i in range(1, 10))}
        if not isinstance(style_id, str) or re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', style_id) is None or len(style_id) > 64 or style_id in reserved:
            raise AutoCapcutError('E_STYLE', '风格 ID 必须是安全的小写英文短横线名称。', '例如 gentle-reversal；不能使用路径或系统保留名。')

    @classmethod
    def _validate(cls, style):
        if not isinstance(style, dict):
            raise AutoCapcutError('E_STYLE', '风格必须是结构化对象。', '检查 style.json。')
        cls._validate_id(style.get('id'))
        cls._version_key(style.get('version'))
        if style.get('schema_version') != '1.0':
            raise AutoCapcutError('E_STYLE', '风格合同版本不支持。', '使用 schema_version 1.0。')
        allowed = {'schema_version', 'id', 'name', 'description', 'source', 'version', 'compatibility', 'trust', 'status', 'approved_at', 'suitable_for', 'not_suitable_for', 'inputs', 'default_behavior', 'decision_rules', 'required_capabilities', 'quality_rules', 'review_gates', 'anti_patterns', 'fallback', 'origin', 'license'}
        if set(style) - allowed:
            raise AutoCapcutError('E_STYLE_UNTRUSTED', '风格包含未支持的元数据字段。', '只保留声明的剪辑规则合同；不要携带执行配置。')
        for key in ('name', 'description', 'suitable_for', 'not_suitable_for', 'default_behavior', 'fallback', 'license'):
            if not isinstance(style.get(key), str) or not style[key].strip():
                raise AutoCapcutError('E_STYLE', f'风格字段缺失: {key}', '补全风格合同。')
        for key in ('inputs', 'decision_rules', 'quality_rules', 'required_capabilities', 'compatibility'):
            if not isinstance(style.get(key), list) or not style[key] or not all(isinstance(x, str) and x.strip() for x in style[key]):
                raise AutoCapcutError('E_STYLE', f'风格列表无效: {key}', '补全非空规则与能力列表。')
        if style.get('source') not in ('builtin', 'learned', 'custom') or not style.get('origin'):
            raise AutoCapcutError('E_STYLE', '风格缺少有效来源。', '记录来源和许可；不执行来源代码。')
        if style['source'] != 'builtin' and not 3 <= len(style['decision_rules']) <= 8:
            raise AutoCapcutError('E_STYLE', '用户风格需要 3–8 条可迁移规则。', '压缩为明确可复用的决策。')
        if style['compatibility'] != ['capcut_official']:
            raise AutoCapcutError('E_STYLE', '风格没有声明官方 CapCut 适配。', '先适配知识规则，不要引入另一编辑引擎。')
        for key in ('anti_patterns', 'review_gates'):
            if key in style and (not isinstance(style[key], list) or not style[key] or not all(isinstance(x, str) and x.strip() for x in style[key])):
                raise AutoCapcutError('E_STYLE', f'风格字段无效: {key}', '使用非空字符串列表。')
        if any(re.fullmatch(r'[a-z][a-z0-9_]{0,63}', gate) is None for gate in style.get('review_gates', [])):
            raise AutoCapcutError('E_STYLE', '风格审查项 ID 无效。', '使用安全的小写标识。')
        if not isinstance(style['origin'], list):
            raise AutoCapcutError('E_STYLE', '风格来源必须是列表。', '记录每项来源及许可。')
        for origin in style['origin']:
            if not isinstance(origin, dict) or not origin:
                raise AutoCapcutError('E_STYLE', '风格来源条目无效。', '使用来源对象。')
            if set(origin) - {'name', 'url', 'blob_sha', 'license', 'license_path', 'trust', 'type', 'sha256', 'analysis_id', 'project_id', 'revision', 'evidence_id'}:
                raise AutoCapcutError('E_STYLE_UNTRUSTED', '来源包含未支持字段。', '仅记录公开出处、哈希、许可和不含私人信息的证据标识。')
            for key, value in origin.items():
                if key == 'license_path' and style['source'] == 'builtin':
                    continue
                if key == 'url':
                    parsed = urlsplit(value) if isinstance(value, str) else None
                    if parsed is None or parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
                        raise AutoCapcutError('E_STYLE_UNTRUSTED', '来源 URL 必须是无凭据的 HTTPS 公开地址。', '去除查询参数、授权信息和私人链接。')
                    continue
                if isinstance(value, str):
                    cls._screen_text(value)
                elif not isinstance(value, int):
                    raise AutoCapcutError('E_STYLE', '风格来源仅接受字符串或版本数字。', '移除嵌套指令。')
        if style.get('trust') not in ('reviewed-knowledge', 'user-approved-knowledge', 'untrusted-data'):
            raise AutoCapcutError('E_STYLE', '风格信任标记无效。', '将导入风格标记为 untrusted-data。')
        if style.get('status') not in ('draft', 'proposed'):
            raise AutoCapcutError('E_STYLE', '本地风格尚不能宣称真机 validated。', '在真实样片和编辑工程验收后单独记录证据。')
        # This is a conservative screening gate, not a code sandbox. No style is
        # ever evaluated or executed, including styles that pass this check.
        content = '\n'.join(style[k] if isinstance(style[k], str) else '\n'.join(style[k])
                            for k in ('name', 'description', 'suitable_for', 'not_suitable_for', 'default_behavior', 'fallback', 'inputs', 'decision_rules', 'quality_rules', 'required_capabilities', 'license'))
        content += '\n' + '\n'.join(style.get('anti_patterns', []))
        cls._screen_text(content)

    @staticmethod
    def _screen_text(content):
        urls = re.findall(r'https://[^\s<>]+', content)
        for url in urls:
            parsed = urlsplit(url)
            if parsed.username or parsed.password or parsed.query:
                raise AutoCapcutError('E_STYLE_UNTRUSTED', '风格含私人或带授权参数的地址。', '只保留公开且无需凭据的来源链接。')
        path_content = re.sub(r'https://[^\s<>]+', '', content)
        unsafe_path = r'[a-zA-Z]:[\\/]|\\\\[^\s]+|\.\.[\\/]|(?<![:\w])/(?:[\w.-]+/)+'
        unsafe = (r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?\b|source_(?:in|out)_us',
                  r'ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions|忽略.{0,8}(?:指令|规则)',
                  r'\b(?:powershell|cmd\.exe|subprocess|os\.system|invoke-expression|curl|wget|npx)\b|\b(?:pip|npm)\s+install|\b(?:exec|eval)\s*\(',
                  r'api[_-]?key|access[_-]?token|credentials|\.codex|\.ssh|读取.{0,6}(?:凭据|密钥)')
        if re.search(unsafe_path, path_content) or any(re.search(pattern, content, re.IGNORECASE) for pattern in unsafe):
            raise AutoCapcutError('E_STYLE_UNTRUSTED', '风格包含路径、一次性时间码或越权执行/凭据指令。', '仅保留可迁移剪辑规则；人工审查并删除私人信息和可执行指令。')

    @staticmethod
    def _safe_file(path, root):
        if not path.resolve().is_relative_to(root.resolve()) or path.is_symlink() or not path.is_file() or path.stat().st_size > 524288:
            raise AutoCapcutError('E_STYLE_UNTRUSTED', '风格文件路径越界或不是普通有界文件。', '检查风格目录和符号链接。')

    @classmethod
    def _read_json(cls, path, root):
        cls._safe_file(path, root)
        try:
            value = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(value, dict):
                raise ValueError('not an object')
            return value
        except (OSError, ValueError, UnicodeError) as exc:
            raise AutoCapcutError('E_STYLE', '风格元数据损坏或不可读。', '恢复已保留的风格版本；不要覆盖原文件。') from exc

    @staticmethod
    def _skill_text(style):
        return ('---\nname: ' + style['id'] + '\ndescription: ' + json.dumps(style['description'], ensure_ascii=False)
                + '\nmetadata:\n  version: ' + style['version'] + '\n---\n\n# ' + style['name']
                + '\n\n状态：draft；未通过真实样片验证。\n\n## 适用\n' + style['suitable_for']
                + '\n\n## 不适用\n' + style['not_suitable_for']
                + '\n\n## 输入\n' + '\n'.join('- ' + r for r in style['inputs'])
                + '\n\n## 默认行为\n' + style['default_behavior']
                + '\n\n## 决策规则\n' + '\n'.join('- ' + r for r in style['decision_rules'])
                + '\n\n## 必要能力\n' + ', '.join(style['required_capabilities'])
                + '\n\n## 质量门禁\n' + '\n'.join('- ' + r for r in style['quality_rules'])
                + '\n\n## 失败退化\n' + style['fallback']
                + '\n\n## 来源与版本\n' + json.dumps(style['origin'], ensure_ascii=False) + '\n')

    @contextmanager
    def _lock(self):
        self.workspace.mkdir(parents=True, exist_ok=True)
        lock = self.workspace / '.style-write.lock'
        try:
            handle = lock.open('x', encoding='utf-8')
        except FileExistsError as exc:
            raise AutoCapcutError('E_BUSY', '风格库正在写入，或上次写入被中断。', '确认没有写入进程后移除工作区的 .style-write.lock。') from exc
        try:
            handle.write(str(os.getpid()))
            handle.close()
            yield
        finally:
            handle.close()
            lock.unlink()

    @staticmethod
    def _atomic_json(path, data):
        StyleRegistry._atomic_text(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    @staticmethod
    def _atomic_text(path, text):
        temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
        try:
            with temporary.open('x', encoding='utf-8') as file:
                file.write(text)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
