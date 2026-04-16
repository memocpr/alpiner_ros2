#!/usr/bin/env python3
"""
Relay /gps/fix and inject realistic position covariance.

The Gazebo GPS plugin publishes zero covariance, which causes the global UKF
to give GPS measurements infinite weight, leading to map->odom drift.
This node republishes the same message with a fixed covariance matching
typical civilian GPS accuracy (1.5m horizontal, 3m vertical).
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix

# Civilian GPS accuracy (variance = stddev^2)
# Diagonal: East-East, North-North, Up-Up (all others 0)
H_VAR = 2.25   # 1.5m stddev horizontal
V_VAR = 9.0    # 3.0m stddev vertical

GPS_COVARIANCE = [
    H_VAR, 0.0,   0.0,
    0.0,   H_VAR, 0.0,
    0.0,   0.0,   V_VAR,
]


class GpsCovarianceRelay(Node):
    def __init__(self):
        super().__init__('gps_covariance_relay')
        self._pub = self.create_publisher(NavSatFix, '/gps/fix_cov', 10)
        self._sub = self.create_subscription(NavSatFix, '/gps/fix', self._cb, 10)

    def _cb(self, msg: NavSatFix):
        msg.position_covariance = GPS_COVARIANCE
        msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_DIAGONAL_KNOWN
        self._pub.publish(msg)


def main():
    rclpy.init()
    node = GpsCovarianceRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

