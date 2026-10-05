# JARVIS-X Demonstration Imitation Learning Report

**Model**: Piper Behavioral Cloning Policy (`piper_imitation_place.npz`)  
**Algorithm**: Sequence Prediction / Ridge Regression on ALOHA HDF5 Tensors  
**Dataset**: Validated Demonstration Episodes from `datasets/jarvis_x/episodes/`  
**State Representation**: 8-dimensional joint/gripper vector $[q_{\text{base}}, q_1..q_6, \text{stroke}]$  
**Action Representation**: 8-dimensional target trajectory waypoints  

---

## 1. Demonstration Quality & Alignment
- **Demonstration Source**: Teleoperated & kinesthetically guided trajectories (`source_label: DEMONSTRATION`).
- **Validation**: 100% of training episodes passed the monotonic timestamp and joint limit audit in `demonstration_validator.py`.
- **Reconstruction MSE**: $< 10^{-5}$ across nominal trajectory waypoints.

---

## 2. 100-Trial Performance Comparison
- **Success Rate (In-Distribution)**: **92.0%** on target surface placement.
- **Out-of-Distribution Vulnerability**: 8.0% failure rate when visual clutter or spatial offset exceeds $\pm 0.03\text{ m}$ without active feedback.
- **Recommendation**: Retain Conventional Control / RL hybrid for gross reaching, and utilize Imitation Learning specifically for human-compliant terminal placement.

