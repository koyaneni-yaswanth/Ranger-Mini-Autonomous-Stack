# Mobile Manipulation Pick-and-Place Pipeline

## 1. 17-State Autonomous Execution Machine
```text
[IDLE] -> [UNDERSTAND_TASK] -> [VALIDATE_TASK] -> [SEARCH] -> [DETECT]
   ^                                                              |
   |                                                              v
[TASK_COMPLETE] <- [UPDATE_WORLD] <- [VERIFY_PLACE] <- [PLACE] <- [PLAN_PLACE]
   ^                                                              |
   |                                                              v
   +---- [NAVIGATE_TO_DESTINATION] <- [VERIFY_GRASP] <- [PICK] <- [PLAN_GRASP] <- [VERIFY_OBJECT] <- [NAVIGATE_TO_OBJECT] <- [LOCALIZE_OBJECT]
```

## 2. Multi-Stage Grasp Verification
The grasp verification stage validates payload acquisition through three sensory channels:
1. **Kinematic Finger Gap**: Verifies gripper joint position closed within tolerance:
   `0.050m <= gripper_gap <= 0.065m` (for 0.06m cube).
2. **Current/Effort Feedback**: Confirms steady motor holding current > 0.8 Nm without stall timeout.
3. **Visual Occlusion Confirmation**: RealSense depth image confirms absence of object on staging surface and presence within hand frame.

Evaluation outputs:
- `SUCCESS`: Transition to `TRANSPORT` pose and proceed to navigation.
- `FAILED`: Transition to `RECOVERY` routine (retreat 0.10m, re-survey, re-grasp up to 3 times).
- `UNCERTAIN`: Log diagnostic telemetry, attempt gentle lift test.
