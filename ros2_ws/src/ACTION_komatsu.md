
# Action 9 : Gazebo + Nav2 + GNSS (with static map fallback)

### Action 9 command flow (current)

- Nav2 controller publishes raw `geometry_msgs/Twist` on `/cmd_vel_nav`
- `ros_ll_controller_python` consumes `/cmd_vel_nav` and publishes `/atcom_wa380/wheeler/write/nav_ctrl`
- `gazebo_machine_bridge` converts `MachineSetAll` to `/cmd_vel_ll` and Gazebo consumes `/cmd_vel_ll`

Quick check:
```bash
ros2 topic info /cmd_vel -v
ros2 topic info /cmd_vel_nav -v
ros2 topic info /cmd_vel_ll -v
ros2 topic info /atcom_wa380/wheeler/write/nav_ctrl -v
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
ros2 launch robot_bringup komatsu_gazebo.launch.py use_sim_time:=true

```

### Action 9 verified GNSS behavior (important)

- `navsat_transform_node` should consume `/odometry/filtered` (global EKF), not `/odometry/filtered_local`.
- Expected `/odometry/gps` header frame is `map`.
- `map -> odom` should remain smooth/small at idle. Large jumps usually indicate stale duplicate bringup processes.
- Rolling global costmap is enlarged to `450 x 450 m` so GPS waypoints farther from the current robot pose remain inside the planning window.

Quick sanity checks:
```bash
ros2 node list | grep -E "ukf_filter_node_(odom|map)|navsat_transform_node|gps_covariance_relay"
ros2 topic echo /odometry/gps --once | grep frame_id
ros2 run tf2_ros tf2_echo map odom
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

```bash
ros2 node info /navsat_transform_node
```

## check nav2
```bash
ros2 topic echo /joint_states --once
````


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

### Check Available Topics
```bash
ros2 topic list
ros2 topic list | grep odom
ros2 topic list | grep imu
```







## Custom ros_ll_controller_python
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

### check Nav2 velocity output (direct)
```bash
ros2 topic echo /cmd_vel
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

## build custom RPP controller and check if it's loaded by Nav2

```bash
kill -9 $(ps aux | grep -E "ros2|gz|gazebo|nav2" | grep -v grep | awk '{print $2}') 2>/dev/null
ros2 daemon stop
sleep 2
ros2 daemon start

cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash

colcon build --symlink-install \
  --packages-select nav2_regulated_pure_pursuit_controller \
  --allow-overriding nav2_regulated_pure_pursuit_controller
source install/setup.bash
ros2 launch robot_bringup komatsu_gazebo.launch.py use_sim_time:=true
```

```bash
ros2 pkg prefix nav2_regulated_pure_pursuit_controller
```

Expected:
/home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws/install/nav2_regulated_pure_pursuit_controller


### run custom RPP controller node
```bash
ros2 run ros_ll_controller_python ll_controller
```


```bash
pid=$(pgrep -f controller_server | head -n1)
grep nav2_regulated_pure_pursuit_controller /proc/$pid/maps | head
```
If /proc/$pid/maps shows /opt/ros/humble/.../libnav2_regulated_pure_pursuit_controller...so, it is not using your custom one.
If it shows your workspace ...alpiner_ros2/ros2_ws/build/nav2_regulated_pure_pursuit_controller/libnav2_regulated_pure_pursuit_controller.so
..., custom plugin is loaded.

---

### Check Nav2 Velocity Output
```bash
ros2 topic echo /cmd_vel
```


```bash
ros2 topic list | grep cmd_vel
```

```bash
ros2 topic info /cmd_vel -v
```

```bash
ros2 topic info /atcom_wa380/wheeler/write/nav_ctrl -v
```

```bash
ros2 topic echo /cmd_vel_nav
```
expected:
linear:
x: 1.0
y: 7.898482295126057
z: 2.5
angular:
x: -1.0
y: 0.03054870430392691
z: 0.03054870430392691`

> **Note:** `/cmd_vel_nav` is the raw controller output remapped from the controller_server's `cmd_vel`.
> The velocity smoother then takes `/cmd_vel_nav` as input and publishes the final output on `/cmd_vel`:
> `controller_server → /cmd_vel_nav → velocity_smoother → /cmd_vel`
>
> The current active RPP controller (standard Nav2 build) only sets `linear.x` and `angular.z` — all other fields are `0.0`. This is correct.
>
> The "expected" output with extra fields (`linear.y/z`, `angular.x/y`) was from a **legacy custom RPP controller** (see `KnowledgeBase/RetroFit_Kit_Code/`) that packed debug data into unused Twist fields:
> - `linear.y` = distance_end_of_transformed_plan
> - `linear.z` = lookahead_dist
> - `angular.x` = dist_to_cusp
> - `angular.y` = curvature
>
> This is **no longer active** in the current build.

```bash
ros2 topic info /cmd_vel_nav -v
```

check velocity smoother output:
```bash
ros2 node info /velocity_smoother
```

## ACTION 10: GZ, custom RPP, GPS localization

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

### quick run (single terminal)
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash

colcon build --symlink-install \
  --packages-select nav2_regulated_pure_pursuit_controller ros_ll_controller_python ros2_application robot_bringup robot_description ros2_interfaces \
  --allow-overriding nav2_regulated_pure_pursuit_controller

source install/setup.bash
ros2 launch robot_bringup komatsu_gazebo.launch.py use_sim_time:=true use_ll_control_chain:=true
```

## run teleop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/cmd_vel_teleop
```

Quick verify while teleop is sending commands:
```bash
ros2 topic echo /atcom_wa380/wheeler/write/nav_ctrl --once
ros2 topic echo /cmd_vel_nav --once
ros2 topic echo /cmd_vel_ll --once
ros2 topic echo /joint_states --once
```


### quick checks (new terminal)
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 topic info /cmd_vel_nav -v
ros2 topic info /atcom_wa380/wheeler/write/nav_ctrl -v
ros2 topic info /cmd_vel_ll -v
ros2 topic info /atcom_wa380/wheeler/read/all -v
```

Expected for Action 10:
- `/cmd_vel_nav` published by `controller_server`
- `/atcom_wa380/wheeler/write/nav_ctrl` published by `ll_controller_python`
- `/cmd_vel_ll` consumed by Gazebo drive plugin
- `/joint_states` contains `articulation_to_front`
- `/atcom_wa380/wheeler/read/all` feedback is present

Expected chain for articulated P12:
Nav2 / teleop
→ P12
→ MachineSetAll
→ gazebo_machine_bridge
→ directly command:
- wheel drive joints
- articulation_to_front joint

## check controller output and feedback
```bash
ros2 control list_controllers
ros2 topic echo /wheel_velocity_controller/commands --once
ros2 topic echo /articulation_position_controller/commands --once
ros2 topic echo /joint_states --once
ros2 topic echo /odom --once
```