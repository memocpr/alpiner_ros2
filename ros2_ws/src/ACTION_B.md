# ACTION_B.md

## GNSS-RTK + Static Map Navigation Architecture

Target system replaces SLAM with GNSS-based localization and a predefined map.

System pipeline

GNSS-RTK + IMU + wheel odom  
↓  
navsat_transform_node  
↓  
robot_localization (UKF)  
↓  
map → odom → base_footprint → base_link  
↓  
map_server (static map)  
↓  
Nav2  
↓  
cmd_vel → machine_controller → MachineSetAll


---

# Action 1 — Interfaces

Package: ros2_interfaces

Messages
- MachineIndAll
- MachineIndErrors
- MachineIndOthers
- MachineSetAll
- MachineSetOptions

Build

cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws  
colcon build --packages-select ros2_interfaces  
source install/setup.bash  
ros2 interface list | grep ros2_interfaces

Control chain

Nav2  
→ cmd_vel  
→ machine_controller  
→ MachineSetAll  
→ bridge_write → Modbus → machine


---

# Action 2 — Robot Model

Package: robot_description

Required TF tree

map
└── odom
        └── base_footprint
                └── base_link
                        └── articulation_link
                                ├── rear_chassis
                                │   ├── imu_link
                                │   ├── gnss_link
                                │   └── laser_frame
                                └── front_chassis

Requirements
- add gnss_link frame
- define base_link → gnss_link static transform
- verify base_link → imu_link
- verify base_link → laser_frame


---

# Action 3 — GNSS Localization Pipeline

Replace SLAM localization with GNSS fusion.

Localization chain

/fix + /imu/data + /odometry/raw  
↓  
navsat_transform_node  
↓  
/odometry/gps  
↓  
robot_localization (UKF)  
↓  
map → odom → base_link

Required nodes
- navsat_transform_node
- robot_localization ukf_node

Required topics
- /fix (sensor_msgs/NavSatFix)
- /imu/data (sensor_msgs/Imu)
- /odometry/raw (nav_msgs/Odometry)

UKF output
- /odometry/filtered

Verification

ros2 topic list | grep odom  
ros2 topic echo /odometry/filtered --once

TF check

ros2 run tf2_ros tf2_echo map odom  
ros2 run tf2_ros tf2_echo odom base_footprint


---

# Action 4 — Static Map

Package: robot_bringup/maps

Files
- map.yaml
- map.pgm

Map server

ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=map.yaml

Verify

ros2 topic echo /map --once

Expected

header.frame_id: map  
info.resolution: 0.05


---

# Action 5 — Navigation Stack (Nav2)

Planner
- SmacPlannerHybrid

Controller
- RegulatedPurePursuitController

Velocity
- 0.5 m/s

Inputs

/map  
/odometry/filtered

Output

/cmd_vel

Lifecycle check

ros2 lifecycle get /planner_server  
ros2 lifecycle get /controller_server


---

# Action 6 — GNSS + Map + Nav2 Integration

Launch file

komatsu_gnss_rviz_integration.launch.py

Launch components
- robot_state_publisher
- navsat_transform_node
- ukf_node
- map_server
- Nav2
- RViz

Expected TF chain

map → odom → base_footprint → base_link

Verification

ros2 node list  
ros2 topic list

Check navigation action

ros2 action list | grep navigate

Send short goal

ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"


---

# Action 7 — Sensor Inputs

Required sensors

GNSS-RTK receiver  
IMU  
wheel odometry  
LiDAR (optional but recommended)

Default topic mapping

gnss_topic := /fix  
imu_topic := /imu/data  
odom_topic := /odometry/raw  
scan_topic := /scan


---

# Action 8 — GNSS Hardware Driver

Optional stub node

ros2_application/gnss_receiver_node.py

Publishes

/fix

Message type

sensor_msgs/NavSatFix

Required fields
- latitude
- longitude
- altitude
- covariance
- status


---

# Action 9 — Map Alignment

Map origin must match GNSS frame.

Options

A — manual initialization in RViz  
use 2D Pose Estimate

B — fixed GPS reference

store known waypoint

lat  
lon  
map x,y

C — navsat_transform_node reference


---

# Action 10 — Final Hardware Navigation

Full runtime stack

GNSS-RTK  
IMU  
wheel odom  
navsat_transform_node  
UKF  
map_server  
Nav2

Control chain

Nav2  
→ cmd_vel  
→ machine_controller  
→ MachineSetAll


---

# Success Criteria

System considered operational if

- /map published
- /odometry/filtered stable
- TF chain exists

map → odom → base_footprint → base_link

- Nav2 accepts goals
- /cmd_vel commands produced  