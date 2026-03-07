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
        self.t = 0.0

        self.num_beams = 360
        self.angle_min = -math.pi
        self.angle_max = math.pi
        self.angle_increment = (self.angle_max - self.angle_min) / self.num_beams

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

        # Simple synthetic environment with a moving frontal obstacle.
        obstacle_distance = 3.0 + 0.5 * math.sin(0.2 * self.t)
        ranges = []
        for i in range(self.num_beams):
            angle = self.angle_min + i * self.angle_increment
            distance = 12.0

            # Frontal sector: obstacle used to create map structure over time.
            if abs(angle) < 0.35:
                distance = min(distance, obstacle_distance)

            # Side corridor walls.
            if abs(abs(angle) - math.pi / 2.0) < 0.15:
                distance = min(distance, 4.0)

            ranges.append(float(distance))

        msg.ranges = ranges

        self.publisher.publish(msg)
        self.t += 0.1


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
