import sys
import time
import math
from typing import Optional
import yaml

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

from geometry_msgs.msg import PointStamped, PoseStamped, Quaternion
from geographic_msgs.msg import GeoPoint
from nav2_simple_commander.robot_navigator import BasicNavigator
from robot_localization.srv import FromLL
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
import tf2_geometry_msgs


def quaternion_from_euler(roll: float, pitch: float, yaw: float) -> Quaternion:
    q = Quaternion()

    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    q.w = cy * cp * cr + sy * sp * sr
    q.x = cy * cp * sr - sy * sp * cr
    q.y = sy * cp * sr + cy * sp * cr
    q.z = sy * cp * cr - cy * sp * sr
    return q


class YamlWaypointParser:
    def __init__(self, yaml_file_path: str) -> None:
        with open(yaml_file_path, "r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

    def get_waypoints(self):
        return self.data["waypoints"]


class GpsWaypointFollower(Node):
    def __init__(self, yaml_file_path: str) -> None:
        super().__init__("gps_waypoint_follower")
        self.declare_parameter('fromll_source_frame', 'map')
        self.declare_parameter('fromll_timeout_sec', 2.0)
        self._fromll_source_frame = self.get_parameter('fromll_source_frame').get_parameter_value().string_value
        self._fromll_timeout_sec = self.get_parameter('fromll_timeout_sec').get_parameter_value().double_value

        self.navigator = BasicNavigator("gps_waypoint_basic_navigator")
        self.parser = YamlWaypointParser(yaml_file_path)
        self.fromll_client = self.create_client(FromLL, '/fromLL')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def _convert_ll_to_map_pose(self, latitude: float, longitude: float, yaw: float) -> Optional[PoseStamped]:
        if not self.fromll_client.wait_for_service(timeout_sec=self._fromll_timeout_sec):
            self.get_logger().warning('Cannot convert waypoint: /fromLL service is unavailable.')
            return None

        request = FromLL.Request()
        request.ll_point = GeoPoint(latitude=float(latitude), longitude=float(longitude), altitude=0.0)

        future = self.fromll_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=self._fromll_timeout_sec)
        if future.result() is None:
            self.get_logger().warning(
                f'Failed to convert GPS waypoint with /fromLL. exception={future.exception()}'
            )
            return None

        source_point = PointStamped()
        source_point.header.frame_id = self._fromll_source_frame
        source_point.header.stamp = self.get_clock().now().to_msg()
        source_point.point.x = future.result().map_point.x
        source_point.point.y = future.result().map_point.y
        source_point.point.z = future.result().map_point.z

        point_map = source_point
        if self._fromll_source_frame != 'map':
            try:
                transform = self.tf_buffer.lookup_transform(
                    'map',
                    self._fromll_source_frame,
                    rclpy.time.Time(),
                    timeout=Duration(seconds=0.5),
                )
                point_map = tf2_geometry_msgs.do_transform_point(source_point, transform)
            except TransformException as exc:
                self.get_logger().warning(
                    f'Cannot transform /fromLL output from {self._fromll_source_frame} to map: {exc}'
                )
                return None

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(point_map.point.x)
        pose.pose.position.y = float(point_map.point.y)
        pose.pose.position.z = float(point_map.point.z)
        pose.pose.orientation = quaternion_from_euler(0.0, 0.0, float(yaw))
        return pose

    def run(self) -> None:
        self.get_logger().info("Waiting briefly for Nav2 servers...")
        time.sleep(2.0)

        map_waypoints = []
        for wp in self.parser.get_waypoints():
            latitude = wp["latitude"]
            longitude = wp["longitude"]
            yaw = wp.get("yaw", 0.0)

            pose = self._convert_ll_to_map_pose(latitude, longitude, yaw)
            if pose is None:
                continue

            map_waypoints.append(pose)
            self.get_logger().info(
                f"Loaded GPS waypoint: lat={float(latitude):.8f}, lon={float(longitude):.8f}, yaw={float(yaw):.3f} -> x={pose.pose.position.x:.3f}, y={pose.pose.position.y:.3f}"
            )

        if not map_waypoints:
            raise RuntimeError("No valid waypoint could be converted to map frame.")

        self.get_logger().info(f"Sending {len(map_waypoints)} converted waypoint(s) to Nav2 /follow_waypoints.")
        self.navigator.followWaypoints(map_waypoints)

        while not self.navigator.isTaskComplete():
            time.sleep(0.1)

        result = self.navigator.getResult()
        self.get_logger().info(f"Waypoint task finished with result: {result}")


def main() -> None:
    rclpy.init()

    if len(sys.argv) < 2:
        print("Usage: ros2 run ros2_application gps_waypoint_follower <waypoints.yaml>")
        return

    yaml_file_path = sys.argv[1]

    node = GpsWaypointFollower(yaml_file_path)
    node.run()
    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()