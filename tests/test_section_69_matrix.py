#!/usr/bin/env python3
"""
PROJECT JARVIS-X: SECTION 69 TEST MATRIX & SECTION 65 FAILURE MODES
Tests all 8 canonical voice commands and safety failure recoveries.
"""
import unittest
import time
from jarvis_core.orchestration.decision_loop import DecisionLoop
from jarvis_core.world_model.world_model import SemanticEntity
from jarvis_core.safety.safety_manager import HumanSafetyZone

class TestSection69Matrix(unittest.TestCase):
    def setUp(self):
        self.jarvis = DecisionLoop(manipulator_enabled=True)

    def test_01_what_do_you_see(self):
        """Test 1: 'JARVIS, what do you see?' -> vision -> world model -> spoken response"""
        resp = self.jarvis.process_utterance("JARVIS, what do you see?")
        self.assertIn("cube", resp.lower())
        self.assertIn("red", resp.lower())
        print(f"\n[TEST 1 PASS] What do you see -> {resp}")

    def test_02_where_are_you(self):
        """Test 2: 'JARVIS, where are you?' -> robot state -> location response"""
        resp = self.jarvis.process_utterance("JARVIS, where are you?")
        self.assertIn("positioned at", resp.lower())
        print(f"[TEST 2 PASS] Where are you -> {resp}")

    def test_03_go_to_table(self):
        """Test 3: 'JARVIS, go to the table.' -> task -> Nav2 -> arrival -> response"""
        resp = self.jarvis.process_utterance("JARVIS, go to the table.")
        self.assertIn("arrived at", resp.lower())
        print(f"[TEST 3 PASS] Go to table -> {resp}")

    def test_04_find_red_cube(self):
        """Test 4: 'JARVIS, find the red cube.' -> search -> detection -> localization -> response"""
        resp = self.jarvis.process_utterance("JARVIS, find the red cube.")
        self.assertIn("task complete", resp.lower())
        print(f"[TEST 4 PASS] Find red cube -> {resp}")

    def test_05_pick_up_red_cube(self):
        """Test 5: 'JARVIS, pick up the red cube.' -> find -> navigate -> grasp -> verify"""
        resp = self.jarvis.process_utterance("JARVIS, pick up the red cube.")
        self.assertIn("task complete", resp.lower())
        # Verify working memory recorded target
        self.assertEqual(self.jarvis.memory.working_memory["last_target_object"]["color"], "red")
        print(f"[TEST 5 PASS] Pick up red cube -> {resp}")

    def test_06_put_it_on_the_table_context_resolution(self):
        """Test 6: 'JARVIS, put it on the table.' -> resolve 'it' -> resolve table -> navigate -> place -> verify"""
        # Seed working memory with prior target
        self.jarvis.memory.update_working_memory("last_target_object", {"class": "cube", "color": "red"})
        resp = self.jarvis.process_utterance("JARVIS, put it on the table.")
        self.assertIn("placed on the table", resp.lower())
        print(f"[TEST 6 PASS] Put it on table (context resolved) -> {resp}")

    def test_07_stop_immediate(self):
        """Test 7: 'JARVIS, stop.' -> safe stop"""
        resp = self.jarvis.process_utterance("JARVIS, stop.")
        self.assertIn("stopping", resp.lower())
        print(f"[TEST 7 PASS] Stop -> {resp}")

    def test_08_go_home_and_charge(self):
        """Test 8: 'JARVIS, go home and charge.' -> navigate -> dock -> verify charging"""
        resp = self.jarvis.process_utterance("JARVIS, go home and charge.")
        self.assertIn("charging", resp.lower())
        print(f"[TEST 8 PASS] Go home and charge -> {resp}")


class TestSection65FailureModes(unittest.TestCase):
    def test_piper_disconnected_rejection(self):
        """Section 19: When Piper is detached, reject manipulation tasks cleanly."""
        jarvis_base_only = DecisionLoop(manipulator_enabled=False)
        resp = jarvis_base_only.process_utterance("JARVIS, pick up the red cube.")
        self.assertIn("manipulator is currently unavailable", resp)
        print(f"[FAILURE TEST 1 PASS] Piper disconnected rejection -> {resp}")

    def test_ambiguity_no_guessing(self):
        """Section 17: When two boxes exist, DO NOT guess; ask for clarification."""
        jarvis = DecisionLoop(manipulator_enabled=True)
        # Add a second red cube at a different location
        jarvis.world_model.update_entity(SemanticEntity(
            entity_id="obj_002",
            entity_class="cube",
            color="red",
            pose={"x": 2.5, "y": 1.0, "z": 0.42},
            confidence=0.92,
            location_description="beside the storage rack"
        ))
        resp = jarvis.process_utterance("JARVIS, pick up the red cube.")
        self.assertIn("Which one do you mean?", resp)
        print(f"[FAILURE TEST 2 PASS] Ambiguity clarification query -> {resp}")

    def test_human_safety_stop_zone(self):
        """Section 36: Human < 1.0m forces immediate motion halt."""
        jarvis = DecisionLoop(manipulator_enabled=True)
        jarvis.safety.set_human_distance(0.8)  # Inside 1.0m critical zone
        self.assertEqual(jarvis.safety.get_safety_zone(), HumanSafetyZone.STOP)
        resp = jarvis.process_utterance("JARVIS, go to the table.")
        self.assertIn("Safety halt", resp)
        print(f"[FAILURE TEST 3 PASS] Human safety stop -> {resp}")

    def test_hardware_estop_interlock(self):
        """Section 34 & 66: Physical E-stop overrides all AI reasoning."""
        jarvis = DecisionLoop(manipulator_enabled=True)
        jarvis.safety.set_e_stop(True)
        resp = jarvis.process_utterance("JARVIS, pick up the red cube.")
        self.assertIn("Safety halt", resp)
        self.assertIn("Emergency Stop", resp)
        print(f"[FAILURE TEST 4 PASS] Hardware E-stop priority -> {resp}")

if __name__ == '__main__':
    unittest.main()
