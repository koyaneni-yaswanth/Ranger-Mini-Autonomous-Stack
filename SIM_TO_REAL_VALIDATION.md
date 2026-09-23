# SIM-TO-REAL QUANTITATIVE VALIDATION

## 1. Kinematic & Dynamic Tolerance Bounds
| Metric | Simulation Expected | Hardware Limit | Tolerance | Acceptance Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **Linear Velocity** | $1.50\,	ext{m/s}$ | $1.50\,	ext{m/s}$ | $\pm 0.05\,	ext{m/s}$ | Closed-loop wheel feedback matches commanded velocity |
| **Angular Velocity**| $2.00\,	ext{rad/s}$ | $2.00\,	ext{rad/s}$ | $\pm 0.08\,	ext{rad/s}$ | Pure spin within track envelope |
| **Command Timeout** | $0.25\,	ext{s}$ | $0.20\,	ext{s}$ | $\pm 0.05\,	ext{s}$ | Fail-safe zero velocity on heartbeat cessation |
| **LiDAR Latency** | $\le 10\,	ext{ms}$ | $\le 15\,	ext{ms}$ | $\le 20\,	ext{ms}$ | Processing buffer without dropped frames |
| **TF Transform Lag**| $\le 5\,	ext{ms}$ | $\le 8\,	ext{ms}$ | $\le 15\,	ext{ms}$ | Real-time extrapolation without transform warnings |
