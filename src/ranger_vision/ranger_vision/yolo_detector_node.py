import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import cv2
import numpy as np

class YoloDetectorNode(Node):
    def __init__(self):
        super().__init__('vision_detector_node')
        
        self.get_logger().info('Initializing OpenCV HOG Pedestrian Detector (Fallback from YOLOv8 due to network limits)...')
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.get_logger().info('HOG Detector loaded successfully.')

        self.bridge = CvBridge()
        
        self.subscription = self.create_subscription(
            Image,
            '/camera',
            self.image_callback,
            10)
            
        self.image_pub = self.create_publisher(Image, '/vision/detections', 10)
        self.bbox_pub = self.create_publisher(Detection2DArray, '/vision/bounding_boxes', 10)

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Detect people in the image
            (regions, _) = self.hog.detectMultiScale(cv_image, 
                                                    winStride=(4, 4),
                                                    padding=(4, 4),
                                                    scale=1.05)
            
            det_array = Detection2DArray()
            det_array.header = msg.header
            
            # Draw bounding boxes and populate messages
            for (x, y, w, h) in regions:
                cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(cv_image, "Person", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                det = Detection2D()
                det.header = msg.header
                det.bbox.center.position.x = float(x + w / 2.0)
                det.bbox.center.position.y = float(y + h / 2.0)
                det.bbox.size_x = float(w)
                det.bbox.size_y = float(h)
                
                hyp = ObjectHypothesisWithPose()
                hyp.hypothesis.class_id = "Person"
                hyp.hypothesis.score = 1.0
                det.results.append(hyp)
                
                det_array.detections.append(det)
            
            annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
            annotated_msg.header = msg.header
            
            self.image_pub.publish(annotated_msg)
            self.bbox_pub.publish(det_array)
            
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
