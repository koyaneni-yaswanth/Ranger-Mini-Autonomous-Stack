import rclpy
from rclpy.node import Node
from amr_x_interfaces.msg import WorldObject
import math

class SemanticWorldModel(Node):
    def __init__(self):
        super().__init__('semantic_world_model')
        
        self.objects = {}
        self.confidence_threshold = 0.8
        
        # Subscribe to detections from any robot
        self.detection_sub = self.create_subscription(
            WorldObject,
            '/fleet/detections',
            self.detection_callback,
            10)
            
        # Publish the aggregated world state
        self.world_pub = self.create_publisher(
            WorldObject,
            '/world_model/objects',
            10)
            
        self.get_logger().info("Semantic World Model initialized.")

    def detection_callback(self, msg):
        obj_id = msg.object_id
        
        # If object is new or confidence is higher, update it
        if obj_id not in self.objects or msg.confidence > self.objects[obj_id].confidence:
            self.objects[obj_id] = msg
            self.get_logger().info(f"Updated {obj_id} (Class: {msg.class_name}) from {msg.detected_by} with confidence {msg.confidence:.2f}")
            
            # If confidence is below threshold, tag it for active perception
            if msg.confidence < self.confidence_threshold:
                msg.status = "NEEDS_INSPECTION"
                self.get_logger().warn(f"{obj_id} confidence low. Needs active inspection.")
            else:
                msg.status = "CONFIRMED"
                
            self.world_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SemanticWorldModel()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
