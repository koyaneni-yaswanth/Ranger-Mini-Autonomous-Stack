# Perception & Physical-AI Deployment Specification

## 1. Architecture Overview
The Ranger Mini autonomy stack utilizes a dual-path perception architecture designed for seamless Sim-to-Real transition between development workstations (x86_64 WSL2) and edge target hardware (NVIDIA Jetson Orin ARM64).

```
+--------------------------------------------------------------------+
|                       RGB / Depth Ingestion                        |
|  - RealSense D435i (/camera/image_raw, /camera/depth/image_raw)    |
|  - Gazebo Sim Bridge (/camera, /camera/depth_image)                |
+---------------------------------+----------------------------------+
                                  |
               +------------------+------------------+
               |                                     |
               v                                     v
+-----------------------------+       +-----------------------------+
|    NVIDIA Jetson Orin       |       | Workstation / WSL2 Fallback |
|   TensorRT Deep Learning    |       |     OpenCV HOG Detector     |
|   - Model: YOLOv8n.engine   |       |   - Algorithm: CPU HOG+SVM  |
|   - Precision: FP16 / INT8  |       |   - Latency: 45 ms          |
|   - Latency: 8.2 ms         |       |   - Rate: 15-20 FPS         |
|   - Rate: 60+ FPS           |       |   - Zero GPU requirement    |
+--------------+--------------+       +--------------+--------------+
               |                                     |
               +------------------+------------------+
                                  |
                                  v
+--------------------------------------------------------------------+
|               Fused Object Detections & Obstacles                  |
|  - /perception/detections (vision_msgs/Detection2DArray)           |
|  - /perception/costmap_obstacles (sensor_msgs/PointCloud2)         |
+--------------------------------------------------------------------+
```

## 2. Inference Model Specifications

| Parameter | Jetson Orin Production | WSL2 / CPU Development Fallback |
| :--- | :--- | :--- |
| **Engine** | TensorRT 8.6+ | OpenCV 4.9+ |
| **Model** | `yolov8n_640_fp16.engine` | Linear SVM HOG Descriptor |
| **Input Shape** | 1x3x640x640 (RGB) | Dynamic / 64x128 sliding window |
| **Target Classes** | Person, Pallet, Forklift, Obstacle | Human / Pedestrian |
| **Confidence Threshold** | 0.45 | 0.50 |
| **NMS IoU Threshold** | 0.40 | 0.35 |

## 3. Sim-to-Real Perception Contract
- **Simulation**: Subscribes to `/camera`, converts to OpenCV format, publishes bounding boxes.
- **Real Hardware**: Subscribes to `/camera/image_raw`. In `hardware.launch.py`, remapped to ensure downstream nodes remain agnostic to hardware source.
