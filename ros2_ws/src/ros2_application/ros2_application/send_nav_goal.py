import time

import rclpy
from geometry_msgs.msg import PointStamped, PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException


class MapvizNavGoalSender(Node):
    def __init__(self) -> None:
        super().__init__('mapviz_nav_goal_sender')
        self.navigator = BasicNavigator('mapviz_basic_navigator')
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.clicked_point_sub = self.create_subscription(
            PointStamped,
            '/clicked_point',
            self._clicked_point_cb,
            10,
        )

    def _clicked_point_cb(self, msg: PointStamped) -> None:
        if msg.header.frame_id != 'map':
            self.get_logger().warning(
                f'Ignoring /clicked_point in frame {msg.header.frame_id!r}; expected map.'
            )
            return

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = msg.point.x
        pose.pose.position.y = msg.point.y
        pose.pose.position.z = msg.point.z
        pose.pose.orientation.w = 1.0

        self.goal_pub.publish(pose)
        self.navigator.goToPose(pose)
        self.get_logger().info(
            f'Sent Nav2 goal from /clicked_point: x={pose.pose.position.x:.3f}, '
            f'y={pose.pose.position.y:.3f}'
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MapvizNavGoalSender()
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
            time.sleep(0.05)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

