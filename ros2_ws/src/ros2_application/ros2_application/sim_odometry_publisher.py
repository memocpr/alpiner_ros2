import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node


class SimOdometryPublisher(Node):
    def __init__(self):
        super().__init__('sim_odometry_publisher')
        self.publisher = self.create_publisher(Odometry, '/odometry/raw', 10)
        self.timer = self.create_timer(0.05, self._on_timer)
        self.t = 0.0

    def _on_timer(self):
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'

        # Gentle forward arc so UKF receives non-zero motion.
        x = 0.2 * self.t
        y = 0.5 * math.sin(0.2 * self.t)
        yaw_rate = 0.2 * math.cos(0.2 * self.t)

        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        msg.pose.pose.orientation.w = 1.0

        msg.twist.twist.linear.x = 0.2
        msg.twist.twist.angular.z = yaw_rate

        msg.pose.covariance[0] = 0.05
        msg.pose.covariance[7] = 0.05
        msg.pose.covariance[35] = 0.1
        msg.twist.covariance[0] = 0.1
        msg.twist.covariance[35] = 0.2

        self.publisher.publish(msg)
        self.t += 0.05


def main(args=None):
    rclpy.init(args=args)
    node = SimOdometryPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

