#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from sensor_msgs.msg import JointState

class ManipulatorVerification(Node):
    def __init__(self, expected_mode):
        super().__init__('manipulator_verification_test')
        self.expected_mode = expected_mode
        self.status_msg = None
        self.capabilities_msg = None
        self.ready_msg = None
        self.joint_names = set()

        self.create_subscription(String, '/manipulator/status', self.status_cb, 10)
        self.create_subscription(String, '/manipulator/capabilities', self.capabilities_cb, 10)
        self.create_subscription(Bool, '/manipulator/ready', self.ready_cb, 10)
        self.create_subscription(JointState, '/joint_states', self.joint_cb, 10)

    def status_cb(self, msg):
        self.status_msg = json.loads(msg.data)

    def capabilities_cb(self, msg):
        self.capabilities_msg = json.loads(msg.data)

    def ready_cb(self, msg):
        self.ready_msg = msg.data

    def joint_cb(self, msg):
        for name in msg.name:
            self.joint_names.add(name)

def run_test(expected_mode):
    print("=" * 70)
    print(f"RUNNING MODULAR MANIPULATOR VERIFICATION FOR MODE: {expected_mode.upper()}")
    print("=" * 70)

    errors = []

    # 1. Controller Manager Check
    print("[1] Verifying ros2_control Active Controllers...")
    res = subprocess.run(
        ["ros2", "control", "list_controllers"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    ctrl_out = res.stdout
    print("    Active Controllers Output:")
    for line in ctrl_out.strip().split("\n"):
        print(f"      {line}")

    if "joint_state_broadcaster" not in ctrl_out:
        errors.append("joint_state_broadcaster missing from active controllers")
    if "traction_controller" not in ctrl_out:
        errors.append("traction_controller missing from active controllers")
    if "steering_controller" not in ctrl_out:
        errors.append("steering_controller missing from active controllers")

    if expected_mode == "base_only":
        if "piper_arm_controller" in ctrl_out:
            errors.append("FATAL: piper_arm_controller is active in base-only mode!")
        else:
            print("    [PASS] piper_arm_controller is strictly absent in base-only mode.")
    elif expected_mode == "piper":
        if "piper_arm_controller" not in ctrl_out:
            errors.append("FATAL: piper_arm_controller is NOT active in piper mode!")
        else:
            print("    [PASS] piper_arm_controller is active in piper mode.")

    # 2. Check MoveIt Node presence
    print("[2] Verifying MoveIt Nodes...")
    node_res = subprocess.run(
        ["ros2", "node", "list"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    nodes = node_res.stdout
    moveit_present = "move_group" in nodes
    if expected_mode == "base_only":
        if moveit_present:
            errors.append("FATAL: MoveIt move_group node is running in base-only mode!")
        else:
            print("    [PASS] MoveIt nodes are absent in base-only mode.")
    elif expected_mode == "piper":
        print(f"    MoveIt running: {moveit_present}")

    # 3. Check Robot Description & TF
    print("[3] Verifying /robot_description URDF Links & Joints...")
    desc_res = subprocess.run(
        ["ros2", "param", "get", "/robot_state_publisher", "robot_description"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    urdf_content = desc_res.stdout
    piper_in_urdf = ("piper_link" in urdf_content or "piper_joint" in urdf_content)
    mount_in_urdf = "manipulator_mount" in urdf_content

    if not mount_in_urdf:
        errors.append("manipulator_mount frame missing from robot description!")
    else:
        print("    [PASS] Universal mechanical interface 'manipulator_mount' confirmed.")

    if expected_mode == "base_only":
        if piper_in_urdf:
            errors.append("FATAL: Piper arm links/joints found in URDF during base-only mode!")
        else:
            print("    [PASS] URDF strictly contains zero piper links/joints.")
    elif expected_mode == "piper":
        if not piper_in_urdf:
            errors.append("FATAL: Piper arm links/joints missing from URDF during piper mode!")
        else:
            print("    [PASS] Piper arm attached to manipulator_mount in URDF.")

    # 4. ROS 2 Node Spin for Status & Capabilities
    print("[4] Querying /manipulator/status and /manipulator/capabilities...")
    rclpy.init()
    node = ManipulatorVerification(expected_mode)

    import time
    start = time.time()
    while time.time() - start < 5.0:
        rclpy.spin_once(node, timeout_sec=0.2)
        if node.status_msg is not None and node.capabilities_msg is not None:
            break

    node.destroy_node()
    rclpy.shutdown()

    if node.status_msg is None:
        errors.append("Failed to receive /manipulator/status message within timeout")
    else:
        print(f"    Status: {json.dumps(node.status_msg, indent=2)}")

    if node.capabilities_msg is None:
        errors.append("Failed to receive /manipulator/capabilities message within timeout")
    else:
        print(f"    Capabilities: {json.dumps(node.capabilities_msg, indent=2)}")

    if node.status_msg:
        if expected_mode == "base_only":
            if node.status_msg.get("enabled") != False:
                errors.append(f"Status enabled={node.status_msg.get('enabled')}, expected False")
            if node.status_msg.get("type") != "none":
                errors.append(f"Status type={node.status_msg.get('type')}, expected 'none'")
        elif expected_mode == "piper":
            if node.status_msg.get("enabled") != True:
                errors.append(f"Status enabled={node.status_msg.get('enabled')}, expected True")
            if node.status_msg.get("type") != "piper":
                errors.append(f"Status type={node.status_msg.get('type')}, expected 'piper'")

    if node.capabilities_msg:
        if expected_mode == "base_only":
            if node.capabilities_msg.get("can_pick") != False:
                errors.append("Capabilities can_pick is True in base-only mode!")
            if node.capabilities_msg.get("can_place") != False:
                errors.append("Capabilities can_place is True in base-only mode!")
            if node.capabilities_msg.get("can_move_arm") != False:
                errors.append("Capabilities can_move_arm is True in base-only mode!")
        elif expected_mode == "piper":
            if node.capabilities_msg.get("can_pick") != True:
                errors.append("Capabilities can_pick is False in piper mode!")
            if node.capabilities_msg.get("can_place") != True:
                errors.append("Capabilities can_place is False in piper mode!")
            if node.capabilities_msg.get("can_move_arm") != True:
                errors.append("Capabilities can_move_arm is False in piper mode!")

    print("=" * 70)
    if errors:
        print("VERIFICATION FAILED WITH ERRORS:")
        for err in errors:
            print(f"  [X] {err}")
        return False
    else:
        print(f"VERIFICATION SUCCESSFUL: ALL CHECKS PASSED FOR {expected_mode.upper()}!")
        return True

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else "base_only"
    ok = run_test(mode)
    sys.exit(0 if ok else 1)
