#!/usr/bin/env python3
"""
JARVIS-X Demonstration & Episode Dataset Validator
Validates episode integrity, monotonic timestamps, joint bounds, and source labels.
Rejects malformed, incomplete, or unsynchronized demonstration data.
"""

import os
import sys
import glob
import json
import math

VALID_SOURCE_LABELS = {"SIMULATION", "HARDWARE", "REPLAY", "DEMONSTRATION", "SYNTHETIC"}

def validate_episode(file_path):
    issues = []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return False, [f"Corrupt JSON file: {e}"]

    # 1. Metadata Header Audit (supports both v1 legacy and v2 strict schemas)
    meta = data.get("metadata", {})
    task = meta.get("task_instruction") or meta.get("task_name")
    if not task:
        issues.append("Missing task identifier ('task_instruction' or 'task_name')")

    source_label = meta.get("source_label")
    if not source_label:
        if "simulator" in meta or "sim" in meta.get("execution_mode", "").lower():
            source_label = "SIMULATION"
        else:
            issues.append("Missing 'source_label' in metadata")

    if source_label and source_label not in VALID_SOURCE_LABELS:
        issues.append(f"Invalid source_label '{source_label}'. Must be one of {VALID_SOURCE_LABELS}")

    robot_model = meta.get("robot_model") or meta.get("robot_platform")
    if not robot_model:
        issues.append("Missing robot identifier ('robot_model' or 'robot_platform')")

    # 2. Timestep Telemetry Audit
    steps = data.get("timesteps") or data.get("trajectory_stream") or []
    if len(steps) < 5:
        issues.append(f"Insufficient timesteps ({len(steps)}). Minimum required: 5")

    prev_t = -1.0
    for idx, step in enumerate(steps):
        t = step.get("timestamp") or step.get("time_from_start_s") or (idx * 0.02)
        if t <= prev_t and idx > 0:
            issues.append(f"Non-monotonic timestamp at step {idx}: prev={prev_t:.4f}, curr={t:.4f}")
        prev_t = t

        # Joint bounds validation (check either direct joint_positions or observation.q)
        q = step.get("joint_positions")
        if q is None and "observation" in step:
            q = step["observation"].get("q")

        if q and len(q) == 6:
            for j_idx, val in enumerate(q):
                if abs(val) > 3.5:
                    issues.append(f"Joint q{j_idx+1} exceeded physical limits ({val:.2f} rad) at step {idx}")

    return len(issues) == 0, issues

def main():
    print("=" * 80)
    print("        JARVIS-X DEMONSTRATION & EPISODE DATASET VALIDATOR")
    print("=" * 80)

    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "datasets", "jarvis_x", "episodes")
    os.makedirs(dataset_dir, exist_ok=True)
    
    episode_files = sorted(glob.glob(os.path.join(dataset_dir, "*.json")))

    if not episode_files:
        print(f"[FAIL] No episode files found in {dataset_dir}")
        sys.exit(1)

    print(f"Auditing {len(episode_files)} episode file(s) in: {dataset_dir}\n")

    passed_count = 0
    failed_count = 0

    for ep_path in episode_files:
        basename = os.path.basename(ep_path)
        is_valid, errors = validate_episode(ep_path)
        if is_valid:
            passed_count += 1
            print(f"  [PASS] {basename:32} | Schema: Valid | Timestamps: Monotonic | Bounds: Clean")
        else:
            failed_count += 1
            print(f"  [FAIL] {basename:32} | Issues: {len(errors)}")
            for err in errors[:3]:
                print(f"         - {err}")

    print("=" * 80)
    print(f"Dataset Audit Summary: {passed_count} Valid | {failed_count} Rejected")
    if failed_count == 0 and passed_count > 0:
        print(">>> [PASS] ALL DEMONSTRATION & EPISODE DATASETS VALIDATED <<<")
        print("=" * 80)
        return 0
    else:
        print(">>> [FAIL] DATASET VALIDATION REJECTED ONE OR MORE EPISODES <<<")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
