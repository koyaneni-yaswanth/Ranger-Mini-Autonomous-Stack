# ROS 2 Humble Environment Setup

## 1. Native Prerequisites
- Ubuntu 22.04.5 LTS host
- ROS 2 Humble Hawksbill (`/opt/ros/humble`)

## 2. Workspace Build & Source
```bash
cd ~/ranger_mini_humble_ws
./build.sh
source install/setup.bash
```

## 3. Verification
```bash
ros2 pkg list | grep ranger
```
