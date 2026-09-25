#!/usr/bin/env python3
import sys
import unittest

ws_path = '/home/yash/ranger_mini_lyrical_2604_ws/install/jarvis_core/lib/python3.14/site-packages'
if ws_path not in sys.path:
    sys.path.insert(0, ws_path)

from jarvis_core.voice_system import VoicePipeline

class TestVoiceSystem(unittest.TestCase):
    def setUp(self):
        self.voice = VoicePipeline(wake_word="JARVIS")

    def test_01_wake_word_case_insensitivity(self):
        cases = [
            ("JARVIS, stop", True, "stop"),
            ("jarvis, come here", True, "come here"),
            ("Hey JARVIS: pick up the cube", True, "pick up the cube"),
            ("hello robot", False, "hello robot")
        ]
        for inp, exp_wake, exp_cmd in cases:
            has_wake, cmd = self.voice.detect_wake_word(inp)
            self.assertEqual(has_wake, exp_wake)
            if exp_wake:
                self.assertIn(exp_cmd, cmd)

    def test_02_tts_formatting(self):
        res = self.voice.format_tts_response("Task completed successfully")
        self.assertTrue(res.endswith('.'))

if __name__ == '__main__':
    unittest.main()
