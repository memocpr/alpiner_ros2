# ros2_application

## Action 1: Interfaces

### Custom Messages (ros2_interfaces)

Package contains 5 custom messages for machine control:
- `MachineIndAll` - Machine feedback (speed, angles, sensors, timestamps)
- `MachineIndErrors` - Error and safety flags (emergency stops, sensors)
- `MachineIndOthers` - Operating mode and status (engine, brake, PPC lock)
- `MachineSetAll` - Control commands (throttle, brake, steering, gear)
- `MachineSetOptions` - Additional options (parking brake, auto-dig, kick-down)

Build and check:
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_interfaces
source install/setup.bash
ros2 interface list | grep ros2_interfaces
ros2 interface show ros2_interfaces/msg/MachineIndAll
```





## Action 2: Robot model

# Robot Description Package

## Robot Specifications

Based on Komatsu WA380 articulated wheel loader:
- **Overall length**: 8.35 m
- **Wheelbase**: 3.03 m
- **Width**: 2.765 m (over tires)
- **Track width**: 2.16 m
- **Ground clearance**: 0.455 m
- **Overall height**: 3.395 m
- **Articulation angle**: ±0.35 rad (±20°)
- **Wheel radius**: ~0.80 m

## TF Tree

```
map
└── odom
    └── base_footprint
        └── base_link
            ├── articulation_link
            │   ├── rear_chassis
            │   │   ├── rear_left_wheel
            │   │   ├── rear_right_wheel
            │   │   ├── laser_frame
            │   │   └── base_rear
            │   └── front_chassis
            │       ├── front_left_wheel
            │       ├── front_right_wheel
            │       └── base_front
            └── imu_link
```
(`map → odom` published by Nav2/UKF at runtime; rest are static from `robot_description`)


### Visualize in RViz

```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select robot_description
source install/setup.bash
ros2 launch robot_description komatsu_view_robot.launch.py
```

create/update TF tree diagram:
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/robot_description/TFs
ros2 run tf2_tools view_frames
```

### Inertia Implementation

Robot URDF now uses physically accurate inertia calculations following ROS2 best practices:

- **Created** `robot_description/urdf/common_properties.xacro` with inertia macros:
  - `box_inertia` - For chassis components (uses formula: `ixx = (m/12) * (y² + z²)`)
  - `cylinder_inertia` - For wheels (uses formula: `ixx = (m/12) * (3r² + l²)`, `izz = (m/2) * r²`)
  - `sphere_inertia` - For future use

- **Updated** `komatsu.urdf.xacro` and `wheels.xacro` to use inertia macros instead of hardcoded values

- **Result**: Chassis and wheels now have correct inertia tensors calculated from actual geometry, improving Gazebo physics simulation accuracy





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
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application
source install/setup.bash
ros2 launch ros2_application komatsu_localization.launch.py
```

### Notes

- `robot_localization` must be installed in the environment.
- You can disable simulation sources with:
  - `use_sim_odometry:=false`
  - `use_sim_imu:=false`
- **Simulation behavior**: `sim_odometry_publisher` integrates `/cmd_vel` into `/odometry/raw` (with timeout), and `sim_imu_publisher` stays simple/static for local testing.




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
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ros2_application komatsu_mapping.launch.py
```

### Hardware Adaptation

Switch from simulated to real sensor input:

```bash
# Option A: Disable sim scan, remap to real topic
ros2 launch ros2_application komatsu_mapping.launch.py use_sim_scan:=false scan_topic:=/your_real_scan_topic

# Option B: Use dedicated hardware launch (cleaner)
ros2 launch ros2_application komatsu_mapping_hw.launch.py scan_topic:=/your_real_scan_topic laser_frame:=/your_laser_frame
```

### Notes

- Start Action 3 first so `/odometry/filtered` is available.
- For retrofit kit: update `scan_topic` and `laser_frame` to match actual hardware TF tree.
- Static TF `base_link -> laser_frame` will be provided by your hardware driver or robot_description URDF.
- **Simulation behavior**: `sim_scan_publisher` provides a static environment (fixed walls and obstacles). No dynamic obstacles that could trigger false motion detection.
- RTAB-Map local test now uses `/tmp/rtabmap_action6.db` with `delete_db_on_start=true` to avoid stale DB conflicts during repeated launch/stop cycles.


## Action 5: Navigation stack (Nav2)

### Overview

Nav2 navigation stack configured with:
- **Planner**: SmacPlannerHybrid (for articulated vehicles)
- **Controller**: RegulatedPurePursuitController (RPP)
- **Smoother**: SimpleSmoother with path inversion enforcement
- **Velocity Smoother**: 20Hz with acceleration limits
- **Collision Monitor**: Enabled with footprint approach detection

### Launch
Run action 3 and action 4 first to provide `/odometry/filtered` and `/map` inputs for Nav2.
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select robot_bringup robot_description
source install/setup.bash
ros2 launch robot_bringup komatsu_nav2.launch.py
```

### Configuration

Main config: `robot_bringup/config/komatsu_nav2_params.yaml`

**Planner Server (SmacPlannerHybrid)**:
- Expected frequency: 20 Hz
- Tolerance: 0.5 m
- A* disabled (using Hybrid-A* for articulated steering)
- Allows unknown space

**Controller Server (RegulatedPurePursuitController)**:
- Frequency: 20 Hz
- Desired linear velocity: 0.5 m/s
- Lookahead distance: 0.6 m (0.3-0.9 m range)
- Use collision detection: enabled
- Allow reversing: disabled
- Rotate to heading: enabled (min angle 0.785 rad)

**Velocity Smoother**:
- Smoothing frequency: 20 Hz
- Max velocity: [0.5, 0.0, 2.0] m/s, rad/s
- Max acceleration: [2.5, 0.0, 3.2] m/s², rad/s²

### Verify

Check running nodes:
```bash
ros2 node list | grep -E "(planner|controller|bt_navigator|smoother)"
```

Expected output:
- `/bt_navigator`
- `/controller_server`
- `/planner_server`
- `/smoother_server`

Check available actions:
```bash
ros2 action list
```

Expected:
- `/navigate_to_pose`
- `/navigate_through_poses`
- `/follow_path`

### Topics

**Input**:
- `/map` (nav_msgs/OccupancyGrid) — published by RTAB-Map (Action 4)
- `/odometry/filtered` (nav_msgs/Odometry) — published by UKF (Action 3)

**Output**:
- `/cmd_vel` (geometry_msgs/Twist) - velocity commands

### Check lifecycle states:

```bash
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
```
expected state: `active [3]`

Meaning: the Nav2 stack is operational and ready for navigation.

### Notes

- Nav2 is configured for articulated vehicle dynamics
- RPP controller provides smooth path tracking
- Collision monitoring prevents unsafe commands
- Ready for Action 6 RViz integration testing

### Robot Footprint (Nav2)

Nav2 requires a **2D footprint** to represent the robot in the costmaps for collision checking during planning and control.

In this project, the articulated loader is simplified to **one rigid navigation footprint**, even though the vehicle consists of two bodies connected by an articulation joint. Nav2 uses a single reference frame (`base_footprint`) and therefore only one footprint is defined.

The footprint approximates the **outer collision envelope of the vehicle**, including a safety margin to account for articulation sweep.

Vehicle dimensions (approx.)

* Length: ~8.3 m
* Width: ~2.8 m

Navigation footprint used in Nav2:

```yaml
footprint: [
  [4.90, 1.60],
  [4.90, -1.60],
  [-3.85, -1.60],
  [-3.85, 1.60]
]
```

This results in a navigation envelope of approximately:

* Length: ~8.7 m
* Width: ~3.2 m

The footprint is defined in the `base_footprint` frame and used by the **global and local costmaps** for obstacle avoidance and path feasibility checking.




## Action 6: RViz integration test (full stack)

New launch file:

- `launch/komatsu_rviz_integration.launch.py`

This launch starts:

- `robot_state_publisher` + `joint_state_publisher` (robot model / TF)
- Action 3 localization (`ukf_node` + optional sim odometry/IMU)
- Action 4 mapping (`rtabmap` + optional sim scan)
- Nav2 navigation stack (`navigation_launch.py`)
- RViz (Nav2 default config)

### Build and run

```bash
pkill -f ros2 || true
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application robot_bringup robot_description
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_bringup komatsu_rviz_integration.launch.py source_mode:=sim
```

### Step-by-step checks (Action 6)

1. In RViz, confirm TF chain is present: `map -> odom -> base_link`.
2. Set **2D Pose Estimate** (initial pose) in RViz.
3. Send **2D Nav Goal** in RViz.
4. Verify a global/local path appears and updates.
5. Verify path-following behavior and monitor `/cmd_vel`:

```bash
ros2 topic echo /cmd_vel
```
```bash
ros2 topic echo /map --once
```

```bash
ros2 topic echo /scan --once
```

### Notes

- This Action 6 flow does **not** include P12 or `ros2_control`.
- For hardware scan input, disable sim scan and set topic:


### Action 6 troubleshooting note

- `sim_scan_publisher` now publishes LaserScan angles with consistent metadata (`angle_min/angle_max/angle_increment` matches beam count). This avoids RTAB-Map scan conversion failures that can prevent `/map` updates and Nav2 planning.
- `rviz_integration.launch.py` now prints startup diagnostics for sim source flags and topic wiring (`odom_topic`, `scan_topic`) to simplify launch-time debugging.
- In this Action 6 SLAM flow, Nav2 AMCL/map_server lifecycle is not started (Nav2 panel may show localization as disabled).





## Action 7: Gazebo + RViz quick run

**Prerequisites**: Install Gazebo and gazebo_ros packages:

```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros
```

**Gazebo features**:
- Differential drive plugin for cmd_vel consumption
- Simulated LiDAR sensor (360° scan, 50m range)
- IMU sensor
- Ground truth odometry
- Realistic physics with wheel friction and inertia

**Topics provided by Gazebo**:
- `/odom` (nav_msgs/Odometry) - Wheel odometry
- `/scan` (sensor_msgs/LaserScan) - LiDAR data
- `/imu/data` (sensor_msgs/Imu) - IMU data
- `/ground_truth/odom` (nav_msgs/Odometry) - Perfect ground truth

**Control interface**:
- `/cmd_vel` (geometry_msgs/Twist) - Velocity commands

## Notes

- Gazebo URDF includes collision and inertial properties required for physics simulation
- Base URDF (komatsu.urdf.xacro) is suitable for RViz visualization and real hardware
- Articulated steering is simplified to differential drive in Gazebo for initial testing
- For full articulated steering simulation, future work will add ros2_control integration



### Quick start separate terminals (for debugging)

Run in 5 terminals (same workspace and sourced environment):

```bash
# Terminal 1: Gazebo only
pkill -f ros2 || true
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_bringup komatsu_gazebo.launch.py
```

```bash
# Terminal 2: Localization
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ros2_application komatsu_localization.launch.py \
  use_sim_time:=true \
  use_sim_odometry:=false \
  use_sim_imu:=false
```

```bash
# Terminal 3: Mapping
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ros2_application komatsu_mapping.launch.py \
  use_sim_time:=true \
  use_sim_scan:=false
```

```bash
# Terminal 4: Nav2
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=true \
  autostart:=true \
  params_file:=/home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/robot_bringup/config/komatsu_nav2_params.yaml
```

```bash
# Terminal 5: RViz
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run rviz2 rviz2 \
  -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz
```

In RViz:
- Click `2D Pose Estimate`, set initial pose.
- Click `Nav2 Goal`, set a simple goal.
- Check movement in both Gazebo and RViz.

Notes:
- Keep `use_sim_time:=true` for all launched nodes.
- Terminal 1 is Gazebo-only for this split workflow.
- With `use_sim_odometry:=false`, localization now uses Gazebo `/odom` directly for UKF odometry input.
- Use `autostart:=true` in Terminal 4 so Nav2 lifecycle nodes activate automatically.
- Do not run `komatsu_rviz_integration.launch.py` together with separate Action 3/4/5 terminals.
- If Nav2 is still inactive, check:
```bash
ros2 lifecycle get /bt_navigator
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
```
