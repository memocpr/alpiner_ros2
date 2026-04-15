#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, NavSatStatus
from nav_msgs.msg import Odometry


class SimGnssPublisher(Node):
    def __init__(self):
        super().__init__('sim_gnss')

        self.frame_id = self.declare_parameter('frame_id', 'gnss_link').value
        self.topic_name = self.declare_parameter('topic_name', '/gps/fix').value
        self.odom_topic = self.declare_parameter('odom_topic', '/odometry/filtered_local').value

        self.origin_latitude = float(self.declare_parameter('latitude', 47.3769).value)
        self.origin_longitude = float(self.declare_parameter('longitude', 8.5417).value)
        self.origin_altitude = float(self.declare_parameter('altitude', 0.0).value)

        self.publish_rate = float(self.declare_parameter('publish_rate', 10.0).value)

        # Simple local XY (meters) -> geodetic approximation around origin.
        # Good enough for simulation over small farm fields.
        self._meters_per_deg_lat = 111320.0
        self._meters_per_deg_lon = (
                111320.0 * math.cos(math.radians(self.origin_latitude))
        )
        if abs(self._meters_per_deg_lon) < 1e-9:
            self._meters_per_deg_lon = 1e-9

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.have_odom = False

        self.publisher = self.create_publisher(NavSatFix, self.topic_name, 10)
        self.subscription = self.create_subscription(
            Odometry,
            self.odom_topic,
            self.odom_callback,
            10,
        )
        self.timer = self.create_timer(1.0 / self.publish_rate, self.publish_fix)

    def odom_callback(self, msg: Odometry) -> None:
        self.current_x = float(msg.pose.pose.position.x)
        self.current_y = float(msg.pose.pose.position.y)
        self.current_z = float(msg.pose.pose.position.z)
        self.have_odom = True

    def publish_fix(self) -> None:
        msg = NavSatFix()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        msg.status.status = NavSatStatus.STATUS_FIX
        msg.status.service = NavSatStatus.SERVICE_GPS

        if self.have_odom:
            msg.latitude = self.origin_latitude + (self.current_y / self._meters_per_deg_lat)
            msg.longitude = self.origin_longitude + (self.current_x / self._meters_per_deg_lon)
            msg.altitude = self.origin_altitude + self.current_z
        else:
            msg.latitude = self.origin_latitude
            msg.longitude = self.origin_longitude
            msg.altitude = self.origin_altitude

        msg.position_covariance = [
            0.5, 0.0, 0.0,
            0.0, 0.5, 0.0,
            0.0, 0.0, 1.0
        ]
        msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_DIAGONAL_KNOWN

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SimGnssPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()