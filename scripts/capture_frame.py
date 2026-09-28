import rclpy, cv2, numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

rclpy.init()
n = Node('frame_capture')
bridge = CvBridge()

def cb(msg):
    rgb = bridge.imgmsg_to_cv2(msg, 'bgr8')
    cv2.imwrite('/tmp/camera_frame.png', rgb)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    print("Frame saved to /tmp/camera_frame.png. Size:", rgb.shape)
    # Find all pixels where Red is dominant (R > G + 40 and R > B + 40)
    b, g, r = cv2.split(rgb)
    red_dominant = (r.astype(int) - g.astype(int) > 40) & (r.astype(int) - b.astype(int) > 40)
    print("Total pixels with R > G+40 & R > B+40:", np.sum(red_dominant))
    if np.sum(red_dominant) > 0:
        hsv_red = hsv[red_dominant]
        print(f"H range: [{np.min(hsv_red[:,0])}, {np.max(hsv_red[:,0])}]")
        print(f"S range: [{np.min(hsv_red[:,1])}, {np.max(hsv_red[:,1])}]")
        print(f"V range: [{np.min(hsv_red[:,2])}, {np.max(hsv_red[:,2])}]")
    rclpy.shutdown()

sub = n.create_subscription(Image, '/camera', cb, 10)
rclpy.spin(n)
