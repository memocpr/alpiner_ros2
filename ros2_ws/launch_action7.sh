#!/bin/bash
# Helper script to launch Action 7 with proper environment setup

cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws

# Source ROS2 humble
source /opt/ros/humble/setup.bash

# Manually add install paths for ros2_application
export PYTHONPATH="/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws/install/ros2_application/lib/python3.10/site-packages:${PYTHONPATH}"
export CMAKE_PREFIX_PATH="/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws/install/ros2_application:${CMAKE_PREFIX_PATH}"

# For ROS2 to find the package, we need to add it to the package index
export AMENT_PREFIX_PATH="/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws/install/ros2_application:/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws/install:${AMENT_PREFIX_PATH}"

echo "🚀 Starting Action 7: Gazebo + Localization + Mapping + Nav2 + RViz"
echo "   Gazebo should open a new window with the farm field..."
echo "   RViz should open for visualization..."
echo ""

# Launch by directly calling the launch file
python3 /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws/install/ros2_application/share/ros2_application/launch/action7_gazebo_stack.launch.py "$@"

echo "✅ Launch completed"

