
# start the node

```bash
ros2 run robot_state_publisher robot_state_publisher   --ros-args -p robot_description:="$(xacro /home/evox/Desktop/ROS2_examples-Basics/ros2_control/ros2_control_ws/ros2_hw_interface_ws/my_robot_description/urdf/my_robot.urdf.xacro)" 
````

# start the controller manager

```bash
ros2 run controller_manager ros2_control_node   --ros-args   --params-file /home/evox/Desktop/ROS2_examples-Basics/ros2_control/ros2_control_ws/ros2_hw_interface_ws/my_robot_bringup/config/my_robot_controller.yaml
``` 

# spawn the controllers

```bash
ros2 run controller_manager spawner joint_state_broadcaster

ros2 run controller_manager spawner diff_drive_controller
```

# start rviz

```bash
ros2 run rviz2 rviz2 -d /home/evox/Desktop/ROS2_examples-Basics/ros2_control/ros2_control_ws/ros2_hw_interface_ws/my_robot_description/rviz/urdf_config.rviz
```

# start teleop

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/diff_drive_controller/cmd_vel -p stamped:=true
```
