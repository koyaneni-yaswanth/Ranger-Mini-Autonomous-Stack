# Testing, Verification & CI/CD Procedures

## 1. Automated Test Suites
Execute the full test engine with:
```bash
make test
```
This runs:
1. Environment pre-flight check (`check_environment.sh`).
2. ROS 2 Lyrical distribution and binary integrity audit (`check_ros.sh`).
3. NVIDIA RTX GPU 3D acceleration test (`check_gpu.sh`).
4. Network interface and DDS multicast check (`check_network.sh`).
5. Hardware bus & CAN sensor audit (`check_hardware.sh`).
6. AI Task Execution and Safety Policy test suite (`test_ai_task_execution.py`).

## 2. Health Check
Run the platform health audit:
```bash
make health
```
