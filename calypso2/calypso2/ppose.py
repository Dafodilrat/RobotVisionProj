import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import Vector3, Point
from nav_msgs.msg import Odometry

class SecondTFExtractor(Node):
    def __init__(self):
        super().__init__('calypso2_ground_truth')
        self.subscription = self.create_subscription(
            TFMessage,
            '/world/empty/pose/info',  # or '/tf' if you're listening directly to TF
            self.tf_callback,
            10
        )
        self.pub = self.create_publisher(Odometry, '/calypso2/pose', 10)

    def tf_callback(self, msg):
        
        if len(msg.transforms) >= 2:
            tf = msg.transforms[1]
            odom = Odometry()
            odom.header = tf.header
            odom.header.frame_id='world'
            odom.child_frame_id = 'base_link'
            odom.header.stamp = self.get_clock().now().to_msg()
            translation=tf.transform.translation
            odom.pose.pose.position = Point(x=translation.x, y=translation.y, z=translation.z)
            odom.pose.pose.orientation = tf.transform.rotation
            # Optional: Add dummy covariance
            odom.pose.covariance = [0.001] * 36
            self.pub.publish(odom)

def main(args=None):
    print("starting pose publisher node ......")
    rclpy.init(args=args)
    node = SecondTFExtractor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()       
