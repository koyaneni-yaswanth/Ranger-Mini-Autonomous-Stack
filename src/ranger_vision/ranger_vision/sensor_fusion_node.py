#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo, PointCloud2
from vision_msgs.msg import Detection2DArray
from cv_bridge import CvBridge
import cv2
import numpy as np
import tf2_ros
from tf2_ros import Buffer, TransformListener
import sensor_msgs_py.point_cloud2 as pc2
import image_geometry

class SensorFusionNode(Node):
    def __init__(self):
        super().__init__('sensor_fusion_node')
        self.get_logger().info('Initializing LiDAR + Camera Fusion Node...')

        self.bridge = CvBridge()
        self.cam_model = image_geometry.PinholeCameraModel()
        
        # TF Buffer and Listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Subscriptions
        self.sub_cam_info = self.create_subscription(CameraInfo, '/camera/camera_info', self.cam_info_cb, 10)
        self.sub_image = self.create_subscription(Image, '/camera', self.image_cb, 10)
        self.sub_lidar = self.create_subscription(PointCloud2, '/lidar/points', self.lidar_cb, 10)
        self.sub_detections = self.create_subscription(Detection2DArray, '/vision/bounding_boxes', self.detections_cb, 10)
        
        # Publishers
        self.pub_fusion_image = self.create_publisher(Image, '/vision/fusion_image', 10)
        
        # State
        self.camera_info = None
        self.latest_image = None
        self.latest_detections = None
        
    def cam_info_cb(self, msg):
        self.camera_info = msg
        self.cam_model.fromCameraInfo(msg)
        
    def image_cb(self, msg):
        self.latest_image = msg
        
    def detections_cb(self, msg):
        self.latest_detections = msg
        
    def lidar_cb(self, msg):
        if self.camera_info is None or self.latest_image is None or self.latest_detections is None:
            return
            
        try:
            trans = self.tf_buffer.lookup_transform(
                self.camera_info.header.frame_id, 
                msg.header.frame_id, 
                rclpy.time.Time(),
                rclpy.duration.Duration(seconds=0.1)
            )
            
            # Quaternion to Rotation Matrix
            q = trans.transform.rotation
            x, y, z, w = q.x, q.y, q.z, q.w
            R = np.array([
                [1 - 2*(y**2 + z**2), 2*(x*y - z*w),     2*(x*z + y*w)],
                [2*(x*y + z*w),     1 - 2*(x**2 + z**2), 2*(y*z - x*w)],
                [2*(x*z - y*w),     2*(y*z + x*w),       1 - 2*(x**2 + y**2)]
            ])
            T = np.array([trans.transform.translation.x, 
                          trans.transform.translation.y, 
                          trans.transform.translation.z])
            
            # Read LiDAR points
            points = list(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True))
            if not points:
                return
            points = np.array(points)
            
            # Transform to Camera Frame
            points_cam = (R @ points.T).T + T
            
            # Filter points behind camera
            points_cam = points_cam[points_cam[:, 2] > 0.0]
            
            cv_image = self.bridge.imgmsg_to_cv2(self.latest_image, desired_encoding='bgr8')
            
            if len(points_cam) > 0 and self.cam_model.fx() is not None:
                # Vectorized projection
                Z = points_cam[:, 2]
                X = points_cam[:, 0]
                Y = points_cam[:, 1]
                
                fx = self.cam_model.fx()
                fy = self.cam_model.fy()
                cx = self.cam_model.cx()
                cy = self.cam_model.cy()
                
                u = (fx * X / Z) + cx
                v = (fy * Y / Z) + cy
                
                for det in self.latest_detections.detections:
                    box_x = int(det.bbox.center.position.x - det.bbox.size_x / 2.0)
                    box_y = int(det.bbox.center.position.y - det.bbox.size_y / 2.0)
                    box_w = int(det.bbox.size_x)
                    box_h = int(det.bbox.size_y)
                    
                    # Boolean mask for points inside the box
                    inside_box = (u >= box_x) & (u <= box_x + box_w) & (v >= box_y) & (v <= box_y + box_h)
                    box_depths = Z[inside_box]
                    
                    if len(box_depths) > 0:
                        median_dist = np.median(box_depths)
                        label = f"{det.results[0].hypothesis.class_id}: {median_dist:.2f}m"
                    else:
                        label = f"{det.results[0].hypothesis.class_id}: ?m"
                        
                    cv2.rectangle(cv_image, (box_x, box_y), (box_x + box_w, box_y + box_h), (255, 165, 0), 2)
                    cv2.putText(cv_image, label, (box_x, box_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                    
            fusion_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
            fusion_msg.header = self.latest_image.header
            self.pub_fusion_image.publish(fusion_msg)
            
        except Exception as e:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = SensorFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
