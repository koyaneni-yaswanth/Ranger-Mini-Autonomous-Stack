# PROJECT JARVIS-X: Overall System Architecture

## 1. System Vision & Architecture
JARVIS-X is an embodied AI robotic system built upon the AgileX Ranger Mini v2 mobile base, an optional modular Piper 6-DOF robotic manipulator, an elevated multimodal perception mast, and a hierarchical cognitive intelligence layer running on ROS 2 Lyrical, NVIDIA Isaac Sim / Isaac Lab, and NVIDIA Jetson Orin.

```text
                    JARVIS-X
                 EMBODIED AI
                     BRAIN
                       │
        ┌──────────────┼──────────────┐
        │              │              │
      VOICE          VISION         MEMORY
        │              │              │
        └──────────────┼──────────────┘
                       │
                WORLD MODEL
                       │
                REASONING ENGINE
                       │
                TASK PLANNER
                       │
                SKILL MANAGER
                       │
             ┌─────────┴─────────┐
             │                   │
         NAVIGATION         MANIPULATION
             │                   │
            Nav2          MoveIt / Learned
             │                   │
             └─────────┬─────────┘
                       │
                 SAFETY LAYER
                       │
                ROBOT HARDWARE
```

## 2. Key Engineering Principles
- **AI Never Directly Controls Motors**: High-level AI models generate semantic intent and structured task schemas. Deterministic motion planning, obstacle inflation, collision monitoring, and joint trajectory controllers convert those plans into safe physical actuation.
- **Physical E-Stop Supremacy**: Hardware mushroom switch breaks actuator contactor power; no AI agent or software routine can override an active emergency stop.
- **Strict Modularity**: Operates seamlessly as a standalone AMR (`manipulator:=false`) or as an autonomous mobile manipulator (`manipulator:=true manipulator_type:=piper`).
