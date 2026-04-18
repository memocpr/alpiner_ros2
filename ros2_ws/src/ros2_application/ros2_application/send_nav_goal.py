import time

import rclpy
from geometry_msgs.msg import PointStamped, PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import tf2_geometry_msgs
from math import atan2


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
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def _clicked_point_cb(self, msg: PointStamped) -> None:
        # Accept clicked points from mapviz (may come in 'origin' frame from local_xy_origin)
        target_frame = 'map'
        source_frame = msg.header.frame_id

        # If clicked point is in 'origin' frame, transform to 'map'
        if source_frame != target_frame:
            try:
                transform = self.tf_buffer.lookup_transform(
                    target_frame, source_frame,
                    rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=0.5)
                )
                point_stamped = tf2_geometry_msgs.do_transform_point(msg, transform)
            except TransformException as e:
                self.get_logger().warning(
                    f'Cannot transform from {source_frame} to {target_frame}: {e}'
                )
                return
        else:
            point_stamped = msg

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = point_stamped.point.x
        pose.pose.position.y = point_stamped.point.y
        pose.pose.position.z = point_stamped.point.z
        pose.pose.orientation.w = 1.0

        self.goal_pub.publish(pose)
        self.navigator.goToPose(pose)
        self.get_logger().info(
            f'Sent Nav2 goal from /clicked_point ({source_frame} -> {target_frame}): '
            f'x={pose.pose.position.x:.3f}, y={pose.pose.position.y:.3f}'
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

