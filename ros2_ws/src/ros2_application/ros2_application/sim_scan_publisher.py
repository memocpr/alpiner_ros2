import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class SimScanPublisher(Node):
    def __init__(self):
        super().__init__('sim_scan_publisher')
        self.publisher = self.create_publisher(LaserScan, '/scan', 10)
        self.timer = self.create_timer(0.1, self._on_timer)

        self.num_beams = 360
        self.angle_min = -math.pi
        # Keep metadata consistent with ranges length: N = ((max-min)/inc) + 1
        self.angle_increment = (2.0 * math.pi) / (self.num_beams - 1)
        self.angle_max = self.angle_min + self.angle_increment * (self.num_beams - 1)

    def _on_timer(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser_frame'

        msg.angle_min = self.angle_min
        msg.angle_max = self.angle_max
        msg.angle_increment = self.angle_increment
        msg.time_increment = 0.0
        msg.scan_time = 0.1
        msg.range_min = 0.1
        msg.range_max = 25.0

        # Static environment for stable mapping
        ranges = []
        for i in range(self.num_beams):
            angle = self.angle_min + i * self.angle_increment
            distance = 12.0

            # Frontal wall at fixed distance
            if abs(angle) < 0.35:
                distance = min(distance, 5.0)

            # Side corridor walls
            if abs(abs(angle) - math.pi / 2.0) < 0.15:
                distance = min(distance, 4.0)

            ranges.append(float(distance))

        msg.ranges = ranges

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SimScanPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
