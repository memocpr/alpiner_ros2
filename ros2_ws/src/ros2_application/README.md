# ros2_application

## Action 3: Localization pipeline (UKF)

This package now includes a minimal local-test localization setup:

- `launch/localization.launch.py`
- `config/ukf_params.yaml`
- `ros2_application/sim_odometry_publisher.py`
- `ros2_application/sim_imu_publisher.py`

### Topics

- Inputs:
  - `/odometry/raw` (`nav_msgs/msg/Odometry`)
  - `/imu/data` (`sensor_msgs/msg/Imu`)
- Output:
  - `/odometry/filtered` (`nav_msgs/msg/Odometry`)
- TF:
  - `odom -> base_link` (published by `ukf_node`)

### Run

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application
source install/setup.bash
ros2 launch ros2_application localization.launch.py
```

### Notes

- `robot_localization` must be installed in the environment.
- You can disable simulation sources with:
  - `use_sim_odometry:=false`
  - `use_sim_imu:=false`

## Action 4: Mapping pipeline (RTAB-Map)

This package now includes a minimal local-test mapping setup:

- `launch/mapping.launch.py`
- `config/rtabmap_params.yaml`
- `ros2_application/sim_scan_publisher.py`

### Topics

- Inputs:
  - `/odometry/filtered` (`nav_msgs/msg/Odometry`)
  - `/scan` (`sensor_msgs/msg/LaserScan`)
- Output:
  - `/map`
- TF:
  - `map -> odom` (published by RTAB-Map)
  - `base_link -> laser_frame` (static TF, only in sim scan mode)

### Run

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application
source install/setup.bash
ros2 launch ros2_application mapping.launch.py
```

### Hardware Adaptation

Switch from simulated to real sensor input:

```bash
# Option A: Disable sim scan, remap to real topic
ros2 launch ros2_application mapping.launch.py use_sim_scan:=false scan_topic:=/your_real_scan_topic

# Option B: Use dedicated hardware launch (cleaner)
ros2 launch ros2_application mapping_hw.launch.py scan_topic:=/your_real_scan_topic laser_frame:=/your_laser_frame
```

### Notes

- Start Action 3 first so `/odometry/filtered` is available.
- For retrofit kit: update `scan_topic` and `laser_frame` to match actual hardware TF tree.
- Static TF `base_link -> laser_frame` will be provided by your hardware driver or robot_description URDF.

## Action 5: Nav2 baseline for articulated-steering customization

This workspace now uses a local Nav2 source repo at:

- `src/navigation2`

Baseline integration changes for Action 5:

- `nav2_bringup/params/nav2_params.yaml`
  - `bt_navigator.odom_topic` set to `/odometry/filtered`
  - `controller_server.FollowPath.plugin` switched to `nav2_regulated_pure_pursuit_controller`
  - added RPP articulated-mode parameters:
    - `use_articulated_steering_mode` (default `false`)
    - `articulated_curvature_scale` (default `1.0`)
    - `articulated_min_turning_radius` (default `0.0`, disabled)
    - `articulated_wheelbase` (default `3.03`)
    - `articulated_max_joint_angle` (default `0.35`)
    - `articulated_max_joint_angular_velocity` (default `0.196`)
    - `use_articulated_yaw_rate_clamp` (default `true`)
    - `use_articulated_path_smoothing` (default `false`)
    - `articulated_path_smoothing_window` (default `3`, odd >= 3)
- `planner_server` remains `GridBased` (`nav2_navfn_planner/NavfnPlanner`) for stable baseline before articulated-specific planner changes

### Build (focused)

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --packages-select nav2_planner nav2_regulated_pure_pursuit_controller \
  --allow-overriding nav2_planner nav2_regulated_pure_pursuit_controller
source install/setup.bash
```

### Run Nav2 bringup with current baseline params

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=true \
  params_file:=/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/navigation2/nav2_bringup/params/nav2_params.yaml
```

### Notes

- Keep Action 5 changes minimal and incremental: first parameter-level baseline, then gated code updates in RPP/planner.
- For local test flow: launch Action 3 and Action 4 first so `/odometry/filtered`, `/scan`, and map TF chain are available.
- RPP articulated hooks now include:
  - curvature scaling and min-turning-radius clamp
  - curvature <-> articulation-angle mapping with max joint angle constraint
  - articulation-aware yaw-rate clamp based on max joint angular velocity
  - rotate-to-path in-place guard when articulated mode is enabled
  - optional local path smoothing (default off)
- Dynamic parameter validation now rejects:
  - `articulated_curvature_scale <= 0`
  - `articulated_min_turning_radius < 0`
  - `articulated_wheelbase <= 0`
  - `articulated_max_joint_angle <= 0` or `>= pi/2`
  - `articulated_max_joint_angular_velocity <= 0`
  - `articulated_path_smoothing_window` not odd or `< 3`
  - inconsistent turning radius vs wheelbase/joint-angle limits
- Default behavior parity is preserved when articulated mode is disabled (`false`).
- **Kinematics relationship**: `articulated_wheelbase` and `articulated_max_joint_angle` jointly determine the achievable minimum turning radius via:
  - `min_radius_achievable = wheelbase / (2.0 * sin(max_joint_angle / 2.0))`
  - Current defaults: 3.03 m wheelbase + 0.35 rad max angle ≈ 8.72 m minimum achievable radius
  - If `articulated_min_turning_radius` is set (> 0), it must not exceed this achievable minimum; otherwise validation will warn

### Quick runtime test

After launching Nav2, test articulated parameter validation:

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
./src/ros2_application/scripts/test_articulated_params.sh
```

This script validates:
- Valid/invalid articulated curvature and turning-radius updates
- Valid/invalid articulated wheelbase and joint limits
- Articulated mode and yaw-rate clamp toggles
- Valid/invalid path-smoothing parameter updates

Test path smoothing functionality:

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
./src/ros2_application/scripts/test_path_smoothing.sh
```

This script tests:
- Enabling/disabling path smoothing
- Valid/invalid smoothing window sizes (must be odd, >= 3)
- Minimum turning radius constraint integration
- Parameter configuration and validation


# Action 5 Completion Summary - Articulated Vehicle Path Tracking

## Completed in This Session

### 1. **Articulated In-Place Rotation Guard** ✅
- **Implementation**: Added `canArticulatedRotateInPlace()` method to `RegulatedPurePursuitController`
- **Location**: `nav2_regulated_pure_pursuit_controller/src/regulated_pure_pursuit_controller.cpp`
- **Functionality**:
  - Prevents infeasible in-place rotations for articulated vehicles
  - Returns `true` if:
    - Articulated mode is disabled, OR
    - Steering joint can reach straight-ahead configuration (max_joint_angle > 0)
  - Returns `false` if max_joint_angle ≤ 0 (rigid joint, no steering possible)
- **Integration**: Guard is called during `shouldRotateToGoalHeading` and `shouldRotateToPath` decisions
- **Fallback behavior**: When rotation is infeasible, controller follows path at minimum velocity instead

### 2. **Focused Unit Tests** ✅
- **Test File**: `test/test_articulated_guard.cpp`
- **Test Count**: 9 comprehensive tests
- **Test Coverage**:
  - ✅ Non-articulated vehicles can always rotate
  - ✅ Articulated with sufficient joint angle can rotate
  - ✅ Articulated with very small angle can still rotate (straight configuration achievable)
  - ✅ Articulated with negative/invalid angle cannot rotate
  - ✅ Curvature↔articulation angle mapping produces finite values
  - ✅ Articulation angle↔curvature bidirectional mapping
  - ✅ Yaw rate clamping produces finite values and respects limits
  - ✅ Guard consistency with varying joint angles
  - ✅ Mode switching between articulated/non-articulated
- **Status**: ALL TESTS PASSING (9/9)

### 3. **Documentation** ✅
- **Location**: `README.md` - Added new section "Articulated Vehicle Steering"
- **Content**:
  - Explained articulated mode parameters
  - Documented in-place rotation guard behavior
  - Listed all articulated-specific parameters with descriptions
  - Explained fallback behavior for infeasible rotations
  - Added clarifications on kinematic constraints

### 4. **Path Smoothing for Articulated Geometry** ✅
- **Implementation**: Enhanced `smoothArticulatedPath()` in `RegulatedPurePursuitController`
- **Location**: `nav2_regulated_pure_pursuit_controller/src/regulated_pure_pursuit_controller.cpp`
- **Functionality**:
  - Moving average smoothing applied to both X and Y coordinates (preserves endpoints)
  - Orientation updates to align with smoothed path segments
  - Curvature validation using Menger curvature formula
  - Automatic correction when curvature exceeds `articulated_min_turning_radius` constraint
  - Blends back toward original path when turns are too sharp
- **Parameters**:
  - `use_articulated_path_smoothing` (default `false`) - Enable/disable smoothing
  - `articulated_path_smoothing_window` (default `3`, odd >= 3) - Smoothing window size
  - `articulated_min_turning_radius` (default `0.0`) - Used to validate/constrain curvature
- **Test Coverage**: `test_path_smoothing.cpp` with 9 comprehensive tests

## Key Design Decisions

1. **Guard Logic**: Simple and robust - checks if max_joint_angle allows zero steering angle
2. **Error Handling**: Graceful fallback to path-following with throttled warnings
3. **Parameter Validation**: Guard integrates seamlessly with existing articulated mode logic
4. **Testing**: Comprehensive edge-case coverage without requiring full node initialization
5. **Path Smoothing**: Three-stage approach (smooth positions → update orientations → validate curvature)

## Action 5 Status

✅ **All Action 5 items completed:**
1. ✅ Articulated steering mode with curvature scaling and constraints
2. ✅ Articulation angle ↔ curvature bidirectional mapping
3. ✅ Yaw rate clamping based on joint angular velocity limits
4. ✅ In-place rotation guard for articulated vehicles
5. ✅ Path smoothing with curvature constraint enforcement

## Build & Test Results

```
Compilation:  ✅ SUCCESS (no errors)
Unit Tests:   ✅ SUCCESS (articulated guard: 9/9, path smoothing: 9/9)
Package:      ✅ BUILDS CLEAN
```

## Integration Points

The guard is integrated at two critical decision points in `computeVelocityCommands`:

1. **`shouldRotateToGoalHeading` branch**: Checks before rotating to goal orientation
2. **`shouldRotateToPath` branch**: Checks before rotating to path heading

Both use the same guard pattern:
```cpp
if (canArticulatedRotateInPlace()) {
  rotateToHeading(...);  // Safe to command rotation
} else {
  // Fallback: follow path at minimum velocity
  applyConstraints(...);
  RCLCPP_WARN_THROTTLE(..., "Cannot rotate...");
}
```

**Path smoothing integration**:
```cpp
if (use_articulated_steering_mode_ && use_articulated_path_smoothing_) {
  smoothArticulatedPath(transformed_plan);
}
```

## Recommended Next Steps

1. **Integration testing** with simulated articulated vehicle in Gazebo
2. **Real hardware validation** on retrofit kit loader
3. **Parameter tuning** for specific articulated geometry once hardware integration begins
4. **Proceed to Action 6**: RViz integration test of full navigation stack

