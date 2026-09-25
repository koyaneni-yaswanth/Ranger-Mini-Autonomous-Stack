#!/usr/bin/env python3
import sys
import unittest
import json

ws_path = '/home/yash/ranger_mini_lyrical_2604_ws/install/jarvis_core/lib/python3.14/site-packages'
if ws_path not in sys.path:
    sys.path.insert(0, ws_path)

# Mock safety rules directly
class MockSafetySupervisor:
    def __init__(self):
        self.estop = False
        self.battery_pct = 85.0

    def evaluate_zone(self, distance_m: float) -> str:
        if distance_m < 1.0:
            return "STOP"
        elif distance_m < 2.0:
            return "CAUTION"
        return "SAFE"

    def can_execute(self, action: str) -> tuple[bool, str]:
        if self.estop:
            return False, "Emergency Stop active."
        if self.battery_pct < 15.0 and action != "dock":
            return False, "Battery critically low."
        return True, "Safe."

class TestSafetyManager(unittest.TestCase):
    def setUp(self):
        self.safety = MockSafetySupervisor()

    def test_01_human_presence_zones(self):
        self.assertEqual(self.safety.evaluate_zone(0.8), "STOP")
        self.assertEqual(self.safety.evaluate_zone(1.5), "CAUTION")
        self.assertEqual(self.safety.evaluate_zone(3.0), "SAFE")

    def test_02_estop_interlock(self):
        self.safety.estop = True
        ok, reason = self.safety.can_execute("pick")
        self.assertFalse(ok)
        self.assertIn("Emergency Stop", reason)

    def test_03_battery_threshold_gating(self):
        self.safety.battery_pct = 10.0
        ok, reason = self.safety.can_execute("pick")
        self.assertFalse(ok)
        self.assertIn("Battery critically low", reason)

        # But docking is permitted!
        ok_dock, _ = self.safety.can_execute("dock")
        self.assertTrue(ok_dock)

if __name__ == '__main__':
    unittest.main()
