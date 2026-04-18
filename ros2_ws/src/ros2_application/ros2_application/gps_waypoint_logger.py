#!/usr/bin/env python3

import sys
import select
import yaml
import threading

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import NavSatFix


class GpsWaypointLogger(Node):
    def __init__(self, output_file: str):
        super().__init__('gps_waypoint_logger')

        self.output_file = output_file
        self.latest = None
        self.waypoints = []
        self._stop_requested = False

        self.create_subscription(
            NavSatFix,
            '/gps/fix_cov',
            self.callback,
            qos_profile_sensor_data
        )

        self.get_logger().info('GPS waypoint logger started.')
        self.get_logger().info('Press ENTER to save waypoint, Ctrl+C to finish.')

    def callback(self, msg: NavSatFix):
        self.latest = msg

    def save_waypoint(self):
        if self.latest is None:
            self.get_logger().warning('No GPS data yet.')
            return

        wp = {
            'latitude': float(self.latest.latitude),
            'longitude': float(self.latest.longitude),
            'yaw': 0.0
        }

        self.waypoints.append(wp)
        self.get_logger().info(
            f"Saved waypoint #{len(self.waypoints)}: "
            f"lat={wp['latitude']:.10f}, lon={wp['longitude']:.10f}, yaw={wp['yaw']:.3f}"
        )

    def write_file(self):
        data = {'waypoints': self.waypoints}
        with open(self.output_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, sort_keys=False)
        self.get_logger().info(
            f"Saved {len(self.waypoints)} waypoint(s) to {self.output_file}"
        )

    def input_loop(self):
        try:
            while not self._stop_requested and rclpy.ok():
                ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                if not ready:
                    continue

                line = sys.stdin.readline()
                if line == '':
                    raise EOFError

                self.save_waypoint()
        except (KeyboardInterrupt, EOFError):
            self._stop_requested = True


def main():
    rclpy.init()

    output_file = 'gps_waypoints.yaml'
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    node = GpsWaypointLogger(output_file)

    input_thread = threading.Thread(target=node.input_loop)
    input_thread.start()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node._stop_requested = True
        input_thread.join(timeout=1.0)
        node.write_file()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()