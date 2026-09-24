#!/usr/bin/env python3
"""
Interactive Autonomous Task CLI for Ranger Mini Autonomous Mobile Manipulator.
Provides natural language mission dispatch, telemetry monitoring, grasp verification reporting,
and safety control.
"""

import os
import sys
import time
import json
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseStamped

class InteractiveTaskCLI(Node):
    def __init__(self):
        super().__init__('interactive_task_cli')

        # Telemetry Cache
        self.current_state = "IDLE"
        self.last_status = {}
        self.last_grasp_eval = {}
        self.estop_active = False
        self.detected_objects = []

        # Subscriptions
        self.sub_state = self.create_subscription(String, '/mission/state', self.state_cb, 10)
        self.sub_status = self.create_subscription(String, '/mission/status', self.status_cb, 10)
        self.sub_grasp = self.create_subscription(String, '/mission/grasp_verification', self.grasp_cb, 10)
        self.sub_vision = self.create_subscription(String, '/vision/detected_objects', self.vision_cb, 10)
        self.sub_rejection = self.create_subscription(String, '/ai/task_rejection', self.rejection_cb, 10)

        # Publishers
        self.pub_cmd = self.create_publisher(String, '/ai/task_command', 10)
        self.pub_estop = self.create_publisher(Bool, '/safety/estop_active', 10)

    def state_cb(self, msg: String):
        self.current_state = msg.data

    def status_cb(self, msg: String):
        try:
            self.last_status = json.loads(msg.data)
        except Exception:
            pass

    def grasp_cb(self, msg: String):
        try:
            self.last_grasp_eval = json.loads(msg.data)
        except Exception:
            pass

    def vision_cb(self, msg: String):
        try:
            self.detected_objects = json.loads(msg.data)
        except Exception:
            pass

    def rejection_cb(self, msg: String):
        try:
            data = json.loads(msg.data)
            print(f"\n\033[91m[REJECTION ALERT]\033[0m {data.get('status')}: {data.get('reason')}")
        except Exception:
            print(f"\n\033[91m[REJECTION ALERT]\033[0m {msg.data}")

    def dispatch_command(self, text: str):
        msg = String()
        msg.data = text
        self.pub_cmd.publish(msg)
        print(f"\033[92m[DISPATCHED]\033[0m '{text}' sent to AI Task Interpreter.")

    def trigger_estop(self, active: bool):
        msg = Bool()
        msg.data = active
        self.pub_estop.publish(msg)
        status_str = "\033[91mENGAGED\033[0m" if active else "\033[92mRELEASED\033[0m"
        print(f"[SAFETY] Emergency Stop {status_str}")


def print_banner():
    banner = """
================================================================================
     RANGER MINI - AUTONOMOUS MOBILE MANIPULATOR TASK CONTROL CLI
     ROS 2 Lyrical | Piper 6-DOF | Jetson Orin | AI Task Execution
================================================================================
"""
    print(banner)

def print_menu():
    menu = """
--------------------------------------------------------------------------------
 PRESET BENCHMARK TASKS:
  [1] Red Object Pick-and-Place: "Find the red object, pick it up, and place it at the target station"
  [2] Blue Box Handling:        "Pick up the blue box and place it in the assembly bin"
  [3] Inspection Routine:       "Inspect the inspection table"
  [4] Docking & Charging:       "Dock at home dock"
  [5] Custom Natural Language:  Enter any custom English instruction
  [s] Print Status & Telemetry
  [e] Trigger Emergency Stop (E-STOP ENGAGE)
  [r] Reset Emergency Stop (E-STOP RELEASE)
  [q] Quit
--------------------------------------------------------------------------------
"""
    print(menu)

def main():
    rclpy.init()
    cli_node = InteractiveTaskCLI()

    # Spin ROS 2 in background daemon thread
    spin_thread = threading.Thread(target=rclpy.spin, args=(cli_node,), daemon=True)
    spin_thread.start()

    print_banner()

    try:
        while rclpy.ok():
            print_menu()
            choice = input("Select option [1-5, s, e, r, q]: ").strip()

            if choice == '1':
                cli_node.dispatch_command("Find the red object, pick it up, and place it at the target station")
            elif choice == '2':
                cli_node.dispatch_command("Pick up the blue box and place it in the assembly bin")
            elif choice == '3':
                cli_node.dispatch_command("Inspect the inspection table")
            elif choice == '4':
                cli_node.dispatch_command("Dock at home dock")
            elif choice == '5':
                custom_text = input("Enter instruction: ").strip()
                if custom_text:
                    cli_node.dispatch_command(custom_text)
            elif choice.lower() == 's':
                print("\n--- CURRENT SYSTEM TELEMETRY ---")
                print(f"  FSM State:            \033[94m{cli_node.current_state}\033[0m")
                print(f"  Active Task ID:       {cli_node.last_status.get('task_id', 'None')}")
                print(f"  State Elapsed Time:   {cli_node.last_status.get('elapsed_state_sec', 0)}s")
                print(f"  Vision Detections:    {len(cli_node.detected_objects)} tracked object(s)")
                for obj in cli_node.detected_objects:
                    print(f"    -> [{obj.get('color')}] {obj.get('class')} at base: {obj.get('pose_base')}")
                if cli_node.last_grasp_eval:
                    print(f"  Last Grasp Eval:      {cli_node.last_grasp_eval.get('status')} (Effort: {cli_node.last_grasp_eval.get('measured_effort_nm')} Nm)")
                print("--------------------------------\n")
            elif choice.lower() == 'e':
                cli_node.trigger_estop(True)
            elif choice.lower() == 'r':
                cli_node.trigger_estop(False)
            elif choice.lower() == 'q':
                break
            else:
                print("Invalid selection.")
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        cli_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
