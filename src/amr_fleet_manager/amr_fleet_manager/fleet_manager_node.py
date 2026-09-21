import rclpy
from rclpy.node import Node
from amr_x_interfaces.msg import RobotCapability, RobotHealth
from amr_x_interfaces.action import TaskAssignment
from rclpy.action import ActionServer
import time

class FleetManager(Node):
    def __init__(self):
        super().__init__('fleet_manager')
        
        self.robots = {}
        self.health_states = {}
        
        self.cap_sub = self.create_subscription(
            RobotCapability,
            '/fleet/capabilities',
            self.cap_callback,
            10)
            
        self.health_sub = self.create_subscription(
            RobotHealth,
            '/fleet/health',
            self.health_callback,
            10)
            
        self._action_server = ActionServer(
            self,
            TaskAssignment,
            '/fleet/assign_task',
            self.execute_task_callback)
            
        self.get_logger().info("AMR-X Fleet Manager initialized.")

    def cap_callback(self, msg):
        self.robots[msg.robot_id] = msg
        
    def health_callback(self, msg):
        self.health_states[msg.robot_id] = msg

    def calculate_score(self, robot_id, task_type):
        if robot_id not in self.robots or robot_id not in self.health_states:
            return 0.0
            
        cap = self.robots[robot_id]
        health = self.health_states[robot_id]
        
        if health.battery_percentage < 15.0 or not health.hardware_ok:
            return 0.0
            
        score = health.battery_percentage * 0.5
        
        if task_type == "MANIPULATION" and cap.can_manipulate:
            score += 50.0
        if task_type == "TRANSPORT" and cap.can_navigate:
            score += 50.0
            
        return score

    def execute_task_callback(self, goal_handle):
        self.get_logger().info(f"Received Task: {goal_handle.request.task_type}")
        
        best_robot = None
        best_score = -1.0
        
        for robot_id in self.robots:
            score = self.calculate_score(robot_id, goal_handle.request.task_type)
            if score > best_score:
                best_score = score
                best_robot = robot_id
                
        if best_robot and best_score > 0:
            self.get_logger().info(f"Assigned task {goal_handle.request.task_id} to {best_robot} (Score: {best_score:.2f})")
            # Simulate task execution
            time.sleep(1.0)
            goal_handle.succeed()
            result = TaskAssignment.Result()
            result.success = True
            result.message = f"Executed by {best_robot}"
            return result
        else:
            self.get_logger().warn("No suitable robot found for task.")
            goal_handle.abort()
            result = TaskAssignment.Result()
            result.success = False
            result.message = "No capable robot"
            return result

def main(args=None):
    rclpy.init(args=args)
    node = FleetManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
