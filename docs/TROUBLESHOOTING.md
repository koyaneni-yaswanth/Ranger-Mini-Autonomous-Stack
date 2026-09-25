# Diagnostics & Troubleshooting Guide

## 1. Common Scenarios
- **"Task Rejected: Manipulation unavailable"**: Robot is operating in Base-Only mode (`manipulator:=false`). Attach Piper module or enable parameter in launch file.
- **"Human in STOP zone"**: A person is detected within 1.0m. Robot halts automatically; motion resumes once person moves to CAUTION/SAFE zone.
- **"Physical hardware not connected"**: When running `./scripts/run_real.sh` without real CAN adapters, the system cleanly blocks hardware launch and offers simulation fallback.
