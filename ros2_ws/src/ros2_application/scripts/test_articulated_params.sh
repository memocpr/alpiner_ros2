#!/bin/bash
# Quick runtime test for Action 5 articulated steering parameter validation
# Tests dynamic parameter updates with ros2 param set

set -e

echo "========================================="
echo "Action 5: RPP Articulated Params Test"
echo "========================================="
echo ""

# Check if controller_server is running
if ! ros2 node list | grep -q "/controller_server"; then
    echo "ERROR: controller_server node not found!"
    echo "Please launch Nav2 first with:"
    echo "  ros2 launch nav2_bringup navigation_launch.py"
    exit 1
fi

CONTROLLER_NODE="/controller_server"
PARAM_PREFIX="FollowPath"

echo "Testing articulated steering parameter validation..."
echo ""

# Test 1: Valid curvature scale update
echo "Test 1: Set articulated_curvature_scale to valid value (1.5)"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_curvature_scale 1.5; then
    echo "✓ PASS: Valid curvature scale accepted"
else
    echo "✗ FAIL: Valid curvature scale rejected"
fi
echo ""

# Test 2: Invalid curvature scale (zero)
echo "Test 2: Set articulated_curvature_scale to invalid value (0.0) - should reject"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_curvature_scale 0.0 2>&1 | grep -q "Failed"; then
    echo "✓ PASS: Invalid curvature scale (0.0) rejected as expected"
else
    echo "✗ FAIL: Invalid curvature scale (0.0) was accepted (should reject)"
fi
echo ""

# Test 3: Invalid curvature scale (negative)
echo "Test 3: Set articulated_curvature_scale to invalid value (-1.0) - should reject"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_curvature_scale -1.0 2>&1 | grep -q "Failed"; then
    echo "✓ PASS: Invalid curvature scale (-1.0) rejected as expected"
else
    echo "✗ FAIL: Invalid curvature scale (-1.0) was accepted (should reject)"
fi
echo ""

# Test 4: Valid min turning radius
echo "Test 4: Set articulated_min_turning_radius to valid value (2.5)"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_min_turning_radius 2.5; then
    echo "✓ PASS: Valid min turning radius accepted"
else
    echo "✗ FAIL: Valid min turning radius rejected"
fi
echo ""

# Test 5: Valid min turning radius (zero - disables constraint)
echo "Test 5: Set articulated_min_turning_radius to 0.0 (disables constraint)"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_min_turning_radius 0.0; then
    echo "✓ PASS: Min turning radius 0.0 accepted (constraint disabled)"
else
    echo "✗ FAIL: Min turning radius 0.0 rejected"
fi
echo ""

# Test 6: Invalid min turning radius (negative)
echo "Test 6: Set articulated_min_turning_radius to invalid value (-1.0) - should reject"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_min_turning_radius -1.0 2>&1 | grep -q "Failed"; then
    echo "✓ PASS: Invalid min turning radius (-1.0) rejected as expected"
else
    echo "✗ FAIL: Invalid min turning radius (-1.0) was accepted (should reject)"
fi
echo ""

# Test 7: Valid wheelbase update
echo "Test 7: Set articulated_wheelbase to valid value (3.03)"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_wheelbase 3.03; then
    echo "✓ PASS: Valid articulated_wheelbase accepted"
else
    echo "✗ FAIL: Valid articulated_wheelbase rejected"
fi
echo ""

# Test 8: Invalid wheelbase (zero)
echo "Test 8: Set articulated_wheelbase to invalid value (0.0) - should reject"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_wheelbase 0.0 2>&1 | grep -q "Failed"; then
    echo "✓ PASS: Invalid articulated_wheelbase (0.0) rejected as expected"
else
    echo "✗ FAIL: Invalid articulated_wheelbase (0.0) was accepted (should reject)"
fi
echo ""

# Test 9: Valid max joint angle update
echo "Test 9: Set articulated_max_joint_angle to valid value (0.392)"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_max_joint_angle 0.392; then
    echo "✓ PASS: Valid articulated_max_joint_angle accepted"
else
    echo "✗ FAIL: Valid articulated_max_joint_angle rejected"
fi
echo ""

# Test 10: Invalid max joint angle (zero)
echo "Test 10: Set articulated_max_joint_angle to invalid value (0.0) - should reject"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_max_joint_angle 0.0 2>&1 | grep -q "Failed"; then
    echo "✓ PASS: Invalid articulated_max_joint_angle (0.0) rejected as expected"
else
    echo "✗ FAIL: Invalid articulated_max_joint_angle (0.0) was accepted (should reject)"
fi
echo ""

# Test 11: Valid max joint angular velocity update
echo "Test 11: Set articulated_max_joint_angular_velocity to valid value (0.196)"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_max_joint_angular_velocity 0.196; then
    echo "✓ PASS: Valid articulated_max_joint_angular_velocity accepted"
else
    echo "✗ FAIL: Valid articulated_max_joint_angular_velocity rejected"
fi
echo ""

# Test 12: Invalid max joint angular velocity (negative)
echo "Test 12: Set articulated_max_joint_angular_velocity to invalid value (-0.1) - should reject"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_max_joint_angular_velocity -0.1 2>&1 | grep -q "Failed"; then
    echo "✓ PASS: Invalid articulated_max_joint_angular_velocity (-0.1) rejected as expected"
else
    echo "✗ FAIL: Invalid articulated_max_joint_angular_velocity (-0.1) was accepted (should reject)"
fi
echo ""

# Test 13: Toggle articulated mode
echo "Test 13: Toggle use_articulated_steering_mode"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_steering_mode true; then
    echo "✓ PASS: Articulated mode enabled"
else
    echo "✗ FAIL: Failed to enable articulated mode"
fi
echo ""

if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_steering_mode false; then
    echo "✓ PASS: Articulated mode disabled"
else
    echo "✗ FAIL: Failed to disable articulated mode"
fi
echo ""

# Test 14: Toggle articulated yaw rate clamp
echo "Test 14: Toggle use_articulated_yaw_rate_clamp"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_yaw_rate_clamp true; then
    echo "✓ PASS: Articulated yaw rate clamp enabled"
else
    echo "✗ FAIL: Failed to enable articulated yaw rate clamp"
fi
echo ""

if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_yaw_rate_clamp false; then
    echo "✓ PASS: Articulated yaw rate clamp disabled"
else
    echo "✗ FAIL: Failed to disable articulated yaw rate clamp"
fi
echo ""

# Test 15: Toggle articulated path smoothing
echo "Test 15: Toggle use_articulated_path_smoothing"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_path_smoothing true; then
    echo "✓ PASS: Articulated path smoothing enabled"
else
    echo "✗ FAIL: Failed to enable articulated path smoothing"
fi
echo ""

if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_path_smoothing false; then
    echo "✓ PASS: Articulated path smoothing disabled"
else
    echo "✗ FAIL: Failed to disable articulated path smoothing"
fi
echo ""

# Test 16: Valid smoothing window
echo "Test 16: Set articulated_path_smoothing_window to valid value (5)"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_path_smoothing_window 5; then
    echo "✓ PASS: Valid articulated_path_smoothing_window accepted"
else
    echo "✗ FAIL: Valid articulated_path_smoothing_window rejected"
fi
echo ""

# Test 17: Invalid smoothing window (even)
echo "Test 17: Set articulated_path_smoothing_window to invalid value (4) - should reject"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_path_smoothing_window 4 2>&1 | grep -q "Failed"; then
    echo "✓ PASS: Invalid articulated_path_smoothing_window (4) rejected as expected"
else
    echo "✗ FAIL: Invalid articulated_path_smoothing_window (4) was accepted (should reject)"
fi
echo ""

# Test 18: Invalid smoothing window (too small)
echo "Test 18: Set articulated_path_smoothing_window to invalid value (1) - should reject"
if ros2 param set ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_path_smoothing_window 1 2>&1 | grep -q "Failed"; then
    echo "✓ PASS: Invalid articulated_path_smoothing_window (1) rejected as expected"
else
    echo "✗ FAIL: Invalid articulated_path_smoothing_window (1) was accepted (should reject)"
fi
echo ""

# Display current parameter values
echo "========================================="
echo "Current articulated parameter values:"
echo "========================================="
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_steering_mode
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_curvature_scale
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_min_turning_radius
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_wheelbase
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_max_joint_angle
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_max_joint_angular_velocity
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_yaw_rate_clamp
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.use_articulated_path_smoothing
ros2 param get ${CONTROLLER_NODE} ${PARAM_PREFIX}.articulated_path_smoothing_window
echo ""

echo "========================================="
echo "Test sequence completed"
echo "========================================="
