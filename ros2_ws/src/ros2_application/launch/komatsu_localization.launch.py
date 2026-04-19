"""Launch file for robot_localization (UKF node)."""
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Generate launch description for localization pipeline."""

    ros2_app_dir = get_package_share_directory('ros2_application')
    ukf_params_file = os.path.join(ros2_app_dir, 'config', 'ukf_params.yaml')

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if available',
    )

    ukf_node = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_filter_node',
        output='screen',
        parameters=[ukf_params_file, {
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'odom0': '/odom',
        }],
    )

    return LaunchDescription([
        use_sim_time,
        ukf_node,
    ])
