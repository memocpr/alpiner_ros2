import sys
import time
import math
import yaml

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, Quaternion
from geographic_msgs.msg import GeoPoint
from robot_localization.srv import FromLL
from nav2_simple_commander.robot_navigator import BasicNavigator


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
        while not self.fromll_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("/fromLL service not available, waiting...")

    def gps_to_map_pose(self, latitude: float, longitude: float, yaw: float) -> PoseStamped:
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

        self.get_logger().info(f"Sending {len(map_waypoints)} waypoint(s) to Nav2.")
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