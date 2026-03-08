#!/bin/bash
# Quick launcher for RViz with Gazebo simulation
# Usage: ./run_rviz.sh (launches RViz only, assumes other terminals have Gazebo+Nav2 running)

set -e

WS_DIR="/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws"

echo "=== Launching RViz for Gazebo + Nav2 ==="
cd "$WS_DIR"
source /opt/ros/humble/setup.bash
source install/setup.bash

echo ""
echo "RViz will open with Nav2 visualization."
echo ""
echo "Before setting goals, you need to:"
echo "1. Set 2D Pose Estimate (click button in toolbar, click on map)"
echo "2. Click Nav2 Goal button"
echo "3. Click on map where robot should go"
echo ""

ros2 run rviz2 rviz2 \
  -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz

