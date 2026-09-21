import pytest
import numpy as np

def test_vectorized_projection():
    """
    Tests the core vectorized math logic used in the sensor_fusion_node
    to project 3D LiDAR points into a 2D camera plane.
    """
    # Simulated 3D Points (X, Y, Z) in Camera Frame
    # Point 1: Directly in front (center), depth 2.0m
    # Point 2: Offset right, depth 3.0m
    # Point 3: Behind camera (should be filtered), Z = -1.0
    points_cam = np.array([
        [0.0, 0.0, 2.0],
        [1.5, 0.0, 3.0],
        [0.0, 0.0, -1.0]
    ])
    
    # Simulated Camera Intrinsics (640x480)
    fx, fy = 500.0, 500.0
    cx, cy = 320.0, 240.0
    
    # Filter out points behind camera (Z <= 0)
    valid_idx = points_cam[:, 2] > 0
    valid_points = points_cam[valid_idx]
    assert len(valid_points) == 2, "Should have filtered out the point behind the camera"
    
    Z = valid_points[:, 2]
    X = valid_points[:, 0]
    Y = valid_points[:, 1]
    
    # Project to 2D
    u = (fx * X / Z) + cx
    v = (fy * Y / Z) + cy
    
    # Check Point 1: Should project to exact center (cx, cy)
    assert u[0] == 320.0, f"Expected u=320.0, got {u[0]}"
    assert v[0] == 240.0, f"Expected v=240.0, got {v[0]}"
    
    # Check Point 2: Should project to (500 * 1.5 / 3.0) + 320 = 250 + 320 = 570
    assert u[1] == 570.0, f"Expected u=570.0, got {u[1]}"
    assert v[1] == 240.0, f"Expected v=240.0, got {v[1]}"

def test_bounding_box_intersection():
    """
    Tests the boolean mask intersection for LiDAR points inside a bounding box.
    """
    # 5 simulated pixels
    u = np.array([100, 320, 500, 340, 400])
    v = np.array([100, 240, 300, 260, 400])
    Z = np.array([1.0, 2.5, 3.0, 2.6, 5.0])
    
    # Bounding box (center: 330, 250, size: 50x50)
    box_x = 305
    box_y = 225
    box_w = 50
    box_h = 50
    
    # Boolean mask
    inside_box = (u >= box_x) & (u <= box_x + box_w) & (v >= box_y) & (v <= box_y + box_h)
    box_depths = Z[inside_box]
    
    # Points at index 1 (320,240) and index 3 (340,260) should be inside
    assert len(box_depths) == 2
    assert np.allclose(box_depths, [2.5, 2.6])
    assert np.median(box_depths) == 2.55
