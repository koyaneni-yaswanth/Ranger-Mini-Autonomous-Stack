import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from amr_x_interfaces.msg import WorldObject
from amr_x_interfaces.action import TaskAssignment

class ActivePerception(Node):
    def __init__(self):
        super().__init__('active_perception')
        
        self.world_sub = self.create_subscription(
            WorldObject,
            '/world_model/objects',
            self.world_callback,
            10)
            
        self._action_client = ActionClient(
            self,
            TaskAssignment,
            '/fleet/assign_task')
            
        self.pending_inspections = set()
        self.get_logger().info("Active Perception Node initialized.")

    def world_callback(self, msg):
        if msg.status == "NEEDS_INSPECTION" and msg.object_id not in self.pending_inspections:
            self.get_logger().info(f"{msg.object_id} needs inspection. Dispatching request...")
            self.pending_inspections.add(msg.object_id)
            self.send_inspection_task(msg)
            
    def send_inspection_task(self, obj_msg):
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Fleet Manager Action Server not available!")
            self.pending_inspections.remove(obj_msg.object_id)
            return
            
        goal_msg = TaskAssignment.Goal()
        goal_msg.task_id = f"INSPECT_{obj_msg.object_id}_{self.get_clock().now().to_msg().sec}"
        goal_msg.task_type = "INSPECTION"
        goal_msg.target_object_id = obj_msg.object_id
        goal_msg.target_location.header = obj_msg.header
        goal_msg.target_location.pose = obj_msg.pose.pose
        
        self.get_logger().info(f"Sending inspection task {goal_msg.task_id}")
        
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Inspection task rejected by Fleet Manager.")
            # We could remove it from pending here so it tries again later
            return

        self.get_logger().info("Inspection task accepted. Awaiting result...")
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info(f"Inspection succeeded: {result.message}")
        else:
            self.get_logger().error(f"Inspection failed: {result.message}")

def main(args=None):
    rclpy.init(args=args)
    node = ActivePerception()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
