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
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_interfaces
source install/setup.bash
ros2 interface list | grep ros2_interfaces
ros2 interface show ros2_interfaces/msg/MachineIndAll
```


## Action 2: Robot model

Robot Specifications

Based on Komatsu WA380 articulated wheel loader:
- **Overall length**: 8.35 m
- **Wheelbase**: 3.03 m
- **Width**: 2.765 m (over tires)
- **Track width**: 2.16 m
- **Ground clearance**: 0.455 m
- **Overall height**: 3.395 m
- **Articulation angle**: ±0.35 rad (±20°)
- **Wheel radius**: ~0.80 m

### TF Tree

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
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select robot_description --symlink-install
source install/setup.bash
ros2 launch robot_description komatsu_view_robot.launch.py
```

create/update TF tree diagram:
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/robot_description/TFs
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

### Publish Robot Model and TF
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_description komatsu_view_robot.launch.py
```

### Build and Launch Localization
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application robot_description
source install/setup.bash
ros2 launch ros2_application komatsu_localization.launch.py
```

### Check Running Nodes
```bash
ros2 node list
ros2 node list | grep robot_state_publisher
```
Expected:
```
/robot_state_publisher
/sim_imu
/sim_odometry
/ukf_filter_node
```

---

### Check Available Topics
```bash
ros2 topic list
ros2 topic list | grep odom
ros2 topic list | grep imu
```

Expected important topics:
```
/odometry/raw
/odometry/filtered
/imu/data
/tf
/tf_static
/cmd_vel
```

---

### Verify Raw Odometry
```bash
ros2 topic hz /odometry/raw
ros2 topic echo /odometry/raw --once
```

Expected:
```
average rate: ~20 Hz
```

Example message:
```
header.frame_id: odom
child_frame_id: base_footprint
pose.pose.position.x: 0.0
```

---

### Verify IMU Data
```bash
ros2 topic hz /imu/data
ros2 topic echo /imu/data --once
```

Expected:
```
average rate: ~20 Hz
```

Example message:
```
header.frame_id: base_link
linear_acceleration.z: 9.81
orientation.w: 1.0
```

---

### Verify UKF Filtered Odometry
```bash
ros2 topic hz /odometry/filtered
ros2 topic echo /odometry/filtered --once
```

Expected:
```
average rate: ~30 Hz
```

Example message:
```
header.frame_id: odom
child_frame_id: base_footprint
```

---

### Verify TF: Odom → Base Footprint
```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

Expected:
Continuous transform output:
```
Translation: [x, y, 0]
Rotation: [0, 0, yaw]
```

Example:
```
Translation: [0.000, 0.000, 0.000]
Rotation: [0.000, 0.000, 0.000, 1.000]
```

---

### Verify TF: Base Footprint → Base Link
```bash
ros2 run tf2_ros tf2_echo base_footprint base_link
```

Expected:
Static transform from robot model:
```
Translation: [0, 0, 0]
Rotation: [0, 0, 0, 1]
```

Published by:
```
robot_state_publisher
```

---

### Inspect Static TF
```bash
ros2 topic echo /tf_static --once
```

Expected:
List of static transforms such as:
```
base_footprint -> base_link
base_link -> imu_link
base_link -> laser_frame
```

---

### Inspect TF Topics
```bash
ros2 topic list | grep tf
```

Expected:
```
/tf
/tf_static
```

---

### Find Source of Odometry Node
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws/src
grep -R "sim_odometry_publisher" .
grep -R "broadcasts odom" .
```

Expected:
Location of implementation:
```
ros2_application/ros2_application/sim_odometry_publisher.py
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
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
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
````md
## Action 4 Verification Commands

### Check Running Nodes
```bash
ros2 node list
```
Expected:
- Mapping, localization, and robot model nodes are running.
- Important nodes include:
  - `robot_state_publisher`
  - `joint_state_publisher`
  - `rtabmap`
  - `ukf_filter_node`
  - `sim_odometry`
  - `sim_imu`
  - `sim_scan`

Example output:
```bash
/joint_state_publisher
/robot_state_publisher
/rtabmap
/rviz
/sim_imu
/sim_odometry
/sim_scan
/ukf_filter_node
```

---

### Check Required Topics
```bash
ros2 topic list | grep -E "odometry|imu|scan|map|tf"
```

Expected important topics:
```bash
/odometry/raw
/odometry/filtered
/imu/data
/scan
/map
/tf
/tf_static
```

Example output may also include:
```bash
/cloud_map
/grid_prob_map
/mapData
/mapGraph
/mapOdomCache
/mapPath
```

---

### Verify TF: Odom → Base Footprint
```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

Expected:
Continuous transform output:
```bash
Translation: [x, y, 0]
Rotation: [0, 0, yaw]
```

Example:
```bash
Translation: [0.000, 0.000, 0.000]
Rotation: [0.000, 0.000, 0.000, 1.000]
```

---

### Verify TF: Base Footprint → Base Link
```bash
ros2 run tf2_ros tf2_echo base_footprint base_link
```

Expected:
Static transform from robot model:
```bash
Translation: [0.000, 0.000, 0.455]
Rotation: [0.000, 0.000, 0.000, 1.000]
```

Published by:
```bash
robot_state_publisher
```

---

### Verify TF: Map → Odom
```bash
ros2 run tf2_ros tf2_echo map odom
```

Expected:
Continuous transform output:
```bash
Translation: [x, y, 0]
Rotation: [0, 0, yaw]
```

Example:
```bash
Translation: [0.000, 0.000, 0.000]
Rotation: [0.000, 0.000, 0.000, 1.000]
```

Published by:
```bash
rtabmap
```

---

### Verify Occupancy Map
```bash
ros2 topic echo /map --once
```

Expected:
```bash
header.frame_id: map
info:
  resolution: 0.05
  width: ...
  height: ...
data:
  -1
```

Example message:
```bash
header:
  frame_id: map
info:
  resolution: 0.05000000074505806
  width: 485
  height: 495
```

---

### Verify Laser Scan
```bash
ros2 topic echo /scan --once
```

Expected:
```bash
header.frame_id: laser_frame
angle_min: ...
angle_max: ...
angle_increment: ...
ranges:
```

Example message:
```bash
header:
  frame_id: laser_frame
angle_min: -3.1415927410125732
angle_max: 3.1415927410125732
range_min: 0.10000000149011612
range_max: 25.0
```

---

### Inspect TF Topics
```bash
ros2 topic list | grep tf
```

Expected:
```bash
/tf
/tf_static
```

---

### Optional: Generate TF Tree PDF
```bash
ros2 run tf2_tools view_frames
```

Expected:
- A `frames.pdf` file is generated.
- TF tree should contain:
```bash
map -> odom -> base_footprint -> base_link -> laser_frame
```

---

### Action 4 Success Criteria
```bash
# Mapping is considered verified if:
# 1. /rtabmap is running
# 2. /map is published
# 3. /scan is published
# 4. map -> odom -> base_footprint -> base_link TF chain exists
# 5. OccupancyGrid data is available on /map
```

### Notes

- Start Action 3 first so `/odometry/filtered` is available.
- For retrofit kit: update `scan_topic` and `laser_frame` to match actual hardware TF tree.
- Static TF `base_link -> laser_frame` will be provided by your hardware driver or robot_description URDF.
- **Simulation behavior**: `sim_scan_publisher` provides a static environment (fixed walls and obstacles). No dynamic obstacles that could trigger false motion detection.
- RTAB-Map local test now uses `/tmp/rtabmap_action6.db` with `delete_db_on_start=true` to avoid stale DB conflicts during repeated launch/stop cycles.


## Action 5: Navigation stack (Nav2)

### install slam_toolbox
```bash
sudo apt install ros-humble-slam-toolbox
```

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
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
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
ros2 daemon stop
ros2 daemon start
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

### Restart ROS2 daemon and source workspace
```bash
pkill -f ros2
ros2 daemon stop
ros2 daemon start
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
```

### Build and run
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application robot_bringup robot_description
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_bringup komatsu_rviz_integration.launch.py use_sim_time:=false
```

```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application robot_bringup robot_description
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_bringup komatsu_rviz_integration.launch.py \
use_sim_time:=false \
use_sim_imu:=false
```

### run teleop in another terminal
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### check the custom nav2 controller
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws

source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 pkg prefix nav2_regulated_pure_pursuit_controller
```

```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws

rm -rf build/nav2_regulated_pure_pursuit_controller \
       install/nav2_regulated_pure_pursuit_controller \
       log

colcon build --packages-select nav2_regulated_pure_pursuit_controller \
  --allow-overriding nav2_regulated_pure_pursuit_controller

source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 pkg prefix nav2_regulated_pure_pursuit_controller
```


add .bashrc source line:
```bash
export ATCOM_NS=atcom_wa380
export PYTHONPATH=$PYTHONPATH:~/Desktop/AlpineR/alpiner_ros2/P12-python-machine>
```

### check cmd_vel_out relay
```bash
ros2 topic echo /cmd_vel_out
```

### check atcom
```bash
ros2 pkg list | grep atcom
```


set pmi
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/P12-python-machine-interface-master
pip3 install -e .
```

set pymodbus
```
pip install pymodbus==2.5.3
```


```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros_ll_controller_python
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run ros_ll_controller_python ll_controller
```



### Send Short Test Goal
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map}, pose: {position: {x: -6.0, y: -6.0, z: 0.0}, orientation: {w: 1.0}}}}"
```
Expected:
- Goal accepted
- Robot publishes `/cmd_vel`


### check plan
```bash
ros2 topic echo /plan --once
```
```bash
ros2 topic echo /map --once
```
```bash
ros2 run tf2_ros tf2_echo map base_link
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_link
```
```bash
ros2 topic echo /goal_pose --once
```


### see planners
```bash
ros2 node list | grep -E "planner_server|controller_server|bt_navigator"
ros2 param get /planner_server planner_plugins
ros2 param get /planner_server GridBased.plugin
ros2 param get /controller_server controller_plugins
ros2 param get /controller_server FollowPath.plugin
ros2 param get /bt_navigator navigators
ros2 action list
ros2 action info /navigate_to_pose
```

---

### Step-by-step checks (Action 6)

1. In RViz, confirm TF chain is present: `map -> odom -> base_footprint -> base_link`.
2. Set **2D Pose Estimate** (initial pose) in RViz.
3. Send **2D Nav Goal** in RViz.
4. Verify a global/local path appears and updates.
5. Verify path-following behavior and monitor `/cmd_vel`:


### Action 6 Additional Verification Commands

### Check Key Topics Rate
```bash
ros2 topic hz /scan
ros2 topic hz /odometry/filtered
ros2 topic hz /map
```
Expected:
- `/scan` publishes continuously
- `/odometry/filtered` publishes continuously
- `/map` updates continuously in SLAM mode

---

### Check Nav2 Velocity Output
```bash
ros2 topic echo /cmd_vel
```
Expected:
- Non-zero `linear.x` and/or `angular.z` after sending a short goal


```bash
ros2 topic list | grep cmd_vel
```

```bash
ros2 topic list | grep cmd_vel_out
```

```bash
ros2 topic echo /cmd_vel_out
```

```bash
ros2 topic info /cmd_vel_out -v
```

```bash
ros2 topic info /atcom_wa380/wheeler/write/nav_ctrl -v
```

```bash
ros2 topic echo /cmd_vel_nav
```
expected:
`linear:
x: 1.0
y: 7.898482295126057
z: 2.5
angular:
x: -1.0
y: 0.03054870430392691
z: 0.03054870430392691`

raw output is coming from /cmd_vel_nav
publisher is controller_server
and the extra fields match your custom cpp exactly.

Your cpp sets:
linear.x = linear_vel
angular.z = angular_vel
linear.y = distance_end_of_transformed_plan
linear.z = lookahead_dist
angular.x = dist_to_cusp
angular.y = curvature

```bash
ros2 topic info /cmd_vel_nav -v
```

```bash
ros2 topic echo /map --once
```

```bash
ros2 topic echo /scan --once
```


### Check TF Chain
```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo base_footprint base_link
```
Expected:
- All transforms resolve successfully
- Chain is complete: `map -> odom -> base_footprint -> base_link`

---

### Check Nav2 Lifecycle
```bash
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
```
Expected:
```bash
active [3]
```

---

### Check Action Server
```bash
ros2 action info /navigate_to_pose
```
Expected:
- `/bt_navigator` appears as action server

---

### Check Published Footprint
```bash
ros2 topic echo /local_costmap/published_footprint --once
```
Expected:
- Footprint polygon is published in costmap frame

---

### Check Costmap Output
```bash
ros2 topic echo /global_costmap/costmap --once
ros2 topic echo /local_costmap/costmap --once
```
Expected:
- Costmap messages are published successfully

---










### Notes

- This Action 6 flow does **not** include P12 or `ros2_control`.
- In this SLAM-based pipeline, localization is provided by **RTAB-Map + UKF**, therefore the `static_layer` was removed from `global_costmap`
- AMCL and `map_server` are not used in this step, so the **Nav2 RViz panel may show "Localization inactive"**. This is expected.
- For hardware scan input, disable sim scan and set topic.
- When using a **static map workflow** (`map_server` + `AMCL`), the `static_layer` should be enabled so Nav2 costmaps subscribe to the map provided by `map_server`.
- If `static_layer` is enabled without a running `map_server`, Nav2 may report warnings such as "Can't update static costmap layer, no map received".

1. SLAM + Nav2 (your current setup)
   Robot builds the map while driving.
`   RTAB-Map → creates map
   UKF → odom
   Nav2 → navigate`
   RTAB-Map publishes: `map → odom`

2. Static map + AMCL
   Robot uses a pre-built map for localization and navigation.
  `map_server → load map
  AMCL → localize robot
  Nav2 → navigate`
   AMCL publishes: `map → odom`

3. Typical GNSS pipeline:
   GNSS + IMU + odom
   ↓
   navsat_transform_node
   ↓
   robot_localization (UKF)
   ↓
   map → odom → base_link

### Action 6 troubleshooting note

- `sim_scan_publisher` now publishes LaserScan angles with consistent metadata (`angle_min/angle_max/angle_increment` matches beam count). This avoids RTAB-Map scan conversion failures that can prevent `/map` updates and Nav2 planning.
- `rviz_integration.launch.py` now prints startup diagnostics for sim source flags and topic wiring (`odom_topic`, `scan_topic`) to simplify launch-time debugging.
- Nav2 requires TF chain `map -> odom -> base_footprint -> base_link`.
- **Robot shaking / not moving in RViz**: caused by multiple nodes publishing `odom -> base_footprint` simultaneously. 
- The UKF (`publish_tf: true`) must be the **sole** publisher of this transform. Do **not** add a `static_transform_publisher` for `odom -> base_footprint` in the launch file, and do **not** broadcast TF from `sim_odometry_publisher` — it must only publish `/odometry/raw`. 
- Having both a static `[0,0,0]` TF and a dynamic UKF TF for the same frame pair causes the robot pose to snap back to origin on every static update, producing the shaking/spinning behaviour.
- If `odom -> base_footprint` is missing, publish it for testing:

Expected:
- Full stack starts successfully.
- `/scan`, `/map`, `/odometry/filtered`, and `/cmd_vel` are active.
- A short nearby navigation goal is accepted and `/cmd_vel` is published.

Note:
- In RTAB-Map SLAM mode, `2D Pose Estimate` in RViz is ignored.
- Short local goals are recommended for verification.
- Larger goals may fail if the conservative articulated footprint starts inside inflated/lethal costmap cells.

```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 odom base_footprint
```


## Action 7: Gazebo + Cartographer

If `use_ll_controller:=true`, ensure PMI is installed once:
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/P12-python-machine-interface-master
pip3 install -e .
pip3 install pymodbus==2.5.3
```

### kill unnecessary nodes
```bash
pkill -9 -f "ros2|gzserver|gzclient|rviz2|robot_state_publisher|rtabmap|ukf|nav2|controller_manager|spawn_entity"
```

```bash
ros2 daemon stop
sleep 2
ros2 daemon start
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```


## kill all nodes
```bash
pkill -f gzserver
pkill -f gzclient
pkill -f gazebo
pkill -f ros2
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
rm -rf build/ install/ log/
```

## launch **komatsu** in gazebo with custom world
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select robot_bringup robot_description
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_bringup komatsu_gazebo_cartagrapher.launch.py
```

## check robot model
```bash
gz model -m komatsu -i
```


## launch cartographer
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select komatsu_cartographer
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch komatsu_cartographer cartographer.launch.py use_sim_time:=True
```
- Added local `komatsu_cartographer` package in `src/komatsu_cartographer` so Action 7 uses Komatsu-specific Cartographer tuning.

## run teleop
```bash
source /opt/ros/humble/setup.bash
source ~/Desktop/AlpineR/alpiner_ros2/ros2_ws/install/setup.bash
ros2 run turtlebot3_teleop teleop_keyboard
```

## check map
```bash
ros2 topic list | grep map
ros2 topic echo /map --once
```

## save map
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
ros2 run nav2_map_server map_saver_cli -f src/robot_bringup/maps/simple_test_field
```


# Action 8: Gazebo + Nav2 + map_server
## run map server
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select robot_description --symlink-install
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --packages-select robot_bringup ros2_application --symlink-install
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ros2_application komatsu_map_server_nav.launch.py
```

## verify map server
```bash
ros2 topic list | grep map
ros2 topic echo /map --once
ros2 topic echo /map --once | grep frame_id
```


# Action 9 : Gazebo + Nav2 + GNSS (with static map fallback)

## kill nodes
```bash
kill -9 $(ps aux | grep -E "ros2|gz|gazebo|nav2" | grep -v grep | awk '{print $2}')
pkill -f "ukf_node|planner_server|controller_server|bt_navigator|waypoint_follower|velocity_smoother|initialize_origin|map_to_odom_static_tf|mapviz|mapviz_tf|robot_state_publisher|teleop_twist_keyboard|navsat_transform_node"
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
rm -rf build/ install/ log/
source /opt/ros/humble/setup.bash
ros2 daemon stop
ros2 daemon start
ros2 node list
```

- **Current Gazebo + Nav2 default 
  - flow:     no map_server
    GNSS + IMU + odom → localization
    map → odom → dynamic (from GNSS)
    Nav2 → no global planner
    click on mapviz → sends goal
    Waypoint follower → sends goals sequentially
    Local costmap → obstacle avoidance only
    ➡ Simple GPS waypoint navigation (no map, no global planning)
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select robot_bringup robot_description ros2_application --symlink-install
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_bringup komatsu_gazebo_nav.launch.py use_sim_time:=true

```

## run teleop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Evaluation

```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application
source install/setup.bash
ros2 run ros2_application evaluator_node
```


```bash
ros2 topic echo /executed_path --once
```

### plot_eval
```bash
python3 ~/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/ros2_application/ros2_application/plot_eval.py
```


## check nodes
```bash
ros2 node list | grep -E "map_server|ukf|navsat|planner|controller|bt_navigator|rviz|robot_state_publisher"
```

```bash
ros2 action list | grep navigate
```

```bash
ros2 lifecycle get /planner_server
ros2 lifecycle get /controller_server
ros2 lifecycle get /bt_navigator
```
```bash
ros2 topic echo /gps/fix --once
```
```bash
ros2 topic echo /odometry/filtered_local --once
```
```bash
ros2 topic list | grep -E "gps|odometry"
```

```bash
ros2 topic echo /odometry/gps --once
```

```bash
ros2 run tf2_ros tf2_echo map odom
```
```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

```bash
ros2 node list | grep navsat
```

```bash
ros2 node list | grep ukf
```

```bash
ros2 topic list | grep odometry
```

```bash
ros2 node list
```

```bash
ros2 topic list | grep -E "gps|odometry|tf"
```

```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo map base_footprint
```

```bash
ros2 node list | grep -E "ukf|navsat|gps_cov"
```

```bash
ros2 topic echo /gps/fix_cov --once
```


## GPS waypoint follower node

```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application
source install/setup.bash

ros2 launch ros2_application komatsu_gps_waypoint_follower.launch.py
```

activate lifecycle and check action server:
```bash
ros2 lifecycle set /waypoint_follower configure
ros2 lifecycle set /waypoint_follower activate
```
If `/waypoint_follower` is already active, `configure` returns "Unknown transition". In that case, skip directly to action check.
```bash
ros2 action info /follow_waypoints
```

```bash
ros2 run ros2_application gps_waypoint_logger
```

```bash
ros2 service list | grep fromLL
ros2 topic echo /odometry/gps --once
ros2 topic echo /gps/filtered --once
ros2 topic hz /odometry/filtered_local
ros2 topic echo /gps/fix --once
ros2 topic echo /gps/fix_cov --once
```

### Check Available Topics
```bash
ros2 topic list
ros2 topic list | grep odom
ros2 topic list | grep imu
```

