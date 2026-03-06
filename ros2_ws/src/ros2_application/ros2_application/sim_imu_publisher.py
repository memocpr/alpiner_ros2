import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


class SimImuPublisher(Node):
    def __init__(self):
        super().__init__('sim_imu_publisher')
        self.publisher = self.create_publisher(Imu, '/imu/data', 10)
        self.timer = self.create_timer(0.05, self._on_timer)
        self.t = 0.0

    def _on_timer(self):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        yaw_rate = 0.2 * math.cos(0.2 * self.t)

        msg.orientation.w = 1.0
        msg.angular_velocity.z = yaw_rate
        msg.linear_acceleration.x = 0.0
        msg.linear_acceleration.y = 0.0
        msg.linear_acceleration.z = 9.81

        msg.orientation_covariance[0] = 0.2
        msg.orientation_covariance[4] = 0.2
        msg.orientation_covariance[8] = 0.3
        msg.angular_velocity_covariance[8] = 0.1
        msg.linear_acceleration_covariance[0] = 0.5
        msg.linear_acceleration_covariance[4] = 0.5
        msg.linear_acceleration_covariance[8] = 0.5

        self.publisher.publish(msg)
        self.t += 0.05


def main(args=None):
    rclpy.init(args=args)
    node = SimImuPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

