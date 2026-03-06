#!/bin/bash

# Simple launch script for robot visualization
# Navigate to workspace
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash

# Process xacro to URDF
URDF_FILE=$(mktemp /tmp/komatsu_XXXXXX.urdf)
xacro src/robot_description/urdf/komatsu.urdf.xacro > $URDF_FILE

echo "✓ URDF generated at: $URDF_FILE"

# Get RViz config path
RVIZ_CONFIG="$(ros2 pkg prefix robot_description)/share/robot_description/rviz/urdf_config.rviz"

# Launch nodes in parallel
echo "Starting robot_state_publisher..."
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat $URDF_FILE)" &
RSP_PID=$!

sleep 2

echo "Starting joint_state_publisher_gui..."
ros2 run joint_state_publisher_gui joint_state_publisher_gui &
JSP_PID=$!

sleep 1

echo "Starting RViz2..."
ros2 run rviz2 rviz2 -d "$RVIZ_CONFIG" &
RVIZ_PID=$!

# Wait for user interrupt
echo ""
echo "✓ All nodes started!"
echo "  - robot_state_publisher (PID: $RSP_PID)"
echo "  - joint_state_publisher_gui (PID: $JSP_PID)"
echo "  - rviz2 (PID: $RVIZ_PID)"
echo ""
echo "Press Ctrl+C to stop all nodes..."

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping nodes..."
    kill $RSP_PID $JSP_PID $RVIZ_PID 2>/dev/null
    rm -f $URDF_FILE
    echo "✓ Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for all processes
wait

