import time

import rclpy
from geometry_msgs.msg import PointStamped, PoseStamped
from geographic_msgs.msg import GeoPoint, GeoPose
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

    def _convert_wgs84_to_map(self, msg: PointStamped) -> PointStamped | None:
        # mapviz point_click_publisher in wgs84 uses x=lon, y=lat.
        if not self.fromll_client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warning('Cannot convert wgs84 click: /fromLL service is unavailable.')
            return None

        request = FromLL.Request()
        request.ll_point = GeoPoint(
            latitude=float(msg.point.y),
            longitude=float(msg.point.x),
            altitude=float(msg.point.z),
        )

        future = self.fromll_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)
        if future.result() is None:
            self.get_logger().warning('Failed to convert wgs84 click with /fromLL.')
            return None

        # In this stack, /fromLL outputs coordinates in odom-aligned local XY.
        # Transform to map before sending Nav2 goals.
        odom_point = PointStamped()
        odom_point.header.frame_id = 'odom'
        odom_point.header.stamp = self.get_clock().now().to_msg()
        odom_point.point.x = future.result().map_point.x
        odom_point.point.y = future.result().map_point.y
        odom_point.point.z = future.result().map_point.z

        try:
            transform = self.tf_buffer.lookup_transform(
                'map',
                'odom',
                rclpy.time.Time(),
                timeout=Duration(seconds=0.5),
            )
            return tf2_geometry_msgs.do_transform_point(odom_point, transform)
        except TransformException as exc:
            self.get_logger().warning(
                f'Cannot transform /fromLL output from odom to map: {exc}'
            )
            return None

    def _clicked_point_cb(self, msg: PointStamped) -> None:
        # Accept clicked points from mapviz (may come in 'origin' frame from local_xy_origin)
        target_frame = 'map'
        source_frame = msg.header.frame_id

        if source_frame in ('wgs84', '/wgs84'):
            self._ensure_nav2_ready()
            gps_pose = GeoPose()
            gps_pose.position.latitude = float(msg.point.y)
            gps_pose.position.longitude = float(msg.point.x)
            gps_pose.position.altitude = float(msg.point.z)
            gps_pose.orientation.w = 1.0

            try:
                self.navigator.followGpsWaypoints([gps_pose])
                self.get_logger().info(
                    f'Sent GPS waypoint from /clicked_point (wgs84): '
                    f'lat={gps_pose.position.latitude:.8f}, lon={gps_pose.position.longitude:.8f}'
                )
                return
            except Exception as exc:
                # Fallback for environments without followGpsWaypoints support.
                self.get_logger().warning(
                    f'followGpsWaypoints failed, falling back to map goal conversion: {exc}'
                )
                converted = self._convert_wgs84_to_map(msg)
                if converted is None:
                    return
                point_stamped = converted
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

