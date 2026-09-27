#!/usr/bin/env python3
"""
Regression test for Nav2 costmap voxel layer boundary clipping.
Ensures sensor origin height (0.831m) does not exceed costmap height bounds (origin_z + z_voxels * z_resolution).
Also verifies that z_voxels <= 16 as required by costmap_2d voxel_grid bitmask implementation.
"""

import os
import unittest
import yaml

class CostmapBoundsRegressionTestCase(unittest.TestCase):
    def setUp(self):
        ws_dir = os.path.expanduser('~/ranger_mini_lyrical_2604_ws')
        self.nav_params_file = os.path.join(ws_dir, 'src', 'ranger_navigation', 'config', 'nav2_params.yaml')
        self.sensor_z = 0.831

    def test_voxel_bounds_contain_sensor(self):
        with open(self.nav_params_file, 'r') as f:
            data = yaml.safe_load(f)

        voxel_params = data['local_costmap']['local_costmap']['ros__parameters']['voxel_layer']
        origin_z = voxel_params['origin_z']
        z_res = voxel_params['z_resolution']
        z_voxels = voxel_params['z_voxels']

        max_height = origin_z + (z_voxels * z_res)

        # 1. Costmap_2d voxel_grid bitmask requirement: z_voxels <= 16
        self.assertLessEqual(z_voxels, 16, f"voxel_grid supports at most 16 z values, got {z_voxels}")

        # 2. Maximum height must enclose sensor origin (0.831m)
        self.assertGreater(max_height, self.sensor_z,
                           f"Sensor origin {self.sensor_z}m is out of bounds (max {max_height}m)")
        self.assertGreaterEqual(max_height, 1.5, f"Expected at least 1.5m height, got {max_height}m")

if __name__ == '__main__':
    unittest.main()
