import time
import threading
from typing import Optional

import rclpy
from geometry_msgs.msg import PointStamped, PoseStamped
from geographic_msgs.msg import GeoPoint
from nav2_simple_commander.robot_navigator import BasicNavigator
from robot_localization.srv import FromLL
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.duration import Duration
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import tf2_geometry_msgs


class MapvizNavGoalSender(Node):
    def __init__(self) -> None:
        super().__init__('mapviz_nav_goal_sender')
        self.declare_parameter('fromll_source_frame', 'map')
        self.declare_parameter('fromll_timeout_sec', 2.0)
        self._fromll_source_frame = self.get_parameter('fromll_source_frame').get_parameter_value().string_value
        self._fromll_timeout_sec = self.get_parameter('fromll_timeout_sec').get_parameter_value().double_value
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
        self.fromll_client = self.create_client(FromLL, '/fromLL')
        self._nav2_ready = False

    def _ensure_nav2_ready(self) -> None:
        if self._nav2_ready:
            return
        # This stack uses UKF/navsat without AMCL lifecycle, so avoid blocking on a localizer name.
        time.sleep(0.5)
        self._nav2_ready = True

    def _convert_wgs84_to_map(self, msg: PointStamped) -> Optional[PointStamped]:
        # mapviz point_click_publisher in wgs84 uses x=lon, y=lat.
        if not self.fromll_client.wait_for_service(timeout_sec=self._fromll_timeout_sec):
            self.get_logger().warning('Cannot convert wgs84 click: /fromLL service is unavailable.')
            return None

        request = FromLL.Request()
        request.ll_point = GeoPoint(
            latitude=float(msg.point.y),
            longitude=float(msg.point.x),
            altitude=float(msg.point.z),
        )

        future = self.fromll_client.call_async(request)
        deadline = time.monotonic() + self._fromll_timeout_sec
        while rclpy.ok() and not future.done() and time.monotonic() < deadline:
            time.sleep(0.02)

        if not future.done() or future.result() is None:
            self.get_logger().warning(
                f'Failed to convert wgs84 click with /fromLL. exception={future.exception()}'
            )
            return None

        source_point = PointStamped()
        source_point.header.frame_id = self._fromll_source_frame
        source_point.header.stamp = self.get_clock().now().to_msg()
        source_point.point.x = future.result().map_point.x
        source_point.point.y = future.result().map_point.y
        source_point.point.z = future.result().map_point.z

        if self._fromll_source_frame == 'map':
            return source_point

        try:
            transform = self.tf_buffer.lookup_transform(
                'map',
                self._fromll_source_frame,
                rclpy.time.Time(),
                timeout=Duration(seconds=0.5),
            )
            return tf2_geometry_msgs.do_transform_point(source_point, transform)
        except TransformException as exc:
            self.get_logger().warning(
                f'Cannot transform /fromLL output from {self._fromll_source_frame} to map: {exc}'
            )
            return None

    def _send_pose_goal(self, point_stamped: PointStamped, source_frame: str, target_frame: str = 'map') -> None:
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

    def _handle_wgs84_click(self, msg: PointStamped) -> None:
        self._ensure_nav2_ready()
        converted = self._convert_wgs84_to_map(msg)
        if converted is None:
            return
        self._send_pose_goal(converted, source_frame='wgs84')

    def _clicked_point_cb(self, msg: PointStamped) -> None:
        # Accept clicked points from mapviz (may come in 'origin' frame from local_xy_origin)
        target_frame = 'map'
        source_frame = msg.header.frame_id

        if source_frame in ('wgs84', '/wgs84'):
            # Convert WGS84 clicks in a background worker to avoid service deadlocks in callback context.
            threading.Thread(target=self._handle_wgs84_click, args=(msg,), daemon=True).start()
            return
        elif source_frame != target_frame:
            try:
                transform = self.tf_buffer.lookup_transform(
                    target_frame, source_frame,
                    rclpy.time.Time(), timeout=Duration(seconds=0.5)
                )
                point_stamped = tf2_geometry_msgs.do_transform_point(msg, transform)
            except TransformException as e:
                self.get_logger().warning(
                    f'Cannot transform from {source_frame} to {target_frame}: {e}'
                )
                return
        else:
            point_stamped = msg

        self._send_pose_goal(point_stamped, source_frame=source_frame, target_frame=target_frame)


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

