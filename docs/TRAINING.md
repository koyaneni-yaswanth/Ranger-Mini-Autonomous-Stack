# Simulation Policy Training & Deployment Pipeline

## 1. Training Loop
```text
ROBOT MODEL -> ISAAC SIM (Synthetic Data & Physics) -> ISAAC LAB (RL Training)
  -> POLICY EVALUATION -> SIM-TO-REAL TEST -> JETSON ORIN DEPLOYMENT -> REAL ROBOT
```

## 2. Policy Packaging
Trained neural networks are encapsulated as `LearnedGraspSkill` within the Skill Manager, allowing JARVIS to invoke learned policies alongside classical MoveIt 2 trajectories without redesigning higher-level planners.
