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
