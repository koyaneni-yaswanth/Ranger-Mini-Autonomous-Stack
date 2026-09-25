#!/usr/bin/env bash
# JARVIS Brain Cognitive Pipeline Test Suite
import sys
import unittest

ws_path = '/home/yash/ranger_mini_lyrical_2604_ws/install/jarvis_core/lib/python3.14/site-packages'
if ws_path not in sys.path:
    sys.path.insert(0, ws_path)

from jarvis_core.voice_system import VoicePipeline
from jarvis_core.memory_manager import MemoryManager
from jarvis_core.task_planner import HierarchicalTaskPlanner
from jarvis_core.skill_manager import SkillManager
from jarvis_core.fleet_manager import FleetManager

class TestJarvisBrain(unittest.TestCase):
    def setUp(self):
        self.voice = VoicePipeline(wake_word="JARVIS")
        self.memory = MemoryManager()
        self.planner = HierarchicalTaskPlanner(memory_manager=self.memory)
        self.skill_manager = SkillManager()
        self.fleet = FleetManager()

    def test_01_wake_word_parsing(self):
        cmd = "JARVIS, find the red cube and put it on the table."
        has_wake, stripped = self.voice.detect_wake_word(cmd)
        self.assertTrue(has_wake)
        self.assertEqual(stripped, "find the red cube and put it on the table.")

    def test_02_hierarchical_planning(self):
        intent = {
            "action": "pick_and_place",
            "target_object": {"class": "cube", "color": "red"},
            "destination": {"station_id": "target_station"}
        }
        plan, msg = self.planner.plan_task(intent)
        self.assertIsNotNone(plan)
        self.assertEqual(plan.action, "pick_and_place")
        subtask_skills = [st.skill_name for st in plan.subtasks]
        self.assertIn("LocateObject", subtask_skills)
        self.assertIn("Pick", subtask_skills)
        self.assertIn("VerifyGrasp", subtask_skills)
        self.assertIn("Place", subtask_skills)

    def test_03_ambiguity_detection(self):
        # When color is missing and multiple objects could exist
        intent = {
            "action": "pick_and_place",
            "target_object": {"class": "box", "color": None},
            "destination": {"station_id": "target_station"}
        }
        # In a world with multiple boxes
        class MockWorld:
            def find_objects(self, cls):
                return [{"class": "box", "color": "blue"}, {"class": "box", "color": "red"}]
        planner = HierarchicalTaskPlanner(world_model=MockWorld(), memory_manager=self.memory)
        plan, clarify_query = planner.plan_task(intent)
        self.assertIsNone(plan)
        self.assertIn("Which one do you mean?", clarify_query)

    def test_04_capability_gating(self):
        # Manipulator disabled (base-only)
        self.skill_manager.update_capabilities({"manipulation": False, "grasping": False})
        ready, reason = self.skill_manager.check_skill_readiness("Pick")
        self.assertFalse(ready)
        self.assertIn("Manipulation is currently unavailable", reason)

    def test_05_fleet_allocation(self):
        # Pick and place requires manipulation -> allocates Ranger Mini
        alloc_id, reason = self.fleet.allocate_robot_for_task("pick_and_place")
        self.assertEqual(alloc_id, "ranger_mini_01")

        # Heavy payload -> allocates NERO
        alloc_nero, reason_nero = self.fleet.allocate_robot_for_task("patrol", {"heavy_payload": True})
        self.assertEqual(alloc_nero, "nero_01")

if __name__ == '__main__':
    unittest.main()
