# ros2_application

## Localization Overview

### ACTION.md (SLAM-based)
- Localization via **RTAB-Map (map → odom)** + **UKF (odom → base_link)**
- UKF fuses IMU + wheel odometry (local)
- Provides **relative + SLAM-based global pose**

**RTAB-Map** = Real-Time Appearance-Based Mapping (SLAM package : mapping + localization)

---

### ACTION_B.md (GNSS-based / Retrofit)
- Localization via **GNSS (RTK) + IMU + odometry → navsat_transform → UKF**
- UKF provides **map → odom + odom → base_link**
- No SLAM at runtime, uses **static map + absolute GNSS pose**

**RTK** = Real-Time Kinematic

### Key Difference
- ACTION.md → SLAM provides global pose
- ACTION_B.md → UKF (with GNSS) provides global pose


1. SLAM + Nav2 (Action.md)
   Robot builds the map while driving.
   RTAB-Map → creates map
   UKF → odom
   Nav2 → navigate
   RTAB-Map publishes: map → odom

2. Static map + AMCL (Nav2 default) (Adaptive Monte Carlo Localization)
   Robot uses a pre-built map for localization and navigation.
   map_server → load map
   AMCL → localize robot
   Nav2 → navigate
   AMCL publishes: map → odom

3. Typical GNSS pipeline (Action_B.md)
   Robot uses GNSS + IMU + odometry for localization and a static map for navigation.
   GNSS + IMU + odom
   ↓
   navsat_transform_node
   ↓
   robot_localization (UKF)
   ↓
   map → odom → base_link
   UKF publishes: map → odom and odom → base_link

## Action 1: Interfaces

### Custom Messages (ros2_interfaces)

Package contains 5 custom messages for machine control:
- `MachineIndAll` - machine feedback
- `MachineIndErrors` - error and safety flags
- `MachineIndOthers` - mode and status
- `MachineSetAll` - control commands
- `MachineSetOptions` - additional options

### Build and Check
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_interfaces
source install/setup.bash
ros2 interface list | grep ros2_interfaces
ros2 interface show ros2_interfaces/msg/MachineIndAll
```

Expected:
- Build finishes successfully.
- All custom interfaces are listed.
- `MachineIndAll` fields are printed.

Example output:
```bash
ros2_interfaces/msg/MachineIndAll
ros2_interfaces/msg/MachineIndErrors
ros2_interfaces/msg/MachineIndOthers
ros2_interfaces/msg/MachineSetAll
ros2_interfaces/msg/MachineSetOptions
```

---

## Action 2: Robot Model

### Robot Description Package

Robot is based on Komatsu WA380 articulated wheel loader.

### TF Tree
```text
map
└── odom
    └── base_footprint
        └── base_link
            └── articulation_link
                ├── rear_chassis
                │   ├── rear_left_wheel
                │   ├── rear_right_wheel
                │   ├── imu_link
                │   ├── gnss_link
                │   ├── laser_frame
                │   └── base_rear
                └── front_chassis
                    ├── front_left_wheel
                    ├── front_right_wheel
                    └── base_front
```

Notes:
- `map -> odom` comes from localization.
- `odom -> base_footprint` comes from **UKF**. (Unscented Kalman Filter, a powerful nonlinear state estimation algorithm used primarily for sensor fusion. )
- `imu_link`, `gnss_link`, and `laser_frame` are mounted on `rear_chassis`.

Typical GNSS pipeline:
GNSS + IMU + odom
↓
navsat_transform_node
↓
robot_localization (UKF)
↓
map → odom → base_link


### Visualize in RViz
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select robot_description --symlink-install
source install/setup.bash
ros2 launch robot_description komatsu_view_robot.launch.py
```

Expected:
- Robot model opens in RViz.
- Full TF chain is connected.
- Sensor frames are visible.

### Generate TF Tree PDF
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/robot_description/TFs
ros2 run tf2_tools view_frames
```

Expected:
- `frames.pdf` is generated.
- TF tree contains:
```text
base_footprint -> base_link -> articulation_link -> rear_chassis -> imu_link / gnss_link / laser_frame
```

---

## Action 3: Local Mock Validation

This step validates the GNSS pipeline on local PC before Gazebo and before hardware.

### Local Mock Chain
```text
fake /fix + fake /imu/data + fake /odometry/raw
↓
navsat_transform_node
↓
/odometry/gps
↓
robot_localization (ukf_node)
↓
/odometry/filtered
↓
map -> odom -> base_footprint -> base_link
```

### Required Nodes
- `sim_gnss_publisher`
- `sim_imu_publisher`
- `sim_odometry_publisher`
- `navsat_transform_node`
- `ukf_filter_node`
- `robot_state_publisher`

### Build and Launch
first launch the robot model to load the TF tree, then launch the mock publishers and localization nodes:
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select robot_description ros2_application --symlink-install
source install/setup.bash
ros2 launch robot_description komatsu_view_robot.launch.py
```

```bash
ros2 launch ros2_application komatsu_localization.launch.py use_mock_gnss:=false
```

Expected:
- Mock publishers start.
- `navsat_transform_node` starts.
- UKF starts.
- TF becomes available.

Example log lines:
```bash
[INFO] robot_state_publisher: got segment base_link
[INFO] sim_gnss: publishing /fix
[INFO] sim_imu: publishing /imu/data
[INFO] sim_odometry: publishing /odometry/raw
[INFO] navsat_transform_node: Datum set / GPS transform ready
[INFO] ukf_filter_node: Filter initialized
```

### Check Running Nodes
```bash
ros2 node list | grep -E "sim_gnss|sim_imu|sim_odometry|navsat|ukf|robot_state_publisher"
```

Expected:
/navsat_transform_node
/robot_state_publisher
/sim_gnss
/sim_imu
/sim_odometry
/ukf_filter_node

### Check Available Topics
```bash
ros2 topic list | grep -E "fix|imu|odom|gps|tf"
```

Expected:
/fix
/imu/data
/odometry/raw
/odometry/gps
/odometry/filtered
/tf
/tf_static

### Verify Mock GNSS
```bash
ros2 topic echo /gps/fix --once
```

Expected:
latitude: ...
longitude: ...
altitude: ...
status:
position_covariance:

### Verify Mock IMU
```bash
ros2 topic echo /imu/data --once
```

Expected:
header.frame_id: imu_link
orientation:
angular_velocity:
linear_acceleration:

### Verify Mock Raw Odometry
```bash
ros2 topic echo /odometry/raw --once
```

Expected:
header.frame_id: odom
child_frame_id: base_footprint

### Verify GPS Odometry
```bash
ros2 topic echo /odometry/gps --once
```

Expected:
header.frame_id: map
child_frame_id: base_link

### Verify Filtered Odometry
```bash
ros2 topic echo /odometry/filtered --once
```

Expected:
header.frame_id: odom
child_frame_id: base_footprint

### Verify TF: Map → Odom
```bash
ros2 run tf2_ros tf2_echo map odom
```

Expected:
Translation: [x, y, 0]
Rotation: [0, 0, yaw]

### Verify TF: Odom → Base Footprint
```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

Expected:
Translation: [x, y, 0]
Rotation: [0, 0, yaw]

### Verify TF: Base Footprint → Base Link
```bash
ros2 run tf2_ros tf2_echo base_footprint base_link
```

Expected:
Translation: [0, 0, 0]
Rotation: [0, 0, 0, 1]

### Notes
Action 3 (fallback)
odom + imu → UKF

Action 4 (default)
odom + imu → UKF + GNSS → navsat → global localization







## Action 4: GNSS Localization Pipeline

This is the real GNSS localization step after local validation.

### Localization Chain
```text
/fix + /imu/data + /odometry/raw
↓
navsat_transform_node
↓
/odometry/gps
↓
robot_localization (ukf_node)
↓
/odometry/filtered
↓
map -> odom -> base_footprint -> base_link
```

### Required Nodes
- `navsat_transform_node`
- `ukf_filter_node`
- `robot_state_publisher`

### Build and Launch

run the robot model first to load the TF tree, then launch the localization nodes:

```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select robot_description ros2_application --symlink-install
source install/setup.bash
ros2 launch robot_description komatsu_view_robot.launch.py
```

```bash
ros2 launch ros2_application komatsu_localization.launch.py
```

Expected:
- GNSS localization nodes start.
- UKF starts.
- TF becomes available.

### Check Running Nodes
```bash
ros2 node list | grep -E "robot_state_publisher|navsat|ukf"
```

Expected:
/navsat_transform_node
/robot_state_publisher
/ukf_filter_node

### Check Available Topics
```bash
ros2 topic list | grep -E "fix|imu|odom|gps|tf"
```

Expected:
/fix
/imu/data
/odometry/raw
/odometry/gps
/odometry/filtered
/tf
/tf_static


### Check UKF Parameters
```bash
ros2 param get /ukf_local_node world_frame
ros2 param get /ukf_local_node odom_frame
ros2 param get /ukf_local_node base_link_frame
ros2 param get /ukf_global_node world_frame
ros2 param get /ukf_global_node odom_frame
ros2 param get /ukf_global_node base_link_frame
ros2 param get /ukf_global_node publish_tf
```

Expected:
String value is: odom
String value is: odom
String value is: base_footprint
String value is: map
String value is: odom
String value is: base_footprint
Boolean value is: True



### Verify Parameter Files
```bash
ls install/ros2_application/share/ros2_application/config/
```

Expected:
rtabmap_params.yaml  ukf_global.yaml  ukf_params.yaml

### Verify GNSS Data
```bash
ros2 topic echo /gps/fix --once
```

Expected:
latitude: ...
longitude: ...
altitude: ...
status:
position_covariance:

### Verify Filtered Odometry
```bash
ros2 topic echo /odometry/filtered --once
```

Expected:
header.frame_id: map
child_frame_id: base_footprint

### Verify TF: Map → Odom
```bash
ros2 run tf2_ros tf2_echo map odom
```

Expected:
Translation: [x, y, 0]
Rotation: [0, 0, yaw]

---





## Action 5: Static Map Server (Nav2)

This step replaces RTAB-Map online mapping with a predefined static map.

### Files
- `robot_bringup/maps/map.yaml`
- `robot_bringup/maps/map.pgm`

### Build and Launch


run the robot model first to load the TF tree, then launch the localization nodes:

```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select robot_description ros2_application robot_bringup --symlink-install
source install/setup.bash
ros2 launch robot_description komatsu_view_robot.launch.py
```

```bash
ros2 launch ros2_application komatsu_localization.launch.py
```

```bash
ros2 launch robot_bringup komatsu_nav2.launch.py
```

local PC (no simulator) → use_sim_time=false (default)
Gazebo / sim → use_sim_time=true

```bash
ros2 launch robot_bringup komatsu_nav2.launch.py use_sim_time:=true
```


Expected:
- Map server starts successfully.
- `/map` is published.

### Verify Map Topic
```bash
ros2 node list | grep map
ros2 topic info /map -v
ros2 node info /map_server
```

Expected:
header:
  frame_id: map
info:
  resolution: 0.05

### Verify Running Nodes
```bash
ros2 node list | grep map
```

Expected:
/map_server

---

### Verify Nav2 Nodes
```bash
ros2 node list | grep -E "robot_state_publisher|map_server|planner_server|controller_server|bt_navigator|amcl"
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 action info /navigate_to_pose
```
Expected:
robot_state_publisher exists
map_server exists
Nav2 nodes exist
odom -> base_footprint exists
/navigate_to_pose server exists


### Check Running Nodes
```bash
ros2 daemon stop
ros2 daemon start
ros2 node list | grep -E "(planner|controller|bt_navigator|smoother|behavior)"
```

Expected:
/bt_navigator
/controller_server
/planner_server
/smoother_server
/behavior_server

### Check Available Actions
```bash
ros2 action list
```

Expected:
/follow_path
/navigate_through_poses
/navigate_to_pose

### Check Lifecycle States
```bash
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
```

Expected:
active [3]

### Verify Output Command 


first send a short goal to trigger the planner and controller:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

then check the output command:

```bash
ros2 topic echo /cmd_vel
```

Expected:
- Twist messages are produced when a goal is active.

Example:
```bash
linear:
  x: 0.5
angular:
  z: 0.2
```


```bash
ros2 topic echo /goal_pose --once
ros2 topic echo /plan --once
ros2 topic echo /odometry/filtered --once
```

```bash
ros2 topic echo /tf --once
ros2 topic echo /scan --once
```

```bash
ros2 topic list | grep scan
ros2 topic info /scan
ros2 topic echo /scan --once
```
```bash
ros2 node list | grep -E "scan|laser|lidar|urg|sick|rplidar"
```

---

### Verify LiDAR Data
```bash
ros2 topic info /scan
ros2 topic hz /scan
ros2 topic echo /scan --once
```

Expected:
Type: sensor_msgs/msg/LaserScan
Publisher count: 1
rate around 10 Hz
frame_id: laser_frame


### Verify Nav2 Output Command
```bash
ros2 topic echo /cmd_vel
```

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```




## Action 6: GNSS + Static Map + Nav2 Integration

This step combines localization, map server, Nav2, and RViz.

### Launch File
- `komatsu_rviz_integration.launch.py`

### Launch Components
- `robot_state_publisher`
- `navsat_transform_node`
- `ukf_filter_node`
- `map_server`
- Nav2
- RViz


### Restart ROS2 daemon and source workspace
```bash
pkill -f ros2
ros2 daemon stop
ros2 daemon start
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 node list
```

### Kill PID
```bash
ps -ef | grep -E "robot_state_publisher|navsat_transform_node|static_transform_publisher|rviz2|tf2_echo|transform_listener_impl_57b7c259fba0" | grep -v grep
```
```bash
kill -9 PID1 PID2 PID3
```

### Build and Launch
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application robot_bringup robot_description
source install/setup.bash
ros2 launch robot_bringup komatsu_rviz_integration.launch.py \
use_sim_time:=false
```

### Teleoperation (RViz)
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Expected:
- All main nodes start.
- RViz opens.
- Map, TF, robot model, and Nav2 are visible.

### Check Running Nodes
```bash
ros2 node list
```

Expected important nodes:
/bt_navigator
/controller_server
/map_server
/navsat_transform_node
/planner_server
/robot_state_publisher
/rviz2
/ukf_filter_node

### Check Topics
```bash
ros2 topic list | grep -E "map|fix|imu|odom|cmd_vel|tf"
```

Expected:
/cmd_vel
/fix
/imu/data
/map
/odometry/filtered
/odometry/gps
/odometry/raw
/tf
/tf_static

### Check Navigation Action
```bash
ros2 action list | grep navigate
```

Expected:
/navigate_through_poses
/navigate_to_pose

### Send Short Goal
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 10.0, y: 10.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

Expected:
- Goal accepted.
- Planner generates path.
- Controller publishes `/cmd_vel`.

---

 Localization Chain Check

### Check Raw Odometry
```bash
ros2 topic echo /odometry/raw --once
```
Expected:
- One odometry message appears.

---

### Check Local UKF Output
```bash
ros2 topic echo /odometry/filtered_local --once
```
Expected:
- One odometry message appears.
- If this hangs, local UKF is the current blocker.

---

### Check GNSS Odometry From navsat_transform
```bash
ros2 topic echo /odometry/gps --once
```
Expected:
- One odometry message appears.
- If this hangs, navsat_transform is the current blocker.

## Quick Fixes:
- If `base_footprint` drifts while idle, restart cleanly: `pkill -f ros2 && ros2 daemon stop && ros2 daemon start`.
- In mock GNSS mode, keep `map -> odom` static (identity) to avoid circular drift.
- Ensure mock GNSS stops on stale `/cmd_vel` (timeout enabled in `sim_gnss_publisher`).
- Rebuild and relaunch: `colcon build --packages-select ros2_application robot_bringup robot_description`.





## Action 7: P12 + Gazebo Adapter (minimal)

### Goal
Replace:
Nav2 → /cmd_vel → fake sim

With:
Nav2 → /cmd_vel_out → P12 → MachineSetAll → Gazebo adapter

---

### Step 1 — fix input topic

P12 listens to: cmd_vel_out

/cmd_vel -> /cmd_vel_out

## run cmd_vel_out_relay.py (no needed after rviz integration launch adds it)
```bash
ros2 run ros2_application cmd_vel_out_relay
```

### Build and Launch
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application robot_bringup robot_description
source install/setup.bash
ros2 launch robot_bringup komatsu_rviz_integration.launch.py \
use_sim_time:=false
```

## verify cmd_vel_out
```bash
ros2 topic list | grep cmd_vel
ros2 topic info /cmd_vel_out
ros2 topic info /cmd_vel
``` 

## verify ll_controller_launch,
```bash
ros2 node list | grep ll_controller
ros2 topic info /cmd_vel_out
```







Step 2 — create Gazebo adapter
gazebo_machine_adapter.py

Subscribe:
/atcom_wa380/wheeler/write/nav_ctrl   (MachineSetAll)

Publish:
/cmd_vel   (Twist)

Minimal mapping:
linear.x  = throttle - brake
angular.z = steering

Step 3 — disable old fake pipeline

Disable:

sim_odometry (later)
cmd_vel_joint_state_publisher

They bypass P12.

Step 4 — add P12 launch

Include:
`IncludeLaunchDescription(
PythonLaunchDescriptionSource('ll_controller.launch.py')
)`


Step 5 — add adapter node
Add new node:
Node(
    package='your_pkg',
    executable='gazebo_machine_adapter',
)

Step 6 — validation

Flow must be:
Nav2
 → /cmd_vel
 → (remap) /cmd_vel_out
 → P12 controller
 → MachineSetAll
 → Gazebo adapter
 → /cmd_vel
 → Gazebo motion
 
 
 Success criteria
robot moves in Gazebo (not only RViz)
/cmd_vel is produced by adapter (not Nav2 directly)
P12 logs active control loop


---

## Key conclusion (very important)

- You **must NOT use `/cmd_vel` directly anymore**
- P12 becomes mandatory in loop
- Gazebo needs adapter because it does NOT understand `MachineSetAll`

---

If you want next:
I give you the exact `gazebo_machine_adapter.py` (10–15 lines).



 
 
## Action 8: Sensor Inputs

### Required Sensors
- GNSS-RTK receiver
- IMU
- wheel odometry
- LiDAR (optional but recommended)

### Default Topic Mapping
```text
gnss_topic := /fix
imu_topic  := /imu/data
odom_topic := /odometry/raw
scan_topic := /scan
```

### Verify Sensor Topics
```bash
ros2 topic list | grep -E "fix|imu|odom|scan"
```

Expected:
/fix
/imu/data
/odometry/raw
/scan

### Verify Topic Types
```bash
ros2 topic info /fix
ros2 topic info /imu/data
ros2 topic info /odometry/raw
ros2 topic info /scan
```

Expected:
Type: sensor_msgs/msg/NavSatFix
Type: sensor_msgs/msg/Imu
Type: nav_msgs/msg/Odometry
Type: sensor_msgs/msg/LaserScan

---





## Action 9: GNSS Hardware Driver

Optional hardware driver node for GNSS receiver.

### Optional Stub Node
- `ros2_application/gnss_receiver_node.py`

### Publishes
- `/fix`

### Verify
```bash
ros2 topic echo /fix --once
```

Expected:
latitude: ...
longitude: ...
altitude: ...
position_covariance:
status:

---






## Action 10: Map Alignment

Map origin must match GNSS frame.

### Options
- manual initialization in RViz
- fixed GPS reference
- `navsat_transform_node` reference

### Verify Alignment
```bash
ros2 run tf2_ros tf2_echo map base_link
```

Expected:
- Robot pose in `map` is stable.
- Goal positions in RViz match expected positions.

---






## Action 11: Final Hardware Navigation

### Full Runtime Stack
```text
GNSS-RTK
IMU
wheel odometry
navsat_transform_node
UKF
map_server
Nav2
cmd_vel
P12 / machine_controller
MachineSetAll
bridge_write
Modbus
machine
```

### Control Chain
```text
Nav2
→ /cmd_vel
→ P12 / machine_controller
→ MachineSetAll
→ bridge_write
→ Modbus
→ machine
```

### Final Verification
```bash
ros2 topic echo /cmd_vel
ros2 topic echo /odometry/filtered --once
ros2 action list | grep navigate
ros2 run tf2_ros tf2_echo map base_link
```

Expected:
- `/cmd_vel` is published during navigation.
- `/odometry/filtered` is stable.
- Nav2 actions are available.
- TF chain is valid from `map` to `base_link`.

---

## Success Criteria

System is considered operational if:
- `/map` is published
- `/odometry/filtered` is stable
- `/fix` is available
- TF chain exists:
```text
map -> odom -> base_footprint -> base_link
```
- Nav2 accepts goals
- `/cmd_vel` commands are produced
- `P12 / machine_controller` converts `Twist` into `MachineSetAll`