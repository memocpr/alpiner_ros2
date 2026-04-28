# fendt_ackermann_controller

Minimal ROS 2 control controller plugin for Fendt simulation.

- Input: `/cmd_vel` (`geometry_msgs/msg/Twist`)
- Output:
  - `front_left_wheel_steer_joint/position`
  - `front_right_wheel_steer_joint/position`
  - `rear_left_wheel_joint/velocity`
  - `rear_right_wheel_joint/velocity`

Conversion:

```txt
steering_angle = atan(wheelbase * angular_z / linear_x)
rear_wheel_velocity = linear_x / rear_wheel_radius
```

Safety:

- If no command within `cmd_vel_timeout`, output zeros.
- Steering is clamped by `max_steering_angle`.

