#!/usr/bin/env python3
import sys
import unittest

ws_path = '/home/yash/ranger_mini_lyrical_2604_ws/install/jarvis_core/lib/python3.14/site-packages'
if ws_path not in sys.path:
    sys.path.insert(0, ws_path)

from jarvis_core.memory_manager import MemoryManager

class TestMemorySystem(unittest.TestCase):
    def setUp(self):
        self.mem = MemoryManager()

    def test_01_short_term_dialogue(self):
        self.mem.short_term.add_turn("USER", "Find red cube")
        self.mem.short_term.add_turn("JARVIS", "Approaching red cube")
        self.assertEqual(len(self.mem.short_term.dialogue_turns), 2)

    def test_02_episodic_recall(self):
        self.mem.episodic.record_episode("task_1", "pick_and_place", "red cube", "target_station", "SUCCESS", 25.4)
        last_loc = self.mem.episodic.query_last_location_of("red cube")
        self.assertEqual(last_loc, "target_station")

    def test_03_semantic_memory(self):
        priors = self.mem.semantic.get_object_priors("cube")
        self.assertIn("dimensions_m", priors)

    def test_04_robot_memory(self):
        self.mem.robot.log_battery(85.0, 25.4)
        self.mem.robot.record_fault("lidar", "Transient timeout")
        self.assertEqual(len(self.mem.robot.fault_events), 1)

if __name__ == '__main__':
    unittest.main()
