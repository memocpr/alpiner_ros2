#!/bin/bash
# Figure-8 waypoint test for articulated vehicle turning evaluation
# Tests full left/right turns with realistic turning radius

set -e

echo "=== Figure-8 Waypoint Test ==="
echo "This test sends a figure-8 path with sharp turns to evaluate:"
echo "  - Articulation joint rate limiting"
echo "  - Left/right turn behavior"
echo "  - Return to start point accuracy"
echo ""

# Source ROS2 workspace
source /opt/ros/humble/setup.bash
source /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws/install/setup.bash

# Parameters
TURN_RADIUS=3.0  # meters, tight turn for articulated vehicle
FORWARD_DIST=6.0 # meters

echo "Turn radius: ${TURN_RADIUS}m"
echo "Forward distance: ${FORWARD_DIST}m"
echo ""

# Wait for Nav2 to be ready
echo "Waiting for Nav2 bt_navigator..."
timeout 10s bash -c 'until ros2 service list | grep -q navigate_to_pose; do sleep 0.5; done' || {
    echo "ERROR: Nav2 not ready after 10s"
    exit 1
}
echo "Nav2 ready."
echo ""

# Set initial pose at origin
echo "Step 1: Set initial pose at (0, 0, 0)"
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
sleep 1

# Figure-8 waypoints:
# Start (0,0) -> Forward -> Right turn loop -> Cross center -> Left turn loop -> Return to start
#
# Waypoint sequence for figure-8 with 3m turn radius:
#   1. (3.0, 0.0)   - forward
#   2. (6.0, 0.0)   - forward to right loop entry
#   3. (9.0, 3.0)   - right turn start
#   4. (9.0, 6.0)   - right turn apex
#   5. (6.0, 9.0)   - right turn exit
#   6. (3.0, 6.0)   - approach center crossing
#   7. (0.0, 3.0)   - cross center (between loops)
#   8. (-3.0, 0.0)  - left turn start
#   9. (-3.0, -3.0) - left turn apex
#  10. (0.0, -6.0)  - left turn exit
#  11. (3.0, -3.0)  - return path
#  12. (0.0, 0.0)   - back to start

echo "Step 2: Sending figure-8 waypoints..."
echo "  This will take ~2-3 minutes to complete."
echo "  Watch RViz for:"
echo "    - Smooth articulation movement (no sudden jumps)"
echo "    - Full left and right turns"
echo "    - Return to start point"
echo ""

# Use navigate_through_poses action for waypoint sequence
python3 << 'PYTHON_SCRIPT'
import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateThroughPoses
from geometry_msgs.msg import PoseStamped
import math

class Figure8Tester(Node):
    def __init__(self):
        super().__init__('figure8_tester')
        self.action_client = ActionClient(self, NavigateThroughPoses, 'navigate_through_poses')

    def send_figure8(self):
        if not self.action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Action server not available')
            return False

        # Define figure-8 waypoints
        waypoints = [
            (3.0, 0.0),
            (6.0, 0.0),
            (9.0, 3.0),
            (9.0, 6.0),
            (6.0, 9.0),
            (3.0, 6.0),
            (0.0, 3.0),
            (-3.0, 0.0),
            (-3.0, -3.0),
            (0.0, -6.0),
            (3.0, -3.0),
            (0.0, 0.0),
        ]

        goal_msg = NavigateThroughPoses.Goal()
        goal_msg.poses = []

        for i, (x, y) in enumerate(waypoints):
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = 0.0

            # Compute orientation toward next waypoint
            if i < len(waypoints) - 1:
                dx = waypoints[i+1][0] - x
                dy = waypoints[i+1][1] - y
                yaw = math.atan2(dy, dx)
            else:
                yaw = 0.0  # Face forward at end

            pose.pose.orientation.z = math.sin(yaw * 0.5)
            pose.pose.orientation.w = math.cos(yaw * 0.5)

            goal_msg.poses.append(pose)

        self.get_logger().info(f'Sending {len(waypoints)} waypoints for figure-8 path')

        future = self.action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return False

        self.get_logger().info('Goal accepted, executing figure-8...')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=180.0)

        result = result_future.result()
        if result:
            self.get_logger().info('Figure-8 complete!')
            return True
        else:
            self.get_logger().warn('Figure-8 timed out or failed')
            return False

def main():
    rclpy.init()
    node = Figure8Tester()
    success = node.send_figure8()
    node.destroy_node()
    rclpy.shutdown()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
PYTHON_SCRIPT

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=== Figure-8 Test COMPLETE ==="
    echo "Check RViz for:"
    echo "  ✓ Smooth articulation transitions (no sudden jumps)"
    echo "  ✓ Full left and right loop execution"
    echo "  ✓ Final position near (0, 0)"
    echo ""
else
    echo ""
    echo "=== Figure-8 Test FAILED or INCOMPLETE ==="
    echo "Check logs for navigation errors"
    echo ""
fi

exit $EXIT_CODE

