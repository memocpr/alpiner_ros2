# Action 6 Robot Behavior - Complete Fix Summary

## Problem History

### Issue 1: Robot moving autonomously on launch
**Root cause:** Simulated sensors publishing constant motion data
**Fix:** Modified sim publishers to provide static robot state (position 0,0,0, velocity 0)

### Issue 2: Joints rolling continuously when idle
**Root cause:** Joint state publisher was integrating zero velocity commands
**Fix:** Only integrate wheel positions when velocity > threshold (1e-6)

### Issue 3: Articulation showing max angle for straight motion  
**Root cause:** Logic only checked linear velocity, not angular
**Fix:** Return 0.0 when both linear_x < 1e-3 OR angular_z < 1e-6

## Final Expected Behavior

### On Launch (No Nav2 Goal)
✅ Robot position: (0, 0, 0)
✅ Robot velocity: ~0 (< 1e-13 floating point noise)
✅ `/cmd_vel` topic: NOT publishing
✅ Articulation joint: 0.0 rad
✅ Wheel joints: 0.0 rad (all wheels at zero position)
✅ Robot static in RViz

### During Nav2 Goal Execution
✅ Robot moves toward goal in RViz
✅ `/cmd_vel` actively publishing velocity commands
✅ Articulation joint:
   - 0.0 when moving straight
   - Non-zero (±max 0.35 rad) when turning
✅ Wheel joints:
   - Continuously rotating (position increasing)
   - Left/right wheels may rotate at different speeds when turning
   - Rotation reflects linear + angular velocity

### After Goal Reached / Robot Stops
✅ Robot velocity: ~0
✅ `/cmd_vel` stops publishing (or publishes zero)
✅ Articulation joint: returns to 0.0
✅ Wheel joints: HOLD their last position (don't reset to zero)

## Key Design Principles

1. **Odometry/IMU/Scan**: Provide static environment, no autonomous motion
2. **Articulation**: Follows cmd_vel command directly (no integration)
3. **Wheels**: Integrate velocity only when moving (preserve position when stopped)
4. **Velocity threshold**: 1e-6 rad/s to avoid float precision drift

## Files Modified

1. `sim_odometry_publisher.py` - Static position/velocity
2. `sim_imu_publisher.py` - Static orientation/angular velocity
3. `sim_scan_publisher.py` - Fixed environment (no moving obstacles)
4. `cmd_vel_joint_state_publisher.py` - Conditional integration + articulation fix
5. `rtabmap_params.yaml` - Dedicated DB path with auto-delete for clean restarts
6. `README.md` - Documented expected behavior

## Test Commands

### Rebuild
```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select ros2_application
source install/setup.bash
```

### Launch Action 6
```bash
ros2 launch ros2_application rviz_integration.launch.py
```

### Verify Static State
```bash
./src/ros2_application/scripts/action6_quick_check.sh
```

### Test in RViz
1. Set **2D Pose Estimate** (click and drag to set orientation)
2. Send **2D Nav Goal** (click destination)
3. Observe:
   - Robot moves along global/local path
   - Wheels rotate
   - Articulation changes when turning
4. After goal reached, robot stops but wheels keep their rotation angle

### CLI Test (without RViz)
```bash
# Publish forward motion
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5}}'

# Observe joints (wheels rotating, articulation=0)
ros2 topic echo /joint_states

# Publish turning motion
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5}, angular: {z: 0.3}}'

# Observe joints (wheels rotating, articulation non-zero)
ros2 topic echo /joint_states

# Stop
# Ctrl+C the publisher

# Observe joints hold position (articulation returns to 0, wheels keep angle)
ros2 topic echo /joint_states --once
```

## Status

✅ All fixes implemented
✅ Tested with isolated joint state publisher
✅ Ready for full Action 6 RViz test

