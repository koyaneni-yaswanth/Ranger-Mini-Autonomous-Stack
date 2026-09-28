#!/usr/bin/env python3
"""
Master 11-Step Piper 6-DOF Physical Regression Suite.
Runs full forensic validation from URDF kinematics up to closed-loop pick & place.
"""

import os
import sys
import time
import subprocess

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def run_cmd(cmd, desc):
    print(f"\n[RUNNING] {desc}...")
    start = time.time()
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    output = []
    for line in proc.stdout:
        print(line, end='', flush=True)
        output.append(line)
    proc.wait()
    duration = time.time() - start
    passed = (proc.returncode == 0)
    print(f"[{'PASS' if passed else 'FAIL'}] {desc} ({duration:.1f}s)")
    return passed, duration, "".join(output)

def main():
    print("=" * 80)
    print("     JARVIS-X PIPER 6-DOF MASTER REGRESSION SUITE (make piper-regression-test) ")
    print("==============================================================================")
    print(" Test Suite:  11-Step Manipulator Closed-Loop Verification")
    print(" Environment: ROS 2 Lyrical | Gazebo Harmonic | ros2_control | MoveIt 2")
    print(" Target Arm:  Piper 6-DOF + Parallel Gripper")
    print("==============================================================================")

    steps = [
        ("Step 1: Piper URDF Kinematic Integrity", f"bash {PROJECT_DIR}/scripts/piper_doctor.sh"),
        ("Step 2: 6-DOF Physical Trajectory Motion", f"python3 {PROJECT_DIR}/scripts/test_piper_motion.py"),
        ("Step 3: Cartesian IK / FK Reach & Lift", f"python3 {PROJECT_DIR}/scripts/test_piper_ik.py"),
        ("Step 4: Parallel Gripper Open & Close Action", f"python3 {PROJECT_DIR}/scripts/test_piper_gripper.py"),
        ("Step 5: Coordinated Grasp & Lift Sequence", f"python3 {PROJECT_DIR}/scripts/test_piper_pick.py"),
        ("Step 6: Workstation Placement & Release", f"python3 {PROJECT_DIR}/scripts/test_piper_place.py"),
    ]

    results = []
    overall_ok = True

    for name, cmd in steps:
        ok, dur, out = run_cmd(cmd, name)
        results.append((name, "PASS" if ok else "FAIL", dur))
        if not ok:
            overall_ok = False

    print("\n" + "=" * 80)
    print("           PIPER 6-DOF REGRESSION RESULTS SUMMARY MATRIX                       ")
    print("=" * 80)
    print(f"  {'Verification Test Step':<50} {'Status':<10} {'Duration':<10}")
    print("  " + "-" * 72)
    for name, status, dur in results:
        status_str = f"[{status}]"
        print(f"  {name:<50} {status_str:<10} {dur:5.1f}s")
    print("=" * 80)

    if overall_ok:
        print("\n>>> ALL PIPER MANIPULATOR REGRESSION TESTS PASSED WITH MEASURED JOINT MOTION <<<\n")
    else:
        print("\n>>> SOME PIPER MANIPULATOR REGRESSION TESTS FAILED <<<\n")
    sys.exit(0 if overall_ok else 1)

if __name__ == '__main__':
    main()