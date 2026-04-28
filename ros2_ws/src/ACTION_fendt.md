
# Action 1: Fendt robot model
## Build and launch the Fendt URDF in RViz
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select robot_description
source install/setup.bash
xacro src/robot_description/urdf/fendt/fendt.urdf.xacro > /tmp/fendt.urdf
ros2 launch robot_description fendt_view_robot.launch.py
```

Expected:
- `robot_state_publisher`, `joint_state_publisher_gui`, and `rviz2` start.
- The Fendt model appears with different front/rear wheel sizes and body sections.



# Action 9 : Gazebo + Nav2 + GNSS

- Nav2 publishes `geometry_msgs/Twist` on `/cmd_vel`

Quick check:
```bash
ros2 topic info /cmd_vel -v
ros2 topic echo /cmd_vel
```

## kill nodes
```bash
kill -9 $(ps aux | grep -E "ros2|gz|gazebo|nav2" | grep -v grep | awk '{print $2}')
pkill -9 -f "joint_state_publisher|komatsu_gazebo_nav.launch.py|gzserver|gzclient|navsat_transform_node|ukf_node|gps_covariance_relay|mapviz|initialize_origin.py|planner_server|controller_server|bt_navigator|lifecycle_manager|robot_state_publisher|teleop_twist_keyboard"
ros2 daemon stop
sleep 2
ros2 daemon start
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
rm -rf build/ install/ log/
source /opt/ros/humble/setup.bash
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
colcon build --packages-select robot_bringup robot_description ros2_application ros_ll_controller_python ros2_interfaces
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_bringup fendt_gazebo.launch.py use_sim_time:=true

```

## run teleop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## EVALUATION

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

## CHECK NODES
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

```bash
ros2 node info /navsat_transform_node
```


## GPS waypoint follower node

```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application
source install/setup.bash

ros2 launch ros2_application gps_waypoint_follower.launch.py
```

Verified behavior:
- Default `gps_waypoints.yaml` converts to map-frame goals and reaches them successfully in Action 9.
- `gps_waypoint_follower` now reports waypoint failures clearly if Nav2 misses any waypoint, instead of logging a misleading success.

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




# Action 10: Fendt Ackermann ros2_control

## Current state

- Fendt launches with Gazebo + GNSS + Mapviz + Nav2.
- Nav2 publishes `/cmd_vel`.
- Robot currently moves through Gazebo diff-drive plugin.
- Diff-drive plugin must be removed from `fendt_gazebo.urdf.xacro`.
- New control chain should be:

```txt
Nav2 / teleop
  → /cmd_vel
  → custom Ackermann controller
  → steering + throttle + brake commands
  → Gazebo / ros2_control hardware interface
  → wheel + steering joints
```

## Action plan

### 1. Freeze current working baseline

```bash
ros2 launch robot_bringup fendt_gazebo.launch.py use_sim_time:=true
ros2 topic echo /cmd_vel
ros2 topic echo /odom --once
ros2 topic echo /gps/fix --once
```

Expected:
- Robot still moves with current diff-drive.
- GNSS + Mapviz + Nav2 still work.

---

### 2. Remove Gazebo diff-drive plugin

File:
```txt
robot_description/urdf/fendt/fendt_gazebo.urdf.xacro
```

Remove:
```xml
<plugin name="differential_drive_controller" filename="libgazebo_ros_diff_drive.so">
...
</plugin>
```

Expected:
- Robot no longer moves from `/cmd_vel`.
- Sensors still publish:
    - `/gps/fix`
    - `/imu/data`
    - `/scan`
    - `/joint_states`

---

### 3. Add ros2_control xacro

Create:
```txt
robot_description/urdf/fendt/fendt_ros2_control.xacro
```

Control interfaces:
```txt
front_left_wheel_steer_joint  -> position
front_right_wheel_steer_joint -> position
rear_left_wheel_joint         -> velocity
rear_right_wheel_joint        -> velocity
```

Expected:
- Steering joints receive angle commands.
- Rear wheels receive velocity commands.

---

### 4. Add Gazebo ros2_control plugin

In `fendt_gazebo.urdf.xacro`, add:

```xml
<gazebo>
  <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
    <parameters>$(find robot_bringup)/config/fendt_ros2_control.yaml</parameters>
  </plugin>
</gazebo>
```

Expected:
- `/controller_manager` appears.
- Controllers can be loaded.

---

### 5. Create controller config

Create:
```txt
robot_bringup/config/fendt_ros2_control.yaml
```

Controllers:
```txt
joint_state_broadcaster
fendt_ackermann_controller
```

Expected:
```bash
ros2 control list_controllers
```

Shows:
```txt
joint_state_broadcaster active
fendt_ackermann_controller active
```

---

### 6. Create custom Ackermann controller package (ros2_control is better in c++)

Package:
```txt
fendt_ackermann_controller
```

Node/controller input:
```txt
/cmd_vel : geometry_msgs/msg/Twist
```

Internal conversion:
```txt
v = cmd_vel.linear.x
w = cmd_vel.angular.z

steering_angle = atan(wheelbase * w / v)
rear_wheel_velocity = v / rear_wheel_radius
```

Outputs:
```txt
front steering joint position
rear wheel joint velocity
brake command
throttle command
```

Expected:
- Teleop and Nav2 both control the same chain through `/cmd_vel`.

---

### 7. Add lifecycle / safety wrapper

Create lifecycle node:
```txt
fendt_control_manager
```

States:
```txt
unconfigured -> inactive -> active -> finalized
```

Safety behavior:
```txt
no /cmd_vel timeout -> throttle = 0, brake = active
cmd_vel linear.x = 0 -> brake = active
invalid steering angle -> clamp to limit
```

Expected:
- Robot stops safely if Nav2 or teleop stops publishing.

---

### 8. Bridge sim control with real retrofit messages later

For simulation first:
```txt
/cmd_vel -> ackermann controller -> ros2_control joints
```

For real retrofit later:
```txt
/cmd_vel -> ackermann controller -> MachineSetAll
```

Focus fields:
```txt
steering
throttle
brake
directional_sel
```

---

### 9. Update Fendt launch

File:
```txt
robot_bringup/launch/fendt_gazebo.launch.py
```

Add:
```txt
controller_manager
joint_state_broadcaster spawner
fendt_ackermann_controller spawner
```

Keep unchanged:
```txt
GNSS localization
Mapviz
Nav2
Gazebo world
robot_state_publisher
```

Expected:
- Existing GNSS/Mapviz/Nav2 flow remains unchanged.
- Only motion backend changes.

---

### 10. Validate step by step

```bash
ros2 control list_hardware_interfaces
ros2 control list_controllers
ros2 topic echo /cmd_vel
ros2 topic echo /joint_states --once
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_footprint
```

Expected:
- `/cmd_vel` changes steering/wheel joints.
- Robot moves with Ackermann behavior.
- GNSS localization still publishes stable odometry.
- Nav2 still reaches goal.

---

## kill nodes
```bash
kill -9 $(ps aux | grep -E "ros2|gz|gazebo|nav2" | grep -v grep | awk '{print $2}')
pkill -9 -f "joint_state_publisher|komatsu_gazebo_nav.launch.py|gzserver|gzclient|navsat_transform_node|ukf_node|gps_covariance_relay|mapviz|initialize_origin.py|planner_server|controller_server|bt_navigator|lifecycle_manager|robot_state_publisher|teleop_twist_keyboard"
ros2 daemon stop
sleep 2
ros2 daemon start
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
rm -rf build/ install/ log/
source /opt/ros/humble/setup.bash
ros2 node list
```

run nav2 with ackermann controller:
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select robot_bringup robot_description ros2_application ros2_interfaces ros_ll_controller_python fendt_ackermann_controller
source install/setup.bash
ros2 launch robot_bringup fendt_gazebo.launch.py use_sim_time:=true autostart:=true
```

### run teleop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```