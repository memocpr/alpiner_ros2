
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


