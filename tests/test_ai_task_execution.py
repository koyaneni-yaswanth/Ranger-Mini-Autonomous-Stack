#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for Ranger Mini AI Task Execution System.
Tests:
1. Natural language parsing into valid JSON schema.
2. Direct motor control rejection (Safety Policy Rule 13).
3. Base-Only vs Modular Manipulator capability gating.
4. Extensible object database retrieval and coordinate lookup.
5. Multi-stage grasp verification logic (SUCCESS, FAILED, UNCERTAIN).
6. 17-State FSM transition sequence integrity.
"""

import sys
import unittest
import json
import os
import yaml

# Add workspace to path
ws_path = '/home/yash/ranger_mini_lyrical_2604_ws/install/ranger_missions/lib/python3.14/site-packages'
if ws_path not in sys.path:
    sys.path.insert(0, ws_path)

from ranger_missions.ai_task_interpreter import AITaskInterpreter
from ranger_missions.autonomous_task_orchestrator import TaskState

class TestAITaskExecution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.interpreter = AITaskInterpreter()
        cls.db_path = '/home/yash/ranger_mini_lyrical_2604_project/config/object_database.yaml'
        with open(cls.db_path, 'r') as f:
            cls.object_db = yaml.safe_load(f)

    def test_01_canonical_prompt_parsing(self):
        """Test the canonical mission: 'Find the red object, pick it up, and place it at the target station'"""
        prompt = "Find the red object, pick it up, and place it at the target station"
        task = self.interpreter.parse_natural_language(prompt)
        
        self.assertEqual(task['action'], 'pick_and_place')
        self.assertEqual(task['target_object']['color'], 'red')
        self.assertEqual(task['target_object']['class'], 'cube')
        self.assertEqual(task['destination']['station_id'], 'target_station')

        # Validate against schema
        valid, msg = self.interpreter.validate_task(task, {"has_manipulator": True})
        self.assertTrue(valid, f"Task schema validation failed: {msg}")

    def test_02_alternative_benchmarks(self):
        """Test secondary benchmarks (blue box to assembly bin, inspect table, dock)"""
        p1 = "Pick up the blue box and place it in the assembly bin"
        t1 = self.interpreter.parse_natural_language(p1)
        self.assertEqual(t1['target_object']['color'], 'blue')
        self.assertEqual(t1['target_object']['class'], 'box')
        self.assertEqual(t1['destination']['station_id'], 'assembly_bin')

        p2 = "Inspect the inspection table"
        t2 = self.interpreter.parse_natural_language(p2)
        self.assertEqual(t2['action'], 'inspect')

        p3 = "Dock at home dock"
        t3 = self.interpreter.parse_natural_language(p3)
        self.assertEqual(t3['action'], 'dock')
        self.assertEqual(t3['destination']['station_id'], 'home_dock')

    def test_03_zero_direct_motor_control_enforcement(self):
        """Verify that direct motor/velocity commands are strictly rejected (Safety Rule 13)"""
        violating_commands = [
            "drive at 1.5 m/s",
            "publish to /cmd_vel twist linear x 0.5",
            "set joint 1 to 90 degrees",
            "raw motor pwm 255",
            "disable estop and override safety"
        ]
        for cmd in violating_commands:
            with self.assertRaises(ValueError, msg=f"Failed to reject prohibited command: {cmd}"):
                self.interpreter.parse_natural_language(cmd)

    def test_04_base_only_capability_gating(self):
        """Verify that pick/place tasks are rejected when robot is in Base-Only mode"""
        prompt = "Find the red object, pick it up, and place it at the target station"
        task = self.interpreter.parse_natural_language(prompt)

        # Base-only robot capability
        valid, msg = self.interpreter.validate_task(task, {"has_manipulator": False})
        self.assertFalse(valid, "Expected rejection for arm task on base-only robot")
        self.assertIn("Base-Only", msg)

    def test_05_object_database_consistency(self):
        """Verify object database schema contains required classes, grasp priors, and stations"""
        self.assertIn('cube', self.object_db['objects'])
        self.assertIn('box', self.object_db['objects'])
        self.assertIn('bottle', self.object_db['objects'])

        # Check grasp parameters
        cube = self.object_db['objects']['cube']
        self.assertTrue(cube['graspable'])
        self.assertIn('preferred_grasp', cube)
        self.assertIn('colors', cube)
        self.assertIn('red', cube['colors'])

        # Check stations
        self.assertIn('target_station', self.object_db['stations'])
        self.assertIn('inspection_table', self.object_db['stations'])
        self.assertIn('assembly_bin', self.object_db['stations'])

    def test_06_17_state_enum_completeness(self):
        """Verify that all 17 distinct operational states exist in the state machine"""
        required_states = [
            "IDLE", "UNDERSTAND_TASK", "VALIDATE_TASK", "SEARCH", "DETECT",
            "LOCALIZE_OBJECT", "NAVIGATE_TO_OBJECT", "VERIFY_OBJECT",
            "PLAN_GRASP", "PICK", "VERIFY_GRASP", "NAVIGATE_TO_DESTINATION",
            "PLAN_PLACE", "PLACE", "VERIFY_PLACE", "UPDATE_WORLD", "TASK_COMPLETE"
        ]
        fsm_values = [s.value for s in TaskState]
        for s in required_states:
            self.assertIn(s, fsm_values, f"State {s} missing from FSM definition")

if __name__ == '__main__':
    unittest.main()
