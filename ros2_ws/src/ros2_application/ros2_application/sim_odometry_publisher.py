import math

import rclpy
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class SimOdometryPublisher(Node):
    def __init__(self):
        super().__init__('sim_odometry_publisher')
        self.publisher = self.create_publisher(Odometry, '/odometry/raw', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.subscription = self.create_subscription(Twist, '/cmd_vel', self._on_cmd_vel, 10)
        self.timer = self.create_timer(0.05, self._on_timer)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.vx = 0.0
        self.wz = 0.0
        self.last_update_time = self.get_clock().now()
        self.last_cmd_time = self.get_clock().now()
        self.cmd_timeout_sec = 0.5

        self.get_logger().info('Sim odometry integrates /cmd_vel into /odometry/raw and broadcasts odom->base_link TF')

    def _on_cmd_vel(self, msg: Twist):
        self.vx = float(msg.linear.x)
        self.wz = float(msg.angular.z)
        self.last_cmd_time = self.get_clock().now()

    def _on_timer(self):
        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds * 1e-9
        self.last_update_time = now
        if dt <= 0.0:
            return

        cmd_age = (now - self.last_cmd_time).nanoseconds * 1e-9
        vx = self.vx if cmd_age <= self.cmd_timeout_sec else 0.0
        wz = self.wz if cmd_age <= self.cmd_timeout_sec else 0.0

        self.yaw += wz * dt
        self.x += vx * math.cos(self.yaw) * dt
        self.y += vx * math.sin(self.yaw) * dt

        msg = Odometry()
        msg.header.stamp = now.to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_footprint'

        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.w = math.cos(self.yaw * 0.5)
        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = math.sin(self.yaw * 0.5)

        msg.twist.twist.linear.x = vx
        msg.twist.twist.linear.y = 0.0
        msg.twist.twist.linear.z = 0.0
        msg.twist.twist.angular.x = 0.0
        msg.twist.twist.angular.y = 0.0
        msg.twist.twist.angular.z = wz

        msg.pose.covariance[0] = 0.05
        msg.pose.covariance[7] = 0.05
        msg.pose.covariance[35] = 0.1
        msg.twist.covariance[0] = 0.1
        msg.twist.covariance[35] = 0.2

        self.publisher.publish(msg)

        # Broadcast TF so RViz can visualize base_link motion
        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation.w = math.cos(self.yaw * 0.5)
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(self.yaw * 0.5)
        self.tf_broadcaster.sendTransform(t)


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
