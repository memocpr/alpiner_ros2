"""Launch file for robot_localization (UKF node)."""
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Generate launch description for localization pipeline."""

    ros2_app_dir = get_package_share_directory('ros2_application')
    ukf_params_file = os.path.join(ros2_app_dir, 'config', 'ukf_params.yaml')

    use_sim_odometry = DeclareLaunchArgument(
        'use_sim_odometry',
        default_value='true',
        description='Use simulated odometry input',
    )

    use_sim_imu = DeclareLaunchArgument(
        'use_sim_imu',
        default_value='true',
        description='Use simulated IMU input',
    )

    ukf_node = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_filter_node',
        output='screen',
        parameters=[ukf_params_file],
    )

    sim_odometry_node = Node(
        package='ros2_application',
        executable='sim_odometry_publisher',
        name='sim_odometry',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_sim_odometry')),
    )

    sim_imu_node = Node(
        package='ros2_application',
        executable='sim_imu_publisher',
        name='sim_imu',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_sim_imu')),
    )

    return LaunchDescription([
        use_sim_odometry,
        use_sim_imu,
        ukf_node,
        sim_odometry_node,
        sim_imu_node,
    ])
