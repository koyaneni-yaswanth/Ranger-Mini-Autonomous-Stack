# Verified Solutions & Diagnostic Guide

- **Black Gazebo Window**: Set `<render_engine>ogre</render_engine>` in world SDF.
- **Missing GPU Acceleration**: Set `MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA`.
- **Python Double Shutdown**: Guard with `if rclpy.ok(): rclpy.shutdown()`.
