#!/bin/bash
# Action 6 Quick Test Script
# Verifies that robot is static without Nav2 goals and shows joint animation when goal is active

set -e

WORKSPACE="/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws"

cd $WORKSPACE
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "=========================================="
echo "Action 6 Static Robot Verification"
echo "=========================================="
echo ""

echo "1. Checking filtered odometry velocity..."
ODOM=$(ros2 topic echo /odometry/filtered --once 2>/dev/null)
LINEAR_X=$(echo "$ODOM" | grep -A1 "linear:" | grep "x:" | awk '{print $2}')
ANGULAR_Z=$(echo "$ODOM" | grep -A3 "angular:" | grep "z:" | awk '{print $2}')

echo "   Linear X:  $LINEAR_X (should be ~0)"
echo "   Angular Z: $ANGULAR_Z (should be ~0)"
echo ""

echo "2. Checking cmd_vel topic..."
timeout 2 ros2 topic echo /cmd_vel --once 2>/dev/null && echo "   ❌ FAIL: cmd_vel is publishing without a goal!" || echo "   ✅ PASS: No cmd_vel (robot is idle)"
echo ""

echo "3. Checking joint_states..."
JOINTS=$(ros2 topic echo /joint_states --once 2>/dev/null)
ARTIC=$(echo "$JOINTS" | grep -A20 "name:" | grep "articulation_to_front" -A1 | tail -1 | awk '{print $2}')
echo "   Articulation angle: $ARTIC rad (should be ~0)"
echo ""

echo "=========================================="
echo "To test with Nav2 goal:"
echo "1. Open RViz"
echo "2. Set 2D Pose Estimate"
echo "3. Send 2D Nav Goal"
echo "4. Observe wheels/articulation animate"
echo "=========================================="

