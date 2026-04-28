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
R = linear_x / angular_z
left_steer  = atan2(wheelbase, R - steering_track_width/2)
right_steer = atan2(wheelbase, R + steering_track_width/2)
left_rear_wheel_velocity  = angular_z * (R - traction_track_width/2) / rear_wheel_radius
right_rear_wheel_velocity = angular_z * (R + traction_track_width/2) / rear_wheel_radius
```

Safety:

- If no command within `cmd_vel_timeout`, output zeros.
- Steering is clamped by `max_steering_angle`.

Lifecycle safety wrapper (`fendt_control_manager_node`):

- Lifecycle states: `unconfigured -> inactive -> active -> finalized`
- Input: `/cmd_vel`
- Output: `/cmd_vel_safe` and `/fendt/brake_active`
- Behavior in `active` state:
  - timeout on `/cmd_vel` -> publish zero `/cmd_vel_safe`, brake active
  - `linear.x == 0` -> brake active
  - invalid or excessive steering request -> clamped before forwarding

    Optional retrofit placeholder bridge (default disabled):

    - Parameter: `enable_machine_set_bridge` (`false` by default)
    - When enabled, the node also publishes `ros2_interfaces/msg/MachineSetAll`
    - Mapping focus fields: `steering`, `throttle`, `brake`, `directional_sel`
    - This keeps simulation backend unchanged (`/cmd_vel_safe -> ros2_control joints`)

Parameters (key):

- `wheelbase`
- `traction_track_width`
- `steering_track_width` (if `<= 0`, controller falls back to `traction_track_width`)
- `rear_wheel_radius`

