import sys
import time
import math
import yaml

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, Quaternion
from geographic_msgs.msg import GeoPoint
from sensor_msgs.msg import NavSatFix
from robot_localization.srv import FromLL
from nav2_simple_commander.robot_navigator import BasicNavigator
from tf2_ros import Buffer, TransformException, TransformListener


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
        self.navigator = BasicNavigator("basic_navigator")
        self.parser = YamlWaypointParser(yaml_file_path)

        self.fromll_client = self.create_client(FromLL, "/fromLL")
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.latest_fix = None
        self.fallback_reference_fix = None
        self.fallback_reference_pose = None
        self._logged_fromll_mode = False
        self._logged_fallback_mode = False

        self.create_subscription(NavSatFix, "/gps/fix", self._gps_fix_cb, 10)

    def _gps_fix_cb(self, msg: NavSatFix) -> None:
        self.latest_fix = msg

    def _wait_for_latest_fix(self, timeout_s: float = 15.0) -> NavSatFix:
        deadline = time.monotonic() + timeout_s
        while rclpy.ok() and time.monotonic() < deadline:
            if self.latest_fix is not None:
                return self.latest_fix
            rclpy.spin_once(self, timeout_sec=0.2)

        raise RuntimeError(
            "No /gps/fix messages received. Waypoint follower needs GNSS data to convert latitude/longitude waypoints."
        )

    def _wait_for_current_map_pose(self, timeout_s: float = 15.0) -> PoseStamped:
        deadline = time.monotonic() + timeout_s
        while rclpy.ok() and time.monotonic() < deadline:
            try:
                transform = self.tf_buffer.lookup_transform(
                    "map",
                    "base_footprint",
                    rclpy.time.Time(),
                    timeout=Duration(seconds=0.2),
                )
                pose = PoseStamped()
                pose.header.frame_id = "map"
                pose.header.stamp = self.get_clock().now().to_msg()
                pose.pose.position.x = transform.transform.translation.x
                pose.pose.position.y = transform.transform.translation.y
                pose.pose.position.z = transform.transform.translation.z
                pose.pose.orientation = transform.transform.rotation
                return pose
            except TransformException:
                rclpy.spin_once(self, timeout_sec=0.2)

        raise RuntimeError(
            "TF map -> base_footprint is unavailable. Start navigation bringup before running the waypoint follower."
        )

    def _ensure_fallback_reference(self) -> None:
        if self.fallback_reference_fix is not None and self.fallback_reference_pose is not None:
            return

        self.fallback_reference_fix = self._wait_for_latest_fix()
        self.fallback_reference_pose = self._wait_for_current_map_pose()

        if not self._logged_fallback_mode:
            self.get_logger().info(
                "Using /gps/fix + current TF as fallback because /fromLL is unavailable."
            )
            self._logged_fallback_mode = True

    def _gps_to_map_pose_from_reference(self, latitude: float, longitude: float, yaw: float) -> PoseStamped:
        self._ensure_fallback_reference()

        ref_fix = self.fallback_reference_fix
        ref_pose = self.fallback_reference_pose

        meters_per_deg_lat = 111320.0
        meters_per_deg_lon = 111320.0 * math.cos(math.radians(ref_fix.latitude))
        if abs(meters_per_deg_lon) < 1e-9:
            meters_per_deg_lon = 1e-9

        east_m = (float(longitude) - float(ref_fix.longitude)) * meters_per_deg_lon
        north_m = (float(latitude) - float(ref_fix.latitude)) * meters_per_deg_lat

        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = ref_pose.pose.position.x + east_m
        pose.pose.position.y = ref_pose.pose.position.y + north_m
        pose.pose.position.z = ref_pose.pose.position.z
        pose.pose.orientation = quaternion_from_euler(0.0, 0.0, float(yaw))
        return pose

    def gps_to_map_pose(self, latitude: float, longitude: float, yaw: float) -> PoseStamped:
        if self.fromll_client.wait_for_service(timeout_sec=0.25):
            if not self._logged_fromll_mode:
                self.get_logger().info("Using /fromLL service for GPS waypoint conversion.")
                self._logged_fromll_mode = True

            req = FromLL.Request()
            req.ll_point = GeoPoint(latitude=float(latitude), longitude=float(longitude), altitude=0.0)

            future = self.fromll_client.call_async(req)
            rclpy.spin_until_future_complete(self, future)

            if future.result() is None:
                raise RuntimeError("Failed to call /fromLL service")

            map_point = future.result().map_point

            pose = PoseStamped()
            pose.header.frame_id = "map"
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position.x = map_point.x
            pose.pose.position.y = map_point.y
            pose.pose.position.z = map_point.z
            pose.pose.orientation = quaternion_from_euler(0.0, 0.0, float(yaw))
            return pose

        return self._gps_to_map_pose_from_reference(latitude, longitude, yaw)

    def run(self) -> None:
        self.get_logger().info("Waiting briefly for Nav2 servers...")
        time.sleep(3.0)

        map_waypoints = []
        for wp in self.parser.get_waypoints():
            latitude = wp["latitude"]
            longitude = wp["longitude"]
            yaw = wp.get("yaw", 0.0)

            pose = self.gps_to_map_pose(latitude, longitude, yaw)
            map_waypoints.append(pose)

            self.get_logger().info(
                f"GPS ({latitude}, {longitude}) -> map ({pose.pose.position.x:.3f}, {pose.pose.position.y:.3f})"
            )

        if not map_waypoints:
            raise RuntimeError("No waypoints found in the YAML file.")

        self.get_logger().info(f"Sending {len(map_waypoints)} waypoint(s) to Nav2.")
        if not self.navigator.followWaypoints(map_waypoints):
            raise RuntimeError("Nav2 rejected the FollowWaypoints request.")

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