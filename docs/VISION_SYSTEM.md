# Multimodal Vision & Perception System

## 1. Sensor Complement
- **RGB-D Vision**: Intel RealSense D435i streaming 1920x1080 RGB @ 30 FPS and 1280x720 16UC1 Depth @ 30 FPS.
- **3D Solid-State LiDAR**: Livox Mid-360 streaming high-density PointCloud2.
- **Chassis IMU**: 6-axis inertial measurement unit.

## 2. Perception Pipeline (`ranger_vision`)
- Multi-spectral HSV color segmentation and contour geometry extraction.
- Pinhole camera backprojection calculating 3D metric centroids.
- Live TF transformation into `base_link` and `map` coordinates.
- Topics: `/vision/detections`, `/vision/detected_objects`, `/vision/target_pose`.
