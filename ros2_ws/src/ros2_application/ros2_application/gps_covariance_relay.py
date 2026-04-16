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
        self._received_fix = False
        self._pub = self.create_publisher(NavSatFix, '/gps/fix_cov', 10)
        self._sub = self.create_subscription(NavSatFix, '/gps/fix', self._cb, 10)
        self._startup_warn_timer = self.create_timer(5.0, self._warn_if_no_fix)

        self.get_logger().info(
            'gps_covariance_relay started. Waiting for /gps/fix and publishing corrected fixes on /gps/fix_cov.'
        )

    def _cb(self, msg: NavSatFix):
        if not self._received_fix:
            self._received_fix = True
            self._startup_warn_timer.cancel()
            self.get_logger().info('Received first /gps/fix message. GNSS covariance relay is active.')

        msg.position_covariance = GPS_COVARIANCE
        msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_DIAGONAL_KNOWN
        self._pub.publish(msg)

    def _warn_if_no_fix(self):
        if not self._received_fix:
            self.get_logger().warning(
                'No /gps/fix messages received yet. GNSS localization chain cannot produce /gps/fix_cov or /odometry/gps until GPS data arrives.'
            )


def main():
    rclpy.init()
    node = GpsCovarianceRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

