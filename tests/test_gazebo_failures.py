import unittest
from jarvis_core.capabilities.capability_manager import CapabilityManager
from jarvis_core.safety.safety_manager import SafetyManager, HumanSafetyZone
from jarvis_core.world_model.world_model import WorldModel, SemanticEntity

class GazeboFailuresTestCase(unittest.TestCase):
    def setUp(self):
        self.cap_mgr = CapabilityManager()
        self.safety_mgr = SafetyManager()
        self.world_model = WorldModel()

    def test_missing_object_detection(self):
        """Verify that searching for a non-existent object yields no candidates, prompting active search."""
        matches = self.world_model.find_objects(color='blue', entity_class='cube')
        self.assertEqual(len(matches), 0, "Non-existent object must return empty candidate list")

    def test_piper_disabled_refuses_manipulation(self):
        """Verify robot rejects pick-and-place if Piper arm is disabled."""
        self.cap_mgr.set_manipulator_enabled(False)
        can_manipulate = self.cap_mgr.is_capable('manipulation')
        self.assertFalse(can_manipulate, "Robot must refuse manipulation when Piper arm is disabled")

    def test_estop_forces_zero_velocity(self):
        """Verify safety supervisor collapses velocity to zero and forbids action upon E-Stop."""
        self.safety_mgr.set_e_stop(True)
        valid, msg = self.safety_mgr.validate_action('move_base', {'vx': 0.5})
        self.assertFalse(valid)
        self.assertIn("SAFETY INTERLOCK", msg)

    def test_human_proximity_stop(self):
        """Verify human entering STOP zone (< 1.0m) forces velocity to 0.0."""
        self.safety_mgr.set_human_distance(0.6)
        self.assertEqual(self.safety_mgr.get_safety_zone(), HumanSafetyZone.STOP)
        clamped_vel = self.safety_mgr.clamp_velocity(0.5)
        self.assertEqual(clamped_vel, 0.0)

    def test_human_proximity_caution(self):
        """Verify human entering CAUTION zone (1.0m - 2.0m) clamps velocity to 50%."""
        self.safety_mgr.set_human_distance(1.5)
        self.assertEqual(self.safety_mgr.get_safety_zone(), HumanSafetyZone.CAUTION)
        clamped_vel = self.safety_mgr.clamp_velocity(0.4)
        self.assertAlmostEqual(clamped_vel, 0.2)

if __name__ == '__main__':
    unittest.main()
