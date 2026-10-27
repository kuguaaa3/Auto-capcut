import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/auto-capcut/scripts'))

from autocapcut.routes import route_intent


class RouteTests(unittest.TestCase):
    def test_known_control_requests_preserve_project_and_original_instruction(self):
        text = '第三镜缩短1秒，最后音乐小一点，其它别动'
        route = route_intent(text, {'project_id': 'dog'})
        self.assertEqual(route['intent'], 'revise')
        self.assertEqual(route['raw_text'], text)
        self.assertEqual(route['project_id'], 'dog')
        self.assertTrue(route['requires_project'])
        self.assertEqual(route_intent('有什么剪辑风格')['intent'], 'styles')
        self.assertEqual(route_intent('导出 MP4 和国内剪映草稿', 'dog')['formats'], ['mp4', 'jianying'])

    def test_all_control_hints_remain_nonexecuting_and_ambiguous_text_is_left_to_codex(self):
        examples = {
            '停止剪辑': 'pause', '为什么这段放开头': 'explain',
            '把这套剪法保存为 Skill': 'learn', '找更好的卡点skill': 'research',
            '学这条片子的节奏': 'reference', '继续上次狗狗项目': 'resume',
            '直接剪': 'mode', '用我的 pet-healing v2 skill': 'style',
            '把素材剪成30秒': 'new', '随便聊聊': 'unknown',
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                route = route_intent(text)
                self.assertEqual(route['intent'], expected)
                self.assertEqual(route['execution'], 'none')
                self.assertTrue(route['needs_interpretation'])
        self.assertTrue(route_intent('把这套剪法保存为 Skill')['confirmation_required'])
        self.assertEqual(route_intent('先看计划再剪')['execution_preference'], 'plan-first')


if __name__ == '__main__':
    unittest.main()
