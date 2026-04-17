import os
import sys
import time
import math
import yaml

import rclpy
from rclpy.node import Node

from geographic_msgs.msg import GeoPose
from geometry_msgs.msg import Quaternion
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


def lat_lon_yaw_to_geopose(latitude: float, longitude: float, yaw: float = 0.0) -> GeoPose:
    geopose = GeoPose()
    geopose.position.latitude = float(latitude)
    geopose.position.longitude = float(longitude)
    geopose.position.altitude = 0.0
    geopose.orientation = quaternion_from_euler(0.0, 0.0, float(yaw))
    return geopose


class YamlWaypointParser:
    def __init__(self, yaml_file_path: str) -> None:
        with open(yaml_file_path, "r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

    def get_gps_waypoints(self) -> list[GeoPose]:
        waypoints = []

        for wp in self.data["waypoints"]:
            latitude = wp["latitude"]
            longitude = wp["longitude"]
            yaw = wp.get("yaw", 0.0)

            waypoints.append(lat_lon_yaw_to_geopose(latitude, longitude, yaw))

        return waypoints


class GpsWaypointFollower(Node):
    def __init__(self, yaml_file_path: str) -> None:
        super().__init__("gps_waypoint_follower")
        self.navigator = BasicNavigator("basic_navigator")
        self.parser = YamlWaypointParser(yaml_file_path)

    def run(self) -> None:
        self.get_logger().info("Waiting briefly for Nav2 servers...")
        time.sleep(3.0)

        gps_waypoints = self.parser.get_gps_waypoints()
        self.get_logger().info(f"Loaded {len(gps_waypoints)} GPS waypoint(s).")

        self.navigator.followGpsWaypoints(gps_waypoints)

        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()
            if feedback is not None:
                pass
            time.sleep(0.1)

        result = self.navigator.getResult()
        self.get_logger().info(f"GPS waypoint task finished with result: {result}")


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