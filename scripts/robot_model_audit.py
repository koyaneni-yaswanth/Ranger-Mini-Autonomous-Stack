#!/usr/bin/env python3
"""
JARVIS-X Robot Digital Twin & Kinematics Audit Tool
Audits robot model geometry, inertial parameters, joint limits, and mounting constraints.
Cross-references against official AgileX Piper and Ranger specifications.
"""

import os
import sys
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URDF_PATH = os.path.join(PROJECT_ROOT, "description", "urdf", "ranger_mini_piper.urdf")

def audit_model():
    print("=" * 80)
    print("           JARVIS-X ROBOT DIGITAL TWIN & KINEMATICS AUDIT")
    print("=" * 80)
    print(f"Target URDF: {URDF_PATH}")

    if not os.path.exists(URDF_PATH):
        print(f"[FAIL] URDF file not found at {URDF_PATH}")
        sys.exit(1)

    tree = ET.parse(URDF_PATH)
    root = tree.getroot()

    # Define official AgileX Piper ground truth specifications
    OFFICIAL_SPECS = {
        "joint1": {"type": "revolute", "origin": [0.0, 0.0, 0.123], "bounds": [-2.618, 2.618], "axis": [0,0,1]},
        "joint2": {"type": "revolute", "origin": [0.0, 0.0, 0.0], "bounds": [0.0, 3.140], "axis": [0,0,1]},
        "joint3": {"type": "revolute", "origin": [0.28503, 0.0, 0.0], "bounds": [-2.967, 0.0], "axis": [0,0,1]},
        "joint4": {"type": "revolute", "origin": [-0.02198, -0.25075, 0.0], "bounds": [-1.745, 1.745], "axis": [0,0,1]},
        "joint5": {"type": "revolute", "origin": [0.0, 0.0, 0.0], "bounds": [-1.220, 1.220], "axis": [0,0,1]},
        "joint6": {"type": "revolute", "origin": [0.000088, -0.091, 0.0], "bounds": [-2.094, 2.094], "axis": [0,0,1]},
    }

    print("\n--- [1] Manipulator Link & Inertia Audit ---")
    total_arm_mass = 0.0
    piper_links = [l for l in root.findall("link") if "piper" in l.attrib.get("name", "")]
    for l in piper_links:
        name = l.attrib.get("name")
        inertial = l.find("inertial")
        mass = float(inertial.find("mass").attrib.get("value")) if inertial is not None and inertial.find("mass") is not None else 0.0
        total_arm_mass += mass
        geom = l.find(".//geometry")
        geom_type = list(geom)[0].tag if geom is not None and len(list(geom)) > 0 else "none"
        print(f"  Link: {name:22} | Mass: {mass:5.2f} kg | Geometry: {geom_type}")

    print(f"  Total Modeled Manipulator Mass: {total_arm_mass:.2f} kg (Official AgileX: 4.67 kg)")

    print("\n--- [2] Link-by-Link Audit Matrix ---")
    headers = f"{'Joint/Link':<18} | {'Official Bounds':<16} | {'URDF Bounds':<16} | {'Discrepancy':<14} | {'Status'}"
    print(headers)
    print("-" * 80)

    discrepancies = 0
    all_joints = root.findall("joint")
    for j_idx in range(1, 7):
        official_name = f"joint{j_idx}"
        urdf_name = f"piper_joint{j_idx}"
        matching = [j for j in all_joints if j.attrib.get("name") == urdf_name]
        j_elem = matching[0] if matching else None
        
        off_b = OFFICIAL_SPECS[official_name]["bounds"]
        off_b_str = f"[{off_b[0]:+.2f}, {off_b[1]:+.2f}]"

        if j_elem is not None:
            limit = j_elem.find("limit")
            urdf_b = [float(limit.attrib.get("lower", -3.14)), float(limit.attrib.get("upper", 3.14))]
            urdf_b_str = f"[{urdf_b[0]:+.2f}, {urdf_b[1]:+.2f}]"
            err = max(abs(off_b[0] - urdf_b[0]), abs(off_b[1] - urdf_b[1]))
            if err > 0.05:
                status = "PROVISIONAL"
                discrepancies += 1
            else:
                status = "MATCH"
        else:
            urdf_b_str = "MISSING"
            err = 999.0
            status = "FAIL"
            discrepancies += 1

        print(f"{urdf_name:<18} | {off_b_str:<16} | {urdf_b_str:<16} | {err:10.3f} rad | {status}")

    print("\n--- [3] Chassis Mounting Verification ---")
    total_xyz = [0.0, 0.0, 0.0]
    chain = ['body_enclosure_joint', 'top_deck_joint', 'manipulator_mount_joint', 'piper_mount_joint']
    for jname in chain:
        j_matches = [j for j in all_joints if j.attrib.get('name') == jname]
        if j_matches:
            orig = j_matches[0].find('origin')
            if orig is not None:
                xyz = [float(v) for v in orig.attrib.get('xyz', '0 0 0').split()]
                total_xyz[0] += xyz[0]
                total_xyz[1] += xyz[1]
                total_xyz[2] += xyz[2]
                print(f"  Transform [{jname:23}]: delta xyz=[{xyz[0]:+.3f}, {xyz[1]:+.3f}, {xyz[2]:+.3f}]")

    print(f"  Cumulative Arm Mount Offset from base_link: X={total_xyz[0]:+.3f}m, Y={total_xyz[1]:+.3f}m, Z={total_xyz[2]:+.3f}m")
    if abs(total_xyz[2] - 0.345) < 0.02 and abs(total_xyz[0] - 0.150) < 0.02:
        print("  [OK] Manipulator mounting matches CAD specification (X=+0.150m, Z=+0.345m).")
    else:
        print("  [WARN] Mounting offset deviates from standard CAD position.")

    print("=" * 80)
    print(">>> MODEL ACCEPTANCE GATE VERDICT <<<")
    print(f"Discrepancies identified against official AgileX SolidWorks CAD: {discrepancies}")
    print("CLASSIFICATION: PROVISIONAL_MODEL_NOT_FOR_SIM_TO_REAL")
    print("Safety Constraint: Model approved ONLY for ROS 2 software integration, FSM, and Gazebo sim.")
    print("Physical Deployment: STRICTLY BLOCKED until official CAD STLs and DH offsets are loaded.")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(audit_model())
