#!/bin/bash
# Action 7 Quick Test Script
# Tests Gazebo integration for AlpineR navigation stack

set -e

WORKSPACE="/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws"

echo "=========================================="
echo "Action 7: Gazebo Simulation - Quick Test"
echo "=========================================="
echo ""

cd $WORKSPACE

# Test 1: Verify build
echo "Test 1: Building robot_description package..."
colcon build --packages-select robot_description 2>&1 | tail -5
echo "✅ Build completed"
echo ""

# Test 2: Verify files installed
echo "Test 2: Checking installed files..."
source install/setup.bash

if [ -f "install/robot_description/share/robot_description/launch/gazebo.launch.py" ]; then
    echo "✅ gazebo.launch.py installed"
else
    echo "❌ gazebo.launch.py NOT found"
    exit 1
fi

if [ -f "install/robot_description/share/robot_description/urdf/komatsu_gazebo.urdf.xacro" ]; then
    echo "✅ komatsu_gazebo.urdf.xacro installed"
else
    echo "❌ komatsu_gazebo.urdf.xacro NOT found"
    exit 1
fi

if [ -f "install/robot_description/share/robot_description/worlds/farm_field.world" ]; then
    echo "✅ farm_field.world installed"
else
    echo "❌ farm_field.world NOT found"
    exit 1
fi
echo ""

# Test 3: Validate URDF
echo "Test 3: Validating Gazebo URDF..."
xacro install/robot_description/share/robot_description/urdf/komatsu_gazebo.urdf.xacro > /tmp/gazebo_test.urdf 2>&1
if [ $? -eq 0 ]; then
    echo "✅ URDF xacro processing successful"
    rm /tmp/gazebo_test.urdf
else
    echo "❌ URDF xacro processing failed"
    exit 1
fi
echo ""

# Test 4: Check Gazebo packages
echo "Test 4: Checking Gazebo ROS packages..."
if dpkg -l | grep -q "ros-humble-gazebo-ros-pkgs"; then
    echo "✅ gazebo-ros-pkgs installed"
else
    echo "⚠️  gazebo-ros-pkgs NOT installed"
    echo "   Install with: sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros"
fi
echo ""

# Test 5: List available launch files
echo "Test 5: Available launch files in robot_description:"
ls -1 install/robot_description/share/robot_description/launch/*.py | xargs -n1 basename
echo ""

# Test 6: Check documentation
echo "Test 6: Checking documentation..."
if [ -f "src/robot_description/README.md" ]; then
    echo "✅ robot_description/README.md present"
else
    echo "⚠️  robot_description/README.md missing"
fi

if grep -q "Action 7" src/ros2_application/README.md 2>/dev/null; then
    echo "✅ Action 7 documented in ros2_application/README.md"
else
    echo "⚠️  Action 7 not documented in ros2_application/README.md"
fi

if [ -f "ACTION7_SUMMARY.md" ]; then
    echo "✅ ACTION7_SUMMARY.md present"
else
    echo "⚠️  ACTION7_SUMMARY.md missing"
fi
echo ""

echo "=========================================="
echo "Action 7 Quick Test Summary"
echo "=========================================="
echo "✅ All critical tests passed"
echo ""
echo "To launch Gazebo simulation:"
echo "  ros2 launch robot_description gazebo.launch.py"
echo ""
echo "For full stack integration, see:"
echo "  src/ros2_application/README.md (Action 7 section)"
echo "  ACTION7_SUMMARY.md"
echo "=========================================="

