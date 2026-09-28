import rclpy, cv2, numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

rclpy.init()
n = Node('dbg')
bridge = CvBridge()

def cb(msg):
    rgb = bridge.imgmsg_to_cv2(msg, 'bgr8')
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(hsv, np.array([0, 80, 40]), np.array([15, 255, 255]))
    m2 = cv2.inRange(hsv, np.array([165, 80, 40]), np.array([180, 255, 255]))
    mask = m1 | m2
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Total red pixels: {np.sum(mask > 0)}, contours: {len(cnts)}")
    for c in cnts:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        print(f"  Contour area: {area:.1f}, bbox: [{x}, {y}, {w}, {h}]")
    rclpy.shutdown()

sub = n.create_subscription(Image, '/camera', cb, 10)
rclpy.spin(n)
