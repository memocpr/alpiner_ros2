#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, NavSatStatus


class SimGnssPublisher(Node):
    def __init__(self):
        super().__init__('sim_gnss')

        self.frame_id = self.declare_parameter('frame_id', 'gnss_link').value
        self.topic_name = self.declare_parameter('topic_name', '/gps/fix').value
        self.latitude = float(self.declare_parameter('latitude', 47.3769).value)
        self.longitude = float(self.declare_parameter('longitude', 8.5417).value)
        self.altitude = float(self.declare_parameter('altitude', 0.0).value)
        self.publish_rate = float(self.declare_parameter('publish_rate', 10.0).value)

        self.publisher = self.create_publisher(NavSatFix, self.topic_name, 10)
        self.timer = self.create_timer(1.0 / self.publish_rate, self.publish_fix)

    def publish_fix(self):
        msg = NavSatFix()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        msg.status.status = NavSatStatus.STATUS_FIX
        msg.status.service = NavSatStatus.SERVICE_GPS

        msg.latitude = self.latitude
        msg.longitude = self.longitude
        msg.altitude = self.altitude

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