#!/usr/bin/env python3

"""Mock GNSS publisher for local Action_B validation."""

import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import NavSatFix, NavSatStatus
from geometry_msgs.msg import Twist


class SimGnssPublisher(Node):
    """Publish a simple mock GNSS fix derived from commanded motion."""

    def __init__(self):
        super().__init__('sim_gnss')

        self.declare_parameter('frame_id', 'gnss_link')
        self.declare_parameter('publish_rate', 10.0)
        self.declare_parameter('origin_lat', 47.397742)
        self.declare_parameter('origin_lon', 8.545594)
        self.declare_parameter('origin_alt', 0.0)

        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value
        publish_rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        self.origin_lat = self.get_parameter('origin_lat').get_parameter_value().double_value
        self.origin_lon = self.get_parameter('origin_lon').get_parameter_value().double_value
        self.origin_alt = self.get_parameter('origin_alt').get_parameter_value().double_value

        self.x_m = 0.0
        self.y_m = 0.0
        self.yaw = 0.0
        self.vx = 0.0
        self.wz = 0.0
        self.last_time = self.get_clock().now()
        self.last_cmd_time = self.get_clock().now()
        self.cmd_timeout_sec = 0.5

        self.cmd_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10,
        )

        self.fix_pub = self.create_publisher(NavSatFix, '/gps/fix', 10)

        self.timer = self.create_timer(1.0 / max(publish_rate, 1.0), self.timer_callback)

        self.get_logger().info('sim_gnss_publisher started')

    def cmd_vel_callback(self, msg: Twist) -> None:
        """Store latest commanded velocity."""
        self.vx = msg.linear.x
        self.wz = msg.angular.z
        self.last_cmd_time = self.get_clock().now()

    def timer_callback(self) -> None:
        """Integrate simple planar motion and publish mock GNSS."""
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        if dt < 0.0 or dt > 1.0:
            dt = 0.1

        # Zero out velocity if cmd_vel is stale (same as sim_odometry)
        cmd_age = (now - self.last_cmd_time).nanoseconds / 1e9
        vx = self.vx if cmd_age <= self.cmd_timeout_sec else 0.0
        wz = self.wz if cmd_age <= self.cmd_timeout_sec else 0.0

        self.yaw += wz * dt
        self.x_m += vx * math.cos(self.yaw) * dt
        self.y_m += vx * math.sin(self.yaw) * dt

        lat, lon = self.local_xy_to_latlon(self.x_m, self.y_m)

        msg = NavSatFix()
        msg.header.stamp = now.to_msg()
        msg.header.frame_id = self.frame_id

        msg.status.status = NavSatStatus.STATUS_FIX
        msg.status.service = NavSatStatus.SERVICE_GPS

        msg.latitude = lat
        msg.longitude = lon
        msg.altitude = self.origin_alt

        # Simple diagonal covariance, enough for mock validation
        msg.position_covariance = [
            0.25, 0.0, 0.0,
            0.0, 0.25, 0.0,
            0.0, 0.0, 1.0,
        ]
        msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_DIAGONAL_KNOWN

        self.fix_pub.publish(msg)

    def local_xy_to_latlon(self, x_m: float, y_m: float) -> tuple[float, float]:
        """Convert local ENU meters to approximate lat/lon."""
        dlat = y_m / 111320.0
        dlon = x_m / (111320.0 * max(math.cos(math.radians(self.origin_lat)), 1e-6))
        return self.origin_lat + dlat, self.origin_lon + dlon


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SimGnssPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()