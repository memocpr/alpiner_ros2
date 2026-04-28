import launch
import launch.actions
import launch.substitutions
import launch_ros.actions
from launch.substitutions import EnvironmentVariable


def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package='ros_ll_controller_python', executable='ll_controller', output='screen',
            name='ll_controller_python',
            parameters=[
                {"p_gain_braking_ll_controller": 0.5}, # proportional gain brakes, range 0..1
                {"factor_throttle_reduction_when_not_active_braking" : 0.5}, # throttle reduction when a small deceleration is needed, range 0..1
                {"p_gain_linear_speed_ll_controller": 0.2}, # proportional gain linear speed, range 0.05..2.0 ? to be tested for each application
                {"p_gain_angular_speed_ll_controller": 0.14}, # proportional gain angular speed, range 0.05..2.0 ? to be tested for each application
                {"i_gain_linear_speed_ll_controller": 0.0}, # integral gain linear speed, not implemented yet
                {"i_gain_angular_speed_ll_controller": 0.0}, # integral gain angular speed, not implemented yet
                {"d_gain_linear_speed_ll_controller": 0.0}, # derivative gain linear speed, not implemented yet
                {"d_gain_angular_speed_ll_controller": 0.0}, # derivative gain angular speed, not implemented yet
                {"min_target_angular_speed_ll_controller": 0.0}, # minimum target so that we consider doing the regulation in rad/s
                {"cmd_input_topic": "/cmd_vel_nav"}, # consume raw Nav2 controller output (before smoothing)
                {"teleop_input_topic": "/cmd_vel"}, # fallback manual teleop input topic
                {"cmd_vel_timeout_sec": 0.6}, # tolerate short Nav2/Gazebo scheduling jitter before forcing idle
            ],
            respawn=True,
            namespace=EnvironmentVariable("ATCOM_NS"),
        ),
    ])
