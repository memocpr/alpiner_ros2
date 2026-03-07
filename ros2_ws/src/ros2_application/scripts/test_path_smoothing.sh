#!/bin/bash
# Test script for articulated path smoothing parameters

echo "Testing Articulated Path Smoothing Parameters..."
echo "================================================"

# Wait for Nav2 controller server to be ready
sleep 2

# Test 1: Enable path smoothing
echo ""
echo "Test 1: Enable path smoothing"
ros2 param set /controller_server use_articulated_path_smoothing true
if [ $? -eq 0 ]; then
  echo "✓ Successfully enabled path smoothing"
else
  echo "✗ Failed to enable path smoothing"
fi

# Test 2: Set smoothing window to valid value (5)
echo ""
echo "Test 2: Set smoothing window to 5 (valid, odd)"
ros2 param set /controller_server articulated_path_smoothing_window 5
if [ $? -eq 0 ]; then
  echo "✓ Successfully set smoothing window to 5"
else
  echo "✗ Failed to set smoothing window"
fi

# Test 3: Try invalid smoothing window (even number)
echo ""
echo "Test 3: Try invalid smoothing window (4, even) - should be rejected"
ros2 param set /controller_server articulated_path_smoothing_window 4
if [ $? -ne 0 ]; then
  echo "✓ Correctly rejected even window size"
else
  echo "⚠ Warning: Even window size was accepted (should be odd)"
fi

# Test 4: Try invalid smoothing window (too small)
echo ""
echo "Test 4: Try invalid smoothing window (1, too small) - should be rejected"
ros2 param set /controller_server articulated_path_smoothing_window 1
if [ $? -ne 0 ]; then
  echo "✓ Correctly rejected window size < 3"
else
  echo "⚠ Warning: Small window size was accepted (should be >= 3)"
fi

# Test 5: Set smoothing window back to default
echo ""
echo "Test 5: Set smoothing window back to default (3)"
ros2 param set /controller_server articulated_path_smoothing_window 3
if [ $? -eq 0 ]; then
  echo "✓ Successfully reset smoothing window to 3"
else
  echo "✗ Failed to reset smoothing window"
fi

# Test 6: Test with minimum turning radius constraint
echo ""
echo "Test 6: Set minimum turning radius for curvature constraint"
ros2 param set /controller_server articulated_min_turning_radius 5.0
if [ $? -eq 0 ]; then
  echo "✓ Successfully set minimum turning radius to 5.0m"
  echo "  (Path smoothing will respect this constraint)"
else
  echo "✗ Failed to set minimum turning radius"
fi

# Test 7: Disable path smoothing
echo ""
echo "Test 7: Disable path smoothing"
ros2 param set /controller_server use_articulated_path_smoothing false
if [ $? -eq 0 ]; then
  echo "✓ Successfully disabled path smoothing"
else
  echo "✗ Failed to disable path smoothing"
fi

# Summary
echo ""
echo "================================================"
echo "Path Smoothing Parameter Tests Complete"
echo ""
echo "Current path smoothing configuration:"
ros2 param get /controller_server use_articulated_path_smoothing
ros2 param get /controller_server articulated_path_smoothing_window
ros2 param get /controller_server articulated_min_turning_radius
echo ""
echo "Notes:"
echo "- Path smoothing uses moving average filter on path coordinates"
echo "- Smoothing window must be odd and >= 3"
echo "- Curvature is validated against min_turning_radius if set"
echo "- Endpoint positions are always preserved"
echo "- Orientations are updated to match smoothed segments"

