# Troubleshooting & Diagnostic Guide

## 1. Common Issues & Solutions

### Issue: "Static cache is empty, when looking up transform from frame [lidar_link] to frame [odom]"
- **Cause**: RViz launched before `robot_state_publisher` or `ranger_base_node` published the initial TF transforms.
- **Fix**: Launch the base simulation first (`make sim` or `make piper`), allow TF to stabilize (5-8 seconds), then run `make rviz`.

### Issue: "topic '/cmd_vel' has more than one types associated"
- **Cause**: Concurrent publishers using Twist vs TwistStamped.
- **Fix**: The orchestrator and base nodes use canonical `geometry_msgs/msg/Twist`.

### Issue: "Task Rejected: Base-Only configuration"
- **Cause**: Task requires arm action (`pick`, `place`) but launch argument `manipulator` was set to `false`.
- **Fix**: Launch with `make piper` or set `manipulator:=true`.
