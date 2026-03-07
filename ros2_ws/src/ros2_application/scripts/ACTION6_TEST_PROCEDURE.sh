#!/bin/bash
# Complete Action 6 Test Procedure
# Tests static robot → Nav2 goal → joint animation

set -e

WORKSPACE="/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws"

cd $WORKSPACE
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "=============================================="
echo "Action 6 Complete Test - User Instructions"
echo "=============================================="
echo ""
echo "STEP 1: Clean any previous ROS2 processes"
echo "  Run: pkill -9 -f ros2; sleep 2"
echo ""
echo "STEP 2: Launch Action 6"
echo "  cd $WORKSPACE"
echo "  source /opt/ros/humble/setup.bash"
echo "  source install/setup.bash"
echo "  ros2 launch ros2_application rviz_integration.launch.py"
echo ""
echo "STEP 3: Wait ~20 seconds for Nav2 to activate"
echo "  Watch terminal for 'Managed nodes are active'"
echo ""
echo "STEP 4: In RViz, verify TF tree"
echo "  Add → TF → should see map→odom→base_link→wheels"
echo ""
echo "STEP 5: Set initial pose"
echo "  Click '2D Pose Estimate' button"
echo "  Click and drag on map to set pose"
echo ""
echo "STEP 6: Send navigation goal"
echo "  Click '2D Nav Goal' button"
echo "  Click destination on map"
echo ""
echo "EXPECTED BEHAVIOR:"
echo "  ✅ Robot was STATIC before goal"
echo "  ✅ Robot moves along path toward goal"
echo "  ✅ Articulation joint moves when turning"
echo "  ✅ Articulation = 0 when moving straight"
echo "  ✅ All 4 wheels rotate continuously"
echo "  ✅ Robot stops at goal, wheels hold position"
echo ""
echo "VERIFY WITH CLI (in another terminal):"
echo "  # Watch velocity commands"
echo "  ros2 topic echo /cmd_vel"
echo ""
echo "  # Watch joint animation"
echo "  ros2 topic echo /joint_states"
echo ""
echo "=============================================="

