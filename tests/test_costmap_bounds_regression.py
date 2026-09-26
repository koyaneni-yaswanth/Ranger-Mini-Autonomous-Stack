#!/usr/bin/env python3
"""
PROJECT JARVIS-X: AUTOMATED REGRESSION TEST SUITE (SECTIONS 20 & 77)
Tests:
1. Costmap Voxel Boundary vs Sensor Origin (Section 20)
   Calculates sensor_origin, costmap_min, costmap_max.
   Validates that the original condition (z_sensor ≈ 0.83, z_max ≈ 0.80) fails,
   and verifies that the updated configuration (z_voxels=32, z_max=1.60m) passes
   with adequate engineering margin.
2. Module Import Regression: verifies jarvis_core standalone import.
"""

import unittest
import yaml
import os

class TestCostmapBoundsRegression(unittest.TestCase):
    def setUp(self):
        self.nav2_params_file = "/home/yash/ranger_mini_lyrical_2604_ws/src/ranger_navigation/config/nav2_params.yaml"
        # Sensor origin Z calculation from URDF:
        # Base to top deck: 0.460m
        # Mast mount offset: 0.015m
        # Lidar joint on mast: 0.356m
        # Total lidar Z in base_footprint frame:
        self.sensor_origin_z = 0.460 + 0.015 + 0.356  # 0.831 m

    def test_reproduce_original_failure_condition(self):
        """Simulate the original configuration (z_voxels=16) and assert it fails."""
        origin_z = 0.0
        z_resolution = 0.05
        original_z_voxels = 16
        original_costmap_max_z = origin_z + (z_resolution * original_z_voxels)  # 0.80 m
        
        # Verify that original condition detected sensor out of bounds
        is_in_bounds = origin_z <= self.sensor_origin_z <= original_costmap_max_z
        self.assertFalse(
            is_in_bounds,
            f"Original condition must be detected as OUT OF BOUNDS: sensor_z={self.sensor_origin_z:.3f}m > max_z={original_costmap_max_z:.2f}m"
        )
        print(f"\n[REGRESSION REPRODUCED] Original z_voxels=16 produced max_z={original_costmap_max_z:.2f}m, correctly rejecting sensor at z={self.sensor_origin_z:.3f}m")

    def test_current_costmap_bounds_enclose_sensor_origin(self):
        """Verify the active nav2_params.yaml encloses the sensor origin with >= 0.50m margin."""
        with open(self.nav2_params_file, "r") as f:
            params = yaml.safe_load(f)

        voxel_params = params["local_costmap"]["local_costmap"]["ros__parameters"]["voxel_layer"]
        origin_z = voxel_params.get("origin_z", 0.0)
        z_res = voxel_params.get("z_resolution", 0.05)
        z_vox = voxel_params.get("z_voxels", 16)
        
        costmap_min_z = origin_z
        costmap_max_z = origin_z + (z_res * z_vox)
        margin = costmap_max_z - self.sensor_origin_z

        print(f"\n[COSTMAP GEOMETRY AUDIT]")
        print(f"  Sensor Origin Z:   {self.sensor_origin_z:.3f} m")
        print(f"  Costmap Min Z:     {costmap_min_z:.3f} m")
        print(f"  Costmap Max Z:     {costmap_max_z:.3f} m (z_resolution={z_res}m, z_voxels={z_vox})")
        print(f"  Headroom Margin:   {margin:.3f} m")

        self.assertGreaterEqual(
            self.sensor_origin_z, costmap_min_z,
            f"Sensor origin ({self.sensor_origin_z}m) is below costmap min ({costmap_min_z}m)"
        )
        self.assertLessEqual(
            self.sensor_origin_z, costmap_max_z,
            f"Sensor origin ({self.sensor_origin_z}m) exceeds costmap max ({costmap_max_z}m)"
        )
        self.assertGreaterEqual(
            margin, 0.50,
            f"Engineering headroom margin ({margin:.3f}m) should be at least 0.50m"
        )
        print(f"[PASS] Sensor origin is safely enclosed within costmap vertical bounds.")

    def test_jarvis_core_import_regression(self):
        """Verify jarvis_core can be imported without import errors."""
        import jarvis_core
        self.assertTrue(hasattr(jarvis_core, "DecisionLoop"))
        self.assertTrue(hasattr(jarvis_core, "JarvisEvent"))
        self.assertTrue(hasattr(jarvis_core, "SafetyManager"))
        print(f"[PASS] jarvis_core successfully imported from {jarvis_core.__file__}")

if __name__ == '__main__':
    unittest.main()
