#!/bin/bash
# Test script for Gazebo robot visualization

echo "=== Gazebo Robot Model Test ==="
echo ""

# Clean up any existing Gazebo processes
echo "1. Cleaning up existing Gazebo processes..."
killall -9 gzserver gzclient 2>/dev/null
sleep 1

# Source workspace
echo "2. Sourcing workspace..."
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash

# Test xacro processing
echo "3. Testing xacro processing..."
xacro src/robot_description/urdf/komatsu_gazebo.urdf.xacro > /tmp/test_robot.urdf
if [ $? -eq 0 ]; then
    echo "   ✓ Xacro processing successful"
    link_count=$(grep -c "<link name=" /tmp/test_robot.urdf)
    echo "   ✓ Robot has $link_count links"
else
    echo "   ✗ Xacro processing failed"
    exit 1
fi

# Check robot_description topic
echo "4. Launching Gazebo (this will take ~10 seconds)..."
echo "   - Watch for 'Successfully spawned entity' message"
echo "   - Gazebo GUI should show the Komatsu robot model"
echo ""

ros2 launch robot_description gazebo.launch.py

