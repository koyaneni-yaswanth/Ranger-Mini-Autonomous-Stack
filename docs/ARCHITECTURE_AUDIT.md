# JARVIS-X: COMPLETE REPOSITORY FORENSIC ARCHITECTURE AUDIT

## 1. Executive Summary
This document provides an exhaustive dependency map, package topology, and architectural audit of the **JARVIS-X Autonomous Mobile Manipulator** project.

## 2. Package Dependency Map
```text
[Human Voice / Text Input]
            │
            ▼
┌───────────────────────┐
│     jarvis_core       │ <── 13 Submodules (audio, speech, intent, reasoning, planner,
└───────────┬───────────┘     memory, world_model, skills, capabilities, safety, dialogue, events, orchestration)
            │
            ▼
┌───────────────────────┐
│    ranger_missions    │ <── Robot Hardware Abstraction Layer (HAL) & Skill Library
└───────────┬───────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
┌───────────────┐ ┌──────────────────┐
│ranger_nav2    │ │ranger_manipulation│ <── MoveIt 2 & Piper 6-DOF
└───────┬───────┘ └────────┬─────────┘
        │                  │
        └─────────┬────────┘
                  ▼
┌───────────────────────┐
│    ranger_control     │ <── ros2_control & 4WIS Kinematics Node
└───────────┬───────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
[Gazebo Harmonic] [Jetson Hardware / CAN]
```

## 3. Strict Boundary Rules Enforced
- **Rule 21 & 64**: AI never directly commands raw actuators, motor currents, or velocity.
- **Physical Modularity**: Standalone AMR (`manipulator:=false`) and Piper 6-DOF Arm (`manipulator:=true`).
- **Sim-to-Real Decoupling**: Unified HAL abstracts backend execution across Gazebo, Isaac Sim, and physical Jetson.
